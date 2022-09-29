# Container Builder source code

## Design

Generally, we try to:

- error early
- use self-decribing commands and options
- make it simple.

### Arguments design

The container builder is designed around the command line action/command structure like in git

There are 2 supported commands:

- build : Build a container
- info : Obtain info about the state of all required dependencies for building a container

The idea is to invoke the commands like

- `python builder.py build <positional_arg> <non-positional args>`
- `python builder.py info`

Each subcommand then supports a set of options. They all support `--help` for displaying a help message.

The main command does not support any options except for `--help`.

### The build subcommand

The build command takes one positional argument:

- `image_path` : path to the built Singularity image.

The following non-positional arguments may be specified with the `build` subcommand:

- `--base-image` : a valid singularity \<BUILD SPEC\> that is used as the base for the container.
- `--conda-env` : an exported Conda environment to install and activate in the container.

### The info subcommand

The info subcommand does not take any arguments.
