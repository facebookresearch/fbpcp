#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from dataclasses import dataclass
from typing import List


@dataclass
class PolicyStatement:
    """AWS Policy Statement: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_statement.html"""

    effect: str
    principals: List[str]
    actions: List[str]
    resources: List[str]
    sid: str = ""


@dataclass
class PublicAccessBlockConfig:
    """AWS PublicAccessBlockConfiguration: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-publicaccessblockconfiguration.html"""

    block_public_acls: bool
    ignore_public_acls: bool
    block_public_policy: bool
    restrict_public_buckets: bool
