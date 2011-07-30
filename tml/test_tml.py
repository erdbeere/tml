#!/usr/bin/env python
# -*- coding: utf-8 -*-

import filecmp
import os
import shutil
import unittest
import warnings

from tml import Teemap, MapError
import items

class TestTeemap(unittest.TestCase):

    def setUp(self):
        os.mkdir('test_tmp')
        self.teemap = Teemap('tml/test_maps/vanilla')

    def tearDown(self):
        if os.path.isdir('test_tmp'):
            shutil.rmtree('test_tmp')

    def test_load(self):
        pass
        #with warnings.catch_warnings(record=True) as w:
        #    warnings.simplefilter('always')
        #    Teemap('tml/test_maps/vanilla')
        #    self.assertEqual(len(w), 1)
        #    self.assertTrue(issubclass(w[0].category, UserWarning))
        #    self.assertIn(str(w[0].message), 'External image „test2“ does not exist')
        #assert Teemap('tml/maps/dm1.map')
        #assert Teemap('tml/maps/dm1')

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
        classes = [items.QuadLayer, items.QuadLayer, items.TileLayer, items.TileLayer, items.TileLayer,
                   items.TileLayer]
        for i, layer in enumerate(self.teemap.layers):
            self.assertIsInstance(layer, classes[i])
            self.assertEqual(layer.name, names[i])

        for layer in self.teemap.layers:
            if isinstance(layer, items.TileLayer):
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
        images = [None, 'grass_main', 'grass_main', None, 'grass_main', 'test']
        for i, layer in enumerate(self.teemap.layers):
            if images[i] is None:
                self.assertIs(layer.image_id, -1)
            else:
                self.assertEqual(self.teemap.images[layer.image_id].name,
                                 images[i])

        self.assertIs(self.teemap.layers[2].image_id, 0)
        self.assertIs(self.teemap.layers[4].image_id, 0)
        self.assertIs(self.teemap.layers[5].image_id, 1)
        self.assertTrue(self.teemap.images[0].external)
        self.assertFalse(self.teemap.images[1].external)
        self.assertTrue(self.teemap.images[2].external)
        self.teemap.images[0].save('test_tmp/grass_main.png')
        self.teemap.images[1].save('test_tmp/test.png')
        self.assertRaises(ValueError, self.teemap.images[2].save,
                          'test_tmp/test2.png')
        self.assertTrue(filecmp.cmp('test_tmp/grass_main.png',
                                    'tml/mapres/grass_main.png'))
        self.assertTrue(filecmp.cmp('test_tmp/test.png',
                                    'tml/test_mapres/test.png'))

    def test_tiles(self):
        layer = self.teemap.layers[2]
        tiles = layer.tiles
        self.assertEqual(len(tiles), 15)

        # XXX: wouldn't be coordinates in layer make more sense?
        for i, tile in enumerate(tiles[:5]):
            self.assertEqual(tile.index, i)
            self.assertEqual(tile.coords, (i, 0))
        for tile in tiles[5:10]:
            self.assertEqual(tile.index, 0)
            self.assertEqual(tile.coords, (0, 0))
        for i, tile in enumerate(tiles[10:]):
            self.assertEqual(tile.index, i + 251)
            self.assertEqual(tile.coords, (11 + i, 15))

        flags = [
            {'rotation': False, 'hflip': True, 'vflip': False},
            {'rotation': False, 'hflip': False, 'vflip': True},
            {'rotation': False, 'hflip': True, 'vflip': True},
            {'rotation': True, 'hflip': True, 'vflip': True},
            {'rotation': True, 'hflip': False, 'vflip': False},
            {'rotation': False, 'hflip': False, 'vflip': False},
        ]
        for i, tile in enumerate(tiles[:6]):
            self.assertEqual(tile.flags, flags[i])

    def test_quads(self):
        self.assertEqual(len(self.teemap.layers[0].quads), 1)
        self.assertEqual(len(self.teemap.layers[1].quads), 2)
        pos_envs = [-1, -1, 0]
        pos_env_offsets = [0, 0, 0]
        color_envs = [-1, -1, 1]
        color_env_offsets = [0, 0, 0]
        points = [
            [
                (-800000, -600000),
                (800000, -600000),
                (-800000, 600000),
                (800000, 600000),
                (32768, 32768)
            ], [
                (329099, 208820),
                (608709, 162163),
                (304402, 515873),
                (773381, 589973),
                (361867, 241588)
            ], [
                (-194633, 306165),
                (-13007, 301225),
                (-286028, 556954),
                (-13007, 492731),
                (-111637, 400134)
            ]
        ]
        texcoords = [
            [
                (0, 0),
                (1024, 0),
                (0, 1024),
                (1024, 1024)
            ], [
                (0, 0),
                (1024, 0),
                (0, 1024),
                (1024, 1024)
            ], [
                (2215, -1076),
                (3204, -1076),
                (2215, 946),
                (3204, 946)
            ]
        ]

        quads = []
        for layer in self.teemap.layers:
            if isinstance(layer, items.QuadLayer):
                quads.extend(layer.quads)
        for i, quad in enumerate(quads):
            self.assertEqual(quad.pos_env, pos_envs[i])
            self.assertEqual(quad.pos_env_offset, pos_env_offsets[i])
            self.assertEqual(quad.color_env, color_envs[i])
            self.assertEqual(quad.color_env_offset, color_env_offsets[i])
            self.assertEqual(quad.texcoords, texcoords[i])
            self.assertEqual(quad.points, points[i])

    def test_envpoints(self):
        times = [0, 722, 835, 2062, 0, 99, 643, 861, 1000]
        curvetypes = [4, 0, 4, 1, 1, 1, 1, 1, 1]
        values = [
            [0, 0, 0, 0],
            [0, 0, 207678, 9600],
            [0, 0, 213958, 9600],
            [0, 0, -3105, 0],
            [1, 1, 1, 767],
            [1, 355, 514, 843],
            [1,  289, 995, 959],
            [824, 143, 86, 597],
            [1, 1, 1, 1]
        ]
        for i, envpoint in enumerate(self.teemap.envpoints):
            self.assertEqual(envpoint.time, times[i])
            self.assertEqual(envpoint.curvetype, curvetypes[i])
            self.assertEqual(envpoint.values, values[i])

    def test_save(self):
        self.teemap.save('test_tmp/copy.map')
        self.teemap.save('test_tmp/copy2')
        self.assertTrue(filecmp.cmp('tml/test_maps/vanilla.map',
                                    'test_tmp/copy.map'))
        self.assertTrue(filecmp.cmp('tml/test_maps/vanilla.map',
                                    'test_tmp/copy2.map'))
    def test_validate(self):
        teemap = Teemap()
        self.assertRaises(MapError, teemap.validate)
        group = items.Group()
        group.layers.append(items.TileLayer(game=True))
        teemap.groups.append(group)
        self.assertTrue(teemap.validate())
        group.layers.append(items.TileLayer(game=True))
        self.assertRaises(MapError, teemap.validate)


if __name__ == '__main__':
    unittest.main()
