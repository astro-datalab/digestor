=====
TO DO
=====

* Set SDSS-style "null values":

  - For real and double precision, ``not numpy.isfinite()`` goes to -9999
    (this is already implemented).
  - For real, ``abs(x) > 3.4e+38`` goes to -9999.  But in practice, in any
    safe FITS to SQL conversion, this would be enforced anyway.
  - Convert commas to '%2C'?  Not really needed if we're avoiding CSV.
  - The conversion is SDSS specific, but currently happens in the base digestor class.

* SQL functions for ``specObjID``, etc.
* Need instructions for indexing DL-specific tables.
* Post-load SQL.
* Support pre-computed columns that are exactly equivalent to Data Lab columns,
  for example, ``(L, B)``  in photoObj files is equivalent to ``(glon, glat)``.
