#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from fbpcp.error.pcp import InvalidParameterError, PcpError, ThrottlingError
from kubernetes.client.exceptions import (
    ApiException,
    ApiTypeError,
    ApiValueError,
    OpenApiException,
)

# reference: https://github.com/kubernetes-client/python/blob/d3de7a85a63fa6bec6518d1cc75dc5e9458b9bbc/kubernetes/client/exceptions.py
def map_k8s_error(error: OpenApiException) -> PcpError:
    message = str(error)
    if isinstance(error, (ApiValueError, ApiTypeError)):
        return InvalidParameterError(message)
    elif isinstance(error, ApiException):
        code = error.status
        if code == 429:
            return ThrottlingError(message)
        if code == 400 or code == 404:
            return InvalidParameterError(message)

    return PcpError(message)
