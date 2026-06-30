# VERIFICATION　博雅驗證證據鏈

> 每個 skill 都拿真實研究材料跑過、把暴露的坑寫回規則。本表是過去實測的留痕證據；未來回歸斷言見 [evals/](evals/)。
> 資料源：[examples/](examples/) 與 git 歷史，不新增實測、只彙總已發生的。

## 驗證狀態

| 狀態 | 意義 | 進入條件 |
|---|---|---|
| Stable | 已穩定 | 已用真實材料完整跑過，暴露的坑已寫回 `SKILL.md`，且有 example 或 eval 可回看 |
| Beta | 可用但仍在磨 | 已有實測或局部案例，但邊界條件、地區語境或資料類型仍需要更多回歸 |
| Draft | 草稿 | 只有設計或少量試跑，尚未形成可依賴的實測證據鏈 |

目前 15 個 Boya skills 均列為 **Stable**：每個 skill 至少有一輪真實材料實測、暴露的坑已寫回 `SKILL.md` 或 `evals/`，且有 example／evidence ledger 可回看。知識表中的單筆事實仍可保留 `❓`／`待補`；這代表該事實尚未核完，不影響 skill 工作流本身的 Stable 狀態。未來新增 skill 一律先從 Draft 或 Beta 開始，不可未測即標 Stable。

- **venue-fit**（0.3.0 新增）：目前 **Stable**——先用作者碩論對標《公共行政學報》真實投稿規範（`examples/2026-06-18-venuefit-thesis-jpa.md`），再補英文教育科技／高教評量案例（`examples/2026-06-30-venuefit-jalt-genai-assessment.md`）。第二例核到 JALT submissions page 的 Word、APA 7、匿名稿與生成式 AI dedicated declaration 要求，同時固化「已發表文章頁不等於作者須知」「查不到字數仍待補」。
- **framework-build**（0.X.0 新增，2026-06-22 升 0.1.0 Beta，2026-06-30 升 Stable）：目前 **Stable**——已有 JASM 國際關係／經濟安全、作者碩論文組實證／混合方法、人文思辨型 LLM silicon sampling 知識論、以及台灣碳費政策分析型四例。三分流「概念框架／理論視角／分析框架」均已實跑，政策分析型案例見 `examples/2026-06-30-framework-carbon-fee-policy.md`。
- **lit-discovery**（0.5.0 新增，2026-06-30 升 0.6.0 Beta、同日打磨升 0.6.1、2026-06-30 升 Stable）：目前 **Stable**——已有探勘核心、venue 證據、TSSCI 命中路徑壓測，並補完整中文題全鏈案例 `examples/2026-06-30-litdiscovery-genai-assessment-taiwan.md`。該例用中文精準題名反查 OpenAlex/Crossref 命中真實 DOI，做英文對照、相關性分層與 venue 待查標記；同日補 TSSCI 2025（適用2026）與 CSSCI 2025-2026 公開來源層級。

## Evidence Ledger 最小格式

每次新增 example、修訂 skill 規則、或宣稱某個坑已被驗證時，至少留下這五欄。它是輕量證據帳，不是大型自動化研究系統。

| 欄位 | 必填內容 |
|---|---|
| claim | 正在驗證的判斷或規則，例如「API 查無不等於文獻不存在」 |
| source | 證據來源：example、原始材料、公開資料庫、文件路徑或 commit |
| check | 實際做了什麼核對，例如 DOI 反查、資料庫比對、段落回源、格式對照 |
| result | 通過／不通過／不確定；不確定時必須說明缺口 |
| next | 下一步：寫回 `SKILL.md`、補 eval、標待人工、或暫不採納 |

建議用這個 Markdown 骨架：

```md
### YYYY-MM-DD · <skill> · <短標題>

- claim:
- source:
- check:
- result:
- next:
```

## Source Map 與 Action Map

當任務涉及多份材料、審稿意見、口試問題、或長篇修改時，建議額外加兩張表，避免 AI 把來源、評論與行動混在一起。

**Source Map**

| source_id | 來源 | 範圍 | 用途 |
|---|---|---|---|
| S1 | 文件路徑、URL、資料庫紀錄或訪談材料 | 頁碼、段落、條目或時間戳 | 用來支持哪個 claim |

**Action Map**

| action_id | 來源 | 要做的事 | 狀態 |
|---|---|---|---|
| A1 | S1 / reviewer comment / defense question | 修改、查核、補資料、刪除或保留 | done / pending / rejected |

## 刻意不採用的重型設計

