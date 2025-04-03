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
    cotainr_version = (
        _get_hatch_version() or _get_importlib_metadata_version() or "<unknown version>"
    )

    return cotainr_version


def _get_hatch_version():
    """
    Compute the version number in a development environment.

    Uses the hatchling package functionality to determine the version number.

    Returns
    -------
    str or None
        The version number or `None` if hatchling is unable to determine the
        version number.
    """
    try:
        from hatchling.metadata.core import ProjectMetadata
        from hatchling.plugin.manager import PluginManager
    except ImportError:
        return None

    cotainr_root_path = Path(__file__).parents[1]
    metadata = ProjectMetadata(root=cotainr_root_path, plugin_manager=PluginManager())

    try:
        vcs_version = metadata.hatch.version.cached
    except Exception:
        # If "cached" doesn't exist or raises an exception, give up and return None.
        return None

    return vcs_version


def _get_importlib_metadata_version():
    """
    Get the version number for an installed cotainr package.

    Uses standard importlib.metadata functions to get the version number for an
    installed package.

    Returns
    -------
    str or None
        The version number or `None` if not used from an installed package.

    """
    from importlib.metadata import PackageNotFoundError, version

    try:
        package_version = version(__package__)
    except PackageNotFoundError:
        return None

    return package_version


__version__ = _determine_cotainr_version()
