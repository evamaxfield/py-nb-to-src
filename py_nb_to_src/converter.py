"""Functions for converting notebook files to source code files."""

import subprocess
from enum import Enum
from pathlib import Path


class ConverterType(Enum):
    """Enum for specifying which converters to use."""

    IPYNB = "ipynb"
    RMD = "rmd"
    BOTH = "both"


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


def convert_directory(
    directory: Path | str,
    converter_type: ConverterType = ConverterType.BOTH,
) -> dict[Path, Path]:
    """
    Convert all notebook files in a directory to source scripts.

    Parameters
    ----------
    directory : Path | str
        Path to the directory containing notebook files.
    converter_type : ConverterType
        Which converters to use: IPYNB (only .ipynb files), RMD (only .Rmd files),
        or BOTH (default, converts all supported file types).

    Returns
    -------
    dict[Path, Path]
        Dictionary mapping original file paths to converted script paths.

    Raises
    ------
    NotADirectoryError
        If the provided path is not a directory.
    """
    directory = Path(directory).resolve()
    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} is not a directory")

    results: dict[Path, Path] = {}

    if converter_type in (ConverterType.IPYNB, ConverterType.BOTH):
        for ipynb_file in directory.glob("*.ipynb"):
            results[ipynb_file] = convert_ipynb(ipynb_file)

    if converter_type in (ConverterType.RMD, ConverterType.BOTH):
        for rmd_file in directory.glob("*.Rmd"):
            results[rmd_file] = convert_rmd(rmd_file)

    return results