Boya 維持人文社科研究者可讀、可手動介入的技能庫，不把每個 skill 改成大型自動化框架。因此目前不採用：

- `_shared/` 大型共用 fragments。
- `manifest.yaml` 分片載入系統。
- 多 agent 長跑 orchestrator。
- 無人值守研究 pipeline。
- Nature／理工論文專用的圖表、專利、投稿包流程。

> **界定：引導式精靈 ≠ 無人值守 pipeline。** `boya`（原 `research-roadmap`）自 2026-06-20 升級為「引導式精靈」——會主動接力喚起下一個 skill，讓使用者「一步一個 skill 被帶著走」。它**不是**上面禁止的無人值守 pipeline：兩者差別只在一件事——**遇到「只有你能決定」的關卡會不會停**。引導式精靈每關硬停、等使用者拍板才放行，研究判斷全留人；無人值守 pipeline 不停、AI 代做判斷。後者仍不採用。接力的是流程腳手架，不接力的是研究判斷。

若未來某個 skill 明顯過長，才考慮把少量共用材料外移到 `knowledge/` 或 `templates/`，但 `SKILL.md` 仍保留可直接閱讀的核心規則。

| skill | 版本 | 實測日期 | 用的真實材料 | 暴露的坑 | 對應 example |
|---|---|---|---|---|---|
| citation-verify | 0.0.2 | 2026-06-12 | 作者碩論 47 筆參考文獻 | 查無≠偽造（中文文獻誤判風險） | examples/2026-06-12-master-thesis-case.md |
| lit-matrix | 0.0.2 | 2026-06-13 | 碩論 5 篇異質文獻 | 引用語境≠主題、異質語料硬併 | examples/2026-06-13-litmatrix-thesis-litreview.md |
| self-review | 0.0.2 | 2026-06-13 | 本書教學章稿 | 文稿類型錯配、證據-宣稱規模不相稱、絕對宣稱 | examples/2026-06-13-selfreview-teaching-chapter.md |
| topic-refine | 0.0.2 | 2026-06-14 | 兩岸關係題 | 可行性紅燈（資料閉門） | examples/2026-06-14-topicrefine-cross-strait.md |
| method-design | 0.0.2 | 2026-06-14 | 碩論研究設計 | 對象分層不清、AI 扮受訪者太乖 | examples/2026-06-14-methoddesign-thesis.md |
| outline-builder | 0.0.2 | 2026-06-14 | 碩論骨架 | 完整性幻覺、warrant 缺席 | examples/2026-06-14-outlinebuilder-thesis.md |
| style-tune | 0.0.2 | 2026-06-14 | 碩論緒論 | AI 腔的專業偽裝 | examples/2026-06-14-styletune-thesis.md |
| defense-prep | 0.0.2 | 2026-06-14 | 碩論口試模擬 | 論文階段誤判、漏質性可推論性 | examples/2026-06-14-defenseprep-thesis.md |
| ai-disclosure | 0.0.2 | 2026-06-14 | 重度 AI 協作聲明 | 重度使用時 AI 不敢說 | examples/2026-06-14-aidisclosure-heavy-ai-use.md |
| abstract-bilingual | 0.0.2 | 2026-06-14 | 碩論中英摘要 | 關鍵詞中英不對齊、「顯著」當統計詞照搬 | examples/2026-06-14-abstractbilingual-thesis.md |
| cite-format | 0.0.2 | 2026-06-14 | 碩論參考文獻 | 先排後驗＝錯資料的漂亮包裝 | examples/2026-06-14-citeformat-thesis.md |
| boya（原 research-roadmap） | 0.0.2 | 2026-06-14 | 完整研究工作流 | 退化成目錄朗讀機 | examples/2026-06-14-researchroadmap-workflow.md |
| venue-fit | 0.0.1 Beta | 2026-06-18 | 作者碩論 ×《公共行政學報》投稿規範 | 不可編作者須知、學位論文轉期刊需先判文稿類型 | examples/2026-06-18-venuefit-thesis-jpa.md |
| work-trace-table | convention/template | 2026-06-19 | 碩論 47 筆引用查核＋既有 self-review／ai-disclosure 真錄 | DOI 貼錯不可落 🗑、AI 審查意見先標 🤖、揭露須據表寫具體分工 | examples/2026-06-19-work-trace-table-case.md |
| outline-builder | 0.0.3 | 2026-06-20 | 碩論骨架與文風既有真錄節錄 | 逆向體檢須三動作齊全；節錄級材料不可偽裝成逐字全文體檢 | examples/2026-06-20-outline-reverse-checkup-case.md |
| framework-build | 0.4.0 Draft | 2026-06-21 | 日台半導體經濟安全（JASM）課題、文獻已過 lit-matrix | 框架沙拉、紅海誤選、假地基、兩張皮 | examples/2026-06-21-framework-jasm.md |
| topic-refine | 0.0.3 | 2026-06-21 | 兩岸關係題＋STORM 五透鏡發散 | 利益透鏡易發無源事實、透鏡撐爆清單、懷疑者最救命 | examples/2026-06-21-topicrefine-storm-lens.md |
| self-review | 0.0.3 | 2026-06-21 | 教學章稿審查報告＋收尾自評 | 信心分數誘導裝權威、偏誤須分合理留白／假嚴格、缺席視角接文稿類型表 | examples/2026-06-21-selfreview-storm-lens.md |
| lit-matrix | 0.0.3 | 2026-06-21 | 碩論 5 篇＋盲點缺口框法 | 盲點易滑成「首創」腦補、缺口要扣 RQ 需要的面向 | examples/2026-06-21-litmatrix-storm-lens.md |
| lit-discovery | 0.5.0 Draft | 2026-06-21 | 公部門×生成式 AI，實打 OpenAlex／Crossref | 模糊檢索噪音、高被引≠相關、同論文多 DOI 副本、中文覆蓋稀疏夾離題、Crossref 回非論文 grant | examples/2026-06-21-litdiscovery-genai-public-sector.md |
| framework-build | 0.0.2 Draft | 2026-06-22 | 作者碩論（立委助理×生成式 AI，TAM＋科技壓力＋社會影響），文獻已過 lit-matrix | 偽並列主框架（平鋪≠並列地位）、隱性遷移代價（✅支撐≠免遷移）、混合方法漏質性抓手 | examples/2026-06-22-framework-thesis.md |
| framework-build | 0.1.0 Beta | 2026-06-22 | 社計博士生 LLM silicon sampling 知識論（批判實在論×四原則主義），人文思辨型首例 | 思辨版框架沙拉（跨哲學子域並列≠層數貪疊）、人文型操作化＝分析維度、老倫理框架跨域遷移代價、研究問題跨子域步驟 2 預警 | examples/2026-06-22-framework-humanist.md |
| outline-builder | 0.0.4 | 2026-06-27 | silicon sampling 知識論（接力 framework-build 定錨框架），人文思辨型正向搭骨架＋topic-sentence 前置首跑 | 讓步句冒充主題句（思辨型）、段落主題句覆讀章論點 | examples/2026-06-27-outlinebuilder-silicon-sampling.md |
| lit-discovery | 0.6.0 Beta | 2026-06-30 | 沿用公部門×生成式 AI 候選，加跑新增 venue 證據步驟（借鑒 paper-quality-filter），Crossref 解 DOI 補刊名 | 來源表缺 SSCI／英文社科候選落空、無刊名須先解 DOI、預印本不給級 | examples/2026-06-30-litdiscovery-venue-evidence.md |
| lit-discovery | 0.6.1 Beta | 2026-06-30 | 台灣期刊命中壓測，實抓國科會官方 TSSCI／THCI 名單對比《公共行政學報》等 | 官方頁也可能非最新版（抓到名單適用2024）、近似刊名查無不自動更正、CSSCI 非公開可抓、無 discovery API 須誠實標未新撈 | examples/2026-06-30-litdiscovery-venue-tssci-match.md |
| lit-discovery | 1.0.0 Stable | 2026-06-30 | 中文題「生成式 AI 與台灣學習評量／高等教育治理」，OpenAlex／Crossref 精準題名反查＋英文對照 | 中文寬查無命中不等於無文獻；書目已核不等於 venue 已核；TSSCI/CSSCI 來源層級需明寫 | examples/2026-06-30-litdiscovery-genai-assessment-taiwan.md |
| framework-build | 1.0.0 Stable | 2026-06-30 | 台灣碳費政策，環境部／氣候變遷署公開材料 | 政策分析型＝分析框架；多準則不可假量化；政策事實與方法文獻分開 | examples/2026-06-30-framework-carbon-fee-policy.md |
| venue-fit | 1.0.0 Stable | 2026-06-30 | Ogunleye et al. 2024 × Journal of Applied Learning & Teaching submissions page | 已發表文章頁不等於作者須知；英文刊格式/AI 要求須回頁面；查不到字數仍待補 | examples/2026-06-30-venuefit-jalt-genai-assessment.md |

