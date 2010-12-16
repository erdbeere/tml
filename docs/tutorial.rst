========
Tutorial
========

This tutorial will help you using and understanding this library.

Create, load and save a map
===========================
Creating a new teeworlds map is pretty simple. You just need to create an
instance of the `Teemap` class in our `tml` module. A gamelayer and a
background quad will be automatically created for you.
If you want you can load an existing teeworlds map with the load method
and of course save them, you can give the path as the first parameter.
The "map" fileextension is optional.

>>> from tml import Teemap
>>> twmap = Teemap()
>>> twmap.load('dm1_test')
>>> twmap.save('unnamed')

.. autoclass:: tml.Teemap
   :members: load, save

Accessing the data
==================
You may wonder where you can find the different things of a teeworlds map.
The order is similar to the order in the original teeworlds client. You have
a list of groups, and in those groups a list of the Tile and Quadlayers and the
Gamelayer (which is a Tilelayer with a special flag). Also there are three more
lists with the images (image name and if it is embedded additional the image
itself), envelopes and envpoints.

>>> from tml import Teemap
>>> t = Teemap()
>>> t.load('dm1_test')
>>> t.envelopes
[<Envelope>, <Envelope>, <Envelope>, <Envelope>, <Envelope>, <Envelope>]
>>> t.envpoints
[<Envpoint>, <Envpoint>, <Envpoint>, <Envpoint>, <Envpoint>, <Envpoint>, <Envpoint>, <Envpoint>, <Envpoint>, <Envpoint>, <Envpoint>, <Envpoint>, <Envpoint>]
>>> t.images
[<Image>, <Image>, <Image>, <Image>, <Image>, <Image>, <Image>]
>>> t.images[0].name
'bg_cloud1'
>>> t.images[5].name
'mountains'
>>> t.groups
[<Group>, <Group>, <Group>, <Group>, <Group>, <Group>, <Group>]
>>> t.groups[1].layers
[<Quad layer>, <Quad layer>]
>>> t.groups[6].layers
[<Tile layer (60x50)>, <Tile layer (60x50)>, <Tile layer (60x50)>, <Tile layer (60x50)>, <Tile layer (60x50)>]


Modifying
=========

.. autoclass:: items.TileLayer
   :members:
