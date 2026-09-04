"""Word 修訂分析工具的 Windows 桌面圖形介面。"""

from __future__ import annotations

import os
import threading
import webbrowser
from pathlib import Path
from tkinter import BooleanVar, StringVar, Tk, filedialog, messagebox
from tkinter import ttk

from generate_mock import generate_mock
from word_review.document_compare import compare_documents
from word_review.html_report import generate_html
from word_review.i18n import get_language, set_language, t
from word_review.single_extractor import extract_tracked_document


class WordReviewApp:
    """提供檔案選擇、分析、Mock 生成及報告開啟功能。"""

    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title(t("gui.title"))
        self.root.geometry("780x540")
        self.root.minsize(680, 480)

        self.mode = StringVar(value="extract")
        self.tracked_path = StringVar()
        self.old_path = StringVar()
        self.new_path = StringVar()
        self.output_dir = StringVar(value=str(Path.home() / "WordReviewReports"))
        self.open_after = BooleanVar(value=True)
        self.status = StringVar(value=t("msg.initial"))
        self._file_labels = []
        self._browse_buttons = []

        self._build_ui()
        self._switch_mode()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=20)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer)
        header.pack(fill="x")
        self._lbl_title = ttk.Label(header, text=t("gui.title"), font=("Microsoft JhengHei UI", 18, "bold"))
        self._lbl_title.pack(side="left")
        self.language = StringVar(value="繁體中文" if get_language() == "zh" else "English")
        self._language_box = ttk.Combobox(header, textvariable=self.language, values=["繁體中文", "English"], state="readonly", width=12)
        self._language_box.pack(side="right")
        self._language_box.bind("<<ComboboxSelected>>", self._change_language)
        self._lbl_description = ttk.Label(outer, text=t("gui.description"), foreground="#52606d")
        self._lbl_description.pack(anchor="w", pady=(4, 18))

        self._mode_box = ttk.LabelFrame(outer, text=t("gui.mode.title"), padding=12)
        mode_box = self._mode_box
        mode_box.pack(fill="x")
        self._radio_extract = ttk.Radiobutton(mode_box, text=t("gui.mode.extract"), variable=self.mode, value="extract", command=self._switch_mode)
        self._radio_extract.pack(side="left", padx=(0, 24))
        self._radio_compare = ttk.Radiobutton(mode_box, text=t("gui.mode.compare"), variable=self.mode, value="compare", command=self._switch_mode)
        self._radio_compare.pack(side="left")

        self.input_box = ttk.LabelFrame(outer, text=t("gui.input.title"), padding=12)
        self.input_box.pack(fill="x", pady=14)
        self.extract_frame = ttk.Frame(self.input_box)
        self.compare_frame = ttk.Frame(self.input_box)
        self._file_row(self.extract_frame, t("gui.file.tracked"), self.tracked_path)
        self._file_row(self.compare_frame, t("gui.file.old"), self.old_path)
        self._file_row(self.compare_frame, t("gui.file.new"), self.new_path)
        self._lbl_compare_hint = ttk.Label(self.compare_frame, text=t("gui.file.compare_hint"), foreground="#52606d")
        self._lbl_compare_hint.pack(anchor="w", pady=(6, 0))

        self._output_box = ttk.LabelFrame(outer, text=t("gui.output.title"), padding=12)
        output_box = self._output_box
        output_box.pack(fill="x")
        row = ttk.Frame(output_box)
        row.pack(fill="x")
        ttk.Entry(row, textvariable=self.output_dir).pack(side="left", fill="x", expand=True)
        self._btn_choose_folder = ttk.Button(row, text=t("gui.btn.choose_folder"), command=self._choose_output_dir)
        self._btn_choose_folder.pack(side="left", padx=(8, 0))
        self._check_open_after = ttk.Checkbutton(output_box, text=t("gui.open_after"), variable=self.open_after)
        self._check_open_after.pack(anchor="w", pady=(8, 0))

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=18)
        self.run_button = ttk.Button(actions, text=t("gui.btn.analyze"), command=self._start_analysis)
        self.run_button.pack(side="left")
        self._btn_mock = ttk.Button(actions, text=t("gui.btn.mock"), command=self._start_mock)
        self._btn_mock.pack(side="left", padx=10)
        self._btn_open_folder = ttk.Button(actions, text=t("gui.btn.open_folder"), command=self._open_output_dir)
        self._btn_open_folder.pack(side="left")

        ttk.Separator(outer).pack(fill="x", pady=(2, 12))
        self._lbl_status = ttk.Label(outer, textvariable=self.status, wraplength=720, foreground="#344054")
        self._lbl_status.pack(anchor="w")

    def _file_row(self, parent: ttk.Frame, label: str, variable: StringVar) -> None:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=5)
        label_widget = ttk.Label(row, text=label, width=16)
        label_widget.pack(side="left")
        self._file_labels.append(label_widget)
        ttk.Entry(row, textvariable=variable).pack(side="left", fill="x", expand=True)
        browse_button = ttk.Button(row, text=t("gui.btn.browse"), command=lambda: self._choose_docx(variable))
        browse_button.pack(side="left", padx=(8, 0))
        self._browse_buttons.append(browse_button)

    def _switch_mode(self) -> None:
        self.extract_frame.pack_forget()
        self.compare_frame.pack_forget()
        if self.mode.get() == "extract":
            self.extract_frame.pack(fill="x")
        else:
            self.compare_frame.pack(fill="x")

    def _choose_docx(self, variable: StringVar) -> None:
        selected = filedialog.askopenfilename(title=t("gui.dialog.choose_word"), filetypes=[(t("gui.dialog.word_file"), "*.docx")])
        if selected:
            variable.set(selected)

    def _choose_output_dir(self) -> None:
        selected = filedialog.askdirectory(title=t("gui.dialog.choose_output"))
        if selected:
            self.output_dir.set(selected)

    def _start_analysis(self) -> None:
        mode = self.mode.get()
        tracked_path = self.tracked_path.get()
        old_path = self.old_path.get()
        new_path = self.new_path.get()
        output_dir = self.output_dir.get()
        if mode == "extract" and not tracked_path:
            messagebox.showwarning(t("msg.no_file.title"), t("msg.no_file.extract"))
            return
        if mode == "compare" and (not old_path or not new_path):
            messagebox.showwarning(t("msg.no_file.title"), t("msg.no_file.compare"))
            return
        self._run_in_background(
            lambda: self._analyze(mode, tracked_path, old_path, new_path, output_dir)
        )

    @staticmethod
    def _analyze(
        mode: str,
        tracked_path: str,
        old_path: str,
        new_path: str,
        output_dir_value: str,
    ) -> Path:
        output_dir = Path(output_dir_value).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)
        if mode == "extract":
            source = Path(tracked_path)
            report = extract_tracked_document(source)
            output = output_dir / f"{source.stem}_{t('gui.filename.extract')}.html"
        else:
            old_source = Path(old_path)
            new_source = Path(new_path)
            report = compare_documents(old_source, new_source)
            output = output_dir / f"{old_source.stem}_{t('gui.filename.compare').strip('_')}_{new_source.stem}_{t('gui.filename.compare_suffix')}.html"
        return generate_html(report, output, get_language())

    def _start_mock(self) -> None:
        selected = filedialog.askdirectory(title=t("gui.dialog.choose_mock_output"))
        if selected:
            self._run_in_background(lambda: self._generate_mock(Path(selected)))

    @staticmethod
    def _generate_mock(output_dir: Path) -> Path:
        generate_mock(output_dir)
        return output_dir

    def _run_in_background(self, operation) -> None:  # type: ignore[no-untyped-def]
        self.run_button.configure(state="disabled")
        self.status.set(t("msg.processing"))

        def worker() -> None:
            try:
                result = operation()
                self.root.after(0, lambda: self._operation_finished(result))
            except Exception as exc:
                self.root.after(0, lambda error=exc: self._operation_failed(error))

        threading.Thread(target=worker, daemon=True).start()

    def _operation_finished(self, result: Path) -> None:
        self.run_button.configure(state="normal")
        self.status.set(t("msg.success.status", result=result))
        messagebox.showinfo(t("msg.success.title"), t("msg.success.detail", result=result))
        if self.open_after.get() and result.suffix.lower() == ".html":
            webbrowser.open(result.resolve().as_uri())

    def _operation_failed(self, error: Exception) -> None:
        self.run_button.configure(state="normal")
        self.status.set(t("msg.failure.status", error=error))
        messagebox.showerror(t("msg.failure.title"), str(error))

    def _change_language(self, event):
        initial = self.status.get() == t("msg.initial")
        set_language("zh" if self.language.get() == "繁體中文" else "en")
        self.retranslate()
        if initial:
            self.status.set(t("msg.initial"))

    def retranslate(self):
        self.root.title(t("gui.title"))
        self._lbl_title.configure(text=t("gui.title"))
        self._lbl_description.configure(text=t("gui.description"))
        self._mode_box.configure(text=t("gui.mode.title"))
        self._radio_extract.configure(text=t("gui.mode.extract"))
        self._radio_compare.configure(text=t("gui.mode.compare"))
        self.input_box.configure(text=t("gui.input.title"))
        self._file_labels[0].configure(text=t("gui.file.tracked"))
        self._file_labels[1].configure(text=t("gui.file.old"))
        self._file_labels[2].configure(text=t("gui.file.new"))
        for browse_button in self._browse_buttons:
            browse_button.configure(text=t("gui.btn.browse"))
        self._lbl_compare_hint.configure(text=t("gui.file.compare_hint"))
        self._output_box.configure(text=t("gui.output.title"))
        self._btn_choose_folder.configure(text=t("gui.btn.choose_folder"))
        self._check_open_after.configure(text=t("gui.open_after"))
        self.run_button.configure(text=t("gui.btn.analyze"))
        self._btn_mock.configure(text=t("gui.btn.mock"))
        self._btn_open_folder.configure(text=t("gui.btn.open_folder"))

    def _open_output_dir(self) -> None:
        output_dir = Path(self.output_dir.get()).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.startfile(output_dir)  # type: ignore[attr-defined]
        except (AttributeError, OSError):
            webbrowser.open(output_dir.resolve().as_uri())


def main() -> None:
    root = Tk()
    WordReviewApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