## Evidence Ledger 紀錄（2026-06-30 1.0.0 全套 Stable）

### 2026-06-30 · lit-discovery · 中文題全鏈探勘補齊

- claim：`lit-discovery` 可跑通中文題「檢索策略→真實 API 命中→候選分層→venue 比對」全鏈；中文寬查無命中不等於文獻不存在。
- source：examples/2026-06-30-litdiscovery-genai-assessment-taiwan.md；OpenAlex `W4406228191`；Crossref DOI `10.53106/168063602025020370002`；ERICDATA 條目；JALT DOI `10.37074/jalt.2024.7.1.28`。
- check：以中文精準題名反查 OpenAlex/Crossref，命中〈生成式AI時代的學習評量〉；用英文題名查 Crossref 得 JALT 對照候選；寬查 `生成式AI 高等教育` count=0 時標查無於該 API、不推論文獻不存在；venue 未逐刊命中者保持 `❓待查`。
- result：通過。補齊升 Stable 缺口；同時更新 TSSCI 2025／CSSCI 2025-2026 來源層級，避免把書目真實誤寫成 venue 已核。
- next：已寫回 eval；承重前仍須把候選交 `citation-verify` 與 `lit-matrix`。

### 2026-06-30 · framework-build · 政策分析型分流跑通

