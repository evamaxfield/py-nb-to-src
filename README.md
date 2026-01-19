# py-nb-to-src

Convert Jupyter Notebooks (of all languages) and Rmd to their non-notebook counterparts.

## Installation

```bash
pip install py-nb-to-src
```

### Additional Requirements

**For R Markdown (.Rmd) conversion:**
- R must be installed and available on your PATH
- The `knitr` R package must be installed

The easiest way to install all dependencies is via micromamba/conda:

```bash
# Install R and knitr in one command
micromamba install -c conda-forge r-base r-knitr
```

**After installing R, install knitr:**
```bash
R -e "install.packages('knitr', repos='https://cloud.r-project.org')"
```

## Usage

### Converting Jupyter Notebooks

Convert any Jupyter notebook (.ipynb) to its source script. The output format depends on the kernel specified in the notebook (Python, R, Julia, etc.).

```python
from py_nb_to_src import convert_ipynb

# Convert a Python notebook
output_path = convert_ipynb("analysis.ipynb")
# Returns: Path to analysis.py

# Convert an R notebook
output_path = convert_ipynb("analysis_r.ipynb")
# Returns: Path to analysis_r.r
```

### Converting R Markdown Files

Convert R Markdown (.Rmd) files to R scripts (.r) using knitr.

```python
from py_nb_to_src import convert_rmd

# Convert an Rmd file
output_path = convert_rmd("report.Rmd")
# Returns: Path to report.r
```