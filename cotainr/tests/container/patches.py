import shutil
from subprocess import CompletedProcess

import pytest

import cotainr.container


@pytest.fixture
def patch_disable_singularity_sandbox_subprocess_runner(monkeypatch):
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


@pytest.fixture
def patch_save_singularity_sandbox_context(monkeypatch):
    """
    Store the SingularitySandbox context for inspection in tests.

    The content on `SingularitySandbox.sandbox_dir` is copied to
    `saved_sandbox_dir` before being cleaned up.
    """

    def mock_exit(self, exc_type, exc_value, traceback):
        # Copy content of _tmp_dir
        shutil.copytree(self.sandbox_dir, self._origin / "saved_sandbox_dir")

        # Call "true" __exit__ for cleanup
        self._non_mocked_context_exit(exc_type, exc_value, traceback)

    monkeypatch.setattr(
        cotainr.container.SingularitySandbox,
        "_non_mocked_context_exit",
        cotainr.container.SingularitySandbox.__exit__,
        raising=False,
    )
    monkeypatch.setattr(cotainr.container.SingularitySandbox, "__exit__", mock_exit)
