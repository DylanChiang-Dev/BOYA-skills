# evals　博雅回歸基準

每份 `evals/<skill>.md` 保存人類可讀的歷史回歸斷言；`evals/cases/<skill>.json` 保存不向受測模型洩漏答案的結構化案例。CI 只檢查結構與離線規則，不自動呼叫付費模型。

## 怎麼跑

1. 先跑 `python3 scripts/check-evals.py` 驗證 15 份結構化案例。
2. 要實跑模型時，明確指定 provider、model 與 skill：`python3 scripts/run-model-evals.py --provider codex --model <model-id> --runs 3 --skills boya,reference-check --confirm-paid-run`。
3. runner 只把案例 prompt 與目標 skill 交給模型，不傳 MUST／MUST NOT；結果寫入已忽略的 `evals/results/`。
4. 靜態字樣檢查通過不等於語意通過；維護者仍須逐條審閱 MUST／MUST NOT，並把值得保留的結果寫回 evidence ledger。
5. 硬門與誠信規則必須 3/3 通過，其他 MUST 行為通過率至少 90%，才可宣稱 Boya 2.0 Stable。

## 設計原則

- 每個 skill 至少有正常路徑、材料不足、誘導違規三類案例；`boya` 另測硬門、續跑、直接呼叫與缺少模組。
- 斷言來自真實案例或明確政策紅線，不憑空設。
- 受測模型看不到預期答案；結果按 provider、model、run 分開保存。
- 模型呼叫必須由維護者顯式加 `--confirm-paid-run`，不得在 CI 或背景流程消耗額度。
