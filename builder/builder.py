import argparse
import sys
import os
from workers import BuildWorker, ReportWorker

#design
# error early
# self decribe commands and options
# simple. Let the works do the work and keep this file only to add options and write help text.
# Wrokers will have an init, verify and a run.


# make sure to check the dir path now and up front to ensure we do have to do it later
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
        parser.add_argument("--dryrun", action='store_true')
        parser.add_argument('--python', type=dir_path, help="Path to the python instalation to include")
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command (builder) and the subcommand (build)
        args = parser.parse_args(sys.argv[2:])
        
        # Setup the builder object to with all the args needed.
        worker = BuildWorker.BuildWorker(args.python)
        worker.verify()
        if (args.dryrun == False):
            worker.run()
        
    def system_report(self):
        #output different system veriables the script would normaly want to include in the container
        parser = argparse.ArgumentParser(
            description='Report the different system enverioment and installed libs.')
        parser.add_argument("--onlyenv", action='store_true', help="Only list the system enverioment to check if they are set")
        args = parser.parse_args(sys.argv[2:])
        worker = ReportWorker.ReportWorker(args.onlyenv)
        worker.verify()
        worker.run()




if __name__ == '__main__':
    Builder()