"""Tests for the converter module."""

import shutil
import subprocess
from pathlib import Path

import pytest

from py_nb_to_src import ConverterType, convert_directory, convert_ipynb, convert_rmd

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def temp_python_notebook(tmp_path: Path) -> Path:
    """Copy the sample Python notebook to a temp directory."""
    src = FIXTURES_DIR / "sample_python.ipynb"
    dst = tmp_path / "sample_python.ipynb"
    shutil.copy(src, dst)
    return dst


@pytest.fixture
def temp_r_notebook(tmp_path: Path) -> Path:
    """Copy the sample R notebook to a temp directory."""
    src = FIXTURES_DIR / "sample_r.ipynb"
    dst = tmp_path / "sample_r.ipynb"
    shutil.copy(src, dst)
    return dst


@pytest.fixture
def temp_rmd_file(tmp_path: Path) -> Path:
    """Copy the sample Rmd file to a temp directory."""
    src = FIXTURES_DIR / "sample.Rmd"
    dst = tmp_path / "sample.Rmd"
    shutil.copy(src, dst)
    return dst


def is_jupyter_available() -> bool:
    """Check if jupyter nbconvert is available."""
    try:
        subprocess.run(
            ["jupyter", "nbconvert", "--version"],
            check=True,
            capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def is_r_available() -> bool:
    """Check if R and knitr are available."""
    try:
        subprocess.run(
            ["R", "-e", "library(knitr)"],
            check=True,
            capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


@pytest.mark.skipif(not is_jupyter_available(), reason="jupyter not available")
def test_convert_ipynb_python(temp_python_notebook: Path) -> None:
    """Test converting a Python notebook."""
    result = convert_ipynb(temp_python_notebook)

    assert result.exists()
    assert result.suffix == ".py"
    assert result.stem == "sample_python"

    content = result.read_text()
    assert "import os" in content
    assert "import sys" in content
    assert "from pathlib import Path" in content
    assert "x = 1 + 1" in content
    assert "def hello():" in content


@pytest.mark.skipif(not is_jupyter_available(), reason="jupyter not available")
def test_convert_ipynb_with_str_path(temp_python_notebook: Path) -> None:
    """Test converting a notebook using a string path."""
    result = convert_ipynb(str(temp_python_notebook))

    assert result.exists()
    assert result.suffix == ".py"


@pytest.mark.skipif(not is_jupyter_available(), reason="jupyter not available")
def test_convert_ipynb_file_not_found(tmp_path: Path) -> None:
    """Test that converting a non-existent file raises an error."""
    with pytest.raises(subprocess.CalledProcessError):
        convert_ipynb(tmp_path / "nonexistent.ipynb")


@pytest.mark.skipif(not is_r_available(), reason="R/knitr not available")
def test_convert_rmd(temp_rmd_file: Path) -> None:
    """Test converting an Rmd file."""
    result = convert_rmd(temp_rmd_file)

    assert result.exists()
    assert result.suffix == ".r"
    assert result.stem == "sample"

    content = result.read_text()
    assert "library(stats)" in content
    assert "library(utils)" in content
    assert "x <- 1 + 1" in content
    assert "hello <- function()" in content


@pytest.mark.skipif(not is_r_available(), reason="R/knitr not available")
def test_convert_rmd_with_str_path(temp_rmd_file: Path) -> None:
    """Test converting an Rmd file using a string path."""
    result = convert_rmd(str(temp_rmd_file))

    assert result.exists()
    assert result.suffix == ".r"


@pytest.mark.skipif(not is_r_available(), reason="R/knitr not available")
def test_convert_rmd_file_not_found(tmp_path: Path) -> None:
    """Test that converting a non-existent Rmd file raises an error."""
    with pytest.raises(subprocess.CalledProcessError):
        convert_rmd(tmp_path / "nonexistent.Rmd")


@pytest.fixture
def temp_directory_with_notebooks(tmp_path: Path) -> Path:
    """Create a temp directory with both notebook types."""
    shutil.copy(FIXTURES_DIR / "sample_python.ipynb", tmp_path / "sample_python.ipynb")
    shutil.copy(FIXTURES_DIR / "sample.Rmd", tmp_path / "sample.Rmd")
    return tmp_path


@pytest.mark.skipif(
    not is_jupyter_available() or not is_r_available(),
    reason="jupyter and R/knitr required",
)
def test_convert_directory_both(temp_directory_with_notebooks: Path) -> None:
    """Test converting a directory with both converter types."""
    results = convert_directory(temp_directory_with_notebooks, ConverterType.BOTH)

    assert len(results) == 2
    for original, converted in results.items():
        assert original.exists()
        assert converted.exists()


@pytest.mark.skipif(not is_jupyter_available(), reason="jupyter not available")
def test_convert_directory_ipynb_only(temp_directory_with_notebooks: Path) -> None:
    """Test converting only ipynb files in a directory."""
    results = convert_directory(temp_directory_with_notebooks, ConverterType.IPYNB)

    assert len(results) == 1
    original = next(iter(results.keys()))
    assert original.suffix == ".ipynb"


@pytest.mark.skipif(not is_r_available(), reason="R/knitr not available")
def test_convert_directory_rmd_only(temp_directory_with_notebooks: Path) -> None:
    """Test converting only Rmd files in a directory."""
    results = convert_directory(temp_directory_with_notebooks, ConverterType.RMD)

    assert len(results) == 1
    original = next(iter(results.keys()))
    assert original.suffix == ".Rmd"


def test_convert_directory_not_a_directory(tmp_path: Path) -> None:
    """Test that converting a non-directory raises an error."""
    file_path = tmp_path / "not_a_dir.txt"
    file_path.write_text("test")
    with pytest.raises(NotADirectoryError):
        convert_directory(file_path)


def test_convert_directory_empty(tmp_path: Path) -> None:
    """Test converting an empty directory returns empty dict."""
    results = convert_directory(tmp_path)
    assert results == {}
