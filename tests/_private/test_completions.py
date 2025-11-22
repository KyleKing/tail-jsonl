"""Tests for shell completions (Phase 8)."""

from __future__ import annotations

import pytest

from tail_jsonl._private.completions import generate_completion


class TestGenerateCompletion:
    """Test completion script generation."""

    def test_generate_bash_completion(self):
        """Test generating bash completion script."""
        script = generate_completion('bash')

        assert isinstance(script, str)
        assert len(script) > 0
        assert '_tail_jsonl_completions' in script
        assert 'complete -F' in script
        assert 'tail-jsonl' in script

    def test_generate_zsh_completion(self):
        """Test generating zsh completion script."""
        script = generate_completion('zsh')

        assert isinstance(script, str)
        assert len(script) > 0
        assert '#compdef tail-jsonl' in script
        assert '_tail_jsonl' in script

    def test_generate_unsupported_shell(self):
        """Test generating completion for unsupported shell raises error."""
        with pytest.raises(ValueError, match='Unsupported shell'):
            generate_completion('fish')

        with pytest.raises(ValueError, match='Unsupported shell'):
            generate_completion('powershell')


class TestBashCompletionContent:
    """Test bash completion script content."""

    def test_bash_has_theme_completion(self):
        """Test bash script completes theme names."""
        script = generate_completion('bash')

        assert 'dark' in script
        assert 'none' in script
        assert 'catppuccin-light' in script

    def test_bash_has_shell_completion(self):
        """Test bash script completes shell names."""
        script = generate_completion('bash')

        assert 'bash' in script
        assert 'zsh' in script

    def test_bash_has_all_flags(self):
        """Test bash script includes all major flags."""
        script = generate_completion('bash')

        assert '--theme' in script
        assert '--completion' in script
        assert '--include' in script
        assert '--exclude' in script
        assert '--config-path' in script


class TestZshCompletionContent:
    """Test zsh completion script content."""

    def test_zsh_has_theme_completion(self):
        """Test zsh script completes theme names."""
        script = generate_completion('zsh')

        assert 'dark' in script
        assert 'none' in script
        assert 'catppuccin-light' in script

    def test_zsh_has_shell_completion(self):
        """Test zsh script completes shell names."""
        script = generate_completion('zsh')

        assert 'bash' in script
        assert 'zsh' in script

    def test_zsh_has_all_flags(self):
        """Test zsh script includes all major flags."""
        script = generate_completion('zsh')

        assert '--theme' in script
        assert '--completion' in script
        assert '--include' in script
        assert '--exclude' in script
        assert '--config-path' in script
