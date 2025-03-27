.. _cli_internals:

CLI internals
=============

The `cotainr` command line interface is designed around a subcommand for each major action, `cotainr` provides. Each subcommand then supports a set of options. They all support :code:`--help` for displaying a help message.

The CLI is build using :mod:`argparse`.

The main way to invoke the CLI (sub)commands is via the `cotainr` entrypoint,

.. code-block:: console

    $ cotainr build <positional_arg> <non-positional args>
    $ cotainr info

This assumes that `cotainr` is installed via :code:`pip install cotainr`. Alternatively, the CLI (sub)commands may also be executed directly via the `bin/cotainr` executable in an HPC environment by substituting ``./bin/cotainr`` instead of ``cotainr``.

Implementation of command line interface
----------------------------------------
The command line interface is implemented in the :mod:`cotainr.cli` module. It consists of the :class:`~cotainr.cli.CotainrCLI` class that implements the main CLI command. When instantiated, it exposes the following two attributes:

- :attr:`~cotainr.cli.CotainrCLI.args`: A :class:`types.SimpleNamespace` containing the parsed CLI arguments.
- :attr:`~cotainr.cli.CotainrCLI.subcommand`: An instance of the subcommand class that is requested when the script was invoked.

The :class:`~cotainr.cli.CotainrCLI` class is intended to be used as:

.. code-block:: python

    cli = CotainrCLI()
    cli.subcommand.execute()

Each of the subcommands is implemented as a separate subclass of the :class:`~cotainr.cli.CotainrSubcommand` class which defines the following interface:

- :meth:`~cotainr.cli.CotainrSubcommand.__init__`: Constructor that assigns all parameters as instance attributes and performs any check/verification and parsing of the parameters beyond simple checks and parsing implemented by the :meth:`argparse.ArgumentParser.add_argument` method.
- :meth:`~cotainr.cli.CotainrSubcommand.add_arguments`: Classmethod that implements the relevant :meth:`argparse.ArgumentParser.add_argument` CLI arguments corresponding to the constructor arguments.
- :meth:`~cotainr.cli.CotainrSubcommand.execute`: Method that does whatever it entails to run the subcommand.

In order to add a new subcommand, one has to:

- Implement a class that:

  - Is named as the desired subcommand name.
  - Implements the above subcommands interface.

- Add the class to the :attr:`cotainr.cli.CotainrCLI._subcommands` class attribute.

This implementation was inspired by `Satya Sai Vineeth Guna's cli_design.py <https://gist.github.com/vineethguna/d72a8f071a783de2d7ca>`_.

Throughout the implementation, we try to avoid repeating (in the source code) help messages for the CLI by (ab)using the `__doc__` dunder to automatically extract such help messages from a single place of definition. That is, the text shown when running :code:`cotainr --help`, :code:`cotainr build --help`, etc. is automatically extracted from the docstrings of the classes implementing those (sub)commands. Specifically, we automatically extract:

- The main CLI description text from the :class:`~cotainr.cli.CotainrCLI` class docstring short summary.
- The subcommands description and help summary from their class docstring short summary, e.g. for the :code:`cotainr build` subcommand we extract it from the :class:`~cotainr.cli.Build` class docstring.
- The subcommands help texts from the `Parameters` section in their class docstring. For easing this, we have the :func:`cotainr.cli._extract_help_from_docstring` function. Note that this utility function relies on the assumption that the docstrings are formatted according to the `numpydoc format <https://numpydoc.readthedocs.io/en/latest/format.html>`_.
