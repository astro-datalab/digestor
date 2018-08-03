.. Digestor documentation master file, created by
   sphinx-quickstart on Fri Jun  8 15:16:09 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Digestor's documentation!
====================================

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   api

Data Lab Database Loading Notes
===============================

* ``/net/dl1/users/datalab/ingest_party/Tutorial.txt``.
* Use ``gp02`` as the staging database::

    psql tapdb datalab

* Use ``/dl2/data`` for scratch space as needed.
* There are several columns that Data Lab will add to all tables, including
  HTM and HEALPix columns.
* `STILTS <http://www.star.bris.ac.uk/~mbt/stilts/sun256/sun256.html>`_
* The :command:`stilts` ``explodeall`` command converts array-valued columns
  into scalar columns. The columns can be renamed as needed at a later stage.
  ``explodeall`` creates 1-based columns, not 0-based columns.
* :command:`stilts` can load the database directly, but slowly.
* Look for scripts called ``zz*`` or ``_zz*`` in ``/dl2/data``.
* `fits2db <https://github.com/noao-datalab/fits2db>`_.
* `TapSchema <http://gitlab.noao.edu/weaver/TapSchema>`_ has the Data Lab
  table definitions.
* Treat ``varchar(N)`` columns the same as ``text`` when ordering.

TO DO
=====

* SQL functions for ``specObjID``, etc.
* Some primary keys are in the range where a signed 64-bit integer would be
  negative, *i.e.* :math:`2^{63} < k < 2^{64} - 1`.  Need functions to
  deal with this in SQL.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
