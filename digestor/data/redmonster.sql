CREATE TABLE redmonster (
-------------------------------------------------------------------------------
--/H The DR14 redmonster catalog.
--
--/T This table contains a summary of the redmonster outputs for all spectra.
-------------------------------------------------------------------------------
    qsoID              bigint NOT NULL, --/D Unique, arbitrary database ID.
    specObjID          bigint NOT NULL, --/D Unique database ID based on PLATE, MJD, FIBERID, RUN2D --/K ID_CATALOG
    plateID            bigint NOT NULL, --/D Database ID of Plate
    fiberID            smallint NOT NULL, --/D Spectroscopic fiber number (0-based)
    plate              smallint NOT NULL, --/D Spectroscopic plate number
    mjd                int NOT NULL, --/U days --/D Modified Julian Day of the spectroscopic observation
    dof                int NOT NULL, --/D Degrees of freedom for best fit
    boss_target1       bigint NOT NULL, --/D BOSS survey primary target selection flag
    eboss_target0      bigint NOT NULL, --/D SEQUELS survey primary target selection flag
    eboss_target1      bigint NOT NULL, --/D eBOSS survey primary target selection flag
    z                  real NOT NULL, --/D Redshift
    zErr               real NOT NULL, --/D Redshift error estimate
    class              varchar(15) NOT NULL, --/D Object type classification
    subclass           varchar(12) NOT NULL, --/D Best-fit template parameters
    fname              varchar(32) NOT NULL, --/D Filename of best-fit template
    minvector          varchar(11) NOT NULL, --/D Coordinates of best-fit template in template file
    minrchi2           real NOT NULL, --/D Reduced chi-squared value of best fit
    npoly              int NOT NULL, --/D Number of additive polynomials used in best fit
    npixstep           int NOT NULL, --/D Pixel step size used
    theta              varchar(49) NOT NULL, --/D Coefficients of template and polynomial terms in fit
    zwarning           int NOT NULL, --/D ZWARNING flags
    rchi2diff          real NOT NULL, --/D Reduced chi-squared difference between first and second fit
    chi2null           real NOT NULL, --/D Chi-squared value of polynomial-only model
    sn2data            real NOT NULL --/D Signal-to-noise squared of spectrum
);
