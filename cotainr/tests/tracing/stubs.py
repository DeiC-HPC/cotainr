"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import contextlib


class AlwaysCompareFalse:
    """A stub that returns False for all Python "rich comparisons"."""

    def __lt__(self, other):
        return False

    def __le__(self, other):
        return False

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return False

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return False

    def __repr__(self):
        return "AlwaysCompareFalseStub"


class FixedNumberOfSpinsEvent:
    """
    An event that fixes the number of times the message is spun in a MessageSpinner.
    """

    def __init__(self, *, spins):
        assert isinstance(spins, int)
        assert spins >= 0
        self.remaining_spins = spins

    def is_set(self):
        if self.remaining_spins == 0:
            return True
        else:
            self.remaining_spins -= 1
            return False

    def set(self):
        pass


@contextlib.contextmanager
def RaiseOnEnterContext():
    raise NotImplementedError("Entered context")
    yield
