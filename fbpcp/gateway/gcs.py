#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Any, Dict, List, Optional

from fbpcp.decorator.error_handler import error_handler
from fbpcp.gateway.gcp import GCPGateway
from google.cloud import storage
from google.oauth2.service_account import Credentials


class GCSGateway(GCPGateway):
    def __init__(
        self,
        credentials_json: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(credentials_json=credentials_json, config=config)
        credentials = (
            (Credentials.from_service_account_info(self.config["credentials_json"]))
            if "credentials_json" in self.config.keys()
            else None
        )
        project = credentials.project_id if credentials is not None else None

        self.client = storage.Client(
            project=project,
            credentials=credentials,
        )

    @error_handler
    def create_bucket(self, bucket: str, location: Optional[str] = None) -> None:
        # If location is none, then the bucket will be created in US regions (multi-region)
        self.client.create_bucket(bucket, location=location)

    @error_handler
    def delete_bucket(self, bucket: str) -> None:
        bucket = self.client.get_bucket(bucket)
        bucket.delete()

    @error_handler
    def upload_file(self, file_name: str, bucket: str, key: str) -> None:
        # TODO: Add ProgressBar
        bucket = self.client.bucket(bucket)
        blob = bucket.blob(key)
        blob.upload_from_filename(file_name)

    @error_handler
    def download_file(self, bucket: str, key: str, file_name: str) -> None:
        # TODO: Add ProgressBar
        bucket = self.client.bucket(bucket)
        blob = bucket.blob(key)
        blob.download_to_filename(file_name)

    @error_handler
    def put_object(self, bucket: str, key: str, data: str) -> None:
        bucket = self.client.bucket(bucket)
        blob = bucket.blob(key)
        blob.upload_from_string(data)

    @error_handler
    def get_object(self, bucket: str, key: str) -> str:
        bucket = self.client.bucket(bucket)
        blob = bucket.blob(key)
        return blob.download_as_string()

    @error_handler
    def get_object_size(self, bucket: str, key: str) -> int:
        bucket = self.client.bucket(bucket)
        blob = bucket.get_blob(key)
        return blob.size

    @error_handler
    def get_object_info(self, bucket: str, key: str) -> Dict[str, Any]:
        bucket = self.client.bucket(bucket)
        blob = bucket.get_blob(key)
        return {"size": blob.size, "updated": blob.updated}

    @error_handler
    def list_objects(self, bucket: str, key: str) -> List[str]:
        """
        Bucket:
            fileA
            fileB
            different_prefix_file
            folderA/fileC
            folderB/fileD

        list_blobs(bucker, prefix='file', delimiter='/') ->
            fileA
            fileB

        list_blobs(bucker, prefix='folderA/', delimiter='/') ->
            folderA/
            folderA/fileC
        """
        blobs = self.client.list_blobs(bucket, prefix=key)
        objects = []
        for blob in blobs:
            objects.append(blob.name)
        return objects

    @error_handler
    def delete_object(self, bucket: str, key: str) -> None:
        bucket = self.client.bucket(bucket)
        blob = bucket.blob(key)
        blob.delete()

    @error_handler
    def object_exists(self, bucket: str, key: str) -> bool:
        bucket = self.client.bucket(bucket)
        blob = bucket.blob(key)
        return blob.exists()

    @error_handler
    def copy(
        self,
        source_bucket_name: str,
        source_key: str,
        dest_bucket_name: str,
        dest_key: str,
    ) -> None:
        source_bucket = self.client.bucket(source_bucket_name)
        source_blob = source_bucket.blob(source_key)
        dest_bucket = self.client.bucket(dest_bucket_name)

        source_bucket.copy_blob(source_blob, dest_bucket, dest_key)
