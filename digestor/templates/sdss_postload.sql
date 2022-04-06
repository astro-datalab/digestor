--
-- This file is intended to be processed by the Jinja2 template engine, and
-- executed *after* the table data has been loaded
--
CREATE INDEX {{table}}_q3c_ang2ipix ON {{schema}}.{{table}} (q3c_ang2ipix({{ra}}, {{dec}})) WITH (fillfactor=100);
CLUSTER {{table}}_q3c_ang2ipix ON {{schema}}.{{table}};
-- CREATE INDEX {{table}}_{{glon}}_q3c_ang2ipix ON {{schema}}.{{table}} (q3c_ang2ipix({{glon}}, {{glat}})) WITH (fillfactor=100);
-- CREATE INDEX {{table}}_{{elon}}_q3c_ang2ipix ON {{schema}}.{{table}} (q3c_ang2ipix({{elon}}, {{elat}})) WITH (fillfactor=100);
ALTER TABLE {{schema}}.{{table}} ADD PRIMARY KEY ({{pkey}});
CREATE UNIQUE INDEX {{table}}_sdss_joinid ON {{schema}}.{{table}} (sdss_joinid) WITH (fillfactor=100);
CREATE INDEX {{table}}_{{ra}} ON {{schema}}.{{table}} ({{ra}}) WITH (fillfactor=100);
CREATE INDEX {{table}}_{{dec}} ON {{schema}}.{{table}} ({{dec}}) WITH (fillfactor=100);
CREATE INDEX {{table}}_{{elon}} ON {{schema}}.{{table}} ({{elon}}) WITH (fillfactor=100);
CREATE INDEX {{table}}_{{elat}} ON {{schema}}.{{table}} ({{elat}}) WITH (fillfactor=100);
CREATE INDEX {{table}}_{{glon}} ON {{schema}}.{{table}} ({{glon}}) WITH (fillfactor=100);
CREATE INDEX {{table}}_{{glat}} ON {{schema}}.{{table}} ({{glat}}) WITH (fillfactor=100);
CREATE INDEX {{table}}_htm9 ON {{schema}}.{{table}} (htm9) WITH (fillfactor=100);
CREATE INDEX {{table}}_ring256 ON {{schema}}.{{table}} (ring256) WITH (fillfactor=100);
CREATE INDEX {{table}}_nest4096 ON {{schema}}.{{table}} (nest4096) WITH (fillfactor=100);
CREATE INDEX {{table}}_random_id ON {{schema}}.{{table}} (random_id) WITH (fillfactor=100);
GRANT SELECT ON {{schema}}.{{table}} TO dlquery;
ANALYZE {{schema}}.{{table}};
