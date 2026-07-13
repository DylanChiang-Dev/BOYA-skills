# Boya 使用手冊

> 這份手冊給「已安裝 Boya，但不知道下一句該怎麼問」的研究者。若你只是想快速了解這個專案，先看 [README.md](README.md)；若你要讓 agent 判斷該用哪個 skill，看 [ROUTER.md](ROUTER.md)。

## 1. 這套 skill 適合誰

Boya 適合正在做文組／人文社科研究的人：大學部專題、碩博士論文、期刊投稿前整理、自我審查、口試準備都可以用。

它特別適合三種情況：

- 你知道自己要寫論文，但不知道下一步該做什麼。
- 你手上有資料、文獻或草稿，想請 AI 幫你整理、查核、挑問題。
- 你想用 Claude Code / Codex 協作研究，但不希望 AI 替你編文獻、代寫結論或越過學術倫理紅線。

Boya 不適合用來做這些事：

- 一鍵產生整篇論文。
- 讓 AI 替你決定研究問題、方法選擇或投稿目標。
- 美化不存在的引用、資料或期刊規範。
- 規避學校、期刊或指導教授對 AI 使用的揭露要求。

## 2. 安裝後第一步：先問 boya

如果你不知道該喚哪個 skill，直接從 `boya` 開始。它是唯一推薦入口：第一次呼叫後會依你手上的產物定位、執行下一個 skill，並在每輪保存檢查點。研究問題、框架、方法、論證與取捨等關卡一律停下等你拍板；你回答後會直接續跑，不必再次輸入 `boya`。完整接力需要整套 Boya，缺少下游 skill 時會明確停止並報告缺失 ID。

可以這樣問：

```text
我正在寫一篇關於生成式 AI 與大學生學習行為的論文，目前只有一個模糊題目。請用 boya 幫我判斷現在在哪一階段，下一步該用哪個 Boya skill。
```

或：

```text
我已經有初稿和參考文獻清單，想在交給指導教授前自查。請用 boya 幫我排一個投稿前檢查順序。
```

`boya` 的輸出通常會告訴你：

- 你現在最像哪個研究階段。
- 應該先用哪個 skill。
- 進入下一階段前，要交出什麼產出物。
- 哪些判斷不能交給 AI。

## Boya 2.0 名稱遷移

2.0 不保留舊 skill 目錄，避免舊、新名稱同時被載入。升級前先列出現有安裝目錄，確認沒有自訂修改；有修改先備份，再移除舊副本並複製完整 2.0 `skills/`。不可只把新目錄蓋上去。

| 1.x 舊 ID | 2.0 新 ID |
|---|---|
| `topic-refine` | `research-question` |
| `lit-discovery` | `literature-search` |
| `citation-verify` | `reference-check` |
| `lit-matrix` | `literature-analysis` |
| `framework-build` | `theoretical-framework` |
| `method-design` | `research-design` |
| `outline-builder` | `paper-outline` |
| `style-tune` | `academic-revision` |
| `self-review` | `manuscript-review` |
| `defense-prep` | `thesis-defense-prep` |
| `venue-fit` | `journal-fit` |
| `cite-format` | `citation-format` |
| `abstract-bilingual` | `bilingual-abstract` |
| `ai-disclosure` | `ai-use-disclosure` |

`boya` 的技術 ID 不變，2.0 展示名改為「博雅研究助手」。完成遷移後應只看到 15 個目錄。

## 3. 從研究階段選 skill

如果你已經知道自己卡在哪裡，可以直接選對應 skill。

| 你現在想做什麼 | 優先使用 |
|---|---|
| 題目太大、太散、不知道能不能做 | `research-question` |
| 有題目、還沒文獻清單，要先找該讀哪些 paper | `literature-search` |
| 檢查參考文獻是不是真的存在 | `reference-check` |
| 讀幾篇文獻、整理共識與分歧 | `literature-analysis` |
| 文獻讀完，要把理論透鏡／主框架定下來 | `theoretical-framework` |
| 想研究方法、訪談大綱、問卷或資料設計 | `research-design` |
| 搭論文章節、整理段落論證鏈 | `paper-outline` |
| 潤段落、去 AI 腔、校準成自己的文風 | `academic-revision` |
| 交出去前模擬審查、找漏洞 | `manuscript-review` |
| 口試前壓簡報、練問題 | `thesis-defense-prep` |
| 寫 AI 使用揭露聲明 | `ai-use-disclosure` |
| 統一 APA / Chicago / MLA 等引用格式 | `citation-format` |
| 從定稿濃縮中英摘要與關鍵詞 | `bilingual-abstract` |
| 不確定下一步 | `boya` |
| 投稿前對標目標刊作者須知 | `journal-fit` |

若你要讓 agent 自己判斷，請它先讀 [ROUTER.md](ROUTER.md)。

## 4. 一條完整工作流怎麼跑

典型順序不是硬規定，但可以作為起點：

```text
research-question
→ literature-search
→ reference-check
→ literature-analysis
→ theoretical-framework
→ research-design
→ paper-outline
→ academic-revision
→ manuscript-review
→ citation-format / bilingual-abstract
→ ai-use-disclosure
→ thesis-defense-prep
```

如果你是從一份已經寫好的草稿開始，不需要回到第一步。可以直接從 `manuscript-review`、`citation-format`、`bilingual-abstract` 或 `ai-use-disclosure` 開始。

