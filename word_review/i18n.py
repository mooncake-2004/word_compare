_current_language = "zh"

_TRANSLATIONS = {
    "gui.title": {"zh": "Word 修訂與批註分析工具", "en": "Word Revision and Comment Analysis Tool"},
    "gui.description": {"zh": "文件只在本機處理；分析完成後生成單一離線 HTML 報告。", "en": "Documents are processed locally; a single offline HTML report is generated after analysis."},
    "gui.mode.title": {"zh": "1. 選擇模式", "en": "1. Select Mode"},
    "gui.mode.extract": {"zh": "單文件：提取修訂與批註", "en": "Single document: extract revisions and comments"},
    "gui.mode.compare": {"zh": "雙文件：比較兩份目前版本（可含修訂／批註）", "en": "Two documents: compare current versions (revisions/comments included)"},
    "gui.input.title": {"zh": "2. 選擇文件", "en": "2. Select Documents"},
    "gui.file.tracked": {"zh": "帶修訂的 DOCX", "en": "DOCX with revisions"},
    "gui.file.old": {"zh": "版本一 DOCX", "en": "Old Version"},
    "gui.file.new": {"zh": "版本二 DOCX", "en": "New Version"},
    "gui.file.compare_hint": {"zh": "會接受兩份文件各自的既有修訂後再比較，只顯示版本一與版本二之間的差異。", "en": "Existing revisions in each document are accepted before comparison; only differences between Version One and Version Two are shown."},
    "gui.output.title": {"zh": "3. 輸出位置", "en": "3. Output Location"},
    "gui.btn.choose_folder": {"zh": "選擇資料夾", "en": "Choose Folder"},
    "gui.open_after": {"zh": "完成後自動用瀏覽器打開報告", "en": "Open the report in a browser when complete"},
    "gui.btn.analyze": {"zh": "開始分析", "en": "Start Analysis"},
    "gui.btn.mock": {"zh": "生成 Mock 測試文件", "en": "Generate Mock Test Documents"},
    "gui.btn.open_folder": {"zh": "打開輸出資料夾", "en": "Open Output Folder"},
    "gui.btn.browse": {"zh": "瀏覽…", "en": "Browse…"},
    "gui.dialog.choose_word": {"zh": "選擇 Word 文件", "en": "Select Word Document"},
    "gui.dialog.word_file": {"zh": "Word 文件", "en": "Word Document"},
    "gui.dialog.choose_output": {"zh": "選擇輸出資料夾", "en": "Select Output Folder"},
    "gui.dialog.choose_mock_output": {"zh": "選擇 Mock 測試文件的輸出資料夾", "en": "Select Output Folder for Mock Test Documents"},
    "gui.filename.extract": {"zh": "修訂批註報告", "en": "revision_comment_report"},
    "gui.filename.compare": {"zh": "與", "en": "_and_"},
    "gui.filename.compare_suffix": {"zh": "對比報告", "en": "comparison_report"},
    "msg.initial": {"zh": "請選擇分析模式和 Word 文件。", "en": "Select an analysis mode and Word document."},
    "msg.no_file.title": {"zh": "尚未選擇文件", "en": "No Document Selected"},
    "msg.no_file.extract": {"zh": "請選擇一份帶修訂或批註的 DOCX。", "en": "Select a DOCX with revisions or comments."},
    "msg.no_file.compare": {"zh": "請同時選擇版本一和版本二 DOCX。", "en": "Select both Version One and Version Two DOCX files."},
    "msg.processing": {"zh": "處理中，請稍候……", "en": "Processing, please wait…"},
    "msg.success.status": {"zh": "完成：{result}", "en": "Complete: {result}"},
    "msg.success.title": {"zh": "處理完成", "en": "Processing Complete"},
    "msg.success.detail": {"zh": "文件已生成：\n{result}", "en": "Document generated:\n{result}"},
    "msg.failure.status": {"zh": "失敗：{error}", "en": "Failed: {error}"},
    "msg.failure.title": {"zh": "處理失敗", "en": "Processing Failed"},
    "html.report_title.compare": {"zh": "版本差異：{old} → {new}", "en": "Version Differences: {old} -> {new}"},
    "html.report_title.extract": {"zh": "修訂與批註分析：{file}", "en": "Revision & Comment Analysis: {file}"},
    "html.header.offline": {"zh": "本地離線報告", "en": "Local Offline Report"},
    "html.search.placeholder": {"zh": "搜尋作者、日期或內容", "en": "Search author, date, or content"},
    "html.nav.previous": {"zh": "上一個變更", "en": "Previous Change"},
    "html.nav.next": {"zh": "下一個變更", "en": "Next Change"},
    "html.nav.expand": {"zh": "展開整份文件", "en": "Expand Full Document"},
    "html.nav.nearby": {"zh": "只看附近段落", "en": "Show Nearby Paragraphs Only"},
    "html.hint.jump": {"zh": "像 Word「尋找」一樣逐項跳轉；可展開整份文件查看所有變化。", "en": "Jump through items like Word's Find feature; expand the full document to view all changes."},
    "html.badge.insert": {"zh": "新增", "en": "Added"},
    "html.badge.delete": {"zh": "刪除", "en": "Deleted"},
    "html.badge.comment": {"zh": "批註", "en": "Comment"},
    "html.badge.modify": {"zh": "修改", "en": "Modified"},
    "html.filter.all": {"zh": "全部", "en": "All"},
    "html.empty.no_text": {"zh": "（無文字）", "en": "(No text)"},
    "html.empty.no_items": {"zh": "沒有符合條件的項目", "en": "No matching items"},
    "html.author.unrecorded": {"zh": "未記錄", "en": "Not recorded"},
    "html.paragraph.no_match": {"zh": "（此版本無對應段落）", "en": "(No corresponding paragraph in this version)"},
    "html.paragraph.number": {"zh": "第 {number} 段", "en": "Paragraph {number}"},
    "html.compare.before": {"zh": "修改前：{value}", "en": "Before: {value}"},
    "html.compare.after": {"zh": "修改後：{value}", "en": "After: {value}"},
    "html.compare.version_one": {"zh": "版本一", "en": "Version One"},
    "html.compare.version_two": {"zh": "版本二", "en": "Version Two"},
    "html.empty.no_preview": {"zh": "文件沒有可預覽的段落", "en": "The document has no paragraphs to preview"},
    "html.paragraph.blank": {"zh": "（空白段落）", "en": "(Blank paragraph)"},
    "html.detail.title": {"zh": "詳細內容", "en": "Details"},
    "html.detail.author_time": {"zh": "作者／時間", "en": "Author / Time"},
    "html.detail.quoted_text": {"zh": "被批註原文", "en": "Commented Text"},
    "html.detail.unanchored": {"zh": "（未找到錨定文字）", "en": "(Anchored text not found)"},
    "html.detail.comment": {"zh": "批註", "en": "Comment"},
    "html.detail.old_author": {"zh": "版本一修訂人", "en": "Version One Editor"},
    "html.detail.new_author": {"zh": "版本二修訂人", "en": "Version Two Editor"},
    "html.detail.before": {"zh": "修改前", "en": "Before"},
    "html.detail.after": {"zh": "修改後", "en": "After"},
    "html.detail.none": {"zh": "（無）", "en": "(None)"},
    "html.summary.compare": {"zh": "{count} 項版本差異（只比較兩份文件目前內容）", "en": "{count} version differences (comparing only the current content of both documents)"},
    "html.summary.extract": {"zh": "{revisions} 項修訂，{comments} 條批註", "en": "{revisions} revisions, {comments} comments"},
}


def t(key, **kwargs):
    value = _TRANSLATIONS.get(key, {}).get(_current_language, key)
    return value.format(**kwargs) if kwargs else value


def set_language(lang):
    global _current_language
    if lang not in ("zh", "en"):
        raise ValueError("Unsupported language")
    _current_language = lang


def get_language():
    return _current_language


def get_translations(lang):
    if lang not in ("zh", "en"):
        raise ValueError("Unsupported language")
    translations = {}
    for key, values in _TRANSLATIONS.items():
        group, name = key.split(".", 1)
        translations.setdefault(group, {})[name] = values[lang]
    return translations
