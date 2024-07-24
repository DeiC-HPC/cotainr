"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import pathlib
import subprocess

import pytest


def _pull_image(image_name: str, target_path: pathlib.Path) -> pathlib.Path:
    subprocess.run(
        args=[
            "singularity",
            "pull",
            f"{target_path}",
            f"docker://{image_name}",
        ],
        capture_output=True,
        check=True,
        text=True,
    )
    assert target_path.exists()
    return target_path


@pytest.fixture(scope="session")
def data_cached_alpine_sif(tmp_path_factory):
    """A session scope cached SIF image of the latest alpine linux container."""
    return _pull_image(
        "alpine:latest",
        tmp_path_factory.mktemp("singularity_images") / "alpine_latest.sif",
    )


@pytest.fixture(scope="session")
def data_cached_ubuntu_sif(tmp_path_factory):
    """A session scope cached SIF image of the latest ubuntu linux container."""
    return _pull_image(
        "ubuntu:latest",
        tmp_path_factory.mktemp("singularity_images") / "ubuntu_latest.sif",
    )


@pytest.fixture(scope="session")
def data_cached_python312_sif(tmp_path_factory):
    """A session scope cached SIF image of the latest Python 3.12 container."""
    return _pull_image(
        "python:3.12-slim",
        tmp_path_factory.mktemp("singularity_images") / "python312_latest.sif",
    )