- claim：`framework-build` 第三分流「政策分析型＝分析框架」可跑通；政策分析題不應被硬畫成概念變項模型。
- source：examples/2026-06-30-framework-carbon-fee-policy.md；環境部氣候變遷署碳費專區；環境部新聞稿〈環境部公告「碳費徵收費率」〉。
- check：從公開政策材料抽取政策問題與制度事實，候選框架分為政策工具、公平轉型、行政可行性、多準則政策評估；推薦多準則定性分析，但標明方法文獻待補且不做權重分數。
- result：通過。三分流「概念框架／理論視角／分析框架」均有真實案例；政策事實來源與理論／方法來源分欄，未用官方政策頁冒充方法文獻。
- next：已寫回 eval；實作正文前需補政策工具／MCA 方法文獻。

### 2026-06-30 · venue-fit · 英文教育科技投稿對標跑通

- claim：`venue-fit` 可處理不同語種／不同學科公開材料，且能區分已發表文章頁與作者須知。
- source：examples/2026-06-30-venuefit-jalt-genai-assessment.md；JALT article page；JALT submissions page `https://jalt.open-publishing.org/index.php/jalt/about/submissions`。
- check：核對 JALT submissions page，確認 Word 投稿、APA 7、article classifications、匿名稿、生成式 AI 超過校對用途須 dedicated declaration section；未在 HTML 穩定取得的字數／摘要／關鍵詞保持待補。
- result：通過。第二語種／學科案例成立，且不把文章頁反推成作者須知；AI 揭露可回到真實來源。
- next：已寫回 eval；投稿前需下載或開啟 JALT guideline PDF 補細節。

## Evidence Ledger 紀錄（2026-06-30 lit-discovery venue 命中路徑壓測，對真實 TSSCI 官方名單）

### 2026-06-30 · lit-discovery · 命中路徑走通＋官方頁也可能非最新版

- claim：venue 命中須回指官方名單原列並標抓取版次；官方頁本身也可能不是最新版，須記適用期間＋抓取日。
- source：examples/2026-06-30-litdiscovery-venue-tssci-match.md（實抓 hss.ntu.edu.tw TSSCI／THCI 名單；《公共行政學報》命中政治學門 TSSCI 第一級）。
- check：對官方名單精確比對——公共行政學報→第一級、行政暨政策學報→第二級、資訊管理學報→第二級，皆核出學門與級別；頁面標「名單適用2024、更新2024-05-28」，而 2025 名單（適用2026）另已存在。
- result：通過。命中路徑首次走通；命中一律標 `TSSCI 名單適用2024`，並提示可能有更新版，未寫「現行」。
- next：已寫回 SKILL 已知陷阱 7、knowledge/venues.md 抓名單注意①、eval；v1.0.0 已補 TSSCI 2025／CSSCI 來源層級與全鏈中文案例。

### 2026-06-30 · lit-discovery · 精確比對查無不自動更正／無 API 須標未新撈

