#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Callable

from botocore.exceptions import ClientError
from fbpcs.error.mapper.aws import map_aws_error
from fbpcs.error.pcs import PcsError


def error_handler(f: Callable) -> Callable:
    def wrap(*args):
        try:
            return f(*args)
        except ClientError as err:
            raise map_aws_error(err)
        except Exception as err:
            raise PcsError(err)

    return wrap
