"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

Automatically create the version switcher configuration for the PyData Sphinx Theme.
See https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/version-dropdown.html#add-a-json-file-to-define-your-switcher-s-versions for details.

The switcher will contain the latest 4 releases. This should be run before making a tag for the latest version.
More information about releasing can be found here: https://cotainr.readthedocs.io/en/latest/development/releasing.html
"""

import json
from pathlib import Path
from re import match
import subprocess
import sys

sys.path.insert(0, f"{(Path(__file__) / '../..').resolve()}")

import cotainr

tags = [
    tag
    for tag in (
        subprocess.run(
            ["git", "--no-pager", "tag"], capture_output=True, text=True
        ).stdout.splitlines()
    )
    # Checking if the tag matches the versioning scheme YYYY.MM.MINOR
    if match(r"^20[0-9]{2}\.(0[1-9]|10|11|12)\.[0-9]+$", tag) is not None
]
tags.reverse()

switcher = [
    {
        "name": "dev",
        "version": "latest",
        "url": "https://cotainr.readthedocs.io/en/latest/",
    },
    {
        "name": f"{cotainr.__version__} (stable)",
        "version": "stable",
        "url": "https://cotainr.readthedocs.io/en/stable/",
    },
]

for tag in tags[0:3]:
    switcher.append(
        {
            "name": tag,
            "version": tag,
            "url": f"https://cotainr.readthedocs.io/en/{tag}/",
        }
    )


(Path(__file__) / "../_static/switcher.json").resolve().write_text(
    json.dumps(switcher, indent="  ")
)
