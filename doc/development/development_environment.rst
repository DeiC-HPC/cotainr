.. _containerized_development_environment:

Containerized development environment
=====================================
The `cotainr` project provides a containerized development environment that can be used to develop and test `cotainr` itself. This environment is built using `Docker <https://www.docker.com/>`_ and is defined in the `Dockerfile <https://github.com/DeiC-HPC/cotainr/blob/main/.github/workflows/dockerfiles/Dockerfile>`_.


Runs the docker build process. The Dockerfile used for the building can be found `here <https://github.com/DeiC-HPC/cotainr/actions/workflows/dockerfiles/Dockerfile>`_

We build docker images for *all* supported architectures (AMD64 & ARM), *relevant* Singularity-CE as well as *relevant* Apptainer versions. Python is not installed during the build process but is installed during the test process.


All workflows are run on docker images build by the `CI_build_docker_images.yml` pipeline. The Docker images are stored on the Github Container Registry (`ghcr <https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry>`_).



The CI utilizes `reusable workflows <https://docs.github.com/en/actions/sharing-automations/reusing-workflows>`_ in frequently used helper scripts and in other workflows that has multiple use-cases.


- `Container-inputs.yml`: Extracts the required variables for running jobs on the correct docker image. This extracts the relevant part from the single source `matrix.json` to be used in the other workflows. Additionally, the workflow returns the GitHub repository name in lowercase as required by the GHCR repository and the SHA of `matrix.json`, `Dockerfile` and `CI_Build_docker_images.yml` to ensure the correctness of the container version.
- `CI_push.yml`: The push tests are both utilized by itself on the push action and in `CI_build_docker_images.yml` after a new docker build.


Running in the containerized development environment
----------------------------------------------------


Using the reference makefile
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As an IDE development container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
