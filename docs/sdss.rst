==================
SDSS Loading Notes
==================

Example post-load SQL code::

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
    ALTER TABLE sdss_dr14.specobjall ADD CONSTRAINT specobjall_platex_fx FOREIGN KEY (plateid) REFERENCES sdss_dr14.platex (plateid);
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
    UPDATE TABLE sdss_dr14.photoplate SET dered_u = u - extinction_u;
    UPDATE TABLE sdss_dr14.photoplate SET dered_g = g - extinction_g;
    UPDATE TABLE sdss_dr14.photoplate SET dered_r = r - extinction_r;
    UPDATE TABLE sdss_dr14.photoplate SET dered_i = i - extinction_i;
    UPDATE TABLE sdss_dr14.photoplate SET dered_z = z - extinction_z;
    GRANT SELECT ON sdss_dr14.photoplate TO dlquery;
