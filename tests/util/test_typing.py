#!/usr/bin/env python3

import unittest

from fbpcs.util.typing import checked_cast

TEST_STR = "test"
TEST_NUM = 123


class TestTyping(unittest.TestCase):
    def test_checked_cast(self):
        error = f"Value was not of type {type!r}:\n{TEST_STR!r}"
        with self.assertRaisesRegex(ValueError, error):
            checked_cast(int, TEST_STR)

        self.assertEqual(checked_cast(int, TEST_NUM), TEST_NUM)
