"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, f"{Path('..').resolve()}")

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
templates_path = ["_templates"]
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
numpydoc_class_members_toctree = False

# -- Options for linkcheck ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-the-linkcheck-builder
linkcheck_retries = 3  # Retry 3 times before considering a link broken
linkcheck_workers = 1  # Limit the number of workers to avoid hitting rate limits
linkcheck_ignore = [
    # It is easy to hit the rate limit of stackoverflow
    # Let's assume that stackoverflows does not move its supposedly permanent links
    "https://stackoverflow.com",
    # Its also easy to hit the rate limit of github
    # We do have quite a lot of links to our own github repo
    # For now, let's avoid checking these
    "https://github.com/DeiC-HPC/cotainr",
]
linkcheck_anchors_ignore_for_url = [
    # Ignore GitHub issue comment anchors that apparently fails
    "https://github.com/apptainer/singularity/issues/5941"
]
if "GITHUB_TOKEN" in os.environ:
    # Authenticate with GitHub token in GitHub Actions to avoid hitting rate limits
    # It is not entirely clear if this has any effect outside of api.github.com, though...
    linkcheck_request_headers = {
        "https://github.com": {"Authorization": f"token {os.environ['GITHUB_TOKEN']}"}
    }

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

rtd_version = os.environ.get("READTHEDOCS_VERSION")
if not rtd_version or rtd_version.isdigit():
    # Either not on readthedocs or it is a pull request number
    switcher_version = "latest"
    switcher_json = "_static/switcher.json"
else:
    switcher_version = rtd_version
    switcher_json = "https://cotainr.readthedocs.io/en/latest/_static/switcher.json"

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
    "use_edit_page_button": True,
    "navbar_start": ["navbar-logo", "version-switcher"],
    "footer_start": ["cotainr_footer"],
    "switcher": {
        "json_url": switcher_json,
        "version_match": switcher_version,
    },
    "icon_links": [
        {
            "name": "GitHub",
            "url": f"https://github.com/{html_context['github_user']}/{html_context['github_repo']}",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
        {
            "name": "PyPI",
            "url": f"https://pypi.org/project/{project}/",
            "icon": "fa-brands fa-python",
            "type": "fontawesome",
        },
    ],
    # We only set "navigation_with_keys = False" to explicitly remove the
    # warning introduced in pydata-sphinx-theme v0.14.2:
    # "WARNING: The default value for `navigation_with_keys` will change to
    # `False` in the next release. If you wish to preserve the old behavior for
    # your site, set `navigation_with_keys=True` in the `html_theme_options`
    # dict in your `conf.py` file.Be aware that `navigation_with_keys = True`
    # has negative accessibility
    # implications:https://github.com/pydata/pydata-sphinx-theme/issues/1492"
    "navigation_with_keys": False,
}

# -- Autodoc configuration ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration


def add_api_headline_to_module_docs(app, what, name, obj, options, lines):
    """Add an 'API reference' headline before showing API content in auto modules."""
    if what == "module":
        lines.append("\n")
        lines.append("API reference")
        lines.append("-------------")


def setup(app):  # noqa: D103
    app.connect("autodoc-process-docstring", add_api_headline_to_module_docs)
