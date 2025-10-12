"""Basic tests for OOS setup validation."""

import pytest


def test_basic_functionality() -> None:
    """Test that basic Python functionality works."""
    assert 1 + 1 == 2


def test_import_oos() -> None:
    """Test that we can import the OOS package."""
    import sys
    from pathlib import Path

    # Add src to path for testing
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))

    import __init__ as src

    assert src.__version__ == "1.2.0"


@pytest.mark.asyncio
async def test_async_functionality() -> None:
    """Test async functionality works."""
    result = await async_add(1, 2)
    assert result == 3


async def async_add(a: int, b: int) -> int:
    """Simple async function for testing."""
    return a + b
