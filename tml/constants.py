# -*- coding: utf-8 -*-

import os

ITEM_TYPES = ('version', 'info', 'image', 'envelope', 'group', 'layer',
              'envpoint')
LAYER_TYPES = ('invalid', 'game', 'tile', 'quad')
TML_DIR = os.path.dirname(os.path.abspath(__file__))