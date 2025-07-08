.. _containerized_development_environment:

Containerized development environment
=====================================
The `cotainr` project provides a containerized development environment that can be used to develop and test `cotainr` itself. The containerized development environment is defined in the `Dockerfile <https://github.com/DeiC-HPC/cotainr/blob/main/.github/workflows/dockerfiles/Dockerfile>`_ included in the https://github.com/DeiC-HPC/cotainr repository.

Developers that are part of the https://github.com/DeiC-HPC organization may pull the development containers from the https://github.com/orgs/DeiC-HPC/packages `GitHub Container Registry (GHCR) <https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry>`_. This requires logging into GHCR using the `docker login <https://docs.docker.com/reference/cli/docker/login/>`_ / `podman login <https://docs.podman.io/en/stable/markdown/podman-login.1.html>`_ CLI tool with a `personal access token (classic) <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic>`_ that has at least the `read:packages` scope. Using the `GitHub gh CLI tool <https://cli.github.com/manual/>`_ this may be achieved by running:

.. code-block:: console

    $ gh auth login --scopes read:packages
    $ gh auth token | podman login ghcr.io --username $(gh api user --jq '.login') --password-stdin

Replace `podman` with `docker` in the above command if you use `docker` instead of `podman`.

Automated building of the containers
------------------------------------
The containerized development environment containers are automatically built and pushed to GHCR using the `CI_build_docker_images.yml <https://github.com/DeiC-HPC/cotainr/actions/workflows/CI_build_docker_images.yml>`_ GitHub Action workflow. This workflow uses `the official Docker GitHub Actions <https://docs.docker.com/build/ci/github-actions/>`_ to build the containers for all supported architectures and dependencies as defined in the :ref:`single sourced dependency matrix <single_source_dep_matrix>`.

The workflow is triggered on pushes to the `main` branch, as well as development branches starting with `docker_dev_env`, if the files "defining" the development environment have changed, i.e. if changes are made to the following files:

- `Dockerfile <https://github.com/DeiC-HPC/cotainr/blob/main/.github/workflows/dockerfiles/Dockerfile>`_
- `matrix.json <https://github.com/DeiC-HPC/cotainr/actions/workflows/matrix.json>`_
- `CI_build_docker_images.yml <https://github.com/DeiC-HPC/cotainr/actions/workflows/CI_build_docker_images.yml>`_

A SHA256 checksum of these files, as calculated by the `hashFiles <https://docs.github.com/en/actions/reference/evaluate-expressions-in-workflows-and-actions#hashfiles>`_ function, is used to uniquely identify the "version" of the development environment as defined by these files. The built containers are tagged with this checksum, which allows for identification of the containers that should be used in the :ref:`CI/CD pipelines <continuous_integration>`, i.e. the checksum of the three files on the `main` branch identify the containers that must be used in the CI/CD pipelines for the `main` branch - likewise for other branches. Additionally, the containers are tagged with the branch name (`main` or `docker_dev_env_*`) to make it easier to pull the containers for local development.

