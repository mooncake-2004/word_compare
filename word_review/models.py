"""分析結果使用的資料模型。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


@dataclass(slots=True)
class ParagraphInfo:
    """Word 段落的原始及接受修訂後文字。"""

    index: int
    original_text: str
    current_text: str
    location_id: str


@dataclass(slots=True)
class RevisionInfo:
    """一個 w:ins 或 w:del 修訂節點。"""

    revision_id: str
    revision_type: Literal["insert", "delete"]
    before_text: str
    after_text: str
    author: str
    date: str
    paragraph_index: int
    paragraph_original: str
    paragraph_current: str
    location_id: str


@dataclass(slots=True)
class CommentInfo:
    """一條 Word 批註及其錨定原文。"""

    comment_id: str
    content: str
    quoted_text: str
    author: str
    date: str
    start_paragraph: int
    end_paragraph: int
    location_id: str


@dataclass(slots=True)
class ParagraphDiff:
    """兩份文件之間的一項段落差異。"""

    diff_id: str
    diff_type: Literal["equal", "insert", "delete", "modify"]
    old_text: str
    new_text: str
    old_index: int | None
    new_index: int | None
    context_index: int
    inline_changes: list[dict[str, str]] = field(default_factory=list)
    old_authors: list[str] = field(default_factory=list)
    new_authors: list[str] = field(default_factory=list)
    old_dates: list[str] = field(default_factory=list)
    new_dates: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AnalysisReport:
    """可交給 HTML 產生器的完整報告。"""

    mode: Literal["extract", "compare"]
    title: str
    paragraphs: list[ParagraphInfo]
    revisions: list[RevisionInfo] = field(default_factory=list)
    comments: list[CommentInfo] = field(default_factory=list)
    differences: list[ParagraphDiff] = field(default_factory=list)
    comparison_rows: list[ParagraphDiff] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """轉成只含 JSON 相容型別的字典。"""

        return asdict(self)
