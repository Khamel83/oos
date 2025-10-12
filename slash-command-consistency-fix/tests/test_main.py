"""Tests for main module."""

from slash-command-consistency-fix.main import hello_world


def test_hello_world():
    """Test hello_world function."""
    result = hello_world()
    assert "Hello from slash-command-consistency-fix" in result
    assert isinstance(result, str)
