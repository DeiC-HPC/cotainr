import sys
import os

class ReportWorker(object):
    def __init__(self, onlyenv):
        self.onlyenv = onlyenv

    # used to error early for things that need to be check when all options are in.
    def verify(self):
        print("verify the options to see if any are contradicting etc.")

    # do the magic and run...run.....
    def run(self):
        #run the damm thing.
        #change to cehck for the env settings we want to check for. it only prints now.
        print(os.environ)
        
        