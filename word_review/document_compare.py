"""比較兩份 DOCX 的目前版本內容，並保留各版本修訂人資訊。"""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from lxml import etree

from .models import AnalysisReport, ParagraphDiff, ParagraphInfo

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
W = f"{{{W_NS}}}"


@dataclass(slots=True)
class _VersionParagraph:
    """一個版本中接受既有修訂後的段落及修訂中繼資料。"""

    text: str
    authors: list[str]
    dates: list[str]


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _current_text(paragraph: etree._Element) -> str:
    """只讀取接受修訂後的文字：保留 w:ins，排除 w:del。"""

    pieces: list[str] = []
    for node in paragraph.xpath(".//w:t | .//w:delText | .//w:tab | .//w:br", namespaces=NS):
        if any(ancestor.tag == f"{W}del" for ancestor in node.iterancestors()):
            continue
        if node.tag == f"{W}tab":
            pieces.append("\t")
        elif node.tag == f"{W}br":
            pieces.append("\n")
        elif node.text:
            pieces.append(node.text)
    return "".join(pieces).strip()


def _extract_paragraphs(path: Path) -> list[_VersionParagraph]:
    """直接解析 XML，讓帶 Track Changes 的兩份文件也能正確比較。"""

    try:
        with ZipFile(path) as package:
            root = etree.fromstring(package.read("word/document.xml"))
    except (BadZipFile, KeyError) as exc:
        raise ValueError(f"文件不是有效的 DOCX：{path}") from exc

    body = root.find(".//w:body", namespaces=NS)
    if body is None:
        return []

    paragraph_nodes: list[etree._Element] = []
    for child in body:
        if child.tag == f"{W}p":
            paragraph_nodes.append(child)
        elif child.tag == f"{W}tbl":
            paragraph_nodes.extend(child.xpath(".//w:tr/w:tc/w:p", namespaces=NS))

    result: list[_VersionParagraph] = []
    for paragraph in paragraph_nodes:
        text = _current_text(paragraph)
        if not text:
            continue
        revisions = paragraph.xpath(".//w:ins | .//w:del", namespaces=NS)
        result.append(
            _VersionParagraph(
                text=text,
                authors=_unique([node.get(f"{W}author", "") for node in revisions]),
                dates=_unique([node.get(f"{W}date", "") for node in revisions]),
            )
        )
    return result


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
    """比較兩份文件目前呈現的版本，不展開各自更早的修訂歷史。"""

    old_file, new_file = Path(old_path), Path(new_path)
    for path in (old_file, new_file):
        if path.suffix.lower() != ".docx" or not path.is_file():
            raise FileNotFoundError(f"找不到有效的 DOCX：{path}")

    old_paragraphs = _extract_paragraphs(old_file)
    new_paragraphs = _extract_paragraphs(new_file)
    old_texts = [paragraph.text for paragraph in old_paragraphs]
    new_texts = [paragraph.text for paragraph in new_paragraphs]
    matcher = SequenceMatcher(None, old_texts, new_texts, autojunk=False)
    differences: list[ParagraphDiff] = []
    comparison_rows: list[ParagraphDiff] = []

    def add_row(kind: str, old_index: int | None, new_index: int | None) -> None:
        old_paragraph = old_paragraphs[old_index] if old_index is not None else None
        new_paragraph = new_paragraphs[new_index] if new_index is not None else None
        row_index = len(comparison_rows)
        row = ParagraphDiff(
            diff_id=f"diff-{row_index}",
            diff_type=kind,  # type: ignore[arg-type]
            old_text=old_paragraph.text if old_paragraph else "",
            new_text=new_paragraph.text if new_paragraph else "",
            old_index=old_index,
            new_index=new_index,
            context_index=row_index,
            inline_changes=(
                _inline_changes(old_paragraph.text, new_paragraph.text)
                if kind == "modify" and old_paragraph and new_paragraph
                else []
            ),
            old_authors=old_paragraph.authors if old_paragraph else [],
            new_authors=new_paragraph.authors if new_paragraph else [],
            old_dates=old_paragraph.dates if old_paragraph else [],
            new_dates=new_paragraph.dates if new_paragraph else [],
        )
        comparison_rows.append(row)
        if kind != "equal":
            differences.append(row)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for offset in range(i2 - i1):
                add_row("equal", i1 + offset, j1 + offset)
        elif tag == "delete":
            for old_index in range(i1, i2):
                add_row("delete", old_index, None)
        elif tag == "insert":
            for new_index in range(j1, j2):
                add_row("insert", None, new_index)
        else:
            paired = min(i2 - i1, j2 - j1)
            for offset in range(paired):
                add_row("modify", i1 + offset, j1 + offset)
            for old_index in range(i1 + paired, i2):
                add_row("delete", old_index, None)
            for new_index in range(j1 + paired, j2):
                add_row("insert", None, new_index)

    paragraphs = [
        ParagraphInfo(index=i, original_text=item.text, current_text=item.text, location_id=f"paragraph-{i}")
        for i, item in enumerate(new_paragraphs)
    ]
    return AnalysisReport(
        mode="compare",
        title=f"版本差異：{old_file.name} → {new_file.name}",
        paragraphs=paragraphs,
        differences=differences,
        comparison_rows=comparison_rows,
        metadata={
            "old_source": str(old_file),
            "new_source": str(new_file),
            "old_name": old_file.name,
            "new_name": new_file.name,
            "old_paragraph_count": len(old_paragraphs),
            "new_paragraph_count": len(new_paragraphs),
            "difference_count": len(differences),
        },
    )
