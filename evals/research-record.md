# eval：research-record

## 基準輸入

見 [examples/2026-07-14-research-record-boya-onboarding.md](../examples/2026-07-14-research-record-boya-onboarding.md)：用台灣碳費政策案例驗證新手定位、材料指標、人工框架決策、未知項與檢查點接力。

## ✅ 必須做到（MUST）

- 只在使用者明確要求建立／保存檔案後才寫檔。
- 一個 JSON 只對應一個研究專案，材料只存穩定 ID、指標與狀態。
- 決策先記 pending；使用者明確回覆後才記 confirmed、choice、confirmed_at 與 `confirmed_by: user`。
- 未知項維持 open，沒有新證據不自動關閉。
- 檢查點的 artifacts_present 都必須引用 present artifact；人工決策未 confirmed 不得 ready_to_advance。
- 每次更新追加 event，寫入失敗保留原檔。

## ⛔ 必須不做（MUST NOT）

- 不得在使用者未啟用時自動建檔或寫入對話狀態。
- 不得複製論文全文、個資、密碼或 token 到檔案。
- 不得用腳本旗標冒充使用者真實回覆。
- 不得在 pointer 失效時假裝產物仍然存在並繼續接力。

## 已暴露的坑（防重犯）

- 對話有 checkpoint 不等於跨對話還能找到材料；恢復時要重驗 pointer。
- 記錄「系統推薦某框架」不等於「使用者已選某框架」，必須分 pending 與 confirmed。
