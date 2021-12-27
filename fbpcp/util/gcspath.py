#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import re
from typing import Tuple


class GCSPath:
    bucket: str
    key: str

    def __init__(self, fileURL: str) -> None:
        self.bucket, self.key = self._get_bucket_key(fileURL)

    def __eq__(self, other: "GCSPath") -> bool:
        return self.bucket == other.bucket and self.key == other.key

    # virtual host style url
    # https://storage.cloud.google.com/<bucket>/<key>
    def _get_bucket_key(self, fileURL: str) -> Tuple[str, str]:
        match = re.search("^https?://storage.cloud.google.com/(.*)$", fileURL)
        if not match:
            raise ValueError(f"Could not parse {fileURL} as an GCSPath")
        bucket, *rest = match.group(1).split("/")
        key = "/".join(rest)
        return (bucket, key)
