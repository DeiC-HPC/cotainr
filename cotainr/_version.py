"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk Licensed under the European Union Public License (EUPL)
1.2
 - see the LICENSE file for details.

This module implements dynamic version number computation for cotainr based on
git history (if in a git development environment) or the installed package
version (if used from an installed cotainr package). If neither is available,
the reported version is "<unknown version>".

Adapted from the hatch-vcs-footgun-example, see
<https://github.com/maresb/hatch-vcs-footgun-example/>.

Functions
---------
_determine_cotainr_version()
    Determine the version number for cotainr.
_get_cotainr_calver_tag_pattern()
    Load the cotainr calver tag pattern from pyproject.toml.
_get_hatch_version()
    Compute the version number in a development environment.
_get_importlib_metadata_version()
    Get the version number for an installed cotainr package.

Attributes
----------
__version__
    The cotainr version number.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _determine_cotainr_version():
    """
    Determine the version number for cotainr.

    If the git history is available, the hatch-vcs package is used to determine
    the version number based on the latest git release tag and any commits
    since then.
    If the git history is not available, the version number is
    extracted from package metadata.
    If neither is available, the version is reported as "<unknown version>".

    Returns
    -------
    cotainr_version : str
        The cotainr version number.
    """
    try:
        # Attempt to get the version number dynamically from the git history
        # using hatch-vcs.
        from hatchling.metadata.core import ProjectMetadata
        from hatchling.plugin.manager import PluginManager

        cotainr_root_path = Path(__file__).parents[1]
        metadata = ProjectMetadata(
            root=cotainr_root_path, plugin_manager=PluginManager()
        )
        cotainr_version = metadata.hatch.version.cached
        logger.debug("Cotainr version number determined by hatch: %s", cotainr_version)
    except Exception:
        # ImportError if hatchling is not installed.
        # Any Exception that metadata.hatch.version.cached may raise if it is
        # unable to determine the version number.
        logger.debug(
            "Unable to determine cotainr version number from hatch, falling back to importlib.metadata."
        )
        import importlib.metadata

        try:
            # Fallback to the version number from importlib.metadata
            cotainr_version = importlib.metadata.version(__package__)
            logger.debug(
                "Cotainr version number determined by importlib.metadata: %s",
                cotainr_version,
            )
        except importlib.metadata.PackageNotFoundError:
            # If none of the above work, give up and return "<unknown version>".
            cotainr_version = "<unknown version>"
            logger.debug(
                "Unable to determine cotainr version number from hatch or importlib."
            )

    return cotainr_version


def _get_cotainr_calver_tag_pattern():
    """
    Load the cotainr calver tag pattern from pyproject.toml.

    The hatch version tag pattern is the single source of truth for the regex
    defining the calver pattern for cotainr version numbers.

    Returns
    -------
    cotainr_calver_tag_pattern : str
        The cotainr calver tag pattern regex.
    """
    pyproject_toml_path = Path(__file__).resolve().parents[1] / "pyproject.toml"

    # The tomllib module is only available in Python 3.11 and later.
    # Until we only support Python 3.11 and later, we use this custom code to
    # read the pyproject.toml file. It attempts to do the same thing as:
    #   import tomllib
    #   cotainr_calver_tag_pattern = tomllib.loads(pyproject_toml_path.read_text())["tool"]["hatch"]["version"]["tag-pattern"]
    with open(pyproject_toml_path) as f:
        for line in f:
            if line.startswith("tag-pattern = "):
                # Split line on "=" and remove #comments, whitespace, and single quotes
                cotainr_calver_tag_pattern = (
                    line.split("=")[1].split("#")[0].strip().strip("'")
                )
                break
        else:
            raise RuntimeError(
                "Unable to find the cotainr calver tag pattern in pyproject.toml"
            )

    return cotainr_calver_tag_pattern


__version__ = _determine_cotainr_version()