Manually building the containers
--------------------------------
If you do not have access to the `cotainr` GHCR or want to build the containers locally, you can do so using the `Dockerfile <https://github.com/DeiC-HPC/cotainr/blob/main/.github/workflows/dockerfiles/Dockerfile>`_. When building the containers locally, you need to provide the SINGULARITY_PROVIDER (`apptainer` or `singularity-ce``) and SINGULARITY_VERSION build arguments to the `docker build <https://docs.docker.com/reference/cli/docker/buildx/build/>`_ / `podman build <https://docs.podman.io/en/stable/markdown/podman-build.1.html>`_ command, e.g. from the `cotainr` repository root directory:

.. code-block:: console

    $ docker build --build-arg SINGULARITY_PROVIDER=apptainer --build-arg SINGULARITY_VERSION=1.3.6 -t cotainr-dev-env:local -f .github/workflows/dockerfiles/Dockerfile .

When using `podman` the command is as follows:

.. code-block:: console

    $ podman build --format=docker --build-arg SINGULARITY_PROVIDER=apptainer --build-arg SINGULARITY_VERSION=1.3.6 -t cotainr-dev-env:local -f .github/workflows/dockerfiles/Dockerfile .

<<<<<<< Updated upstream
The `--format=docker` is needed as the `Dockerfile <https://github.com/DeiC-HPC/cotainr/blob/main/.github/workflows/dockerfiles/Dockerfile>`_ contains bash commands that are not supported by the OCI image format.
=======
The :code:`--format=docker` is needed as the `Dockerfile <https://github.com/DeiC-HPC/cotainr/blob/main/.github/workflows/dockerfiles/Dockerfile>`_ contains bash commands that are not supported by the OCI image format.

>>>>>>> Stashed changes
Running in the containerized development environment
----------------------------------------------------
The containerized development environment includes a singularity container runtime (`apptainer` or `singularity-ce`) and the `uv <https://docs.astral.sh/uv/>`_ Python package manager. At runtime, you need to run :code:`uv sync` to install/update the Python environment to include the dependencies specified in the `pyproject.toml <https://github.com/DeiC-HPC/cotainr/blob/main/pyproject.toml>`_ file to get a fully working development environment.

Synchronizing the `uv` managed Python virtual environment is so fast and cheap that we have opted for doing it every time the container is started instead of building individual container images for all the different Python versions and dependencies specified in the :ref:`single sourced dependency matrix <single_source_dep_matrix>`.

We recommend running the containerized development environment `rootless as a non-root user <https://www.redhat.com/en/blog/rootless-containers-podman>`_ using either `docker <https://docs.docker.com/get-started/>`_ or `podman <https://podman.io/get-started>`_. Since we are running one container runtime (`apptainer` / `singularity-ce`) inside another container runtime (`docker` / `podman`), for this to work, it is in general necessary to:

1. Have unprivileged user namespaces enabled. Generally this means that the `user.max_user_namespaces` kernel parameter must be 1 (or larger) and the `kernel.unprivileged_userns_clone` kernel parameter must be set to 1. This is the default on most modern Linux distributions. Additionally, you must make sure that `the other prerequisites for running rootless <https://docs.docker.com/engine/security/rootless/#prerequisites>`_ are met.
2. Run with at least some of the `docker` / `podman` security options disabled. While it is possible to run with the :code:`--privileged` flag, this disables all security features and is not recommended. Instead, we recommend looking at the suggested security options in the reference :ref:`makefile <dev_env_makefile>` and :ref:`development container <dev_env_devcontainer>` configurations and then try to run with as few of these options as possible.

We provide two reference methods to run the containerized development environment, one for running it in a terminal using a makefile and one for running the container as a `development container <https://containers.dev/>`_ integrated with an IDE.

.. _dev_env_user_id:

A note on the ID of the user running inside the container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The containerized development environment is designed to be run as a non-root user. On most Linux distributions, the default non-root user has user ID 1000. So in the reference :ref:`makefile <dev_env_makefile>` and :ref:`development container <dev_env_devcontainer>` configurations, we assume that you are running as user 1000 and map this user to the user inside the container to avoid permission issues when accessing files on the host system from inside the container.

On the GitHub action runners, used in the :ref:`CI/CD pipelines <continuous_integration>`, the default user has user ID 1001. Consequently, we specify :code:`--user 1001` when running the containerized development environment in the GitHub Actions workflows to avoid subtle permission errors when accessing files on the host system from inside the container, e.g. `accessing the repository clone done by the checkout action <https://github.com/actions/checkout/issues/47>`_. While this rootless setting should theoretically also work for running `apptainer` / `singularity-ce` inside the container on the GitHub action runners, when we need to run `apptainer` / `singularity-ce` in the container on GitHub action runners, we run as the root user with the :code:`--privileged` flag. This is because it is currently `too tedious to disable the apparmor restriction on kernel.unprivileged_userns_clone on GitHub action runners <https://github.com/actions/runner-images/issues/10015>`_ which seems to be necessary for running as a non-root user.

.. _dev_env_makefile:

Using the reference makefile
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We provide a reference `Makefile <https://github.com/DeiC-HPC/cotainr/blob/main/Makefile>`_ that includes targets for using the containerized development environment to run the `cotainr` :ref:`test suite <test_suite>` as well as build the :ref:`reference documentation <reference_docs>`. It should generally work with both `docker` and `podman`, on most Linux distributions, though you may have to adjust it to your specific environment :ref:`if your local user does not have user ID 1000 <dev_env_user_id>` or if you want to limit the `docker` / `podman` security options that are disabled. Run :code:`make help` for more details on the available targets.

.. _dev_env_devcontainer:

Using the IDE development container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We provide a reference `devcontainer.json <https://github.com/DeiC-HPC/cotainr/blob/main/.devcontainer/devcontainer.json>`_ file that includes the necessary configuration to run the containerized development environment as a `development container <https://containers.dev/>`_ integrated with an IDE. The `devcontainer.json` file is mainly designed for use with `Visual Studio Code <https://code.visualstudio.com/docs/remote/containers>`_ with rootless `podman` as the container runtime. For this to work, you need to install the `Dev Containers extension <https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers>`_ and set the :code:`dev.containers.dockerPath` setting to :code:`podman` in your `Visual Studio Code settings <https://code.visualstudio.com/docs/configure/settings>`_.

.. admonition:: The development container setup is work-in-progress
    :class: warning

    The IDE development container setup is still work-in-progress. It may not work as expected for all combinations of OS'es, IDEs, and container runtimes. It may still need further configuration to fully integrate with Visual Studio Code or other IDEs.
