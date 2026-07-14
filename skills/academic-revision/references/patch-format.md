# 局部修訂檔案規約

## 四種檔案

- `boya-revision-manifest/v1`：原稿 SHA-256、區塊 ID、類型、行數範圍與區塊 hash。
- `boya-revision-proposal/v1`：修改提案；每個 operation 只能是 `replace`，且必須有原 hash、新文字、理由與 issue ID。
- `boya-revision-patch/v1`：只收錄使用者明確批准的 operations，並記錄批准時間與說明。
- `boya-revision-report/v1`：原稿／新稿 hash、修改與保留區塊數、保留比例與每筆變更。

## Proposal 最小格式

```json
{
  "schema_version": "boya-revision-proposal/v1",
  "document_sha256": "<manifest 的原稿 hash>",
  "operations": [
    {
      "op": "replace",
      "block_id": "B0001",
      "expected_sha256": "<區塊 hash>",
      "new_text": "<新區塊文字>",
      "reason": "<為何要改>",
      "issue_ids": ["ISSUE-001"]
    }
  ]
}
```

## 區塊邊界

腳本以 Markdown 結構切區塊：標題單獨一塊；連續段落、清單、表格、引文、fenced code 各自成塊。空行與區塊間換行不納入替換範圍，因此未修改的文字與分隔字元可原樣保留。

v1 不支援新增、刪除、搬移、合併或拆分區塊。這些是結構修訂，要回 `paper-outline` 與使用者重新決定範圍。
