# Word 修訂與批註分析工具

這是一個完全離線的 Python 工具，用於提取 `.docx` 的 Track Changes／批註，或比較兩份乾淨 Word 文件。輸出為內嵌 CSS、JavaScript 和資料的單一互動式 HTML，不會上傳文件或呼叫外部服務。

## 功能

- 直接使用 `lxml` 解析 `word/document.xml` 中的 `w:ins`、`w:del`、`w:author` 和 `w:date`。
- 解析 `word/comments.xml` 及正文中的批註範圍，取得批註內容和被批註原文。
- 產生修改前及接受修訂後的段落文字。
- 使用 `difflib.SequenceMatcher` 比較兩份文件的段落和修改段落內的字元。
- 互動式左右雙欄 HTML；點擊項目後顯示目標段落前後各 3 段。
- 新增、刪除、批註和修改以不同顏色顯示，並可搜尋及篩選。

## 環境與安裝

需要 Python 3.12。安裝依賴：

```bash README.md
python -m pip install -r requirements.txt
```

依賴只有：

- `lxml`
- `python-docx`

## 生成 Mock 文件

```bash README.md
python generate_mock.py --output-dir mock_data
```

將生成：

- `mock_data/contract_tracked.docx`：5 個底層修訂節點、4 位修改人及 2 條批註。
- `mock_data/contract_before.docx`：乾淨的合同原始版。
- `mock_data/contract_after.docx`：包含新增、刪除和修改段落的乾淨最終版。

`generate_mock.py` 先使用 `python-docx` 建立 DOCX 骨架，再直接修改 ZIP 內的 WordprocessingML，加入修訂節點、批註 XML、relationship 和 content type。

## 模式一：提取修訂與批註

```bash README.md
python main.py extract mock_data/contract_tracked.docx \
  --output output/tracked_report.html
```

## 模式二：比較兩份文件

```bash README.md
python main.py compare \
  mock_data/contract_before.docx \
  mock_data/contract_after.docx \
  --output output/comparison_report.html
```

## 打開報告

生成的 HTML 不需要 HTTP 服務器。可下載到本機雙擊，或在有桌面環境的 Linux 中執行：

```bash README.md
xdg-open output/tracked_report.html
```

Codespace 若未提供圖形瀏覽器，可在文件瀏覽器中右鍵下載 HTML 後於本機打開。

## 文件結構

```text README.md
.
├── generate_mock.py
├── main.py
├── requirements.txt
└── word_review/
    ├── __init__.py
    ├── models.py
    ├── single_extractor.py
    ├── document_compare.py
    └── html_report.py
```

## 限制

- 單文件模式以 `word/document.xml` 正文為主要分析範圍；頁眉、頁腳、腳註中的修訂目前不納入。
- 一次文字替換通常在 Word XML 中表示為相鄰的刪除和插入，因此會保留成兩條修訂記錄。
- 雙文件模式以段落為比較單位；內容相差很大的連續段落會依 `SequenceMatcher` 的 opcode 配對為修改、刪除或新增。