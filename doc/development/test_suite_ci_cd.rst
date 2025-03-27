.. _test_suite:

Test suite & CI/CD
==================

`cotainr` comes with an extensive test suite which is run automatically via continuous integration when code is committed to the `cotainr` GitHub repository: https://github.com/DeiC-HPC/cotainr

The test suite
--------------

The `cotainr` test suite is implemented using `pytest <https://docs.pytest.org/>`_ and uses the `pytest-cov <https://docs.pytest.org/>`_ plugin for reporting test coverage. In order to run the test suite locally, first set up a developer environment by installing the test dependencies declared in the `cotainr pyproject.toml file <https://github.com/DeiC-HPC/cotainr/blob/main/pyproject.toml>`_. This can be done using `uv <https://docs.astral.sh/uv/>`_ for setting up the environment:

.. code-block:: console

    $ uv sync --group tests

Alternatively, you can also install the (default) `dev` group which contains the full development environment, including the `tests` group.

Once the development environment has been installed, simply run `pytest` from the repository root directory, e.g. using uv:

.. code-block:: console

    $ uv run pytest


Pytest marks
~~~~~~~~~~~~
The following custom `pytest marks <https://docs.pytest.org/en/7.1.x/how-to/mark.html>`_ are implemented:

- :func:`pytest.mark.endtoend`: end-to-end tests of workflows using `cotainr` (may take a long time to run)
- :func:`pytest.mark.singularity_integration`: integration tests that require and use singularity (may take a long time to run)
- :func:`pytest.mark.conda_integration`: integration tests that installs and manipulates a conda environment (may take a long time to run)

You may select/deselect end-to-end and integration tests using the :code:`-m` option to :code:`pytest`, e.g. to only run the unittest:

.. code-block:: console

    $ pytest -m "not endtoend and not singularity_integration and not conda_integration"


The tests folder hierarchy and naming conventions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
All tests are placed in the `cotainr/tests` folder. This `tests` folder acts as a sub-package in :mod:`cotainr`. The :mod:`cotainr.tests` sub-package contains a sub-package for each module in `cotainr` (structured in the same way as the modules in `cotainr`). Each such test sub-package contains a module for each class/function in the corresponding `cotainr` module. If the test module relates to a class, it contains, for each method in that class, one test class with any number of tests cases (implemented as methods). If the test module relates to a function, it contains one test class for that function and, optionally, one test class for any private "helper" function to that function. Here are a few examples to illustrate all of this:

- All tests of the :class:`cotainr.pack.CondaInstall` class are placed in `cotainr/tests/pack/test_conda_install.py` which acts as a python module reachable via :mod:`cotainr.tests.pack.test_conda_install`.
- The tests of the :meth:`cotainr.pack.CondaInstall.add_environment` method are implemented in the class :class:`cotainr.tests.pack.test_conda_install.TestAddEnvironment`.
- The tests of the :func:`cotainr.util.stream_subprocess`: function are implemented in the class :class:`cotainr.tests.util.test_stream_subprocess.TestStreamSubprocess`. Specifically, this class implements test cases (methods) like :meth:`test_completed_process` or :meth:`test_check_returncode`.
- The module :mod:`cotainr.tests.util.test_stream_subprocess` also includes a class, :class:`Test_PrintAndCaptureStream`, implementing the tests of the private "helper" function :func:`cotainr.utils._print_and_capture_stream`.

In addition to the modules implementing the tests of the functions and classes in `cotainr`, the sub-packages in :mod:`cotainr.tests` may also include "special" modules implementing test fixtures and stubs:

- `patches.py`: Contains all (monkey)patch fixtures related to that sub-package, e.g. the patch fixture :func:`cotainr.tests.util.patches.patch_disable_stream_subprocess`. All patch fixtures are prefixed with `patch_`.
- `data.py`: Contains all test data fixtures related to that sub-package, e.g. the data fixture :func:`cotainr.tests.container.data.data_cached_ubuntu_sif`. All data fixtures are prefixed with `data_`.
- `stubs.py`: Contains all test stubs related to that sub-package, e.g. the stub :class:`cotainr.tests.cli.stubs.StubValidSubcommand`.

All general purpose fixtures, which do not belong in one of the sub-package specific fixture modules listed above, are defined in the `tests/conftest.py` module.

Finally, the :mod:`cotainr.tests.test_end_to_end` module contains all workflow end-to-end test using `cotainr`.

Imports in test modules
~~~~~~~~~~~~~~~~~~~~~~~
Imports in test modules are based on the following conventions:

