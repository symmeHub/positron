# Filename: <Makefile>
# Copyright (C) <2022> Authors: <Christian Elmo>
# 
# This program is free software: you can redistribute it and / or 
# modify it under the terms of the GNU General Public License as published 
# by the Free Software Foundation, either version 2 of the License. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of  
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the  
# GNU General Public License for more details.  
# 
# You should have received a copy of the GNU General Public License  
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

path = docker
SHELL := /bin/bash
include ./.sh/config.sh


update: env-exp img-update

web-build: 
	git commit --allow-empty -m "[ci-run] Build Website authored by ${GIT_FORGE_USERNAME}"
	git push origin main

book-build:
	eval "$$(conda shell.bash hook)" && \
	conda activate $(CONDA_ENV) && \
	jupyter-book build book

book-clean:
	eval "$$(conda shell.bash hook)" && \
	conda activate $(CONDA_ENV) && \
	jupyter-book clean book --all

book-open:
	$(BROWSER) book/_build/html/index.html

env-exp:
	@echo "Exporting conda environment from \"$(CONDA_ENV)\" as YAML file" ; \
	eval "$$(conda shell.bash hook)" && \
	conda activate $(CONDA_ENV) && \
	conda env export | sed 's/name: .*/name: base/'  | sed 's/prefix: .*//' > environment.yml ; \
	echo "File exporteds as \"./environment.yml\" " ; \

img-update:
	@echo "Update image" ; \
	docker build -t $(REPO_REGISTRY)/$(IMAGE_NAME):$(TAG) . ;\
	echo "Pushing image" ; \
	docker push $(REPO_REGISTRY)/$(IMAGE_NAME):$(TAG)

log-registry:
	@echo "Please make sure that you already log this machine with your set registry"
	@docker login $(DOCKER_REGISTRY_URL)

infos:
	@echo "Conda parameters ========================================"
	@echo "CONDA_ENV = $(CONDA_ENV)"
	@echo "Git forge parameters ===================================="
	@echo "GIT_FORGE_USERNAME = $(GIT_FORGE_USERNAME)"
	@echo "Registry parameters ====================================="
	@echo "DOCKER_REGISTRY_URL = $(DOCKER_REGISTRY_URL)"
	@echo "DOCKER_REGISTRY_USERNAME = $(DOCKER_REGISTRY_USERNAME)"
	@echo "IMAGE_NAME = $(IMAGE_NAME)"
	@echo "TAG = $(TAG)"
	@echo "Repository parameters ====================================="
	@echo "REPO_REGISTRY = ${REPO_REGISTRY}"





