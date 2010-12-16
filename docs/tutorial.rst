========
Tutorial
========

This tutorial will help you using and understanding this library.

Create, load and save a map
===========================
Creating a new teeworlds map is pretty simple. You just need to create an
instance of the "Teemap" class in our "tml" module. A gamelayer and a
background quad will be automatically created for you.
If you want you can load an existing teeworlds map with the load method
and of course save them, you can give the path as the first parameter.
The "map" file extension is optional.

>>> from tml import Teemap
>>> twmap = Teemap()
>>> twmap.load('dm1_test')
>>> twmap.save('unnamed')

.. autoclass:: tml.Teemap
   :members: load, save
