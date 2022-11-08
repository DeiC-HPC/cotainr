import pytest

import cotainr.container


@pytest.fixture
def patch_sandbox_run_command_in_container(monkeypatch):
    def mock_run_command_in_container(self, *args, **kwargs):
        print(f"Ran command: {kwargs['cmd']}")

    monkeypatch.setattr(
        cotainr.container.SingularitySandbox,
        "run_command_in_container",
        mock_run_command_in_container,
    )
