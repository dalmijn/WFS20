"""Setup defined for database."""

import subprocess

from setuptools import setup
from setuptools.command.build_py import build_py


class CustomBuild(build_py):
    """Custom build class."""

    def run(self):
        """Build the database."""
        # Run the script to generate the database file
        subprocess.run(["python", "dbase.py"])
        # Continue with the normal build process
        build_py.run(self)


setup(
    name="wfs20",
    version="1.0.0",
    packages=["src/wfs20"],
    cmdclass={"build_py": CustomBuild},
)
