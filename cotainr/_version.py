"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
 - see the LICENSE file for details.

This module implements dynamic version number computation for cotainr based on
git history (if in a git development environment) or the installed package
version (if used from an installed cotainr package).

Adapted from the hatch-vcs-footgun-example, see
<https://github.com/maresb/hatch-vcs-footgun-example/>.

Functions
---------
_get_hatch_version()
    Compute the version number in a development environment.
_get_importlib_metadata_version()
    Get the version number using importlib.metadata
"""

from pathlib import Path


def _get_hatch_version():
    """Compute the version number in a development environment.

    Returns
    -------
    str or None
        The version number or `None` if Hatchling is not installed.

    """

    try:
        from hatchling.metadata.core import ProjectMetadata
        from hatchling.plugin.manager import PluginManager
    except ImportError:
        return None

    cotainr_root_path = Path(__file__).parents[1]
    metadata = ProjectMetadata(root=cotainr_root_path, plugin_manager=PluginManager())
    return metadata.hatch.version.cached


def _get_importlib_metadata_version():
    """Get the version number using importlib.metadata

    Returns
    -------
    str or None
        The version number or `None` if not used from an installed package.

    """
    from importlib.metadata import version, PackageNotFoundError

    try:
        package_version = version(__package__)
        return package_version
    except PackageNotFoundError:
        return None


# The cotainr version based on git history or the installed package version. If
# neither is available, the reported version is "<unknown version>".
__version__ = (
    _get_hatch_version() or _get_importlib_metadata_version() or "<unknown version>"
)

