.. _pypi_package:

PyPI package
============
The `cotainr` project provides `wheels <https://packaging.python.org/en/latest/specifications/binary-distribution-format/>`_ and `sdist sources <https://packaging.python.org/en/latest/specifications/source-distribution-format/>`_ on `PyPI <https://pypi.org/project/cotainr/>`_.

These wheels and dist sources are automatically built as part of the :ref:`CD release pipeline <CD_workflows>` using `hatchling <https://hatch.pypa.io/latest/>`_ as build backend and `uv <https://docs.astral.sh/uv/>`_ as a build frontend. The build configuration is defined in the `pyproject.toml <https://github.com/DeiC-HPC/cotainr/blob/main/pyproject.toml>`_ file. The wheels only contain the `cotainr` sub-packages and modules, i.e. the minimal set of files needed to run `cotainr`. The sdist sources contain the `cotainr` sub-packages and modules as well as the :ref:`test suite <test_suite>`, :ref:`reference documentation <reference_docs>`, the `cotainr` license text, and the `cotainr` development configuration files. See the `build-system` and `tool.hatch` configuration tables in the `pyproject.toml <https://github.com/DeiC-HPC/cotainr/blob/main/pyproject.toml>`_ file for more details.

As part of the :ref:`CD release pipeline <CD_workflows>`, the wheels and sdist sources are also uploaded to `TestPyPI <https://test.pypi.org/project/cotainr/>`_ for testing purposes. These are not intended for production use. They are only used to test the build and upload process before releasing a new version of `cotainr` to `PyPI <https://pypi.org/project/cotainr/>`_.
