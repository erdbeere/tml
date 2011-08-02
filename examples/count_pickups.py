import os

from tml.tml import Teemap
from tml.constants import TML_DIR, TILEINDEX

map_path = os.sep.join([TML_DIR, '/maps/dm1'])
t = Teemap(map_path)
pickups = {
    'shotgun': 0,
    'grenade': 0,
    'rifle': 0,
    'ninja': 0,
    'health': 0,
    'armor': 0,
    # 'solid': 0,
    # 'air': 0,
    # 'death': 0,
    # 'nohook': 0,
}
for tile in t.gamelayer.tiles:
    for key, value in pickups.iteritems():
        if tile.index == TILEINDEX[key]:
            pickups[key] += 1

for k, v in pickups.iteritems():
    print '{value:3}x {key}'.format(value=v, key=k)
