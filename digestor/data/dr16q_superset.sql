CREATE TABLE dr16q_superset (
-------------------------------------------------------------------------------
--/H The DR16 QSO Superset Catalog (v3)
--
--/T The primary DR16Q is derived from this superset of objects targeted as quasars. 
--/T The catalog is documented in more detail at the DR16Q VAC algorithm page
--/T (https://www.sdss.org/dr16/algorithms/qso_catalog)
--/T which also includes a link to the ApJS paper (Lyke et al. 2020). The catalog contains 
--/T spectroscopic and photometric data for over 1.44 million observations. To ensure 
--/T completeness, known quasars from previous catalog releases (DR7Q and DR12Q) have 
--/T also been included. The file can be found at: 
--/T https://data.sdss.org/sas/dr16/eboss/qso/DR16Q/DR16Q_Superset_v3.fitsDR16Q_Superset_v3.fits
-------------------------------------------------------------------------------

specobjid               BIGINT NOT NULL, --/D Unique database ID based on PLATE, MJD, FIBERID, RUN2D --/K ID_CATALOG
SDSS_NAME               VARCHAR(34) NOT NULL, --/D  SDSS-DR16 designation (hhmmss.ss±ddmmss.s, J2000)
RA                      FLOAT NOT NULL, --/U deg  --/D  Right ascension in decimal degrees (J2000)
DEC                     FLOAT NOT NULL, --/U deg  --/D  Declination in decimal degrees (J2000)
RUN2D                   varchar(32) NOT NULL, --/D Spectroscopic reduction version
PLATE                   TINYINT NOT NULL, --/D   Spectroscopic plate number
MJD                     INT NOT NULL, --/U days  --/D   Modified Julian day of the spectroscopic observation
FIBERID                 TINYINT NOT NULL, --/D   Fiber ID number
AUTOCLASS_PQN           VARCHAR(8) NOT NULL, --/D  Object classification post-QuasarNET
AUTOCLASS_DR14Q         VARCHAR(8) NOT NULL, --/D  Object classification based only on the DR14Q algorithm
IS_QSO_QN               INT NOT NULL, --/D   Binary flag for QuasarNET quasar identification
Z_QN                    FLOAT NOT NULL, --/D  Systemic redshift from QuasarNET
RANDOM_SELECT           INT NOT NULL, --/D   Binary flag indicating objects selected for random visual inspection
Z_10K                   FLOAT NOT NULL, --/D  Redshift from visual inspection in random set
Z_CONF_10K              INT NOT NULL, --/D   Confidence rating for visual inspection redshift in random set
PIPE_CORR_10K           INT NOT NULL, --/D   Binary flag indicating if the automated pipeline classification and redshift were correct in the random set
IS_QSO_10K              INT NOT NULL, --/D   Binary flag for random set quasar identification
PRIM_REC                INT NOT NULL, --/D   Flag to indicate if observation is primary observation appearing in DR16Q or a duplicate
THING_ID                BIGINT NOT NULL, --/D   SDSS identifier
Z_VI                    FLOAT NOT NULL, --/D  Visual inspection redshift
Z_CONF                  INT NOT NULL, --/D   Confidence rating for visual inspection redshift
CLASS_PERSON            INT NOT NULL, --/D   Object classification from visual inspection
Z_DR12Q                 FLOAT NOT NULL, --/D  Redshift taken from DR12Q visual inspection
IS_QSO_DR12Q            INT NOT NULL, --/D   Flag indicating if an object was a quasar in DR12Q
Z_DR7Q_SCH              FLOAT NOT NULL, --/D  Redshift taken from DR7Q Schneider et al (2010) catalog
IS_QSO_DR7Q             INT NOT NULL, --/D   Flag indicating if an object was a quasar in DR7Q
Z_DR6Q_HW               FLOAT NOT NULL, --/D  Redshift taken from DR6 Hewett and Wild (2010) catalog
Z_DR7Q_HW               FLOAT NOT NULL, --/D  Redshift using Hewett and Wild (2010) updates for DR7Q sources from the Shen et al. (2011) catalog
IS_QSO_FINAL            INT NOT NULL, --/D   Flag indicating quasars to be included in final catalog
Z                       FLOAT NOT NULL, --/D  Best available redshift taken from Z_VI, Z_PIPE, Z_DR12Q, Z_DR7Q_SCH, Z_DR6Q_HW, and Z_10K
ZSOURCE                 VARCHAR(14) NOT NULL, --/D  Origin of the reported redshift in Z --/F SOURCE_Z
Z_PIPE                  FLOAT NOT NULL, --/D  SDSS automated pipeline redshift
ZWARNING                INT NOT NULL, --/D   Quality flag on the pipeline redshift estimate
OBJID                   VARCHAR(21) NOT NULL, --/D  SDSS object identification number
Z_PCA                   FLOAT NOT NULL, --/D  PCA-derived systemic redshift from redvsblue
ZWARN_PCA               BIGINT NOT NULL, --/D   Warning flag for redvsblue redshift
DELTACHI2_PCA           FLOAT NOT NULL, --/D  Delta χ2 for PCA redshift vs. cubic continuum fit
Z_HALPHA                FLOAT NOT NULL, --/D  PCA line redshift for Hα from redvsblue
ZWARN_HALPHA            BIGINT NOT NULL, --/D   Warning flag for Hα redshift
DELTACHI2_HALPHA        FLOAT NOT NULL, --/D  Delta χ2 for Hα line redshift vs. cubic continuum fit
Z_HBETA                 FLOAT NOT NULL, --/D  PCA line redshift for Hβ from redvsblue
ZWARN_HBETA             BIGINT NOT NULL, --/D   Warning flag for Hβ redshift
DELTACHI2_HBETA         FLOAT NOT NULL, --/D  Delta χ2 for Hβ line redshift vs. cubic continuum fit
Z_MGII                  FLOAT NOT NULL, --/D  PCA line redshift for Mg II λ2799 from redvsblue
ZWARN_MGII              BIGINT NOT NULL, --/D   Warning flag for Mg II λ2799 redshift
DELTACHI2_MGII          FLOAT NOT NULL, --/D  Delta χ2 for Mg II λ2799 line redshift vs. cubic continuum fit
Z_CIII                  FLOAT NOT NULL, --/D  PCA line redshift for C III] λ1908 from redvsblue
ZWARN_CIII              BIGINT NOT NULL, --/D   Warning flag for C III] λ1908 redshift
DELTACHI2_CIII          FLOAT NOT NULL, --/D  Delta χ2 for C III] λ1908 line redshift vs. cubic continuum fit
Z_CIV                   FLOAT NOT NULL, --/D  PCA line redshift for C IV λ1549 from redvsblue
ZWARN_CIV               BIGINT NOT NULL, --/D   Warning flag for C IV λ1549 redshift
DELTACHI2_CIV           FLOAT NOT NULL, --/D  Delta χ2 for C IV λ1549 line redshift vs. cubic continuum fit
Z_LYA                   FLOAT NOT NULL, --/D  PCA line redshift for Lyα from redvsblue
ZWARN_LYA               BIGINT NOT NULL, --/D   Warning flag for Lyα redshift
DELTACHI2_LYA           FLOAT NOT NULL, --/D  Delta χ2 for Lyα line redshift vs. cubic continuum fit
Z_DLA_1                 FLOAT NOT NULL, --/D  Redshift for damped Lyα features --/F Z_DLA 0
Z_DLA_2                 FLOAT NOT NULL, --/D  Redshift for damped Lyα features --/F Z_DLA 1
Z_DLA_3                 FLOAT NOT NULL, --/D  Redshift for damped Lyα features --/F Z_DLA 2
Z_DLA_4                 FLOAT NOT NULL, --/D  Redshift for damped Lyα features --/F Z_DLA 3
Z_DLA_5                 FLOAT NOT NULL, --/D  Redshift for damped Lyα features --/F Z_DLA 4
NHI_DLA_1               FLOAT NOT NULL, --/D  Absorber column density for damped Lyα features --/F Z_DLA 0
NHI_DLA_2               FLOAT NOT NULL, --/D  Absorber column density for damped Lyα features --/F Z_DLA 1
NHI_DLA_3               FLOAT NOT NULL, --/D  Absorber column density for damped Lyα features --/F Z_DLA 2
NHI_DLA_4               FLOAT NOT NULL, --/D  Absorber column density for damped Lyα features --/F Z_DLA 3
NHI_DLA_5               FLOAT NOT NULL, --/D  Absorber column density for damped Lyα features --/F Z_DLA 4
CONF_DLA_1              FLOAT NOT NULL, --/D  Confidence of detection for damped Lyα features --/F Z_DLA 0
CONF_DLA_2              FLOAT NOT NULL, --/D  Confidence of detection for damped Lyα features --/F Z_DLA 1
CONF_DLA_3              FLOAT NOT NULL, --/D  Confidence of detection for damped Lyα features --/F Z_DLA 2
CONF_DLA_4              FLOAT NOT NULL, --/D  Confidence of detection for damped Lyα features --/F Z_DLA 3
CONF_DLA_5              FLOAT NOT NULL, --/D  Confidence of detection for damped Lyα features --/F Z_DLA 4
BAL_PROB                FLOAT NOT NULL, --/D   BAL probability
BI_CIV                  FLOAT NOT NULL, --/U km/s --/D  BALnicity index for C IV λ1549 region
ERR_BI_CIV              FLOAT NOT NULL, --/U km/s --/D  Uncertainty of BI for C IV λ1549 region
AI_CIV                  FLOAT NOT NULL, --/D  Absorption index for C IV λ1549 region
ERR_AI_CIV              FLOAT NOT NULL, --/D  Uncertainty of absorption index for C IV λ1549 region
BI_SIIV                 FLOAT NOT NULL, --/D  BALnicity index for Si IV λ1396 region
ERR_BI_SIIV             FLOAT NOT NULL, --/D  Uncertainty of BI for Si IV λ1396 region
AI_SIIV                 FLOAT NOT NULL, --/D  Absorption index for Si IV λ1396 region
ERR_AI_SIIV             FLOAT NOT NULL, --/D  Uncertainty of absorption index for Si IV λ1396 region
BOSS_TARGET1            BIGINT NOT NULL, --/D   BOSS target selection for main survey
EBOSS_TARGET0           BIGINT NOT NULL, --/D   Target selection flag for the eBOSS pilot survey (SEQUELS)
EBOSS_TARGET1           BIGINT NOT NULL, --/D   eBOSS target selection flag
EBOSS_TARGET2           BIGINT NOT NULL, --/D   eBOSS target selection flag
ANCILLARY_TARGET1       BIGINT NOT NULL, --/D   BOSS target selection flag for ancillary programs
ANCILLARY_TARGET2       BIGINT NOT NULL, --/D   BOSS target selection flag for ancillary programs
NSPEC_SDSS              INT NOT NULL, --/D   Number of additional observations from SDSS-I/II
NSPEC_BOSS              INT NOT NULL, --/D   Number of additional observations from BOSS/eBOSS
NSPEC                   INT NOT NULL, --/D   Total number of additional observations
LAMBDA_EFF              FLOAT NOT NULL, --/D  Wavelength to optimize hold location for, in Angstroms
ZOFFSET                 FLOAT NOT NULL, --/D  Backstopping offset distance, in μm
XFOCAL                  FLOAT NOT NULL, --/D  Hole x-axis position in focal plane, in mm
YFOCAL                  FLOAT NOT NULL, --/D  Hole y-axis position in focal plane, in mm
CHUNK                   VARCHAR(16) NOT NULL, --/D  Name of tiling chunk (from platelist product)
TILE                    INT NOT NULL, --/D   Tile number
PLATESN2                FLOAT NOT NULL, --/D  Overall (S/N)2 measure for plate, minimum of all 4 cameras
PSFFLUX_U               FLOAT NOT NULL, --/U nanomaggies --/D   Flux in u, g, r, i, z bands
PSFFLUX_G               FLOAT NOT NULL, --/U nanomaggies --/D   Flux in u, g, r, i, z bands
PSFFLUX_R               FLOAT NOT NULL, --/U nanomaggies --/D   Flux in u, g, r, i, z bands
PSFFLUX_I               FLOAT NOT NULL, --/U nanomaggies --/D   Flux in u, g, r, i, z bands
PSFFLUX_Z               FLOAT NOT NULL, --/U nanomaggies --/D   Flux in u, g, r, i, z bands
PSFFLUX_IVAR_U          FLOAT NOT NULL, --/U nanomaggies^2 --/D   Inverse variance of u, g, r, i, z fluxes
PSFFLUX_IVAR_G          FLOAT NOT NULL, --/U nanomaggies^2 --/D   Inverse variance of u, g, r, i, z fluxes
PSFFLUX_IVAR_R          FLOAT NOT NULL, --/U nanomaggies^2 --/D   Inverse variance of u, g, r, i, z fluxes
PSFFLUX_IVAR_I          FLOAT NOT NULL, --/U nanomaggies^2 --/D   Inverse variance of u, g, r, i, z fluxes
PSFFLUX_IVAR_Z          FLOAT NOT NULL, --/U nanomaggies^2 --/D   Inverse variance of u, g, r, i, z fluxes
PSFMAG_U                FLOAT NOT NULL, --/U mag --/D   PSF magnitudes in u, g, r, i, z bands
PSFMAG_G                FLOAT NOT NULL, --/U mag --/D   PSF magnitudes in u, g, r, i, z bands
PSFMAG_R                FLOAT NOT NULL, --/U mag --/D   PSF magnitudes in u, g, r, i, z bands
PSFMAG_I                FLOAT NOT NULL, --/U mag --/D   PSF magnitudes in u, g, r, i, z bands
PSFMAG_Z                FLOAT NOT NULL, --/U mag --/D   PSF magnitudes in u, g, r, i, z bands
PSFMAGERR_U             FLOAT NOT NULL, --/U mag --/D   Error of PSF magnitudes in u, g, r, i, z bands
PSFMAGERR_G             FLOAT NOT NULL, --/U mag --/D   Error of PSF magnitudes in u, g, r, i, z bands
PSFMAGERR_R             FLOAT NOT NULL, --/U mag --/D   Error of PSF magnitudes in u, g, r, i, z bands
PSFMAGERR_I             FLOAT NOT NULL, --/U mag --/D   Error of PSF magnitudes in u, g, r, i, z bands
PSFMAGERR_Z             FLOAT NOT NULL, --/U mag --/D   Error of PSF magnitudes in u, g, r, i, z bands
EXTINCTION_U            FLOAT NOT NULL, --/U mag --/D   Galactic extinction in u, g, r, i, z bands
EXTINCTION_G            FLOAT NOT NULL, --/U mag --/D   Galactic extinction in u, g, r, i, z bands
EXTINCTION_R            FLOAT NOT NULL, --/U mag --/D   Galactic extinction in u, g, r, i, z bands
EXTINCTION_I            FLOAT NOT NULL, --/U mag --/D   Galactic extinction in u, g, r, i, z bands
EXTINCTION_Z            FLOAT NOT NULL, --/U mag --/D   Galactic extinction in u, g, r, i, z bands
SN_MEDIAN_ALL           FLOAT NOT NULL, --/D  Median S/N value of all good spectroscopic pixels
DISK_ONLY               BOOLEAN NOT NULL, --/D TRUE if the object is not listed in specobjall
);
