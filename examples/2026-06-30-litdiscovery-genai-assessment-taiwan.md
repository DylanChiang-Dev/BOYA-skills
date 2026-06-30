# 實測案例：lit-discovery 中文題全鏈探勘——生成式 AI 與台灣學習評量

> 日期：2026-06-30 ｜ skill：lit-discovery（Stable 證據補強）
> 題目：生成式 AI 與台灣學習評量／高等教育治理。
> 目的：補上先前缺口——不只壓測 venue 比對層，而是完整跑一次「中文題探勘 → 真實文章命中 → 相關性分層 → venue 比對」。
>
> 紅線：本案例只使用 OpenAlex、Crossref 與公開可訪問來源頁；候選均來自 API 回應或公開頁。未命中的 venue 一律 `❓待查`，不把查無寫成論文差，也不替作者決定收捨。

## 研究問題與檢索策略

**研究問題**：生成式 AI 進入台灣教育場域後，學習評量如何被重新設計、治理或規範？

| 概念 | 同義詞／變體 |
|---|---|
| 生成式 AI | 生成式AI、生成式人工智慧、ChatGPT、GenAI、generative AI |
| 學習評量 | 學習評量、評量治理、assessment、assessment practice |
| 教育場域 | 台灣、高等教育、學校、higher education |

**納入準則**：2023 年後；中文或英文；教育／高教／評量相關；期刊論文、公開 DOI 條目、公開全文或可回源頁。

**排除準則**：只談技術模型、不談教育評量或治理者降為低相關；API 回非論文或舊書章節保留但標低相關／待人工。

> gate：檢索範圍與最後收哪篇仍由研究者決定。本案例只示範候選如何被撈出、分層與留痕。

## 實跑查詢（As of 2026-06-30）

### 查詢 1：中文精準題名

```bash
curl -L -s 'https://api.openalex.org/works?filter=title.search:%E7%94%9F%E6%88%90%E5%BC%8FAI%E6%99%82%E4%BB%A3%E7%9A%84%E5%AD%B8%E7%BF%92%E8%A9%95%E9%87%8F&per-page=5'

curl -L -s 'https://api.crossref.org/works?query.bibliographic=%E7%94%9F%E6%88%90%E5%BC%8FAI%E6%99%82%E4%BB%A3%E7%9A%84%E5%AD%B8%E7%BF%92%E8%A9%95%E9%87%8F&rows=5&mailto=ld@example.org'
```

**命中**：

- OpenAlex `W4406228191`，DOI `10.53106/168063602025020370002`，題名〈生成式AI時代的學習評量〉，2025，來源《教育研究月刊》，卷／期 370，頁 015-031。
- Crossref 同 DOI；publisher 為 Angle Publishing Co., Ltd.；resource URL 指向 `https://ericdata.com/tw/detail.aspx?no=913255`；英文題名 `Learning Assessment in the Era of Generative AI`。

### 查詢 2：中文寬查

```bash
curl -L -s 'https://api.openalex.org/works?filter=title.search:%E7%94%9F%E6%88%90%E5%BC%8FAI%20%E9%AB%98%E7%AD%89%E6%95%99%E8%82%B2&per-page=5'
```

**命中**：OpenAlex count = 0。這只表示該組查詢在 OpenAlex 未命中，不代表文獻不存在。

### 查詢 3：英文對照查詢

```bash
curl -L -s 'https://api.crossref.org/works?query.bibliographic=Higher%20education%20assessment%20practice%20in%20the%20era%20of%20generative%20AI%20tools&rows=3&mailto=ld@example.org'
```

**命中**：

- Ogunleye et al. (2024), "Higher education assessment practice in the era of generative AI tools," *Journal of Applied Learning & Teaching*, DOI `10.37074/jalt.2024.7.1.28`，resource URL `https://journals.sfu.ca/jalt/index.php/jalt/article/view/1533`。
- 同查詢另回 2025/2026 書章與 STEM assessment 條目，因場域或文類不同，保留為中／低相關線索。

## 候選清單與分層

