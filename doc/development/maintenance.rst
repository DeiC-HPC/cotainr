.. _maintenance:

Maintenance
===========

The only production dependencies are Python, Singularity-CE and Apptainer. `cotainr` should be up-to-date with the newest supported versions of all these dependencies. The full list of current supported and tested versions are single-sourced in the `matrix.json` file. (Note, the Python version is also specified in `pyproject.toml`). Whenever new minor supported versions are released, they should be tested. If no changes are required, the new versions should be added to `matrix.json` in a `dev_env*` git branch.

In the code, we try to keep track of points of importance for version bumps by leaving markers.
More specifically we leave the following `MARK_` throughout the code to highlight important sections that require a change.
`MARK_PYTHON_VERSION` thus indicates changes that need to be made in case of version bumps.
And likewise `MARK_APPTAINER_VERSION` indicates if changes for Apptainer/Singularity-CE need to be made.

Additional marks could be `MARK_MAINTENANCE`.
