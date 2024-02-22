# POSITRON: PythOn for Science In The Reblochon cOuNtry

Welcome to you in Positron. This repository is intended to gather documents, mainly Jupyter notebooks as teaching aids for digital methods. In order to keep the repository free of unnecessary files and hard-to-read commits, it is mandatory to follow the following guidelines:

The associated book is available online here: 

- Github : https://symmehub.github.io/positron/intro.html

## Devcontainer

This repository is designed to be used with a devcontainer. To use it, you need to have acces to Docker (locally or remotely) and Visual Studio Code installed on your computer. The devcontainer relies on the base image defined in https://github.com/symmeHub/symme_docker_images/tree/main/src/scientific_python . If not already done, you need to build the base image before building the devcontainer.


## Pre-commit
Before playing, you need to activate **pre-commit** in your environment:

``` bash
pre-commit install
```

## Book building and publishing
To build the book and test it locally, run the following command from the root folder:

``` bash
jupyter-book build book
```

Sometimes it is necessary to clean the book build folder with it:

``` bash
jupyter-book clean book
```

<!-- To publish the book once it has been tested and validated by you:

``` bash
ghp-import -n -p -f book/_build/html
``` -->

## Update Online Book

To update the online Book, you need to trigger de CI/CD. Two options are available here :

1. Add key **[ci-run]** to your commit message.

    Example :

            git commit -am "[ci-run] This is an example commit to trigger CI"

2. Triggering from CI/CD from web. 

- If  Gitlab :

    - Go to: https://gitlab.com/symmehub/teaching/positron >> CI/CD/ >> ***Run pipeline***
