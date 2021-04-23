#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from setuptools import setup, find_packages

install_requires = [
    "boto3",
    "docopt",
    "schema",
    "pyyaml",
    "dataclasses-json",
    "jmespath",
    "s3transfer",
    "parameterized",
    "tqdm",
]

package_name = "fbpcs"
packages = [package_name] + [
    "%s.%s" % (package_name, sub_package) for sub_package in find_packages(package_name)
]

setup(
    name=package_name,
    version="0.1.0",
    description="Facebook Private Computation Service",
    author="Facebook",
    author_email="researchtool-help@fb.com",
    url="https://www.facebook.com/",
    install_requires=install_requires,
    packages=packages,
)
