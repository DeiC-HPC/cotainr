import subprocess

import pytest


@pytest.fixture(scope="session")
def data_cached_alpine_sif(tmp_path_factory):
    singularity_image_path = (
        tmp_path_factory.mktemp("singularity_images") / "alpine_latest.sif"
    )
    subprocess.run(
        args=[
            "singularity",
            "pull",
            f"{singularity_image_path.resolve()}",
            "docker://alpine:latest",
        ],
        capture_output=True,
        check=True,
        text=True,
    )

    return singularity_image_path


@pytest.fixture(scope="session")
def data_cached_ubuntu_sif(tmp_path_factory):
    singularity_image_path = (
        tmp_path_factory.mktemp("singularity_images") / "ubuntu_latest.sif"
    )
    subprocess.run(
        args=[
            "singularity",
            "pull",
            f"{singularity_image_path.resolve()}",
            "docker://ubuntu:latest",
        ],
        capture_output=True,
        check=True,
        text=True,
    )

    return singularity_image_path
