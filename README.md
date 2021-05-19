# Synt-tool

## How to build
Execute the following commands

    virtualenv --python=python2.7 env
    source env/bin/activate
    python setup.py build_ext --inplace

Then, you can import the packages from the root of this project.

### Unit tests
Once `synttool` is installed, the unit tests can be run as:

    python -m unittest discover .

from the root directory of the project