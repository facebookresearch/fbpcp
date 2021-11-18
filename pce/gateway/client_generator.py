# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Optional, Dict, Any, Callable

import boto3
import botocore

CloudProviderClient = botocore.client.BaseClient
ClientGeneratorFuncton = Callable[[str], CloudProviderClient]


def create_client_generator(
    region: str,
    access_key_id: str,
    access_key_data: str,
    config: Optional[Dict[str, Any]] = None,
) -> ClientGeneratorFuncton:
    config = config or {}
    config.update(
        {"aws_access_key_id": access_key_id, "aws_secret_access_key": access_key_data}
    )

    return lambda client_name: boto3.client(client_name, region_name=region, **config)