- Functions and classes, subject to testing, are imported using absolute imports, e.g. :code:`import cotainr.pack.CondaInstall` in `tests/pack/test_conda_install.py`.
- Sub-package specific fixtures are explicitly imported using relative imports, e.g. :code:`from ..container.data import data_cached_ubuntu_sif` in `tests/pack/test_conda_install.py`.
- Fixtures defined in `tests/conftest.py` are not explicitly imported (they are implicitly imported by `pytest``). Thus, if a fixture is used, but not imported, in a test module, `tests/conftest.py` is the only module in which it can (or at least should) be defined.

.. _continuous_integration:

Continuous Integration (CI)
---------------------------
Continuous Integration (CI) is handled via `GitHub Actions <https://docs.github.com/en/actions>`_ in the `cotainr` GitHub repository https://github.com/DeiC-HPC/cotainr/actions. The tests run on the GitHub-hosted `ubuntu-latest <https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners/about-github-hosted-runners#supported-runners-and-hardware-resources>`_ runner. When running the CI test `matrix <https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs>`_, we differentiate between the following (meta)versions of dependencies:

- *stable*: The minimum supported version of the dependency.
- *latest*: The latest released version of the dependency.
- *all*: All supported versions of the dependency.

CI workflows
~~~~~~~~~~~~
The following CI `workflows <https://docs.github.com/en/actions/using-workflows/about-workflows>`_ are implemented:

- `CI_pull_requests.yml <https://github.com/DeiC-HPC/cotainr/actions/workflows/CI_pull_request.yml>`_:
  Runs the unit tests, integration tests, and end-to-end tests on pull requests to the *main* branch.
  *All* Python versions and *stable* Singularity as well as *stable* Apptainer versions are tested.
  Lint and formatting checks (as described in the :ref:`style guide <style_guide>`) are also run and enforced.
- `CI_push.yml <https://github.com/DeiC-HPC/cotainr/actions/workflows/CI_push.yml>`_:
  Runs the unit tests on pushes to all branches. Restricted to *stable* and *latest* Python versions.
  Lint and formatting checks (as described in the :ref:`style guide <style_guide>`) are also run and enforced.


Continuous Delivery (CD)
------------------------
Continuous Delivery (CD) is handled partly via `GitHub Actions <https://docs.github.com/en/actions>`_, partly via the a `Read the Docs webhook integration <https://docs.readthedocs.io/en/stable/continuous-deployment.html>`_ to the `cotainr` GitHub repository: https://github.com/DeiC-HPC/cotainr/.

CD workflows
~~~~~~~~~~~~
The following CD `workflow <https://docs.github.com/en/actions/using-workflows/about-workflows>`_ is implemented:

- `CD_release.yml <https://github.com/DeiC-HPC/cotainr/actions/workflows/CD_release.yml>`_: Creates GitHub and PyPI releases when new tags following the :ref:`versioning scheme <version-scheme>` are committed to the main branch.

  The GitHub release job is run independently and does not have deployment protection rules as it can easily be undone by first removing the release through the GitHub UI and then remove the tag if something goes wrong.

  The PyPI release process goes as following:

  - Build the Python Wheel
  - Publish to TestPyPI index
  - In a clean environment, download and install from TestPyPI and run basic CLI functionality
  - Publish to PyPI.

  The testPyPI and PyPI index locations are both implemented as `GitHub environments <https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-deployments/managing-environments-for-deployment>`_ attached to the DeiC-HPC account. These environments have deployment protection rules which require review from a member of the HPC-developers team before the action is executed. This ensures protection against accidental tag pushes which is needed since removal of releases from TestPyPI and PyPI is difficult.

Read the Docs continuous documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The :ref:`HTML documentation <building_the_html_docs>` served at http://cotainr.readthedocs.io is automatically built by Read the Docs based on the configuration in the `.readthedocs.yml configuration file <https://github.com/DeiC-HPC/cotainr/blob/main/.readthedocs.yml>`_.

.. include:: ../../.readthedocs.yml
    :literal:

This fully automates the process of building `*latest* and *stable* versions <https://docs.readthedocs.io/en/stable/versions.html>`_ of the HTML documentation served at http://cotainr.readthedocs.io. Additionally, the `"build pull requests" <https://docs.readthedocs.io/en/stable/pull-requests.html>`_ feature is enabled. A pull request documentation build is linked in the list of checks for the GitHub pull request.

The automated release process `can be inspected here <https://readthedocs.org/dashboard/cotainr/rules/>`_. Essentially any git-tag matching the described :ref:`versioning-scheme <releasing>` will be picked up by Read the Docs and should be available among the versions as well as activated as `stable <https://cotainr.readthedocs.io/en/stable>`_ and `latest <https://cotainr.readthedocs.io/en/latest>`_


Scheduled tests
---------------
We run `scheduled GitHub actions <https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule>`_ (weekly, every Tuesday night) in order to continuously test `cotainr` against its dependencies. That way we proactively monitor for changes in dependencies that end up breaking `cotainr`.

Currently, the following scheduled `workflows <https://docs.github.com/en/actions/using-workflows/about-workflows>`_ are implemented:

- `SCHED_docs_linkcheck <https://github.com/DeiC-HPC/cotainr/actions/workflows/SCHED_docs_linkcheck.yml>`_: Builds the documentation and checks for any broken hyperlinks.

Additionally, we currently also schedule the `CI_pull_requests.yml <https://github.com/DeiC-HPC/cotainr/actions/workflows/CI_pull_request.yml>`_ workflow which tests the most recent point release of Python in the :ref:`CI test matrix <continuous_integration>`.
