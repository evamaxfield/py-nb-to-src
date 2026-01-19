"""Top-level package for py_nb_to_src."""

from importlib.metadata import PackageNotFoundError, version

from .converter import (
    ConverterType,
    DirectoryConversionResult,
    convert_directory,
    convert_ipynb,
    convert_rmd,
)

try:
    __version__ = version("py-nb-to-src")
except PackageNotFoundError:
    __version__ = "uninstalled"

__author__ = "Eva Maxfield Brown"
__email__ = "evamxb@uw.edu"

__all__ = [
    "ConverterType",
    "DirectoryConversionResult",
    "__author__",
    "__email__",
    "__version__",
    "convert_directory",
    "convert_ipynb",
    "convert_rmd",
]
