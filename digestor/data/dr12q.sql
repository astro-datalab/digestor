CREATE TABLE dr12q (
-------------------------------------------------------------------------------
--/H The DR12 QSO Catalog.
--
--/T DR12Q is the final quasar catalog of SDSS-III, associated to the twelfth
--/T data release, as documented in Pâris et al. (2015). It contains photometric
--/T and spectroscopic information of about 300,000 quasars.
-------------------------------------------------------------------------------
    specObjID          bigint NOT NULL, --/D Unique database ID based on PLATE, MJD, FIBERID, RUN2D --/K ID_CATALOG
    sdss_joinid        bigint NOT NULL, --/D Unique ID based on PLATE, MJD, FIBERID for joining across data releases
    sdssName           varchar(18) NOT NULL, --/D SDSS-DR14 designation - hhmmss.ss+ddmmss.s (J2000)
    ra                 float NOT NULL, --/U deg --/D Right Ascension in decimal degrees(J2000)
    dec                float NOT NULL, --/U deg --/D Declination in decimal degrees(J2000)
    thing_id           int NOT NULL, --/D Unique SDSS source identifier
    -- run2d              varchar(32) NOT NULL, --/D 2D Reduction version of spectrum --/WARNING: run2d is not in DR12Q.
    plate              int NOT NULL, --/D Spectroscopic plate number
    mjd                int NOT NULL, --/U days --/D Modified Julian Day of the spectroscopic observation
    fiberID            int NOT NULL, --/D Spectroscopic fiber number
    zVI                float NOT NULL, --/D Redshift based on visual inspection (when available)
    zPipe              real NOT NULL, --/D SDSS pipeline redshift estimate
    zPipeErr           real NOT NULL, --/D Error on SDSS pipeline redshift estimate --/F err_zpipe
    zWarning           int NOT NULL, --/D Quality flag on SDSS pipeline redshift measurement
    zPCA               float NOT NULL, --/D PCA redshift (homogeneous over the full sample)
    zPCAErr            float NOT NULL, --/D Error on PCA redshift --/F err_zpca
    pcaQual            float NOT NULL, --/D Quality of PCA continuum
    zCIV               float NOT NULL, --/D Redshift of the CIV emission line
    zCIII              float NOT NULL, --/D Redshift of the CIII emission line
    zMgII              float NOT NULL, --/D Redshift of the MgII emission line
    sdssMorpho         smallint NOT NULL, --/D Morphology flag
    boss_target1       bigint NOT NULL, --/D BOSS target selection flag for main survey
    ancillary_target1  bigint NOT NULL, --/D BOSS target selection flag for ancillary programs
    ancillary_target2  bigint NOT NULL, --/D BOSS target selection flag for ancillary programs
    eboss_target0      bigint NOT NULL, --/D Target selection flag for the eBOSS pilot survey
    nspec_boss         int NOT NULL, --/D Number of additional spectra available in SDSS-III/IV
    sdss_dr7           int NOT NULL, --/D DR7 observation flag
    plate_dr7          int NOT NULL, --/D DR7 Plate number
    mjd_dr7            int NOT NULL, --/D DR7 spectroscopic MJD
    fiberid_dr7        int NOT NULL, --/D DR7 Fiber number
    uniform            smallint NOT NULL, --/D Uniform sample flag
    alpha_nu           float NOT NULL, --/D Spectral index
    snr_spec           float NOT NULL, --/D Median SNR (whole spectrum)
    snr_1700           float NOT NULL, --/D Median SNR (1650-1750A rest)
    snr_3000           float NOT NULL, --/D Median SNR (2950-3050A rest)
    snr_5150           float NOT NULL, --/D Median SNR (5100-5250A rest)
    fwhm_civ           float NOT NULL, --/U km/s --/D FWHM of CIV emission
    bhwhm_civ          float NOT NULL, --/U km/s --/D Blue HWHM of CIV emission
    rhwhm_civ          float NOT NULL, --/U km/s --/D Red HWHM of CIV emission
    amp_civ            float NOT NULL, --/D Amplitude of CIV emission
    rewe_civ           float NOT NULL, --/U Angstrom --/D Rest EW of CIV emission
    err_rewe_civ       float NOT NULL, --/U Angstrom --/D Error on rest EW of CIV emission
    fwhm_ciii          float NOT NULL, --/U km/s --/D FWHM of CIII emission
    bhwhm_ciii         float NOT NULL, --/U km/s --/D Blue HWHM of CIII emission
    rhwhm_ciii         float NOT NULL, --/U km/s --/D Red HWHM of CIII emission
    amp_ciii           float NOT NULL, --/D Amplitude of CIII emission
    rewe_ciii          float NOT NULL, --/U Angstrom --/D Rest EW of CIII emission
    err_rewe_ciii      float NOT NULL, --/U Angstrom --/D Error on rest EW of CIII emission
    fwhm_mgii          float NOT NULL, --/U km/s --/D FWHM of MgII emission
    bhwhm_mgii         float NOT NULL, --/U km/s --/D Blue HWHM of MgII emission
    rhwhm_mgii         float NOT NULL, --/U km/s --/D Red HWHM of MgII emission
    amp_mgii           float NOT NULL, --/D Amplitude of MgII emission
    rewe_mgii          float NOT NULL, --/U Angstrom --/D Rest EW of MgII emission
    err_rewe_mgii      float NOT NULL, --/U Angstrom --/D Error on rest EW of MgII emission
    bal_flag_vi        smallint NOT NULL, --/D BAL flag from visual inspection
    bi_civ             float NOT NULL, --/U km/s --/D BALnicity Index of CIV absorption trough
    err_bi_civ         float NOT NULL, --/U km/s --/D Error on the Balnicity index of CIV trough
    ai_civ             float NOT NULL, --/U km/s --/D AI of CIV absorption trough
    err_ai_civ         float NOT NULL, --/U km/s --/D Error on the AI of CIV trough
    chi2trough         float NOT NULL, --/D Chi2 of the CIV troughs
    nciv_2000          int NOT NULL, --/D Number of CIV troughs larger than 2000 km/s
    vmin_civ_2000      float NOT NULL, --/U km/s --/D Min velocity of CIV troughs (col60)
    vmax_civ_2000      float NOT NULL, --/U km/s --/D Max velocity of CIV troughs (col60)
    nciv_450           int NOT NULL, --/D Number of CIV troughs larger than 450 km/s
    vmin_civ_450       float NOT NULL, --/U km/s --/D Min velocity of CIV troughs (col63)
    vmax_civ_450       float NOT NULL, --/U km/s --/D Max velocity of CIV troughs (col63)
    rew_siiv           float NOT NULL, --/U Angstrom --/D Rest EW of SiIV trough
    rew_civ            float NOT NULL, --/U Angstrom --/D Rest EW of CIV trough
    rew_aliii          float NOT NULL, --/U Angstrom --/D Rest EW of AlIII trough
    objid              bigint NOT NULL, --/D Photometric ObjID
    photo_mjd          int NOT NULL, --/D Photometric MJD
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
    targetflux_u       float NOT NULL, --/U nanomaggies --/D Target flux in u band
    targetflux_g       float NOT NULL, --/U nanomaggies --/D Target flux in g band
    targetflux_r       float NOT NULL, --/U nanomaggies --/D Target flux in r band
    targetflux_i       float NOT NULL, --/U nanomaggies --/D Target flux in i band
    targetflux_z       float NOT NULL, --/U nanomaggies --/D Target flux in z band
    mi                 float NOT NULL, --/D Absolute magnitude in i band, Mi [z = 2], see DR12Q paper for cosmology
    dgmi               float NOT NULL, --/D Differential color delta(g-i)
    sfd_ext_u          real NOT NULL, --/U mag --/D Galactic extinction in SDSS u band from from Schlegel et al. (1998) --/F gal_ext 0
    sfd_ext_g          real NOT NULL, --/U mag --/D Galactic extinction in SDSS g band from from Schlegel et al. (1998) --/F gal_ext 1
    sfd_ext_r          real NOT NULL, --/U mag --/D Galactic extinction in SDSS r band from from Schlegel et al. (1998) --/F gal_ext 2
    sfd_ext_i          real NOT NULL, --/U mag --/D Galactic extinction in SDSS i band from from Schlegel et al. (1998) --/F gal_ext 3
    sfd_ext_z          real NOT NULL, --/U mag --/D Galactic extinction in SDSS z band from from Schlegel et al. (1998) --/F gal_ext 4
    extinction_u       real NOT NULL, --/U mag --/D Galactic extinction in SDSS u band from from Schlafly & Finkbeiner (2011) --/F gal_ext_recal 0
    extinction_g       real NOT NULL, --/U mag --/D Galactic extinction in SDSS g band from from Schlafly & Finkbeiner (2011) --/F gal_ext_recal 1
    extinction_r       real NOT NULL, --/U mag --/D Galactic extinction in SDSS r band from from Schlafly & Finkbeiner (2011) --/F gal_ext_recal 2
    extinction_i       real NOT NULL, --/U mag --/D Galactic extinction in SDSS i band from from Schlafly & Finkbeiner (2011) --/F gal_ext_recal 3
    extinction_z       real NOT NULL, --/U mag --/D Galactic extinction in SDSS z band from from Schlafly & Finkbeiner (2011) --/F gal_ext_recal 4
    hi_gal             float NOT NULL, --/U log(cm^-2) --/D log of Galactic HI column density
    var_matched        smallint NOT NULL, --/D Variability information flag
    var_chi2           float NOT NULL, --/D Reduced chi2 when the light curve is fitted with a constant
    var_a              float NOT NULL, --/D Structure function parameter A as defined in Palanque-Delabrouille et al. (2011)
    var_gamma          float NOT NULL, --/D Structure function parameter gamma as defined in Palanque-Delabrouille et al. (2011)
    rass_counts        float NOT NULL, --/U log(counts/s) --/D log RASS full band count rate (counts/s)
    rass_counts_snr    float NOT NULL, --/D S/N of the RASS count rate
    sdss2rosat_sep     float NOT NULL, --/U arcsec --/D SDSS-RASS separation
    n_detection_xmm    smallint NOT NULL, --/D Number of detections in XMM-Newton
    xmm_sgl_flux       float NOT NULL, --/U ergs/cm2/s --/D Total (0.2-12.0 keV) X-ray flux from XMM-Newton computed from longest observation --/F FLUX02_12KEV_SGL
    xmm_sgl_flux_err   float NOT NULL, --/U ergs/cm2/s --/D Error on total X-ray flux from XMM-Newton --/F ERR_FLUX02_12KEV_SGL
    xmm_soft_flux      float NOT NULL, --/U ergs/cm2/s --/D Soft (0.2-2.0 keV) X-ray flux from XMM-Newton --/F FLUX02_2KEV
    xmm_soft_flux_err  float NOT NULL, --/U ergs/cm2/s --/D Error on soft X-ray flux from XMM-Newton --/F ERR_FLUX02_2KEV
    xmm_hard_flux      float NOT NULL, --/U ergs/cm2/s --/D Hard (4.5-12.0 keV) X-ray flux from XMM-Newton --/F FLUX45_12KEV
    xmm_hard_flux_err  float NOT NULL, --/U ergs/cm2/s --/D Error on hard X-ray flux from XMM-Newton --/F ERR_FLUX45_12KEV
    xmm_flux           float NOT NULL, --/U ergs/cm2/s --/D Total weighted average X-ray flux (0.2-12.0 keV) from XMM-Newton --/F FLUX02_12KEV
    xmm_flux_err       float NOT NULL, --/U ergs/cm2/s --/D Error on total weighted average X-ray flux from XMM-Newton --/F ERR_FLUX02_12KEV
    xmm_sgl_lum        float NOT NULL, --/U erg/s --/D Total X-ray luminosity (0.2-12.0 keV) from XMM-Newton using the longest exposure --/F LUM02_12KEV_SGL
    xmm_soft_lum       float NOT NULL, --/U erg/s --/D Soft (0.5-2.0 keV) X-ray luminosity from XMM-Newton --/F LUM05_2KEV
    xmm_hard_lum       float NOT NULL, --/U erg/s --/D Hard (2.0-12.0 keV) X-ray luminosity from XMM-Newton --/F LUM2_12KEV
    xmm_luminosity     float NOT NULL, --/U erg/s --/D Total (0.2-12.0 keV) X-ray luminosity from XMM-Newton --/F LUM02_12KEV
    xmm_lum_flag       smallint NOT NULL, --/D Flag for upper limit for hard X-ray flux --/F LUMX2_12_UPPER
    sdss2xmm_sep       float NOT NULL, --/U arcsec --/D SDSS-XMM-Newton separation
    galex_matched      smallint NOT NULL, --/D GALEX match flag
    fuv                float NOT NULL, --/U nanomaggies --/D FUV flux (GALEX)
    fuv_ivar           float NOT NULL, --/U 1/nanomaggies^2 --/D Inverse variance of FUV flux
    nuv                float NOT NULL, --/U NUV flux (GALEX)
    nuv_ivar           float NOT NULL, --/U 1/nanomaggies^2 --/D Inverse variance of NUV flux
    jmag               float NOT NULL, --/U mag --/D J magnitude (Vega, 2MASS)
    jmag_err           float NOT NULL, --/U mag --/D Error in J magnitude --/F err_jmag
    jsnr               float NOT NULL, --/D J-Band S/N
    jrdflag            int NOT NULL, --/D H-Band photometry flag
    hmag               float NOT NULL, --/U mag --/D H magnitude (Vega, 2MASS)
    hmag_err           float NOT NULL, --/U mag --/D Error in H magnitude --/F err_hmag
    hsnr               float NOT NULL, --/D H-Band S/N
    hrdflag            int NOT NULL, --/D H-Band photometry flag
    kmag               float NOT NULL, --/U mag --/D K magnitude (Vega, 2MASS)
    kmag_err           float NOT NULL, --/U mag --/D Error in K magnitude --/F err_kmag
    ksnr               float NOT NULL, --/D K-Band S/N
    krdflag            int NOT NULL, --/D K-Band photometry flag
    sdss2mass_sep      float NOT NULL, --/U arcsec --/D SDSS-2MASS separation
    w1mag              float NOT NULL, --/U mag --/D W1 magnitude (Vega, WISE)
    w1mag_err          float NOT NULL, --/U mag --/D Error in W1 magnitude --/F err_w1mag
    w1snr              float NOT NULL, --/D S/N in W1 band
    w1chi2             float NOT NULL, --/D chi-squared in W1 band
    w2mag              float NOT NULL, --/U mag --/D W2 magnitude (Vega, WISE)
    w2mag_err          float NOT NULL, --/U mag --/D Error in W2 magnitude --/F err_w2mag
    w2snr              float NOT NULL, --/D S/N in W2 band
    w2chi2             float NOT NULL, --/D chi-squared in W2 band
    w3mag              float NOT NULL, --/U mag --/D W3 magnitude (Vega, WISE)
    w3mag_err          float NOT NULL, --/U mag --/D Error in W3 magnitude --/F err_w3mag
    w3snr              float NOT NULL, --/D S/N in W3 band
    w3chi2             float NOT NULL, --/D chi-squared in W3 band
    w4mag              float NOT NULL, --/U mag --/D W4 magnitude (Vega, WISE)
    w4mag_err          float NOT NULL, --/U mag --/D Error in W4 magnitude --/F err_w4mag
    w4snr              float NOT NULL, --/D S/N in W4 band
    w4chi2             float NOT NULL, --/D chi-squared in W4 band
    cc_flags           varchar(4) NOT NULL, --/D WISE contamination and confusion flag
    ph_flags           varchar(4) NOT NULL, --/D WISE photometric quality flag
    sdss2wise_sep      float NOT NULL, --/U arcsec --/D SDSS-WISE separation
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
    first_flux         float NOT NULL, --/U mJy --/D FIRST peak flux density at 20 cm
    first_snr          float NOT NULL, --/D S/N of the FIRST flux density
    sdss2first_sep     float NOT NULL, --/U arcsec --/D SDSS-FIRST separation
);
