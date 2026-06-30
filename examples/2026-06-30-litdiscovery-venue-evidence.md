# 實測案例：lit-discovery 新增「先讀哪篇」venue 證據步驟（沿用公部門×生成式 AI 案例）

> 2026-06-30，`lit-discovery` 新增第 3.5 步「標出處強弱、給先讀提示」後的首跑真錄。
> **延用案例 013**（`2026-06-21-litdiscovery-genai-public-sector.md`）已撈出的同一批候選，不重撈，只對它們**加跑 venue 證據這條新線**，測四件事：分級會不會被誠實回查官方名單、查不到會不會老實標 ❓、預印本會不會被誤給等級、三句免責有沒有講。
> 啟發來源：`yilaai/paper-quality-filter`（venue 證據層概念）。其理工本位分區（JCR／CAS／CCF／EI）與自動排序腳本**撞本庫設計邊界、不採用**；只取「拿真表查、附證據、查不到老實標、人來拍板」骨架，改寫成人文社科版、無腳本、人在環中。

## 輸入

- 候選來源：案例 013 已撈的 7 筆（OpenAlex／Crossref 實打命中），全部 🤖 待核。
- 新需求：使用者問「這幾篇先讀哪篇？出處夠不夠分量？」
- 分級回查對象：`knowledge/venues.md` 列的官方名單（CSSCI／TSSCI／北大核心／AMI核心／A&HCI）。

## 實跑（venue 逐筆回查，As of 2026-06-30）

新步驟第一關：**沒有 venue 欄位就不能判**。案例 013 的候選只記了標題＋DOI，沒記期刊名。先用 Crossref 解 DOI 補出 `container-title`，再拿刊名查官方名單。

| # | 候選（縮略） | 解出的出處 | 類型 | venue 證據 | 命中？ |
|---|---|---|---|---|---|
| 1 | Evaluating public sector employee perceptions...（10.1177/01655515241293775） | **Journal of Information Science**（SAGE, ISSN 0165-5515） | 期刊論文 | ❓待查 | 英文 LIS／社科刊，**不在** CSSCI／TSSCI／北大／AMI／A&HCI |
| 2 | Automating Government Report Generation（10.1145/3691352） | ACM（Crossref 本次未解出容器名） | 研討會/ACM | ❓待查 | 未解出刊名＋CS 場域，本表不涵蓋 |
| 3 | Exploring the Future...Generative AI Adoption（10.2139/ssrn.5258102） | SSRN | **預印本** | 不給級 | 預印本無正式出處，按鐵律不給 venue 級 |
| 4 | Synergizing GenAI and Cybersecurity（10.36227/techrxiv...） | TechRxiv | **預印本** | 不給級 | 同上；且案例 013 已標 ⚪ 低相關 |
| 5 | 立法委員個人助理之研究（2003，中文學位論文） | 學位論文 | 非期刊 | 不適用 | 學位論文非期刊，venue 分級不適用 |

> 結果：5 筆裡 0 筆拿到我們表內的分級——**沒有一筆被硬給等級**。1 筆解出真期刊但不在本表（待查）、1 筆未解出刊名（待查）、2 筆預印本（不給級）、1 筆學位論文（不適用）。

## 三句免責（每次給 venue 提示必說，本輪有講）

1. 出處強只代表「建議先讀」，**不代表切題**（案例 013 第 4 筆 cybersecurity 高被引卻離題，正是反證）。
2. **查不到出處 ≠ 論文差**——第 1 筆是同儕審查正式期刊，只是不在我們這幾張中文／A&HCI 名單裡。
3. 最後讀不讀，**由你定**。

## 打磨發現（feed 回規則）

1. **來源表缺 SSCI＝英文社科候選一律落空**。本案候選是英文公共行政／資訊科學論文，對應的國際索引是 **SSCI（社會科學）**，不是只收藝術人文的 A&HCI。原表只放了 A&HCI，導致第 1 筆這種正牌 SSCI 期刊被迫標 ❓待查，看起來像「查無」其實是「我們沒把這張表納進來」。**修正：`knowledge/venues.md` 補一列 SSCI（Clarivate Web of Science，社會科學引文索引），與 A&HCI 並列為國際線。** 仍只當「收錄與否」用，不引入 IF 分區（守住不採理工分區的邊界）。
2. **venue 步驟的第一道關是「有沒有 venue 欄位」**。案例 013 只記標題＋DOI，得先 Crossref 解 `container-title` 才能查——坐實 SKILL 鐵律 6 與 paper-quality-filter 同源教訓：「只有標題不能判出處」。寫進工作流：給 venue 提示前先確認有刊名，沒有就先解 DOI，解不出標 ❓。
3. **預印本不給級是對的、且要主動講**。SSRN／TechRxiv 兩筆按鐵律不給 venue 級，避免把「掛在預印本平台」誤讀成有正式出處。
4. **這批英文候選讓 venue 步驟幾乎全 ❓**，反證 venue 證據對**中文／台灣期刊候選**才最有用（CSSCI／TSSCI／北大／AMI 命中率才高）。本案當時留下「升 Stable 前仍須補一個以中文／台灣期刊為主的候選跑」；後續已於 v1.0.0 補 `examples/2026-06-30-litdiscovery-genai-assessment-taiwan.md` 與 TSSCI/CSSCI 來源層級。

## 方法與聲明

- 工具：本倉庫 `lit-discovery` 第 3.5 步（新增首跑）。DOI 解析為 2026-06-30 實際以 Crossref 公開 API（`api.crossref.org/works/<doi>`）查得 `container-title`／`type`／`ISSN`。
- 紅線守住：**無一筆被編造分級**；不在表內或預印本一律 ❓／不給級，未美化成已證實；理工分區（JCR／CAS／CCF／EI）未引入；未做自動排序腳本，排序判斷留人。
- 邊界：本步驟只給「出處強弱」線索，不判真偽（交 citation-verify）、不判切題（看相關性那條線）、不替使用者決定收捨。
