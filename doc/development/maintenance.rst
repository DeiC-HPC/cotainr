.. _maintenance:

Maintenance
===========

We currently have one important topic for ongoing maintenance work.
This are the needed procedures to bump/deprecate supported versions of Python, Singularity-CE and Apptainer.

Below we describe the changes required for bumping Python.
Singularity-CE and Apptainer bumps for now only need to be tested by bumping the version in the test matrix.

In the code, we try to keep track of points of importance for version bumps by leaving markers.
More specifically we leave the following `MARK_` throughout the code to highlight important sections that require a change.
`MARK_PYTHON_VERSION` thus indicates changes that need to be made in case of version bumps.
And likewise `MARK_APPTAINER_VERSION` indicates if changes for Apptainer/Singularity-CE need to be made.

Additional marks could be `MARK_MAINTENANCE`.

Python version bumping/deprecating
----------------------------------

TBD
