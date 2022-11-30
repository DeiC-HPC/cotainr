# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from pathlib import Path
import sys
import time

sys.path.insert(0, f'{Path("..").resolve()}')

import cotainr

project = "cotainr"
copyright = f"2022-{time.strftime('%Y')}, DeiC"
author = "DeiC"
version = cotainr.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
# https://numpydoc.readthedocs.io/en/latest/install.html#configuration

extensions = ["sphinx.ext.autodoc", "sphinx_design", "numpydoc"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
numpydoc_class_members_toctree = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_theme_options = {
    "secondary_sidebar_items": ["page-toc", "edit-this-page"],
    "github_url": "https://github.com/DeiC-HPC/cotainr",
}

# -- Autodoc configuration ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration


def add_api_headline_to_module_docs(app, what, name, obj, options, lines):
    """
    Event for adding a 'API reference' headline before showing API content in
    auto modules.
    """
    if what == "module":
        lines.append("API reference")
        lines.append("-------------")


def setup(app):
    app.connect("autodoc-process-docstring", add_api_headline_to_module_docs)
