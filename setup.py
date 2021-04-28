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
