CONTAINER_RUN=docker

TESTFLAGS=
CONTAINER_TEST_COMMAND=cd /home/ubuntu/code && uv sync --group=tests && uv run pytest
CONTAINER_DOC_COMMAND=cd /home/ubuntu/code/doc && uv sync --group docs && uv run make apidoc && uv run make relnotes && uv run make html


CONTAINER_ENTRYPOINT=--entrypoint bash
CONTAINER_INTERNAL_PYTHON_VENV=--tmpfs=/venv:exec
CONTAINER_ENVIRONMENT=--env UV_PROJECT_ENVIRONMENT=/venv
CONTAINER_VOLUME_MOUNT=-v ${PWD}:/home/ubuntu/code
CONTAINER_USER_ID=1000
CONTAINER_SECURITY_OPTIONS=--security-opt label=disable --security-opt systempaths=unconfined --security-opt seccomp=unconfined --security-opt apparmor=unconfined
CONTAINER_OPTIONS=--rm -it --user=$(CONTAINER_USER_ID) $(CONTAINER_SECURITY_OPTIONS) $(CONTAINER_ENTRYPOINT) $(CONTAINER_INTERNAL_PYTHON_VENV) $(CONTAINER_ENVIRONMENT) $(CONTAINER_VOLUME_MOUNT) $(OPTIONAL)

APPTAINER_URL=ghcr.io/deic-hpc/cotainr-dev_env-apptainer-1.3.6:main
SINGULARITY_URL=ghcr.io/deic-hpc/cotainr-dev_env-singularity-ce-4.3.0:main

CONTAINER_URL=$(APPTAINER_URL)

HELP_OUTPUT=" Welcome to the cotainr makefile\n\
This is to help you easily test cotainr\n\
\n\
The default way of running cotainr is by using 'make test'\n\
We have a list of different goals defined to help out:\n\
\n\
help: prints this output\n\
login: helps you login to the container registry\n\
\n\
Execution goals that are executed in the container\n\
test: executes the cotainr test-suite in a container\n\
docs: build the cotainr documentation in a container\n\
\n\
Environments goals that are defined before the execution goal to setup the environment\n\
podman: changes the cotainer runner from docker to podman\n\
singularity: changes the container to one containing singularity\n\
apptainer: changes the container to one containing apptainer (default)\n\
\n\
Runtime environment flags can be provided in any order\n\
TESTFLAGS: string that is parsed to pytest, e.g. TESTFLAGS='-k test_info.py'\n\
"

.PHONY:default help podman login singularity apptainer test docs
default: test

help:
	@echo $(HELP_OUTPUT)

podman:
	$(eval OPTIONAL=--userns=keep-id)
	$(eval CONTAINER_RUN=podman)

login:
	@echo "For more details on how to login to the github container registry see: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry";\
	read -p "Enter Github username:" USERNAME;\
	echo "Username: "$$USERNAME;\
	read -p "Enter Github token:" CR_PAT;\
	read -p "Enter Github password:" -s PASS;\
	echo $$CR_PAT | $(CONTAINER_RUN) login ghcr.io -u $$USERNAME -p $$PASS

singularity:
	$(eval CONTAINER_URL=$(SINGULARITY_URL))

apptainer:
	$(eval CONTAINER_URL=$(APPTAINER_URL))

test:
	$(eval CONTAINER_COMMAND="$(CONTAINER_TEST_COMMAND) $(TESTFLAGS)")
	$(call execute)

docs:
	$(eval CONTAINER_COMMAND="$(CONTAINER_DOC_COMMAND)")
	$(call execute)

execute = $(CONTAINER_RUN) run $(CONTAINER_OPTIONS) $(CONTAINER_URL) -c $(CONTAINER_COMMAND)