- claim：近似刊名查無不得自動改判為相近真刊；CSSCI 無官方名單須待查；discovery API 不可用時須誠實標「未新撈」，不得假裝檢索。
- source：同 example（#4「公共行政學刊」近似誤名、#5 大陸 CSSCI 候選；本輪 bash 網路 000、web_fetch 清單端點回空）。
- check：「公共行政學刊」名單查無→標 ❓待查，未改成「公共行政學報」；大陸刊無官方 CSSCI 名單→❓待查；本輪無法新撈文章，example 明記「僅就已知刊名比對、未捏造文章」。
- result：通過。查無不更正、無源不補級、無 API 不假裝；全程無捏造文章標題或 DOI。
- next：已寫回 SKILL 已知陷阱 8–10、eval（MUST NOT 自動更正／假裝檢索／憑記憶補級）。

## Evidence Ledger 紀錄（2026-06-30 lit-discovery 新增 venue 證據步驟，借鑒 paper-quality-filter）

> 評估 `yilaai/paper-quality-filter`（雙語 venue 證據 skill＋本地分級資料集＋自動排序腳本）。其理工本位分區（JCR／CAS／CCF／EI）、寫死閾值的自動排序腳本、無日期靜態資料集皆撞本庫設計邊界與誠信鐵律，**整套不採用**；只取「拿真表查、附證據、查不到老實標、最後人來定」骨架，改寫成人文社科版 venue 證據步驟（無腳本、人在環中、來源標版次年份）。

### 2026-06-30 · lit-discovery · 來源表缺 SSCI＝英文社科候選一律落空

- claim：英文社會科學候選對應的國際索引是 SSCI；原 venue 來源表只放 A&HCI（只收藝術人文），會讓正牌 SSCI 期刊被誤標「查無」。
- source：examples/2026-06-30-litdiscovery-venue-evidence.md（第 1 筆 Crossref 解出 container-title＝Journal of Information Science, SAGE, ISSN 0165-5515）。
- check：拿刊名查 `knowledge/venues.md` 五張表（CSSCI／TSSCI／北大／AMI／A&HCI），全不命中→只能標 ❓待查；判定問題在「表沒納 SSCI」而非「刊不好」。
- result：通過修正——`knowledge/venues.md` 補一列 SSCI（與 A&HCI 並列國際線），僅當「收錄與否」用、不引入 IF 分區（守不採理工分區邊界）。eval／SKILL 涵蓋名單同步補 SSCI。
- next：已寫回 knowledge/venues.md、skills/lit-discovery/SKILL.md 第 3.5 步、evals/lit-discovery.md。

### 2026-06-30 · lit-discovery · venue 證據第一道關＝有沒有刊名，沒有先解 DOI

- claim：只有標題＋DOI、無 venue 欄位時不能判出處；須先解 DOI 補 container-title，解不出標 ❓，不靠記憶補刊名；預印本不給 venue 級。
- source：同 example（候選只記標題＋DOI；SSRN／TechRxiv 兩筆為預印本；中文學位論文非期刊）。
- check：以 Crossref 公開 API 實解 4 個 DOI，1 筆得真刊名、1 筆未解出→❓；2 筆預印本按鐵律不給級；學位論文標不適用。全程無一筆被硬給等級。
- result：通過。5 筆中 0 筆被編造分級；三句免責（強≠切題／查無≠論文差／你定）有講。
- next：已寫回 SKILL 第 3.5 步（先解 DOI／預印本不給級）；中文／台灣期刊命中路徑與全鏈案例已於 v1.0.0 補齊。



### 2026-06-27 · outline-builder · topic-sentence 前置在思辨型須辨「讓步—反轉」

- claim：正向設計關鍵段落時，把 claim 放首句（鐵律 6）能讓首句即點明本段 message。
- source：examples/2026-06-27-outlinebuilder-silicon-sampling.md（接力 framework-build silicon sampling 框架，理論思辨型）。
- check：在第 2 章「既有爭論共享被限縮提問層次」段實際擺位——機械前置會讓 Argyle 讓步句佔首句，與本段批評 message 相反。
- result：通過但須補例外——思辨型「讓步—反轉」段，讓步可放首句但須緊跟轉折，不得讓對手觀點獨佔首句。
- next：已寫回鐵律 6 與 SKILL 已知陷阱 9、eval 已暴露的坑。

### 2026-06-27 · outline-builder · 段落主題句不得覆讀章核心論點

- claim：message-first 是段落級，每段首句放本段獨有 claim。
- source：同上 example，第 3 步章核心論點欄與第 4 步段落論證鏈交界。
- check：試擺時把章核心論點複製成章內每段首句，導致段段覆述、無推進。
- result：不通過該寫法——須區分章論點（章層）與段主題句（段層，章論點的下一步）。
- next：已寫回鐵律 6、SKILL 已知陷阱 10、eval 已暴露的坑。

