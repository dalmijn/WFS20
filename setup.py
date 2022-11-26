from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
	name="wfs20",
	version="0.2.0a1",
	description="Small library to request geospatial data (WFS)",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/B-Dalmijn/WFS20",
	author="Brendan Wybo Dalmijn",
	author_email="brencodeert@outlook.com",
	license="BSD",
	classifiers=[
	# How mature is this project? Common values are
	#   3 - Alpha
	#   4 - Beta
	#   5 - Production/Stable
	'Development Status :: 3 - Alpha',

	# Indicate who your project is intended for
	'Intended Audience :: End Users/Desktop',
	'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',

    # Topic of the package
    'Topic :: Scientific/Engineering :: GIS',

	# Pick your license as you wish (should match "license" above)
	'License :: OSI Approved :: BSD License',

	# Language
	'Natural Language :: English',

	# OS
	'Operating System :: OS Independent',

	# Specify the Python versions you support here. In particular, ensure
	# that you indicate whether you support Python 2, Python 3 or both.
	'Programming Language :: Python :: 3',
	'Programming Language :: Python :: 3.6',
	'Programming Language :: Python :: 3.7',
	'Programming Language :: Python :: 3.8',
	'Programming Language :: Python :: 3.9',
	],
	keywords="wfs WebFeatureService shapefile gml request",
	project_urls={
	'Source': 'https://github.com/B-Dalmijn/WFS20/',
	'Tracker': 'https://github.com/B-Dalmijn/WFS20/issues',
	},
	package_dir={"":"src"},
	packages=find_packages(where="src"),
	install_requires=[
	"requests",
	"lxml"
	],
	python_requires='>=3.6',
	package_data={
	"wfs20": ["data\\axisorder.db"],
	}
	)