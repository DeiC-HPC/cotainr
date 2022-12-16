"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

Automatically create the list of release notes
"""

from pathlib import Path

release_notes_dir = Path(__file__).parent

print(f"Creating file {release_notes_dir.name}/release_list.rst")
with (release_notes_dir / "release_list.rst").open(mode="w") as f:
    for path in sorted(release_notes_dir.glob("*.md"), reverse=True):
        f.write(f".. include:: {path.name}\n")
        f.write("    :parser: myst_parser.sphinx_\n\n")