## Evidence Ledger 紀錄（2026-06-22 framework-build 人文思辨型首例）

### 2026-06-22 · framework-build · 跨哲學子域並列為思辨版框架沙拉

- claim: 批判實在論（回答認識論）與四原則主義（回答規範倫理）回答的哲學問題不同，無法並列為同級主框架；並列即「思辨版框架沙拉」。
- source: examples/2026-06-22-framework-humanist.md（LLM silicon sampling 知識論；候選表中批判實在論與四原則主義同列）。
- check: 試跑把兩個框架並排作主視角——批判實在論答「LLM 能否代表社會真實」、四原則主義答「這樣做合不合倫理」，兩者回答不同哲學問題無法並列；改為批判實在論單一主視角，倫理問題收入「知識責任邊界」分析維度。
- result: 通過。主視角唯一，四原則主義降為「論點」層入文末，說明自主原則失去著力點的論據功能。
- next: 已寫回 SKILL.md 鐵律 3（框架沙拉的第②種隱形版：跨哲學子域並列）。

### 2026-06-22 · framework-build · 人文思辨型的「操作化」是分析維度，不是問卷

- claim: 人文思辨型 framework 的操作化落點是「從哪幾個面向審視爭議」（分析維度），不是問卷題目、假設命題或訪談提綱。
- source: examples/2026-06-22-framework-humanist.md（批判實在論三層本體論＋三個分析維度）。
- check: 若 skill 只給「用批判實在論」標籤而不指出「從什麼角度讀、看什麼、怎麼讀文本」，框架無法落地；本輪明確給出三個維度（生成機制可及性、層間跌落診斷、知識責任邊界），驗可接力 `outline-builder`。
- result: 通過。三個分析維度可直接映射到論文各節標題，框架不懸空。
- next: 已寫回 SKILL.md 鐵律 5（人文思辨型操作化分流：分析維度≠問卷）。

### 2026-06-22 · framework-build · 老倫理框架套新 AI 場景的跨域遷移代價

- claim: 有庫存支撐的倫理框架（四原則主義）套到設計前提不同的新場景（LLM silicon sampling）時，可能有核心概念直接失去著力點的跨域遷移代價，必須在理論代價欄標明。
- source: examples/2026-06-22-framework-humanist.md（四原則主義「自主原則」預設真實研究對象能行使知情同意）。
- check: 四原則的自主原則（尊重研究對象自主）設計前提是有真實受訪者；silicon sampling 根本沒有真實受訪者，自主原則直接失去著力點。此為「應用場景跨域遷移」而非「技術世代遷移」，與 TAM 案例同屬「✅支撐≠免遷移」但成因不同。
- result: 通過。理論代價欄標明「自主原則失去著力點」，提示需以 AI 專屬倫理框架替代或重構。
- next: 已寫回 SKILL.md 鐵律 1 延伸（「✅支撐≠免遷移」從技術世代延伸到應用場景跨域）。

### 2026-06-22 · framework-build · 研究問題橫跨哲學子域須步驟 2 預警

- claim: 若研究問題同時橫跨認識論與規範倫理兩個哲學子域，應在步驟 2「判論文類型」時主動標出分裂風險，給出收窄或整合選項，而非靜默讓研究者走入步驟 4 才發現並列衝動。
- source: examples/2026-06-22-framework-humanist.md（研究問題同問「知識論正當性」與「倫理邊界」兩個子問題）。
- check: 步驟 2 加入⚠️預警後，研究者在此步驟就收到「三條出口」（收窄選一／整合入單一視角的分析維度／明確承認雙主題），GATE 時不再面對臨時的並列衝動。
- result: 通過。預警提前攔截，研究者在 GATE 能基於充分資訊拍板採納推薦（批判實在論單主視角）。
- next: 已寫回 SKILL.md 步驟 2（⚠️跨哲學子域預警區塊＋三條解法）。

## Evidence Ledger 紀錄（2026-06-22 framework-build 文組實證題實測）

### 2026-06-22 · framework-build · 平鋪三理論不等於三並列主框架

- claim: 文獻／關鍵詞把數個理論平鋪並列，不代表它們是並列主框架；主框架仍最多一個。
- source: examples/2026-06-22-framework-thesis.md（作者碩論，官方關鍵詞平鋪 TAM／科技壓力／社會影響）。
- check: 試跑順著關鍵詞排列把三者擺成三並列主框架＝框架沙拉隱形版；改為追問哪個扣題最直接（TAM），餘二降中介並說清補哪塊盲區後重跑。
- result: 通過。單一主框架 TAM，科技壓力＋社會影響為中介，分工說得清。
- next: 已寫回 SKILL.md 鐵律 3 與 eval（MUST NOT 因平鋪列出擺成並列主框架）。

