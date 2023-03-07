ARG BASE_IMAGE=ubuntu:focal-20221130
FROM ${BASE_IMAGE}

# BASIC LIBRARIES
ENV DEBIAN_FRONTEND="noninteractive" TZ="Europe/London"
RUN apt-get update && \
    apt-get install -y git wget sudo cmake libncurses5-dev libncursesw5-dev build-essential ffmpeg libsm6 libxext6 acl && \
    apt-get clean

# MINICONDA3 INSTALL
ARG CONDA_DIR='/opt/conda'
ARG CONDA_ENV_NAME='foobar'

ENV CONDA_DIR=$CONDA_DIR
ENV CONDA_ENV_NAME=$CONDA_ENV_NAME
ENV CONDA_BIN_PATH $CONDA_DIR/condabin/conda
ENV PATH=$CONDA_DIR/condabin/:$PATH
ENV CONDA_ENV_BIN_PATH $CONDA_DIR/envs/${CONDA_ENV_NAME}/bin
COPY environment.yml /tmp/environment.yml

RUN line_num=$(cat /etc/pam.d/common-session | grep -n umask | cut -d: -f1 | tail -1) && \
    sed -i "${line_num}s/.*/session optional pam_umask.so umask=000/" /etc/pam.d/common-session

RUN line_num=$(cat /etc/login.defs | grep -n UMASK | cut -d: -f1 | tail -1) && \
    sed -i "${line_num}s/.*/UMASK               000/" /etc/pam.d/common-session
RUN echo 'umask 000' >> ~/.profile


RUN groupadd conda_env
RUN umask 000 && \
    mkdir -p ${CONDA_DIR} && \
    chmod 777 ${CONDA_DIR} && \
    wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -ub -p $CONDA_DIR && \
    rm ~/miniconda.sh

# CONDA ENV CREATION
RUN umask 000 && \
    conda update -n base conda && \ 
    conda create -y -n $CONDA_ENV_NAME && \
    conda env update --name $CONDA_ENV_NAME --file /tmp/environment.yml --prune 

# PYTORCH INSTALL
RUN $CONDA_ENV_BIN_PATH/pip install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html

# # OPEN-CV INSTALL
# RUN $CONDA_ENV_BIN_PATH/pip install opencv-python opencv-contrib-python

# RUN $CONDA_ENV_BIN_PATH/pip install sphinx sphinxcontrib-packages pybtex jupyter-book fonttools importlib-metadata ipykernel ipython jupyterlab-mathjax3 kaleido pillow scikit-image

# # NVTOP INSTALL
# RUN cd /tmp \
#     && git clone https://github.com/Syllo/nvtop.git \
#     && mkdir -p nvtop/build && cd nvtop/build \
#     && cmake .. -DNVIDIA_SUPPORT=ON -DAMDGPU_SUPPORT=OFF -DINTEL_SUPPORT=OFF \
#     && make install

# # HTOP INSTALL
# RUN apt-get install -y htop

# # LOCALES UPDATE
# RUN apt install locales && \
#     locale-gen en_US.UTF-8 && \
#     dpkg-reconfigure locales

# COPY tests /tmp/tests

# # # RUN apt-get update && \
# # #     apt-get -y upgrade && \
# # #     apt-get -y install curl dirmngr apt-transport-https lsb-release ca-certificates && \
# # #     curl -sL https://deb.nodesource.com/setup_12.x | bash -

# RUN apt-get -y remove nodejs
# RUN apt-get -y install nodejs
# RUN apt -y install npm

RUN echo ". ${CONDA_DIR}/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "${CONDA_BIN_PATH} activate $CONDA_ENV_NAME" >> ~/.bashrc

SHELL ["/bin/bash", "--login", "-c"]


