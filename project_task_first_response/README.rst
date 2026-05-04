.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================
Task first response
===================

This module measures the **first response time** for project tasks.

It records when the first external reply is posted on a task and calculates
the elapsed working time between task creation and that first reply using
the project working calendar.

Features
========

- Stores the **first reply date** (first external comment)
- Calculates:
  
  - Working hours to first reply
  - Working days to first reply

- Uses Odoo core working time calculation (resource calendar)
- Integrates into project task reporting

Configuration
=============

No configuration is required.

To get accurate working time calculations:

- Ensure the project has a **Working Time (resource calendar)** configured

Usage
=====

1. Create a project task
2. Post an external message (non-internal comment) on the task

Result:

- The first reply date is stored
- Working hours and days to reply are calculated

Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Jarmo Kortetjärvi <jarmo.kortetjarvi@futural.fi>
* Timo Kekäläinen <timo.kekalainen@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy
