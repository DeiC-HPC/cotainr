import subprocess

import pytest

from cotainr.cli import Build
from cotainr.tests.container.data import data_singularity_ubuntu_image


@pytest.mark.endtoend
def test_conda_env_build(data_singularity_ubuntu_image, tmp_path):
    """Test build command when including simple conda environment."""
    build_container_path = tmp_path / "conda_container.sif"
    conda_env_path = tmp_path / "conda_env.yml"
    conda_env_path.write_text("channels:\n  - conda-forge\ndependencies:\n  - python")

    build = Build(
        image_path=build_container_path,
        base_image=data_singularity_ubuntu_image,
        conda_env=conda_env_path,
    )
    build.execute()

    # TODO: refactor "singularity exec" as a fixture
    container_python_version_process = subprocess.run(
        [
            "singularity",
            "exec",
            f"{build_container_path}",
            "python",
            "-c",
            "import sys; print(sys.version)",
        ],
        capture_output=True,
        check=True,
        text=True,
    )

    # TODO: check conda_env.yml python note base env version
    assert "conda-forge" in container_python_version_process.stdout
