"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

from abc import ABC


class StubLicensePopen(ABC):
    def __init__(self, args, stdin=None, stdout=None, text=None):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def communicate(self, input=None):
        print(f"{self.__class__.__name__} received: {input=}.")
        return (self.license_text, "")

    def kill(self):
        print(f"{self.__class__.__name__} killed.")


class StubEmptyLicensePopen(StubLicensePopen):
    license_text = ""


class StubShowLicensePopen(StubLicensePopen):
    license_text = (
        "STUB:\n"
        "Please, press ENTER to continue\n"
        ">>> \n"
        "This is the license terms..."
    )
