#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from tml import Header, Teemap
from items import Layer, QuadLayer, TileLayer

class TestHeader(unittest.TestCase):

    def setUp(self):
        with open('tml/maps/dm1.map') as f:
            self.header = Header(f)

    def test_signature(self):
        pass

    def test_load(self):
        assert Teemap('tml/maps/dm1.map')
        assert Teemap('tml/maps/dm1')
        t = Teemap()
        t.load('tml/maps/dm1.map')
        t = Teemap()
        t.load('tml/maps/dm1')

class TestTeemap(unittest.TestCase):

    def setUp(self):
        self.teemap = Teemap('tml/test_maps/vanilla')

    def test_groups(self):
        self.assertEqual(len(self.teemap.groups), 7)
        names = [None, None, 'Game', 'NamedGroup', None, None, 'OtherGroup']
        for i, group in enumerate(self.teemap.groups):
            self.assertEqual(group.name, names[i])

    def test_layers(self):
        self.assertEqual(len(self.teemap.layers), 6)
        for i, num in enumerate([1,2,1,0,2,0,0]):
            self.assertEqual(len(self.teemap.groups[i].layers), num)

        self.assertIs(self.teemap.groups[0].layers[0], self.teemap.layers[0])
        self.assertIs(self.teemap.groups[1].layers[0], self.teemap.layers[1])
        self.assertIs(self.teemap.groups[1].layers[1], self.teemap.layers[2])
        self.assertIs(self.teemap.groups[2].layers[0], self.teemap.layers[3])
        self.assertIs(self.teemap.groups[4].layers[0], self.teemap.layers[4])
        self.assertIs(self.teemap.groups[4].layers[1], self.teemap.layers[5])

        names = ['TestQuads', 'Quads', 'TestTiles', 'Game', None, 'LastTiles']
        classes = [QuadLayer, QuadLayer, TileLayer, TileLayer, TileLayer,
                   TileLayer]
        for i, layer in enumerate(self.teemap.layers):
            self.assertIsInstance(layer, classes[i])
            self.assertEqual(layer.name, names[i])

        for layer in self.teemap.layers:
            if isinstance(layer, TileLayer):
                if layer.name == 'TestTiles':
                    self.assertEqual(layer.width, 5)
                    self.assertEqual(layer.height, 3)
                else:
                    self.assertEqual(layer.width, 50)
                    self.assertEqual(layer.height, 50)

        self.assertIs(self.teemap.layers[3], self.teemap.gamelayer)

    def test_envelopes(self):
        self.assertEqual(len(self.teemap.envelopes), 2)
        self.assertEqual(self.teemap.envelopes[0].name, 'PosEnv')
        self.assertEqual(self.teemap.envelopes[1].name, 'ColorEnv')

    def test_envpoints(self):
        self.assertEqual(len(self.teemap.envpoints), 9)
        self.assertEqual(len(self.teemap.envelopes[0].envpoints), 4)
        self.assertEqual(len(self.teemap.envelopes[1].envpoints), 5)

        for i, envpoint in enumerate(self.teemap.envelopes[0].envpoints):
            self.assertIs(envpoint, self.teemap.envpoints[i])
        for i, envpoint in enumerate(self.teemap.envelopes[1].envpoints):
            self.assertIs(envpoint, self.teemap.envpoints[i+4])

    def test_images(self):
        images = [None, None, 'grass_main', None, 'grass_main', 'test']
        for i, layer in enumerate(self.teemap.layers):
            if images[i] is None:
                self.assertIs(layer.image, None)
            else:
                self.assertEqual(layer.image.name, images[i])

        self.assertIs(self.teemap.layers[2].image, self.teemap.images[0])
        self.assertIs(self.teemap.layers[4].image, self.teemap.images[0])
        self.assertIs(self.teemap.layers[5].image, self.teemap.images[1])
        self.assertTrue(self.teemap.images[0].external)
        self.assertFalse(self.teemap.images[1].external)
        self.assertTrue(self.teemap.images[2].external)

    def test_tiles(self):
        tiles = self.teemap.layers[2].tiles
        self.assertEqual(len(tiles), 15)

        for i, tile in enumerate(tiles[:5]):
            self.assertEqual(tile.index, i)
        for tile in tiles[5:10]:
            self.assertEqual(tile.index, 0)
        for i, tile in enumerate(tiles[10:]):
            self.assertEqual(tile.index, i + 251)

        flags = [
            {'rotation': False, 'hflip': False, 'vflip': True},
            {'rotation': False, 'hflip': True, 'vflip': False},
            {'rotation': False, 'hflip': True, 'vflip': True},
            {'rotation': True, 'hflip': True, 'vflip': True},
            {'rotation': True, 'hflip': False, 'vflip': False},
            {'rotation': False, 'hflip': False, 'vflip': False},
        ]
        for i, tile in enumerate(tiles[:6]):
            self.assertEqual(tile.flags, flags[i])

if __name__ == '__main__':
    unittest.main()
