===================
Digestor Change Log
===================

0.5.1 (unreleased)
------------------

* No changes yet.

0.5.0 (2021-09-10)
------------------

* Migrate continuous integration to GitHub Actions (PR `#14`_, `#15`_).
* Planned changes:
  - DR12 stellar mass tables
  - DR16 spiders tables, etc.

.. _`#14`: https://github.com/astro-datalab/digestor/pull/14
.. _`#15`: https://github.com/astro-datalab/digestor/pull/15

0.4.0 (2020-06-30)
------------------

* Updates for multiple data releases (PR `#12`_).
  - Support loading DR12
  - Support loading DR16
  - Add ``sdss_joinid`` column to DR14

.. _`#12`: https://github.com/astro-datalab/digestor/pull/12

0.3.1 (2020-02-28)
------------------

* Reference tag before proceeding with SDSS DR16 ingestion.
* Add column descriptions for simple views to metadata files (PR `#10`_).
* Fix a variety of outstanding bugs (PR `#9`_).

.. _`#10`: https://github.com/astro-datalab/digestor/pull/10
.. _`#9`: https://github.com/astro-datalab/digestor/pull/9

0.3.0 (2019-03-25)
------------------

* Support for SDSS DR14 VACs (PR `#7`_).
* Fix some test problems (PR `#4`_).

.. _`#7`: https://github.com/astro-datalab/digestor/pull/7
.. _`#4`: https://github.com/astro-datalab/digestor/pull/4

0.2.1 (2018-08-16)
------------------

* Store fully-qualified table name in column descriptions.

0.2.0 (2018-08-16)
------------------

* Support processing of SDSS photometric data (PR `#3`_).

.. _`#3`: http://gitlab.noao.edu/weaver/digestor/merge_requests/3

0.1.0 (2018-08-09)
------------------

* Reference tag.

  - Fully working version.
  - Tested on SDSS DR14 platex and specobjall tables.
