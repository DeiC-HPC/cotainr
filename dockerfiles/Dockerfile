FROM ubuntu:latest
LABEL authors="julius"

ENTRYPOINT ["top", "-b"]

ENV DEBIAN_FRONTEND=noninteractive
RUN set -eux ; \
    apt -y update ;\
    apt -y upgrade ;\
    apt -y install wget

ARG SINGULARITY_PROVIDER
ENV SINGULARITY_PROVIDER=${SINGULARITY_PROVIDER}

ARG SINGULARITY_VERSION
ENV SINGULARITY_VERSION=${SINGULARITY_VERSION}

RUN echo $SINGULARITY_PROVIDER
RUN echo $SINGULARITY_VERSION

RUN set -eux ; \
    if [ "$SINGULARITY_PROVIDER" = "apptainer" ]; then \
#        echo "match apptainer" ;\
        wget -O singularity_installer.deb https://github.com/apptainer/apptainer/releases/download/v${SINGULARITY_VERSION}/apptainer_${SINGULARITY_VERSION}_amd64.deb ;\
    fi; \
    if [ "$SINGULARITY_PROVIDER" = "singularity" ]; then \
        wget -O singularity_installer.deb https://github.com/apptainer/singularity/releases/download/v${SINGULARITY_VERSION}/singularity-container_${SINGULARITY_VERSION}_amd64.deb ;\
    fi;\
    apt -y install ./singularity_installer.deb ;\
    singularity --version