### 2026-06-22 · framework-build · ✅ 庫存支撐不等於免遷移

- claim: 框架有真文獻支撐（✅）只證書目為真，不證它能無痕套到新對象；老框架套新技術要標遷移代價。
- source: examples/2026-06-22-framework-thesis.md（TAM＝Davis 1989，案例 001 已查證書目）。
- check: 試跑把 TAM 當「拿來即用」；核對其 PU/PEOU 為確定性 mainframe IT 建，接不住生成式 AI 的幻覺／不確定性（呼應 lit-matrix 缺口「生成式 AI 技術特殊性」），改在理論代價欄標世代遷移成本。
- result: 通過。理論代價欄明列遷移成本，未靜默套用。
- next: 已寫回 SKILL.md 鐵律 1 延伸與 eval（MUST NOT 把 ✅ 當免遷移）。

### 2026-06-22 · framework-build · 混合方法的實證抓手要雙棲

- claim: 混合方法題，每個關鍵概念要同時給「問卷怎麼測」與「訪談怎麼追」兩種實證抓手，不得只列可量化指標。
- source: examples/2026-06-22-framework-thesis.md（碩論＝212 問卷＋6 深度訪談）。
- check: 試跑只給 PU/PEOU／壓力量表等可量化抓手，漏了質性訪談那半＝框架與質性兩張皮；改為每概念分排「問卷／訪談」兩種抓手後重跑。
- result: 通過。實證抓手依方法形態分排，量化與質性兩腿都接得住，交棒 method-design（案例 006）不漏。
- next: 已寫回 SKILL.md 鐵律 5 與 eval（MUST 混合方法雙棲抓手）。

## Evidence Ledger 紀錄（2026-06-21 STORM 啟發吸收）

> STORM（Stanford）招牌機制「模擬專家生成議題認識」撞本庫誠信鐵律與「不採無人值守 pipeline」，整套不採用；只取「多角度逼問題／自評」骨架，落進三個既有 skill，產出全鎖成 🤖 待核問題。

### 2026-06-21 · topic-refine · 多透鏡發散只逼問題不生答案

- claim: STORM 五透鏡可當發散維度補盲點，但產出須鎖成 🤖 待核問題、不得發無源事實。
- source: examples/2026-06-21-topicrefine-storm-lens.md（延用兩岸關係真實案例）。
- check: 試跑利益透鏡，捕到 AI 差點斷言「北京從接觸獲益」；改成「只標值得查」後重跑；核對子題仍 ≤10、仍走三問。
- result: 通過。透鏡逼出原維度漏掉的「懷疑前提」「歷史平行」「中斷/監管」盲點，無無源斷言。
- next: 已寫回 SKILL.md 第 2 步（透鏡表＋三條硬紀律）與 eval；升 0.0.3。

### 2026-06-21 · self-review · 信心分數須與 AI 邊界一致

- claim: 收尾自評（信心/偏誤/缺席）方向同 self-review，可安全吸收；但信心分數對領域細節不得給高分。
- source: examples/2026-06-21-selfreview-storm-lens.md（延用教學章稿審查報告）。
- check: 試跑對「三層閱讀法 vs Keshav」給 8/10＝裝權威，改為 4/10 標需專家確認；核對偏誤檢查能分辨「合理留白」與「假嚴格」。
- result: 通過。信心分數變成「哪幾條優先信、哪幾條自己再查」的導引，非證實感包裝。
- next: 已寫回 SKILL.md 第 4.5 步與 eval（含 MUST NOT 領域給高分）；升 0.0.3。

### 2026-06-21 · lit-matrix · 盲點缺口只標「這批未覆蓋」不得腦補首創

- claim: 盲點框法可辨識缺口候選，但「這批沒人碰」≠「全世界沒人做過」。
- source: examples/2026-06-21-litmatrix-storm-lens.md（延用碩論 5 篇）。
- check: 試跑把「立法幕僚場景沒人碰」誤報成「本研究首創」；改為「目前 5 篇未覆蓋，請擴大檢索確認」後重跑。
- result: 通過。缺口扣「RQ 需要 × 這批是否覆蓋」兩欄，未腦補不存在文獻。
- next: 已寫回 SKILL.md 第 4 步缺口處與 eval（含 MUST NOT 腦補首創）；升 0.0.3。

