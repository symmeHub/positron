#!/bin/bash
echo "Start Devcontainer post-command process !"

#cd ../workspace/
# echo "Installing pre-commit"
# echo $CONDA_ENV
# ${CONDA_ENV_PATH}pre-commit install
# ${CONDA_ENV_PATH}pre-commit install-hooks
# echo "Devcontainer post-command process done !"

echo "Running unit tests"
/opt/conda/envs/awesome/bin/pytest /tmp/tests


echo "Installing custom packages from my_environment.yml file."
if [ -e /tmp/my_environment.yml ]
then
    sudo ${CONDA_BIN_PATH} env update --file /tmp/my_environment.yml
else
    echo "no my_environment.yml file"
fi

echo "Terminated"
