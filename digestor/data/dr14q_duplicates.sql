CREATE TABLE dr14q_duplicates (
-------------------------------------------------------------------------------
--/H A join table linking the spectra in dr14q to other observations of the same object.
--
-------------------------------------------------------------------------------
    specObjID     bigint NOT NULL, --/D specObjID of the primary spectrum in the dr14q table.
    dupSpecObjID  bigint NOT NULL --/D specObjID of other observations of the same object.
);
