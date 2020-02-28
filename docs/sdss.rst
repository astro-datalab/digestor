==================
SDSS Loading Notes
==================

SQL
---

Example pre-load SQL code::

    CREATE SCHEMA IF NOT EXISTS sdss_dr16;
    GRANT USAGE ON SCHEMA sdss_dr16 TO dlquery;
    --
    -- Version for FITS-style unsigned integers.  This function is no
    -- longer required.
    --
    -- CREATE OR REPLACE FUNCTION sdss_dr16.uint64(id bigint) RETURNS numeric(20,0) AS $$
    -- DECLARE
    --     tzero CONSTANT numeric(20,0) := 9223372036854775808;
    -- BEGIN
    --     RETURN CAST(id AS numeric(20,0)) + tzero;
    -- END;
    -- $$ LANGUAGE plpgsql IMMUTABLE;
    --
    -- Version for bitwise-correct signed to unsigned conversion.
    --
    CREATE OR REPLACE FUNCTION sdss_dr16.uint64(id bigint) RETURNS numeric(20,0) AS $$
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
    CREATE OR REPLACE FUNCTION sdss_dr16.objid(rerun text, run smallint, camcol smallint, field smallint, objnum smallint) RETURNS bigint AS $$
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
    CREATE OR REPLACE FUNCTION sdss_dr16.objid(rerun smallint, run smallint, camcol smallint, field smallint, objnum smallint) RETURNS bigint AS $$
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
    CREATE OR REPLACE FUNCTION sdss_dr16.specobjid(plate smallint, fiber smallint, mjd integer, run2d text) RETURNS bigint AS $$
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
    CREATE INDEX platex_q3c_ang2ipix ON sdss_dr16.platex (q3c_ang2ipix(ra, dec)) WITH (fillfactor=100);
    CLUSTER platex_q3c_ang2ipix ON sdss_dr16.platex;
    -- CREATE INDEX platex_glon_q3c_ang2ipix ON sdss_dr16.platex (q3c_ang2ipix(glon, glat)) WITH (fillfactor=100);
    -- CREATE INDEX platex_elon_q3c_ang2ipix ON sdss_dr16.platex (q3c_ang2ipix(elon, elat)) WITH (fillfactor=100);
    ALTER TABLE sdss_dr16.platex ADD PRIMARY KEY (plateid);
    CREATE UNIQUE INDEX platex_uint64_plateid ON sdss_dr16.platex (sdss_dr16.uint64(plateid)) WITH (fillfactor=100);
    CREATE INDEX platex_ra ON sdss_dr16.platex (ra) WITH (fillfactor=100);
    CREATE INDEX platex_dec ON sdss_dr16.platex (dec) WITH (fillfactor=100);
    CREATE INDEX platex_elon ON sdss_dr16.platex (elon) WITH (fillfactor=100);
    CREATE INDEX platex_elat ON sdss_dr16.platex (elat) WITH (fillfactor=100);
    CREATE INDEX platex_glon ON sdss_dr16.platex (glon) WITH (fillfactor=100);
    CREATE INDEX platex_glat ON sdss_dr16.platex (glat) WITH (fillfactor=100);
    CREATE INDEX platex_htm9 ON sdss_dr16.platex (htm9) WITH (fillfactor=100);
    CREATE INDEX platex_ring256 ON sdss_dr16.platex (ring256) WITH (fillfactor=100);
    CREATE INDEX platex_nest4096 ON sdss_dr16.platex (nest4096) WITH (fillfactor=100);
    CREATE INDEX platex_random_id ON sdss_dr16.platex (random_id) WITH (fillfactor=100);
    GRANT SELECT ON sdss_dr16.platex TO dlquery;
    --
    -- specobjall
    --
    CREATE INDEX specobjall_q3c_ang2ipix ON sdss_dr16.specobjall (q3c_ang2ipix(ra, dec)) WITH (fillfactor=100);
    CLUSTER specobjall_q3c_ang2ipix ON sdss_dr16.specobjall;
    ALTER TABLE sdss_dr16.specobjall ADD PRIMARY KEY (specobjid);
    CREATE UNIQUE INDEX specobjall_uint64_specobjid ON sdss_dr16.specobjall (sdss_dr16.uint64(specobjid)) WITH (fillfactor=100);
    CREATE INDEX specobjall_uint64_plateid ON sdss_dr16.specobjall (sdss_dr16.uint64(plateid)) WITH (fillfactor=100);
    CREATE INDEX specobjall_ra ON sdss_dr16.specobjall (ra) WITH (fillfactor=100);
    CREATE INDEX specobjall_dec ON sdss_dr16.specobjall (dec) WITH (fillfactor=100);
    CREATE INDEX specobjall_elon ON sdss_dr16.specobjall (elon) WITH (fillfactor=100);
    CREATE INDEX specobjall_elat ON sdss_dr16.specobjall (elat) WITH (fillfactor=100);
    CREATE INDEX specobjall_glon ON sdss_dr16.specobjall (glon) WITH (fillfactor=100);
    CREATE INDEX specobjall_glat ON sdss_dr16.specobjall (glat) WITH (fillfactor=100);
    CREATE INDEX specobjall_htm9 ON sdss_dr16.specobjall (htm9) WITH (fillfactor=100);
    CREATE INDEX specobjall_ring256 ON sdss_dr16.specobjall (ring256) WITH (fillfactor=100);
    CREATE INDEX specobjall_nest4096 ON sdss_dr16.specobjall (nest4096) WITH (fillfactor=100);
    CREATE INDEX specobjall_random_id ON sdss_dr16.specobjall (random_id) WITH (fillfactor=100);
    ALTER TABLE sdss_dr16.specobjall ADD CONSTRAINT specobjall_platex_fk FOREIGN KEY (plateid) REFERENCES sdss_dr16.platex (plateid);
    CREATE VIEW sdss_dr16.specobj AS SELECT s.* FROM sdss_dr16.specobjall AS s WHERE s.scienceprimary = 1;
    CREATE VIEW sdss_dr16.seguespecobjall AS SELECT s.* FROM sdss_dr16.specobjall AS s JOIN sdss_dr16.platex AS p ON s.plateid = p.plateid WHERE p.programname LIKE 'seg%';
    CREATE VIEW sdss_dr16.segue1specobjall AS SELECT s.* FROM sdss_dr16.specobjall AS s JOIN sdss_dr16.platex AS p ON s.plateid = p.plateid WHERE p.programname LIKE 'seg%' AND p.programname NOT LIKE 'segue2%';
    CREATE VIEW sdss_dr16.segue2specobjall AS SELECT s.* FROM sdss_dr16.specobjall AS s JOIN sdss_dr16.platex AS p ON s.plateid = p.plateid WHERE p.programname LIKE 'segue2%';
    GRANT SELECT ON sdss_dr16.specobjall TO dlquery;
    GRANT SELECT ON sdss_dr16.specobj TO dlquery;
    GRANT SELECT ON sdss_dr16.seguespecobjall TO dlquery;
    GRANT SELECT ON sdss_dr16.segue1specobjall TO dlquery;
    GRANT SELECT ON sdss_dr16.segue2specobjall TO dlquery;
    --
    -- photoplate
    --
    CREATE INDEX photoplate_q3c_ang2ipix ON sdss_dr16.photoplate (q3c_ang2ipix(ra, dec)) WITH (fillfactor=100);
    CLUSTER photoplate_q3c_ang2ipix ON sdss_dr16.photoplate;
    ALTER TABLE sdss_dr16.photoplate ADD PRIMARY KEY (objid);
    CREATE INDEX photoplate_ra ON sdss_dr16.photoplate (ra) WITH (fillfactor=100);
    CREATE INDEX photoplate_dec ON sdss_dr16.photoplate (dec) WITH (fillfactor=100);
    CREATE INDEX photoplate_htm9 ON sdss_dr16.photoplate (htm9) WITH (fillfactor=100);
    CREATE INDEX photoplate_ring256 ON sdss_dr16.photoplate (ring256) WITH (fillfactor=100);
    CREATE INDEX photoplate_nest4096 ON sdss_dr16.photoplate (nest4096) WITH (fillfactor=100);
    CREATE INDEX photoplate_random_id ON sdss_dr16.photoplate (random_id) WITH (fillfactor=100);
    UPDATE sdss_dr16.photoplate SET dered_u = u - extinction_u;
    UPDATE sdss_dr16.photoplate SET dered_g = g - extinction_g;
    UPDATE sdss_dr16.photoplate SET dered_r = r - extinction_r;
    UPDATE sdss_dr16.photoplate SET dered_i = i - extinction_i;
    UPDATE sdss_dr16.photoplate SET dered_z = z - extinction_z;
    GRANT SELECT ON sdss_dr16.photoplate TO dlquery;
    --
    -- dr14q
    --
    CREATE INDEX dr14q_q3c_ang2ipix ON sdss_dr16.dr14q (q3c_ang2ipix(ra, dec)) WITH (fillfactor=100);
    CLUSTER dr14q_q3c_ang2ipix ON sdss_dr16.dr14q;
    ALTER TABLE sdss_dr16.dr14q ADD PRIMARY KEY (specobjid);
    CREATE UNIQUE INDEX dr14q_uint64_specobjid ON sdss_dr16.dr14q (sdss_dr16.uint64(specobjid)) WITH (fillfactor=100);
    UPDATE sdss_dr16.dr14q SET disk_only = TRUE WHERE specobjid IN
        (SELECT d.specobjid FROM sdss_dr16.dr14q AS d LEFT JOIN sdss_dr16.specobjall AS s ON d.specobjid = s.specobjid WHERE s.specobjid IS NULL);
    CREATE INDEX dr14q_ra ON sdss_dr16.dr14q (ra) WITH (fillfactor=100);
    CREATE INDEX dr14q_dec ON sdss_dr16.dr14q (dec) WITH (fillfactor=100);
    CREATE INDEX dr14q_htm9 ON sdss_dr16.dr14q (htm9) WITH (fillfactor=100);
    CREATE INDEX dr14q_ring256 ON sdss_dr16.dr14q (ring256) WITH (fillfactor=100);
    CREATE INDEX dr14q_nest4096 ON sdss_dr16.dr14q (nest4096) WITH (fillfactor=100);
    CREATE INDEX dr14q_random_id ON sdss_dr16.dr14q (random_id) WITH (fillfactor=100);
    GRANT SELECT ON sdss_dr16.dr14q TO dlquery;
    --
    -- dr14q_duplicates
    --
    COPY sdss_dr16.dr14q_duplicates FROM '/net/dl2/data/sdss_dr14/dr14q_duplicates.csv' DELIMITER ',' CSV HEADER;
    ALTER TABLE sdss_dr16.dr14q_duplicates ADD CONSTRAINT dr14q_duplicates_primary_specobjall_fk FOREIGN KEY (specobjid) REFERENCES sdss_dr16.specobjall (specobjid);
    -- ALTER TABLE sdss_dr16.dr14q_duplicates ADD CONSTRAINT dr14q_duplicates_specobjall_fk FOREIGN KEY (dupspecobjid) REFERENCES sdss_dr16.specobjall (specobjid);
    UPDATE sdss_dr16.dr14q_duplicates SET disk_only = TRUE WHERE dupspecobjid IN
        (SELECT d.dupspecobjid FROM sdss_dr16.dr14q_duplicates AS d LEFT JOIN sdss_dr16.specobjall AS s ON d.dupspecobjid = s.specobjid WHERE s.specobjid IS NULL);
    GRANT SELECT ON sdss_dr16.dr14q_duplicates TO dlquery;
    --
    -- sdssebossfirefly
    --
    COPY sdss_dr16.sdssebossfirefly FROM '/net/dl2/data/sdss_dr14/sdss_dr16.sdssebossfirefly.csv' DELIMITER ',' CSV HEADER;
    CREATE INDEX sdssebossfirefly_q3c_ang2ipix ON sdss_dr16.sdssebossfirefly (q3c_ang2ipix(plug_ra, plug_dec)) WITH (fillfactor=100);
    CLUSTER sdssebossfirefly_q3c_ang2ipix ON sdss_dr16.sdssebossfirefly;
    ALTER TABLE sdss_dr16.sdssebossfirefly ADD PRIMARY KEY (specobjid);
    CREATE UNIQUE INDEX sdssebossfirefly_uint64_specobjid ON sdss_dr16.sdssebossfirefly (sdss_dr16.uint64(specobjid)) WITH (fillfactor=100);
    ALTER TABLE sdss_dr16.sdssebossfirefly ADD CONSTRAINT sdssebossfirefly_specobjall_fk FOREIGN KEY (specobjid) REFERENCES sdss_dr16.specobjall (specobjid);
    CREATE INDEX sdssebossfirefly_plug_ra ON sdss_dr16.sdssebossfirefly (plug_ra) WITH (fillfactor=100);
    CREATE INDEX sdssebossfirefly_plug_dec ON sdss_dr16.sdssebossfirefly (plug_dec) WITH (fillfactor=100);
    CREATE INDEX sdssebossfirefly_htm9 ON sdss_dr16.sdssebossfirefly (htm9) WITH (fillfactor=100);
    CREATE INDEX sdssebossfirefly_ring256 ON sdss_dr16.sdssebossfirefly (ring256) WITH (fillfactor=100);
    CREATE INDEX sdssebossfirefly_nest4096 ON sdss_dr16.sdssebossfirefly (nest4096) WITH (fillfactor=100);
    CREATE INDEX sdssebossfirefly_random_id ON sdss_dr16.sdssebossfirefly (random_id) WITH (fillfactor=100);
    GRANT SELECT ON sdss_dr16.sdssebossfirefly TO dlquery;
    --
    -- spiders_quasar
    --
    CREATE INDEX spiders_quasar_q3c_ang2ipix ON sdss_dr16.spiders_quasar (q3c_ang2ipix(ra, dec)) WITH (fillfactor=100);
    CREATE INDEX spiders_quasar_plug_q3c_ang2ipix ON sdss_dr16.spiders_quasar (q3c_ang2ipix(plug_ra, plug_dec)) WITH (fillfactor=100);
    CLUSTER spiders_quasar_q3c_ang2ipix ON sdss_dr16.spiders_quasar;
    -- ALTER TABLE sdss_dr16.spiders_quasar ADD PRIMARY KEY (specobjid);
    ALTER TABLE sdss_dr16.spiders_quasar ADD CONSTRAINT spiders_quasar_specobjall_fk FOREIGN KEY (specobjid) REFERENCES sdss_dr16.specobjall (specobjid);
    CREATE INDEX spiders_quasar_ra ON sdss_dr16.spiders_quasar (ra) WITH (fillfactor=100);
    CREATE INDEX spiders_quasar_dec ON sdss_dr16.spiders_quasar (dec) WITH (fillfactor=100);
    CREATE INDEX spiders_quasar_plug_ra ON sdss_dr16.spiders_quasar (plug_ra) WITH (fillfactor=100);
    CREATE INDEX spiders_quasar_plug_dec ON sdss_dr16.spiders_quasar (plug_dec) WITH (fillfactor=100);
    CREATE INDEX spiders_quasar_htm9 ON sdss_dr16.spiders_quasar (htm9) WITH (fillfactor=100);
    CREATE INDEX spiders_quasar_ring256 ON sdss_dr16.spiders_quasar (ring256) WITH (fillfactor=100);
    CREATE INDEX spiders_quasar_nest4096 ON sdss_dr16.spiders_quasar (nest4096) WITH (fillfactor=100);
    CREATE INDEX spiders_quasar_random_id ON sdss_dr16.spiders_quasar (random_id) WITH (fillfactor=100);
    GRANT SELECT ON sdss_dr16.spiders_quasar TO dlquery;



