.. _docker_dev_env_vsc:

Docker Dev Env in VS Code
=========================

Resources:
https://code.visualstudio.com/docs/devcontainers/containers

- Docker installation
- VS Code installation
- Install the Dev Containers extension (https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- Docker pull the dev enironment image from ghcr
- Adjust the `.devcontainer/devcontainer.json` to reflect the image you pulled
- There is possibly a pop up prompting you to rebuild the container. Accept.
- Hit `F1` and use `Dev Containers: Open Folder in Container`

To run test suit:
- `uv python install 3.9`
- `uv sync --python 3.9 --group=tests --frozen`
- `uv run pytest -vv -m "not endtoend and not singularity_integration and not conda_integration"`

Replace with the right Python version.

All tests should pass.

Issues:
-------

- pre-commit doesnt work in container --> needed in the dev container?
- Files created in the dev container are currently root:root --> https://github.com/microsoft/vscode-remote-release/issues/49
