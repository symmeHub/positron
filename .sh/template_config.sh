#!/bin/bash
#  Conda parameters 
export CONDA_ENV=jupyter_book

# Git forge parameters
export GIT_FORGE_USERNAME=elmokulc
export GIT_FORGE_REPO_NAME=positron

#  Registry parameters
export DOCKER_REGISTRY_URL=ghcr.io
export DOCKER_REGISTRY_USERNAME=elmokulc
export DOCKER_REGISTRY_GROUP=symmehub
export IMAGE_NAME=positron
export TAG=latest
export BROWSER=firefox
# if DOCKER_REGISTRY_GROUP not empty 
export REPO_REGISTRY=$(DOCKER_REGISTRY_URL)/$(DOCKER_REGISTRY_GROUP)/$(GIT_FORGE_REPO_NAME)
# else
# export REPO_REGISTRY=$(DOCKER_REGISTRY_URL)/$(DOCKER_REGISTRY_USERNAME)

