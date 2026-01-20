"""Functions for converting notebook files to source code files."""

import subprocess
import traceback
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from tqdm import tqdm


class ConverterType(Enum):
    """Enum for specifying which converters to use."""

    IPYNB = "ipynb"
    RMD = "rmd"
    BOTH = "both"


@dataclass
class DirectoryConversionResult:
    """Result of converting all notebook files in a directory.

    Attributes
    ----------
    converted : dict[Path, Path]
        Dictionary mapping successfully converted source file paths
        to their output script paths.
    failed : dict[Path, str]
        Dictionary mapping file paths that failed to convert
        to their error tracebacks.
    """

    converted: dict[Path, Path] = field(default_factory=dict)
    failed: dict[Path, str] = field(default_factory=dict)


KNITR_RMD_TO_R_CONVERSION_COMMAND = """
knitr::purl(input = "{input_path}", output = "{output_path}", documentation = 0)
""".strip()


def convert_ipynb(ipynb_path: Path | str) -> Path:
    """
    Convert a Jupyter notebook (.ipynb) to its source script.

    Uses `jupyter nbconvert` to convert the notebook. The output language
    depends on the kernel specified in the notebook (Python, R, Julia, etc.).

    Parameters
    ----------
    ipynb_path : Path | str
        Path to the .ipynb notebook file.

    Returns
    -------
    Path
        Path to the converted source script file.

    Raises
    ------
    FileNotFoundError
        If the converted script file cannot be found after conversion.
    subprocess.CalledProcessError
        If the jupyter nbconvert command fails.
    """
    ipynb_path = Path(ipynb_path).resolve()
    subprocess.run(
        [
            "jupyter",
            "nbconvert",
            "--to",
            "script",
            str(ipynb_path),
            "--output",
            ipynb_path.stem,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # List all files and find the one that has the same stem but not the "ipynb" suffix
    for f in ipynb_path.parent.iterdir():
        if f.stem == ipynb_path.stem and f.suffix != ".ipynb":
            return f

    raise FileNotFoundError(f"Could not find converted script for {ipynb_path}")


def _escape_r_string(path: str) -> str:
    """Escape a string for use in R code (handles backslashes and quotes)."""
    return path.replace("\\", "\\\\").replace('"', '\\"')


def convert_rmd(rmd_path: Path | str) -> Path:
    """
    Convert an R Markdown (.Rmd) file to an R script (.r).

    Uses knitr::purl to extract R code from the Rmd file.
    Requires R and the knitr package to be installed.

    Parameters
    ----------
    rmd_path : Path | str
        Path to the .Rmd file.

    Returns
    -------
    Path
        Path to the converted .r script file.

    Raises
    ------
    subprocess.CalledProcessError
        If the R command fails (e.g., R not installed, knitr not available).
    """
    rmd_path = Path(rmd_path).resolve()
    output_r_path = rmd_path.with_suffix(".r")
    r_conversion_command = KNITR_RMD_TO_R_CONVERSION_COMMAND.format(
        input_path=_escape_r_string(str(rmd_path)),
        output_path=_escape_r_string(str(output_r_path)),
    )

    subprocess.run(
        ["R", "-e", r_conversion_command],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return output_r_path


def _collect_files_to_convert(
    directory: Path,
    converter_type: ConverterType,
    recursive: bool = False,
) -> list[tuple[Path, str]]:
    """Collect all notebook files in a directory based on converter type."""
    files: list[tuple[Path, str]] = []
    ipynb_pattern = "**/*.ipynb" if recursive else "*.ipynb"
    rmd_pattern = "**/*.Rmd" if recursive else "*.Rmd"
    if converter_type in (ConverterType.IPYNB, ConverterType.BOTH):
        files.extend((f, "ipynb") for f in directory.glob(ipynb_pattern))
    if converter_type in (ConverterType.RMD, ConverterType.BOTH):
        files.extend((f, "rmd") for f in directory.glob(rmd_pattern))
    return files


def _convert_file(file_path: Path, file_type: str) -> Path:
    """Convert a single file based on its type."""
    if file_type == "ipynb":
        return convert_ipynb(file_path)
    return convert_rmd(file_path)


def convert_directory(
    directory: Path | str,
    converter_type: ConverterType = ConverterType.BOTH,
    recursive: bool = False,
    show_progress: bool = True,
    progress_leave: bool = True,
) -> DirectoryConversionResult:
    """
    Convert all notebook files in a directory to source scripts.

    Parameters
    ----------
    directory : Path | str
        Path to the directory containing notebook files.
    converter_type : ConverterType
        Which converters to use: IPYNB (only .ipynb files), RMD (only .Rmd files),
        or BOTH (default, converts all supported file types).
    recursive : bool
        Whether to recursively search subdirectories for notebook files
        (default False).
    show_progress : bool
        Whether to display a progress bar (default True).
    progress_leave : bool
        Whether to leave the progress bar visible after completion (default True).
        Set to False to remove the progress bar when done.

    Returns
    -------
    DirectoryConversionResult
        Dataclass containing successfully converted files and failed conversions
        with their tracebacks.

    Raises
    ------
    NotADirectoryError
        If the provided path is not a directory.
    """
    directory = Path(directory).resolve()
    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} is not a directory")

    files_to_convert = _collect_files_to_convert(directory, converter_type, recursive)
    result = DirectoryConversionResult()

    if not files_to_convert:
        return result

    progress_bar = tqdm(
        files_to_convert,
        desc="Converting notebooks",
        leave=progress_leave,
        disable=not show_progress,
    )

    for file_path, file_type in progress_bar:
        progress_bar.set_description(f"Converting {file_path.name}")
        try:
            result.converted[file_path] = _convert_file(file_path, file_type)
        except Exception:
            result.failed[file_path] = traceback.format_exc()

    return result
