import os
import re
import shutil
import subprocess  # noqa: S404
import sys

import pytest

from tail_jsonl._private.completions import SHELLS, generate
from tail_jsonl.scripts import _parser


def _option_strings(parser):
    return [flag for action in parser._actions for flag in action.option_strings]  # noqa: SLF001


def _contains_token(text, token):
    return bool(re.search(rf'(?<![-\w]){re.escape(token)}(?![-\w])', text))


@pytest.mark.parametrize('shell', SHELLS)
def test_generate_includes_every_option_string(shell):
    parser = _parser()

    result = generate(parser, shell)

    assert [_ for _ in _option_strings(parser) if not _contains_token(result, _)] == []


@pytest.mark.parametrize('shell', SHELLS)
def test_generate_reflects_a_flag_added_to_the_parser(shell):
    parser = _parser()
    parser.add_argument('--not-yet-real', choices=('alpha', 'beta'), help='Added after the parser was built')

    result = generate(parser, shell)

    assert _contains_token(result, '--not-yet-real')
    assert _contains_token(result, 'alpha')
    assert _contains_token(result, 'beta')


@pytest.mark.parametrize('shell', SHELLS)
def test_generate_includes_choices(shell):
    result = generate(_parser(), shell)

    assert all(_contains_token(result, _) for _ in ('critical', 'debug', 'error', 'info', 'warning'))


def test_zsh_describes_arguments_with_metavars_and_help():
    result = generate(_parser(), 'zsh')

    assert ':KEY=PATTERN:' in result
    assert '[Path to a configuration file]:CONFIG_PATH:_files' in result


def test_generate_rejects_an_unknown_shell():
    with pytest.raises(ValueError, match=r"Unsupported shell 'fish'"):
        generate(_parser(), 'fish')


@pytest.mark.parametrize('shell', SHELLS)
def test_generated_script_parses_in_the_real_shell(shell, tmp_path):
    executable = shutil.which(shell)
    if not executable:
        pytest.skip(f'{shell} is not installed')
    script = tmp_path / f'completion.{shell}'
    script.write_text(generate(_parser(), shell), encoding='utf-8')

    result = subprocess.run([executable, '-n', str(script)], capture_output=True, text=True, check=False)  # noqa: S603

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize('shell', SHELLS)
def test_completions_exit_without_reading_stdin(shell):
    """The parent holds the write end open, so a read from stdin would block until the timeout."""
    read_fd, write_fd = os.pipe()
    try:
        proc = subprocess.Popen(  # noqa: S603
            [sys.executable, '-c', 'from tail_jsonl.scripts import start; start()', '--completions', shell],
            stdin=read_fd, stdout=subprocess.PIPE, text=True,
        )
        os.close(read_fd)
        try:
            stdout, _ = proc.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            pytest.fail(f'--completions {shell} blocked on stdin')
    finally:
        os.close(write_fd)

    assert proc.returncode == 0
    assert stdout == generate(_parser(), shell)
