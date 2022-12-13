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

project = cotainr.__name__
author = "DeiC"
copyright = f"2022-{time.strftime('%Y')}, {author}"
version = cotainr.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
# https://numpydoc.readthedocs.io/en/latest/install.html#configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.duration",
    "sphinx.ext.intersphinx",
    "sphinx_design",
    "numpydoc",
    "myst_parser",
]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
numpydoc_class_members_toctree = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["css/cotainr.css"]
html_title = project
html_context = {
    "github_user": "DeiC-HPC",
    "github_repo": project,
    "github_version": "main",
    "doc_path": "doc",
}
html_theme_options = {
    "github_url": f"https://github.com/{html_context['github_user']}/{html_context['github_repo']}",
    "use_edit_page_button": True,
}

# -- Autodoc configuration ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration


def add_api_headline_to_module_docs(app, what, name, obj, options, lines):
    """
    Event for adding a 'API reference' headline before showing API content in
    auto modules.
    """
    if what == "module":
        lines.append("\n")
        lines.append("API reference")
        lines.append("-------------")


def setup(app):
    app.connect("autodoc-process-docstring", add_api_headline_to_module_docs)