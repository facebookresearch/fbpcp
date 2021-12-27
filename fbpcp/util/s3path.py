#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import re
from typing import Tuple


class S3Path:
    region: str
    bucket: str
    key: str

    def __init__(self, fileURL: str) -> None:
        self.region, self.bucket, self.key = self._get_region_bucket_key(fileURL)

    def __eq__(self, other: "S3Path") -> bool:
        return (
            self.region == other.region
            and self.bucket == other.bucket
            and self.key == other.key
        )

    # virtual host style url
    # https://bucket-name.s3.Region.amazonaws.com/key-name
    def _get_region_bucket_key(self, fileURL: str) -> Tuple[str, str, str]:
        match = re.search("^https?:/([^.]+).s3.([^.]+).amazonaws.com/(.*)$", fileURL)
        if not match:
            raise ValueError(f"Could not parse {fileURL} as an S3Path")
        bucket, region, key = (
            match.group(1).strip("/"),
            match.group(2),
            match.group(3).strip("/"),
        )
        return (region, bucket, key)
