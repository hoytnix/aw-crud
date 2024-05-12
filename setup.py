#!/usr/bin/env python
"""Setup script for the package."""

import os
import sys

import setuptools

PACKAGE_NAME = 'hoyt'
MINIMUM_PYTHON_VERSION = 3, 5


def check_python_version():
    """Exit when the Python version is too low."""
    if sys.version_info < MINIMUM_PYTHON_VERSION:
        sys.exit("Python {}.{}+ is required.".format(*MINIMUM_PYTHON_VERSION))


def read_package_variable(key):
    """Read the value of a variable from the package without importing."""
    package_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), PACKAGE_NAME)
    module_path = os.path.join(package_path, '__init__.py')
    with open(module_path) as module:
        for line in module:
            parts = line.strip().split(' ')
            if parts and parts[0] == key:
                return parts[-1].strip("'")
    assert 0, "'{0}' not found in '{1}'".format(key, module_path)


def read_descriptions():
    """Build a description for the project from documentation files."""
    return ''  # todo: include readme and changelog
    # pylint: disable=unreachable
    try:
        readme = open("README.rst").read()
        changelog = open("CHANGELOG.rst").read()
    except IOError:
        return "<placeholder>"
    else:
        return readme + '\n' + changelog


check_python_version()

setuptools.setup(
    name=read_package_variable('__project__'),
    version=read_package_variable('__version__'),
    description="My personal website.",
    url='https://hoyt.io',
    author='Michael Hoyt',
    author_email='base64(aG95dC5uaXhAZ21haWwuY29t)',
    packages=setuptools.find_packages(),
    entry_points={'console_scripts': ['hoyt = cli.cli:cli']},
    long_description=read_descriptions(),
    license='GPLv3',
    classifiers=[
        # TODO: update this list to match your application: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 1 - Planning',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=open("requirements.txt").readlines(), )
