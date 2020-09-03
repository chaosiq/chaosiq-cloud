#!/usr/bin/env python
"""Chaos Toolkit Cloud builder and installer"""

import io
import os
import sys

import setuptools


def get_version_from_package() -> str:
    """
    Read the package version from the source without importing it.
    """
    path = os.path.join(os.path.dirname(__file__), "chaoscloud/__init__.py")
    path = os.path.normpath(os.path.abspath(path))
    with open(path) as f:
        for line in f:
            if line.startswith("__version__"):
                token, version = line.split(" = ", 1)
                version = version.replace("'", "").strip()
                return version


name = 'chaosiq-cloud'
desc = 'ChaosIQ plugin for the Chaos Toolkit CLI'

with io.open('README.md', encoding='utf-8') as strm:
    long_desc = strm.read()

classifiers = [
    'Intended Audience :: Developers',
    'License :: Freely Distributable',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: Implementation',
    'Programming Language :: Python :: Implementation :: CPython'
]
author = 'ChaosIQ'
author_email = 'contact@chaosiq.io'
url = 'https://chaosiq.io'
license = 'Apache License Version 2.0'
packages = [
    'chaoscloud',
    'chaoscloud.api',
    'chaoscloud.verify',
    'chaoscloud.probes',
    'chaoscloud.tolerances'
]

setup_params = dict(
    name=name,
    version=get_version_from_package(),
    description=desc,
    long_description=long_desc,
    long_description_content_type='text/markdown',
    classifiers=classifiers,
    author=author,
    author_email=author_email,
    url=url,
    license=license,
    packages=packages,
    include_package_data=True,
    python_requires='>=3.5.*',
    entry_points={
        'chaostoolkit.cli_plugins': [
            'signin = chaoscloud.cli:signin',
            'publish = chaoscloud.cli:publish',
            'enable = chaoscloud.cli:enable',
            'disable = chaoscloud.cli:disable',
            'org = chaoscloud.cli:org',
            'team = chaoscloud.cli:team',
            'verify = chaoscloud.cli:verify'
        ]
    }
)


def main():
    """Package installation entry point."""
    setuptools.setup(**setup_params)


if __name__ == '__main__':
    main()
