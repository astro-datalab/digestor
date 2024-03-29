CREATE TABLE sdss_dr16.dr16q_duplicates (
-------------------------------------------------------------------------------
--/H A join table linking the spectra in dr16q to other observations of the same object.
--
-------------------------------------------------------------------------------
    specobjid     bigint NOT NULL, --/D specObjID of the primary spectrum in the dr16q table.
    dupspecobjid  bigint NOT NULL, --/D specObjID of other observations of the same object.
    run2d         varchar(32) NOT NULL, --/D 2D Reduction version of spectrum
    plate         smallint NOT NULL, --/D Spectroscopic plate number
    mjd           integer NOT NULL, --/U days --/D Modified Julian Day of the spectroscopic observation
    fiberid       smallint NOT NULL, --/D Spectroscopic fiber number
    disk_only     boolean NOT NULL --/D TRUE if the duplicate is not listed in specobjall.
);
