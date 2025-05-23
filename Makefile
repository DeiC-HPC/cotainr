CONTAINER_RUN=docker

CONTAINER_TEST_COMMAND="cd /home/ubuntu/code && ls -alh && uv sync --group=tests && uv run pytest"
CONTAINER_DOC_COMMAND="cd /home/ubuntu/code/doc &&  uv sync --group docs && uv run make apidoc && uv run make relnotes && uv run make html"


CONTAINER_ENTRYPOINT=--entrypoint bash
CONTAINER_INTERNAL_PYTHON_VENV=--tmpfs=/venv:exec
CONTAINER_ENVIRONMENT=--env UV_PROJECT_ENVIRONMENT=/venv
CONTAINER_VOLUME_MOUNT=-v ${PWD}:/home/ubuntu/code
CONTAINER_USER_ID=1000
CONTAINER_SECURITY_OPTIONS=--security-opt label=disable --security-opt systempaths=unconfined --security-opt seccomp=unconfined --security-opt apparmor=unconfined
CONTAINER_TEST_OPTIONS=--rm -it --user=$(CONTAINER_USER_ID) $(CONTAINER_SECURITY_OPTIONS) $(CONTAINER_ENTRYPOINT) $(CONTAINER_INTERNAL_PYTHON_VENV) $(CONTAINER_ENVIRONMENT) $(CONTAINER_VOLUME_MOUNT)

APPTAINER_URL=ghcr.io/deic-hpc/cotainr-dev_env-apptainer-1.3.4:docker_dev_env_lint
SINGULARITY_URL=ghcr.io/deic-hpc/cotainr-dev_env-singularity-ce-4.3.0:docker_dev_env_lint

CONTAINER_URL=$(APPTAINER_URL)

default: test

podman:
	$(eval CONTAINER_RUN=podman)


#For more details ee: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
login:
	echo $(CR_PAT) | $(CONTAINER_RUN) login ghcr.io -u USERNAME --password-stdin

singularity:
	$(eval CONTAINER_URL=$(SINGULARITY_URL))

apptainer:
	$(eval CONTAINER_URL=$(APPTAINER_URL))

test:
	$(eval CONTAINER_COMMAND=$(CONTAINER_TEST_COMMAND))
	$(call execute)

docs:
	$(eval CONTAINER_COMMAND=$(CONTAINER_DOC_COMMAND))
	$(call execute)

execute = $(CONTAINER_RUN) run $(CONTAINER_TEST_OPTIONS) $(CONTAINER_URL) -c $(CONTAINER_COMMAND)
