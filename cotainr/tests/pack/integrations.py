import pytest


@pytest.fixture(
    params=[
        pytest.param("conda_only", marks=pytest.mark.conda_integration),
        pytest.param(
            "conda_and_singularity",
            marks=(pytest.mark.conda_integration, pytest.mark.singularity_integration),
        ),
    ]
)
def integration_conda_singularity(request):
    """
    Handle integration to conda and singularity.

    This fixture parameterizes testing of integration to conda alone as well as
    integration to conda and singularity at the same time.
    """
    if request.param == "conda_only":
        return request.getfixturevalue("patch_singularity_sandbox_subprocess_runner")
