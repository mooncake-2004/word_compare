"""Word 修訂／批註分析工具命令列入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from word_review.document_compare import compare_documents
from word_review.html_report import generate_html
from word_review.single_extractor import extract_tracked_document


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="離線分析 Word 修訂、批註及段落差異")
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract = subparsers.add_parser("extract", help="提取一份 DOCX 的修訂與批註")
    extract.add_argument("document", help="帶 Track Changes 的 DOCX")
    extract.add_argument("-o", "--output", default="output/tracked_report.html", help="輸出 HTML 路徑")

    compare = subparsers.add_parser("compare", help="比較兩份乾淨 DOCX")
    compare.add_argument("old_document", help="舊版本 DOCX")
    compare.add_argument("new_document", help="新版本 DOCX")
    compare.add_argument("-o", "--output", default="output/comparison_report.html", help="輸出 HTML 路徑")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "extract":
            report = extract_tracked_document(args.document)
        else:
            report = compare_documents(args.old_document, args.new_document)
        result = generate_html(report, Path(args.output))
        print(f"報告已生成：{result.resolve()}")
        return 0
    except Exception as exc:  # 命令列工具統一輸出易讀錯誤，保留非零狀態碼。
        print(f"錯誤：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
