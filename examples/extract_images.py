import os

from tml.tml import Teemap
from tml.constants import TML_DIR

map_path = os.sep.join([TML_DIR, '/maps/dm1'])
t = Teemap(map_path)
try:
    os.mkdir('images')
except OSError, e:
    if e.errno != 17:
        raise e
for image in t.images:
    image.save(os.sep.join(['images', image.name]))
print 'Extracted {0} images.'.format(len(t.images))
