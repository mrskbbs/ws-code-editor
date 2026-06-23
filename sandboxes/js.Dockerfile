FROM node:latest

USER root
WORKDIR /
SHELL ["/bin/bash", "-c"]
RUN deluser node
RUN useradd --create-home -s /bin/bash -u 1000 sandbox

WORKDIR /home/sandbox
USER sandbox
