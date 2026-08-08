# 潮语 ASR 数据目录

```
data/asr/
├── README.md                 # 本文件
├── SCHEMA.md                 # 字段说明
├── l1_commands/
│   ├── phrases.csv           # 待录口播清单（产品意图）
│   ├── manifest.csv          # 已录条目索引（请往下追加）
│   └── audio/                # 录音文件（git 忽略，本地保存）
├── l2_nana/
│   ├── manifest.csv
│   └── audio/
└── eval_holdout/
    ├── manifest.csv          # 锁定测试集
    └── audio/
```

## 立刻开始

1. 打开 `l1_commands/phrases.csv`  
2. 用潮汕话逐句录到 `l1_commands/audio/`  
3. 在 `l1_commands/manifest.csv` 追加一行  

校验：

```bash
python teochew-asr/scripts/check_manifest.py data/asr/l1_commands/manifest.csv
```

## 隐私

阿嫲原始录音默认仅本地保存；不要提交到公开仓库。  
`audio/` 已在根 `.gitignore` 中忽略。
