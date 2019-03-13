==================
SDSS Loading Notes
==================

SQL
---

Example pre-load SQL code::

    CREATE SCHEMA IF NOT EXISTS sdss_dr14;
    GRANT USAGE ON SCHEMA sdss_dr14 TO dlquery;
    --
    -- Version for FITS-style unsigned integers.  This function is no
    -- longer required.
    --
    -- CREATE OR REPLACE FUNCTION sdss_dr14.uint64(id bigint) RETURNS numeric(20,0) AS $$
    -- DECLARE
    --     tzero CONSTANT numeric(20,0) := 9223372036854775808;
    -- BEGIN
    --     RETURN CAST(id AS numeric(20,0)) + tzero;
    -- END;
    -- $$ LANGUAGE plpgsql IMMUTABLE;
    --
    -- Version for bitwise-correct signed to unsigned conversion.
    --
    CREATE OR REPLACE FUNCTION sdss_dr14.uint64(id bigint) RETURNS numeric(20,0) AS $$
    DECLARE
        tzero CONSTANT numeric(20,0) := 18446744073709551616;
    BEGIN
        IF id < 0 THEN
            RETURN CAST(id AS numeric(20,0)) + tzero;
        ELSE
            RETURN CAST(id AS numeric(20,0));
        END IF;
    END;
    $$ LANGUAGE plpgsql IMMUTABLE;
    --
    -- Create a SDSS (photo)objID for tables that do not have one.
    --
    CREATE OR REPLACE FUNCTION sdss_dr14.objid(rerun text, run smallint, camcol smallint, field smallint, objnum smallint) RETURNS bigint AS $$
    DECLARE
        skyversion CONSTANT bigint := 2;
        firstfield CONSTANT bigint := 0;
    BEGIN
        RETURN ((skyversion << 59) |
                (CAST(rerun AS bigint) << 48) |
                (CAST(run AS bigint) << 32) |
                (CAST(camcol AS bigint) << 29) |
                (firstfield << 28) |
                (CAST(field AS bigint) << 16) |
                CAST(objnum AS bigint));
    END;
    $$ LANGUAGE plpgsql IMMUTABLE;
    CREATE OR REPLACE FUNCTION sdss_dr14.objid(rerun smallint, run smallint, camcol smallint, field smallint, objnum smallint) RETURNS bigint AS $$
    DECLARE
        skyversion CONSTANT bigint := 2;
        firstfield CONSTANT bigint := 0;
    BEGIN
        RETURN ((skyversion << 59) |
                (CAST(rerun AS bigint) << 48) |
                (CAST(run AS bigint) << 32) |
                (CAST(camcol AS bigint) << 29) |
                (firstfield << 28) |
                (CAST(field AS bigint) << 16) |
                CAST(objnum AS bigint));
    END;
    $$ LANGUAGE plpgsql IMMUTABLE;
    --
    -- Create a SDSS specObjID for tables that do not have one.
    --
    CREATE OR REPLACE FUNCTION sdss_dr14.specobjid(plate smallint, fiber smallint, mjd integer, run2d text) RETURNS bigint AS $$
    DECLARE
        rmjd bigint;
        irun bigint;
        mjd_offset CONSTANT bigint := 50000;
    BEGIN
        rmjd := CAST(mjd AS bigint) - mjd_offset;
        IF run2d LIKE 'v%' THEN
            irun := (10000*(CAST(substring(run2d from 'v(\d+)_\d+_\d+') AS bigint) - 5) +
                        100*CAST(substring(run2d from 'v\d+_(\d+)_\d+') AS bigint) +
                            CAST(substring(run2d from 'v\d+_\d+_(\d+)') AS bigint));
        ELSE
            irun := CAST(run2d AS bigint);
        END IF;
        RETURN ((CAST(plate AS bigint) << 50) |
                (CAST(fiber AS bigint) << 38) |
                (rmjd << 24) |
                (irun << 10));
    END;
    $$ LANGUAGE plpgsql IMMUTABLE;

