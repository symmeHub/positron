FROM continuumio/miniconda3:latest
LABEL org.opencontainers.image.source https://github.com/symmehub/positron
SHELL ["/bin/bash", "--login", "-c"]
RUN apt update -y && \
    apt install ffmpeg -y 
ADD environment.yml /tmp/environment.yml
RUN conda env update -f /tmp/environment.yml --prune
