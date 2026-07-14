# Research Record Schema

## 頂層欄位

- `schema_version`：固定 `boya-research-record/v1`。
- `project`：`id`、`title`、`created_at`。
- `checkpoint`：最新 `boya_checkpoint`；尚未同步時為 `null`。
- `artifacts`：材料與產物指標。
- `decisions`：人工決策。
- `unknowns`：未知與阻斷項。
- `events`：只追加的變更紀錄。
- `updated_at`：UTC ISO 8601 時間。

## Artifact

必填：`id`、`type`、`title`、`pointer`、`status`、`added_at`。

`status` 只能是：

- `present`：指標指向的材料或產物已核對存在；不代表內容正確或品質良好。
- `missing`：本輪找不到指向材料。
- `superseded`：已被新版本取代。

## Decision

必填：`id`、`question`、`status`、`choice`、`evidence_ids`、`proposed_at`、`confirmed_at`、`confirmed_by`。

`status`：`pending`、`confirmed`、`rejected`、`superseded`。`confirmed` 時 `choice` 與 `confirmed_at` 必填，`confirmed_by` 必須是 `user`。`evidence_ids` 只能引用已登錄 artifact。

## Unknown

必填：`id`、`question`、`status`、`created_at`。

`status`：`open`、`resolved`、`blocked`。本標準庫 v1 只新增 unknown，解決與阻斷狀態需使用者在檔案中明確記錄新證據後再更新。

## Checkpoint

欄位固定與 `boya` 一致：

- `stage`：1–14 的階段號，或 `null` 表示尚在定位。
- `status`：`locating`、`running`、`waiting_for_user`、`ready_to_advance`、`blocked`、`complete`。
- `artifacts_present`：artifact ID 陣列，每筆必須存在且狀態為 present。
- `decision_required`：待使用者決定的問題；無時為空字串。
- `decision_status`：`pending`、`confirmed`、`not_applicable`。
- `decision_id`：決策項 ID；需人工決定時必填。
- `active_skill`、`next_skill`：skill ID 或 `null`。

`ready_to_advance` 必須同時滿足：所有 artifacts_present 存在且 present；decision_status 為 confirmed 時，decision_id 引用已 confirmed 決策；若本階段無人工決策，則為 not_applicable。
