# 案例：claim-audit 查台灣碳費主張，串批准後局部修訂

> 日期：2026-07-14｜skill：`claim-audit` 與 `academic-revision`（Boya 2.0 Beta）
> 材料：沿用真實台灣碳費政策案例，回查環境部新聞稿與氣候變遷署碳費專區。

## 為什麼跑這個案例

`reference-check` 能查文獻存在與書目欄位，但 Boya 原本沒有一個可留痕的機制，核對「這個來源是否真的撐得起這句話」。本案例故意把一個可核對的政策數字，與一個過度的方法宣稱放在同一份短稿。

## 原稿兩個承重主張

1. `C1`：一般費率 300 元，優惠費率 A 50 元，優惠費率 B 100 元，單位為每公噸二氧化碳當量。
2. `C2`：「環境部官方政策頁已證明多準則政策分析是客觀最佳方法。」

## 回源查核

### C1：supported

- 來源：環境部新聞稿〈環境部公告「碳費徵收費率」〉。
- pointer：`https://enews.moenv.gov.tw/Page/3B3C62C78849F32F/3a0a408a-33e5-4a0d-9939-23e8222c5284`
- locator：內文「一般費率」「優惠費率 A」「優惠費率 B」三段。
- 查證日期：2026-07-14。
- 核對：原頁明寫每公噸 300／50／100 元二氧化碳當量，數值、單位與類型均符。
- verdict：`supported`。

### C2：unsupported

- 來源：環境部氣候變遷署「碳費專區」。
- pointer：`https://www.cca.gov.tw/affairs/carbon-fee-fund/2301.html`
- locator：「碳費機制」與「收費對象」段落。
- 查證日期：2026-07-14。
- 核對：原頁可支持碳費先行、優惠費率、徵收對象與自主減量機制；它不是多準則政策分析的方法文獻，也沒有比較後得出「客觀最佳」。
- verdict：`unsupported`。
- 修復選項：刪除「官方已證明最佳」；改成作者的框架選擇，並另補方法文獻。

## 標準庫實跑結果

`claim_audit.py summary` 輸出：

```json
{
  "claims": 2,
  "verdicts": {
    "supported": 1,
    "unsupported": 1
  },
  "gate": "block",
  "freshness_error": null
}
```

`claim_audit.py gate` 回傳 exit code `2`，並輸出 `block`。這阻止了原稿帶著「官方政策頁＝方法論證據」的錯置繼續接力。

## 批准後局部修訂

用 `revision_patch.py prepare` 將短稿切為 3 個區塊：標題 `B0001`、費率事實 `B0002`、方法宣稱 `B0003`。實作計畫已明確批准案例中的局部收窄示範，因此 patch 只批准 `B0003`：

> 本研究選擇多準則政策分析作為整理減碳誘因、成本分配、行政可行性與社會接受度的分析框架；此為作者的方法選擇，仍須另補政策分析方法文獻，不能由環境部政策頁直接證成。

實跑報告：

- total blocks：3。
- changed blocks：1。
- preserved blocks：2。
- preserved ratio：`0.6666666666666666`。
- 原稿 SHA-256：`63dd59c4800c95a9099899bfe42cf229a8d65be20884e998dff28944b80f6d44`。
- 新稿 SHA-256：`78bbec512cb917543e43c773c139ade2171441ba21c40c536d7e9382b8df6b2d`。

原稿沒有被覆蓋，`B0002` 費率事實原樣保留。

## 暴露的坑與寫回

1. **來源強不代表什麼都能撐。** 環境部是制度事實的第一手來源，但不是政策分析方法的證據。已寫回 `claim-audit` 範圍對齊與 eval。
2. **核書目不等於核主張。** DOI／URL 存在不能讓 gate 通過。已寫回 verdict 硬規。
3. **只改批准處要有機器證據。** 靠口頭提示不能證明其他段沒漂移；sidecar hash 與 preserved ratio 能留痕。已寫回 `academic-revision` 第 3.5 步與 eval。

## 驗證邊界

- 上述兩個官方頁面已於 2026-07-14 實際取得與核對。
- 本案例驗證政策事實主張、方法主張邊界與 Markdown patch；不代表 `claim-audit` 已經跨學科、跨資料類型穩定。
- 未執行付費模型矩陣，對應 skill 保持 Beta。
