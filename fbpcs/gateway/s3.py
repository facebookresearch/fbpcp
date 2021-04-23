#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import os
from typing import Any, Dict, List, Optional

import boto3
from tqdm.auto import tqdm


class S3Gateway:
    def __init__(
        self,
        region: str = "us-west-1",
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.region = region
        config = config or {}

        if access_key_id:
            config["aws_access_key_id"] = access_key_id

        if access_key_data:
            config["aws_secret_access_key"] = access_key_data

        # pyre-ignore
        self.client = boto3.client("s3", region_name=self.region, **config)

    def create_bucket(self, bucket: str, region: Optional[str] = None) -> None:
        region = region if region is not None else self.region
        self.client.create_bucket(
            Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": region}
        )

    def delete_bucket(self, bucket: str) -> None:
        self.client.delete_bucket(Bucket=bucket)

    def upload_file(self, file_name: str, bucket: str, key: str) -> None:
        file_size = os.path.getsize(file_name)
        self.client.upload_file(
            file_name,
            bucket,
            key,
            Callback=self.ProgressPercentage(file_name, file_size),
        )

    def download_file(self, bucket: str, key: str, file_name: str) -> None:
        file_size = self.client.head_object(Bucket=bucket, Key=key)["ContentLength"]
        self.client.download_file(
            bucket,
            key,
            file_name,
            Callback=self.ProgressPercentage(file_name, file_size),
        )

    def put_object(self, bucket: str, key: str, data: str) -> None:
        self.client.put_object(Bucket=bucket, Key=key, Body=data.encode())

    def get_object(self, bucket: str, key: str) -> str:
        res = self.client.get_object(Bucket=bucket, Key=key)
        return res["Body"].read().decode()

    def get_object_info(self, bucket: str, key: str) -> Dict[str, Any]:
        return self.client.get_object(Bucket=bucket, Key=key)

    def list_object2(self, bucket: str, key: str) -> List[str]:
        paginator = self.client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=bucket, Prefix=key)

        key_list = []
        for page in pages:
            for content in page["Contents"]:
                key_list.append(content["Key"])

        return key_list

    def delete_object(self, bucket: str, key: str) -> None:
        self.client.delete_object(Bucket=bucket, Key=key)

    def object_exists(self, bucket: str, key: str) -> bool:
        try:
            # Result intentionally discarded
            _ = self.client.head_object(Bucket=bucket, Key=key)
            return True
        except Exception:
            return False

    def copy(
        self, source_bucket: str, source_key: str, dest_bucket: str, dest_key: str
    ) -> None:
        source = {"Bucket": source_bucket, "Key": source_key}
        self.client.copy(source, dest_bucket, dest_key)

    class ProgressPercentage(object):
        def __init__(self, file_name: str, file_size: int) -> None:
            self._progressbar = tqdm(total=file_size, desc=file_name)

        def __call__(self, bytes_amount: int) -> None:
            self._progressbar.update(bytes_amount)

        def __del__(self) -> None:
            self._progressbar.close()
