"""Shell completion generation for tail-jsonl (Phase 8)."""

from __future__ import annotations


def generate_completion(shell: str) -> str:
    """Generate shell completion script.

    Args:
        shell: Shell type ('bash' or 'zsh')

    Returns:
        Completion script as string

    Raises:
        ValueError: If shell type is not supported
    """
    if shell == 'bash':
        return _generate_bash_completion()
    if shell == 'zsh':
        return _generate_zsh_completion()
    raise ValueError(f'Unsupported shell: {shell}')


def _generate_bash_completion() -> str:
    """Generate bash completion script."""
    return '''# Bash completion for tail-jsonl
# Source this file or add to ~/.bashrc:
#   source <(tail-jsonl --completion bash)

_tail_jsonl_completions() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    opts="--version --config-path --debug --include --exclude --field-selector \\
--case-insensitive --theme --theme-path --list-themes --completion -h --help \\
-i -e -v"

    case "${prev}" in
        --theme)
            COMPREPLY=( $(compgen -W "dark none catppuccin-light" -- ${cur}) )
            return 0
            ;;
        --theme-path|--config-path)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --completion)
            COMPREPLY=( $(compgen -W "bash zsh" -- ${cur}) )
            return 0
            ;;
        --include|-i|--exclude|-e|--field-selector)
            # No completion for patterns
            return 0
            ;;
        *)
            ;;
    esac

    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}

complete -F _tail_jsonl_completions tail-jsonl
'''


def _generate_zsh_completion() -> str:
    """Generate zsh completion script."""
    return '''#compdef tail-jsonl
# Zsh completion for tail-jsonl
# Add to fpath or save as _tail-jsonl:
#   tail-jsonl --completion zsh > ~/.zsh/completions/_tail-jsonl
# Then add to ~/.zshrc:
#   fpath=(~/.zsh/completions $fpath)
#   autoload -Uz compinit && compinit

_tail_jsonl() {
    local -a args

    args=(
        '(- :)'{-h,--help}'[Show help message]'
        '(- :)'{-v,--version}'[Show version]'
        '(- :)--list-themes[List available themes]'
        '(- :)--completion[Generate completion script]:shell:(bash zsh)'
        '--config-path[Path to configuration file]:file:_files'
        '--debug[Enable debug mode]'
        '(-i --include)'{-i,--include}'[Include pattern (allowlist)]:pattern:'
        '(-e --exclude)'{-e,--exclude}'[Exclude pattern (blocklist)]:pattern:'
        '--field-selector[Filter by field]:selector:'
        '--case-insensitive[Case-insensitive matching]'
        '--theme[Color theme]:theme:(dark none catppuccin-light)'
        '--theme-path[Custom theme file]:file:_files -g "*.toml"'
    )

    _arguments -s $args
}

_tail_jsonl "$@"
'''
