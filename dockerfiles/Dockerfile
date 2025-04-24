FROM ubuntu:latest
LABEL authors="julius"

ENTRYPOINT ["top", "-b"]

ARG SINGULARITY_PROVIDER
ENV SINGULARITY_PROVIDER=${SINGULARITY_PROVIDER}
ARG SINGULARITY_VERSION
ENV SINGULARITY_VERSION=${SINGULARITY_VERSION}

ENV DEBIAN_FRONTEND=noninteractive

#everything after golang is needed by singularity-ce
RUN set -eux ; \
    apt-get update;\
    apt-get install -y \
        build-essential \
        libseccomp-dev \
        uidmap \
        fakeroot \
        cryptsetup \
        tzdata \
        dh-apparmor \
        curl wget git \
        libsubid-dev \
        golang \
        autoconf \
        automake \
        fuse2fs \
        fuse \
        libfuse-dev \
        libtool \
        runc \
        squashfs-tools \
        squashfs-tools-ng \
        zlib1g-dev\
        libglib2.0-dev        

# Download apptainer/singularity
RUN set -eux ; \
    if [ "$SINGULARITY_PROVIDER" = "apptainer" ]; then \
        wget -O singularity_installer.tar.gz https://github.com/apptainer/apptainer/releases/download/v${SINGULARITY_VERSION}/apptainer-${SINGULARITY_VERSION}.tar.gz;\
    fi; \
    if [ "$SINGULARITY_PROVIDER" = "singularity-ce" ]; then \
        wget -O singularity_installer.tar.gz https://github.com/sylabs/singularity/releases/download/v${SINGULARITY_VERSION}/singularity-ce-${SINGULARITY_VERSION}.tar.gz;\
    fi

RUN set -eux;\
    mkdir singularity;\
    tar -xf singularity_installer.tar.gz --strip-components=1 -C /singularity;\
    cd singularity;\
    ./mconfig --without-suid;\
    cd ./builddir;\
    make;\
    make install

RUN set -eux;\
    singularity --version
