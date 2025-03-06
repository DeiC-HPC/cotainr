"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

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
def patch_fake_singularity_sandbox_env_folder(monkeypatch):
    """
    Fake the creation of the .singularity.d/env/ folder.
    Additionally, fake creation of the environment file 92-cotainr-env.sh

    Normally, the folder is created by SingularitySandbox.__enter__() when it
    runs Singularity to create the sandbox, but when the call to singularity
    has been patched, this fixture may be used to create the folder anyway.
    When singularity is patched, the environment file can no longer be created
    inside the container with correct file permissions, so here it is created outside.
    """

    def mock_enter(self):
        # Call "true" __enter__ for setup
        ret_val = self._non_mocked_context_enter()

        # Create fake environment folder
        singularity_env_folder = self.sandbox_dir / ".singularity.d/env"
        singularity_env_folder.mkdir(parents=True, exist_ok=True)

        return ret_val

    def mock_create_file(self, f):
        # Create file outside the container
        env_file = f or self.sandbox_dir / ".singularity.d/env/92-cotainr-env.sh"
        env_file.touch(exist_ok=True)

    monkeypatch.setattr(
        cotainr.container.SingularitySandbox,
        "_create_file",
        mock_create_file,
    )

    monkeypatch.setattr(
        cotainr.container.SingularitySandbox,
        "_non_mocked_context_enter",
        cotainr.container.SingularitySandbox.__enter__,
        raising=False,
    )

    monkeypatch.setattr(cotainr.container.SingularitySandbox, "__enter__", mock_enter)


@pytest.fixture
def patch_save_singularity_sandbox_context(monkeypatch):
    """
    Store the SingularitySandbox context for inspection in tests.

    The content on `SingularitySandbox.sandbox_dir` is copied to
    `saved_sandbox_dir` before being cleaned up.
    """
    saved_sandbox_dir_name = "saved_sandbox_dir"

    def mock_exit(self, exc_type, exc_value, traceback):
        # Copy content of _tmp_dir
        shutil.copytree(self.sandbox_dir, self._origin / saved_sandbox_dir_name)

        # Call "true" __exit__ for cleanup
        return self._non_mocked_context_exit(exc_type, exc_value, traceback)

    monkeypatch.setattr(
        cotainr.container.SingularitySandbox,
        "_non_mocked_context_exit",
        cotainr.container.SingularitySandbox.__exit__,
        raising=False,
    )
    monkeypatch.setattr(cotainr.container.SingularitySandbox, "__exit__", mock_exit)

    return saved_sandbox_dir_name


@pytest.fixture
def patch_disable_add_metadata(monkeypatch):
    """
    Disable SingularitySandbox.add_metadata().
    """
    monkeypatch.setattr(
        cotainr.container.SingularitySandbox, "add_metadata", lambda _: None
    )
