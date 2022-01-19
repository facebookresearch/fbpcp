# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# Usage: this script is to run from Github Actions Workflow
import re
import sys

import requests
from packaging.version import parse as version_parse


package = "fbpcp"
setup_file_path = "./setup.py"


def get_setup_version(file_path: str) -> str:
    setup_text = open(file_path).read().strip()
    version = re.search("version=['\"]([^'\"]*)['\"]", setup_text)

    return version.group(1)


def get_pypi_version(package: str) -> str:
    try:
        pypi_package_url = f"https://pypi.python.org/pypi/{package}/json"
        response = requests.get(pypi_package_url)
    except (requests.exceptions.RequestException) as e:
        print(f"{str(e)}")
        sys.exit(1)
    if response is not None:
        response_json = response.json()
        version = response_json["info"]["version"]

        return version


def main() -> None:
    setup_version = get_setup_version(setup_file_path)
    pypi_version = get_pypi_version(package)
    if version_parse(setup_version) > version_parse(pypi_version):
        print(f"setup.py {setup_version} is higher than Pypi version {pypi_version}")
        print("higher")
    elif version_parse(setup_version) == version_parse(pypi_version):
        print(f"setup.py {setup_version} is equal to Pypi version {pypi_version}")
        print("equal")
    elif "post" in setup_version:
        print("higher")
    else:
        print(
            f"Error: setup.py {setup_version} is lower than to Pypi version {pypi_version}, this is not exepected."
        )
        # when exit code is 1, the workflow will stop and raise an error
        sys.exit(1)


if __name__ == "__main__":
    main()
