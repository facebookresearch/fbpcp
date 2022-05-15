#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from botocore.exceptions import ClientError
from fbpcp.error.pcp import InvalidParameterError, PcpError, ThrottlingError


# reference: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html
def map_aws_error(error: ClientError) -> PcpError:
    code = error.response["Error"]["Code"]
    response_metadata = error.response["ResponseMetadata"]
    message = f"{error}\n\n Details: {response_metadata}\n"

    if code == "InvalidParameterException":
        return InvalidParameterError(message)

    if code == "ThrottlingException":
        return ThrottlingError(message)

    return PcpError(message)
