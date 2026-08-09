#!/usr/bin/env python3
"""Upload L1 train + holdout zips to AutoDL, run LoRA finetune + holdout eval."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import paramiko

HOST = os.getenv("AUTODL_SSH_HOST", "")
PORT = int(os.getenv("AUTODL_SSH_PORT", "0"))
USER = os.getenv("AUTODL_SSH_USER", "root")
PASSWORD = os.getenv("AUTODL_SSH_PASSWORD", "")
if not HOST or not PORT or not PASSWORD:
    raise SystemExit(
        "Set AUTODL_SSH_HOST, AUTODL_SSH_PORT, AUTODL_SSH_PASSWORD env vars"
    )

REMOTE_TMP = "/root/autodl-tmp"
REPO = f"{REMOTE_TMP}/nana-teochew-agent"
LOCAL_ROOT = Path(__file__).resolve().parents[2]
LOCAL_TRAIN_ZIP = LOCAL_ROOT / "data" / "asr" / "l1_commands" / "l1_train_audio.zip"
LOCAL_HOLD_ZIP = LOCAL_ROOT / "data" / "asr" / "eval_holdout" / "holdout_audio.zip"
LOCAL_FT_SH = LOCAL_ROOT / "teochew-asr" / "scripts" / "autodl_finetune.sh"
LOCAL_FT_PY = LOCAL_ROOT / "teochew-asr" / "scripts" / "finetune_whisper_l1.py"
LOCAL_EVAL = LOCAL_ROOT / "teochew-asr" / "scripts" / "eval_holdout.py"
LOCAL_REPORT_DIR = LOCAL_ROOT / "data" / "asr" / "eval_holdout" / "reports"
REMOTE_RUN = f"{REMOTE_TMP}/_run_finetune.sh"


def connect() -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"connecting {USER}@{HOST}:{PORT} …")
    client.connect(
        HOST,
        port=PORT,
        username=USER,
        password=PASSWORD,
        timeout=60,
        allow_agent=False,
        look_for_keys=False,
    )
    return client


def run(client: paramiko.SSHClient, cmd: str, timeout: int = 14400) -> int:
    print(f"$ {cmd}")
    _, stdout, _ = client.exec_command(cmd, timeout=timeout, get_pty=True)
    while True:
        if stdout.channel.recv_ready():
            print(stdout.channel.recv(4096).decode("utf-8", errors="replace"), end="", flush=True)
        if stdout.channel.exit_status_ready() and not stdout.channel.recv_ready():
            break
        time.sleep(0.1)
    code = stdout.channel.recv_exit_status()
    while stdout.channel.recv_ready():
        print(stdout.channel.recv(4096).decode("utf-8", errors="replace"), end="", flush=True)
    print()
    return code


def main() -> int:
    for p in (LOCAL_TRAIN_ZIP, LOCAL_HOLD_ZIP, LOCAL_FT_SH, LOCAL_FT_PY, LOCAL_EVAL):
        if not p.exists():
            raise SystemExit(f"missing {p}")

    LOCAL_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    run_sh = f"""#!/usr/bin/env bash
set -euo pipefail
export WORKDIR={REMOTE_TMP}
export REPO_DIR={REPO}
export TRAIN_ZIP={REMOTE_TMP}/l1_train_audio.zip
export HOLDOUT_ZIP={REMOTE_TMP}/holdout_audio.zip
export BASE_MODEL=panlr/whisper-finetune-teochew
export EPOCHS="${{EPOCHS:-30}}"
export PATH="/root/miniconda3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export HF_ENDPOINT="https://hf-mirror.com"
export HF_HUB_ENABLE_HF_TRANSFER=0
mkdir -p "$WORKDIR"
cd "$WORKDIR"
if [ ! -d "$REPO_DIR/.git" ]; then
  git clone --depth 1 https://github.com/barewchiu/nana-teochew-agent.git "$REPO_DIR"
else
  git -C "$REPO_DIR" pull --ff-only || true
fi
cp -f {REMOTE_TMP}/autodl_finetune.sh "$REPO_DIR/teochew-asr/scripts/autodl_finetune.sh"
cp -f {REMOTE_TMP}/finetune_whisper_l1.py "$REPO_DIR/teochew-asr/scripts/finetune_whisper_l1.py"
cp -f {REMOTE_TMP}/eval_holdout.py "$REPO_DIR/teochew-asr/scripts/eval_holdout.py"
bash "$REPO_DIR/teochew-asr/scripts/autodl_finetune.sh"
"""

    client = connect()
    try:
        run(client, "nvidia-smi || true")
        sftp = client.open_sftp()
        print("upload zips + scripts …")
        for local, remote in (
            (LOCAL_TRAIN_ZIP, f"{REMOTE_TMP}/l1_train_audio.zip"),
            (LOCAL_HOLD_ZIP, f"{REMOTE_TMP}/holdout_audio.zip"),
            (LOCAL_FT_SH, f"{REMOTE_TMP}/autodl_finetune.sh"),
            (LOCAL_FT_PY, f"{REMOTE_TMP}/finetune_whisper_l1.py"),
            (LOCAL_EVAL, f"{REMOTE_TMP}/eval_holdout.py"),
        ):
            data = local.read_bytes()
            if local.suffix in {".sh", ".py"}:
                data = data.replace(b"\r\n", b"\n")
            with sftp.file(remote, "wb") as f:
                f.write(data)
            print(f"  {remote}")
        with sftp.file(REMOTE_RUN, "w") as f:
            f.write(run_sh.replace("\r\n", "\n"))
        sftp.chmod(REMOTE_RUN, 0o755)
        sftp.close()

        code = run(client, f"bash {REMOTE_RUN}", timeout=14400)

        sftp = client.open_sftp()
        remote_reports = f"{REPO}/data/asr/eval_holdout/reports"
        try:
            names = sftp.listdir(remote_reports)
        except OSError:
            names = []
        for name in sorted(names):
            if name.endswith(".json") or name.endswith(".csv"):
                print(f"download {name}")
                sftp.get(f"{remote_reports}/{name}", str(LOCAL_REPORT_DIR / name))
        # download train meta if present
        meta_remote = f"{REPO}/teochew-asr/checkpoints/l1_lora/train_meta.json"
        try:
            local_meta = LOCAL_ROOT / "teochew-asr" / "checkpoints" / "l1_lora" / "train_meta.json"
            local_meta.parent.mkdir(parents=True, exist_ok=True)
            sftp.get(meta_remote, str(local_meta))
            print(f"download {local_meta}")
        except OSError:
            pass
        sftp.close()

        jsons = sorted(
            LOCAL_REPORT_DIR.glob("holdout_transformers_*.json"),
            key=lambda p: p.stat().st_mtime,
        )
        if jsons:
            newest = jsons[-1]
            data = json.loads(newest.read_text(encoding="utf-8"))
            print("=== SUMMARY ===", newest.name)
            print(json.dumps(data.get("summary", {}), ensure_ascii=False, indent=2))
        else:
            print("No transformers report downloaded.")
        return code
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
