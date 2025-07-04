.. _maintenance:

Maintenance
===========

This section covers the tasks that must be performed regularly to keep the `cotainr` code base up-to-date with its upstream dependencies as well as its build and test infrastructure.

Dependency version bumps
------------------------
Cotainr (development) dependencies are defined in three places:

- The `matrix.json <https://github.com/DeiC-HPC/cotainr/actions/workflows/matrix.json>`_ file, which is the :ref:`single sourced dependency matrix <single_source_dep_matrix>` for the :ref:`containerized development environment <containerized_development_environment>` used for development of `cotainr` and in the :ref:`CI/CD workflows <continuous_integration>`.
- The `pyproject.toml <https://github.com/DeiC-HPC/cotainr/blob/main/pyproject.toml>`_ file, which specifies the Python package dependencies.
- The `.pre-commit-config.yaml <https://github.com/DeiC-HPC/cotainr/blob/main/.pre-commit-config.yaml>`_ file, which specifies the pre-commit hooks.

All of these need to be regularly updated to keep `cotainr` up-to-date with the latest upstream versions of its dependencies. The strategy and process for updating them is described below.

Bumping `matrix.json` dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We aim to test `cotainr` against versions of its dependencies that we expect to be used in production on HPC systems. Thus, the `matrix.json <https://github.com/DeiC-HPC/cotainr/actions/workflows/matrix.json>`_ should regularity be updated to reflect this. Specifically it should be updated to include:

- All `fully released and still supported versions <https://devguide.python.org/versions/>`_ of Python. Note, the minimum Python version is also specified in `pyproject.toml <https://github.com/DeiC-HPC/cotainr/blob/main/pyproject.toml>`_. When removing the minimum Python version from the `matrix.json`, updates should also be made to the `pyproject.toml` file to reflect this as described in `section covering updates to pyproject.toml dependencies <bumping-pyproject-toml-dependencies>`_.
- SingularityCE and Apptainer versions from the oldest version that is still in use in production on HPC systems that we aim to support up to the latest fully released version. We aim to test all MAJOR and MINOR versions, but only the most recent PATCH, (as defined by `SemVer <https://semver.org/>`_ versioning) of SingularityCE and Apptainer within this span.

.. _bumping-pyproject-toml-dependencies:

Bumping `pyproject.toml` dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The `cotainr` third party Python development dependencies are defined in the `dependency-group` table in the `pyproject.toml <https://github.com/DeiC-HPC/cotainr/blob/main/pyproject.toml>`_ file. As these dependencies only relate to the development of `cotainr`, and thus do not affect the end users of `cotainr`, we don't have a strict policy for which versions we use and test. In general, we aim to regularly update to the most recent fully released versions. When updating the third party Python dependencies, the `minversion` key in the `tool.pytest.ini_options` table should be updated to match the minimum version of `pytest` in the `tests` dependency group.

In addition to the third party Python dependencies, the minimum required Python version for running `cotainr` is also specified in the `pyproject.toml <https://github.com/DeiC-HPC/cotainr/blob/main/pyproject.toml>`_ file in two places:

- The `requires-python` key in the `project` table.
- The `target-version` key in the `tool.ruff` table.

These should be updated to reflect the minimum supported Python version as defined by the `matrix.json <https://github.com/DeiC-HPC/cotainr/actions/workflows/matrix.json>`_ file.

.. _bumping-pre-commit-config-yaml-dependencies:

Bumping `.pre-commit-config.yaml` dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The pre-commit hooks only relate to the development of `cotainr`, and thus do not affect the end users of `cotainr`. Thus, we don't have a strict policy for which versions we use. We just aim to regularly update the pre-commit hooks to the latest fully released versions. The pre-commit hooks may be updated by running :code:`pre-commit autoupdate` which will update the `.pre-commit-config.yaml` to use the latest versions of the pre-commit hooks. The next time you run :code:`git commit`, the installed hooks will be automatically updated to the new versions.

Additional infrastructure updates
---------------------------------
In addition to updating the dependencies, the following should also regularly be updated:

- The OS and Python version for the Read the Docs configuration in `.readthedocs.yaml <https://github.com/DeiC-HPC/cotainr/blob/main/.readthedocs.yaml>`_.
- The actions used in the GitHub workflows in `.github/workflows/`.
- The ARM64 `os.runs-on` target in the `matrix.json <https://github.com/DeiC-HPC/cotainr/actions/workflows/matrix.json>`_ file. As of July 2025, you must specify a specific Ubuntu version for the ARM64 target, e.g. `ubuntu-24.04-arm` whereas the x86_64 target can be set to `ubuntu-latest`.

Maintenance MARKs
-----------------
To make it easier to keep track of the places in the code that require maintenance when `cotainr` dependencies are updated, we use :code:`MARK`'s in the code. Specifically, we use the following marks:

- :code:`MARK_PYTHON_VERSION`: Indicates that the code needs to be updated when changes are made to the tested Python versions.
- :code:`MARK_APPTAINER_VERSION`: Indicates that the code needs to be updated when changes are made to the tested  Apptainer/SingularityCE versions.

When updating the dependencies and doing infrastructure updates, you should search for these marks in the code and update the relevant places in the code accordingly.
