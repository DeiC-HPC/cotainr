FROM python:3.12 AS python-base

RUN apt-get update -y
RUN passwd --delete root
RUN adduser cotainr --disabled-password --gecos ""

RUN pip install pip --upgrade
COPY test-requirements.txt /tmp/requirements/test-requirements.txt
COPY docs-requirements.txt /tmp/requirements/docs-requirements.txt
RUN pip install -r /tmp/requirements/test-requirements.txt
RUN pip install -r /tmp/requirements/docs-requirements.txt

WORKDIR /home/cotainr
COPY . /home/cotainr/
USER root
ENV PATH="/home/cotainr/bin:$PATH"

FROM python-base AS go-base

RUN apt-get update
RUN apt-get install -y build-essential \
    uuid-dev \
    libgpgme-dev \
    squashfs-tools \
    libseccomp-dev \
    wget \
    pkg-config \
    git \
    cryptsetup-bin

RUN export VERSION=1.17.6 OS=linux ARCH=amd64 && \
    wget https://dl.google.com/go/go$VERSION.$OS-$ARCH.tar.gz && \
    tar -C /usr/local -xzvf go$VERSION.$OS-$ARCH.tar.gz && \
    rm go$VERSION.$OS-$ARCH.tar.gz

ENV GOPATH="/home/cotainr/go"
ENV PATH="/usr/local/go/bin:$PATH:/home/cotainr/go/bin"

FROM go-base AS singularity

# adjust this as necessary
RUN export VERSION=3.8.7 && \
    wget https://github.com/hpcng/singularity/releases/download/v${VERSION}/singularity-${VERSION}.tar.gz && \
    tar -xzf singularity-${VERSION}.tar.gz
WORKDIR /home/cotainr/singularity-3.8.7
RUN ./mconfig
RUN make -C ./builddir
RUN make -C ./builddir install
WORKDIR /home/cotainr
