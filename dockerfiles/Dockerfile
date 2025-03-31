FROM fedora:latest
LABEL authors="tor, julius"

ENTRYPOINT ["top", "-b"]

ARG SINGULARITY_PROVIDER
ENV SINGULARITY_PROVIDER=${SINGULARITY_PROVIDER}
ARG SINGULARITY_VERSION
ENV SINGULARITY_VERSION=${SINGULARITY_VERSION}

ENV DEBIAN_FRONTEND=noninteractive
RUN set -eux ; \
    dnf upgrade --refresh -y; \
    dnf install -y uv;\
    dnf install -y $SINGULARITY_PROVIDER-$SINGULARITY_VERSION;\
    singularity --version

#ARG PYTHON_VERSION
#ENV PYTHON_VERSION=${PYTHON_VERSION}
#
#RUN set -eux ; \
#    uv python install $PYTHON_VERSION

