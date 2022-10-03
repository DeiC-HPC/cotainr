# Container Builder source code

## Design

Generally, we try to:

- error early
- use self-describing commands and options
- make it simple.

### Command line interface design

The container builder is designed around the command line action/command structure like in git

There are 2 supported commands:

- build : Build a container
- info : Obtain info about the state of all required dependencies for building a container

The idea is to invoke the commands like

- `python builder/cli.py build <positional_arg> <non-positional args>`
- `python builder/cli.py info`

Each subcommand then supports a set of options. They all support `--help` for displaying a help message.

The main command does not support any options except for `--help`.

#### The build subcommand

The build command takes one positional argument:

- `image_path` : path to the built Singularity image.

The following non-positional arguments may be specified with the `build` subcommand:

- `--base-image` : a valid singularity \<BUILD SPEC\> that is used as the base for the container.
- `--conda-env` : an exported Conda environment to install and activate in the container.

#### The info subcommand

The info subcommand does not take any arguments.

### Implementation of command line interface

The command line interface is implemented in the `builder.py` module. It consists of the `BuilderCLI` class that implements the main CLI command. When instantiated, it exposes the follow two attributes:

- `args`: A `SimpleNamespace` containing the parsed CLI arguments.
- `subcommand`: An instance of the subcommand that is requested when the script was invoked.

The `BuilderCLI` is intended to be used as:

```python
cli = BuilderCLI()
cli.subcommand.execute()
```

Each of the subcommands is implemented as a separate class in the `builder.py` module with the following interface:

- `__init__(...)`: Constructor that assigns all parameters as instance attributes and performs any check/verification and parsing of the parameters beyond simple checks and parsing implemented by the `ArgumentParser.add_argument()` method.
- `add_arguments(cls, parser)`: Classmethod that implements the relevant `add_arguments()` CLI arguments corresponding to the constructor arguments.
- `execute()`: Method that does whatever it entails to run the subcommand.

In order to add a new subcommand, one has to:

- Implement a class that:
  - Is named as the desired subcommand name.
  - Implements the above subcommands interface.
- Add the class to the `subcommands` list in the `BuilderCLI.__init__()` constructor.

This implementation was inspired by https://gist.github.com/vineethguna/d72a8f071a783de2d7ca.

Throughout the implementation, we try to avoid repeating help messages for the CLI by (ab)using the `__doc__` dunder to automatically extract such help messages from a single place of definition. Specifically, we automatically extract:

- The main CLI description text from the `BuilderCLI` short summary.
- The subcommands help summary from their class short summary.
- The subcommands help texts from the `Parameters` section in the class docstring. For easing this, we have the `_extract_help_from_docstring(arg, docstring)` function in `builder.py`. Note that this utility function relies on the assumption that the docstrings are formatted according to the numpydoc format.
