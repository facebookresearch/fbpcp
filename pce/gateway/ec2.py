# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
from typing import List, Optional, Dict, Any

import boto3


class EC2Gateway:
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.region = region
        self.config: Dict[str, Any] = config or {}

        if access_key_id is not None:
            self.config["aws_access_key_id"] = access_key_id

        if access_key_data is not None:
            self.config["aws_secret_access_key"] = access_key_data

        self.client = boto3.client("ec2", region_name=self.region, **self.config)

    def describe_availability_zones(
        self,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        response = self.client.describe_availability_zones()

        return [aws_az["ZoneName"] for aws_az in response["AvailabilityZones"]]
