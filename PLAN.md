# Task: Add Bilingual (Chinese/English) Support to word_compare

## Strict Rules — READ FIRST

1. **ONLY do i18n work.** Do not fix bugs, do not refactor, do not rename variables, do not reorganize imports, do not "improve" anything.
2. **Do not touch any business logic.** `models.py`, `document_compare.py`, `single_extractor.py`, and `generate_mock.py` MUST remain exactly as-is.
3. **Do not modify function signatures or class interfaces, EXCEPT adding a `lang` parameter to HTML generation.**
4. **Do not delete or rewrite existing code blocks.** Only replace hardcoded Chinese strings with translation calls.
5. **Do not add type hints, docstrings, comments, or formatting changes to existing code.**
6. **If you see a bug or something you want to improve — IGNORE IT. Do not mention it. Do not fix it.**
7. **The goal is immediate language switching.** When the user selects a language in the dropdown, the GUI text changes immediately without a restart. The generated HTML report will use the currently selected language.

## What to Build

### Step 1: Create `word_review/i18n.py`

- Create a `_TRANSLATIONS` dict with all UI strings (both GUI and HTML).
  - GUI keys: e.g. `"gui.title"`, `"gui.mode_extract"`, `"gui.btn.analyze"`, `"msg.no_file"`, etc.
  - HTML keys: e.g. `"html.header.offline"`, `"html.hint.jump"`, `"html.badge.insert"`, `"html.detail.old_author"`, etc.
- Each key maps to `{"zh": "中文文字", "en": "English text"}`
- Provide:
  - `_current_language` variable, default `"zh"`
  - `t(key, **kwargs) -> str` function that returns the translated string (with `.format(**kwargs)` support)
  - `set_language(lang: str)` function
  - `get_language() -> str` function
  - `get_translations(lang: str) -> dict` function (useful for injecting translations into HTML JS)

### Step 2: Update `gui.py` (Tkinter UI)

**A) Add Language Switcher:**
- Add a `ttk.Combobox` in a prominent place (e.g., top-right corner of the window) with values `["繁體中文", "English"]`, state `"readonly"`.
- On selection change, call `set_language()` based on the selection, then call `retranslate()`.

**B) Update Widget Texts:**
- Replace hardcoded Chinese strings in `gui.py` with `t("key")`.
- If a widget displays static text and isn't saved to `self` yet (e.g., `ttk.Label(..., text="...")`), assign it to an instance variable like `self._lbl_title = ttk.Label(...)`.

**C) Implement `retranslate(self)`:**
- Add a `retranslate(self)` method to `WordReviewApp` that calls `.configure(text=t("..."))` on every widget storing text, and updates the root window title.
- Remember to also update the texts inside dialog boxes (like `messagebox`) dynamically when they are triggered.

### Step 3: Update `word_review/html_report.py`

**A) Update Signature:**
- Change `generate_html(report: AnalysisReport, output_path: str | Path)` to `generate_html(report: AnalysisReport, output_path: str | Path, lang: str = "zh")`.

**B) Translate HTML Template:**
- Replace hardcoded Chinese text in the static HTML skeleton with `t("html.some_key")` (import `t` and set the language temporarily, or pass the language down).
- Translate the HTML `lang` attribute dynamically (`zh-Hant` or `en`).

**C) Inject Translations into JavaScript:**
- The HTML report uses JS for interactive logic. Inject the necessary translations as a JSON object into the `<script>` tag.
- Example: `<script> const I18N = {json.dumps(get_translations(lang)["html"])}; ... </script>`
- Replace hardcoded strings in the JS template (e.g., `"沒有符合條件的項目"`, `"新增"`, `"批註"`) with lookups from the injected `I18N` object.

## Execution Plan for Agents

- **Agent Manager:** Orchestrate the work. Create `PLAN.md` based on this document.
- **Agent Coder:** Implement Step 1, Step 2, and Step 3 strictly following the rules.
- **Agent Tester/Reviewer:** Ensure GUI and HTML generate correctly in both languages and no business logic is broken.
