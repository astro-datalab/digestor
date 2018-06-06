--
-- Create a SDSS (photo)objID for tables
-- that do not have one.
--
CREATE OR REPLACE FUNCTION objid(rerun text, run smallint, camcol smallint, field smallint, objnum smallint) RETURNS bigint AS $$
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
CREATE UNIQUE INDEX calibobj_gal_objid_idx ON sdss_dr13.calibobj_gal (objid(rerun, run, camcol, field, id));
CREATE UNIQUE INDEX calibobj_star_objid_idx ON sdss_dr13.calibobj_star (objid(rerun, run, camcol, field, id));
