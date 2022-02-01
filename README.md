# POSITRON: PythOn for Science In The Reblochon cOuNtry

Welcome to you in Positron. This repository is intended to gather documents, mainly Jupyter notebooks as teaching aids for digital methods. In order to keep the repository free of unnecessary files and hard-to-read commits, it is mandatory to follow the following guidelines:

The associated book is available online here: https://symmehub.github.io/positron/intro.html

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

To publish the book once it has been tested and validated by you:

``` bash
ghp-import -n -p -f book/_build/html
```
