#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from setuptools import find_packages, setup

install_requires = [
    "boto3==1.18.57",
    "urllib3==1.26.7",
    "dataclasses-json==0.5.2",
    "pyyaml==5.4.1",
    "tqdm==4.55.1",
    "google-cloud-storage==1.30.0",
    "docopt==0.6.2",
    "schema==0.7.0",
    "psutil==5.8.0",
    "click==7.1.2",
    "kubernetes==12.0.1",
    "cryptography==36.0.2",
]

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="fbpcp",
    version="0.2.10",
    description="Facebook Private Computation Platform",
    author="Facebook",
    author_email="researchtool-help@fb.com",
    url="https://github.com/facebookresearch/fbpcp",
    install_requires=install_requires,
    packages=find_packages(),
    long_description_content_type="text/markdown",
    long_description=long_description,
    python_requires=">=3.8",
)
