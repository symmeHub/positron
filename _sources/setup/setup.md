


# Installing Python

## Install Miniforge

As of January 2025, we recommend installing Miniforge rather than Anaconda, for reasons of simplicity and licensing:

1. [Miniforge installer](https://conda-forge.org/download/), you may need to have a look at the [Miniforge documentation](https://github.com/conda-forge/miniforge) for more information.
    Mamba is already included in Miniforge.

:::{admonition} **For Windows users only**
:class: important
 If you do so, it is important that you chose 2 options during installation: 
- install only for me and
- add mini-forge to your `PATH`.
:::

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
    
# Installing GIT

If you're new to Python, learning Git is a game-changer! 
It helps you track changes, undo mistakes, and collaborate easily. 
With GitHub or GitLab, you can contribute to open-source projects and showcase your work. 
Start using Git early—it’ll make your coding journey way smoother!


## Procedure

- For Windows users: [GIT-SCM](https://git-scm.com/downloads)
- Linux: GIT is already instlalled
- MAC OS: for example, install it via Brew  [`brew install git`](https://formulae.brew.sh/formula/git)



# Installing VSCode

Visual Studio Code (VSCode) is a lightweight but powerful source code editor that runs on your desktop.

## Procedure

1. Download the installer from the [VSCode website](https://code.visualstudio.com/).
2. Run the installer and follow the instructions.

:::{admonition} **For Windows users only**
:class: important
Chose the "system installer" and not the "user installer".
:::

3. Open VSCode and install the Python extension by Microsoft.
