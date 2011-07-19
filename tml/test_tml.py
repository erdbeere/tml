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
        maps = [
            {'name': 'ctf1', 'layers_per_group': [1,2,1,1,4]},
            {'name': 'ctf2', 'layers_per_group': [1,1,1,1,1,1,1,6]},
            {'name': 'ctf3', 'layers_per_group': [1,1,1,2,1,5]},
            {'name': 'ctf4', 'layers_per_group': [1,1,1,2,2,7]},
            {'name': 'ctf5', 'layers_per_group': [1,1,1,1,5]},
            {'name': 'ctf6', 'layers_per_group': [1,1,1,2,2,8]},
            {'name': 'ctf7', 'layers_per_group': [1,2,1,1,7]},
            {'name': 'dm1', 'layers_per_group': [1,2,2,1,1,1,6]},
            {'name': 'dm2', 'layers_per_group': [1,2,1,2,1,6,1]},
            {'name': 'dm6', 'layers_per_group': [1,1,1,2,1,1,1,7]},
            {'name': 'dm7', 'layers_per_group': [1,1,1,1,6]},
            {'name': 'dm8', 'layers_per_group': [1,1,1,1,1,1,2,2,10]},
            {'name': 'dm9', 'layers_per_group': [1,1,1,1,1,1,7,0]},
        ]
        for map_ in maps:
            t = Teemap('/'.join(['tml', 'maps', map_['name']]))
            msg = 'Map %s: wrong group number' % map_['name']
            self.assertEqual(len(t.groups), len(map_['layers_per_group']), msg)
            msg = 'Map %s: wrong layer number' % map_['name']
            self.assertEqual(len(t.layers), sum(map_['layers_per_group']), msg)
            for i, num in enumerate(map_['layers_per_group']):
                msg = 'Map %s: wrong layer number in group %d' % (
                    map_['name'], i)
                self.assertEqual(len(t.groups[i].layers), num, msg)

if __name__ == '__main__':
    unittest.main()
