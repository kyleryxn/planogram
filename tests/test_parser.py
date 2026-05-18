"""Tests for the parser service helper functions."""

from planogram.services.parser import filter_lines, to_pipe_lines


class TestToPipeLines:
    def test_basic_multi_column(self):
        text = (
            "DATE: 2025-01-06\n"
            "Clark Kent | 09:00 | 17:00\n"
            "Lois Lane | 10:00 | 18:00\n"
            "\n"
            "DATE: 2025-01-07\n"
            "Clark Kent | 12:00 | 20:00\n"
        )
        result = to_pipe_lines(text)
        assert result == [
            "Clark Kent | 2025-01-06 | 09:00 | 17:00",
            "Lois Lane | 2025-01-06 | 10:00 | 18:00",
            "Clark Kent | 2025-01-07 | 12:00 | 20:00",
        ]

    def test_empty_input(self):
        assert to_pipe_lines("") == []

    def test_no_date_header_ignored(self):
        # Lines without a DATE: header should not appear in output
        assert to_pipe_lines("Clark Kent | 09:00 | 17:00") == []

    def test_blank_lines_skipped(self):
        text = "DATE: 2025-01-06\n\n\nClark Kent | 09:00 | 17:00\n"
        result = to_pipe_lines(text)
        assert len(result) == 1

    def test_date_header_case_insensitive(self):
        text = "date: 2025-01-06\nClark Kent | 09:00 | 17:00\n"
        result = to_pipe_lines(text)
        assert len(result) == 1

    def test_missing_end_time(self):
        text = "DATE: 2025-01-06\nClark Kent | 09:00\n"
        result = to_pipe_lines(text)
        assert result == ["Clark Kent | 2025-01-06 | 09:00 | "]


class TestFilterLines:
    LINES = [
        "Clark Kent | 2025-01-06 | 09:00 | 17:00",
        "Lois Lane | 2025-01-06 | 10:00 | 18:00",
        "Jimmy Olsen | 2025-01-06 | 11:00 | 19:00",
    ]

    def test_full_name_match(self):
        result = filter_lines(self.LINES, "Clark Kent")
        assert result == ["Clark Kent | 2025-01-06 | 09:00 | 17:00"]

    def test_partial_word_match(self):
        result = filter_lines(self.LINES, "Kent")
        assert result == ["Clark Kent | 2025-01-06 | 09:00 | 17:00"]

    def test_case_insensitive(self):
        result = filter_lines(self.LINES, "clark")
        assert result == ["Clark Kent | 2025-01-06 | 09:00 | 17:00"]

    def test_no_match_returns_empty(self):
        result = filter_lines(self.LINES, "Bruce Wayne")
        assert result == []

    def test_multi_word_any_word_matches(self):
        # "Lois" alone should match "Lois Lane"
        result = filter_lines(self.LINES, "Lois")
        assert result == ["Lois Lane | 2025-01-06 | 10:00 | 18:00"]

    def test_empty_lines(self):
        assert filter_lines([], "Clark Kent") == []
