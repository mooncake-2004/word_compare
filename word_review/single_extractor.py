"""直接解析 DOCX XML，提取修訂、批註及上下文。"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from lxml import etree

from .models import AnalysisReport, CommentInfo, ParagraphInfo, RevisionInfo

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
W = f"{{{W_NS}}}"


def _attribute(element: etree._Element, name: str, default: str = "") -> str:
    return element.get(f"{W}{name}", default)


def _node_text(element: etree._Element) -> str:
    """讀取節點內一般文字與刪除文字。"""

    return "".join(element.xpath(".//w:t/text() | .//w:delText/text()", namespaces=NS))


def _paragraph_text(paragraph: etree._Element, view: str) -> str:
    """產生修改前（original）或接受修訂後（current）的段落文字。"""

    pieces: list[str] = []
    for node in paragraph.xpath(".//w:t | .//w:delText | .//w:tab | .//w:br", namespaces=NS):
        ancestors = node.iterancestors()
        in_insert = any(ancestor.tag == f"{W}ins" for ancestor in ancestors)
        ancestors = node.iterancestors()
        in_delete = any(ancestor.tag == f"{W}del" for ancestor in ancestors)
        if (view == "current" and in_delete) or (view == "original" and in_insert):
            continue
        if node.tag == f"{W}tab":
            pieces.append("\t")
        elif node.tag == f"{W}br":
            pieces.append("\n")
        elif node.text:
            pieces.append(node.text)
    return "".join(pieces)


def _load_xml(package: ZipFile, member: str) -> etree._Element | None:
    try:
        return etree.fromstring(package.read(member))
    except KeyError:
        return None


def extract_tracked_document(docx_path: str | Path) -> AnalysisReport:
    """分析一份帶修訂或批註的 DOCX。"""

    path = Path(docx_path)
    if path.suffix.lower() != ".docx":
        raise ValueError("輸入文件必須是 .docx")
    if not path.is_file():
        raise FileNotFoundError(f"找不到文件：{path}")

    try:
        with ZipFile(path) as package:
            document_root = _load_xml(package, "word/document.xml")
            comments_root = _load_xml(package, "word/comments.xml")
    except BadZipFile as exc:
        raise ValueError(f"文件不是有效的 DOCX：{path}") from exc

    if document_root is None:
        raise ValueError("DOCX 缺少 word/document.xml")

    paragraph_nodes = document_root.xpath(".//w:body//w:p", namespaces=NS)
    paragraphs = [
        ParagraphInfo(
            index=index,
            original_text=_paragraph_text(node, "original"),
            current_text=_paragraph_text(node, "current"),
            location_id=f"paragraph-{index}",
        )
        for index, node in enumerate(paragraph_nodes)
    ]

    revisions: list[RevisionInfo] = []
    for paragraph_index, paragraph in enumerate(paragraph_nodes):
        revision_nodes = paragraph.xpath(".//w:ins | .//w:del", namespaces=NS)
        for serial, node in enumerate(revision_nodes):
            is_insert = node.tag == f"{W}ins"
            text = _node_text(node)
            revision_id = _attribute(node, "id", f"{paragraph_index}-{serial}")
            revisions.append(
                RevisionInfo(
                    revision_id=revision_id,
                    revision_type="insert" if is_insert else "delete",
                    before_text="" if is_insert else text,
                    after_text=text if is_insert else "",
                    author=_attribute(node, "author", "未知作者"),
                    date=_attribute(node, "date"),
                    paragraph_index=paragraph_index,
                    paragraph_original=paragraphs[paragraph_index].original_text,
                    paragraph_current=paragraphs[paragraph_index].current_text,
                    location_id=f"revision-{revision_id}-{len(revisions)}",
                )
            )

    # 按文件順序追蹤 commentRangeStart/End，收集被批註的文字。
    active_comments: set[str] = set()
    quoted_parts: dict[str, list[str]] = defaultdict(list)
    starts: dict[str, int] = {}
    ends: dict[str, int] = {}
    current_paragraph = -1
    paragraph_indices = {node: index for index, node in enumerate(paragraph_nodes)}
    for node in document_root.iter():
        if node.tag == f"{W}p":
            current_paragraph = paragraph_indices.get(node, current_paragraph)
        elif node.tag == f"{W}commentRangeStart":
            comment_id = _attribute(node, "id")
            active_comments.add(comment_id)
            starts.setdefault(comment_id, current_paragraph)
        elif node.tag == f"{W}commentRangeEnd":
            comment_id = _attribute(node, "id")
            ends[comment_id] = current_paragraph
            active_comments.discard(comment_id)
        elif node.tag in {f"{W}t", f"{W}delText"} and node.text:
            for comment_id in active_comments:
                quoted_parts[comment_id].append(node.text)

    comments: list[CommentInfo] = []
    if comments_root is not None:
        for node in comments_root.xpath(".//w:comment", namespaces=NS):
            comment_id = _attribute(node, "id")
            start = starts.get(comment_id, 0)
            end = ends.get(comment_id, start)
            comments.append(
                CommentInfo(
                    comment_id=comment_id,
                    content="\n".join(
                        "".join(p.xpath(".//w:t/text()", namespaces=NS))
                        for p in node.xpath("./w:p", namespaces=NS)
                    ),
                    quoted_text="".join(quoted_parts.get(comment_id, [])),
                    author=_attribute(node, "author", "未知作者"),
                    date=_attribute(node, "date"),
                    start_paragraph=max(start, 0),
                    end_paragraph=max(end, max(start, 0)),
                    location_id=f"comment-{comment_id}",
                )
            )

    return AnalysisReport(
        mode="extract",
        title=f"修訂與批註分析：{path.name}",
        paragraphs=paragraphs,
        revisions=revisions,
        comments=comments,
        metadata={
            "source": str(path),
            "revision_count": len(revisions),
            "comment_count": len(comments),
        },
    )
