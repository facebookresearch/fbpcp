#!/bin/bash
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

set -e

SCRIPTS_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "${SCRIPTS_DIRECTORY}"
cd "${SCRIPTS_DIRECTORY}/.."

files=$(find tests "${SCRIPTS_DIRECTORY}" -name '*.py')
echo "${files}"
if [[ -z "${files}" ]]; then
  echo 'No test files found, exiting.'
  exit 1
fi

echo " Running all tests:"
echo "${files}" | xargs python3 -m unittest -v
