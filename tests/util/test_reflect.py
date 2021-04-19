#!/usr/bin/env python3

import unittest

from util.reflect import get_class
from util.s3path import S3Path

TEST_CLASS_PATH = "util.s3path.S3Path"


class TestReflect(unittest.TestCase):
    def test_get_class(self):
        self.assertEqual(S3Path, get_class(TEST_CLASS_PATH))
