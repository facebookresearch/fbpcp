#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-unsafe

import unittest

from fbpcp.error.mapper.k8s import map_k8s_error
from fbpcp.error.pcp import InvalidParameterError, PcpError, ThrottlingError
from kubernetes.client.exceptions import ApiException, ApiTypeError, ApiValueError


class TestMapK8SError(unittest.TestCase):
    def test_invalid_error(self):
        src_errs = [
            ApiValueError(
                "Missing the required parameter `namespace` when calling `create_namespaced_job`"
            ),
            ApiTypeError(
                "Got an unexpected keyword argument 'unexpected_arg' to method get_api_group"
            ),
            ApiException(status=400, reason="Bad Request"),
        ]

        for src_err in src_errs:
            dst_err = map_k8s_error(src_err)
            self.assertIsInstance(dst_err, InvalidParameterError)

    def test_throttling_error(self):
        src_err = ApiException(status=429, reason="Too Many Requests")
        dst_err = map_k8s_error(src_err)

        self.assertIsInstance(dst_err, ThrottlingError)

    def test_default_pce_error(self):
        src_err = ApiException(status=503, reason="Service Unavailable")
        dst_err = map_k8s_error(src_err)

        self.assertIsInstance(dst_err, PcpError)
