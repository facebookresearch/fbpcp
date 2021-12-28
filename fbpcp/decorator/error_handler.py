#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import functools
from typing import Callable

from botocore.exceptions import ClientError
from fbpcp.error.mapper.aws import map_aws_error
from fbpcp.error.mapper.gcp import map_gcp_error
from fbpcp.error.mapper.k8s import map_k8s_error
from fbpcp.error.pcp import PcpError
from google.cloud.exceptions import GoogleCloudError
from kubernetes.client.exceptions import OpenApiException


def error_handler(f: Callable) -> Callable:
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except PcpError as err:
            raise err from None
        # AWS Error
        except ClientError as err:
            raise map_aws_error(err) from None
        # GCP Error
        except GoogleCloudError as err:
            raise map_gcp_error(err) from None
        except OpenApiException as err:
            raise map_k8s_error(err) from None
        except Exception as err:
            raise PcpError(err) from None

    return wrapper