Example post-load SQL code::

    ---
    --- platex
    ---
    CREATE INDEX platex_q3c_ang2ipix ON sdss_dr14.platex (q3c_ang2ipix(ra, dec)) WITH (fillfactor=100);
    CLUSTER platex_q3c_ang2ipix ON sdss_dr14.platex;
    -- CREATE INDEX platex_glon_q3c_ang2ipix ON sdss_dr14.platex (q3c_ang2ipix(glon, glat)) WITH (fillfactor=100);
    -- CREATE INDEX platex_elon_q3c_ang2ipix ON sdss_dr14.platex (q3c_ang2ipix(elon, elat)) WITH (fillfactor=100);
    ALTER TABLE sdss_dr14.platex ADD PRIMARY KEY (plateid);
    CREATE UNIQUE INDEX platex_uint64_plateid ON sdss_dr14.platex (sdss_dr14.uint64(plateid)) WITH (fillfactor=100);
    CREATE INDEX platex_ra ON sdss_dr14.platex (ra) WITH (fillfactor=100);
    CREATE INDEX platex_dec ON sdss_dr14.platex (dec) WITH (fillfactor=100);
    CREATE INDEX platex_htm9 ON sdss_dr14.platex (htm9) WITH (fillfactor=100);
    CREATE INDEX platex_ring256 ON sdss_dr14.platex (ring256) WITH (fillfactor=100);
    CREATE INDEX platex_nest4096 ON sdss_dr14.platex (nest4096) WITH (fillfactor=100);
    CREATE INDEX platex_random_id ON sdss_dr14.platex (random_id) WITH (fillfactor=100);
    GRANT SELECT ON sdss_dr14.platex TO dlquery;
    --
    -- specobjall
    --
    CREATE INDEX specobjall_q3c_ang2ipix ON sdss_dr14.specobjall (q3c_ang2ipix(ra, dec)) WITH (fillfactor=100);
    CLUSTER specobjall_q3c_ang2ipix ON sdss_dr14.specobjall;
    ALTER TABLE sdss_dr14.specobjall ADD PRIMARY KEY (specobjid);
    CREATE UNIQUE INDEX specobjall_uint64_specobjid ON sdss_dr14.specobjall (sdss_dr14.uint64(specobjid)) WITH (fillfactor=100);
    CREATE INDEX specobjall_uint64_plateid ON sdss_dr14.specobjall (sdss_dr14.uint64(plateid)) WITH (fillfactor=100);
    CREATE INDEX specobjall_ra ON sdss_dr14.specobjall (ra) WITH (fillfactor=100);
    CREATE INDEX specobjall_dec ON sdss_dr14.specobjall (dec) WITH (fillfactor=100);
    CREATE INDEX specobjall_htm9 ON sdss_dr14.specobjall (htm9) WITH (fillfactor=100);
    CREATE INDEX specobjall_ring256 ON sdss_dr14.specobjall (ring256) WITH (fillfactor=100);
    CREATE INDEX specobjall_nest4096 ON sdss_dr14.specobjall (nest4096) WITH (fillfactor=100);
    CREATE INDEX specobjall_random_id ON sdss_dr14.specobjall (random_id) WITH (fillfactor=100);
    ALTER TABLE sdss_dr14.specobjall ADD CONSTRAINT specobjall_platex_fk FOREIGN KEY (plateid) REFERENCES sdss_dr14.platex (plateid);
    CREATE VIEW sdss_dr14.specobj AS SELECT s.* FROM sdss_dr14.specobjall AS s WHERE s.scienceprimary = 1;
    CREATE VIEW sdss_dr14.seguespecobjall AS SELECT s.* FROM sdss_dr14.specobjall AS s JOIN sdss_dr14.platex AS p ON s.plateid = p.plateid WHERE p.programname LIKE 'seg%';
    CREATE VIEW sdss_dr14.segue1specobjall AS SELECT s.* FROM sdss_dr14.specobjall AS s JOIN sdss_dr14.platex AS p ON s.plateid = p.plateid WHERE p.programname LIKE 'seg%' AND p.programname NOT LIKE 'segue2%';
    CREATE VIEW sdss_dr14.segue2specobjall AS SELECT s.* FROM sdss_dr14.specobjall AS s JOIN sdss_dr14.platex AS p ON s.plateid = p.plateid WHERE p.programname LIKE 'segue2%';
    GRANT SELECT ON sdss_dr14.specobjall TO dlquery;
    GRANT SELECT ON sdss_dr14.specobj TO dlquery;
    GRANT SELECT ON sdss_dr14.seguespecobjall TO dlquery;
    GRANT SELECT ON sdss_dr14.segue1specobjall TO dlquery;
    GRANT SELECT ON sdss_dr14.segue2specobjall TO dlquery;
    --
    -- photoplate
    --
    CREATE INDEX photoplate_q3c_ang2ipix ON sdss_dr14.photoplate (q3c_ang2ipix(ra, dec)) WITH (fillfactor=100);
    CLUSTER photoplate_q3c_ang2ipix ON sdss_dr14.photoplate;
    ALTER TABLE sdss_dr14.photoplate ADD PRIMARY KEY (objid);
    CREATE INDEX photoplate_ra ON sdss_dr14.photoplate (ra) WITH (fillfactor=100);
    CREATE INDEX photoplate_dec ON sdss_dr14.photoplate (dec) WITH (fillfactor=100);
    CREATE INDEX photoplate_htm9 ON sdss_dr14.photoplate (htm9) WITH (fillfactor=100);
    CREATE INDEX photoplate_ring256 ON sdss_dr14.photoplate (ring256) WITH (fillfactor=100);
    CREATE INDEX photoplate_nest4096 ON sdss_dr14.photoplate (nest4096) WITH (fillfactor=100);
    CREATE INDEX photoplate_random_id ON sdss_dr14.photoplate (random_id) WITH (fillfactor=100);
    UPDATE sdss_dr14.photoplate SET dered_u = u - extinction_u;
    UPDATE sdss_dr14.photoplate SET dered_g = g - extinction_g;
    UPDATE sdss_dr14.photoplate SET dered_r = r - extinction_r;
    UPDATE sdss_dr14.photoplate SET dered_i = i - extinction_i;
    UPDATE sdss_dr14.photoplate SET dered_z = z - extinction_z;
    GRANT SELECT ON sdss_dr14.photoplate TO dlquery;
    --
    -- dr14q
    --
    CREATE INDEX dr14q_q3c_ang2ipix ON sdss_dr14.dr14q (q3c_ang2ipix(ra, dec)) WITH (fillfactor=100);
    CLUSTER dr14q_q3c_ang2ipix ON sdss_dr14.dr14q;
    ALTER TABLE sdss_dr14.dr14q ADD PRIMARY KEY (specobjid);
    ALTER TABLE sdss_dr14.dr14q ADD CONSTRAINT dr14_platex_fk FOREIGN KEY (plateid) REFERENCES sdss_dr14.platex (plateid);
    ALTER TABLE sdss_dr14.dr14q ADD CONSTRAINT dr14_specobjall_fk FOREIGN KEY (specobjid) REFERENCES sdss_dr14.specobjall (specobjid);
    CREATE INDEX dr14q_ra ON sdss_dr14.dr14q (ra) WITH (fillfactor=100);
    CREATE INDEX dr14q_dec ON sdss_dr14.dr14q (dec) WITH (fillfactor=100);
    CREATE INDEX dr14q_htm9 ON sdss_dr14.dr14q (htm9) WITH (fillfactor=100);
    CREATE INDEX dr14q_ring256 ON sdss_dr14.dr14q (ring256) WITH (fillfactor=100);
    CREATE INDEX dr14q_nest4096 ON sdss_dr14.dr14q (nest4096) WITH (fillfactor=100);
    CREATE INDEX dr14q_random_id ON sdss_dr14.dr14q (random_id) WITH (fillfactor=100);
    GRANT SELECT ON sdss_dr14.dr14q TO dlquery;
    --
    -- dr14q_duplicates
    --
    COPY sdss_dr14.dr14q_duplicates FROM '/net/dl2/data/sdss_dr14/dr14q_duplicates.csv' DELIMITER ',' CSV HEADER;
    ALTER TABLE sdss_dr14.dr14q_duplicates ADD CONSTRAINT dr14_duplicates_primary_specobjall_fk FOREIGN KEY (specobjid) REFERENCES sdss_dr14.specobjall (specobjid);
    ALTER TABLE sdss_dr14.dr14q_duplicates ADD CONSTRAINT dr14_duplicates_specobjall_fk FOREIGN KEY (dupspecobjid) REFERENCES sdss_dr14.specobjall (specobjid);
    GRANT SELECT ON sdss_dr14.dr14q_duplicates TO dlquery;


