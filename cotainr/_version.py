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
_get_hatch_version()
    Compute the version number in a development environment.
_get_importlib_metadata_version()
    Get the version number for an installed cotainr package.
"""

from pathlib import Path


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
    from importlib.metadata import version, PackageNotFoundError

    try:
        package_version = version(__package__)
    except PackageNotFoundError:
        return None

    return package_version


# The cotainr version based on git history or the installed package version. If
# neither is available, the reported version is "<unknown version>".
__version__ = (
    _get_hatch_version() or _get_importlib_metadata_version() or "<unknown version>"
)
