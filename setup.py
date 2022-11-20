from wfs20 import __version__

from setuptools import setup, find_packages

setup(
	name="wfs20",
	version=f"{__version__}a1",
	description="Small library to request geospatial data (WFS)",
	url="https://github.com/B-Dalmijn/WFS20",
	author="Brendan Wybo Dalmijn",
	author_email="brencodeert@outlook.com",
	license="MIT",
	classifiers=[
	# How mature is this project? Common values are
	#   3 - Alpha
	#   4 - Beta
	#   5 - Production/Stable
	'Development Status :: 3 - Alpha',

	# Indicate who your project is intended for
	'Intended Audience :: Users',

	# Pick your license as you wish (should match "license" above)
	'License :: OSI Approved :: MIT License',

	# Specify the Python versions you support here. In particular, ensure
	# that you indicate whether you support Python 2, Python 3 or both.
	'Programming Language :: Python :: 3.6',
	'Programming Language :: Python :: 3.7',
	'Programming Language :: Python :: 3.8',
	'Programming Language :: Python :: 3.9',
	],
	keyword="wfs WebFeatureService shapefile gml request",
	project_urls={
	'Source': 'https://github.com/B-Dalmijn/WFS20',
	'Tracker': 'https://github.com/B-Dalmijn/WFS20/issues',
	},
	package_dir={"":"src"},
	packages=find_packages(where="src"),
	install_requires=[
	"lxml"
	],
	python_requires='>=3.6',
	)