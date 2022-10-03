"""
Packaging for user space Apptainer/Singularity container builder.

Created by DeiC, deic.dk

Classes
-------
CondaInstall
"""


class CondaInstall:
    def __init__(self, install_root, prefix="/opt/conda"):
        pass

    def run_command(self, conda_cmd):
        pass
        #subprocess.run(["source test_source.sh; echo $CHRSO_TEST"], capture_output=True, shell=True, executable="/bin/bash", check=True, text=True)
