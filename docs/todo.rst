=====
TO DO
=====

* Some primary keys are in the range where a signed 64-bit integer would be
  negative, *i.e.* :math:`2^{63} < k < 2^{64} - 1`.  Need functions to
  deal with this in SQL.
* ``bestObjID`` has some rows that are blank strings.  Those should be set to zero.
  In general, need to be able to deal with ``inf``, ``nan``.
* Set SDSS-style "null values":

  - During string to bigint conversions, blank strings become zero.
  - For real and double precision, ``not numpy.isfinite()`` goes to -9999.
  - For real, ``abs(x) > 3.4e+38`` goes to -9999.
  - Convert commas to '%2C'?  Not really needed if we're avoiding CSV.

* Only convert to ``np.uint64`` if absolutely necessary.
* Set ``uint=False`` when writing final FITS file?
* SQL functions for ``specObjID``, etc.
* Post-load SQL.
