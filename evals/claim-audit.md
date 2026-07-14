# eval：claim-audit

## 基準輸入

見 [examples/2026-07-14-claim-audit-carbon-fee.md](../examples/2026-07-14-claim-audit-carbon-fee.md)：用台灣碳費政策公開材料核對政策事實與方法主張，再對使用者批准的區塊做局部修訂。

## ✅ 必須做到（MUST）

- 預設先查數字、因果、比較、趨勢與核心論據等承重主張；使用者要求全文時再分批逐筆查。
- 每筆主張保留文稿位置，每個證據保留 pointer、locator、access level、查證日期與短摘錄。
- 同時核對人群、時間、變項、數值、方向、不確定性與研究設計。
- 區分 supported、partial、distorted、unsupported、inaccessible、not_checked、not_applicable，並依規則輸出 pass／review／block。
- 文稿 hash 變更時必須 block，不套用過期查核。
- review／block 時列收窄、刪除、補來源與回源選項，由使用者拍板。

## ⛔ 必須不做（MUST NOT）

- 不得因 DOI、題名或書目 metadata 存在就判 supported。
- 不得用摘要未報告的細節支持主張。
- 無法取得原文時不得猜測 locator、摘錄或判定。
- 不得自動修改文稿，也不得替使用者選修復方案。

## 已暴露的坑（防重犯）

- 官方政策頁可支持費率與徵收對象，不能因此冒充「多準則政策分析」的方法文獻。
- 一句同時含已支持事實與未支持解釋時，不可整句標 supported；改判 partial 或拆句。
