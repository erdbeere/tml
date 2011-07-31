#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from .items import Layer, TileLayer, TileManager, Tile, QuadLayer, QuadManager, \
     Quad

class TestTileLayer(unittest.TestCase):

    def setUp(self):
        self.layer = TileLayer()
        tile = Tile()
        tile.index = 1
        self.layer.tiles[20] = tile
        self.layer.tiles[70] = tile
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
        self.assertEqual(layer.color, (255, 255, 255, 255))

    def test_get_tile(self):
        for i in range(5):
            self.assertEqual(self.layer.get_tile(40 + i, 0),
                             self.layer.tiles[40 + i])
        for i in range(10):
            self.assertEqual(self.layer.get_tile(40 + i, 4),
                             self.layer.tiles[240 + i])
        self.assertRaises(ValueError, self.layer.get_tile, 50, 49)
        self.assertRaises(ValueError, self.layer.get_tile, -1, 49)
        self.assertRaises(ValueError, self.layer.get_tile, 49, 50)
        self.assertRaises(ValueError, self.layer.get_tile, 49, -1)

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

    def test_resizing(self):
        self.assertEqual(self.layer.width, 50)
        self.assertEqual(self.layer.height, 50)

        self.layer.width = 25
        self.assertEqual(self.layer.width, 25)
        self.assertEqual(len(self.layer.tiles), 25 * 50)
        self.layer.height = 25
        self.assertEqual(self.layer.height, 25)
        self.assertEqual(len(self.layer.tiles), 25 * 25)
        self.assertEqual(self.layer.tiles[20].index, 1)
        self.assertEqual(self.layer.tiles[45].index, 1)

        return
        self.layer.width = 100
        self.assertEqual(self.layer.width, 100)
        self.assertEqual(len(self.layer.tiles), 100 * 25)
        self.layer.height = 100
        self.assertEqual(self.layer.height, 100)
        self.assertEqual(len(self.layer.tiles), 100 * 100)
        self.assertEqual(self.layer.tiles[20].index, 1)
        self.assertEqual(self.layer.tiles[45].index, 1)

        with self.assertRaises(ValueError):
            self.layer.width = -1
        with self.assertRaises(ValueError):
            self.layer.height = -1

    def test_draw(self):
        # TODO
        pass

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
        self.manager = QuadManager([Quad() for i in xrange(10)])

    def test_init(self):
        manager = QuadManager()
        self.assertEqual(len(manager), 0)

        quads = [Quad() for i in xrange(10)]
        quad = Quad(pos_env=1, pos_env_offset=2, color_env=3,
                          color_env_offset=4)
        quads.append(quad)
        manager = QuadManager(quads)
        self.assertEqual(len(manager), 11)
        self.assertEqual(manager[0], Quad())
        self.assertEqual(manager[10], quad)

    def test_setitem(self):
        orig_quad = Quad(pos_env=8, color_env=4, pos_env_offset=2)
        self.manager[4] = orig_quad
        quad = self.manager[4]
        self.assertEqual(quad, orig_quad)

    def test_append(self):
        quad = Quad(pos_env=4, pos_env_offset=2)
        self.manager.append(quad)
        self.assertEqual(len(self.manager), 11)
        self.assertEqual(self.manager[10], quad)

    def test_pop(self):
        orig_quad = Quad(pos_env=4, pos_env_offset=2)
        self.manager.append(orig_quad)
        self.assertEqual(len(self.manager), 11)
        quad = self.manager.pop(0)
        self.assertEqual(len(self.manager), 10)
        self.assertEqual(quad, Quad())
        quad = self.manager.pop(9)
        self.assertEqual(len(self.manager), 9)
        self.assertEqual(quad, orig_quad)
        self.manager.append(orig_quad)
        quad = self.manager.pop(-1)
        self.assertEqual(quad, orig_quad)

if __name__ == '__main__':
    unittest.main()
