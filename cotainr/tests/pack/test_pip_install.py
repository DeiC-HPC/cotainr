"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Copyright Aarni Koskela

Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import pytest

from cotainr.container import SingularitySandbox
from ..container.data import data_cached_python312_sif  # noqa
from cotainr.pip import PipInstall


@pytest.mark.pip_integration
@pytest.mark.singularity_integration
@pytest.mark.parametrize("use_uv", [False, True], ids=["vanilla", "uv"])
def test_env_creation(tmp_path, data_cached_python312_sif, use_uv):
    requirements_path = tmp_path / "requirements.txt"
    requirements_path.write_text("six")  # `six` is small enough to be installed quickly
    with SingularitySandbox(base_image=data_cached_python312_sif) as sandbox:
        conda_install = PipInstall(sandbox=sandbox, use_uv=use_uv)
        conda_install.configure(
            requirements_files=[str(requirements_path)], add_to_env=True
        )
        process = sandbox.run_command_in_container(cmd="pip freeze")
        assert "six==" in process.stdout
