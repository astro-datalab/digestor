--
-- This file is intended to be processed by the Jinja2 template engine, and
-- executed *after* the table data has been loaded
--
CREATE INDEX {{table}}_q3c_ang2ipix ON {{schema}}.{{table}} (q3c_ang2ipix({{ra}}, {{dec}})) WITH (fillfactor=100);
CLUSTER {{table}}_q3c_ang2ipix ON {{schema}}.{{table}};
-- CREATE INDEX {{table}}_{{glon}}_q3c_ang2ipix ON {{schema}}.{{table}} (q3c_ang2ipix({{glon}}, {{glat}})) WITH (fillfactor=100);
-- CREATE INDEX {{table}}_{{elon}}_q3c_ang2ipix ON {{schema}}.{{table}} (q3c_ang2ipix({{elon}}, {{elat}})) WITH (fillfactor=100);
ALTER TABLE {{schema}}.{{table}} ADD PRIMARY KEY ({{pkey}});
CREATE UNIQUE INDEX {{table}}_uint64_{{pkey}} ON {{schema}}.{{table}} ({{schema}}.uint64({{pkey}})) WITH (fillfactor=100);
{%- if join -%}
CREATE UNIQUE INDEX {{table}}_sdss_joinid ON {{schema}}.{{table}} (sdss_joinid) WITH (fillfactor=100);
{%- endif %}
{%- if table == 'specobjall' -%}
--
-- Index columns used to create a view.
--
CREATE INDEX {{table}}_plateid ON {{schema}}.{{table}} (plateid) WITH (fillfactor=100);
CREATE INDEX {{table}}_scienceprimary ON {{schema}}.{{table}} (scienceprimary) WITH (fillfactor=100);
ALTER TABLE {{schema}}.{{table}} ADD CONSTRAINT {{table}}_platex_fk FOREIGN KEY (plateid) REFERENCES {{schema}}.platex (plateid);
CREATE INDEX {{table}}_uint64_plateid ON {{schema}}.{{table}} ({{schema}}.uint64(plateid)) WITH (fillfactor=100);
{%- endif %}
CREATE INDEX {{table}}_{{ra}} ON {{schema}}.{{table}} ({{ra}}) WITH (fillfactor=100);
CREATE INDEX {{table}}_{{dec}} ON {{schema}}.{{table}} ({{dec}}) WITH (fillfactor=100);
{%- if table == 'photoplate' -%}
CREATE INDEX {{table}}_l ON {{schema}}.{{table}} (l) WITH (fillfactor=100);
CREATE INDEX {{table}}_b ON {{schema}}.{{table}} (b) WITH (fillfactor=100);
{%- else -%}
CREATE INDEX {{table}}_{{elon}} ON {{schema}}.{{table}} ({{elon}}) WITH (fillfactor=100);
CREATE INDEX {{table}}_{{elat}} ON {{schema}}.{{table}} ({{elat}}) WITH (fillfactor=100);
{%- endif %}
CREATE INDEX {{table}}_{{glon}} ON {{schema}}.{{table}} ({{glon}}) WITH (fillfactor=100);
CREATE INDEX {{table}}_{{glat}} ON {{schema}}.{{table}} ({{glat}}) WITH (fillfactor=100);
CREATE INDEX {{table}}_htm9 ON {{schema}}.{{table}} (htm9) WITH (fillfactor=100);
CREATE INDEX {{table}}_ring256 ON {{schema}}.{{table}} (ring256) WITH (fillfactor=100);
CREATE INDEX {{table}}_nest4096 ON {{schema}}.{{table}} (nest4096) WITH (fillfactor=100);
CREATE INDEX {{table}}_random_id ON {{schema}}.{{table}} (random_id) WITH (fillfactor=100);
{% if table == 'platex' -%}
--
-- Index column used to create a view.
--
CREATE INDEX {{table}}_programname ON {{schema}}.{{table}} (programname) WITH (fillfactor=100);
{% endif -%}
{%- if table == 'photoplate' -%}
UPDATE {{schema}}.{{table}} SET dered_u = u - extinction_u;
UPDATE {{schema}}.{{table}} SET dered_g = g - extinction_g;
UPDATE {{schema}}.{{table}} SET dered_r = r - extinction_r;
UPDATE {{schema}}.{{table}} SET dered_i = i - extinction_i;
UPDATE {{schema}}.{{table}} SET dered_z = z - extinction_z;
{%- endif %}
GRANT SELECT ON {{schema}}.{{table}} TO dlquery;
{%- if table == 'specobjall' -%}
CREATE VIEW {{schema}}.specobj AS SELECT s.* FROM {{schema}}.{{table}} AS s WHERE s.scienceprimary = 1;
CREATE VIEW {{schema}}.seguespecobjall AS SELECT s.* FROM {{schema}}.{{table}} AS s JOIN {{schema}}.platex AS p ON s.plateid = p.plateid WHERE p.programname LIKE 'seg%';
CREATE VIEW {{schema}}.segue1specobjall AS SELECT s.* FROM {{schema}}.{{table}} AS s JOIN {{schema}}.platex AS p ON s.plateid = p.plateid WHERE p.programname LIKE 'seg%' AND p.programname NOT LIKE 'segue2%';
CREATE VIEW {{schema}}.segue2specobjall AS SELECT s.* FROM {{schema}}.{{table}} AS s JOIN {{schema}}.platex AS p ON s.plateid = p.plateid WHERE p.programname LIKE 'segue2%';
GRANT SELECT ON {{schema}}.specobj TO dlquery;
GRANT SELECT ON {{schema}}.seguespecobjall TO dlquery;
GRANT SELECT ON {{schema}}.segue1specobjall TO dlquery;
GRANT SELECT ON {{schema}}.segue2specobjall TO dlquery;
{%- endif %}
ANALYZE {{schema}}.{{table}};
