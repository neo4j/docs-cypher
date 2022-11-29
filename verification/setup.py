#!/usr/bin/env python

# Copyright (c) "Neo4j"
# Neo4j Sweden AB [https://neo4j.com]
#
# This file is part of Neo4j.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import setuptools

# packages = setuptools.find_packages(exclude=["tests"])

# readme_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "README.rst"))

# with open(readme_path, mode="r", encoding="utf-8") as fr:
#     readme = fr.read()

setup_args = {
    "name": "neo4j-docs",
    "version": "1",
    "description": "Neo4j Documentation Verification Tests",
}

setuptools.setup(**setup_args)
