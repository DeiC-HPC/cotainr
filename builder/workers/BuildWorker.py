import sys
import os

# will take all the options we want to add to the command lineinterface. Remember to add them here as well.
class BuildWorker(object):
    def __init__(self, pythonPath):
        self.pythonPath = pythonPath

    def run(self):
        #run the damm thing.

        print("running builder with python path=%s", self.pythonPath)
        