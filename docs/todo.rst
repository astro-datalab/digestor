=====
TO DO
=====

* Set SDSS-style "null values":

  - For real and double precision, ``not numpy.isfinite()`` goes to -9999.
  - For real, ``abs(x) > 3.4e+38`` goes to -9999.
  - Convert commas to '%2C'?  Not really needed if we're avoiding CSV.

* SQL functions for ``specObjID``, etc.
* Post-load SQL.
