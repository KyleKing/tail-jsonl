"""Generate shell completion scripts from the argparse parser."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass

SHELLS = ('bash', 'zsh')
"""Shells with a completion generator."""

_FILE_SUFFIXES = ('_dir', '_file', '_path')


@dataclass(frozen=True)
class _Option:
    """One optional argument, reduced to what a completion script needs."""

    flags: tuple[str, ...]
    description: str
    choices: tuple[str, ...]
    metavar: str
    takes_value: bool
    repeatable: bool
    completes_files: bool
    exclusive: bool


def _read_option(action: argparse.Action) -> _Option:
    return _Option(
        flags=tuple(action.option_strings),
        description=re.sub(r'\s+', ' ', action.help or '').replace('%%', '%').strip(),
        choices=tuple(str(_) for _ in action.choices or ()),
        metavar=str(action.metavar or action.dest.upper()),
        takes_value=action.nargs != 0,
        repeatable=isinstance(action, argparse._AppendAction),  # noqa: SLF001
        completes_files=action.dest.endswith(_FILE_SUFFIXES),
        exclusive=isinstance(action, argparse._HelpAction | argparse._VersionAction),  # noqa: SLF001
    )


def _read_options(parser: argparse.ArgumentParser) -> list[_Option]:
    return [_read_option(_) for _ in parser._actions if _.option_strings]  # noqa: SLF001


def _slug(prog: str) -> str:
    return re.sub(r'\W', '_', prog)


def _bash_branch(option: _Option) -> list[str]:
    if option.choices:
        body = f"""COMPREPLY=($(compgen -W '{' '.join(option.choices)}' -- "${{cur}}"))"""
    elif option.completes_files:
        body = 'COMPREPLY=($(compgen -f -- "${cur}"))'
    else:
        body = 'COMPREPLY=()'
    return [
        f'        {"|".join(option.flags)})',
        f'            {body}',
        '            return 0',
        '            ;;',
    ]


def _bash(parser: argparse.ArgumentParser) -> str:
    options = _read_options(parser)
    func = f'_{_slug(parser.prog)}_completion'
    branches = [line for option in options if option.takes_value for line in _bash_branch(option)]
    flags = ' '.join(flag for option in options for flag in option.flags)
    lines = [
        f'# bash completion for {parser.prog}',
        f'{func}() {{',
        '    local cur prev',
        '    COMPREPLY=()',
        '    cur="${COMP_WORDS[COMP_CWORD]}"',
        '    prev="${COMP_WORDS[COMP_CWORD-1]}"',
        *(['    case "${prev}" in', *branches, '    esac'] if branches else []),
        f"""    COMPREPLY=($(compgen -W '{flags}' -- "${{cur}}"))""",
        '    return 0',
        '}',
        '',
        f'complete -F {func} {parser.prog}',
    ]
    return '\n'.join(lines) + '\n'


def _zsh_escape(text: str) -> str:
    for character in ('\\', '[', ']', ':'):
        text = text.replace(character, f'\\{character}')
    return text.replace("'", """'"'"'""")


def _zsh_value(option: _Option) -> str:
    if not option.takes_value:
        return ''
    if option.choices:
        return f':{_zsh_escape(option.metavar)}:({" ".join(option.choices)})'
    if option.completes_files:
        return f':{_zsh_escape(option.metavar)}:_files'
    return f':{_zsh_escape(option.metavar)}:'


def _zsh_spec(option: _Option) -> str:
    if option.exclusive:
        prefix = "'(- *)'"
    elif option.repeatable:
        prefix = "'*'"
    elif len(option.flags) > 1:
        prefix = f"'({' '.join(option.flags)})'"
    else:
        prefix = ''
    body = f'[{_zsh_escape(option.description)}]{_zsh_value(option)}'
    if len(option.flags) > 1:
        return f"{prefix}{{{','.join(option.flags)}}}'{body}'"
    return f"{prefix}'{option.flags[0]}{body}'"


def _zsh(parser: argparse.ArgumentParser) -> str:
    specs = [_zsh_spec(_) for _ in _read_options(parser)]
    func = f'_{_slug(parser.prog)}'
    lines = [
        f'#compdef {parser.prog}',
        '',
        f'{func}() {{',
        '    _arguments -s -S \\',
        *[f'        {spec} \\' for spec in specs[:-1]],
        f'        {specs[-1]}',
        '}',
        '',
        f'if [ "$funcstack[1]" = "{func}" ]; then',
        f'    {func} "$@"',
        'else',
        f'    compdef {func} {parser.prog}',
        'fi',
    ]
    return '\n'.join(lines) + '\n'


def generate(parser: argparse.ArgumentParser, shell: str) -> str:
    """Return the completion script for the given shell, derived from the parser's own options."""
    generators = {'bash': _bash, 'zsh': _zsh}
    try:
        return generators[shell](parser)
    except KeyError as err:
        expected = ', '.join(SHELLS)
        msg = f'Unsupported shell {shell!r}. Expected one of: {expected}'
        raise ValueError(msg) from err
