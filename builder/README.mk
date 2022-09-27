# Container Builder source code

## Design

### Arguments design
The container builder is designed around the commandline action/command structure like in git and other tools

There are for now 3 commands supported
 - help
 - build
 - system_report

The idea is to invoke the commands like
`python builder.py help`
`python builder.py build`
`python builder.py system_report`

Each subcommand then support a set of options. They all support
`python builder.py build --help`
that could results in the following report
> usage: builder.py [-h] [--dryrun] [--python PYTHON]
> 
> Build the container with the selected options
> 
> options:
>   -h, --help       show this help message and exit
>   --dryrun
>   --python PYTHON  Path to the python instalation to include



