#!/usr/bin/env python3

import unittest

from fbpcs.util.s3path import S3Path


class TestS3Path(unittest.TestCase):
    def test_s3path_no_subfolder(self):
        test_s3path = S3Path("https://bucket-name.s3.Region.amazonaws.com/key-name")
        self.assertEqual(test_s3path.region, "Region")
        self.assertEqual(test_s3path.bucket, "bucket-name")
        self.assertEqual(test_s3path.key, "key-name")

    def test_s3path_with_subfoler(self):
        test_s3path = S3Path(
            "https://bucket-name.s3.Region.amazonaws.com/subfolder/key"
        )
        self.assertEqual(test_s3path.region, "Region")
        self.assertEqual(test_s3path.bucket, "bucket-name")
        self.assertEqual(test_s3path.key, "subfolder/key")

    def test_s3path_invalid_fileURL(self):
        test_url = "an invalid fileURL"
        with self.assertRaises(ValueError):
            S3Path(test_url)
