# AutoDL 全自动评测（T4）

本机无 GPU 时，用仓库脚本一键跑 hold-out。

## 你需要上传的只有一个 zip

本机生成（在仓库根目录）：

```powershell
powershell -File teochew-asr/scripts/pack_holdout_for_autodl.ps1
```

产物：`submit/holdout_audio.zip`（含 32 条录音 + manifest）

## AutoDL 上操作（约 3 步）

1. JupyterLab → 上传到 `/root/autodl-tmp/`：
   - `holdout_audio.zip`
   - （可选）`autodl_bootstrap.sh`；也可直接从 GitHub clone 后用仓库内脚本
2. 终端执行：

```bash
cd /root/autodl-tmp
git clone --depth 1 https://github.com/barewchiu/nana-teochew-agent.git
cp nana-teochew-agent/teochew-asr/scripts/autodl_bootstrap.sh .
bash autodl_bootstrap.sh
```

若 zip 已放在 `/root/autodl-tmp/holdout_audio.zip`，脚本会自动解压并评测。

3. 看终端 `intent_accuracy`，然后控制台 **关机**。

## SSH 交给 Cursor 代跑

把实例页的 SSH 命令贴给 Agent（含主机和端口），并提供密码或密钥后，可由 Agent 远程执行同一套脚本。
