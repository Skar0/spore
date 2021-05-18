# Synt-tool

## How to build
Building requires a builder, such as PyPA build.

    virtualenv --python=python2.7 env
    source env/bin/activate
    pip install build
    python setup.py bdist_wheel
    pip install dist/*.whl

### Unit tests
Once `synttool` is installed, the unit tests can be run as:

    cd tests/regular
    python -m unittest discovery