#!/bin/bash
eval "$(conda shell.bash hook)" && /
conda activate jupyter_book && /
jupyter-book clean book $1 && /
jupyter-book build book && /
firefox ./book/_build/html/index.html &