## Evidence Ledger 紀錄（2026-06-21 lit-discovery 新增，借鑒 frontier-tracker）

> 評估 `LiAngsong98/frontier-tracker`（自動化文獻週報 pipeline）：其無人值守 cron、持久狀態、Python 腳本、排名匯入皆撞本庫設計邊界，**整套架構不採用**；只取「從研究問題撈候選文獻」這一概念缺口，改寫成散文、人在環中、無狀態的 `lit-discovery`，補進階段 2「找文獻」（探勘→查核→讀）。

### 2026-06-21 · lit-discovery · 候選全來自真實命中、中文查無標 ❓ 不硬湊

- claim: discovery 場景幻覺風險最高；候選必須對應真實 API 回應，中文覆蓋不到一律 ❓待人工，不得腦補「沒人做過」。
- source: examples/2026-06-21-litdiscovery-genai-public-sector.md（公部門×生成式 AI，實打 OpenAlex／Crossref）。
- check: OpenAlex `title.search` 中文關鍵詞「立法委員助理」count=2 且夾一筆離題日文；英文題撈到真候選但混入 cybersecurity 離題高被引、techrxiv 同論文兩個 DOI、Crossref 一筆 EU grant 非論文。
- result: 通過。候選全為真實命中、無捏造；中文標 ❓導向華藝/國圖；弱相關（cybersecurity）標 ⚪ 低保留未砍；非論文 grant 剔除。
- next: 已寫回 SKILL.md 鐵律＋已知陷阱 1–5 與 eval（MUST NOT 編造/冒充已查證/靜默丟棄/腦補首創）；列 0.5.0 Draft，升 Beta 待補不同學科或中文為主案例。

## Evidence Ledger 紀錄（2026-06-24 借鑒 Auto-Empirical-Research-Skills）

> 評估 `brycewang-stanford/Auto-Empirical-Research-Skills`（STEM／實證計量取向的超級聚合目錄，含 numeric benchmark、多 agent、Makefile/CI）。整套聚合與 pipeline 架構撞本庫設計邊界，**不採用**；只取兩個後設方法：①從 frontmatter 生成/核對路由的防漂移習慣 → `scripts/check-skills.py`；②「陷阱式」eval（給會踩坑的輸入測不上鉤）→ 三條 eval 新增「🪤 陷阱輸入」段。

### 2026-06-24 · scripts/check-skills.py · frontmatter 契約＋ROUTER 同步防呆

- claim: 「以 SKILL.md 為準」應可機器核對，而非僅口頭約定；契約硬規（兩欄 frontmatter／kebab-case／name=目錄名）與 ROUTER 同步可自動掃描。
- source: scripts/check-skills.py 首跑全 15 skill + ROUTER.md（stdlib-only、唯讀、只報告）。
- check: 跑 `python3 scripts/check-skills.py`；INFO 噪音過高時收緊誠信字樣偵測（編造/查無/需補…）由 12→9。
- result: ERROR 0／WARN 0／INFO 9。硬規與結構同步全過；INFO 揭兩件待人工確認：style-tune description 無誠信/紅線字樣、venue-fit ROUTER 措辭「投稿前對標目標刊」與 description「投稿前幫我對標目標刊」差一詞。
- next: 工具屬維護輔助（非 build 依賴），已入關鍵文件地圖；venue-fit 措辭與 style-tune 紅線交作者拍板。

### 2026-06-24 · 三條陷阱式 eval · 從既有坑/RULES 推導、未實跑

- claim: citation-verify／framework-build／style-tune 可各加一條「陷阱輸入」測不上鉤；陷阱須溯自既有「已暴露的坑」或 RULES，不憑空造。
- source: evals/citation-verify.md、evals/framework-build.md、evals/style-tune.md 各新增「🪤 陷阱輸入」段；evals/README §設計原則 補陷阱慣例。
- check: 逐條核對陷阱來源——查無判假（坑「查無≠偽造」）、庫外框架硬撐＋偽並列（坑「假地基」「偽並列主框架」）、規避偵測（RULES §1，政策推導）。
- result: eval 結構已落地；前兩條溯自真實坑，第三條 style-tune 為政策推導、**尚未實跑**，已於該 eval 標註。
- next: style-tune 另暴露 SKILL.md 缺「規避偵測」紅線（交作者拍板是否補鐵律）；補後須一次真實材料實跑才隨 skill 升 Beta。