TO DO
-----

* Need to figure out the best way to index glon, glat, elon, elat.  These
  are marked in TapSchema as indexed but are not currently indexed.

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
* Not every "primary" entry in DR14Q is in the specobjall table either.

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
* Flag "primary" entries that only exist on disk.

Notes
^^^^^

* Be careful when computing ``specObjID``, there are some SEGUE spectra.
* Binary loading still doesn't work as of March 2019::

    fits2db --sql=postgres --truncate -t sdss_dr16.dr14q sdss_dr16.dr14q.fits | psql tapdb datalab

Firefly
~~~~~~~

* Remove ``--/U no unit`` from input SQL file.
* For no obvious reason, these columns were left out of the original SQL definition file:
  ``Chabrier_ELODIE_stellar_mass``, ``Chabrier_STELIB_stellar_mass``, ``Salpeter_STELIB_stellar_mass``.
* ``fits2db`` might be choking on long column names plus ``double precision``::

    COPY sdss_dr16.sdssebossfirefly (specobjid,bestobjid,plug_ra,plug_dec,sn_median_all,
        chabrier_miles_age_lightw,chabrier_miles_age_lightw_up,chabrier_miles_age_lightw_low,
        chabrier_miles_metallicity_lightdouble precision,chabrier_miles_metallicity_lightdouble precision,
        chabrier_miles_metallicity_lightdouble precision,chabrier_miles_stellar_mass,
        chabrier_miles_stellar_mass_up,chabrier_miles_stellar_mass_low,chabrier_miles_spm_ebv,
        chabrier_miles_ncomponentsssp,chabrier_miles_c ...


SPIDERS
~~~~~~~

* Need to add units to input SQL file.
