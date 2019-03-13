CREATE TABLE dr14q (
-------------------------------------------------------------------------------
--/H The DR14 QSO Catalog (v4_4, final).
--
--/T DR14Q is the first quasar catalog of SDSS-IV, associated to the fourteenth
--/T data release, as documented in Pâris et al. (2018). It contains photometric
--/T and spectroscopic information of about half million quasars.
-------------------------------------------------------------------------------
    specObjID          bigint NOT NULL, --/D Unique database ID based on PLATE, MJD, FIBERID, RUN2D --/K ID_CATALOG
    sdssName           varchar(18) NOT NULL, --/D SDSS-DR14 designation - hhmmss.ss+ddmmss.s (J2000)
    ra                 float NOT NULL, --/U deg --/D Right Ascension in decimal degrees(J2000)
    dec                float NOT NULL, --/U deg --/D Declination in decimal degrees(J2000)
    thing_id           int NOT NULL, --/D Unique SDSS source identifier
    plate              smallint NOT NULL, --/D Spectroscopic plate number
    mjd                int NOT NULL, --/U days --/D Modified Julian Day of the spectroscopic observation
    fiberID            smallint NOT NULL, --/D Spectroscopic fiber number
    instrument         varchar(4) NOT NULL, --/D Spectrograph used for the observation (SDSS or BOSS) --/F spectro
    z                  real NOT NULL, --/D Redshift (most robust estimate for each quasar)
    zErr               real NOT NULL, --/D Error on redshift given in Col. #9
    zSource            varchar(4) NOT NULL, --/D Origin of the Z measurement (VI, PIPE, AUTO, OTHER) --/F source_z
    zVI                real NOT NULL, --/D Redshift based on visual inspection (when available)
    zPipe              real NOT NULL, --/D SDSS pipeline redshift estimate
    zPipeErr           real NOT NULL, --/D Error on SDSS pipeline redshift estimate
    zWarning           int NOT NULL, --/D Quality flag on SDSS pipeline redshift measurement
    zPCA               real NOT NULL, --/D PCA redshift (homogeneous over the full sample)
    zPCAErr            real NOT NULL, --/D Error on PCA redshift --/F z_pca_er
    zMgII              real NOT NULL, --/D Redshift of the MgII emission line
    boss_target1       bigint NOT NULL, --/D BOSS target selection flag for main survey
    ancillary_target1  bigint NOT NULL, --/D BOSS target selection flag for ancillary programs
    ancillary_target2  bigint NOT NULL, --/D BOSS target selection flag for ancillary programs
    eboss_target0      bigint NOT NULL, --/D Target selection flag for the eBOSS pilot survey
    eboss_target1      bigint NOT NULL, --/D eBOSS target selection flag
    eboss_target2      bigint NOT NULL, --/D eBOSS target selection flag
    n_spec_sdss        smallint NOT NULL, --/D Number of additional spectra available in SDSS-I/II
    n_spec_boss        smallint NOT NULL, --/D Number of additional spectra available in SDSS-III/IV
    n_spec             smallint NOT NULL, --/D Number of additional spectra available in SDSS-I/II/III/IV
    bi_civ             real NOT NULL, --/U km/s --/D BALnicity Index of CIV absorption trough
    err_bi_civ         real NOT NULL, --/U km/s --/D Error on the Balnicity index of CIV trough
    psfFlux_u          real NOT NULL, --/U nanomaggies --/D PSF flux in u band
    psfFlux_g          real NOT NULL, --/U nanomaggies --/D PSF flux in g band
    psfFlux_r          real NOT NULL, --/U nanomaggies --/D PSF flux in r band
    psfFlux_i          real NOT NULL, --/U nanomaggies --/D PSF flux in i band
    psfFlux_z          real NOT NULL, --/U nanomaggies --/D PSF flux in z band
    psfFluxIvar_u      real NOT NULL, --/U 1/nanomaggies^2 --/D Inverse variance of PSF flux in u band --/F ivar_psfflux 0
    psfFluxIvar_g      real NOT NULL, --/U 1/nanomaggies^2 --/D Inverse variance of PSF flux in g band --/F ivar_psfflux 1
    psfFluxIvar_r      real NOT NULL, --/U 1/nanomaggies^2 --/D Inverse variance of PSF flux in r band --/F ivar_psfflux 2
    psfFluxIvar_i      real NOT NULL, --/U 1/nanomaggies^2 --/D Inverse variance of PSF flux in i band --/F ivar_psfflux 3
    psfFluxIvar_z      real NOT NULL, --/U 1/nanomaggies^2 --/D Inverse variance of PSF flux in z band --/F ivar_psfflux 4
    psfMag_u           real NOT NULL, --/U mag --/D PSF magnitude in u band
    psfMag_g           real NOT NULL, --/U mag --/D PSF magnitude in g band
    psfMag_r           real NOT NULL, --/U mag --/D PSF magnitude in r band
    psfMag_i           real NOT NULL, --/U mag --/D PSF magnitude in i band
    psfMag_z           real NOT NULL, --/U mag --/D PSF magnitude in z band
    psfMagErr_u        real NOT NULL, --/U mag --/D PSF magnitude in u band --/F err_psfmag 0
    psfMagErr_g        real NOT NULL, --/U mag --/D PSF magnitude in g band --/F err_psfmag 1
    psfMagErr_r        real NOT NULL, --/U mag --/D PSF magnitude in r band --/F err_psfmag 2
    psfMagErr_i        real NOT NULL, --/U mag --/D PSF magnitude in i band --/F err_psfmag 3
    psfMagErr_z        real NOT NULL, --/U mag --/D PSF magnitude in z band --/F err_psfmag 4
    mi                 real NOT NULL, --/D Absolute magnitude in i band, Mi [z = 2], see DR14Q paper for cosmology
    extinction_u       real NOT NULL, --/U mag --/D Galactic extinction in SDSS u band from from Schlafly & Finkbeiner (2011) --/F gal_ext 0
    extinction_g       real NOT NULL, --/U mag --/D Galactic extinction in SDSS g band from from Schlafly & Finkbeiner (2011) --/F gal_ext 1
    extinction_r       real NOT NULL, --/U mag --/D Galactic extinction in SDSS r band from from Schlafly & Finkbeiner (2011) --/F gal_ext 2
    extinction_i       real NOT NULL, --/U mag --/D Galactic extinction in SDSS i band from from Schlafly & Finkbeiner (2011) --/F gal_ext 3
    extinction_z       real NOT NULL, --/U mag --/D Galactic extinction in SDSS z band from from Schlafly & Finkbeiner (2011) --/F gal_ext 4
    rass_counts        real NOT NULL, --/U log(counts/s) --/D log RASS full band count rate (counts/s)
    rass_counts_snr    real NOT NULL, --/D S/N of the RASS count rate
    sdss2rosat_sep     real NOT NULL, --/U arcsec --/D SDSS-RASS separation
    xmm_soft_flux      real NOT NULL, --/U ergs/cm2/s --/D Soft (0.2-2.0 keV) X-ray flux from XMM-Newton --/F FLUX_0.2_2.0keV
    xmm_soft_flux_err  real NOT NULL, --/U ergs/cm2/s --/D Error on soft X-ray flux from XMM-Newton --/F FLUX_0.2_2.0keV_ERR
    xmm_hard_flux      real NOT NULL, --/U ergs/cm2/s --/D Hard (4.5-12.0 keV) X-ray flux from XMM-Newton --/F FLUX_2.0_12.0keV
    xmm_hard_flux_err  real NOT NULL, --/U ergs/cm2/s --/D Error on hard X-ray flux from XMM-Newton --/F FLUX_2.0_12.0keV_ERR
    xmm_flux           real NOT NULL, --/U ergs/cm2/s --/D Total (0.2-12.0 keV) X-ray flux from XMM-Newton --/F FLUX_0.2_12.0keV
    xmm_flux_err       real NOT NULL, --/U ergs/cm2/s --/D Error on total X-ray flux from XMM-Newton --/F FLUX_0.2_12.0keV_ERR
    xmm_luminosity     real NOT NULL, --/U erg/s --/D Total (0.2-12.0 keV) X-ray luminosity from XMM-Newton --/F LUM_0.2_12.0keV
    sdss2xmm_sep       real NOT NULL, --/U arcsec --/D SDSS-XMM-Newton separation
    galex_matched      smallint NOT NULL, --/D GALEX match flag
    fuv                real NOT NULL, --/U nanomaggies --/D FUV flux (GALEX)
    fuv_ivar           real NOT NULL, --/U 1/nanomaggies^2 --/D Inverse variance of FUV flux
    nuv                real NOT NULL, --/U NUV flux (GALEX)
    nuv_ivar           real NOT NULL, --/U 1/nanomaggies^2 --/D Inverse variance of NUV flux
    jmag               real NOT NULL, --/U mag --/D J magnitude (Vega, 2MASS)
    jmag_err           real NOT NULL, --/U mag --/D Error in J magnitude --/F err_jmag
    jsnr               real NOT NULL, --/D J-Band S/N
    jrdflag            smallint NOT NULL, --/D H-Band photometry flag
    hmag               real NOT NULL, --/U mag --/D H magnitude (Vega, 2MASS)
    hmag_err           real NOT NULL, --/U mag --/D Error in H magnitude --/F err_hmag
    hsnr               real NOT NULL, --/D H-Band S/N
    hrdflag            smallint NOT NULL, --/D H-Band photometry flag
    kmag               real NOT NULL, --/U mag --/D K magnitude (Vega, 2MASS)
    kmag_err           real NOT NULL, --/U mag --/D Error in K magnitude --/F err_kmag
    ksnr               real NOT NULL, --/D K-Band S/N
    krdflag            smallint NOT NULL, --/D K-Band photometry flag
    sdss2mass_sep      real NOT NULL, --/U arcsec --/D SDSS-2MASS separation
    w1mag              real NOT NULL, --/U mag --/D W1 magnitude (Vega, WISE)
    w1mag_err          real NOT NULL, --/U mag --/D Error in W1 magnitude --/F err_w1mag
    w1snr              real NOT NULL, --/D S/N in W1 band
    w1chi2             real NOT NULL, --/D chi-squared in W1 band
    w2mag              real NOT NULL, --/U mag --/D W2 magnitude (Vega, WISE)
    w2mag_err          real NOT NULL, --/U mag --/D Error in W2 magnitude --/F err_w2mag
    w2snr              real NOT NULL, --/D S/N in W2 band
    w2chi2             real NOT NULL, --/D chi-squared in W2 band
    w3mag              real NOT NULL, --/U mag --/D W3 magnitude (Vega, WISE)
    w3mag_err          real NOT NULL, --/U mag --/D Error in W3 magnitude --/F err_w3mag
    w3snr              real NOT NULL, --/D S/N in W3 band
    w3chi2             real NOT NULL, --/D chi-squared in W3 band
    w4mag              real NOT NULL, --/U mag --/D W4 magnitude (Vega, WISE)
    w4mag_err          real NOT NULL, --/U mag --/D Error in W4 magnitude --/F err_w4mag
    w4snr              real NOT NULL, --/D S/N in W4 band
    w4chi2             real NOT NULL, --/D chi-squared in W4 band
    cc_flags           varchar(4) NOT NULL, --/D WISE contamination and confusion flag
    ph_flags           varchar(4) NOT NULL, --/D WISE photometric quality flag
    sdss2wise_sep      real NOT NULL, --/U arcsec --/D SDSS-WISE separation
    ukidss_matched     smallint NOT NULL, --/D UKIDSS matching flag
    yflux              real NOT NULL, --/U W/m2/Hz --/D Y-band flux density from UKIDSS
    yflux_err          real NOT NULL, --/U W/m2/Hz --/D Error in Y-band flux density from UKIDSS
    jflux              real NOT NULL, --/U W/m2/Hz --/D J-band density flux from UKIDSS
    jflux_err          real NOT NULL, --/U W/m2/Hz --/D Error in J-band flux density from UKIDSS)
    hflux              real NOT NULL, --/U W/m2/Hz --/D H-band flux density from UKIDSS
    hflux_err          real NOT NULL, --/U W/m2/Hz --/D Error in H-band flux density from UKIDSS
    kflux              real NOT NULL, --/U W/m2/Hz --/D K-band flux density from UKIDSS
    kflux_err          real NOT NULL, --/U W/m2/Hz --/D Error in K-band flux density from UKIDSS
    first_matched      smallint NOT NULL, --/D FIRST matching flag
    first_flux         real NOT NULL, --/U mJy --/D FIRST peak flux density at 20 cm
    first_snr          real NOT NULL, --/D S/N of the FIRST flux density
    sdss2first_sep     real NOT NULL, --/U arcsec --/D SDSS-FIRST separation
);
