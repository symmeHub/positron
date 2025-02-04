# Setup

In order to work locally with the examples provided in this book, you will need to install python and jupyter notebook. 
You can install them by following the instructions below.

## Installing Conda and Mamba

You can install conda using alternatively:
1. [Anaconda](https://www.anaconda.com/download/success). Then, install mamba using:
    ```bash
    conda install -c conda-forge mamba
    ```
2. Or [Miniforge](https://conda-forge.org/download/), you may need to have a look at the [Miniforge documentation](https://github.com/conda-forge/miniforge) for more information.
    Mamba is already included in Miniforge.


## Environment setup

Create an environment with the following command:
1. Download the environment file [positron_env.yaml](positron_env.yaml) and put it in the current folder.
2.  Run the following command:
    ```bash
    mamba env create --file=positron_env.yaml
    ```
    If you don't have mamba installed, you can use conda instead:
    ```bash
    conda env create --file=positron_env.yaml
    ```
    The install process will just be a bit slower.
3. Activate the environment:
    ```bash
    conda activate positron
    ```

## Run all examples locally

At this point, you should have all the necessary packages installed. You can run Jupyter Lab with the following command:

```bash
jupyter lab
```

And Jupyter Notebook with:

```bash
jupyter notebook
```
    
