# Container Builder

## Design

Generally, we try to:

- error early
- use self-describing commands and options
- make it simple

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


### Container sandbox design

The container is built using a sandbox, for now a Singularity sandbox, i.e. a temporary folder is created containing the container content. Software may then be packed into this sandbox using Singularity as a chroot bootstrapper. Once everything is in place in the sandbox, it may be converted to a SIF image file. The sandbox is removed when the builder exists.

## Implementation details

In general, we:

- Force keyword only arguments to functions and methods.

### Formatting

- We follow the PEP8 style guide: https://peps.python.org/pep-0008/
- The Python source code is formatted using black: https://black.readthedocs.io/en/stable/
- All docstrings are formatted according to the numpydoc format: https://numpydoc.readthedocs.io/en/latest/format.html

### Implementation of command line interface

The command line interface is implemented in the `builder.py` module. It consists of the `BuilderCLI` class that implements the main CLI command. When instantiated, it exposes the follow two attributes:

- `args`: A `SimpleNamespace` containing the parsed CLI arguments.
- `subcommand`: An instance of the subcommand that is requested when the script was invoked.

The `BuilderCLI` is intended to be used as:

```python
cli = BuilderCLI()
cli.subcommand.execute()
```

Each of the subcommands is implemented as a separate subclass of the `BuilderSubcommand` in the `builder.py` module with the following interface:

- `__init__(self, *, ...)`: Constructor that assigns all parameters as instance attributes and performs any check/verification and parsing of the parameters beyond simple checks and parsing implemented by the `ArgumentParser.add_argument(...)` method.
- `add_arguments(cls, *, parser)`: Classmethod that implements the relevant `add_arguments(...)` CLI arguments corresponding to the constructor arguments.
- `execute(self)`: Method that does whatever it entails to run the subcommand.

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

### Implementation of container sandbox

The container sandbox is implemented in the `container.py` module as a context manger. Running a command in the sandbox context is wrapped as a subprocess call to `singularity exec`.

### Implementation of software packing

Functionality that allows for packing software into the container sandbox is implemented in the `pack.py` module. This packing functionality must interact with a container sandbox from `container.py`.

## Dependencies

- The builder tool requires:
  - Python, version 3.?, for running the tool
  - Singularity, version ?, for building a container
- The `CondaInstall` from `pack.py` requires that Bash, version ?, is installed in the base image used for the container.

## Limitations

- Since the container is being built entirely in user space, we are unable to correctly handle file permissions that should be set with root privileges.

## Examples

Create a container which includes the Conda environment in `example_files/test_conda_env.yml` and use it to run the `example_files/matmul_example.py` script.

```bash
$ python builder/cli.py build ubuntu_conda_container.sif --base-image docker://ubuntu:22.04 --conda-env example_files/test_conda_env.yml
$ singularity exec ubuntu_conda_container.sif python example_files/matmul_example.py
```
