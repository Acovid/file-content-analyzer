"""
String Search Mode Unit Tests

These tests protect the existing String Search semantics while match-position,
context-excerpt, and detailed-report functionality are introduced.

Covered behavior:
- occurrence counts remain equivalent to str.count()
- matches for one term are non-overlapping
- exact line numbers and columns are collected
- case-insensitive matching preserves existing behavior
- multiple requested strings can match the same source line independently
- context windows respect requested line counts and file boundaries
- overlapping and adjacent context windows are merged
- separated windows remain separate
- Summary reporting remains available
- Detailed reporting includes line numbers and MATCH annotations
- multiple terms on one line remain unambiguous
- very long matching lines are safely abbreviated
"""

import os
import tempfile
import unittest

from fca.reporting import write_search_report
from fca.search_mode import (
    build_context_excerpts,
    collect_match_positions,
)


class TestStringSearchPositions(unittest.TestCase):
    def test_counts_match_existing_str_count_semantics(self):
        text = "alpha alpha\nbeta alpha\n"
        strings = [
            "alpha",
            "beta",
            "missing",
        ]

        counts, matches = collect_match_positions(
            text=text,
            strings=strings,
            case_sensitive=True,
        )

        expected = {
            term: text.count(term)
            for term in strings
            if text.count(term)
        }

        self.assertEqual(
            counts,
            expected,
        )

        self.assertEqual(
            len(matches),
            sum(expected.values()),
        )

    def test_same_term_matches_do_not_overlap(self):
        counts, matches = collect_match_positions(
            text="aaa",
            strings=["aa"],
            case_sensitive=True,
        )

        self.assertEqual(
            counts,
            {"aa": 1},
        )

        self.assertEqual(
            len(matches),
            1,
        )

        self.assertEqual(
            matches[0]["start"],
            0,
        )

        self.assertEqual(
            matches[0]["end"],
            2,
        )

    def test_line_numbers_and_columns_are_one_based(self):
        text = (
            "first line\n"
            "xx target yy\n"
            "last target"
        )

        counts, matches = collect_match_positions(
            text=text,
            strings=["target"],
            case_sensitive=True,
        )

        self.assertEqual(
            counts,
            {"target": 2},
        )

        self.assertEqual(
            [
                (
                    match["line_number"],
                    match["column_start"],
                    match["column_end"],
                )
                for match in matches
            ],
            [
                (2, 4, 9),
                (3, 6, 11),
            ],
        )

    def test_case_insensitive_matching(self):
        text = (
            "Alpha\n"
            "ALPHA alpha\n"
        )

        counts, matches = collect_match_positions(
            text=text,
            strings=["alpha"],
            case_sensitive=False,
        )

        self.assertEqual(
            counts,
            {"alpha": 3},
        )

        self.assertEqual(
            [
                match["line_number"]
                for match in matches
            ],
            [1, 2, 2],
        )

    def test_multiple_terms_can_match_same_line(self):
        text = (
            ".bering-btn-primary "
            ".bering-btn-secondary {}\n"
        )

        strings = [
            "bering-btn-primary",
            "bering-btn-secondary",
        ]

        counts, matches = collect_match_positions(
            text=text,
            strings=strings,
            case_sensitive=True,
        )

        self.assertEqual(
            counts,
            {
                "bering-btn-primary": 1,
                "bering-btn-secondary": 1,
            },
        )

        self.assertEqual(
            len(matches),
            2,
        )

        self.assertEqual(
            [
                match["line_number"]
                for match in matches
            ],
            [1, 1],
        )

        self.assertEqual(
            [
                match["term"]
                for match in matches
            ],
            strings,
        )


