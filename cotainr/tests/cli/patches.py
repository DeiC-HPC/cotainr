import pytest

import cotainr.cli


@pytest.fixture
def patch_disable_main(monkeypatch):
    """
    Disable main.

    Replace the `main` cli function with a function that prints and returns a
    message about the execution of the main function that would have run.
    """

    def mock_main(*args, **kwargs):
        msg = "PATCH: Ran cotainr.cli main function"
        print(msg)
        return msg

    monkeypatch.setattr(cotainr.cli, "main", mock_main)
