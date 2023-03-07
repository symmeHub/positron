ARG BASE_IMAGE=positron:beta
FROM ${BASE_IMAGE}

# ARGS
ARG USER_NAME
ARG USER_UID
ARG USER_GID
ARG CONDA_ENV_NAME

# ENV VARIABLES
ENV USER_NAME=${USER_NAME}
ENV USER_GID=${USER_GID}
ENV USER_UID=${USER_UID}
ENV CONDA_ENV_NAME=${CONDA_ENV_NAME}
ENV CONDA_ENV_PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin/

# POST-COMMAND FILES
COPY ./postCreateCommands.sh /tmp/postCreateCommands.sh
# COPY ./environment.yml /tmp/environment.yml
COPY ./my_environment.yml /tmp/my_environment.yml


# USER CREATION
RUN groupadd --gid $USER_GID $USER_NAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USER_NAME

RUN echo $USER_NAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USER_NAME \
    && chmod 0440 /etc/sudoers.d/$USER_NAME

RUN cd / && mkdir python_packages

RUN usermod -a -G conda_env ${USER_NAME}
RUN usermod -a -G root ${USER_NAME}

# Log as $USER and create a .bashrc file for config
USER ${USER_UID}:${USER_GID}

RUN echo ". ${CONDA_DIR}/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate $CONDA_ENV_NAME" >> ~/.bashrc && \
    echo "export PYTHONPATH=\$PYTHONPATH:/python_packages/" >> ~/.bashrc

SHELL ["/bin/bash", "--login", "-c"]
RUN /bin/bash ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]
ENTRYPOINT ["/bin/bash"]
