export USERID = $(shell id -u)

CONTAINER_RUN := docker

CONTAINER_TEST_COMMAND="cd /code && uv sync --group=tests && uv run pytest"

CONTAINER_ENTRYPOINT=--entrypoint bash
CONTAINER_INTERNAL_PYTHON_VENV=--tmpfs=/venv:exec
CONTAINER_ENVIRONMENT=--env UV_PROJECT_ENVIRONMENT=/venv
CONTAINER_VOLUME_MOUNT=-v ${PWD}:/code
CONTAINER_TEST_OPTIONS=--privileged $(CONTAINER_ENTRYPOINT) $(CONTAINER_INTERNAL_PYTHON_VENV) $(CONTAINER_ENVIRONMENT) $(CONTAINER_VOLUME_MOUNT)

APPTAINER_URL=ghcr.io/deic-hpc/cotainr-dev_env-apptainer-1.3.4:docker_dev_env_lint
SINGULARITY_URL=ghcr.io/deic-hpc/cotainr-dev_env-singularity-ce-4.3.0:a0799f3dd059e2e1a3b6a7c5025944ebb38c92f01377d499461470f6db43b748

CONTAINER_URL=$(APPTAINER_URL)

podman:
	$(eval CONTAINER_RUN=podman)


#For more details ee: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
login:
	echo $(CR_PAT) | $(CONTAINER_RUN) login ghcr.io -u USERNAME --password-stdin

singularity:
	$(eval CONTAINER_URL=$(SINGULARITY_URL))

apptainer:
	$(eval CONTAINER_URL=$(APPTAINER_URL))

id:
	@echo "test "$$USERID

test:
	$(CONTAINER_RUN) run $(CONTAINER_TEST_OPTIONS) $(CONTAINER_URL) -c $(CONTAINER_TEST_COMMAND)
