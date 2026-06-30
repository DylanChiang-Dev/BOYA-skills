# CONVENTIONS　博雅 skill 寫作公約

> 本文是新增或修改 skill 時的契約。誠信硬規見 [RULES.md](RULES.md)，版本策略與版權見 [AGENTS.md](AGENTS.md)，本文不重抄、只補「怎麼寫」。

## 1. 目錄約定

- 一個 skill 一個目錄：`skills/<name>/SKILL.md`，單檔，繁體中文優先。
- skill 名一律 kebab-case（如 `citation-verify`）。

## 2. frontmatter schema

```yaml
---
name: <kebab-case，與目錄同名>
description: <一句話功能 ＋ 觸發情境。必須寫明「當使用者說……時使用」，把觸發語寫進去，ROUTER 從這裡抽。誠信類技能須在此聲明「絕不編造／查無即標註」。>
---
```

- 僅 `name`、`description` 兩個欄位；不加版本欄位（版本走倉庫級 tag）。

## 3. SKILL.md 段落模板

依現有 12 個 skill 的共性，新 skill 至少含：

1. `# <英文名>　<中文名>`
2. `## 你的角色` — 一句話界定 agent 扮演誰、只做一件事。
3. `## 鐵律` — 編號硬規，誠信類必含「絕不編造」「查無≠偽造」「逐筆不抽樣」「留痕」。
4. `## 工作流` — 分步驟；標出「僅使用者能決定」的關卡。
5. 輸出格式 — 說明產出長什麼樣（表格／清單／報告）。

## 4. 出案例硬規

- 任一 skill **升版號前**，必須在 `examples/` 有 ≥1 篇實跑真錄（檔名 `日期-skill-案例.md`），記錄：用什麼真實材料跑、暴露了什麼坑、怎麼寫回規則。
- 對應的回歸斷言寫進 `evals/<skill>.md`（見 evals/README.md）。

## 5. 版號規則

見 [AGENTS.md](AGENTS.md) 版本策略（0.0.X／0.X.0／1.0.0），與 [RULES.md](RULES.md) 第 4 條三段式鐵律。本文不重述。

## 6. 命名規範

- skill 目錄／name：kebab-case。
- 案例檔：`YYYY-MM-DD-<skill 簡名>-<案例簡述>.md`。
- eval 檔：`evals/<skill>.md`，與 skill 同名。

## 7. 知識庫／模板／驗證日誌維護

- `knowledge/`：輕量參考卡，每份一頁量級；venue 分級嚴禁編造，未證實標「待補」。
- `templates/`：可填空骨架，非範文；結構與對應 skill 保持一致。
- `VERIFICATION.md`：skill 每次實測後補一行（版本／日期／材料／坑／example）。

## 8. 分層參考料

當一塊參考料超出 SKILL.md 該怎麼放，按三層收納 ＋ 一條軟警戒線。此規矩是**讀者不可見的內部維護決定**：書正文只教概念、按名字叫 skill，不描述目錄結構，故本節不影響書稿。

1. **預設單檔**。`SKILL.md` 只放 §3 四段（角色／鐵律／工作流／輸出格式）。常態，既有 skill 不動。
2. **跨 skill 複用的料 → repo 級共享庫**（同 §7）：參考卡進 `knowledge/`，可填空骨架進 `templates/`。
3. **該 skill 獨佔、又塞不進四段的長料 → `skills/<name>/references/`**。

**觸發判斷（語意為主、行數為輔）：**

- 主判據：是「長範例／長對照表／長清單」，**且**只服務這一個 skill、不被別的 skill 引用。
- 軟警戒線：SKILL.md **> 200 行**時強制檢查一次是否該拆；未超線不必拆。行數是提醒，非鐵律。

**決策樹：**

```
要新增一塊參考料 →
  能塞進 SKILL.md 四段且不臃腫？ → 留在 SKILL.md
  否則 → 會被別的 skill 用到嗎？
            會 → knowledge/ 或 templates/（共享）
            不會 → skills/<name>/references/（獨佔）
```

**邊界紅線**：`references/` 只收獨佔料；任何可能複用的料一律進共享庫，避免兩套機制打架。

> RPWS（`Master-cai/Research-Paper-Writing-Skills`）打包模式對照與取捨依據，見 [docs/superpowers/specs/2026-06-19-skill-reference-layering-design.md](docs/superpowers/specs/2026-06-19-skill-reference-layering-design.md)。

## 9. 工作痕跡表（work-trace-table）

> 把「AI 做苦工、你做判斷」變成一張看得見、可交付的證據表。標記定義**只在本節**出現一次；template 與各 skill 一律引用本節，不得重抄或自訂另一套標記。

### 9.1 五個標記（固定詞彙）

| 標記 | 意思 |
|---|---|
| 🧍 你判斷 | 使用者自己想的、自己決定的內容（論點、選擇、詮釋）。 |
| 🤖 AI待核 | AI 幫忙整理／起草的內容，使用者尚未核實。核實採納後改標 🧍。 |
| ✅ 已查證 | 引用或事實已驗證為真（例：DOI／來源對得上）。 |
| ❓ 待查 | 尚未查證，或查無、存疑（不確定真偽）。 |
| 🗑 捨棄 | 試過又放棄的方向，必須在「來源／原因」欄寫放棄原因。 |

### 9.2 表格欄位

| 內容（一句話） | 標記 | 來源／原因 | 日期 |
|---|---|---|---|

- 「內容」：一句話講清楚是什麼，不長篇。
- 「來源／原因」：✅ 填查證依據；🗑 填放棄原因；其餘可填一句說明或留空。
- 「日期」：可選，未填以 `—` 表示。

### 9.3 用法與邊界

- 表是**輔助、不強制**；但誠信類 skill（citation-verify／self-review／ai-disclosure）預設會幫忙填／讀。
- 標記只記「**誰做的**」這個事實，**不替使用者判斷對不對**——對不對永遠是使用者的事。
- **查無就標 ❓，絕不偽造 ✅**（守 RULES.md 與誠信鐵律「查無≠偽造」）。
- 🗑（捨棄）代表「作者已確認並放棄」，**只由作者標記**；skill 不得替作者把「查無」直接判成捨棄或造假。
- 立場是透明留痕，與 RULES.md 第 1 條一致；不收錄任何規避偵測用法。

## 10. 多語 README 同步

倉庫有四份 README：`README.md`（繁體中文，主檔）、`README.zh-CN.md`（简体中文）、`README.en.md`（English）、`README.ja.md`（日本語）。

- **默認只改繁體中文 `README.md`**：日常更新內容、補功能、修錯字，一律只動繁中主檔，其餘三語**不主動跟改**（避免半同步、語言版本各說各話）。
- 其他三語（zh-CN／en／ja）**僅在作者明確要求時才改**；一旦要改，**四語一起對齊**，不單獨只更新某一語。
- 繁中主檔是真實來源（source of truth）；三語版落後屬已知狀態，不視為錯誤，待作者下令時批次補齊。
