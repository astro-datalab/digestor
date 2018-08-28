=======================================
General Data Lab Database Loading Notes
=======================================

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
* ``random_id`` is added by :command:`fits2db --rid=random_id`.
* Example :command:`fits2db`::

    fits2db --sql=postgres --truncate --rid=random_id -B \
        -t sdss_dr14.specobjall sdss_dr14.specobjall.fits | \
        psql tapdb datalab

* When :command:`FITS2DB` adds the ``random_id`` column, it does not
  obey the ordering of the FITS file or the SQL file.
* `TAP Standard <http://www.ivoa.net/documents/TAP/20180416/PR-TAP-1.1-20180416.html>`_.
