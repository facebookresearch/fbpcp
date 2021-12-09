#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from fbpcp.error.pcp import InvalidParameterError
from fbpcp.error.pcp import PcpError
from fbpcp.error.pcp import ThrottlingError
from google.cloud.exceptions import GoogleCloudError


# reference: https://gcloud.readthedocs.io/en/latest/_modules/google/cloud/exceptions.html
def map_gcp_error(error: GoogleCloudError) -> PcpError:
    code = error.code
    message = error.message
    if code == 429:
        return ThrottlingError(message)
    if code == 400:
        return InvalidParameterError(message)
    return PcpError(message)
