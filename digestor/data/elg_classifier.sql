CREATE  TABLE elg_classifier (
-------------------------------------------------------------------------------
--/H  The DR16 ELG Classifier
--
--/T This table gives the classification of 0.32<z<0.8 emission line galaxies 
--/T with good [OIII], [OII], Hb stellar velocity dispersion, u, g, r, i, z magnitudes 
--/T measurements using the random forest classifier developed in Zhang et al. 
--/T (in prep). Project site is https://github.com/zkdtc/MLC_ELGs. Code V1_0 is 
--/T used For DR16. Contact zkdtckk@gmail.com for more informations and most 
--/T up-to-date version.
-------------------------------------------------------------------------------

SPECOBJID     bigint NOT NULL, --/D Unique database ID based on PLATE, MJD, FIBERID, RUN2D --/K ID_CATALOG
MJD           int NOT NULL, --/D Date the data was taken
PLATE         smallint NOT NULL, --/D Plate number
FIBERID       smallint NOT NULL, --/D Fiber number
z             float NOT NULL, --/D Redshift
O3_Hb         float NOT NULL, --/D Log ([OIII] 5007)/Hbeta.
O2_Hb         float NOT NULL, --/D Log ([OII] 3726+[OII] 3729)/Hbeta
sigma_o3      float NOT NULL, --/D Log [OIIII] 5007 line width. Instrument dispersion is NOT corrected.
sigma_star    float NOT NULL, --/D Stellar velocity dispersion.
u_g           float NOT NULL, --/D u-g color k-corrected to z=0.1. --/F U_G
g_r           float NOT NULL, --/D g-r color k-corrected to z=0.1. --/F G_R
r_i           float NOT NULL, --/D r-i color k-corrected to z=0.1. --/F R_I
i_z           float NOT NULL, --/D i-z color k-corrected to z=0.1. --/F I_Z
TYPE          smallint NOT NULL, --/D  Class of object. 1=starforming galaxy, 2=composite, 3=AGN, 4=LINER
);