Files
-----

Dealing with photoPlate Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. ``setenv _JAVA_OPTIONS -Djava.io.tmpdir=/data0/tmp``
#. Concatenate the photoPlate and photoPosPlate files, *e.g.* ::

    stilts tcat in=photoPlate-dr14.fits in=photoPosPlate-dr14.fits out=photoPlate-dr14.concat.fits

#. Remove blank and duplicate rows (add equivalent statements to sdss.yaml file)::

    stilts tpipe in=photoPlate-dr14.concat.fits cmd='select skyversion==2' \
        cmd='sort parseLong(objid)' cmd='uniq objid' \
        ofmt=fits-basic out=photoPlate-dr14.uniq.fits

#. Proceed with normal processing::

    sdss2dl -G -t photoplate -v photoPlate-dr14.uniq.fits photoObjAll.sql

DR14Q
~~~~~

Problems
^^^^^^^^

The final version of the DR14 QSO catalog, ``v4_4`` has several problems:

* Columns that are supposed to be integers in the set ``0, 1`` are actually
  floating-point and include some values that are ``2`` or ``NaN``
  (``GALEX_MATCHED``, ``UKIDSS_MATCHED``).
* Columns that are supposed to be pointers to the photometric data are
  complete garbage (``RUN_NUMBER``, ``RERUN_NUMBER``, ``COL_NUMBER``,
  ``FIELD_NUMBER``, ``OBJ_ID``).
