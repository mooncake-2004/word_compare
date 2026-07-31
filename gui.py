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
from word_review.single_extractor import extract_tracked_document


class WordReviewApp:
    """提供檔案選擇、分析、Mock 生成及報告開啟功能。"""

    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("Word 修訂與批註分析工具")
        self.root.geometry("780x540")
        self.root.minsize(680, 480)

        self.mode = StringVar(value="extract")
        self.tracked_path = StringVar()
        self.old_path = StringVar()
        self.new_path = StringVar()
        self.output_dir = StringVar(value=str(Path.home() / "WordReviewReports"))
        self.open_after = BooleanVar(value=True)
        self.status = StringVar(value="請選擇分析模式和 Word 文件。")

        self._build_ui()
        self._switch_mode()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=20)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Word 修訂與批註分析工具", font=("Microsoft JhengHei UI", 18, "bold")).pack(anchor="w")
        ttk.Label(outer, text="文件只在本機處理；分析完成後生成單一離線 HTML 報告。", foreground="#52606d").pack(anchor="w", pady=(4, 18))

        mode_box = ttk.LabelFrame(outer, text="1. 選擇模式", padding=12)
        mode_box.pack(fill="x")
        ttk.Radiobutton(mode_box, text="單文件：提取修訂與批註", variable=self.mode, value="extract", command=self._switch_mode).pack(side="left", padx=(0, 24))
        ttk.Radiobutton(mode_box, text="雙文件：比較兩份目前版本（可含修訂／批註）", variable=self.mode, value="compare", command=self._switch_mode).pack(side="left")

        self.input_box = ttk.LabelFrame(outer, text="2. 選擇文件", padding=12)
        self.input_box.pack(fill="x", pady=14)
        self.extract_frame = ttk.Frame(self.input_box)
        self.compare_frame = ttk.Frame(self.input_box)
        self._file_row(self.extract_frame, "帶修訂的 DOCX", self.tracked_path)
        self._file_row(self.compare_frame, "版本一 DOCX", self.old_path)
        self._file_row(self.compare_frame, "版本二 DOCX", self.new_path)
        ttk.Label(self.compare_frame, text="會接受兩份文件各自的既有修訂後再比較，只顯示版本一與版本二之間的差異。", foreground="#52606d").pack(anchor="w", pady=(6, 0))

        output_box = ttk.LabelFrame(outer, text="3. 輸出位置", padding=12)
        output_box.pack(fill="x")
        row = ttk.Frame(output_box)
        row.pack(fill="x")
        ttk.Entry(row, textvariable=self.output_dir).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="選擇資料夾", command=self._choose_output_dir).pack(side="left", padx=(8, 0))
        ttk.Checkbutton(output_box, text="完成後自動用瀏覽器打開報告", variable=self.open_after).pack(anchor="w", pady=(8, 0))

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=18)
        self.run_button = ttk.Button(actions, text="開始分析", command=self._start_analysis)
        self.run_button.pack(side="left")
        ttk.Button(actions, text="生成 Mock 測試文件", command=self._start_mock).pack(side="left", padx=10)
        ttk.Button(actions, text="打開輸出資料夾", command=self._open_output_dir).pack(side="left")

        ttk.Separator(outer).pack(fill="x", pady=(2, 12))
        ttk.Label(outer, textvariable=self.status, wraplength=720, foreground="#344054").pack(anchor="w")

    def _file_row(self, parent: ttk.Frame, label: str, variable: StringVar) -> None:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text=label, width=16).pack(side="left")
        ttk.Entry(row, textvariable=variable).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="瀏覽…", command=lambda: self._choose_docx(variable)).pack(side="left", padx=(8, 0))

    def _switch_mode(self) -> None:
        self.extract_frame.pack_forget()
        self.compare_frame.pack_forget()
        if self.mode.get() == "extract":
            self.extract_frame.pack(fill="x")
        else:
            self.compare_frame.pack(fill="x")

    def _choose_docx(self, variable: StringVar) -> None:
        selected = filedialog.askopenfilename(title="選擇 Word 文件", filetypes=[("Word 文件", "*.docx")])
        if selected:
            variable.set(selected)

    def _choose_output_dir(self) -> None:
        selected = filedialog.askdirectory(title="選擇輸出資料夾")
        if selected:
            self.output_dir.set(selected)

    def _start_analysis(self) -> None:
        mode = self.mode.get()
        tracked_path = self.tracked_path.get()
        old_path = self.old_path.get()
        new_path = self.new_path.get()
        output_dir = self.output_dir.get()
        if mode == "extract" and not tracked_path:
            messagebox.showwarning("尚未選擇文件", "請選擇一份帶修訂或批註的 DOCX。")
            return
        if mode == "compare" and (not old_path or not new_path):
            messagebox.showwarning("尚未選擇文件", "請同時選擇版本一和版本二 DOCX。")
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
            output = output_dir / f"{source.stem}_修訂批註報告.html"
        else:
            old_source = Path(old_path)
            new_source = Path(new_path)
            report = compare_documents(old_source, new_source)
            output = output_dir / f"{old_source.stem}_與_{new_source.stem}_對比報告.html"
        return generate_html(report, output)

    def _start_mock(self) -> None:
        selected = filedialog.askdirectory(title="選擇 Mock 測試文件的輸出資料夾")
        if selected:
            self._run_in_background(lambda: self._generate_mock(Path(selected)))

    @staticmethod
    def _generate_mock(output_dir: Path) -> Path:
        generate_mock(output_dir)
        return output_dir

    def _run_in_background(self, operation) -> None:  # type: ignore[no-untyped-def]
        self.run_button.configure(state="disabled")
        self.status.set("處理中，請稍候……")

        def worker() -> None:
            try:
                result = operation()
                self.root.after(0, lambda: self._operation_finished(result))
            except Exception as exc:
                self.root.after(0, lambda error=exc: self._operation_failed(error))

        threading.Thread(target=worker, daemon=True).start()

    def _operation_finished(self, result: Path) -> None:
        self.run_button.configure(state="normal")
        self.status.set(f"完成：{result}")
        messagebox.showinfo("處理完成", f"文件已生成：\n{result}")
        if self.open_after.get() and result.suffix.lower() == ".html":
            webbrowser.open(result.resolve().as_uri())

    def _operation_failed(self, error: Exception) -> None:
        self.run_button.configure(state="normal")
        self.status.set(f"失敗：{error}")
        messagebox.showerror("處理失敗", str(error))

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
