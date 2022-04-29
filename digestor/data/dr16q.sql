CREATE		TABLE dr16q (
-------------------------------------------------------------------------------
--/H		The DR16 QSO Catalog (v4)
--
--/T		DR16Q is the final quasar catalog of SDSS-IV, associated with the sixteenth 
--/T		data release. The catalog is documented in more detail at the DR16Q VAC algorithm 
--/T		page, which also includes a link to the ApJS paper (Lyke et al. 2020). The catalog 
--/T		contains spectroscopic and photometric data for over 750,000 quasars. To ensure 
--/T		completeness, known quasars from previous catalog releases (DR7Q and DR12Q) have 
--/T		also been included. This catalog is taken from objects in the DR16Q Superset. The 
--/T		file for this quasar catalog can be found at 
--/T		https://data.sdss.org/sas/dr16/eboss/qso/DR16Q/DR16Q_v4.fits
-------------------------------------------------------------------------------

specobjid		            bigint NOT NULL, --/D Unique database ID based on PLATE, MJD, FIBERID, RUN2D --/K ID_CATALOG
SDSS_NAME				    varchar(18) NOT NULL, --/D SDSS-DR16 designation (hhmmss.ss±ddmmss.s, J2000)
RA				            float NOT NULL, --/D  Right ascension in decimal degrees (J2000)
DEC		                    float NOT NULL, --/D		 Declination in decimal degrees (J2000)
RUN2D                       varchar(7), --/D Spectroscopic reduction version
PLATE				        smallint NOT NULL, --/D   Spectroscopic plate number
MJD		                    integer NOT NULL, --/D		  Modified Julian day of the spectroscopic observation
FIBERID		                smallint NOT NULL, --/D		  Fiber ID number
AUTOCLASS_PQN		        varchar(6) NOT NULL, --/D Object classification post-QuasarNET
AUTOCLASS_DR14Q		        varchar(6) NOT NULL, --/D		 Object classification based only on the DR14Q algorithm
IS_QSO_QN				    integer NOT NULL, --/D   Binary flag for QuasarNET quasar identification
Z_QN				        float NOT NULL, --/D  Systemic redshift from QuasarNET
RANDOM_SELECT			    integer NOT NULL, --/D   Binary flag indicating objects selected for random visual inspection
Z_10K				        float NOT NULL, --/D  Redshift from visual inspection in random set
Z_CONF_10K				    integer NOT NULL, --/D   Confidence rating for visual inspection redshift in random set
PIPE_CORR_10K			    integer NOT NULL, --/D   Binary flag indicating if the automated pipeline classification and redshift were correct in the random set
IS_QSO_10K				    integer NOT NULL, --/D   Binary flag for random set quasar identification
THING_ID				    integer NOT NULL, --/D   SDSS identifier
Z_VI				        float NOT NULL, --/D  Visual inspection redshift
Z_CONF				        integer NOT NULL, --/D   Confidence rating for visual inspection redshift
CLASS_PERSON				integer NOT NULL, --/D   Object classification from visual inspection
Z_DR12Q		                float NOT NULL, --/D		 Redshift taken from DR12Q visual inspection
IS_QSO_DR12Q				integer NOT NULL, --/D   Flag indicating if an object was a quasar in DR12Q
Z_DR7Q_SCH				    float NOT NULL, --/D  Redshift taken from DR7Q Schneider et al (2010) catalog
IS_QSO_DR7Q		            integer NOT NULL, --/D		  Flag indicating if an object was a quasar in DR7Q
Z_DR6Q_HW				    float NOT NULL, --/D  Redshift taken from DR6-based Hewett and Wild (2010) catalog
Z_DR7Q_HW				    float NOT NULL, --/D  Redshift using Hewett and Wild (2010) updates for DR7Q sources from the Shen et al. (2011) catalog
IS_QSO_FINAL				integer NOT NULL, --/D   Flag indicating quasars to be included in final catalog
Z				            float NOT NULL, --/D  Best available redshift taken from Z_VI, Z_PIPE, Z_DR12Q, Z_DR7Q_SCH, Z_DR6Q_HW, and Z_10K
SOURCE_Z				    varchar(12) NOT NULL, --/D Origin of the reported redshift in Z
Z_PIPE				        float NOT NULL, --/D  SDSS automated pipeline redshift
ZWARNING				    integer NOT NULL, --/D   Quality flag on the pipeline redshift estimate
OBJID                       varchar(19), --/D SDSS object identification number
Z_PCA				 		float NOT NULL, --/D  PCA-derived systemic redshift from redvsblue
ZWARN_PCA				    bigint NOT NULL, --/D   Warning flag for redvsblue redshift
DELTACHI2_PCA			    float NOT NULL, --/D  Delta χ2 for PCA redshift vs. cubic continuum fit
Z_HALPHA				    float NOT NULL, --/D  PCA line redshift for Hα from redvsblue
ZWARN_HALPHA			    bigint NOT NULL, --/D   Warning flag for Hα redshift
DELTACHI2_HALPHA		    float NOT NULL, --/D  Delta χ2 for Hα line redshift vs. cubic continuum fit
Z_HBETA				        float NOT NULL, --/D		 PCA line redshift for Hβ from redvsblue
ZWARN_HBETA		            bigint NOT NULL, --/D		  Warning flag for Hβ redshift
DELTACHI2_HBETA				float NOT NULL, --/D		 Delta χ2 for Hβ line redshift vs. cubic continuum fit
Z_MGII						float NOT NULL, --/D  PCA line redshift for Mg II λ2799 from redvsblue
ZWARN_MGII				    bigint NOT NULL, --/D   Warning flag for Mg II λ2799 redshift
DELTACHI2_MGII			    float NOT NULL, --/D  Delta χ2 for Mg II λ2799 line redshift vs. cubic continuum fit
Z_CIII						float NOT NULL, --/D  PCA line redshift for C III] λ1908 from redvsblue
ZWARN_CIII				    bigint NOT NULL, --/D   Warning flag for C III] λ1908 redshift
DELTACHI2_CIII			    float NOT NULL, --/D  Delta χ2 for C III] λ1908 line redshift vs. cubic continuum fit
Z_CIV				 		float NOT NULL, --/D  PCA line redshift for C IV λ1549 from redvsblue
ZWARN_CIV				    bigint NOT NULL, --/D   Warning flag for C IV λ1549 redshift
DELTACHI2_CIV			    float NOT NULL, --/D  Delta χ2 for C IV λ1549 line redshift vs. cubic continuum fit
Z_LYA				 		float NOT NULL, --/D  PCA line redshift for Lyα from redvsblue
ZWARN_LYA				    bigint NOT NULL, --/D   Warning flag for Lyα redshift
DELTACHI2_LYA			    float NOT NULL, --/D  Delta χ2 for Lyα line redshift vs. cubic continuum fit
Z_LYAWG				        float NOT NULL, --/D		  PCA systemic redshift from redvsblue with a masked Lyα emission line and forest
Z_DLA				 	    float NOT NULL, --/D   Redshift for damped Lyα features
NHI_DLA				        float NOT NULL, --/D		  Absorber column density for damped Lyα features
CONF_DLA				    float NOT NULL, --/D   Confidence of detection for damped Lyα features
BAL_PROB				    float NOT NULL, --/D  BAL probability
BI_CIV						float NOT NULL, --/D  BALnicity index for C IV λ1549 region
ERR_BI_CIV				    float NOT NULL, --/D  Uncertainty of BI for C IV λ1549 region
AI_CIV						float NOT NULL, --/D  Absorption index for C IV λ1549 region
ERR_AI_CIV				    float NOT NULL, --/D  Uncertainty of absorption index for C IV λ1549 region
BI_SIIV				        float NOT NULL, --/D		 BALnicity index for Si IV λ1396 region
ERR_BI_SIIV				    float NOT NULL, --/D		 Uncertainty of BI for Si IV λ1396 region
AI_SIIV				        float NOT NULL, --/D		 Absorption index for Si IV λ1396 region
ERR_AI_SIIV				    float NOT NULL, --/D		 Uncertainty of absorption index for Si IV λ1396 region
BOSS_TARGET1			    bigint NOT NULL, --/D   BOSS target selection for main survey
EBOSS_TARGET0			    bigint NOT NULL, --/D   Target selection flag for the eBOSS pilot survey (SEQUELS)
EBOSS_TARGET1			    bigint NOT NULL, --/D   eBOSS target selection flag
EBOSS_TARGET2			    bigint NOT NULL, --/D   eBOSS target selection flag
ANCILLARY_TARGET1		    bigint NOT NULL, --/D   BOSS target selection flag for ancillary programs
ANCILLARY_TARGET2		    bigint NOT NULL, --/D   BOSS target selection flag for ancillary programs
NSPEC_SDSS				    smallint NOT NULL, --/D   Number of additional observations from SDSS-I/II
NSPEC_BOSS				    smallint NOT NULL, --/D   Number of additional observations from BOSS/eBOSS
NSPEC				        smallint NOT NULL, --/D   Total number of additional observations
LAMBDA_EFF				    float NOT NULL, --/D  Wavelength to optimize hold location for, in Angstroms
ZOFFSET				        float NOT NULL, --/D		 Backstopping offset distance, in μm
XFOCAL						float NOT NULL, --/D  Hole x-axis position in focal plane, in mm
YFOCAL						float NOT NULL, --/D  Hole y-axis position in focal plane, in mm
CHUNK				        varchar(14) NOT NULL, --/D Name of tiling chunk (from platelist product)
TILE				        smallint NOT NULL, --/D   Tile number
PLATESN2				    float NOT NULL, --/D  Overall (S/N)2 measure for plate, minimum of all 4 cameras
PSFFLUX				        float NOT NULL, --/D Flux in u, g, r, i, z bands
PSFFLUX_IVAR			    float NOT NULL, --/D  Inverse variance of u, g, r, i, z fluxes
PSFMAG						float NOT NULL, --/D  PSF magnitudes in u, g, r, i, z bands
PSFMAGERR				    float NOT NULL, --/D  Error of PSF magnitudes in u, g, r, i, z bands
EXTINCTION				    float NOT NULL, --/D  Galactic extinction in u, g, r, i, z bands
M_I				            float NOT NULL, --/D		 Absolute i-band magnitude, H0 = 67.6 km s-1 Mpc-1, OMEGAM = 0.31, OMEGAL = 0.69, OMEGAR		=		9.11x10-5. K-corrections taken from Table 4 of Richards et al. (2006). Z_PCA used for redshifts
SN_MEDIAN_ALL			    float NOT NULL, --/D  Median S/N value of all good spectroscopic pixels
GALEX_MATCHED			    integer NOT NULL, --/D   Matching flag for GALEX
FUV				            float NOT NULL, --/D		 FUV flux from GALEX
FUV_IVAR				    float NOT NULL, --/D  Inverse variance of FUV flux from GALEX
NUV				            float NOT NULL, --/D		 NUV flux from GALEX
NUV_IVAR				    float NOT NULL, --/D  Inverse variance of NUV flux from GALEX
UKIDSS_MATCHED				integer NOT NULL, --/D   Matching flag for UKIDSS
YFLUX				 		float NOT NULL, --/D  Y-band flux density from UKIDSS in W m-2 Hz-1
YFLUX_ERR				    float NOT NULL, --/D  Error in Y-band flux density from UKIDSS in W m-2 Hz-1
JFLUX				 		float NOT NULL, --/D  J-band flux density from UKIDSS in W m-2 Hz-1
JFLUX_ERR				    float NOT NULL, --/D  Error in J-band flux density from UKIDSS in W m-2 Hz-1
HFLUX				 		float NOT NULL, --/D  H-band flux density from UKIDSS in W m-2 Hz-1
HFLUX_ERR				    float NOT NULL, --/D  Error in H-band flux density from UKIDSS in W m-2 Hz-1
KFLUX				 		float NOT NULL, --/D  K-band flux density from UKIDSS in W m-2 Hz-1
KFLUX_ERR				    float NOT NULL, --/D  Error in K-band flux density from UKIDSS in W m-2 Hz-1
W1_FLUX				        float NOT NULL, --/D		  WISE flux in W1-band (Vega, nanomaggies)
W1_FLUX_IVAR			    float NOT NULL, --/D  Inverse variance in W1-band (Vega, nanomaggies-2)
W1_MAG					    float NOT NULL, --/D  W1-band magnitude (Vega)
W1_MAG_ERR				    float NOT NULL, --/D  W1-band uncertainty in magnitude (Vega)
W1_CHI2				        float NOT NULL, --/D		  Profile-weighed χ2
W1_FLUX_SNR				    float NOT NULL, --/D		  S/N from flux and inverse variance
W1_SRC_FRAC			    	float NOT NULL, --/D		  Profile-weighted number of exposures in coadd
W1_EXT_FLUX				    float NOT NULL, --/D		  Profile-weighted flux from other sources
W1_EXT_FRAC				    float NOT NULL, --/D		  Profile-weighted fraction of flux from other sources (blendedness measure)
W1_NPIX		                integer NOT NULL, --/D		  Number of pixels in fit
W2_FLUX				        float NOT NULL, --/D		  WISE flux in W2-band (Vega, nanomaggies)
W2_FLUX_IVAR			    float NOT NULL, --/D  Inverse variance in W2-band (Vega, nanomaggies-2)
W2_MAG						float NOT NULL, --/D  W2-band magnitude (Vega)
W2_MAG_ERR				    float NOT NULL, --/D  W2-band uncertainty in magnitude (Vega)
W2_CHI2				        float NOT NULL, --/D		  Profile-weighed χ2
W2_FLUX_SNR				    float NOT NULL, --/D		  S/N from flux and inverse variance
W2_SRC_FRAC				    float NOT NULL, --/D		  Profile-weighted number of exposures in coadd
W2_EXT_FLUX			    	float NOT NULL, --/D		  Profile-weighted flux from other sources
W2_EXT_FRAC				    float NOT NULL, --/D		  Profile-weighted fraction of flux from other sources (blendedness measure)
W2_NPIX		                integer NOT NULL, --/D		  Number of pixels in fit
FIRST_MATCHED			    integer NOT NULL, --/D   Matching flag for FIRST
FIRST_FLUX				    float NOT NULL, --/D  FIRST peak flux density at 20 cm in mJy
FIRST_SNR				    float NOT NULL, --/D  FIRST flux density S/N
SDSS2FIRST_SEP			    float NOT NULL, --/D  SDSS-FIRST separation in arcsec
JMAG				  		float NOT NULL, --/D  2MASS J-band magnitude (Vega)
JMAG_ERR				    float NOT NULL, --/D  2MASS Error in J-band magnitude
JSNR				  		float NOT NULL, --/D  2MASS J-band S/N
JRDFLAG		                smallint NOT NULL, --/D		  2MASS J-band photometry flag
HMAG				  		float NOT NULL, --/D  2MASS H-band magnitude (Vega)
HMAG_ERR				    float NOT NULL, --/D  2MASS Error in H-band magnitude
HSNR				  		float NOT NULL, --/D  2MASS H-band S/N
HRDFLAG		                smallint NOT NULL, --/D		  2MASS H-band photometry flag
KMAG				  		float NOT NULL, --/D  2MASS Ks-band magnitude (Vega)
KMAG_ERR				    float NOT NULL, --/D  2MASS Error in Ks-band magnitude
KSNR				  		float NOT NULL, --/D  2MASS Ks-band S/N
KRDFLAG		                smallint NOT NULL, --/D		  2MASS Ks-band photometry flag
SDSS2MASS_SEP			    float NOT NULL, --/D  SDSS-2MASS separation in arcsec
2RXS_ID		                varchar(21) NOT NULL, --/D		 ROSAT ID
2RXS_RA				        float NOT NULL, --/D		 Right ascension of the ROSAT source in decimal degrees (J2000)
2RXS_DEC				    float NOT NULL, --/D  Declination of the ROSAT source in decimal degrees (J2000)
2RXS_SRC_FLUX			    float NOT NULL, --/D  ROSAT source flux in 0.5-2.0 keV band in erg s-1 cm-2 (G = 2.4, dered)
2RXS_SRC_FLUX_ERR		    float NOT NULL, --/D  ROSAT source flux error in 0.5-2.0 keV band in erg s-1 cm-2 (G = 2.4, dered)
SDSS2ROSAT_SEP			    float NOT NULL, --/D  SDSS-ROSAT separation in arcsec
XMM_SRC_ID				    bigint NOT NULL, --/D   XMM source ID
XMM_RA						float NOT NULL, --/D  Right ascension for XMM source in decimal degrees (J2000)
XMM_DEC				        float NOT NULL, --/D		 Declination for XMM source in decimal degrees (J2000)
XMM_SOFT_FLUX			    float NOT NULL, --/D  Soft (0.2-2.0 keV) X-ray flux from XMM-Newton in erg s-1 cm-2
XMM_SOFT_FLUX_ERR		    float NOT NULL, --/D  Error on soft X-ray flux from XMM-Newton in erg s-1 cm-2
XMM_HARD_FLUX			    float NOT NULL, --/D  Hard (2.0-12.0 keV) X-ray flux from XMM-Newton in erg s-1 cm-2
XMM_HARD_FLUX_ERR		    float NOT NULL, --/D  Error on hard X-ray flux from XMM-Newton in erg s-1 cm-2
XMM_TOTAL_FLUX			    float NOT NULL, --/D  Total (0.2-12.0 keV) X-ray flux from XMM-Newton in erg s-1 cm-2
XMM_TOTAL_FLUX_ERR		    float NOT NULL, --/D  Error on total X-ray flux from XMM-Newton in erg s-1 cm-2
XMM_TOTAL_LUM			    float NOT NULL, --/D  Total (0.2-12.0 keV) X-ray luminosity from XMM-Newton in erg s-1
SDSS2XMM_SEP			    float NOT NULL, --/D  SDSS-XMM-Newton separation in arcsec
GAIA_MATCHED			    integer NOT NULL, --/D   Gaia matching flag
GAIA_DESIGNATION		    varchar(28) NOT NULL, --/D Gaia designation, includes data release and source ID in that release
GAIA_RA				        float NOT NULL, --/D		 Gaia barycentric right ascension in decimal degrees (J2015.5)
GAIA_DEC				    float NOT NULL, --/D  Gaia barycentric declination in decimal degrees (J2015.5)
GAIA_PARALLAX			    float NOT NULL, --/D  Absolute stellar parallax (J2015.5)
GAIA_PARALLAX_ERR		    float NOT NULL, --/D  Inverse variance of the stellar parallax (J2015.5)
GAIA_PM_RA				    float NOT NULL, --/D  Proper motion in right ascension (mas yr-1, J2015.5)
GAIA_PM_RA_ERR			    float NOT NULL, --/D  Inverse variance of the proper motion in right ascension (yr2 mas-2, J2015.5)
GAIA_PM_DEC				    float NOT NULL, --/D		 Proper motion in declination (mas yr-1, J2015.5)
GAIA_PM_DEC_ERR				float NOT NULL, --/D		 Inverse variance of the proper motion in declination (yr2 mas-2, J2015.5)
GAIA_G_MAG				    float NOT NULL, --/D  Mean magnitude in G-band (Vega)
GAIA_G_FLUX_SNR				float NOT NULL, --/D		 Mean flux over standard deviation in G-band (Vega)
GAIA_BP_MAG				    float NOT NULL, --/D		 Mean magnitude in BP-band (Vega)
GAIA_BP_FLUX_SNR		    float NOT NULL, --/D  Mean flux over standard deviation in BP-band (Vega)
GAIA_RP_MAG				    float NOT NULL, --/D		 Mean magnitude in RP-band (Vega)
GAIA_RP_FLUX_SNR		    float NOT NULL, --/D  Mean flux over standard deviation in RP-band (Vega)
SDSS2GAIA_SEP				float NOT NULL --/D  SDSS-Gaia separation in arcsec
DISK_ONLY                   bit NOT NULL --/D TRUE if the object is not listed in specobjall
);