| # | 候選（書目縮略） | 相關層級 | 出處（venue） | 命中來源 / 檢索式 | 待辦 |
|---|---|---|---|---|---|
| 1 | 凃金堂（2025）〈生成式AI時代的學習評量〉，《教育研究月刊》370:15-31，DOI `10.53106/168063602025020370002` | 高 | `❓待查`（本輪只確認書目與公開條目；未逐刊命中 TSSCI 2025 名單，不得猜級） | OpenAlex title.search 精準題名；Crossref bibliographic 精準題名 | `citation-verify` 查書目；全文精讀交 `lit-matrix` |
| 2 | Ogunleye et al. (2024) "Higher education assessment practice in the era of generative AI tools," *Journal of Applied Learning & Teaching*, DOI `10.37074/jalt.2024.7.1.28` | 高 | `❓待查`（非本庫已核 SSCI/A&HCI 條目；可作英文對照，不給分級） | Crossref bibliographic 英文題名 | `citation-verify` 查書目；作國際對照 |
| 3 | Farrokhnia et al. (2025) "Generative AI in higher education: Transformative tools for research, teaching, and assessment," in *Navigating Generative AI in Higher Education* | 中 | 書章／不給 venue 級 | Crossref 同英文查詢 | 若研究要含專書章節再讀 |
| 4 | Amar & Benchouk (2026) "The Power Generative AI for Innovative Assessment Design in STEM Education Programs," Springer book chapter | 低 | 書章／STEM 導向，不給 venue 級 | Crossref 同英文查詢 | 由研究者決定看不看 |
| 5 | 「生成式AI 高等教育」OpenAlex 寬查 | 待人工 | 不適用 | OpenAlex count=0 | 改用華藝／國圖／Google Scholar 人工補撈 |

## venue 比對與來源

- **TSSCI 2025（適用 2026）**：本輪更新 `knowledge/venues.md`，來源層為國科會人文社會科學研究中心公開入口與公開 PDF；候選 #1 的《教育研究月刊》未在本輪逐刊表中硬判命中，故標 `❓待查`。不得因「教育類期刊」或 DOI 真實就推定 TSSCI。
- **CSSCI 2025-2026**：本輪只使用公開可訪問的南大官方入口與高校轉載 PDF／頁面作來源層級說明；未登入南大評價中心，不對大陸刊作具體級別判定。
- **SSCI/A&HCI**：候選 #2 為 Journal of Applied Learning & Teaching，不在本庫已列的 Clarivate 官方查詢結果內；標 `❓待查`，不引入 JCR/CAS 分區。

三句提醒：venue 強只代表「建議先讀」，不代表切題；查不到出處不代表論文差；最後讀不讀仍由研究者決定。

## 打磨發現（寫回規則）

1. **中文精準題名比寬查有效**：OpenAlex 對「生成式AI 高等教育」零命中，但精準題名命中 DOI。中文題不宜只跑寬泛關鍵詞，應把人工找到的題名反查 API。
2. **API 命中可證明條目存在，不等於 venue 已核**：#1 有 OpenAlex/Crossref/DOI 三重線索，但 TSSCI/CSSCI 分級仍須另查官方名單；書目真偽與 venue 分級是兩條線。
3. **英文對照會帶出可讀材料，但不能冒充中文語境覆蓋**：#2 與研究問題高度相關，可作國際對照；但它不能替代台灣中文文獻。
4. **書章要保留文類標記**：Crossref 會回 book chapter。它可能有用，但不應混作期刊論文，也不給期刊 venue 級。

## 方法與聲明

- 工具：`lit-discovery` 第 1-4 步＋第 3.5 步 venue 證據。
- 本輪候選均來自 OpenAlex/Crossref 或公開 resource URL；未用訓練記憶補文獻。
- 候選仍是 `🤖 待核`，下一步應交 `citation-verify` 查書目，再交 `lit-matrix` 精讀。
- 紅線守住：未說「查無＝不存在」；未把候選標 ✅；未替使用者收捨；未憑記憶補 TSSCI/CSSCI/SSCI 等級。

## 來源

- OpenAlex Works API：`https://api.openalex.org/works?filter=title.search:...`
- Crossref Works API：`https://api.crossref.org/works?query.bibliographic=...`
- Crossref/DOI：`https://doi.org/10.53106/168063602025020370002`
- ERICDATA 條目：`https://ericdata.com/tw/detail.aspx?no=913255`
- JALT 條目：`https://journals.sfu.ca/jalt/index.php/jalt/article/view/1533`
