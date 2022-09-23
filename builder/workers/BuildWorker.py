import sys
import os

# will take all the options we want to add to the command lineinterface. Remember to add them here as well.
class BuildWorker(object):
    def __init__(self, pythonPath):
        self.pythonPath = pythonPath

    # used to error early for things that need to be check when all options are in.
    def verify(self):
        print("verify the options to see if any are contradicting etc.")

    # do the magic and run...run.....
    def run(self):
        #run the damm thing.

        print("running builder with python path=%s", self.pythonPath)
        