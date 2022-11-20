from wfs20 import __version__

from setuptools import setup, find_packages

setup(name="wfs20",version=f"{__version__}",packages=find_packages())

# print(find_packages())