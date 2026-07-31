"""使用 difflib 比較兩份乾淨 DOCX 的段落。"""

from __future__ import annotations

from difflib import SequenceMatcher
from pathlib import Path

from docx import Document

from .models import AnalysisReport, ParagraphDiff, ParagraphInfo


def _extract_paragraphs(path: Path) -> list[str]:
    """依文件順序提取正文及表格儲存格中的非空段落。"""

    document = Document(path)
    values: list[str] = []
    body = document.element.body
    for child in body.iterchildren():
        local_name = child.tag.rsplit("}", 1)[-1]
        if local_name == "p":
            text = "".join(child.xpath(".//w:t/text()"))
            if text.strip():
                values.append(text.strip())
        elif local_name == "tbl":
            for paragraph in child.xpath(".//w:tr/w:tc/w:p"):
                text = "".join(paragraph.xpath(".//w:t/text()"))
                if text.strip():
                    values.append(text.strip())
    return values


def _inline_changes(old_text: str, new_text: str) -> list[dict[str, str]]:
    """計算修改段落內的字元級差異。"""

    changes: list[dict[str, str]] = []
    matcher = SequenceMatcher(None, old_text, new_text, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            changes.append({"type": "equal", "text": new_text[j1:j2]})
        elif tag == "delete":
            changes.append({"type": "delete", "text": old_text[i1:i2]})
        elif tag == "insert":
            changes.append({"type": "insert", "text": new_text[j1:j2]})
        else:
            changes.append({"type": "delete", "text": old_text[i1:i2]})
            changes.append({"type": "insert", "text": new_text[j1:j2]})
    return changes


def compare_documents(old_path: str | Path, new_path: str | Path) -> AnalysisReport:
    """按段落比較兩份 DOCX，回傳新增、刪除及修改項目。"""

    old_file, new_file = Path(old_path), Path(new_path)
    for path in (old_file, new_file):
        if path.suffix.lower() != ".docx" or not path.is_file():
            raise FileNotFoundError(f"找不到有效的 DOCX：{path}")

    old_paragraphs = _extract_paragraphs(old_file)
    new_paragraphs = _extract_paragraphs(new_file)
    matcher = SequenceMatcher(None, old_paragraphs, new_paragraphs, autojunk=False)
    differences: list[ParagraphDiff] = []

    def add_diff(kind: str, old_index: int | None, new_index: int | None) -> None:
        old_text = old_paragraphs[old_index] if old_index is not None else ""
        new_text = new_paragraphs[new_index] if new_index is not None else ""
        anchor = new_index if new_index is not None else min(old_index or 0, max(len(new_paragraphs) - 1, 0))
        differences.append(
            ParagraphDiff(
                diff_id=f"diff-{len(differences)}",
                diff_type=kind,  # type: ignore[arg-type]
                old_text=old_text,
                new_text=new_text,
                old_index=old_index,
                new_index=new_index,
                context_index=anchor,
                inline_changes=_inline_changes(old_text, new_text) if kind == "modify" else [],
            )
        )

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag == "delete":
            for old_index in range(i1, i2):
                add_diff("delete", old_index, None)
        elif tag == "insert":
            for new_index in range(j1, j2):
                add_diff("insert", None, new_index)
        else:
            paired = min(i2 - i1, j2 - j1)
            for offset in range(paired):
                add_diff("modify", i1 + offset, j1 + offset)
            for old_index in range(i1 + paired, i2):
                add_diff("delete", old_index, None)
            for new_index in range(j1 + paired, j2):
                add_diff("insert", None, new_index)

    paragraphs = [
        ParagraphInfo(index=i, original_text=text, current_text=text, location_id=f"paragraph-{i}")
        for i, text in enumerate(new_paragraphs)
    ]
    return AnalysisReport(
        mode="compare",
        title=f"文件對比：{old_file.name} → {new_file.name}",
        paragraphs=paragraphs,
        differences=differences,
        metadata={
            "old_source": str(old_file),
            "new_source": str(new_file),
            "old_paragraph_count": len(old_paragraphs),
            "new_paragraph_count": len(new_paragraphs),
            "difference_count": len(differences),
        },
    )
