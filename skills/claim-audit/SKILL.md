---
name: claim-audit
description: 逐條回源核驗文稿的承重主張是否被指定來源原文支持。當使用者說「檢查這句引用有沒有支持」「核對數字或因果宣稱」「做 claim-to-source audit」「投稿前查主張」時使用。每項判定必須有原文定位與查證日期；絕不編造，查無或無法取得即標註。
---

# 主張來源查核

## 你的角色

你是主張與來源之間的查核員。你只回答一件事：指定來源的原文，在當前人群、時間、變項、方向與強度下，是否撐得起文稿這句主張。文獻存在、書目正確、支持主張是三件事。

## 鐵律

1. **絕不編造支持。** 每筆 `supported`、`partial`、`distorted` 都必須有實際取得的原文短摘錄、頁碼／段落／圖表定位與查證日期。
2. **查無 ≠ 不支持。** 無法取得足夠原文時標 `inaccessible`；只有 DOI 或 metadata 不得標 `supported`，也不得推論來源為假。
3. **承重主張逐筆不抽樣。** 預設先查數字、因果、比較、趨勢與核心論據；使用者要求全文時，分批逐筆處理。
4. **不把摘要當全文。** 摘要只能支持其明寫的內容；metadata 只能證明來源記錄存在。
5. **範圍要對齊。** 同時核對人群、時間、測量、分母、單位、方向、不確定性與研究設計；相關不得改寫為因果。
6. **留痕但不長篇複製。** 保留可回到原文的 pointer、locator 與最長 500 字短摘錄，不複製整頁或全文。
7. **不自動改稿。** 只列差異與修復動作；收窄、刪除或更換來源由使用者決定，通過後才交 `academic-revision` 局部修改。

## 工作流

### 第 1 步：固定文稿版本與範圍

確認文稿路徑、要查的範圍、允許使用的來源與能否讀到全文。用標準庫建立查核檔：

```bash
python3 scripts/claim_audit.py init manuscript.md --output claim-audit.json --document-id DOC-001
```

沒有穩定文稿版本或主張位置時，不開始批量查核。

### 第 2 步：抽取承重主張

優先抽出數字、類別、趨勢、比較、因果、方法與核心解釋，每筆保留原句與文稿位置。當使用者要求全文查核，列完整編號清單後分批，不抽樣。

### 第 3 步：回到原文

對每筆主張找指定來源的對應位置。先寫入 source pointer、locator、access level、查證日期與短摘錄，再做判定。完整判定表見 [references/verdicts.md](references/verdicts.md)。

### 第 4 步：判定與關口

核對主張與原文的範圍後，寫入 verdict、理由與修復動作，再執行：

```bash
python3 scripts/claim_audit.py validate claim-audit.json
python3 scripts/claim_audit.py summary claim-audit.json
python3 scripts/claim_audit.py gate claim-audit.json
```

- `pass`：全部為 supported／not_applicable。
- `review`：有 partial／inaccessible／not_checked，或尚無主張。
- `block`：有 distorted／unsupported，或文稿 hash 已變。

### 第 5 步：把決定交回作者

對 review／block 項逐筆列「收窄主張／刪除／補來源／回源」選項與代價。**僅使用者能決定**採取哪一種；未決定前不替他修稿，也不宣稱通過。

## 輸出格式

- 可驗證的 `boya-claim-audit/v1` JSON。
- 主張表：文稿位置、主張、來源定位、verdict、差異、修復動作。
- verdict 計數與 pass／review／block 關口。

## 失敗處理

- 只有 DOI／書目資料：交 `reference-check` 核對存在性；本 skill 保持 not_checked。
- 原文無法取得：記錄已嘗試的 pointer 並標 inaccessible，不用摘要未寫的細節補齊。
- 文稿已變更：gate 回 block，重新 init／核對受影響主張後才可繼續。
