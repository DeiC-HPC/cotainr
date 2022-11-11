import pytest

from cotainr.cli import Build
from .container.data import data_cached_ubuntu_sif


@pytest.mark.endtoend
def test_conda_env_build(data_cached_ubuntu_sif, singularity_exec, tmp_path):
    """Test build command when including simple conda environment."""
    build_container_path = tmp_path / "conda_container.sif"
    conda_env_path = tmp_path / "conda_env.yml"
    conda_env_path.write_text("channels:\n  - conda-forge\ndependencies:\n  - python")

    build = Build(
        image_path=build_container_path,
        base_image=data_cached_ubuntu_sif,
        conda_env=conda_env_path,
    )
    build.execute()

    container_python_process = singularity_exec(
        f"{build_container_path} python -c 'import sys; print(sys.executable)'"
    )
    for conda_identifier in ["conda", "/envs/"]:
        assert conda_identifier in container_python_process.stdout
