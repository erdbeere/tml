# -*- coding: utf-8 -*-
"""
    Important constants.

    :copyright: 2010-2011 by the TML Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""

import os

ITEM_VERSION, ITEM_INFO, ITEM_IMAGE, ITEM_ENVELOPE, ITEM_GROUP, ITEM_LAYER, \
    ITEM_ENVPOINT = range(7) # TODOD: nice?

# TODO: do we need this?
ITEM_TYPES = ('version', 'info', 'image', 'envelope', 'group', 'layer',
              'envpoint')
LAYER_TYPES = ('invalid', 'game', 'tile', 'quad')
TML_DIR = os.path.dirname(os.path.abspath(__file__))