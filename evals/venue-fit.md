# eval：venue-fit

## 基準輸入

案例：`examples/2026-06-18-venuefit-thesis-jpa.md`。

- 文稿：作者碩士論文《生成式人工智慧使用行為之研究：以立法委員助理為例》的事實卡。
- 目標 venue：《公共行政學報》（Journal of Public Administration, JPA）。
- 真實規範來源：期刊簡介、徵稿啟事、論文撰寫體例 2023 年 05 月版、出版與寫作倫理、生成式 AI 使用指引。
- 測試重點：只能使用真實來源；查不到的近兩年目錄契合、IRB/知情同意固定格式、量化報告細項須標待補；不得生成影響因子、排名、接受率或作者須知。

補充案例：`examples/2026-06-30-venuefit-jalt-genai-assessment.md`。

- 文稿替代材料：Ogunleye et al. (2024) "Higher education assessment practice in the era of generative AI tools"，DOI `10.37074/jalt.2024.7.1.28`。
- 目標 venue：Journal of Applied Learning & Teaching（英文／高教評量／教育科技）。
- 真實規範來源：JALT submissions page（Word、APA 7、article classifications、匿名投稿、生成式 AI dedicated declaration section）。
- 測試重點：已發表文章頁不得冒充作者須知；英文刊也只有在頁面明列時才可寫 APA 7／AI 揭露；細部字數、摘要、關鍵詞查不到仍待補。

## ✅ 必須做到（MUST）

- 先確認目標刊落在哪個「索引/語種（SSCI/TSSCI/CSSCI）× 學科方法（量化/質性）」象限，再取對應對標清單。
- 引導使用者從目標刊的「作者須知／投稿指南／近兩年目錄」提取真實要求；任何查不到的要求一律標「待補」。
- 對標涵蓋五層：結構、報告規範、格式（隨語種）、語言、倫理與 AI 揭露。
- 質性／人文向論文不套 IMRaD 完整性，改用「脈絡鋪陳／方法透明／可信度」對標。
- 差距輸出分三級：must-fix／should-fix／待補查證。
- 引用格式指向 cite-format、AI 揭露指向 ai-disclosure、摘要指向 abstract-bilingual，不在本 skill 重做。
- 結尾把「投不投、差距補不補」交回使用者決定。
- 學位論文轉投期刊時，必須先指出「學位論文 → 研究論文」的文稿類型差距，包括篇幅壓縮、去識別化、貢獻重寫與投稿附件，再談格式細節。
- 若目標刊有 AI 使用指引，必須把 AI 揭露列為 must-fix 或 should-fix，並指向 ai-disclosure。
- 對英文公開稿做投稿對標時，必須先分清「已發表文章頁／DOI」與「當前作者須知」兩種來源；前者只支撐題材與書目存在，後者才支撐格式與揭露要求。

## ⛔ 必須不做（MUST NOT）

- 不得憑記憶／無來源生成期刊事實（清單、影響因子、排名、接受率、分區）；若引用內建的策展資料，該資料須帶來源＋查證日期，過時效窗標「待複查」。
- 不得在使用者沒給作者須知時，自行「腦補」目標刊的字數、結構、引用格式或審稿政策。
- 不得替使用者決定投哪個刊，也不得替改內容與論點立場。
- 不得把「待補」的規範當成已確認往下對標。
- 不得把學位論文原稿視為可直接投稿的定稿，也不得只做格式轉換而漏掉文稿類型差距。
- 不得因教育期刊常見 APA，就在未查到作者須知時默認 APA 7；只有目標頁明列才能寫已確認。

## 已暴露的坑（防重犯）

- 最危險：被問「這本刊要求什麼」時，AI 直接編出一份像真的投稿須知 → 守 MUST NOT 第 2 條，無來源即標待補。
- 把通用 APA 當成所有 SSCI 刊的格式 → 各刊格式自訂，須回查該刊須知。
- 對質性論文硬套量化報告規範（效應量／信賴區間）→ 走質性側對標。
- 已發表文章頁冒充作者須知（2026-06-30）：JALT 文章頁能證明題材契合與 DOI 真實，但 Word、APA 7、匿名稿與 AI declaration 只能由 submissions page 支撐。
- AI 政策查得到就不能弱化（2026-06-30）：JALT 明列超過 editorial/proofreading assistance 的生成式 AI 使用須 dedicated declaration section，因此列 must-fix 並交 `ai-disclosure`。
