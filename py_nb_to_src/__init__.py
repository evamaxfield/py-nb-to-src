"""Top-level package for py_nb_to_src."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("py-nb-to-src")
except PackageNotFoundError:
    __version__ = "uninstalled"

__author__ = "Eva Maxfield Brown"
__email__ = "evamxb@uw.edu"
