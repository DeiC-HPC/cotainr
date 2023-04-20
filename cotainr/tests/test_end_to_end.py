"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import shlex

import pytest

from cotainr.cli import CotainrCLI
from cotainr import __version__ as _cotainr_version
from .container.data import data_cached_ubuntu_sif


@pytest.mark.endtoend
def test_conda_env_build(
    data_cached_ubuntu_sif, singularity_exec, singularity_inspect, tmp_path
):
    """Test build command when including simple conda environment."""
    build_container_path = tmp_path / "conda_container.sif"
    conda_env_path = tmp_path / "conda_env.yml"
    conda_env_path.write_text("channels:\n  - conda-forge\ndependencies:\n  - python")

    CotainrCLI(
        args=shlex.split(
            f"build {build_container_path} "
            f"--base-image={data_cached_ubuntu_sif} "
            f"--conda-env={conda_env_path}"
        )
    ).subcommand.execute()

    container_metadata = singularity_inspect(build_container_path).stdout.split("\n")
    assert f"cotainr.version: {_cotainr_version}" in container_metadata
    assert "cotainr.url: https://github.com/DeiC-HPC/cotainr" in container_metadata
    assert any(datum.startswith("cotainr.command: ") for datum in container_metadata)

    container_python_process = singularity_exec(
        f"{build_container_path} python3 -c 'import sys; print(sys.executable)'"
    )
    for conda_identifier in ["conda", "/envs/"]:
        assert conda_identifier in container_python_process.stdout
