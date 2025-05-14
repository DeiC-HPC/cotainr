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

from pathlib import Path


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
            if line.startswith("tag-pattern"):
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


def _get_hatch_version(fp: str = __file__) -> str | None:
    """
    Compute the version number in a development environment.

    Uses the hatchling package functionality to determine the version number.

    Parameters
    ----------
    fp : str
        The path to the _version.py file.

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

    file_path = Path(fp)
    if file_path.parent.stem != "site-packages":
        cotainr_root_path = file_path.parents[1]
    else:
        return None
    metadata = ProjectMetadata(root=cotainr_root_path, plugin_manager=PluginManager())

    try:
        vcs_version = metadata.hatch.version.cached
    except Exception:
        # If "cached" doesn't exist or raises an exception, give up and return None.
        return None

    assert isinstance(vcs_version, str)
    return vcs_version


def _get_importlib_metadata_version() -> str | None:
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

    assert isinstance(package_version, str)
    return package_version


# Priority queue: First hatch version, then import lib or else the default value
__version__ = (
    _get_hatch_version() or _get_importlib_metadata_version() or "unknown version"
)
