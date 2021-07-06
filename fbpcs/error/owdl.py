#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict


class OWDLError(Exception):
    pass


class OWDLParsingError(OWDLError):
    pass


class OWDLRuntimeError(OWDLError):
    pass
