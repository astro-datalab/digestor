--
-- Create a SDSS "JOIN" ID that can be used across data releases.
--
CREATE OR REPLACE FUNCTION sdss_dr14.sdss_joinid(plate smallint, fiber smallint, mjd integer) RETURNS bigint AS $$
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
CREATE OR REPLACE FUNCTION sdss_dr14.sdss_joinid(specobjid bigint) RETURNS bigint AS $$
DECLARE
    run2dmask CONSTANT bigint := -16777216;
BEGIN
    RETURN (specobjid & run2dmask);
END;
$$ LANGUAGE plpgsql IMMUTABLE;
--
-- Add sdss_joinid to sdss_dr14.specobjall.
--
ALTER TABLE sdss_dr14.specobjall ADD COLUMN sdss_joinid bigint;
UPDATE sdss_dr14.specobjall SET sdss_joinid = sdss_dr14.sdss_joinid(specobjid);
CREATE UNIQUE INDEX specobjall_sdss_joinid ON sdss_dr14.specobjall (sdss_joinid) WITH (fillfactor=100);
ANALYZE sdss_dr14.specobjall;
--
-- Update views
--
CREATE OR REPLACE VIEW sdss_dr14.specobj AS SELECT s.* FROM sdss_dr14.specobjall AS s WHERE s.scienceprimary = 1;
CREATE OR REPLACE VIEW sdss_dr14.seguespecobjall AS SELECT s.* FROM sdss_dr14.specobjall AS s JOIN sdss_dr16.platex AS p ON s.plateid = p.plateid WHERE p.programname LIKE 'seg%';
CREATE OR REPLACE VIEW sdss_dr14.segue1specobjall AS SELECT s.* FROM sdss_dr14.specobjall AS s JOIN sdss_dr16.platex AS p ON s.plateid = p.plateid WHERE p.programname LIKE 'seg%' AND p.programname NOT LIKE 'segue2%';
CREATE OR REPLACE VIEW sdss_dr14.segue2specobjall AS SELECT s.* FROM sdss_dr14.specobjall AS s JOIN sdss_dr16.platex AS p ON s.plateid = p.plateid WHERE p.programname LIKE 'segue2%';
--
-- Add sdss_joinid to sdss_dr14.dr14q.
--
ALTER TABLE sdss_dr14.dr14q ADD COLUMN sdss_joinid bigint;
UPDATE sdss_dr14.dr14q SET sdss_joinid = sdss_dr14.sdss_joinid(specobjid);
CREATE UNIQUE INDEX dr14q_sdss_joinid ON sdss_dr14.dr14q (sdss_joinid) WITH (fillfactor=100);
ANALYZE sdss_dr14.dr14q;
--
-- Add sdss_joinid to sdss_dr14.sdssebossfirefly.
--
ALTER TABLE sdss_dr14.sdssebossfirefly ADD COLUMN sdss_joinid bigint;
UPDATE sdss_dr14.sdssebossfirefly SET sdss_joinid = sdss_dr14.sdss_joinid(specobjid);
CREATE UNIQUE INDEX sdssebossfirefly_sdss_joinid ON sdss_dr14.sdssebossfirefly (sdss_joinid) WITH (fillfactor=100);
ANALYZE sdss_dr14.sdssebossfirefly;
--
-- Add sdss_joinid to sdss_dr14.spiders_quasar.
--
ALTER TABLE sdss_dr14.spiders_quasar ADD COLUMN sdss_joinid bigint;
UPDATE sdss_dr14.spiders_quasar SET sdss_joinid = sdss_dr14.sdss_joinid(specobjid);
CREATE UNIQUE INDEX spiders_quasar_sdss_joinid ON sdss_dr14.spiders_quasar (sdss_joinid) WITH (fillfactor=100);
ANALYZE sdss_dr14.spiders_quasar;
