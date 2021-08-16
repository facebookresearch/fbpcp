#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict


class PcpError(Exception):
    pass


class InvalidParameterError(PcpError):
    pass


class ThrottlingError(PcpError):
    pass
