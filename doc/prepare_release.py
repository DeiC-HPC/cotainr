"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk Licensed under the European Union Public License (EUPL)
1.2 - see the LICENSE file for details.

This script is used to prepare the release notes and version switcher for the
documentation for a new release of cotainr. It automatically generates the
version switcher for the documentation and creates a skeleton for the release
notes. The script should be run before making a tag for the latest version.
More information about releasing can be found here:
https://cotainr.readthedocs.io/en/latest/development/releasing.html

"""

import argparse
import datetime
import json
import locale
from pathlib import Path
import re
import subprocess
import sys
from typing import Optional

sys.path.insert(0, f"{(Path(__file__) / '../..').resolve()}")

import cotainr

COTAINR_RELEASE_VERSION_FORMAT_RE = r"^20[0-9]{2}\.([1-9]|10|11|12)\.(0|[1-9][0-9]*)$"  # cotainr YYYY.MM.MICRO version format
COTAINR_WRONG_PRACTICE_VERSION_FORMAT_RE = r"^20[0-9]{2}\.(0[1-9]|10|11|12)\.(0|[1-9][0-9]*)$"  # wrong YYYY.0M.MICRO version format


def create_docs_switcher(*, formatted_release_version: str):
    """
    Create the version switcher for the documentation.

    Automatically create the version switcher configuration for the PyData
    Sphinx Theme. The switcher will contain the latest 4 releases. See
    https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/version-dropdown.html#add-a-json-file-to-define-your-switcher-s-versions
    for more technical details.

    Parameters
    ----------
    formatted_release_version : str
        The YYYY.MM.MICRO version tag for the new release.
    """
    assert re.match(COTAINR_RELEASE_VERSION_FORMAT_RE, formatted_release_version)

    # Create base switcher with the latest and stable versions
    switcher = [
        {
            "name": "dev",
            "version": "latest",
            "url": "https://cotainr.readthedocs.io/en/latest/",
        },
        {
            "name": f"{formatted_release_version} (stable)",
            "version": "stable",
            "url": "https://cotainr.readthedocs.io/en/stable/",
        },
    ]

    # Append the latest 3 releases to the switcher based on git tags that match
    # the cotainr version format (or the wrong practice format)
    tags = [
        tag
        for tag in (
            subprocess.run(
                ["git", "--no-pager", "tag"], capture_output=True, text=True
            ).stdout.splitlines()
        )
        if (
            re.match(COTAINR_RELEASE_VERSION_FORMAT_RE, tag)
            or re.match(COTAINR_WRONG_PRACTICE_VERSION_FORMAT_RE, tag)
        )
    ]
    tags.reverse()
    for tag in tags[0:3]:
        switcher.append(
            {
                "name": tag,
                "version": tag,
                "url": f"https://cotainr.readthedocs.io/en/{tag}/",
            }
        )

    # Write the switcher to a static JSON file
    version_switcher_file = (Path(__file__) / "../_static/switcher.json").resolve()
    version_switcher_file.write_text(json.dumps(switcher, indent="  "))
    print(
        f"Version switcher written to {version_switcher_file}. "
        "Please check its contents and commit it."
    )


def create_release_notes(
    *, formatted_release_version: str, formatted_release_date: str
):
    """
    Create the release notes for the new version.

    Automatically create the skeleton for the release notes for the new
    version. Fills in the version number in the release note template.

    Parameters
    ----------
    formatted_release_version : str
        The YYYY.MM.MICRO version tag for the new release.
    formatted_release_date : str
        The release date formatted as "__Month__ __day__, __year__".
    """
    assert re.match(COTAINR_RELEASE_VERSION_FORMAT_RE, formatted_release_version)

    release_notes = (
        (
            # Load release note template
            (Path(__file__) / "../release_notes/release_note.md.template")
            .resolve()
            .read_text()
        )
        .replace(
            # Insert the new version number as the title
            "__YYYY.MM.MICRO__",
            formatted_release_version,
        )
        .replace(
            # Insert the release date
            "__Month__ __day__, __year__",
            f"{formatted_release_date}",
        )
        .replace(
            # Insert version tag for RTD link
            "__version__tag__",
            formatted_release_version,
        )
    )

    # Write the release note to a new file
    release_notes_file = (
        Path(__file__) / f"../release_notes/{formatted_release_version}.md"
    ).resolve()
    release_notes_file.write_text(release_notes)
    print(
        f"Release notes skeleton written to {release_notes_file}. "
        "Please fill in the release notes and commit it."
    )


def format_release_version_and_date(*, release_date: Optional[str] = None):
    """
    Get the release date and version from the command line arguments.

    Parameters
    ----------
    release_date : str or None
        The release date for the new version in ISO 8601 format, e.g. YYYY-MM-DD. If None,
        the current date is used.

    Returns
    -------
    formatted_release_ver : str
        The new version number in YYYY.MM.MICRO format.
    formatted_release_date : str
        The release date formatted as "__Month__ __day__, __year__".
    """
    if release_date is None:
        date_release = datetime.datetime.today().date()
    else:
        date_release = datetime.date.fromisoformat(release_date)

    # Extract the current version number from the cotainr module
    try:
        yyyy, mm, micro = cotainr.__version__.split(".")[:3]
    except ValueError as e:
        raise ValueError(
            f"Current release version {cotainr.__version__} is not in the expected format."
        ) from e
    assert re.match(COTAINR_RELEASE_VERSION_FORMAT_RE, f"{yyyy}.{mm}.{micro}")

    # Determine the MICRO version number
    if date_release.year < int(yyyy) or (
        date_release.year == int(yyyy) and date_release.month < int(mm)
    ):
        raise ValueError(
            f"New release date {date_release} is before the current version {cotainr.__version__}."
        )
    elif date_release.year > int(yyyy) or date_release.month > int(mm):
        # New year or month since last release, set MICRO to 0
        micro_release_ver = 0
    else:
        # Same year/month as last release, set MICRO += 1
        micro_release_ver = int(micro) + 1

    # Format the full new version number
    formatted_release_ver = (
        f"{date_release.year}.{date_release.month}.{micro_release_ver}"
    )

    # Format the release date for the release notes
    formatted_release_date = _format_release_notes_date(date_release)

    return formatted_release_ver, formatted_release_date


def _format_release_notes_date(date: datetime.date):
    """
    Format `date` as a "__Month__ __day__, __year__" string.

    Parameters
    ----------
    date : datetime.date
        The date to format.

    Returns
    -------
    formatted_date : str
        The formatted date string.
    """
    # Determine english orginal prefix
    if date.day in [1, 21, 31]:
        day_prefix = "st"
    elif date.day in [2, 22]:
        day_prefix = "nd"
    elif date.day in [3, 23]:
        day_prefix = "rd"
    else:
        day_prefix = "th"

    current_locale = locale.getlocale()
    if current_locale[0] not in ["C", "en_US", "en_GB"]:
        raise RuntimeError(
            f"Your locale is set to {current_locale}. "
            "Please set it to an English locale (C, en_US, or en_GB) "
            "via e.g. the LANG environment variable before running this script."
        )

    formatted_date = date.strftime(f"%B %-d{day_prefix}, %Y")

    return formatted_date


if __name__ == "__main__":  # pragma: no cover
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release_date",
        type=str,
        help=(
            "The release date for the new version in ISO 8601 format, e.g. YYYY-MM-DD. "
            "If not provided, the current date is used."
        ),
    )
    args = parser.parse_args()

    # Format the release version number and release notes date
    formatted_release_version, formatted_release_date = format_release_version_and_date(
        release_date=args.release_date
    )

    # Create the version switcher for the documentation
    create_docs_switcher(formatted_release_version=formatted_release_version)
    create_release_notes(
        formatted_release_version=formatted_release_version,
        formatted_release_date=formatted_release_date,
    )
