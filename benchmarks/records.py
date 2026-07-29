"""Synthetic JSONL records shared by the benchmark suite and the throughput script."""

from __future__ import annotations

import io
import json
from typing import Any

from rich.console import Console

CONSOLE_WIDTH = 120
"""Fixed width so rendering cost does not vary with the terminal running the benchmark."""


def make_console(buffer: io.StringIO) -> Console:
    """Return a Console that renders to the given throwaway buffer instead of a terminal."""
    return Console(file=buffer, width=CONSOLE_WIDTH, force_terminal=True, color_system='truecolor')


def simple_record(index: int = 0) -> dict[str, Any]:
    """Return a minimal record: timestamp, level, message, and two extra keys."""
    return {
        'duration_ms': 12.5 + index,
        'level': 'info',
        'message': 'handled request',
        'status': 200,
        'timestamp': '2025-09-10T15:31:37.651Z',
    }


def wide_record(index: int = 0) -> dict[str, Any]:
    """Return a 20+ key record with nested objects and a dotted `error.stack` promotion."""
    return {
        'attempt': index % 3,
        'cache': {'hit': index % 2 == 0, 'key': f'comments:{index}', 'ttl_s': 300},
        'category': ['app', 'http'],
        'client': {'ip': '10.0.0.42', 'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'},
        'duration_ms': 128.4 + index,
        'environment': 'staging',
        'error': {
            'message': 'Invalid for loop',
            'name': 'SourceError',
            'stack': (
                'SourceError: Invalid for loop\n'
                '    at forTag (https://deno.land/x/vento@v2.0.1/plugins/for.ts:74:11)\n'
                '    at tokenize (https://deno.land/x/vento@v2.0.1/src/tokenizer.ts:31:5)'
            ),
        },
        'host': 'localhost:8080',
        'level': 'error',
        'message': 'Failed to load comments',
        'method': 'GET',
        'path': '/partials/comments',
        'referer': 'http://localhost:8080/comments',
        'region': 'us-east-1',
        'request': {'headers': {'accept': 'text/html'}, 'method': 'GET', 'path': '/partials/comments'},
        'requestId': '4c58cd34-f521-4af1-8c6d-e61914216710',
        'retryable': False,
        'service': 'comments-api',
        'span_id': f'{index:016x}',
        'status': 500,
        'timestamp': '2025-09-10T15:31:37.651Z',
        'trace_id': f'{index:032x}',
        'upstream': {'latency_ms': 91.2, 'name': 'postgres', 'pool': {'idle': 4, 'size': 10}},
        'url': 'http://localhost:8080/partials/comments',
        'user': {'id': 4821, 'roles': ['admin', 'reader']},
        'version': '1.4.2',
    }


def simple_line(index: int = 0) -> str:
    """Return the serialized form of `simple_record`."""
    return json.dumps(simple_record(index))


def wide_line(index: int = 0) -> str:
    """Return the serialized form of `wide_record`."""
    return json.dumps(wide_record(index))
