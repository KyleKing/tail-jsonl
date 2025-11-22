"""Tests for context buffer (Phase 7)."""

from __future__ import annotations

import pytest

from tail_jsonl._private.context import ContextBuffer


class TestContextBuffer:
    """Test the ContextBuffer class for before/after context management."""

    def test_no_context(self):
        """Test buffer with no before/after context configured."""
        buffer = ContextBuffer(before=0, after=0)

        # Non-matching line should not print
        before_lines, should_print = buffer.process_line('line1', is_match=False)
        assert before_lines == []
        assert should_print is False

        # Matching line should print
        before_lines, should_print = buffer.process_line('line2', is_match=True)
        assert before_lines == []
        assert should_print is True

    def test_before_context_only(self):
        """Test buffer with only before-context."""
        buffer = ContextBuffer(before=2, after=0)

        # First two lines don't match - stored in buffer
        before_lines, should_print = buffer.process_line('line1', is_match=False)
        assert before_lines == []
        assert should_print is False

        before_lines, should_print = buffer.process_line('line2', is_match=False)
        assert before_lines == []
        assert should_print is False

        # Third line matches - buffer is flushed
        before_lines, should_print = buffer.process_line('line3-match', is_match=True)
        assert before_lines == ['line1', 'line2']
        assert should_print is True

        # After match, buffer starts filling again
        before_lines, should_print = buffer.process_line('line4', is_match=False)
        assert before_lines == []
        assert should_print is False

    def test_after_context_only(self):
        """Test buffer with only after-context."""
        buffer = ContextBuffer(before=0, after=2)

        # Non-matching line doesn't print
        before_lines, should_print = buffer.process_line('line1', is_match=False)
        assert before_lines == []
        assert should_print is False

        # Matching line prints and sets after-counter
        before_lines, should_print = buffer.process_line('line2-match', is_match=True)
        assert before_lines == []
        assert should_print is True

        # Next 2 lines print as after-context
        before_lines, should_print = buffer.process_line('line3', is_match=False)
        assert before_lines == []
        assert should_print is True

        before_lines, should_print = buffer.process_line('line4', is_match=False)
        assert before_lines == []
        assert should_print is True

        # After counter exhausted, line doesn't print
        before_lines, should_print = buffer.process_line('line5', is_match=False)
        assert before_lines == []
        assert should_print is False

    def test_before_and_after_context(self):
        """Test buffer with both before and after context."""
        buffer = ContextBuffer(before=2, after=2)

        # Build before-buffer
        buffer.process_line('line1', is_match=False)
        buffer.process_line('line2', is_match=False)
        buffer.process_line('line3', is_match=False)

        # Match: flush before-buffer, print match, start after-counter
        before_lines, should_print = buffer.process_line('line4-match', is_match=True)
        assert before_lines == ['line2', 'line3']  # Only last 2 lines (maxlen=2)
        assert should_print is True

        # After-context lines
        before_lines, should_print = buffer.process_line('line5', is_match=False)
        assert before_lines == []
        assert should_print is True

        before_lines, should_print = buffer.process_line('line6', is_match=False)
        assert before_lines == []
        assert should_print is True

        # After counter exhausted
        before_lines, should_print = buffer.process_line('line7', is_match=False)
        assert before_lines == []
        assert should_print is False

    def test_consecutive_matches(self):
        """Test behavior with consecutive matching lines."""
        buffer = ContextBuffer(before=2, after=2)

        # Build buffer
        buffer.process_line('line1', is_match=False)
        buffer.process_line('line2', is_match=False)

        # First match
        before_lines, should_print = buffer.process_line('line3-match', is_match=True)
        assert before_lines == ['line1', 'line2']
        assert should_print is True

        # Second match immediately after - before-buffer should be empty
        before_lines, should_print = buffer.process_line('line4-match', is_match=True)
        assert before_lines == []
        assert should_print is True

    def test_match_during_after_context(self):
        """Test match occurring during after-context period."""
        buffer = ContextBuffer(before=2, after=2)

        # First match
        buffer.process_line('ctx1', is_match=False)
        buffer.process_line('ctx2', is_match=False)
        before_lines, should_print = buffer.process_line('match1', is_match=True)
        assert before_lines == ['ctx1', 'ctx2']
        assert should_print is True

        # During after-context, another match occurs
        before_lines, should_print = buffer.process_line('match2', is_match=True)
        assert before_lines == []  # Buffer was cleared by first match
        assert should_print is True  # Still in after-context, so prints

    def test_buffer_maxlen_enforcement(self):
        """Test that before-buffer respects maxlen."""
        buffer = ContextBuffer(before=2, after=0)

        # Add 5 non-matching lines
        for i in range(1, 6):
            buffer.process_line(f'line{i}', is_match=False)

        # Match should only get last 2 lines
        before_lines, should_print = buffer.process_line('match', is_match=True)
        assert before_lines == ['line4', 'line5']
        assert should_print is True

    def test_empty_before_buffer_on_match_without_history(self):
        """Test match with no prior lines."""
        buffer = ContextBuffer(before=2, after=0)

        # Match on first line - no before-context available
        before_lines, should_print = buffer.process_line('match', is_match=True)
        assert before_lines == []
        assert should_print is True

    @pytest.mark.parametrize(
        ('before', 'after', 'lines', 'expected_outputs'),
        [
            # No context: only matches print
            (
                0,
                0,
                [('a', False), ('b', True), ('c', False)],
                [([], False), ([], True), ([], False)],
            ),
            # Before=1: show 1 line before match
            (
                1,
                0,
                [('a', False), ('b', False), ('c', True)],
                [([], False), ([], False), (['b'], True)],  # Only last 1 line
            ),
            # After=1: show 1 line after match
            (
                0,
                1,
                [('a', True), ('b', False), ('c', False)],
                [([], True), ([], True), ([], False)],
            ),
            # Before=1, After=1
            (
                1,
                1,
                [('a', False), ('b', True), ('c', False), ('d', False)],
                [([], False), (['a'], True), ([], True), ([], False)],
            ),
        ],
    )
    def test_parameterized_scenarios(self, before, after, lines, expected_outputs):
        """Test various before/after scenarios with parameterized inputs."""
        buffer = ContextBuffer(before=before, after=after)

        for (line, is_match), (expected_before, expected_should_print) in zip(lines, expected_outputs):
            before_lines, should_print = buffer.process_line(line, is_match)
            assert before_lines == expected_before
            assert should_print == expected_should_print
