"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import subprocess

import pytest


@pytest.fixture(scope="session")
def data_cached_alpine_sif(tmp_path_factory):
    """A session scope cached SIF image of the latest alpine linux container."""
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
    assert singularity_image_path.exists()

    return singularity_image_path


@pytest.fixture(scope="session")
def data_cached_ubuntu_sif(tmp_path_factory):
    """A session scope cached SIF image of the latest ubuntu linux container."""
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
    assert singularity_image_path.exists()

    return singularity_image_path
