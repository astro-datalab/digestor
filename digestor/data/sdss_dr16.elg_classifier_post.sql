--
-- This file is intended to be processed by the Python format method, and
-- executed *after* the table data has been loaded
--
-- CREATE INDEX elg_classifier_q3c_ang2ipix ON sdss_dr16.elg_classifier (q3c_ang2ipix(ra, dec)) WITH (fillfactor=100);
-- CLUSTER elg_classifier_q3c_ang2ipix ON sdss_dr16.elg_classifier;
-- CREATE INDEX elg_classifier_glon_q3c_ang2ipix ON sdss_dr16.elg_classifier (q3c_ang2ipix(glon, glat)) WITH (fillfactor=100);
-- CREATE INDEX elg_classifier_elon_q3c_ang2ipix ON sdss_dr16.elg_classifier (q3c_ang2ipix(elon, elat)) WITH (fillfactor=100);
ALTER TABLE sdss_dr16.elg_classifier ADD PRIMARY KEY (specobjid);
CREATE UNIQUE INDEX elg_classifier_sdss_joinid ON sdss_dr16.elg_classifier (sdss_joinid) WITH (fillfactor=100);
-- CREATE INDEX elg_classifier_ra ON sdss_dr16.elg_classifier (ra) WITH (fillfactor=100);
-- CREATE INDEX elg_classifier_dec ON sdss_dr16.elg_classifier (dec) WITH (fillfactor=100);
-- CREATE INDEX elg_classifier_elon ON sdss_dr16.elg_classifier (elon) WITH (fillfactor=100);
-- CREATE INDEX elg_classifier_elat ON sdss_dr16.elg_classifier (elat) WITH (fillfactor=100);
-- CREATE INDEX elg_classifier_glon ON sdss_dr16.elg_classifier (glon) WITH (fillfactor=100);
-- CREATE INDEX elg_classifier_glat ON sdss_dr16.elg_classifier (glat) WITH (fillfactor=100);
-- CREATE INDEX elg_classifier_htm9 ON sdss_dr16.elg_classifier (htm9) WITH (fillfactor=100);
-- CREATE INDEX elg_classifier_ring256 ON sdss_dr16.elg_classifier (ring256) WITH (fillfactor=100);
-- CREATE INDEX elg_classifier_nest4096 ON sdss_dr16.elg_classifier (nest4096) WITH (fillfactor=100);
CREATE INDEX elg_classifier_random_id ON sdss_dr16.elg_classifier (random_id) WITH (fillfactor=100);
GRANT SELECT ON sdss_dr16.elg_classifier TO dlquery;
ANALYZE sdss_dr16.elg_classifier;