class TestStringSearchContext(unittest.TestCase):
    @staticmethod
    def _make_text(
        line_count: int,
        match_lines: set[int],
    ) -> str:
        return "\n".join(
            (
                f"line {line} "
                f"{'TARGET' if line in match_lines else ''}"
            ).rstrip()
            for line in range(
                1,
                line_count + 1,
            )
        )

    def test_zero_context_returns_matching_line_only(self):
        text = self._make_text(
            5,
            {3},
        )

        _, matches = collect_match_positions(
            text,
            ["TARGET"],
            True,
        )

        excerpts = build_context_excerpts(
            text,
            matches,
            context_lines=0,
        )

        self.assertEqual(
            len(excerpts),
            1,
        )

        self.assertEqual(
            excerpts[0]["start_line"],
            3,
        )

        self.assertEqual(
            excerpts[0]["end_line"],
            3,
        )

        self.assertEqual(
            [
                line["line_number"]
                for line in excerpts[0]["lines"]
            ],
            [3],
        )

    def test_context_is_clipped_to_file_boundaries(self):
        text = self._make_text(
            6,
            {1, 6},
        )

        _, matches = collect_match_positions(
            text,
            ["TARGET"],
            True,
        )

        excerpts = build_context_excerpts(
            text,
            matches,
            context_lines=1,
        )

        self.assertEqual(
            len(excerpts),
            2,
        )

        self.assertEqual(
            (
                excerpts[0]["start_line"],
                excerpts[0]["end_line"],
            ),
            (1, 2),
        )

        self.assertEqual(
            (
                excerpts[1]["start_line"],
                excerpts[1]["end_line"],
            ),
            (5, 6),
        )

    def test_overlapping_context_windows_are_merged(self):
        text = self._make_text(
            20,
            {10, 13},
        )

        _, matches = collect_match_positions(
            text,
            ["TARGET"],
            True,
        )

        excerpts = build_context_excerpts(
            text,
            matches,
            context_lines=3,
        )

        self.assertEqual(
            len(excerpts),
            1,
        )

        self.assertEqual(
            (
                excerpts[0]["start_line"],
                excerpts[0]["end_line"],
            ),
            (7, 16),
        )

    def test_adjacent_context_windows_are_merged(self):
        text = self._make_text(
            20,
            {5, 10},
        )

        _, matches = collect_match_positions(
            text,
            ["TARGET"],
            True,
        )

        excerpts = build_context_excerpts(
            text,
            matches,
            context_lines=2,
        )

        self.assertEqual(
            len(excerpts),
            1,
        )

        self.assertEqual(
            (
                excerpts[0]["start_line"],
                excerpts[0]["end_line"],
            ),
            (3, 12),
        )

    def test_separated_context_windows_remain_separate(self):
        text = self._make_text(
            20,
            {4, 16},
        )

        _, matches = collect_match_positions(
            text,
            ["TARGET"],
            True,
        )

        excerpts = build_context_excerpts(
            text,
            matches,
            context_lines=2,
        )

        self.assertEqual(
            len(excerpts),
            2,
        )

        self.assertEqual(
            (
                excerpts[0]["start_line"],
                excerpts[0]["end_line"],
            ),
            (2, 6),
        )

        self.assertEqual(
            (
                excerpts[1]["start_line"],
                excerpts[1]["end_line"],
            ),
            (14, 18),
        )

    def test_all_matches_on_a_line_are_attached_to_that_line(self):
        text = (
            "before\n"
            "alpha beta alpha\n"
            "after"
        )

        _, matches = collect_match_positions(
            text,
            ["alpha", "beta"],
            True,
        )

        excerpts = build_context_excerpts(
            text,
            matches,
            context_lines=1,
        )

        matching_line = (
            excerpts[0]["lines"][1]
        )

        self.assertEqual(
            matching_line["line_number"],
            2,
        )

        self.assertEqual(
            [
                match["term"]
                for match in matching_line["matches"]
            ],
            [
                "alpha",
                "beta",
                "alpha",
            ],
        )

    def test_negative_context_is_rejected(self):
        text = "TARGET"

        _, matches = collect_match_positions(
            text,
            ["TARGET"],
            True,
        )

        with self.assertRaises(
            ValueError
        ):
            build_context_excerpts(
                text,
                matches,
                context_lines=-1,
            )


class TestDetailedSearchReporting(unittest.TestCase):
    def _write_report(
        self,
        text: str,
        strings: list[str],
        context_lines: int = 1,
        max_line_length: int = 500,
        detailed: bool = True,
    ) -> str:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(
            temp_dir.cleanup
        )

        entry_file = os.path.join(
            temp_dir.name,
            "file_content_analyzer.py",
        )

        source_path = os.path.join(
            temp_dir.name,
            "sample.css",
        )

        counts, matches = collect_match_positions(
            text=text,
            strings=strings,
            case_sensitive=True,
        )

        results = {
            source_path: counts
        }

        detailed_results = None

        if detailed:
            detailed_results = {
                source_path: {
                    "matches": matches,
                    "excerpts": build_context_excerpts(
                        text=text,
                        matches=matches,
                        context_lines=context_lines,
                    ),
                }
            }

        report_path = write_search_report(
            entry_file=entry_file,
            directory=temp_dir.name,
            case_sensitive=True,
            strings=strings,
            results=results,
            detailed_results=detailed_results,
            context_lines=context_lines,
            max_line_length=max_line_length,
        )

        with open(
            report_path,
            "r",
            encoding="utf-8",
        ) as f:
            return f.read()

    def test_summary_report_remains_available(self):
        report = self._write_report(
            text="TARGET\n",
            strings=["TARGET"],
            detailed=False,
        )

        self.assertIn(
            "TARGET: 1",
            report,
        )

        self.assertNotIn(
            "Detailed Match Context",
            report,
        )

        self.assertNotIn(
            "Report detail: Detailed",
            report,
        )

    def test_detailed_report_contains_line_and_match_annotation(self):
        report = self._write_report(
            text=(
                "before\n"
                "alpha TARGET omega\n"
                "after"
            ),
            strings=["TARGET"],
            context_lines=1,
        )

        self.assertIn(
            "Report detail: Detailed",
            report,
        )

        self.assertIn(
            "Context lines before/after: 1",
            report,
        )

        self.assertIn(
            "> 2 | alpha TARGET omega",
            report,
        )

        self.assertIn(
            "MATCH: TARGET (columns 7-12)",
            report,
        )

    def test_multiple_terms_on_same_line_are_identified(self):
        report = self._write_report(
            text=(
                ".bering-btn-primary "
                ".bering-btn-secondary {}"
            ),
            strings=[
                "bering-btn-primary",
                "bering-btn-secondary",
            ],
            context_lines=0,
        )

        self.assertIn(
            "MATCH: bering-btn-primary",
            report,
        )

        self.assertIn(
            "MATCH: bering-btn-secondary",
            report,
        )

    def test_long_matching_line_is_truncated_around_match(self):
        text = (
            "x" * 1000
            + "TARGET"
            + "y" * 1000
        )

        report = self._write_report(
            text=text,
            strings=["TARGET"],
            context_lines=0,
            max_line_length=120,
        )

        self.assertIn(
            "TARGET",
            report,
        )

        self.assertIn(
            "[line truncated: original length 2006 characters]",
            report,
        )

        self.assertNotIn(
            text,
            report,
        )


if __name__ == "__main__":
    unittest.main()
    
# End of file test_search_mode.py