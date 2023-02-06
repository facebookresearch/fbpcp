#!/bin/bash
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


if [[ ! -f "docker-compose.yml" ]]; then
    echo "The docker compose file doesn't exist in the directory you ran this script in. Please run it from the repo root."
    exit 1
fi

docker compose build
docker compose run fbpcp /bin/bash -c ./scripts/run-python-tests.sh
