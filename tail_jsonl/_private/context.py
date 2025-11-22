"""Context lines management (Phase 7)."""

from __future__ import annotations

from collections import deque


class ContextBuffer:
    """Buffer for managing context lines (before/after match display)."""

    def __init__(self, before: int = 0, after: int = 0) -> None:
        """Initialize context buffer."""
        self.before_count = before
        self.after_count = after
        self.before_buffer: deque[str] = deque(maxlen=before if before > 0 else None)
        self.after_counter = 0

    def process_line(self, line: str, is_match: bool) -> tuple[list[str], bool]:
        """Process line and return (before_context_lines, should_print_current)."""
        lines_to_print: list[str] = []

        if is_match:
            if self.before_buffer:
                lines_to_print.extend(list(self.before_buffer))
                self.before_buffer.clear()
            self.after_counter = self.after_count
            return (lines_to_print, True)

        if self.after_counter > 0:
            self.after_counter -= 1
            return (lines_to_print, True)

        if self.before_count > 0:
            self.before_buffer.append(line)

        return (lines_to_print, False)
