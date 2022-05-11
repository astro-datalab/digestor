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
SDSS_NAME		        STRING NOT NULL, --/D  SDSS-DR16 designation (hhmmss.ss±ddmmss.s, J2000)
RA				        DOUBLE NOT NULL, --/D  Right ascension in decimal degrees (J2000)
DEC				        DOUBLE NOT NULL, --/D  Declination in decimal degrees (J2000)
PLATE			        INT32 NOT NULL, --/D   Spectroscopic plate number
MJD				        INT32 NOT NULL, --/D   Modified Julian day of the spectroscopic observation
FIBERID				    INT16 NOT NULL, --/D   Fiber ID number
AUTOCLASS_PQN		    STRING NOT NULL, --/D  Object classification post-QuasarNET
AUTOCLASS_DR14Q		    STRING NOT NULL, --/D  Object classification based only on the DR14Q algorithm
IS_QSO_QN			    INT16 NOT NULL, --/D   Binary flag for QuasarNET quasar identification
Z_QN				    DOUBLE NOT NULL, --/D  Systemic redshift from QuasarNET
RANDOM_SELECT		    INT16 NOT NULL, --/D   Binary flag indicating objects selected for random visual inspection
Z_10K				    DOUBLE NOT NULL, --/D  Redshift from visual inspection in random set
Z_CONF_10K		        INT16 NOT NULL, --/D   Confidence rating for visual inspection redshift in random set
PIPE_CORR_10K		    INT16 NOT NULL, --/D   Binary flag indicating if the automated pipeline classification and redshift were correct in the random set
IS_QSO_10K		        INT16 NOT NULL, --/D   Binary flag for random set quasar identification
PRIM_REC		        INT16 NOT NULL, --/D   Flag to indicate if observation is primary observation appearing in DR16Q or a duplicate
THING_ID		        INT64 NOT NULL, --/D   SDSS identifier
Z_VI		            DOUBLE NOT NULL, --/D  Visual inspection redshift
Z_CONF		            INT16 NOT NULL, --/D   Confidence rating for visual inspection redshift
CLASS_PERSON		    INT16 NOT NULL, --/D   Object classification from visual inspection
Z_DR12Q		            DOUBLE NOT NULL, --/D  Redshift taken from DR12Q visual inspection
IS_QSO_DR12Q		    INT16 NOT NULL, --/D   Flag indicating if an object was a quasar in DR12Q
Z_DR7Q_SCH		        DOUBLE NOT NULL, --/D  Redshift taken from DR7Q Schneider et al (2010) catalog
IS_QSO_DR7Q		        INT16 NOT NULL, --/D   Flag indicating if an object was a quasar in DR7Q
Z_DR6Q_HW		        DOUBLE NOT NULL, --/D  Redshift taken from DR6 Hewett and Wild (2010) catalog
Z_DR7Q_HW		  	    DOUBLE NOT NULL, --/D  Redshift using Hewett and Wild (2010) updates for DR7Q sources from the Shen et al. (2011) catalog
IS_QSO_FINAL		    INT16 NOT NULL, --/D   Flag indicating quasars to be included in final catalog
Z		  	            DOUBLE NOT NULL, --/D  Best available redshift taken from Z_VI, Z_PIPE, Z_DR12Q, Z_DR7Q_SCH, Z_DR6Q_HW, and Z_10K
SOURCE_Z		        STRING NOT NULL, --/D  Origin of the reported redshift in Z
Z_PIPE		 	        DOUBLE NOT NULL, --/D  SDSS automated pipeline redshift
ZWARNING		  	    INT32 NOT NULL, --/D   Quality flag on the pipeline redshift estimate
OBJID		            STRING NOT NULL, --/D  SDSS object identification number
Z_PCA		  	        DOUBLE NOT NULL, --/D  PCA-derived systemic redshift from redvsblue
ZWARN_PCA		 	    INT64 NOT NULL, --/D   Warning flag for redvsblue redshift
DELTACHI2_PCA		  	DOUBLE NOT NULL, --/D  Delta χ2 for PCA redshift vs. cubic continuum fit
Z_HALPHA		   	    DOUBLE NOT NULL, --/D  PCA line redshift for Hα from redvsblue
ZWARN_HALPHA		  	INT64 NOT NULL, --/D   Warning flag for Hα redshift
DELTACHI2_HALPHA		DOUBLE NOT NULL, --/D  Delta χ2 for Hα line redshift vs. cubic continuum fit
Z_HBETA			        DOUBLE NOT NULL, --/D  PCA line redshift for Hβ from redvsblue
ZWARN_HBETA		        INT64 NOT NULL, --/D   Warning flag for Hβ redshift
DELTACHI2_HBETA			DOUBLE NOT NULL, --/D  Delta χ2 for Hβ line redshift vs. cubic continuum fit
Z_MGII		 	        DOUBLE NOT NULL, --/D  PCA line redshift for Mg II λ2799 from redvsblue
ZWARN_MGII			    INT64 NOT NULL, --/D   Warning flag for Mg II λ2799 redshift
DELTACHI2_MGII		 	DOUBLE NOT NULL, --/D  Delta χ2 for Mg II λ2799 line redshift vs. cubic continuum fit
Z_CIII		 	        DOUBLE NOT NULL, --/D  PCA line redshift for C III] λ1908 from redvsblue
ZWARN_CIII		    	INT64 NOT NULL, --/D   Warning flag for C III] λ1908 redshift
DELTACHI2_CIII		 	DOUBLE NOT NULL, --/D  Delta χ2 for C III] λ1908 line redshift vs. cubic continuum fit
Z_CIV		  	        DOUBLE NOT NULL, --/D  PCA line redshift for C IV λ1549 from redvsblue
ZWARN_CIV		 	    INT64 NOT NULL, --/D   Warning flag for C IV λ1549 redshift
DELTACHI2_CIV		  	DOUBLE NOT NULL, --/D  Delta χ2 for C IV λ1549 line redshift vs. cubic continuum fit
Z_LYA		  	        DOUBLE NOT NULL, --/D  PCA line redshift for Lyα from redvsblue
ZWARN_LYA		 	    INT64 NOT NULL, --/D   Warning flag for Lyα redshift
DELTACHI2_LYA		  	DOUBLE NOT NULL, --/D  Delta χ2 for Lyα line redshift vs. cubic continuum fit
Z_DLA		  	        DOUBLE[5] NOT NULL, --/D  Redshift for damped Lyα features
NHI_DLA			        DOUBLE[5] NOT NULL, --/D  Absorber column density for damped Lyα features
CONF_DLA		   	    DOUBLE[5] NOT NULL, --/D  Confidence of detection for damped Lyα features
BAL_PROB		        FLOAT NOT NULL, --/D   BAL probability
BI_CIV		 	        DOUBLE NOT NULL, --/D  BALnicity index for C IV λ1549 region
ERR_BI_CIV		 	    DOUBLE NOT NULL, --/D  Uncertainty of BI for C IV λ1549 region
AI_CIV		 	        DOUBLE NOT NULL, --/D  Absorption index for C IV λ1549 region
ERR_AI_CIV		 	    DOUBLE NOT NULL, --/D  Uncertainty of absorption index for C IV λ1549 region
BI_SIIV			        DOUBLE NOT NULL, --/D  BALnicity index for Si IV λ1396 region
ERR_BI_SIIV			    DOUBLE NOT NULL, --/D  Uncertainty of BI for Si IV λ1396 region
AI_SIIV			        DOUBLE NOT NULL, --/D  Absorption index for Si IV λ1396 region
ERR_AI_SIIV			    DOUBLE NOT NULL, --/D  Uncertainty of absorption index for Si IV λ1396 region
BOSS_TARGET1		  	INT64 NOT NULL, --/D   BOSS target selection for main survey
EBOSS_TARGET0		 	INT64 NOT NULL, --/D   Target selection flag for the eBOSS pilot survey (SEQUELS)
EBOSS_TARGET1		 	INT64 NOT NULL, --/D   eBOSS target selection flag
EBOSS_TARGET2		 	INT64 NOT NULL, --/D   eBOSS target selection flag
ANCILLARY_TARGET1	 	INT64 NOT NULL, --/D   BOSS target selection flag for ancillary programs
ANCILLARY_TARGET2	 	INT64 NOT NULL, --/D   BOSS target selection flag for ancillary programs
NSPEC_SDSS			    INT32 NOT NULL, --/D   Number of additional observations from SDSS-I/II
NSPEC_BOSS			    INT32 NOT NULL, --/D   Number of additional observations from BOSS/eBOSS
NSPEC		 	        INT32 NOT NULL, --/D   Total number of additional observations
PLATE_DUPLICATE		    INT32[74] NOT NULL, --/D  Spectroscopic plate number of duplicate spectroscopic observations
MJD_DUPLICATE		 	INT32[74] NOT NULL, --/D  Spectroscopic MJD of duplicate spectroscopic observations
FIBERID_DUPLICATE	    INT16[74] NOT NULL, --/D  Fiber ID number of duplicate spectrocscopic observations.
SPECTRO_DUPLICATE	    INT32[74] NOT NULL, --/D  Spectroscopic instrument for each duplicate, 1=SDSS, 2=(e)BOSS
SKYVERSION			    INT8 NOT NULL, --/D    SDSS photometric sky version number
RUN_NUMBER			    INT32 NOT NULL, --/D   SDSS photometric run number
RERUN_NUMBER		    STRING NOT NULL, --/D  SDSS photometric rerun number
CAMCOL_NUMBER		 	INT32 NOT NULL, --/D   SDSS photometric camera column
FIELD_NUMBER		  	INT32 NOT NULL, --/D   SDSS photometric field number
ID_NUMBER		 	    INT32 NOT NULL, --/D   SDSS photometric ID number
LAMBDA_EFF		 	    DOUBLE NOT NULL, --/D  Wavelength to optimize hold location for, in Angstroms
ZOFFSET			        DOUBLE NOT NULL, --/D  Backstopping offset distance, in μm
XFOCAL		 	        DOUBLE NOT NULL, --/D  Hole x-axis position in focal plane, in mm
YFOCAL		 	        DOUBLE NOT NULL, --/D  Hole y-axis position in focal plane, in mm
CHUNK		            STRING NOT NULL, --/D  Name of tiling chunk (from platelist product)
TILE		  	        INT32 NOT NULL, --/D   Tile number
PLATESN2		   	    DOUBLE NOT NULL, --/D  Overall (S/N)2 measure for plate, minimum of all 4 cameras
PSFFLUX		            FLOAT[5] NOT NULL, --/D   Flux in u, g, r, i, z bands
PSFFLUX_IVAR            FLOAT[5] NOT NULL, --/D   Inverse variance of u, g, r, i, z fluxes
PSFMAG		            FLOAT[5] NOT NULL, --/D   PSF magnitudes in u, g, r, i, z bands
PSFMAGERR		        FLOAT[5] NOT NULL, --/D   Error of PSF magnitudes in u, g, r, i, z bands
EXTINCTION		        FLOAT[5] NOT NULL, --/D   Galactic extinction in u, g, r, i, z bands
SN_MEDIAN_ALL		  	DOUBLE NOT NULL --/D  Median S/N value of all good spectroscopic pixels
);
