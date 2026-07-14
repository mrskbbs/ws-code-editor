FROM gcc:latest

USER root
WORKDIR /
SHELL ["/bin/bash", "-c"]
RUN mkdir /sandbox
RUN chown root:root /sandbox
RUN chmod 0755 /sandbox

WORKDIR /sandbox
