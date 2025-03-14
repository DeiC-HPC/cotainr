

tests:
	docker run --privileged --entrypoint bash --tmpfs=/venv:exec --env UV_PROJECT_ENVIRONMENT=/venv -v ${PWD}:/code ghcr.io/deic-hpc/cotainr/apptainer/1.3.4/3.10:docker_dev_env -c "cd /code && uv sync && source /venv/bin/activate && uv pip install .[dev] && pytest"
