=======================
"Ingest Party" Tutorial
=======================

Provenance
----------

This file is based on ``/net/dl1/users/datalab/ingest_party/Tutorial.txt``,
used for the Data Ingest Tutorial on 27 September 2017, and subsequently
revised 14 August 2018.

Outline
-------

Tips and Pitfalls of Data Publication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Overview of steps needed to create a TAP/DB data service
  from "raw" data files
- Catalogs-only for this discussion
- Current state-of-the-art
- w/ discussion of where development needed

Input Table Formats
~~~~~~~~~~~~~~~~~~~

- FITS bintables (if you're lucky)
- CSV/TSV/ASCII
- VOTables (from external TAP services)
- Other (SExtractor files, custom table formats, etc)
- NOTE:

  * Tables may not have coherent schema or descriptions
  * Tables may not be uniform (*e.g.* variable string lengths)
  * Tools may not exist to read data of a particular type into DB

A Reasonable "Standard" Schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Per-object tables (object, photavg, etc)
- Summary tables vs full-width per-band
- Per-measurement tables (source, photmag, etc)
- matched-IDs vs single-epoch catalogs
- Per-exposure tables (to tie rows to image origins)
- Per-field/brick/tile tables
- Crossmatch tables (as needed)
- common object/exposure/field IDs to connect them all
- consider what example queries might be submitted

Optimized DB Table Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- minimal needed datatype for colummns
- no int/long when smallint will do, *e.g.* 'brick' or 'tile' number
- type-ordered for page-packing efficiency (can be up to 20% speedup)
- 'fillfactor' for data/indices on static tables
- wide tables split into multiple tables (*e.g.* DECaLS)
- move little-used columns to a separate table to optimize queries
  of the "main" data table
- CLUSTER (co-locate on disk) by main search criteria (typically position)
- Column-stored versions of tables
- very fast for range searches on all columns
- not so great for crossmatches
- Pre-computed columns -- faster than computing in query
- colors, coords, etc
- Index by most commonly used constraints (pos/flux/shape/quality, etc)

DL-Standard Additional Columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Object ID (some services like SCS require primary ID)
- Spatial indices::

    htm9       HTM order 9
    ring256    Healpix (Ring, k=8, nside=256)
    nest4096   Healpix (Nest, k=12, nside=4096)
    random_id  Random float 0.0 -> 100.0 for sampling

- Coordinates::

    Ecliptic coords        (e.g. "objects < 10deg from ecliptic")
    Galactic coords        (e.g. "high galactic latitude")
    ICRS Precessed coords  (?)

- Magnitudes
- Converted fluxes
- Deredenned mags
- Colors in adjacent bands
- S/N from IVAR
- Preview URLs (*e.g.* to object cutout)

Steps to Create a TAP DB
------------------------

1. Transfer data from source to working dir
2. Transfom data as needed to "ingestible format"
3. Create tables in the database
4. Load the data into the database
5. Type order for optimal storage
6. Cluster data
7. Index columns
8. Create any table views needed
9. Set permissions on schema / tables
10. Create and load TAP Schema


1 Data Transfer
~~~~~~~~~~~~~~~~

Method used depends on data source.

- In-house survey datasets::

    % cp -rp /net/mss1/archive/hlsp/<survey> /dl2/data

- To mirror contents of a web URL (*e.g.* PHAT)::

    % wget -q --mirror --no-parent <url>

- To sync a list of files from a remote server (*e.g.* DES/DECaLS)::

    % rsync -avzR --files-from=<flist> <user>@<host>:/ . 2>&1 >> _out

- To "mine" data from a remote TAP service (*e.g.* Skinny PanSTARRS)::

    % stilts tapquery tapurl="..." adql="..." out=file001.fits

- To create a crossmatch table::

    % stilts cdsskymatch .....
    % stilts tapkymatch .....

2 Data Transformation
~~~~~~~~~~~~~~~~~~~~~

- Add computed columns
- Change datatypes
- Rename (or delete) columns (*e.g.* 'ra' *vs.* 'raj2000')
- Convert table format to one that can be loaded into DB

STILTS is the most useful tool here depending on format.  The 'tpipe'
task can process a command file to add/del/rename columns and produce
a new output table format.

- can be scripted to process large numbers of files (in parallel!)
- transformed tables can be loaded (sometimes) faster than performing
  a join with added columns (or table split) in the DB

For example, a command file (called '_cmd_all') such as::

    explodeall;
    addcol htm9 "(int)htmIndex(9,ra,dec)";
    addcol ring256 "(int)healpixRingIndex(8,ra,dec)";
    addcol nest4096 "(int)healpixNestIndex(12,ra,dec)";
    addskycoords -inunit deg -outunit deg icrs galactic ra dec glon glat;
    addskycoords -inunit deg -outunit deg icrs ecliptic ra dec elon elat;

Additional columns can be added for converted fluxes/colors, to delete or
rename columns, or to do other forms of table processing (see the STILTS
'tpipe' documentation).

This command file can be used to add standard Data Lab columns to a FITS
table using the command::

    % stilts tpipe in=indata.fits \
        cmd='@_cmd_all' ofmt='fits-basic' out=outdata.fits

Scripts can be written to loop over lists of files/directories to process
and those lists can be split to run parallel instances to transform the
files (*e.g.* DECaLS would take ~10 days to do serially, can be done in one
day if parallelized).

3 Create tables in the database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before a table can be loaded in the database, it must be created in SQL.
Creating a table from a transformed file ensures we don't waste time
rewritng a loaded table in the DB later on (*e.g.* to add an ID column to
a 1 TB table).

- FITS/VOTable files contain needed type information for columns
- other formats (*e.g.* CSV) require type to be inferred lexically

  - variable-length columns (*e.g.* strings)
  - NaN / Inf values
  - wrong type inference issues.

By generating a "CREATE TABLE" statement at this stage we can accomplish
several things at once:

- we can ensure/modify column types before data are loaded
- we can re-order columns by type for disk efficiency
- we can set the table 'fillfactor' to minimize disk footprint

For example, the following CREATE statement orders columns by type as
largest-to-smallest with variable 'text' at the end, and set the table
fill value at 100% -- all of this ensures the smallest disk footprint
but assumes we'll never need to update the table by inserting new rows
once it is loaded::

    CREATE TABLE IF NOT EXISTS mydata (
        objid     bigint,
        htm9      bigint,
        ra        double precision,
        dec       double precision,
        random_id real,
        pix256    integer,
        pix4096   integer,
        brick     smallint,
        name      text
    ) with (fillfactor=100);

However, this statement is almost never generated optimally from
the input data files, so the recommended tactic is to generate the statement
as best as possible and then modify it by hand.  Tools that can be used:

CSVSQL - Create DB tables from CSV files
++++++++++++++++++++++++++++++++++++++++

::

    % csvsql -i postgresql test.csv | psql tapdb datalab

Pluses:

- part of 'csvkit' python package for CSV manipulation

Minuses:

- type inference not always great
- conflicting or confusing options

FITS2DB - Create/Load DB tables from FITS binary tables
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

::

    % fits2db --sql=postgres --create --noload -t <table> <file> | psql tapdb datalab

Pluses:

- Fastest (and only) solution for FITS
- Uses native FITS types, no inference

Minuses:

- won't (yet) do automatic type ordering

STILTS - Specify output table as DB connection
++++++++++++++++++++++++++++++++++++++++++++++

::

    % stilts tpipe in=<file> cmd="@cmds" omode=tosql \
        protocol=postgresql host=gp01 db=tapdb dbtable=<table> \
        write=dropcreate user=datalab

Pluses:

- can transform tables on the fly
- supports multiple input table formats

Minuses:

- need to dump table from DB to modify CREATE statement

4 Load the data into the database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The method used to load the data depends entirely on:

- the format of the input data files

  - format may constrain the available tool options

- the number of files to be ingested that make up a single DB table

  - can ingest be parallelized?
  - is concatenating files before ingest more efficient?

- the size of individual files to be ingested

  - want efficient bulk ingestion of row data

FITS2DB
+++++++

Assuming we are dealing with FITS binary tables, the FITS2DB tool is
the fastest method to ingest tables since it allows for a binary data
option and can be run in parallel to process multiple files.  HOWEVER,
in order to use the binary option:

- the columns in the FITS file MUST be in the same order as the
  database table
- the bintable CANNOT contain array columns
- use of the ``--rid`` flag only works when the task creates the table
  from a single file, or when appending an existing table with a
  random_id column following the data

When ingest small tables that require no transformation, creating and
loading the table can be done using a command such as::

    fits2db --sql=p --create --drop \  # create table
        -B -t mytable file01.fits | psql tapdb datalab
    fits2db --sql=p -C -B -t mytable file02.fits | psql tapdb datalab
    fits2db --sql=p -C -B -t mytable file03.fits | psql tapdb datalab

where the first command creates the table (``--create``) and loads the
contents of 'file01.fits' in binary mode (``-B``); subsequent commands
concatenate (``-C``) that table with contents of 'file02.fits' and so on.

The output of the FITS2DB command is piped to the PSQL client to
avoid building DB connection details into the task itself.  Note that
when not using the ``-B`` binary option, the SQL statements generated by
the task can be viewed/saved for inspection and processing.

Assuming the FITS files were re-written in the transformation stage to
add columns, but are not in the proper type-order as the DB table, the
default ascii output can be used to create INSERT statements so the
FITS table order doesn't need to match the DB.  The ingestion process
is the same as above, just without the ``-B`` binary flag.

See ``fits2db --help`` for addition details and examples (still needs updating).

STILTS
++++++

The STILTS task can likewise be used to create/load tables but is not
always suitable for large tables or large numbers of files.

- For large tables, row INSERTS are done one-at-a-time and so
  processing can be extremely slow
- For large numbers of files there is the added overhead of the
  JAVA startup each time the task is invoked (a few sec for 170,000
  files adds up to real time).

However, for small tables and single files, it is an adequate and easy
solution.


PSQL Client
+++++++++++

The PSQL client would mostly be used to ingest CSV files to an existing
table using a command such as::

    COPY mydata FROM '/path/mydata.csh' DELIMITER ',' CSV HEADER;

There are external tools that likewise do bulk loading of CSV files that
claim faster speeds (*e.g.* pgloader, see http://pgloader.io) that I've
used with varying levels of success.  We may wish to investigate these
further if CSV files become a common input format to be dealt with, however
given that many tables will need to be augmented with standard columns
anyway it may be simplest to do the transformation and write FITS files
on output to settle on FITS2DB as a standard tool.

"Foreign data" extensions also exist in some versions of PostgreSQL that
may be worth investigating as well.  I defer questions on these to Adam.


5 Type order for optimal storage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Type-ordering the table involves re-writing the table so the columns
are stored with the largest datatype sizes (*e.g.* bigint, double) first,
followed by real/int, then shorts, and then char strings.  If the table
was created with the proper type order before loading then this step can be
skipped, otherwise the table can be rewritten using something like::

    CREATE TABLE <new_name> WITH (fillfactor=100) AS (
      SELECT
         ....list columns in type order
      FROM <load_name>
    );
    DROP TABLE <orig_name>;
    ALTER TABLE <new_name> RENAME TO <orig_name>

This step can also be used as an opportunity to drop/rename columns or
to create joined tables.

6 Cluster or type order as needed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clustering data (in Postgres) means a table is physically re-written so
rows being clustered are physically close on disk, putting many of the
likely result rows in the same page and minimizing disk i/o.  We typically
cluster data using the Q3C spatial index so things close on the sky are
close on disk, but also for efficiencies in using that index in a query.

To generate the cluster it is best to begin with an un-indexed table to
avoid recalculation of indices caused by the rewrite. So the first step
once a table is loaded is always::

    CREATE INDEX <index_name> ON <table> (q3c_ang2ipix(ra,dec))
        WITH (fillfactor=100); -- Minimize disk space required by the index.
    CLUSTER <index_name> on <table>;

These two steps CANNOT be parallelized (but can be run in the background
from a script).  Depending on the size of the table, this step may take
hours to days to complete before you can proceed.

7 Index columns
~~~~~~~~~~~~~~~

Once a table has been clustered, other indices can be computed on the
additional columns.  These indices CAN be run in parallel and so typically
they will be run in the background by a shell script using the PSQL client
rather than from an SQL script, *e.g.* ::

    #!/bin/csh -f

    alias P "psql tapdb datalab -c"

    P "create index on main(coadd_object_id) with (fillfactor=100)" &
    P "create index on main(nest4096) with (fillfactor=100)" &
         "      "    "        "        "        "

    # wait for jobs to complete before processing next index set
    wait
    P "create index on main(ra) with (fillfactor=100)" &
    P "create index on main(dec) with (fillfactor=100)" &
         "      "    "        "        "        "

**On the GP machines it is recommended that no more than ~10 index jobs
be executed at time to help minimize impact on the system performance.**


8 Create any table views needed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Table views can be created as *e.g.* ::

    CREATE VIEW galaxy as (
        SELECT * FROM ls_dr3.tractor_primary WHERE type <> 'PSF'
    );

Once create, select permissions must be granted to the view and it
can be moved to the schema as described below.


9 Set permissions on schema / tables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Database tables are created using the 'datalab' user account which has
full permissions to create/delete/modify tables.  The TAP service and
Query Manager connect to the database as the 'dlquery' user who only
has read-access to the data tables.  To create these permissions once a
table is loaded, use the commands::

    CREATE SCHEMA myschema;
    GRANT USAGE ON SCHEMA myschema TO dlquery;
    and
    GRANT SELECT ON mytable TO dlquery;
    GRANT SELECT ON myview TO dlquery;

Once the permissions have been granted (or even afterwards), tables and
views may be moved to the schema::

    ALTER TABLE mydata SET SCHEMA myschema;
    ALTER VIEW myview SET SCHEMA myschema;

10 Create and load TAP Schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The final stage of data ingestion is to make the new schema/tables visible
to the TAP service.  This is done by populating the 'tap_schema' tables
that contain the table metadata use by the TAP protocol, *e.g.* ::

    % psql tapdb datalab

    tapdb=# \dt tap_schema.*
                 List of relations
       Schema   |    Name     | Type  |  Owner
    ------------+-------------+-------+---------
     tap_schema | columns     | table | datalab
     tap_schema | key_columns | table | datalab
     tap_schema | keys        | table | datalab
     tap_schema | schemas     | table | datalab
     tap_schema | tables      | table | datalab
    (5 rows)

Rather than manipulating these tables directly in the database (*e.g.* to
indicate indexed columns, add column UCDs row-by-row, etc), we've chosen
to use JSON descriptor files for each schema to allow users to edit the
files directly and then simply load them in bulk for a particular schema.

The tools currently in use are first-efforts and more work is needed to
develop features and additional tools, however the process breaks down into
the following steps:

1. Create a template JSON file for your new schema
2. Edit the file to add content, correct column types/indexes, etc
3. Load the JSON file to the 'tap_schema' tables.

Note we're assumimg the TAP service itself has already been configured for
the machine (-- the content of the TAP service is dynamically driven by
what's in the tap_schema tables).

The 'mkjson' and 'tap_schema.py' tasks mentioned here can typically
be found in the /home/datalab/TapSchema directory on a GP machine
running a TAP service (gp01/2/3/4).  The TapSchema is also available
from GitLab.

Step 1: Create a template JSON file for your new schema
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

A script task exists (MKJSON) that takes as a single argument the name
of a schema in the local tap database, the output of this script is
saved as the template JSON file::

    % mkjson myschema |& tee myschema.json

The JSON file itself then looks something like::

    {
      "schemas":    [
                      { "schema_name" : "tap_schema",
                        "description" : "TAP Schema Tables",
                        "utype" : ""
                      }
                    ],
      "tables":     [
                      { "schema_name" : "tap_schema",
                        "table_name" : "columns",
                        "table_type" : "table",     "utype" : "",
                        "description" : "Columns in the tables"
                       },
                            :       :       :       :
                    ],
      "columns":    [
                      { "table_name" : "columns",
                        "column_name" : "table_name",
                        "description" : "",
                        "unit" : "", "ucd" : "", "utype" : "",
                        "datatype" : "", "size" : 1,
                        "principal" : 0, "indexed" : 0, "std" : 0
                      },
                            :       :       :       :
                    ],
      "keys":       [
                      { "key_id" : "",
                        "from_table" : "",
                        "target_table" : "",
                        "description" : "",
                        "utype" : ""
                      }
                    ],
      "key_columns":
                    [
                      { "key_id" : "",
                        "from_column" : "",
                        "target_column" : ""
                      }
                    ]
    }

Step 2: Edit the file to add content, correct column types/indexes, etc
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Modifying the template JSON file can be done using your favorite
editor.  Although the JSON file is (usually) ready to load as-is, a
few changes may be required:

- sometimes a comma is missing when more than one table exists
- 'text' datatypes on columns must explicitly be changed to
  a 'character' datatype and an appropriate 'size' large enough
  to contain the string (to avoid truncation in TOPCAT).

Additional edits are also needed to provide

- descriptions
- units
- ucds (note service-required UCDs)
- index flags (not currently automatic)

Step 3: Load the JSON file to the 'tap_schema' tables
+++++++++++++++++++++++++++++++++++++++++++++++++++++

Once the edits are complete, the JSON file can be validated for errors
using a small script such as::

    #!/usr/bin/python

    import sys, json  # to read config files

    for a in sys.argv[1:]:
        print "Validating file '%s' ..." % a,
        try:
            with open (a) as fd:
                data = json.load (fd)
            print 'OK'
        except ValueError, e:
            print 'Error'
            print e

The file is then loaded into the tap_schema using the command::

    % python tap_schema.py -r -l -i myschema.json

where the ``-r`` removes any existing schema definitions, ``-l`` says to
load the new schema, and ``-i`` gives the input file to process.

Hands-On Exercises
------------------

Data for the exercises can be found at::

    /dl1/users/datalab/ingest_party

This directory contains the sample data files for the hands-on exercises
for the "Data Lab Ingest Party".  Directory contents are as follows::

    table1    ALLWISE catalog distribution (subset of all files)
    table2    PHAT v2 'phot_mod' table input files (subset of all files)
    table3    NDWFS DR3 catalog file (single file only)

The goal of the exercises is simple: load each set of data files into a
database table, optimizing, extending and reformatting where necessary.
