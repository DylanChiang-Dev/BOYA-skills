# 案例：boya 新手定位與 research-record 可續接檔案

> 日期：2026-07-14｜skill：`boya` 與 `research-record`（Boya 2.0 Beta）
> 材料：沿用台灣碳費政策兩個官方來源、候選框架比較與已有人工拍板記錄。

## 新手輸入與定位走查

輸入：

> 我手上已有氣候變遷署碳費專區和環境部費率公告，這一輪要把它們整理成可用的政策分析框架。請用 boya 帶我。

依新規則，材料與本輪目標都已明說，因此 `boya` 不應重問「手上有什麼」或「想要什麼結果」，也不應顯示 17 個 skill 讓新手自選。依產物與瓶頸應直接定位：

- 已有政策材料。
- 目標是定錨分析框架。
- active skill：`theoretical-framework`。
- 硬門：主框架必須由研究者拍板。

若新手只說「不知道從哪開始」，第一輪只問「你現在手上有什麼？」；其他問題留到下一輪。此行為已寫入結構化 eval，但本輪未執行付費模型矩陣。

## 選用建檔硬門

上述定位本身不寫檔。本案例在使用者另行明確要求「請建立研究檔案保存進度」後，才執行 `research_record.py init`。

## 實跑登錄內容

### Artifacts

| ID | 類型 | pointer | 狀態 |
|---|---|---|---|
| `A-POLICY` | official-source | 氣候變遷署碳費專區 URL | present |
| `A-RATE` | official-source | 環境部碳費費率公告 URL | present |
| `A-FRAMEWORK` | framework | 候選框架比較與定錨產物路徑 | present |

檔案只保存 pointer，未複製官方頁內文或論文全文。

### Decision

1. `propose-decision` 先建 `D-FRAMEWORK`，狀態為 pending，問題是「選定哪一個主分析框架？」
2. 沿用真實框架案例中「研究者拍板採用多準則政策分析」的記錄，再以帶 `--user-confirmed` 的 `confirm-decision` 寫入：
   - status：confirmed。
   - choice：多準則政策分析框架。
   - confirmed_by：user。

### Unknown

`U-METHOD`：「政策工具與多準則政策分析的方法文獻尚待補哪些？」，狀態保持 open，沒有因為框架硬門通過就自動關閉。

## 檢查點實跑結果

`sync-checkpoint` 先驗證三個 artifact 均為 present，並確認 `D-FRAMEWORK` 已是 confirmed，才寫入：

```yaml
boya_checkpoint:
  stage: 5
  status: ready_to_advance
  artifacts_present:
    - A-POLICY
    - A-RATE
    - A-FRAMEWORK
  decision_required: 選定主框架
  decision_status: confirmed
  decision_id: D-FRAMEWORK
  active_skill: theoretical-framework
  next_skill: research-design
```

`research_record.py validate` 輸出 `research record valid`；summary 輸出 3 個 present artifacts、1 個 confirmed decision、0 個 pending decisions、1 個 open unknown。

## 反向硬門

離線單元測試另以同樣材料驗證：

- 沒有 `--user-confirmed`：`confirm-decision` 回 exit code 2，決策仍是 pending。
- decision 是 pending 卻嘗試寫 `ready_to_advance`：回 exit code 2，checkpoint 仍為 null。
- 重複 artifact ID：回 exit code 2，原 JSON 仍只有一筆。

## 暴露的坑與寫回

1. **對話 checkpoint 不等於專案檔案。** 要跨對話續接，必須有可驗證的 pointer、決策與未知項；已寫回 `research-record` schema 與 `boya` 失敗處理。
2. **推薦不等於拍板。** 腳本必須分 propose／confirm，且 ready_to_advance 反查 confirmed decision。
3. **新手輸入已有材料與目標時不能重問。** 逐題 onboarding 是減少負擔，不是固定問卷；已寫回 `boya` 新手入口與 eval。

## 驗證邊界

- 本輪實際執行了 research-record 的 init、artifact、unknown、decision、checkpoint、validate 與 summary 全鏈。
- `boya` onboarding 是依真實材料的規則級走查與結構化 eval；未執行付費模型矩陣，因此仍列 Beta。
