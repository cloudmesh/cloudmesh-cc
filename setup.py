#!/usr/bin/env python
# ----------------------------------------------------------------------- #
# Copyright 2017, Gregor von Laszewski, Indiana University                #
#                                                                         #
# Licensed under the Apache License, Version 2.0 (the "License"); you may #
# not use this file except in compliance with the License. You may obtain #
# a copy of the License at                                                #
#                                                                         #
# http://www.apache.org/licenses/LICENSE-2.0                              #
#                                                                         #
# Unless required by applicable law or agreed to in writing, software     #
# distributed under the License is distributed on an "AS IS" BASIS,       #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.#
# See the License for the specific language governing permissions and     #
# limitations under the License.                                          #
# ------------------------------------------------------------------------#

from setuptools import find_packages, setup
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.util import readfile
import io

# def readfile(filename):
#     with io.open(filename, encoding="utf-8") as stream:
#         return stream.read().split()


requiers = readfile('requirements.txt').splitlines()
#
# add minimum requirements here
#
# requiers = """
# cloudmesh-cmd5
# cloudmesh-sys
# cloudmesh-inventory
# cloudmesh-configuration
# cloudmesh-progress
# pyyaml==5.4.1
# psutil
# yamldb
# docker-compose
# networkx[default]
# pydot
# graphviz
# fastapi[all]
# httpx
# trio
# papermill
# pandas
# markdown
# sse-starlette
# ipython
# ipykernel
# """.split("\n")

if os_is_windows():
    requiers.append('pywin32')

print(requiers)

# dependency_links = ['http://github.com/nicolaiarocci/eve.git@develop']

version = readfile("VERSION")[0].strip()

with open('README.md') as f:
    long_description = f.read()



NAME = "cloudmesh-cc"
DESCRIPTION = "A repository for running workflows"
AUTHOR = "Gregor von Laszewski"
AUTHOR_EMAIL = "laszewski@gmail.com"
URL = "https://github.com/cloudmesh/cloudmesh-cc"


setup(
    name=NAME,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=version,
    license="Apache 2.0",
    url=URL,
    packages=find_namespace_packages(
        exclude=("tests",
                 "deprecated",
                 "propose",
                 "examples",
                 "conda"),
        include=['cloudmesh']),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=requiers,
    tests_require=[
        "flake8",
        "coverage",
    ],
    zip_safe=False,
)
