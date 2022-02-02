FROM continuumio/miniconda3:latest

SHELL ["/bin/bash", "--login", "-c"]

ADD environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml

# Pull the environment name out of the environment.yml
RUN echo "source activate $(head -1 /tmp/environment.yml | cut -d' ' -f2)" > ~/.bashrc
ENV PATH /usr/local/envs/$(head -1 /tmp/environment.yml | cut -d' ' -f2)/bin:$PATH

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "$(head -1 /tmp/environment.yml | cut -d' ' -f2)", "/bin/bash", "-c"]
