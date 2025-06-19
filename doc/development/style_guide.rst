.. _style_guide:

Style guide
===========
We aim to keep the `cotainr` code base and documentation consistent by following the style guides listed here.

- We follow the :pep:`8` style guide.
- All metadata and tool configuration is defined in the `pyproject.toml <https://github.com/DeiC-HPC/cotainr/blob/main/pyproject.toml>`_ file, except where this is not possible, e.g. for pre-commit and Readthedocs.
- The Python source code is formatted using `Ruff <https://github.com/astral-sh/ruff>`_ - see the `cotainr pyproject.toml file <https://github.com/DeiC-HPC/cotainr/blob/main/pyproject.toml>`_ for the Ruff rules we use.
- The codebase is linted with `pre-commit <https://pre-commit.com/>`_ - see the `cotainr .pre-commit-config.yaml file <https://github.com/DeiC-HPC/cotainr/blob/main/.pre-commit-config.yaml>`_ for the pre-commit hooks we use.
- All `docstrings <https://peps.python.org/pep-0257/>`_ are formatted according to the `numpydoc format <https://numpydoc.readthedocs.io/en/latest/format.html>`_.
- We reference the python interpreter executable as `python3` (not `python`) when explicitly calling the system python executable and as :data:`sys.executable` when reinvoking the interpreter as recommended in :pep:`394`.

When hacking on `cotainr`, we generally try to:

- Error early.
- Use self-describing commands and options.
- Make it simple.

Specifically, we use the following conventions:

- Force keyword only arguments to functions and methods.
- Use relative imports within the `cotainr` package when importing functionality from other modules. The imports must be done such that all objects imported are still references (not copies) which allows for monkey patching objects in their definition module in tests.

pre-commit
----------

If you like, you can use `pre-commit <https://pre-commit.com/>`_ to automatically check and
format your code as a git pre-commit hook. A simple way to install pre-commit and set up the
hooks is to run something like

.. code-block:: bash

    pip install pre-commit
    pre-commit install

but this varies depending on your system and setup.

The pre-commit configuration is stored in ``.pre-commit-config.yaml`` in the root of the repository.
The CI/CD workflow in :ref:`test_suite` uses the same pre-commit configuration for linting and formatting.
