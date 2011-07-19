#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from tml import Header, Teemap

class TestHeader(unittest.TestCase):

    def setUp(self):
        pass

    def test_signature(self):
        with open('tml/maps/dm1.map') as f:
            header = Header(f)

    def test_load(self):
        assert Teemap('tml/maps/dm1.map')
        assert Teemap('tml/maps/dm1')
        t = Teemap()
        t.load('tml/maps/dm1.map')
        t = Teemap()
        t.load('tml/maps/dm1')

class TestTeemap(unittest.TestCase):

    def setUp(self):
        pass

    def test_num(self):
        t = Teemap('tml/test_maps/vanilla')
        self.assertEqual(len(t.groups), 7)
        self.assertEqual(len(t.layers), 6)
        for i, num in enumerate([1,2,1,0,2,0,0]):
            self.assertEqual(len(t.groups[i].layers), num)

if __name__ == '__main__':
    unittest.main()
