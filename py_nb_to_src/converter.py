"""Functions for converting notebook files to source code files."""

import subprocess
from pathlib import Path

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
    ipynb_path = Path(ipynb_path)
    command = f"jupyter nbconvert --to script '{ipynb_path}' --output '{ipynb_path.stem}'"
    subprocess.run(
        command,
        shell=True,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # List all files and find the one that has the same stem but not the "ipynb" suffix
    for f in ipynb_path.parent.iterdir():
        if f.stem == ipynb_path.stem and f.suffix != ".ipynb":
            return f

    raise FileNotFoundError(f"Could not find converted script for {ipynb_path}")


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
    rmd_path = Path(rmd_path)
    output_r_path = rmd_path.with_suffix(".r")
    r_conversion_command = KNITR_RMD_TO_R_CONVERSION_COMMAND.format(
        input_path=str(rmd_path),
        output_path=str(output_r_path),
    )

    subprocess.run(
        ["R", "-e", r_conversion_command],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return output_r_path
