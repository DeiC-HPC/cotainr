FROM ubuntu:latest
LABEL authors="julius"

ENTRYPOINT ["top", "-b"]

ARG SINGULARITY_PROVIDER
ENV SINGULARITY_PROVIDER=${SINGULARITY_PROVIDER}
ARG SINGULARITY_VERSION
ENV SINGULARITY_VERSION=${SINGULARITY_VERSION}

ENV DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-c"]

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

# just hardcoded the goversion for now to the latest. the script below extracts the min required go version from the mconfig file.
# However, singularity-ce ommits the minor version in the mconfig file so the download fails.
# export GOVERSION=$(grep -re 'hstgo_version=' mconfig | sed 's/.*"\(.*\)".*/\1/');\
# Todo: the if for the arch is a bit questionable atm.
RUN set -eux;\
    export OS=linux;\
    export GOVERSION=1.24.0;\
    [[ "$(uname -m)" == 'x86_64' || "$(uname -m)" == 'AMD64'  || "$(uname -m)" == 'amd64' ]] && export ARCH=amd64 || export ARCH=arm64;\
    echo $ARCH;\
    wget -O /tmp/go${GOVERSION}.${OS}-${ARCH}.tar.gz \
        https://dl.google.com/go/go${GOVERSION}.${OS}-${ARCH}.tar.gz;\
    tar -C /usr/local -xzf /tmp/go${GOVERSION}.${OS}-${ARCH}.tar.gz

ENV PATH=$PATH:/usr/local/go/bin

RUN set -eux;\
    mkdir singularity;\
    tar -xzf singularity_installer.tar.gz --strip-components=1 -C /singularity;\
    cd singularity;\
    ./mconfig --without-suid;\
    cd ./builddir;\
    make;\
    make install

RUN set -eux;\
    singularity --version
