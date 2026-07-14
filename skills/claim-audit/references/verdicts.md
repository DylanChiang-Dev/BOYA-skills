# Claim Audit 判定規約

## 判定值

| verdict | 使用條件 | gate |
|---|---|---|
| `supported` | 原文在當前人群、時間、變項、方向與強度下支持整句 | pass |
| `partial` | 只支持句子的一部分，或主張範圍大於來源 | review |
| `distorted` | 主張改變了數值、方向、限定、人群或因果強度 | block |
| `unsupported` | 原文沒有該資訊，或研究設計不能支持該說法 | block |
| `inaccessible` | 來源存在，但本輪無法取得足夠原文 | review |
| `not_checked` | 尚未完成回源核驗 | review |
| `not_applicable` | 該記錄不是需要外部來源支持的事實主張 | pass |

## 存取層級

- `full_text`：已取得論文、報告、法規或官方頁面的對應內文。
- `abstract`：只有原來源摘要；僅能支持摘要明寫的主張。
- `metadata`：只有題名、作者、年份、DOI 等書目資訊；不得用於 supported、partial 或 distorted。

## 最小證據欄位

`supported`、`partial`、`distorted` 的每個來源至少要有：

- `pointer`：DOI、URL、檔案路徑或其他穩定指標。
- `locator`：頁碼、節、段落、圖、表或補充材料位置。
- `checked_at`：`YYYY-MM-DD` 查證日期。
- `excerpt`：最長 500 字的原文短摘錄。

`inaccessible` 仍須保留 pointer、checked_at 與嘗試紀錄，但不假造 locator 或 excerpt。

## 範圍對齊清單

依序比對：研究對象、時間點／期間、變項與測量、數值／分母／單位、方向、不確定性、研究設計、作者解釋與當前作者推論。
