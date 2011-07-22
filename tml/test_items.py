#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from items import Layer, TileLayer, Tile

class TestTileLayer(unittest.TestCase):

    def setUp(self):
        self.layer = TileLayer()
        tile = Tile()
        tile.index = 1
        for i in range(5):
            self.layer.tiles[40 + i] = tile
        for i in range(10):
            self.layer.tiles[240 + i] = tile
        for i in range(6):
            self.layer.tiles[295 + i * 50] = tile
        self.layer.tiles[2042] = tile
        self.layer.tiles[2043] = tile
        self.layer.tiles[2092] = tile

    def test_init(self):
        layer = TileLayer()
        self.assertEqual(layer.width, 50)
        self.assertEqual(layer.height, 50)
        layer = TileLayer(100, 200)
        self.assertEqual(layer.width, 100)
        self.assertEqual(layer.height, 200)
        self.assertEqual(len(layer.tiles), 20000)
        self.assertEqual(layer.game, 0)
        self.assertEqual(layer.color_env, -1)
        self.assertEqual(layer.color_env_offset, 0)
        self.assertEqual(layer.image_id, -1)
        self.assertEqual(layer.color, {'r': 255, 'g': 255, 'b': 255, 'a': 255})

    def test_get_tile(self):
        for i in range(5):
            self.assertEqual(self.layer.get_tile(40 + i, 0).index, 1)
        for i in range(10):
            self.assertEqual(self.layer.get_tile(40 + i, 4).index, 1)

    def test_select(self):
        layer = self.layer.select(40, 4)
        self.assertEqual(len(layer.tiles), 1)
        self.assertEqual(layer.tiles[0].index, 1)

        layer = self.layer.select(39, 4)
        self.assertEqual(len(layer.tiles), 1)
        self.assertEqual(layer.tiles[0].index, 0)

        layer = self.layer.select(43, 0, 5, 6)
        print len(layer.tiles)
        for tile in layer.tiles[:2]:
            self.assertEqual(tile.index, 1)

        # clamping test to the right
        layer = self.layer.select(45, 3, 5, 4)

        # clamping test to the bottom
        layer = self.layer.select(2, 47, 2, 4)

if __name__ == '__main__':
    unittest.main()
