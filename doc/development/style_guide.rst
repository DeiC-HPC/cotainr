.. _style_guide:

Style guide
===========
We aim to keep the `cotainr` code base and documentation consistent by following the style guidelines listed here.

- We follow the :pep:`8` style guide.
- All metadata and tool configurations are defined in the `pyproject.toml <https://github.com/DeiC-HPC/cotainr/blob/main/pyproject.toml>`_ file, except where this is not possible, e.g. for `pre-commit  <https://pre-commit.com/>`_ and `ReadtheDocs <https://readthedocs.org/>`_.
- The Python source code is formatted using `Ruff <https://github.com/astral-sh/ruff>`_ - see the `cotainr pyproject.toml file <https://github.com/DeiC-HPC/cotainr/blob/main/pyproject.toml>`_ for the Ruff rules we use.
- The codebase is linted with `pre-commit <https://pre-commit.com/>`_ - see the `cotainr .pre-commit-config.yaml file <https://github.com/DeiC-HPC/cotainr/blob/main/.pre-commit-config.yaml>`_ for the pre-commit hooks we use.
- All `docstrings <https://peps.python.org/pep-0257/>`_ are formatted according to the `numpydoc format <https://numpydoc.readthedocs.io/en/latest/format.html>`_.
- We reference the python interpreter executable as `python3` (not `python`) when explicitly calling the system python executable and as :data:`sys.executable` when reinvoking the interpreter as recommended in :pep:`394`.
- No (hard) line wrapping is used in restructured text and markdown files placed in the `doc/` directory (the :ref:`cotainr reference documentation <reference_docs>` files).

When hacking on `cotainr`, we generally try to:

- Error early.
- Use self-describing commands and options.
- Use comments to explain why something is done, not how.
- Include unit and integration tests for new features and bug fixes.
- Make it simple.

Specifically, we use the following conventions:

- Force keyword only arguments to functions and methods (as defined in :pep:`3102`).
- Use relative imports within the `cotainr` package when importing functionality from other modules. The imports must be done such that all objects imported are still references (not copies) which allows for monkey patching objects in their definition module in tests.

pre-commit
----------

If you like, you can use `pre-commit <https://pre-commit.com/>`_ to automatically check and format your code using a `git pre-commit hook <https://git-scm.com/book/ms/v2/Customizing-Git-Git-Hooks>`_. The pre-commit tool is included in the `lint` dependency group (which is also part of the `dev` dependency group) in the cotainr `pyproject.toml <https://github.com/DeiC-HPC/cotainr/blob/main/pyproject.toml>`_ file. Thus, an easy way to install pre-commit and setup up the pre-commit hooks for cotainr using the `uv package manager <https://docs.astral.sh/uv/>`_ is to run the following commands in the checked out cotainr git repository root directory:

.. code-block:: bash

    uv sync --group lint
    uv run pre-commit install

This will install the pre-commit hooks defined in the `.pre-commit-config.yaml <https://github.com/DeiC-HPC/cotainr/blob/main/.pre-commit-config.yaml>`_. The pre-commit hooks will then automatically run when you run :code:`git commit` in the repository. The  :ref:`CI/CD workflow <continuous_integration>` uses the same pre-commit configuration for linting and formatting.

The pre-commit hooks may be updated by running :code:`pre-commit autoupdate` which will update the `.pre-commit-config.yaml` to use the latest versions of the pre-commit hooks. The next time you run :code:`git commit`, the installed hooks will be automatically updated to the new versions.
