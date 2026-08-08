#!/usr/bin/env python3
"""Upload holdout zip + bootstrap to AutoDL and run transformers eval."""

from __future__ import annotations

import json
import os
import sys
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
LOCAL_ZIP = LOCAL_ROOT / "data" / "asr" / "eval_holdout" / "holdout_audio.zip"
LOCAL_BOOT = LOCAL_ROOT / "teochew-asr" / "scripts" / "autodl_bootstrap.sh"
LOCAL_REPORT_DIR = LOCAL_ROOT / "data" / "asr" / "eval_holdout" / "reports"

REMOTE_RUN = f"{REMOTE_TMP}/_run_eval.sh"


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


def _safe_print(text: str) -> None:
    try:
        print(text, end="", flush=True)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))
        sys.stdout.buffer.flush()


def run(client: paramiko.SSHClient, cmd: str, timeout: int = 7200) -> tuple[int, str, str]:
    print(f"$ {cmd}")
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout, get_pty=True)
    out_chunks: list[str] = []
    err_chunks: list[str] = []
    while True:
        if stdout.channel.recv_ready():
            chunk = stdout.channel.recv(4096).decode("utf-8", errors="replace")
            out_chunks.append(chunk)
            _safe_print(chunk)
        if stderr.channel.recv_stderr_ready():
            chunk = stderr.channel.recv_stderr(4096).decode("utf-8", errors="replace")
            err_chunks.append(chunk)
            _safe_print(chunk)
        if stdout.channel.exit_status_ready() and not stdout.channel.recv_ready():
            break
        time.sleep(0.1)
    code = stdout.channel.recv_exit_status()
    while stdout.channel.recv_ready():
        chunk = stdout.channel.recv(4096).decode("utf-8", errors="replace")
        out_chunks.append(chunk)
        _safe_print(chunk)
    out = "".join(out_chunks)
    err = "".join(err_chunks)
    print()
    return code, out, err


def main() -> int:
    if not LOCAL_ZIP.exists():
        raise SystemExit(f"missing {LOCAL_ZIP}")
    if not LOCAL_BOOT.exists():
        raise SystemExit(f"missing {LOCAL_BOOT}")

    LOCAL_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    run_sh = f"""#!/usr/bin/env bash
set -euo pipefail
export WORKDIR={REMOTE_TMP}
export REPO_DIR={REPO}
export HOLDOUT_ZIP={REMOTE_TMP}/holdout_audio.zip
export MODEL=panlr/whisper-finetune-teochew
export PATH="/root/miniconda3/bin:$PATH"
export HF_ENDPOINT="https://hf-mirror.com"
export HF_HUB_ENABLE_HF_TRANSFER=0
# Prefer hf-mirror; skip network_turbo (can cause Errno 99 to huggingface.co)
mkdir -p "$WORKDIR"
cd "$WORKDIR"
if [ ! -d "$REPO_DIR/.git" ]; then
  git clone --depth 1 https://github.com/barewchiu/nana-teochew-agent.git "$REPO_DIR"
else
  git -C "$REPO_DIR" pull --ff-only || true
fi
# Prefer freshly uploaded scripts (may be newer than GitHub)
if [ -f {REMOTE_TMP}/autodl_bootstrap.sh ]; then
  cp -f {REMOTE_TMP}/autodl_bootstrap.sh "$REPO_DIR/teochew-asr/scripts/autodl_bootstrap.sh"
fi
if [ -f {REMOTE_TMP}/eval_holdout.py ]; then
  cp -f {REMOTE_TMP}/eval_holdout.py "$REPO_DIR/teochew-asr/scripts/eval_holdout.py"
fi
bash "$REPO_DIR/teochew-asr/scripts/autodl_bootstrap.sh"
"""

    client = connect()
    try:
        run(client, "nvidia-smi; (python3 -V || true); (which python3); ls /root/miniconda3/bin/python 2>/dev/null || true")
        sftp = client.open_sftp()
        print("upload zip + scripts …")
        sftp.put(str(LOCAL_ZIP), f"{REMOTE_TMP}/holdout_audio.zip")
        sftp.put(str(LOCAL_BOOT), f"{REMOTE_TMP}/autodl_bootstrap.sh")
        sftp.put(
            str(LOCAL_ROOT / "teochew-asr" / "scripts" / "eval_holdout.py"),
            f"{REMOTE_TMP}/eval_holdout.py",
        )
        with sftp.file(REMOTE_RUN, "w") as f:
            f.write(run_sh.replace("\r\n", "\n"))
        sftp.chmod(REMOTE_RUN, 0o755)
        sftp.close()

        code, out, err = run(client, f"bash {REMOTE_RUN}", timeout=7200)

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
        sftp.close()

        jsons = sorted(LOCAL_REPORT_DIR.glob("holdout_transformers_*.json"))
        if jsons:
            data = json.loads(jsons[-1].read_text(encoding="utf-8"))
            print("=== SUMMARY ===")
            print(json.dumps(data.get("summary", {}), ensure_ascii=False, indent=2))
        else:
            print("No transformers report downloaded.")
        return code
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
