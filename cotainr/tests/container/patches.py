from subprocess import CompletedProcess

import pytest

import cotainr.container


@pytest.fixture
def patch_singularity_sandbox_subprocess_runner(monkeypatch):
    """
    Disable SingularitySandbox._subprocess_runner(...).

    The subprocess runner is replaced by a method that prints and returns a
    message about the command that would have been run.
    """

    def mock_subprocess_runner(self, *, args, **kwargs):
        msg = f"PATCH: Ran command in sandbox: {args}"
        print(msg)
        return CompletedProcess(args, returncode=0, stdout=msg)

    monkeypatch.setattr(
        cotainr.container.SingularitySandbox,
        "_subprocess_runner",
        mock_subprocess_runner,
    )
