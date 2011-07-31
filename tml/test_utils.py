# -*- coding: utf-8 -*-

import unittest

from utils import ints_to_string, string_to_ints

TEST_INT = [-186256396, -2139062144, -2139062144, -2139062144, -2139062144,
            -2139062144, -2139062144, -2139062272]
class TestUtils(unittest.TestCase):

    def test_ints_to_string(self):
        test = ints_to_string(TEST_INT)
        self.assertEqual(test, 'test')

    def test_string_to_ints(self):
        test = string_to_ints('test')
        self.assertEqual(test, TEST_INT)
