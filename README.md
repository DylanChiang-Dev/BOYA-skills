語言：[繁體中文](README.md) | [简体中文](README.zh-CN.md) | [English](README.en.md) | [日本語](README.ja.md)

<div align="center">

# 博雅 Boya

### 給文組／人文社科研究者的 AI 論文工作流

**不會寫程式，也可以用 Open Science Desktop / Codex / Claude Code，把一篇論文從「模糊題目」一步步推到「可以交出去」。**

<strong>AI 做苦工，你做判斷。</strong><br/>
Boya 幫你磨題、查引用、讀文獻、設計方法、搭大綱、修初稿、自我審查、準備口試與投稿對標；<br/>
但不替你編文獻、不代寫結論、不幫你隱藏 AI 使用。

*An Open Science Desktop / Codex / Claude Code workflow for liberal-arts and social-science researchers — from vague idea to submission-ready paper, no coding required.*

<br/>

[![Stars](https://img.shields.io/github/stars/DylanChiang-Dev/BOYA-skills?style=for-the-badge&logo=github&color=ffca28)](https://github.com/DylanChiang-Dev/BOYA-skills/stargazers)
[![Forks](https://img.shields.io/github/forks/DylanChiang-Dev/BOYA-skills?style=for-the-badge&logo=github&color=42a5f5)](https://github.com/DylanChiang-Dev/BOYA-skills/network/members)
[![License: MIT](https://img.shields.io/badge/License-MIT-4caf50?style=for-the-badge)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-17-7e57c2?style=for-the-badge)](#十七個-skill)
[![version](https://img.shields.io/badge/version-2.1.0-7e57c2?style=for-the-badge)](MEMORY.md)
[![繁體中文](https://img.shields.io/badge/繁體中文-First-e4002b?style=for-the-badge)](#)

</div>

---

如果你正在寫論文，Boya 不是要把你變成工程師，而是把指導教授、研究方法課、投稿前檢查清單裡那些「沒人一次講清楚」的步驟，拆成 agent 可以陪你走的流程。

你可以從這裡開始：

- **題目太大**：把一個模糊想法縮成可研究問題。
- **文獻太亂**：查引用真偽，整理文獻矩陣與綜述線索。
- **初稿要交**：先自我審查、排引用格式、寫 AI 使用揭露，再準備口試或投稿。

简体中文与中国大陆高校使用说明见 [README.zh-CN.md](README.zh-CN.md)。English and Japanese introductions are available in [README.en.md](README.en.md) and [README.ja.md](README.ja.md).

完整使用手冊見 [GUIDE.md](GUIDE.md)：安裝後從哪裡開始、不同研究階段該用哪個 skill、templates / knowledge / evals 怎麼配合。

一句話講清楚這個倉庫在做什麼：**把指導教授腦子裡那種「看三篇文獻就知道這題能不能做」的判斷，盡量拆成明白的規則與提問，寫成你隨時叫得動的流程。** 它縮小資訊差，但不替你做研究。

## 🧭 核心信念

> ### AI 是副駕駛，不是機長。

Boya 的最高設計原則是**人類在環（human-in-the-loop）**：流程可以自動接力，但每一個「只有你能決定」的關卡都會**硬停下來等你拍板**——這也是它和「全自動論文機」的唯一分界。底下四條，都是這個原則的展開。

- **苦工外包，判斷自留。** skill 處理檢索、查核、格式、模擬提問；研究問題、方法選擇與詮釋，永遠是你的。
- **凡引用必回源。** `reference-check` 只證明文獻存在與書目相符；承重主張要再用 `claim-audit` 定位原文核對，修不修仍由你決定。
- **透明而非遮掩。** 全部 skill 鼓勵留痕與 AI 使用揭露，目標是品質，不是隱藏協作事實。
- **人類在環，不是一鍵跑完。** 這不是全自動論文機——流程會自己接力喚起下一步，但到「只有你能決定」的關卡就停；每一步 AI 幹活、你握方向盤。

## 🗺️ 工作流地圖

從一個念頭到一篇可以投出去的論文，十七個 skill 各守一段，`boya` 在最上層導航：

```mermaid
flowchart TD
    Start([💡 一個念頭]) --> S1[磨題目<br/>research-question]
    S1 --> S2[找文獻<br/>literature-search→reference-check]
    S2 --> S3[讀文獻<br/>literature-analysis]
    S3 --> SF[理論框架<br/>theoretical-framework]
    SF --> S4[研究設計<br/>research-design]
    S4 --> S5[搭骨架<br/>paper-outline]
    S5 --> S6[寫初稿<br/>academic-revision]
    S6 --> S7[自我審查<br/>manuscript-review]
    S7 --> SC[承重主張回源<br/>claim-audit]
    SC --> S8[定稿・口試<br/>thesis-defense-prep · citation-format · bilingual-abstract]
    S8 --> S9[投稿對標<br/>journal-fit]
    S9 --> S10[倫理揭露<br/>ai-use-disclosure]
    S10 --> End([📄 可投出去的論文])
    RM{{boya<br/>全程導航書脊}} -.隨時定位你在哪.-> S1
    RM -.該喚哪個 skill.-> S5
    RM -.哪些只有你能決定.-> S10
    RR{{research-record<br/>選用專案檔案}} -.啟用後同步檢查點.-> RM
```

## 📦 十七個 skill

> **一個入口＋十六個專用 skill＝十七個**。使用者只需先呼叫 `boya`，它會自動接力；熟練使用者仍可直接呼叫任何專用 skill。1.0 的真實案例證據保留，2.0 新增主張查核、選用研究檔案、批准後局部修訂與逐題新手定位；目前全套列為 Beta，待顯式模型矩陣通過後恢復 Stable。

### 核心 · 一階段一個

| skill | 功能 | 階段 |
|---|---|---|
| [`research-question`](skills/research-question) | 蘇格拉底式磨題：問題意識 → 有界發散 → 三問收斂（新／可行／誰在乎）→ 指導教授模擬 → 一頁研究問題簡報；只追問不給答案 | 磨題 |
| [`literature-search`](skills/literature-search) | 文獻探勘：把研究問題拆成檢索策略，用 OpenAlex / Crossref / Semantic Scholar 撈**待核候選清單**、按相關性分層；選用「先讀哪篇」出處提示（回查 CSSCI／TSSCI／北大核心／AMI核心／SSCI／A&HCI 官方名單、標版次年份，查不到標待查），交棒查核與精讀；絕不編造、查無標待人工 | 找文獻 |
| [`reference-check`](skills/reference-check) | 參考文獻查核：以公開 API 核對存在性與書目欄位，抓 DOI 貼錯、拆名與已查來源未找到；查無不判虛構 | 找文獻 |
| [`literature-analysis`](skills/literature-analysis) | 文獻精讀與矩陣：單篇四欄筆記（主張／證據／方法／可挑戰處）、跨篇對照矩陣、綜述對話地圖 | 讀文獻 |
| [`theoretical-framework`](skills/theoretical-framework) | 理論框架定錨：從文獻地圖攤候選框架（解釋什麼／理論代價／庫存支撐）、推薦分層（主框架→中介機制→實證抓手→落點）、硬 GATE 讓你拍板主框架；另有輔助框架嵌入與逆向體檢兩模式。 | 框架 |
| [`research-design`](skills/research-design) | 研究設計：方法地圖、起草訪談大綱／問卷＋人工校準、角色扮演預訪談、編碼建議（詮釋留你）、統計謬誤核驗 | 設計 |
| [`paper-outline`](skills/paper-outline) | 論文骨架：選結構模式（IMRaD／綜述／思辨／政策）、長出大綱、段落論證鏈 claim–evidence–warrant（專補推理橋） | 大綱 |
| [`academic-revision`](skills/academic-revision) | 學術潤稿：依舊文校準作者聲音、修改既有段落、診斷套話與空洞結構；選用 sidecar hash 與批准清單保證「只改這幾段」 | 初稿 |
| [`manuscript-review`](skills/manuscript-review) | 自我審查（**模擬審查**）：一桌審稿人（方法論／領域／魔鬼代言人／主編）輪審＋誠信自查＋意見分級（必改／可辯／誤讀） | 自審 |
| [`claim-audit`](skills/claim-audit) | 主張來源查核：優先回源核對數字、因果、比較、趨勢與核心論據；定位原文、留 verdict 與 pass/review/block，不把 DOI 存在當成內容支持 | 主張查核 |
| [`thesis-defense-prep`](skills/thesis-defense-prep) | 口試準備：論文 → 簡報骨架、分層出難題（澄清／方法／理論／貢獻／陷阱）、答詢策略（含英文） | 口試 |
| [`journal-fit`](skills/journal-fit) | 投稿對標：用定稿對上目標 venue 的真實作者須知，列出 must-fix／should-fix／待補查證；不編期刊規範、不代決定投哪裡 | 投稿 |
| [`ai-use-disclosure`](skills/ai-use-disclosure) | AI 使用揭露：盤點使用 → 抄襲／代寫／輔助三分法 → 按目標機構格式生成誠實具體聲明 → 留痕自證 | 揭露 |

### 收尾 · 定稿階段

| skill | 功能 | 階段 |
|---|---|---|
| [`citation-format`](skills/citation-format) | 引用格式整理：APA／Chicago／MLA 轉換與全文統一、隨文引註↔文末清單一一對應（抓孤兒）、缺欄位標註不編造；**只管格式不驗真偽** | 格式 |
| [`bilingual-abstract`](skills/bilingual-abstract) | 中英雙語摘要：從定稿濃縮中文摘要＋英文摘要（按英文慣例重寫、非逐字翻譯）＋中英關鍵詞；只濃縮不新增、數字逐一核對 | 摘要 |

### 導航 · 書脊

| skill | 功能 | 階段 |
|---|---|---|
| [`boya`](skills/boya) | **唯一推薦入口**：第一次呼叫後自動定位、執行下一個 skill、保存檢查點；研究問題、框架、方法與取捨一律硬停等你拍板 | 導航 |
| [`research-record`](skills/research-record) | 研究專案檔案：使用者明確啟用後，保存材料指標、人工決策、未知項與 boya checkpoint；不複製全文、不自動替使用者確認決策 | 全程選用 |

## 🚀 安裝

> Boya 2.0 已更換 14 個技術 ID。從 1.x 升級時不可只覆蓋複製，否則舊目錄會與新 skill 並存、造成重複觸發；請按 [GUIDE.md 的 2.0 遷移表](GUIDE.md#boya-20-名稱遷移) 先確認並移除舊安裝副本。新使用者安裝整套後，只需從 boya 開始。

### 方式一：請 agent 自動安裝整套 Boya（推薦）

打開 Open Science Desktop、Codex 或 Claude Code，把這句話貼進去：

```text
幫我從 https://github.com/DylanChiang-Dev/BOYA-skills 安裝全部 17 個 Boya skills，不要只安裝 reference-check。若在 Open Science Desktop，請安裝到當前工作區的 .opencode/skills/；否則先判斷目前的 agent 環境與可用的 skills 目錄。請說明會寫入哪些路徑，等我確認後再執行。
```

常見目標路徑：

- Open Science Desktop（推薦）：當前工作區 `.opencode/skills/`
- Codex：全域 `~/.agents/skills/`；專案內 `.agents/skills/`；若使用 Codex 內建 `$skill-installer`，也可能寫入 `$CODEX_HOME/skills/`（預設常見為 `~/.codex/skills/`）
- Claude Code：全域 `~/.claude/skills/`；專案內 `.claude/skills/`

只想安裝單一技能時，才把「全部 Boya skills」改成具體 skill 名，例如 `reference-check`。

### 方式二：手動複製整套 skills

每個 skill 目錄只要包含 `SKILL.md` 就能被辨識。

**Open Science Desktop 工作區安裝（推薦）**

```bash
git clone https://github.com/DylanChiang-Dev/BOYA-skills.git

mkdir -p .opencode/skills
cp -r BOYA-skills/skills/* .opencode/skills/
```

安裝後應在 Skills 頁看到全部 17 個 Boya skills。從 `boya` 開始，不要用 Open Science Desktop 內建的全自動 `ai4s-agent` 取代 Boya 的人工決策硬門。

**Codex 全域安裝（所有專案可用）**

```bash
git clone https://github.com/DylanChiang-Dev/BOYA-skills.git

mkdir -p ~/.agents/skills
cp -r BOYA-skills/skills/* ~/.agents/skills/
```

若你的 Codex 明確使用 `$CODEX_HOME/skills/` 載入技能，改用：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -r BOYA-skills/skills/* "${CODEX_HOME:-$HOME/.codex}/skills/"
```

**Codex 專案安裝（只給當前專案用）**

```bash
mkdir -p .agents/skills
cp -r BOYA-skills/skills/* .agents/skills/
```

裝好後在 Codex 裡可用 `$reference-check` 這類明確呼叫，也可以直接用自然語言觸發，例如：「幫我查核這份參考文獻的真偽」。

**Claude Code 全域安裝（所有專案可用）**

```bash
mkdir -p ~/.claude/skills
cp -r BOYA-skills/skills/* ~/.claude/skills/
```

**Claude Code 專案安裝（只給當前專案用）**

```bash
mkdir -p .claude/skills
cp -r BOYA-skills/skills/* .claude/skills/
```

裝好後在 Claude Code 裡直接用自然語言觸發，例如：「幫我查核這份參考文獻的真偽」。

## 🔬 實測案例

每個 skill 都拿**真實研究材料**跑過、把暴露的坑寫回規則——多數用在作者自己那本碩士論文上，是一條工作流全鏈的真實示範。

驗證狀態採三層：`Draft`、`Beta`、`Stable`。1.0 工作流的真實案例與 evidence ledger 全部保留；2.0 因技術 ID、觸發描述、自動接力協定與四項新能力均有變更，目前 17 個 skill 暫列 **Beta**。結構化案例與手動模型 runner 已就位，通過硬門／誠信 3/3 與其他 MUST ≥90% 後才恢復 Stable。詳見 [`VERIFICATION.md`](VERIFICATION.md)。

| # | 案例 | 一句話戰果 |
|---|---|---|
| 001 | [reference-check 查作者碩論](examples/2026-06-12-master-thesis-case.md) | 47 筆全量查核，抓到 **3 筆 DOI 貼錯**、1 筆拆名、11 筆出處不全，附公開勘誤表 |
| 002 | [literature-analysis 整理碩論文獻](examples/2026-06-13-litmatrix-thesis-litreview.md) | 5 篇異質文獻分群做矩陣；暴露「引用語境≠主題／異質語料分群」 |
| 003 | [manuscript-review 審教學稿](examples/2026-06-13-selfreview-teaching-chapter.md) | 暴露「文稿類型錯配／證據-宣稱規模不相稱／絕對宣稱」 |
| 004 | [thesis-defense-prep 模擬碩論口試](examples/2026-06-14-defenseprep-thesis.md) | 分層出真考題；暴露「論文階段誤判／漏質性可推論性」 |
| 005 | [research-question 磨「兩岸關係」題](examples/2026-06-14-topicrefine-cross-strait.md) | 在「日台非官方安全」踩出可行性紅燈（資料閉門），示範換做法保住問題 |
| 006 | [research-design 檢視碩論設計](examples/2026-06-14-methoddesign-thesis.md) | 暴露「對象分層要想清楚／AI 扮受訪者太乖」 |
| 007 | [paper-outline 檢視碩論骨架](examples/2026-06-14-outlinebuilder-thesis.md) | 暴露「完整性幻覺（齊全≠論證線）／warrant 缺席」 |
| 008 | [academic-revision 掃碩論 AI 腔](examples/2026-06-14-styletune-thesis.md) | 一本談 GenAI 的論文緒論本身讀起來像 AI 生成；暴露「AI 腔的專業偽裝」 |
| 009 | [ai-use-disclosure 處理重度 AI 協作聲明](examples/2026-06-14-aidisclosure-heavy-ai-use.md) | 暴露「重度使用時 AI 不敢說」 |
| 010 | [bilingual-abstract 生碩論中英摘要](examples/2026-06-14-abstractbilingual-thesis.md) | 抓到「官方關鍵詞中英本身不對齊／『顯著』是統計詞別照搬」 |
| 011 | [citation-format 排碩論參考文獻](examples/2026-06-14-citeformat-thesis.md) | 坐實「先驗後排——未查核清單＝錯資料的漂亮包裝」 |
| 012 | [boya（原 research-roadmap）導航完整研究工作流](examples/2026-06-14-researchroadmap-workflow.md) | 抓到最大退化「目錄朗讀機」——要依產出物倒推、非按線性順序 |
| 013 | [journal-fit 對標作者碩論與《公共行政學報》](examples/2026-06-18-venuefit-thesis-jpa.md) | 坐實「不編作者須知」與「學位論文轉期刊先判文稿類型」，作為 journal-fit 首輪實測 |
| 014 | [theoretical-framework 定錨日台半導體框架](examples/2026-06-21-framework-jasm.md) | 固化理論框架定錨：不堆框架沙拉、不編承重文獻、硬 GATE 讓研究者拍板主框架 |
| 015 | [paper-outline 搭 silicon sampling 思辨型大綱](examples/2026-06-27-outlinebuilder-silicon-sampling.md) | 正向搭骨架實測 topic-sentence 前置，撞出思辨型兩坑：讓步句冒充主題句、段主題句覆讀章論點 |
| 016 | [literature-search 中文題全鏈探勘](examples/2026-06-30-litdiscovery-genai-assessment-taiwan.md) | 中文精準題名反查命中真實 DOI，補齊「中文題探勘→候選分層→venue 待查」全鏈 |
| 017 | [theoretical-framework 台灣碳費政策分析框架](examples/2026-06-30-framework-carbon-fee-policy.md) | 補足政策分析型分流：政策問題、分析維度、評估準則、政策代價與 GATE 全跑通 |
| 018 | [journal-fit 對標 JALT 英文高教評量稿](examples/2026-06-30-venuefit-jalt-genai-assessment.md) | 核 JALT submissions page，坐實文章頁不等於作者須知、AI 揭露與 APA 7 必須回真實來源 |
| 019 | [claim-audit 查台灣碳費主張＋批准後局部修訂](examples/2026-07-14-claim-audit-carbon-fee.md) | 一筆費率 supported、一筆方法宣稱 unsupported 直接 block；只改批准的 1/3 區塊，原稿不覆蓋 |
| 020 | [research-record 續接碳費政策案例＋boya 新手走查](examples/2026-07-14-research-record-boya-onboarding.md) | 材料只存指標、決策分 pending/confirmed、未知仍 open；新手資訊已齊時不重問 |

## 🧱 設計原則

- **人類在環（human-in-the-loop）**：全庫最高原則——流程會自動接力喚起下一步，但每個「只有你能決定」的關卡都硬停下來等你拍板。這是 boya 與「全自動論文機」的分界，底下其餘原則都服務於它。
- **單文件 skill**：每個 skill 一個 `SKILL.md`，看得懂、改得動，歡迎 fork 改造成你的領域版本。
- **不編造**：所有 skill 內建「查無即標註、不確定即說明」的硬規則。
- **用—磨—寫**：每個 skill 都先拿真實材料跑、把坑寫回規則，才升版號——不閉門造框架。
- **中文優先**：為華語人文社科研究場景設計（含台灣學術環境的引用與政策語境）。
- **輕量參考層**：`VERIFICATION.md` 彙總實測證據，`knowledge/` 放 venue 與中文學術寫作速查卡，`templates/` 放可填空論文與口試骨架。
- **不做重型自動化框架**：不引入 `_shared/` fragments、`manifest.yaml` 分片載入、多 agent 長跑 orchestrator；除非某個 skill 真的長到不可讀，才把少量共用材料外移。

## 💬 加入討論

Bug、公開問題與功能建議請使用 [GitHub Issues](https://github.com/DylanChiang-Dev/BOYA-skills/issues)。Telegram 群維持免費交流；需要作者直接提供安裝、使用答疑與版本更新導讀，可加入 [BOYA 作者答疑群（¥199／年）](https://boya-website.pages.dev/zh-hant/community/)。Skills 本身始終依 MIT 免費提供。

## ⭐ Star 趨勢

如果這個倉庫幫到你，按顆星——讓更多卡在論文裡、身邊沒有人可商量的文組生看到它。

[![Star History Chart](https://api.star-history.com/svg?repos=DylanChiang-Dev/BOYA-skills&type=Date)](https://star-history.com/#DylanChiang-Dev/BOYA-skills&Date)

## 🏷️ 版本策略

| 版號 | 意義 |
|---|---|
| `0.0.X` | 打磨輪——任何 skill 經實測修訂一輪，尾號 +1 |
| `0.X.0` | 新 skill 發布或工作流結構調整，中號 +1 |
| `1.0.0` | 全套 skill 穩定版 |
| `2.0.0` | 直白技術 ID、博雅單入口接力、結構化模型回歸與確定性查詢工具 |
| `2.1.0` | 主張回源查核、選用研究檔案、批准後局部修訂與逐題新手路由；全套增至 17 個 skill |

每個版本打 git tag，CHANGELOG 記在 [`MEMORY.md`](MEMORY.md#changelog)。

## 📄 授權與致謝

**MIT License**（版權人 Dylan Chiang 蔣濤）——可自由使用、修改、再發布（含商用），保留版權聲明即可。

工作流思路受以下公開項目與研究啟發，特此致謝：

- [**academic-research-skills**](https://github.com/Imbad0202/academic-research-skills)（ARS）—— 誠信閘門與引用核驗的理念方向
- [**Supervisor-Skills**](https://github.com/HKUSTDial/Supervisor-Skills)（HKUST）—— 把導師判斷編碼成 skill、投稿前自審（模擬審查）的立意
- [**RW Research Skill**](https://github.com/rolandwonglonam/rw-research-skill)（Roland Wayne）—— 研究狀態檔案、主張回源查核、hash 局部修訂與逐題新手路由的理念啟發；Boya 依自身人類在環邊界與 MIT 規範原創重寫，未複製其 Apache-2.0 文字或程式
- **The AI Scientist**（Lu et al., 2024, [arXiv:2408.06292](https://arxiv.org/abs/2408.06292), Sakana AI）—— 全自動化研究的失敗模式
- **Zhao et al.（2026）** —— 對幻覺引用的大規模實證
- [**彭思達公開研究筆記**](https://pengsida.notion.site/c1a22465a0fa4b15a12985223916048e) —— 論文段落寫作方法（主題句前置、反向大綱）的理念啟發；僅借鑑方法理念，規則與行文原創重寫

> 僅借鑑理念方向與問題意識，**提示語、結構、案例全部原創自製**——零內容轉述、不抄 prompt、不用截圖。這份分寸，也是本庫堅持的學術誠信。
