"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.


 This should be run before
    making a tag for the latest version. More information about releasing can
    befound here:
    https://cotainr.readthedocs.io/en/latest/development/releasing.html




"""

import argparse
import contextlib
import datetime
import json
import locale
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, f"{(Path(__file__) / '../..').resolve()}")

import cotainr

COTAINR_RELEASE_VERSION_FORMAT_RE = r"^20[0-9]{2}\.(0[1-9]|10|11|12)\.(0|[1-9][0-9]*)$"  # cotainr YYYY.0M.MICRO version format


def _format_date(date: datetime.date):
    """
    Format `date` as a "__Month__ __day__, __year__" string.

    Parameters
    ----------
    date : datetime.date
        The date to format.
    """

    @contextlib.contextmanager
    def fixed_locale(category, locale_string):
        """Context manager to temporarily fix the locale."""
        current_locale = locale.getlocale(category)
        locale.setlocale(category, locale_string)
        yield
        locale.setlocale(category, current_locale)

    # Determine english orginal prefix
    if date.day in [1, 21, 31]:
        day_prefix = "st"
    elif date.day in [2, 22]:
        day_prefix = "nd"
    elif date.day in [3, 23]:
        day_prefix = "rd"
    else:
        day_prefix = "th"

    with fixed_locale(locale.LC_TIME, "C"):
        formatted_date = date.strftime(f"%B %-d{day_prefix}, %Y")

    return formatted_date


def create_docs_switcher(*, new_release_ver: str):
    """
    Create the version switcher for the documentation.

    Automatically create the version switcher configuration for the PyData
    Sphinx Theme. The switcher will contain the latest 4 releases. See
    https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/version-dropdown.html#add-a-json-file-to-define-your-switcher-s-versions
    for more technical details.

    Parameters
    ----------
    new_release_ver : str
        The YYYY.0M.MICRO version tag for the new release.
    """
    assert re.match(COTAINR_RELEASE_VERSION_FORMAT_RE, new_release_ver)

    # Create base switcher with the latest and stable versions
    switcher = [
        {
            "name": "dev",
            "version": "latest",
            "url": "https://cotainr.readthedocs.io/en/latest/",
        },
        {
            "name": f"{new_release_ver} (stable)",
            "version": "stable",
            "url": "https://cotainr.readthedocs.io/en/stable/",
        },
    ]

    # Append the latest 3 releases to the switcher based on git tags that match
    # the cotainr version format
    tags = [
        tag
        for tag in (
            subprocess.run(
                ["git", "--no-pager", "tag"], capture_output=True, text=True
            ).stdout.splitlines()
        )
        if re.match(COTAINR_RELEASE_VERSION_FORMAT_RE, tag)
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


def create_release_notes(*, new_release_ver: str, release_date: datetime.date):
    """
    Create the release notes for the new version.

    Automatically create the skeleton for the release notes for the new
    version. Fills in the version number in the release note template.

    Parameters
    ----------
    new_release_ver : str
        The YYYY.0M.MICRO version tag for the new release.
    release_date : datetime.date
        The release date for the new version.
    """
    assert re.match(COTAINR_RELEASE_VERSION_FORMAT_RE, new_release_ver)
    # FIXME: Assert that the release date matches the version tag + test it

    release_notes = (
        (
            # Load release note template
            (Path(__file__) / "../release_notes/release_note.md.template")
            .resolve()
            .read_text()
        )
        .replace(
            # Insert the new version number as the title
            "__YYYY.0M.MICRO__",
            new_release_ver,
        )
        .replace(
            # Insert the release date
            "__Month__ __day__, __year__",
            f"{_format_date(release_date)}",
        )
        .replace(
            # Insert version tag for RTD link
            "__version__tag__",
            new_release_ver,
        )
    )

    # Write the release note to a new file
    release_notes_file = (
        Path(__file__) / f"../release_notes/{new_release_ver}.md"
    ).resolve()
    release_notes_file.write_text(release_notes)
    print(
        f"Release notes skeleton written to {release_notes_file}. "
        "Please fill in the release notes and commit it."
    )


if __name__ == "__main__":  # pragma: no cover
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release_date",
        type=str,
        help="The release date for the new version in YYYY.MM.DD format. The default is the current date.",
    )
    args = parser.parse_args()

    if args.release_date is None:
        release_date = datetime.datetime.today().date()
    else:
        release_date = datetime.datetime.strptime(args.release_date, "%Y.%m.%d").date()

    new_release_ver = cotainr.__version__.split(".dev")[0]

    # Create the version switcher for the documentation
    create_docs_switcher(new_release_ver=new_release_ver)
    create_release_notes(new_release_ver=new_release_ver, release_date=release_date)
