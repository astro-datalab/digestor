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
* Example :command:`fits2db`::

    fits2db --sql=postgres --truncate --rid=random_id -B \
        -t sdss_dr14.specobjall sdss_dr14.specobjall.fits | \
        psql tapdb datalab

* Example post-load SQL::

    CREATE OR REPLACE FUNCTION sdss_dr14.uint64(id bigint) RETURNS numeric(20,0) AS $$
    DECLARE
        tzero CONSTANT numeric(20,0) := 9223372036854775808;
    BEGIN
        RETURN CAST(id AS numeric(20,0)) + tzero;
    END;
    $$ LANGUAGE plpgsql IMMUTABLE;
    CREATE INDEX platex_q3c_ang2ipix ON sdss_dr14.platex (q3c_ang2ipix(ra, dec)) WITH (fillfactor=100);
    CLUSTER platex_q3c_ang2ipix ON sdss_dr14.platex;
    -- CREATE INDEX platex_glon_q3c_ang2ipix ON sdss_dr14.platex (q3c_ang2ipix(glon, glat)) WITH (fillfactor=100);
    -- CREATE INDEX platex_elon_q3c_ang2ipix ON sdss_dr14.platex (q3c_ang2ipix(elon, elat)) WITH (fillfactor=100);
    ALTER TABLE sdss_dr14.platex ADD PRIMARY KEY (plateid);
    CREATE UNIQUE INDEX platex_uint64_plateid ON sdss_dr14.platex (sdss_dr14.uint64(plateid)) WITH (fillfactor=100);
    CREATE INDEX specobjall_q3c_ang2ipix ON sdss_dr14.specobjall (q3c_ang2ipix(ra, dec)) WITH (fillfactor=100);
    CLUSTER specobjall_q3c_ang2ipix ON sdss_dr14.specobjall;
    ALTER TABLE sdss_dr14.specobjall ADD PRIMARY KEY (specobjid);
    CREATE UNIQUE INDEX specobjall_uint64_specobjid ON sdss_dr14.specobjall (sdss_dr14.uint64(specobjid)) WITH (fillfactor=100);
    CREATE INDEX specobjall_uint64_plateid ON sdss_dr14.specobjall (sdss_dr14.uint64(plateid)) WITH (fillfactor=100);
    ALTER TABLE sdss_dr14.specobjall ADD CONSTRAINT specobjall_platex_fx FOREIGN KEY (plateid) REFERENCES sdss_dr14.platex (plateid);
    CREATE VIEW sdss_dr14.specobj AS SELECT * FROM sdss_dr14.specobjall AS s WHERE s.scienceprimary = 1;
    CREATE VIEW sdss_dr14.seguespecobjall AS SELECT s.* FROM sdss_dr14.specobjall AS s JOIN sdss_dr14.platex AS p ON s.plateid = p.plateid WHERE p.programname LIKE 'seg%';
    CREATE VIEW sdss_dr14.segue1specobjall AS SELECT s.* FROM sdss_dr14.specobjall AS s JOIN sdss_dr14.platex AS p ON s.plateid = p.plateid WHERE p.programname LIKE 'seg%' AND p.programname NOT LIKE 'segue2%';
    CREATE VIEW sdss_dr14.segue2specobjall AS SELECT s.* FROM sdss_dr14.specobjall AS s JOIN sdss_dr14.platex AS p ON s.plateid = p.plateid WHERE p.programname LIKE 'segue2%';
    GRANT USAGE ON SCHEMA sdss_dr14 TO dlquery;
    GRANT SELECT ON sdss_dr14.platex TO dlquery;
    GRANT SELECT ON sdss_dr14.specobjall TO dlquery;
    GRANT SELECT ON sdss_dr14.specobj TO dlquery;
    GRANT SELECT ON sdss_dr14.seguespecobjall TO dlquery;
    GRANT SELECT ON sdss_dr14.segue1specobjall TO dlquery;
    GRANT SELECT ON sdss_dr14.segue2specobjall TO dlquery;

TO DO
=====

* Some primary keys are in the range where a signed 64-bit integer would be
  negative, *i.e.* :math:`2^{63} < k < 2^{64} - 1`.  Need functions to
  deal with this in SQL.
* ``bestObjID`` has some rows that are blank strings.  Those should be set to zero.
  In general, need to be able to deal with ``inf``, ``nan``.
* Set SDSS-style "null values":

  - During string to bigint conversions, blank strings become zero.
  - For real and double precision, ``not numpy.isfinite()`` goes to -9999.
  - For real, ``abs(x) > 3.4e+38`` goes to -9999.
  - Convert commas to '%2C'?  Not really needed if we're avoiding CSV.

* Only convert to ``np.uint64`` if absolutely necessary.
* ``random_id`` is added by :command:`fits2db --rid=random_id`.
* Set ``uint=False`` when writing final FITS file?
* SQL functions for ``specObjID``, etc.
* Post-load SQL.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
