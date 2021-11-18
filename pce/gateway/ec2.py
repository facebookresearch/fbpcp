# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import List, Optional, Dict

import botocore
from fbpcp.gateway.aws import AWSGateway
from pce.gateway.client_generator import ClientGeneratorFuncton


class EC2Gateway(AWSGateway):
    def __init__(self, create_generator_fn: ClientGeneratorFuncton) -> None:
        super().__init__()
        self.client: botocore.client.BaseClient = create_generator_fn("ec2")

    def describe_availability_zones(
        self,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        response = self.client.describe_availability_zones()

        return [aws_az["ZoneName"] for aws_az in response["AvailabilityZones"]]
