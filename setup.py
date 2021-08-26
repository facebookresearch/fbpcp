#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from setuptools import setup, find_packages

install_requires = [
    "boto3==1.11.11",
    "dataclasses-json==0.5.2",
    "pyyaml==5.4.1",
    "tqdm==4.55.1",
]

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="fbpcp",
    version="0.1.4",
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
