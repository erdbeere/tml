#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from items import Layer, TileLayer, TileManager, Tile, QuadLayer, QuadManager, \
     Quad

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
        self.layer.tiles[2402] = tile
        self.layer.tiles[2403] = tile
        self.layer.tiles[2452] = tile

    def test_init(self):
        layer = TileLayer()
        self.assertEqual(layer.width, 50)
        self.assertEqual(layer.height, 50)
        layer = TileLayer(100, 200, 'Tee')
        self.assertEqual(layer.width, 100)
        self.assertEqual(layer.height, 200)
        self.assertEqual(layer.name, 'Tee')
        self.assertEqual(len(layer.tiles), 20000)
        self.assertEqual(layer.game, 0)
        self.assertEqual(layer.color_env, -1)
        self.assertEqual(layer.color_env_offset, 0)
        self.assertEqual(layer.image_id, -1)
        self.assertEqual(layer.color, {'r': 255, 'g': 255, 'b': 255, 'a': 255})

    def test_get_tile(self):
        for i in range(5):
            self.assertEqual(self.layer.get_tile(40 + i, 0),
                             self.layer.tiles[40 + i])
        for i in range(10):
            self.assertEqual(self.layer.get_tile(40 + i, 4),
                             self.layer.tiles[240 + i])

    def test_select(self):
        layer = self.layer.select(40, 4)
        self.assertEqual(len(layer.tiles), 1)
        self.assertEqual(layer.tiles[0].index, 1)

        layer = self.layer.select(39, 4)
        self.assertEqual(len(layer.tiles), 1)
        self.assertEqual(layer.tiles[0].index, 0)

        layer = self.layer.select(43, 0, 5, 6)
        self.assertEqual(len(layer.tiles), 30)
        for tile in layer.tiles[:2]:
            self.assertEqual(tile.index, 1)
        for tile in layer.tiles[2:20]:
            self.assertEqual(tile.index, 0)
        for tile in layer.tiles[20:25]:
            self.assertEqual(tile.index, 1)
        for tile in layer.tiles[25:27]:
            self.assertEqual(tile.index, 0)
        self.assertEqual(layer.tiles[27].index, 1)
        for tile in layer.tiles[28:30]:
            self.assertEqual(tile.index, 0)

        # clamping test to the right
        layer = self.layer.select(45, 3, 7, 4)
        self.assertEqual(len(layer.tiles), 20)
        for tile in layer.tiles[:5]:
            self.assertEqual(tile.index, 0)
        for tile in layer.tiles[5:10]:
            self.assertEqual(tile.index, 1)
        self.assertEqual(layer.tiles[10].index, 1)
        for tile in layer.tiles[11:15]:
            self.assertEqual(tile.index, 0)
        self.assertEqual(layer.tiles[15].index, 1)
        for tile in layer.tiles[16:20]:
            self.assertEqual(tile.index, 0)

        # clamping test to the bottom
        layer = self.layer.select(2, 47, 2, 4)
        self.assertEqual(len(layer.tiles), 6)
        for tile in layer.tiles[:2]:
            self.assertEqual(tile.index, 0)
        for tile in layer.tiles[2:5]:
            self.assertEqual(tile.index, 1)
        self.assertEqual(layer.tiles[5].index, 0)

class TestTileManager(unittest.TestCase):

    def test_init(self):
        pass

class TestQuadLayer(unittest.TestCase):

    def test_init(self):
        layer = QuadLayer()
        self.assertEqual(layer.name, 'Quads')
        self.assertEqual(layer.image_id, -1)
        self.assertEqual(len(layer.quads), 0)
        self.assertTrue(isinstance(layer.quads, QuadManager))
        self.assertEqual(QuadLayer('TeeWar').name, 'TeeWar')

class TestQuadManager(unittest.TestCase):

    def setUp(self):
        self.manager = QuadManager()

    def test_init(self):
        manager = QuadManager()
        self.assertEqual(len(manager), 0)
        quads = [Quad() for i in xrange(10)]
        quads.append(Quad(pos_env=1, pos_env_offset=2, color_env=3,
                          color_env_offset=4))
        manager = QuadManager(quads)
        self.assertEqual(len(manager), 11)

if __name__ == '__main__':
    unittest.main()