* The duplicates columns, which are array-valued, contain spurious zero
  values. For example::

    >>> w = dr14q3['N_SPEC'] == 3
    >>> dr14q3['PLATE_DUPLICATE'][w, :6]
    array([[   0, 6110,    0, 6879,    0, 7595],
           [   0, 6279,    0, 6880,    0, 7663],
           [   0,  689,    0, 4220,    0, 7855],
           ...,
           [   0, 5025,    0, 5026,    0, 7581],
           [   0, 6290,    0, 6308,    0, 6588],
           [   0, 6117,    0, 6127,    0, 7598]], dtype=int32)

* Not every duplicate is present in the specobjall table, although the
  files still may be present on disk.

Solutions
^^^^^^^^^

* Version ``v3_0`` seems to have good values of ``GALEX_MATCHED`` and
  ``UKIDSS_MATCHED``.  *However*, in ``v3_0``, *all* values are zero.
  Just forcibly convert to integer, coerce ``NaN`` to zero, and document.
* Ignore the photometric information entirely.  That can be obtained by
  matching to the ``specobj`` view.
* Move duplicates to a separate "join" table which maps primary ``specObjID``
  to duplicate ``specObjID``.  Not every duplicate will be included, unfortunately,
  but the vast majority will.
* Also include plate, mjd, fiber in duplicates.  Flag duplicates that may
  only exist on disk.

Notes
^^^^^

* Be careful when computing ``specObjID``, there are some SEGUE spectra.
* Binary loading still doesn't work as of March 2019::

    fits2db --sql=postgres --truncate -t sdss_dr14.dr14q sdss_dr14.dr14q.fits | psql tapdb datalab
