# ASR 标注字段

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| id | 是 | 唯一 ID，如 `eat_01_bafang_1` |
| audio_path | 是 | 相对 `manifest.csv` 所在目录，如 `audio/eat_01_family1_1.m4a`；扩展名可用 `m4a` / `mp3` / `wav` |
| phrase_id | 是 | 对应 `phrases.csv` 的 id |
| text_teochew | 是 | 潮语文本（与口播一致） |
| text_zh | 是 | 普通话意思 |
| intent | 是 | `eat` / `meds` / `miss_family` / `affection` / `thanks` / `weather` / `opera` / `health` / `grandson` |
| speaker | 是 | 说话人代号，如 `bafang` / `family1` |
| accent | 否 | 澄海 / 汕头 / 潮州 等 |
| take | 是 | 第几遍，从 1 起 |
| noise | 否 | `quiet` / `tv` / `kitchen` |
| duration_sec | 否 | 秒 |
| split | 否 | `train` / `val` / `holdout` |
| notes | 否 | 备注 |

## 用字约定（起步）

- 未 / 唔好 / 阿嫲 / 食 / 药 / 返来 / 天时  
- 同一意思固定一种写法，勿「囝」「仔」混用（本项目统一：孙仔）  
- 听不清：`text_teochew` 填 `[unk]`，`intent` 可空，勿硬猜  
