import argparse
import sys
import os
from workers import BuildWorker


# 
def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)



class Builder(object):
    def __init__(self):
        parser = argparse.ArgumentParser(description='Build container for running python on HPC systems', usage='''builder <command> [<args>]''')
        parser.add_argument('command', help='Build command to run and build the container')
        

        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unknown command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()
    def build(self):
        parser = argparse.ArgumentParser(
            description='Build the container with the selected options')
        # prefixing the argument with -- means it's optional
        parser.add_argument('--python', type=dir_path, help="Path to the python instalation to include")
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command (git) and the subcommand (commit)
        args = parser.parse_args(sys.argv[2:])
        
        # Setup the builder object to with all the args needed.
        worker = BuildWorker.BuildWorker(args.python)
        worker.run()
        





if __name__ == '__main__':
    Builder()