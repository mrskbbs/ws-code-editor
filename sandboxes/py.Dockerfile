FROM python:latest

USER root
WORKDIR /
SHELL ["/bin/bash", "-c"]
RUN useradd --create-home -s /bin/bash -u 1000 sandbox

WORKDIR /home/sandbox
USER sandbox
