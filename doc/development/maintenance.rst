.. _maintenance:

Maintenance
===========

This section covers the tasks that must be performed regularly to keep the `cotainr` code base update-to-date.

Dependency version bumps
------------------------
Cotainr (development) dependencies are defined in three places:

- The `matrix.json <https://github.com/DeiC-HPC/cotainr/actions/workflows/matrix.json>`_ file, which is the :ref:`single sourced dependency matrix <single_source_dep_matrix>` for the :ref:`containerized development environment <containerized_development_environment>` used for development of `cotainr` and in the :ref:`CI/CD workflows <continuous_integration>`.
- The `pyproject.toml <https://github.com/DeiC-HPC/cotainr/blob/main/pyproject.toml>`_ file, which specifies the Python package dependencies.
- The `.pre-commit-config.yaml <https://github.com/DeiC-HPC/cotainr/blob/main/.pre-commit-config.yaml>`_ file, which specifies the pre-commit hooks.



Also update OS in `.readthedocs.yaml <https://github.com/DeiC-HPC/cotainr/blob/main/.readthedocs.yaml>`_ file, which specifies the Read the Docs configuration.



Bumping `matrix.json` dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Version range choices + strategy


The only production dependencies are Python, Singularity-CE and Apptainer. `cotainr` should be up-to-date with the newest supported versions of all these dependencies. The full list of current supported and tested versions are single-sourced in the `matrix.json` file. (Note, the Python version is also specified in `pyproject.toml`). Whenever new minor supported versions are released, they should be tested. If no changes are required, the new versions should be added to `matrix.json` in a `dev_env*` git branch.


Bumping `pyproject.toml` dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bumping `.pre-commit-config.yaml` dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Merge with style guide description



Maintenance MARKs
-----------------


In the code, we try to keep track of points of importance for version bumps by leaving markers.
More specifically we leave the following :code:`MARK_` throughout the code to highlight important sections that require a change.
`MARK_PYTHON_VERSION` thus indicates changes that need to be made in case of version bumps.
And likewise `MARK_APPTAINER_VERSION` indicates if changes for Apptainer/Singularity-CE need to be made.

Additional marks could be `MARK_MAINTENANCE`.
