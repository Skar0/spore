from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize([
            "regularcython/arena.pyx",
            "regularcython/attractor.pyx",
            "regularcython/generalizedRecursive.pyx",
            "regularcython/gpg2arena.pyx",
        ]
    )
)