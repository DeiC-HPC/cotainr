FROM python:3.12

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
USER cotainr
ENV PATH="/home/cotainr/bin:$PATH"