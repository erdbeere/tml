# -*- coding: utf-8 -*-
"""
    Important constants.

    :copyright: 2010-2011 by the TML Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""

import os

ITEM_VERSION, ITEM_INFO, ITEM_IMAGE, ITEM_ENVELOPE, ITEM_GROUP, ITEM_LAYER, \
    ITEM_ENVPOINT = range(7)

LAYERTYPE_INVALID, LAYERTYPE_GAME, LAYERTYPE_TILES, LAYERTYPE_QUADS = range(4)

# TODO: do we need this?
ITEM_TYPES = ('version', 'info', 'image', 'envelope', 'group', 'layer',
              'envpoint')

TML_DIR = os.path.dirname(os.path.abspath(__file__))

TILEFLAG_VFLIP = 1
TILEFLAG_HFLIP = 2
TILEFLAG_OPAQUE = 4
TILEFLAG_ROTATE = 8

LAYERFLAG_DETAIL = 1

TILEINDEX  = {
    'air': 0,
    'solid': 1,
    'death': 2,
    'nohook': 3,
    'spawn': 192,
    'spawn_red': 193,
    'spawn_blue': 194,
    'flagstand_red': 195,
    'flagstand_blue': 196,
    'armor': 197,
    'health': 198,
    'shotgun': 199,
    'grenade': 200,
    'ninja': 201,
    'rifle': 202,
}
