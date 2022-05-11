--
-- This file is intended to be processed by the Python format method.
--
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
--
-- Create a SDSS "JOIN" ID that can be used across data releases.
--
CREATE OR REPLACE FUNCTION sdss_dr16.sdss_joinid(plate smallint, fiber smallint, mjd integer) RETURNS bigint AS $$
DECLARE
    rmjd bigint;
    mjd_offset CONSTANT bigint := 50000;
BEGIN
    rmjd := CAST(mjd AS bigint) - mjd_offset;
    RETURN ((CAST(plate AS bigint) << 50) |
            (CAST(fiber AS bigint) << 38) |
            (rmjd << 24));
END;
$$ LANGUAGE plpgsql IMMUTABLE;
--
-- Create a SDSS "JOIN" ID that can be used across data releases.
-- The constant run2dmask = ~(2**24 - 1) removes the bits corresponding to
-- run2d from specobjid.
--
CREATE OR REPLACE FUNCTION sdss_dr16.sdss_joinid(specobjid bigint) RETURNS bigint AS $$
DECLARE
    run2dmask CONSTANT bigint := -16777216;
BEGIN
    RETURN (specobjid & run2dmask);
END;
$$ LANGUAGE plpgsql IMMUTABLE;
CREATE TABLE IF NOT EXISTS sdss_dr16.elg_classifier (
    sdss_joinid bigint NOT NULL,
    specobjid bigint NOT NULL,
    z double precision NOT NULL,
    o3_hb double precision NOT NULL,
    o2_hb double precision NOT NULL,
    sigma_o3 double precision NOT NULL,
    sigma_star double precision NOT NULL,
    u_g double precision NOT NULL,
    g_r double precision NOT NULL,
    r_i double precision NOT NULL,
    i_z double precision NOT NULL,
    mjd integer NOT NULL,
    random_id real NOT NULL,
    plate smallint NOT NULL,
    fiberid smallint NOT NULL,
    type smallint NOT NULL
) WITH (fillfactor=100);
