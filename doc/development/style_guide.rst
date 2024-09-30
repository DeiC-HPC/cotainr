.. _style_guide:

Style guide
===========
We aim to keep the `cotainr` code base and documentation consistent by following the style guides listed here.

- We follow the :pep:`8` style guide.
- The Python source code is formatted using `Ruff <https://github.com/astral-sh/ruff>`_ .
- The codebase is linted with `pre-commit <https://pre-commit.com/>`_.
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
