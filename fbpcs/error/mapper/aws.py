#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from botocore.exceptions import ClientError
from fbpcs.error.pcs import InvalidParameterError
from fbpcs.error.pcs import PcsError
from fbpcs.error.pcs import ThrottlingError


# reference: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html
def map_aws_error(error: ClientError) -> PcsError:
    code = error.response["Error"]["Code"]
    message = error.response["Error"]["Message"]

    if code == "InvalidParameterException":
        return InvalidParameterError(message)

    if code == "ThrottlingException":
        return ThrottlingError(message)

    return PcsError(message)
