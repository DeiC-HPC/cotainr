"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

from abc import ABC


class StubLicensePopen(ABC):
    license_text: str

    def __init__(self, args, stdin=None, stdout=None, text=None):  # noqa: B027
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: B027
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
        "STUB:\nPlease, press ENTER to continue\n>>> \nThis is the license terms...\n"
    )