如果你是準備投稿，建議先跑：

```text
manuscript-review
→ reference-check
→ citation-format
→ ai-use-disclosure
→ bilingual-abstract
→ journal-fit
```

這裡的原則是：先確認論文本身、引用與揭露沒有硬傷，再拿定稿對標目標刊。不要反過來先問「這本刊要什麼」，再讓 AI 猜一份投稿規範。

## 5. templates / knowledge / evals 怎麼用

### templates/

`templates/` 是可填空骨架，不是範文。你可以把它們複製到自己的研究專案裡填寫，例如：

- `templates/paper-imrad.md`：量化或實證論文常用骨架。
- `templates/paper-思辨.md`：人文思辨型論文骨架。
- `templates/paper-政策.md`：政策分析型論文骨架。
- `templates/defense-slides.md`：口試簡報骨架。
- `templates/journal-fit-checklist.md`：投稿對標表。

使用模板時，請把空格填成你的真實材料；查不到的資料保留「待補」，不要請 AI 猜。

### knowledge/

`knowledge/` 是輕量參考卡，用來提醒你該查什麼、怎麼分辨，而不是資料庫。

- `knowledge/venues.md`：選刊方法與帶來源、查證日期的策展期刊事實表；它不是即時完整資料庫，待補／待複查項承重前仍須回官網。
- `knowledge/zh-academic-style.md`：中文學術寫作常見問題與修法。

### evals/

`evals/` 是給維護者和進階使用者看的回歸斷言。它回答的是：「這個 skill 之後改版時，哪些行為絕對不能退化？」

一般研究者不必先讀 `evals/` 才能使用 Boya；但如果你想 fork 這套 skill，請先讀對應 eval。

## 6. Boya 2.0 驗證狀態

1.0 工作流的真實案例與 evidence ledger 全部保留。2.0 更換技術 ID、觸發描述與自動接力協定，因此 15 個 skill 暫列 Beta；結構化案例與手動模型 runner 已就位。

其中 `journal-fit` 仍有三條特別重要的限制：

- 不憑記憶生成期刊清單、影響因子、排名、接受率或作者須知；策展資料也必須有來源與查證日期。
- 目標刊規範必須來自你提供或實際取得的原始來源；查不到就標「待補」。
- 它只指出差距，不替你決定投不投，也不代寫修改稿。

維護者顯式跑模型矩陣後，硬門與誠信規則須 3/3 通過，其他 MUST 行為須達 90%，才恢復全套 Stable。CI 只跑靜態契約、案例結構與離線工具測試，不自動消耗模型額度。

## 7. 誠信紅線

Boya 的底線很簡單：AI 是副駕駛，不是機長。

你可以請 AI 做：

- 查核引用是否存在。
- 整理文獻之間的主張、證據與方法。
- 幫你把訪談題、問卷題或章節骨架整理成可討論版本。
- 模擬審稿人或口試委員提出問題。
- 幫你把已存在的材料收斂成摘要、聲明或檢查清單。

你不應該請 AI 做：

- 編造不存在的文獻、資料、作者須知或期刊規範。
- 替你決定研究問題與方法選擇。
- 替你下結論，或把你沒有證據的說法寫得像已證實。
- 把 AI 使用藏起來。

凡是查不到、沒有來源、你自己也不確定的內容，都應該標「待補」或「需人工確認」。

## 8. 常見情境範例

### 我只有一個模糊題目

```text
請用 research-question 幫我把「AI 對大學生學習的影響」縮成 3 個可研究題目。不要替我決定最後題目，只追問並指出每個題目的可行性風險。
```

### 我有一份參考文獻清單

```text
請用 reference-check 檢查這份參考文獻是否真實存在。查不到的不要直接判定偽造，請標成待人工確認，並說明你查了哪些來源。
```

### 我有五篇文獻想整理

```text
請用 literature-analysis 幫我把這五篇文獻整理成主張、證據、方法、可挑戰處四欄，最後做一張共識與分歧表。
```

### 我已經有初稿

```text
請用 manuscript-review 模擬方法論審稿人、領域審稿人、魔鬼代言人與主編，幫我挑出這篇初稿最需要修的問題。請分成必改、可辯、誤讀。
```

### 我要投稿前檢查

```text
我已經有定稿和目標刊作者須知。請用 journal-fit 幫我做投稿對標，只列 must-fix、should-fix、待補查證，不要替我改稿，也不要補任何我沒提供的期刊規範。
```

## 9. 維護者入口

如果你要修改或新增 skill，請先讀：

- [AGENTS.md](AGENTS.md)：倉庫定位、版本策略、版權模式。
- [CONVENTIONS.md](CONVENTIONS.md)：skill 寫作公約。
- [RULES.md](RULES.md)：誠信鐵律。
- [VERIFICATION.md](VERIFICATION.md)：驗證狀態與 evidence ledger。
- [evals/README.md](evals/README.md)：回歸斷言格式。

新增 skill 的基本節奏：

1. 先寫 `evals/<skill>.md`，定義 MUST / MUST NOT。
2. 再寫 `skills/<skill>/SKILL.md`。
3. 若需要可填空骨架，新增 `templates/<name>.md`。
4. 接入 `ROUTER.md`。
5. 未實測前只能標 Draft；拿真實材料跑過、把坑寫回規則後，才考慮升 Beta 或 Stable。
