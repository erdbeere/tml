===============
Classes
===============

In this section you will learn about every class and its functions.

Teemap
======

.. autoclass:: tml.tml.Teemap
   :members:

   .. attribute:: images

      List of all :class:`images <tml.items.Image>` included in the map,
      external and embedded.

   .. attribute:: groups

      List of the :class:`groups <tml.items.Group>`, ordered like they are
      placed in teeworlds.

   .. attribute:: mapinfo

      :class:`MapInfo <tml.tml.items.MapInfo>` object, contains information like
      author and maplicense. Can be ``None``.

   .. attribute:: envelopes

      List of all :class:`envelopes <tml.items.Envelope>` of the map.

Header
======

.. automodule:: tml.tml
   :members: Header
