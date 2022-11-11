from subprocess import CompletedProcess

import pytest

import cotainr.container


@pytest.fixture
def patch_singularity_sandbox_subprocess_runner(monkeypatch):
    def mock_subprocess_runner(self, *, args, **kwargs):
        msg = f"PATCH: Ran command in sandbox: {args}"
        print(msg)
        return CompletedProcess(args, returncode=0, stdout=msg)

    monkeypatch.setattr(
        cotainr.container.SingularitySandbox,
        "_subprocess_runner",
        mock_subprocess_runner,
    )
