=====================================================
 Complete dependency version inventory (generated)
=====================================================

:Generated: 2026-07-28 from PyPI JSON metadata (2371 individual release records,
            49 packages)
:Companion to: ``upgrade-plan.rst`` — that document explains *what to do*; this
               one is the raw evidence it was derived from.

Every release of every package in the dependency tree, from the version this
project currently pins (or the earliest relevant one) through to the newest
available, with the Python requirement and the declared dependencies of each.

Consecutive releases that declare **identical** Python requirements, Django
classifiers and dependencies are collapsed into one entry — so
"``1.5 – 1.6.11 (25 releases)``" means all 25 of those releases declare exactly
what is listed beneath it.

Reading the ``:Python:`` field
==============================

``>=3.8``
    The release's own ``Requires-Python`` metadata. Authoritative — pip and uv
    enforce it.

``clf:2.7,3.4,3.5``
    The release predates ``Requires-Python`` (roughly, anything before 2016),
    so this is the list of ``Programming Language :: Python ::`` classifiers
    instead. **Advisory only** — nothing enforces it, and it is often stale.

``-``
    Neither is present. Compatibility has to come from the changelog; see
    ``upgrade-plan.rst`` Part 2.

.. contents::
   :depth: 1
   :local:


Runtime dependencies
====================

django
------
* **1.5 – 1.6.11 (25 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3``
    :Requires: nothing declared
* **1.7**
    :Python: ``clf:2.7,3.2,3.3,3.4``
    :Requires: nothing declared
* **1.7.1**
    :Python: ``-``
    :Requires: nothing declared
* **1.7.2 – 1.8.7 (18 releases)**
    :Python: ``clf:2.7,3.2,3.3,3.4``
    :Requires: nothing declared
* **1.8.8 – 1.8.19 (12 releases)**
    :Python: ``clf:2.7,3.2,3.3,3.4,3.5``
    :Requires: nothing declared
* **1.9 – 1.10.8 (23 releases)**
    :Python: ``clf:2.7,3.4,3.5``
    :Requires: nothing declared
* **1.11 – 1.11.16 (17 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``pytz``
* **1.11.17 – 1.11.29 (12 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6,3.7``
    :Requires: ``pytz``
* **2.0 – 2.0.13 (13 releases)**
    :Python: ``>=3.4``
    :Requires: ``pytz``
* **2.1 – 2.1.15 (15 releases)**
    :Python: ``>=3.5``
    :Requires: ``pytz``
* **2.2 – 2.2.13 (14 releases)**
    :Python: ``>=3.5``
    :Requires: ``pytz; sqlparse``
* **2.2.14 – 2.2.28 (15 releases)**
    :Python: ``>=3.5``
    :Requires: ``pytz; sqlparse>=0.2.2``
* **3.0 – 3.0.14 (15 releases)**
    :Python: ``>=3.6``
    :Requires: ``asgiref~=3.2; pytz; sqlparse>=0.2.2``
* **3.1 – 3.1.2 (3 releases)**
    :Python: ``>=3.6``
    :Requires: ``asgiref~=3.2.10; pytz; sqlparse>=0.2.2``
* **3.1.3 – 3.1.14 (12 releases)**
    :Python: ``>=3.6``
    :Requires: ``asgiref<4,>=3.2.10; pytz; sqlparse>=0.2.2``
* **3.2 – 3.2.25 (26 releases)**
    :Python: ``>=3.6``
    :Requires: ``asgiref<4,>=3.3.2; pytz; sqlparse>=0.2.2``
* **4.0 – 4.0.10 (11 releases)**
    :Python: ``>=3.8``
    :Requires: ``asgiref<4,>=3.4.1; backports.zoneinfo;python_version<"3.9"; sqlparse>=0.2.2; tzdata;sys_platform=="win32"``
* **4.1 – 4.1.13 (14 releases)**
    :Python: ``>=3.8``
    :Requires: ``asgiref<4,>=3.5.2; backports.zoneinfo;python_version<"3.9"; sqlparse>=0.2.2; tzdata;sys_platform=="win32"``
* **4.2 – 4.2.30 (31 releases)**
    :Python: ``>=3.8``
    :Requires: ``asgiref<4,>=3.6.0; backports.zoneinfo;python_version<"3.9"; sqlparse>=0.3.1; tzdata;sys_platform=="win32"``
* **5.0**
    :Python: ``>=3.10``
    :Requires: ``asgiref>=3.7.0; sqlparse>=0.3.1; tzdata;sys_platform=="win32"``
* **5.0.1 – 5.0.14 (14 releases)**
    :Python: ``>=3.10``
    :Requires: ``asgiref<4,>=3.7.0; sqlparse>=0.3.1; tzdata;sys_platform=="win32"``
* **5.1 – 5.1.15 (16 releases)**
    :Python: ``>=3.10``
    :Requires: ``asgiref<4,>=3.8.1; sqlparse>=0.3.1; tzdata;sys_platform=="win32"``
* **5.2 – 5.2.16 (17 releases)**
    :Python: ``>=3.10``
    :Requires: ``asgiref>=3.8.1; sqlparse>=0.3.1; tzdata;sys_platform=="win32"``
* **6.0 – 6.0.7 (8 releases)**
    :Python: ``>=3.12``
    :Requires: ``asgiref>=3.9.1; sqlparse>=0.5.0; tzdata;sys_platform=="win32"``

django-photologue
-----------------
* **2.3 – 2.8.3 (10 releases)**
    :Python: ``-``
    :Requires: nothing declared
* **3.0 – 3.1.1 (5 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4``
    :Requires: nothing declared
* **3.2 – 3.3.2 (4 releases)**
    :Python: ``clf:2.7,3.3,3.4``
    :Requires: nothing declared
* **3.4**
    :Python: ``clf:2.7,3.2,3.3,3.4,3.5``
    :Requires: ``Django>=1.8; ExifRead>=2.1.2; Pillow>=2.7.0; django-sortedm2m>=1.0.1``
* **3.4.1 – 3.5.1 (3 releases)**
    :Python: ``clf:2.7,3.2,3.3,3.4,3.5``
    :Requires: ``Django>=1.8; ExifRead>=2.1.2; Pillow>=2.7.0; django-sortedm2m>=1.1.1``
* **3.6**
    :Python: ``clf:2.7,3.3,3.4,3.5``
    :Requires: ``Django>=1.8; ExifRead>=2.1.2; Pillow>=2.7.0; django-sortedm2m>=1.1.1``
* **3.7**
    :Python: ``clf:2.7,3.3,3.4,3.5``
    :Requires: ``Django>=1.8; ExifRead>=2.1.2; Pillow>=2.7.0; django-sortedm2m>=1.3.3``
* **3.8 – 3.8.1 (2 releases)**
    :Python: ``clf:2.7,3.4,3.5``
    :Requires: ``Django>=1.11; ExifRead>=2.1.2; Pillow>=4.3.0; django-sortedm2m>=1.5.0``
* **3.9**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``ExifRead>=2.1.2; Pillow>=4.3.0; django-sortedm2m>=1.5.0``
* **3.10**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``ExifRead>=2.1.2; Pillow>=4.3.0; django-sortedm2m>=2.0.0``
* **3.11 – 3.13 (3 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``ExifRead>=2.1.2; Pillow>=6.0.0; django-sortedm2m>=3.0.0``
* **3.14 – 3.15.1 (3 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``ExifRead>=2.1.2; Pillow>=6.0.0; django-sortedm2m>=3.1.1``
* **3.16 – 3.17 (2 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``ExifRead>=3; Pillow>=9; django-sortedm2m>=3.1.1``
* **3.18**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``ExifRead>=3; Pillow>=10; django-sortedm2m>=4.0.0``
* **3.19**
    :Python: ``>=3.10``
    :Requires: ``Django<6.1,>=5.2; ExifRead>=3.5.1; Pillow>=12.0.0; django-sortedm2m>=4.0.0``
* **3.20**
    :Python: ``>=3.10``
    :Django: 5.2,6.0
    :Requires: ``Django<6.1,>=5.2; Pillow>=12.0.0; django-sortedm2m>=4.0.0``

django-grappelli
----------------
* **2.4.0 – 2.4.4 (5 releases)**
    :Python: ``-``
    :Requires: nothing declared
* **2.4.5 – 2.5.2 (11 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3``
    :Requires: nothing declared
* **2.5.3 – 2.13.1 (28 releases)**
    :Python: ``clf:2.6,2.7,3.1,3.2,3.3``
    :Requires: nothing declared
* **2.13.2 – 2.14.1 (4 releases)**
    :Python: ``clf:3.6,3.7``
    :Requires: nothing declared
* **2.14.2 – 2.14.4 (3 releases)**
    :Python: ``clf:3.6,3.7,3.8``
    :Requires: nothing declared
* **2.15.1 – 2.15.7 (7 releases)**
    :Python: ``clf:3.6,3.7,3.8,3.9``
    :Requires: nothing declared
* **3.0.1 – 4.0.3 (13 releases)**
    :Python: ``clf:3.8,3.9,3.10``
    :Requires: nothing declared
* **4.0.4**
    :Python: ``clf:3.10,3.11,3.12``
    :Requires: nothing declared
* **5.0.0**
    :Python: ``clf:3.12,3.13,3.14``
    :Requires: nothing declared

django-sortedm2m
----------------
* **0.9.0 – 1.0.1 (9 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3``
    :Requires: nothing declared
* **1.0.2 – 1.1.2 (4 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4``
    :Django: 1.5,1.6,1.7,1.8
    :Requires: nothing declared
* **1.2.0 – 1.5.0 (8 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5``
    :Django: 1.5,1.6,1.7,1.8,1.9
    :Requires: nothing declared
* **2.0.0**
    :Python: ``clf:2.7,3.5,3.6,3.7``
    :Django: 1.11,2.0,2.1,2.2
    :Requires: nothing declared
* **3.0.0 – 3.0.2 (3 releases)**
    :Python: ``clf:3.6,3.7,3.8``
    :Django: 2.1,2.2,3.0
    :Requires: nothing declared
* **3.1.1**
    :Python: ``clf:3.6,3.7,3.8,3.9``
    :Django: 2.2,3.0,3.1,3.2
    :Requires: nothing declared
* **4.0.0**
    :Python: ``clf:3.7,3.8,3.9,3.10,3.11,3.12``
    :Django: 4.2,5.0,5.1
    :Requires: nothing declared

django-model-utils
------------------
* **2.0 – 2.3.1 (9 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3``
    :Requires: nothing declared
* **2.4 – 2.5 (2 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4``
    :Requires: nothing declared
* **2.5.1 – 2.6.1 (4 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5``
    :Requires: nothing declared
* **3.0.0**
    :Python: ``clf:2.7,3.3,3.4,3.5``
    :Requires: nothing declared
* **3.1.0**
    :Python: ``clf:2.7,3.3,3.4,3.5``
    :Django: 1.11,2.0
    :Requires: ``Django>=1.8``
* **3.1.1**
    :Python: ``clf:2.7,3.3,3.4,3.5,3.6``
    :Django: 1.8,1.9,1.10,1.11,2.0
    :Requires: ``Django>=1.8``
* **3.1.2**
    :Python: ``clf:2.7,3.3,3.4,3.5,3.6``
    :Django: 1.8,1.9,1.10,1.11,2.0
    :Requires: nothing declared
* **3.2.0**
    :Python: ``clf:2.7,3.6,3.7``
    :Django: 1.11,2.1,2.2
    :Requires: nothing declared
* **4.0.0**
    :Python: ``clf:3.6,3.7,3.8``
    :Django: 2.1,2.2,3.0
    :Requires: nothing declared
* **4.1.0 – 4.1.1 (2 releases)**
    :Python: ``clf:3.6,3.7,3.8,3.9``
    :Django: 2.2,3.0,3.1
    :Requires: ``Django>=2.0.1``
* **4.2.0**
    :Python: ``clf:3.6,3.7,3.8,3.9,3.10``
    :Django: 2.2,3.1,3.2
    :Requires: ``Django>=2.0.1``
* **4.3.1**
    :Python: ``>=3.7``
    :Django: 3.2,4.0,4.1
    :Requires: nothing declared
* **4.4.0 – 4.5.1 (3 releases)**
    :Python: ``>=3.8``
    :Django: 3.2,4.0,4.1,4.2,5.0
    :Requires: ``Django>=3.2``
* **5.0.0**
    :Python: ``>=3.8``
    :Django: 3.2,4.0,4.1,4.2,5.0,5.1
    :Requires: ``Django>=3.2``

psycopg2-binary
---------------
* **2.7.3.2 – 2.7.5 (3 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4,3.5,3.6``
    :Requires: nothing declared
* **2.7.6 – 2.7.7 (3 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4,3.5,3.6,3.7``
    :Requires: nothing declared
* **2.8 – 2.8.6 (7 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: nothing declared
* **2.9 – 2.9.8 (9 releases)**
    :Python: ``>=3.6``
    :Requires: nothing declared
* **2.9.9**
    :Python: ``>=3.7``
    :Requires: nothing declared
* **2.9.10**
    :Python: ``>=3.8``
    :Requires: nothing declared
* **2.9.11 – 2.9.12 (2 releases)**
    :Python: ``>=3.9``
    :Requires: nothing declared

psycopg2
--------
* **2.7 – 2.7.5 (8 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4,3.5,3.6``
    :Requires: nothing declared
* **2.7.6 – 2.7.7 (3 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4,3.5,3.6,3.7``
    :Requires: nothing declared
* **2.8 – 2.8.6 (7 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: nothing declared
* **2.9 – 2.9.8 (9 releases)**
    :Python: ``>=3.6``
    :Requires: nothing declared
* **2.9.9**
    :Python: ``>=3.7``
    :Requires: nothing declared
* **2.9.10**
    :Python: ``>=3.8``
    :Requires: nothing declared
* **2.9.11 – 2.9.12 (2 releases)**
    :Python: ``>=3.9``
    :Requires: nothing declared

psycopg
-------
* **3.1 – 3.1.4 (5 releases)**
    :Python: ``>=3.7``
    :Requires: ``backports.zoneinfo>=0.2.0;python_version<"3.9"; typing-extensions>=4.1;python_version<"3.11"; tzdata;sys_platform=="win32"``
* **3.1.5 – 3.1.20 (16 releases)**
    :Python: ``>=3.7``
    :Requires: ``backports.zoneinfo>=0.2.0;python_version<"3.9"; typing-extensions>=4.1; tzdata;sys_platform=="win32"``
* **3.2.0 – 3.2.1 (2 releases)**
    :Python: ``>=3.8``
    :Requires: ``backports.zoneinfo>=0.2.0;python_version<"3.9"; typing-extensions>=4.4; tzdata;sys_platform=="win32"``
* **3.2.2 – 3.2.13 (12 releases)**
    :Python: ``>=3.8``
    :Requires: ``backports.zoneinfo>=0.2.0;python_version<"3.9"; typing-extensions>=4.6;python_version<"3.13"; tzdata;sys_platform=="win32"``
* **3.3.0 – 3.3.4 (5 releases)**
    :Python: ``>=3.10``
    :Requires: ``typing-extensions>=4.6;python_version<"3.13"; tzdata;sys_platform=="win32"``

pillow
------
* **2.0.0 – 2.4.0 (9 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3``
    :Requires: nothing declared
* **2.5.0 – 3.1.2 (16 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4``
    :Requires: nothing declared
* **3.2.0 – 3.4.2 (8 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4,3.5``
    :Requires: nothing declared
* **4.0.0**
    :Python: ``clf:2.7,3.3,3.4,3.5,3.6``
    :Requires: ``olefile``
* **4.1.0**
    :Python: ``clf:2.7,3.3,3.4,3.5,3.6``
    :Requires: nothing declared
* **4.1.1 – 4.3.0 (4 releases)**
    :Python: ``clf:2.7,3.3,3.4,3.5,3.6``
    :Requires: ``olefile``
* **5.0.0 – 5.4.1 (6 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: nothing declared
* **6.0.0 – 6.2.2 (5 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*``
    :Requires: nothing declared
* **7.0.0 – 7.2.0 (5 releases)**
    :Python: ``>=3.5``
    :Requires: nothing declared
* **8.0.0 – 8.4.0 (10 releases)**
    :Python: ``>=3.6``
    :Requires: nothing declared
* **9.0.0 – 9.5.0 (8 releases)**
    :Python: ``>=3.7``
    :Requires: nothing declared
* **10.0.0 – 10.4.0 (6 releases)**
    :Python: ``>=3.8``
    :Requires: nothing declared
* **11.0.0 – 11.3.0 (4 releases)**
    :Python: ``>=3.9``
    :Requires: nothing declared
* **12.0.0 – 12.3.0 (5 releases)**
    :Python: ``>=3.10``
    :Requires: nothing declared

exifread
--------
* **2.0.0**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4``
    :Requires: nothing declared
* **2.0.1**
    :Python: ``-``
    :Requires: nothing declared
* **2.0.2**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4``
    :Requires: nothing declared
* **2.1.0 – 2.1.2 (3 releases)**
    :Python: ``-``
    :Requires: nothing declared
* **2.2.0 – 2.2.1 (2 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6,3.7``
    :Requires: nothing declared
* **2.3.0 – 2.3.2 (3 releases)**
    :Python: ``clf:2.7,3.5,3.6,3.7,3.8``
    :Requires: nothing declared
* **3.0.0**
    :Python: ``clf:3.5,3.6,3.7,3.8``
    :Requires: nothing declared
* **3.1.0 – 3.5.1 (8 releases)**
    :Python: ``>=3.7``
    :Requires: nothing declared

gunicorn
--------
* **0.17.0 – 18.0 (7 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3``
    :Requires: nothing declared
* **19.0.0 – 19.6.0 (14 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4``
    :Requires: nothing declared
* **19.7.0 – 19.7.1 (2 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4,3.5,3.6``
    :Requires: nothing declared
* **19.8.0 – 19.10.0 (4 releases)**
    :Python: ``>=2.6,!=3.0.*,!=3.1.*``
    :Requires: nothing declared
* **20.0.0 – 20.0.4 (5 releases)**
    :Python: ``>=3.4``
    :Requires: ``setuptools>=3.0``
* **20.1.0**
    :Python: ``>=3.5``
    :Requires: nothing declared
* **21.0.0 – 21.2.0 (4 releases)**
    :Python: ``>=3.5``
    :Requires: ``importlib-metadata;python_version<"3.8"; packaging``
* **22.0.0 – 23.0.0 (2 releases)**
    :Python: ``>=3.7``
    :Requires: ``importlib-metadata;python_version<"3.8"; packaging``
* **24.0.0 – 26.0.0 (11 releases)**
    :Python: ``>=3.10``
    :Requires: ``packaging``

six
---
No longer a runtime requirement: ``six==1.11.0`` was in
``requirements/production.txt``, and Stage 0 of the upgrade plan moved it to
``requirements/dev.txt`` along with ``django-extensions``, the only
distribution in the installed set that declares it (``six>=1.2``) or imports
it. The pin and the version are unchanged; only the file it lives in is.

* **1.9.0 – 1.11.0 (3 releases)**
    :Python: ``-``
    :Requires: nothing declared
* **1.12.0 – 1.13.0 (2 releases)**
    :Python: ``>=2.6,!=3.0.*,!=3.1.*``
    :Requires: nothing declared
* **1.14.0 – 1.16.0 (3 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*``
    :Requires: nothing declared
* **1.17.0**
    :Python: ``!=3.0.*,!=3.1.*,!=3.2.*,>=2.7``
    :Requires: nothing declared

pytz
----
* **2015.2 – 2017.2 (13 releases)**
    :Python: ``-``
    :Requires: nothing declared
* **2017.3 – 2020.1 (11 releases)**
    :Python: ``clf:2.4,2.5,2.6,2.7,3.0,3.1,3.2,3.3,3.4,3.5,3.6``
    :Requires: nothing declared
* **2020.4**
    :Python: ``clf:2.4,2.5,2.6,2.7,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8``
    :Requires: nothing declared
* **2020.5 – 2021.3 (3 releases)**
    :Python: ``clf:2.4,2.5,2.6,2.7,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9``
    :Requires: nothing declared
* **2022.1 – 2022.5 (5 releases)**
    :Python: ``clf:2.4,2.5,2.6,2.7,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,3.10``
    :Requires: nothing declared
* **2022.6 – 2023.3 (5 releases)**
    :Python: ``clf:2.4,2.5,2.6,2.7,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,3.10,3.11``
    :Requires: nothing declared
* **2023.4 – 2024.1 (2 releases)**
    :Python: ``clf:2.4,2.5,2.6,2.7,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,3.10,3.11,3.12``
    :Requires: nothing declared
* **2024.2 – 2026.3 (6 releases)**
    :Python: ``clf:2.4,2.5,2.6,2.7,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,3.10,3.11,3.12,3.13``
    :Requires: nothing declared

sqlparse
--------
* **0.2.0 – 0.2.2 (3 releases)**
    :Python: ``clf:2.7,3.3,3.4,3.5``
    :Requires: nothing declared
* **0.2.3 – 0.2.4 (2 releases)**
    :Python: ``clf:2.7,3.3,3.4,3.5,3.6``
    :Requires: nothing declared
* **0.3.0 – 0.3.1 (2 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: nothing declared
* **0.4.0 – 0.4.4 (5 releases)**
    :Python: ``>=3.5``
    :Requires: nothing declared
* **0.5.0 – 0.5.5 (6 releases)**
    :Python: ``>=3.8``
    :Requires: nothing declared

asgiref
-------
* **2.0.0 – 2.1.1 (4 releases)**
    :Python: ``-``
    :Requires: nothing declared
* **2.1.2 – 2.1.6 (5 releases)**
    :Python: ``-``
    :Requires: ``async-timeout~=2.0``
* **2.2.0 – 2.3.0 (2 releases)**
    :Python: ``clf:3.5,3.6``
    :Requires: ``async-timeout~=2.0``
* **2.3.1**
    :Python: ``clf:3.5,3.6``
    :Requires: ``async-timeout~=3.0``
* **2.3.2**
    :Python: ``clf:3.5,3.6``
    :Requires: ``async-timeout<4.0,>=2.0``
* **3.0.0 – 3.1.2 (4 releases)**
    :Python: ``clf:3.5,3.6,3.7``
    :Requires: ``async-timeout<4.0,>=2.0``
* **3.1.3 – 3.2.2 (5 releases)**
    :Python: ``clf:3.5,3.6,3.7``
    :Requires: nothing declared
* **3.2.3**
    :Python: ``clf:3.5,3.6,3.7,3.8``
    :Requires: nothing declared
* **3.2.4 – 3.3.1 (9 releases)**
    :Python: ``>=3.5``
    :Requires: nothing declared
* **3.3.2 – 3.4.1 (5 releases)**
    :Python: ``>=3.6``
    :Requires: ``typing-extensions;python_version<"3.8"``
* **3.5.0 – 3.6.0 (4 releases)**
    :Python: ``>=3.7``
    :Requires: ``typing-extensions;python_version<"3.8"``
* **3.7.0**
    :Python: ``>=3.7``
    :Requires: ``typing-extensions;python_version<"3.11"``
* **3.7.1 – 3.7.2 (2 releases)**
    :Python: ``>=3.7``
    :Requires: ``typing-extensions>=4;python_version<"3.11"``
* **3.8.0 – 3.8.1 (2 releases)**
    :Python: ``>=3.8``
    :Requires: ``typing-extensions>=4;python_version<"3.11"``
* **3.9.0 – 3.11.1 (6 releases)**
    :Python: ``>=3.9``
    :Requires: ``typing_extensions>=4;python_version<"3.11"``
* **3.12.0 – 3.12.1 (2 releases)**
    :Python: ``>=3.10``
    :Requires: ``typing_extensions>=4;python_version<"3.11"``

django-extensions
-----------------
No longer a runtime requirement either: ``django-extensions==1.5.9`` was in
both ``requirements/production.txt`` and ``requirements/dev.txt``, and Stage 0
of the upgrade plan left it in the second alone -- it is ``runserver_plus`` and
``shell_plus``, nothing in this repository imports it, and
``ylaneenkasvit/local_settings.development.py`` rather than
``common_settings.py`` is now what puts it into ``INSTALLED_APPS``. The
versions below still matter: the upgrade ladder in ``upgrade-plan.rst`` Part 2
moves this package at almost every stage, development-only or not.

Note what the PyPI metadata below does **not** say. 1.5.9 is in the
"1.5.0 – 1.6.7" band, whose ``:Requires:`` reads "nothing declared" -- but the
``dist-info`` of the *built* package in the image declares ``six>=1.2``, and 22
of its modules import it. Where a release predates reliable metadata, the
built distribution is the primary source, not this table.

* **1.5.0 – 1.6.7 (16 releases)**
    :Python: ``-``
    :Requires: nothing declared
* **1.7.0 – 1.7.4 (5 releases)**
    :Python: ``-``
    :Django: 1.8,1.9
    :Requires: nothing declared
* **1.7.5 – 1.9.1 (9 releases)**
    :Python: ``-``
    :Django: 1.8,1.9,1.10
    :Requires: ``six>=1.2``
* **1.9.3 – 1.9.6 (2 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Django: 1.8,1.9,1.10
    :Requires: ``six>=1.2``
* **1.9.7 – 1.9.8 (2 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Django: 1.8,1.9,1.10
    :Requires: ``six>=1.2; typing``
* **1.9.9 – 2.0.0 (2 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Django: 1.8,1.11,2.0
    :Requires: ``six>=1.2; typing``
* **2.0.2 – 2.0.3 (2 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Django: 1.8,1.11,2.0
    :Requires: ``six>=1.2``
* **2.0.5**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Django: 1.8,1.11,2.0
    :Requires: ``six>=1.2; typing;python_version<'3.5'``
* **2.0.6 – 2.1.0 (4 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Django: 1.8,1.11,2.0
    :Requires: ``six>=1.2; typing;python_version<"3.5"``
* **2.1.1 – 2.2.4 (12 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6,3.7``
    :Django: 1.11,2.0,2.1
    :Requires: ``six>=1.2; typing;python_version<"3.5"``
* **2.2.5**
    :Python: ``clf:2.7,3.5,3.6,3.7,3.8``
    :Django: 1.11,2.1,2.2
    :Requires: ``six>=1.2; typing;python_version<"3.5"``
* **2.2.6 – 3.0.0 (5 releases)**
    :Python: ``clf:2.7,3.5,3.6,3.7,3.8``
    :Django: 1.11,2.1,2.2,3.0
    :Requires: ``six>=1.2; typing;python_version<"3.5"``
* **3.0.1 – 3.0.3 (3 releases)**
    :Python: ``>=3.5``
    :Django: 2.2,3.0
    :Requires: ``six>=1.2; typing;python_version<"3.5"``
* **3.0.4 – 3.0.8 (5 releases)**
    :Python: ``>=3.5``
    :Django: 2.2,3.0,3.1
    :Requires: ``typing;python_version<"3.5"``
* **3.0.9 – 3.1.0 (2 releases)**
    :Python: ``>=3.5``
    :Django: 2.2,3.0,3.1
    :Requires: nothing declared
* **3.1.1**
    :Python: ``>=3.6``
    :Django: 2.2,3.0,3.1
    :Requires: nothing declared
* **3.1.2**
    :Python: ``>=3.6``
    :Django: 2.2,3.0,3.1
    :Requires: ``Django>=2.2``
* **3.1.3 – 3.1.5 (3 releases)**
    :Python: ``>=3.6``
    :Django: 2.2,3.0,3.1,3.2
    :Requires: ``Django>=2.2``
* **3.2.0**
    :Python: ``>=3.6``
    :Django: 3.2,4.0
    :Requires: ``Django>=3.2``
* **3.2.1**
    :Python: ``>=3.6``
    :Django: 3.2,4.0,4.1
    :Requires: ``Django>=3.2``
* **3.2.3**
    :Python: ``>=3.6``
    :Django: 3.2,4.0,4.1,4.2
    :Requires: ``Django>=3.2``
* **4.0 – 4.1 (2 releases)**
    :Python: ``>=3.9``
    :Django: 4.2,5.1,5.2
    :Requires: ``django>=4.2``

south
-----
* **0.7 – 0.7.6 (7 releases)**
    :Python: ``-``
    :Requires: nothing declared
* **0.8 – 1.0.2 (8 releases)**
    :Python: ``clf:2.6,2.7,3.3``
    :Requires: nothing declared

django-indexer
--------------
* **0.1 – 0.3.0 (5 releases)**
    :Python: ``-``
    :Requires: nothing declared

django-paging
-------------
* **0.1 – 0.2.5 (8 releases)**
    :Python: ``-``
    :Requires: nothing declared


Test and development dependencies
=================================

pytest
------
* **3.0.0 – 3.0.5 (6 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5``
    :Requires: nothing declared
* **3.0.6**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5``
    :Requires: ``argparse;python_version=="2.6"; colorama;sys_platform=="win32"; py>=1.4.29; setuptools``
* **3.0.7 – 3.1.0 (2 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5,3.6``
    :Requires: nothing declared
* **3.1.1**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5,3.6``
    :Requires: ``argparse;python_version=="2.6"; colorama;sys_platform=="win32"; py>=1.4.29; setuptools``
* **3.1.2**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5,3.6``
    :Requires: ``argparse;python_version=="2.6"; colorama;sys_platform=="win32"; py>=1.4.33; setuptools``
* **3.1.3**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5,3.6``
    :Requires: nothing declared
* **3.2.0 – 3.2.2 (3 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5,3.6``
    :Requires: ``argparse;python_version=="2.6"; colorama;sys_platform=="win32"; ordereddict;python_version=="2.6"; py>=1.4.33; setuptools``
* **3.2.3 – 3.2.5 (3 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5,3.6``
    :Requires: nothing declared
* **3.3.0 – 3.3.1 (2 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: nothing declared
* **3.3.2 – 3.4.2 (4 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``attrs>=17.2.0; colorama;sys_platform=="win32"; funcsigs;python_version<"3.0"; pluggy<0.7,>=0.5; py>=1.5.0; setuptools; six>=1.10.0``
* **3.5.0 – 3.5.1 (2 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``attrs>=17.4.0; colorama;sys_platform=="win32"; funcsigs;python_version<"3.0"; more-itertools>=4.0.0; pluggy<0.7,>=0.5; py>=1.5.0; setuptools; six>=1.10.0``
* **3.6.0 – 3.6.3 (4 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``atomicwrites>=1.0; attrs>=17.4.0; colorama;sys_platform=="win32"; funcsigs;python_version<"3.0"; more-itertools>=4.0.0; pluggy<0.7,>=0.5; py>=1.5.0; setuptools; six>=1.10.0``
* **3.6.4**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``atomicwrites>=1.0; attrs>=17.4.0; colorama;sys_platform=="win32"; funcsigs;python_version<"3.0"; more-itertools>=4.0.0; pluggy<0.8,>=0.5; py>=1.5.0; setuptools; six>=1.10.0``
* **3.7.0**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``atomicwrites>=1.0; attrs>=17.4.0; colorama;sys_platform=="win32"; funcsigs;python_version<"3.0"; more-itertools>=4.0.0; pathlib2;python_version<"3.6"; pluggy>=0.7; py>=1.5.0; setuptools; six>=1.10.0``
* **3.7.1 – 4.2.0 (18 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``atomicwrites>=1.0; attrs>=17.4.0; colorama;sys_platform=="win32"; funcsigs;python_version<"3.0"; more-itertools>=4.0.0; pathlib2>=2.2.0;python_version<"3.6"; pluggy>=0.7; py>=1.5.0; setuptools; six>=1.10.0``
* **4.2.1 – 4.3.1 (3 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``atomicwrites>=1.0; attrs>=17.4.0; colorama;sys_platform=="win32"; funcsigs;python_version<"3.0"; more-itertools<6.0.0,>=4.0.0;python_version<="2.7"; more-itertools>=4.0.0;python_version>"2.7"; pathlib2>=2.2.0;python_version<"3.6"; pluggy>=0.7; py>=1.5.0; setuptools; six>=1.10.0``
* **4.4.0 – 4.4.1 (2 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``atomicwrites>=1.0; attrs>=17.4.0; colorama;sys_platform=="win32"; funcsigs>=1.0;python_version<"3.0"; more-itertools<6.0.0,>=4.0.0;python_version<="2.7"; more-itertools>=4.0.0;python_version>"2.7"; pathlib2>=2.2.0;python_version<"3.6"; pluggy>=0.9; py>=1.5.0; setuptools; six>=1.10.0``
* **4.4.2**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``atomicwrites>=1.0; attrs>=17.4.0; colorama;sys_platform=="win32"; funcsigs>=1.0;python_version<"3.0"; more-itertools<6.0.0,>=4.0.0;python_version<="2.7"; more-itertools>=4.0.0;python_version>"2.7"; pathlib2>=2.2.0;python_version<"3.6"; pluggy>=0.11; py>=1.5.0; setuptools; six>=1.10.0``
* **4.5.0**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``atomicwrites>=1.0; attrs>=17.4.0; colorama;sys_platform=="win32"; funcsigs>=1.0;python_version<"3.0"; more-itertools<6.0.0,>=4.0.0;python_version<="2.7"; more-itertools>=4.0.0;python_version>"2.7"; pathlib2>=2.2.0;python_version<"3.6"; pluggy!=0.10,<1.0,>=0.9; py>=1.5.0; setuptools; six>=1.10.0; wcwidth``
* **4.6.0 – 4.6.5 (6 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``atomicwrites>=1.0; attrs>=17.4.0; colorama;sys_platform=="win32"; funcsigs>=1.0;python_version<"3.0"; importlib-metadata>=0.12; more-itertools<6.0.0,>=4.0.0;python_version<="2.7"; more-itertools>=4.0.0;python_version>"2.7"; packaging; pathlib2>=2.2.0;python_version<"3.6"; pluggy<1.0,>=0.12; py>=1.5.0; six>=1.10.0; wcwidth``
* **4.6.6 – 4.6.7 (2 releases)**
    :Python: ``!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,>=2.7``
    :Requires: ``atomicwrites>=1.0; attrs>=17.4.0; colorama;sys_platform=="win32"; funcsigs>=1.0;python_version<"3.0"; importlib-metadata>=0.12;python_version<"3.8"; more-itertools<6.0.0,>=4.0.0;python_version<="2.7"; more-itertools>=4.0.0;python_version>"2.7"; packaging; pathlib2>=2.2.0;python_version<"3.6"; pluggy<1.0,>=0.12; py>=1.5.0; six>=1.10.0; wcwidth``
* **4.6.8 – 4.6.11 (4 releases)**
    :Python: ``!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,>=2.7``
    :Requires: ``atomicwrites>=1.0; attrs>=17.4.0; colorama;sys_platform=="win32"andpython_version!="3.4"; colorama<=0.4.1;sys_platform=="win32"andpython_version=="3.4"; funcsigs>=1.0;python_version<"3.0"; importlib-metadata>=0.12;python_version<"3.8"; more-itertools<6.0.0,>=4.0.0;python_version<="2.7"; more-itertools>=4.0.0;python_version>"2.7"; packaging; pathlib2>=2.2.0;python_version<"3.6"; pluggy<1.0,>=0.12; py>=1.5.0; six>=1.10.0; wcwidth``
* **5.0.0 – 5.0.1 (2 releases)**
    :Python: ``>=3.5``
    :Requires: ``atomicwrites>=1.0; attrs>=17.4.0; colorama;sys_platform=="win32"; importlib-metadata>=0.12; more-itertools>=4.0.0; packaging; pathlib2>=2.2.0;python_version<"3.6"; pluggy<1.0,>=0.12; py>=1.5.0; wcwidth``
* **5.1.0 – 5.2.4 (9 releases)**
    :Python: ``>=3.5``
    :Requires: ``atomicwrites>=1.0; attrs>=17.4.0; colorama;sys_platform=="win32"; importlib-metadata>=0.12;python_version<"3.8"; more-itertools>=4.0.0; packaging; pathlib2>=2.2.0;python_version<"3.6"; pluggy<1.0,>=0.12; py>=1.5.0; wcwidth``
* **5.3.0 – 5.4.3 (10 releases)**
    :Python: ``>=3.5``
    :Requires: ``atomicwrites>=1.0;sys_platform=="win32"; attrs>=17.4.0; colorama;sys_platform=="win32"; importlib-metadata>=0.12;python_version<"3.8"; more-itertools>=4.0.0; packaging; pathlib2>=2.2.0;python_version<"3.6"; pluggy<1.0,>=0.12; py>=1.5.0; wcwidth``
* **6.0.0 – 6.0.2 (3 releases)**
    :Python: ``>=3.5``
    :Requires: ``atomicwrites>=1.0;sys_platform=="win32"; attrs>=17.4.0; colorama;sys_platform=="win32"; importlib-metadata>=0.12;python_version<"3.8"; iniconfig; more-itertools>=4.0.0; packaging; pathlib2>=2.2.0;python_version<"3.6"; pluggy<1.0,>=0.12; py>=1.8.2; toml``
* **6.1.0 – 6.1.2 (3 releases)**
    :Python: ``>=3.5``
    :Requires: ``atomicwrites>=1.0;sys_platform=="win32"; attrs>=17.4.0; colorama;sys_platform=="win32"; importlib-metadata>=0.12;python_version<"3.8"; iniconfig; packaging; pathlib2>=2.2.0;python_version<"3.6"; pluggy<1.0,>=0.12; py>=1.8.2; toml``
* **6.2.0 – 6.2.4 (5 releases)**
    :Python: ``>=3.6``
    :Requires: ``atomicwrites>=1.0;sys_platform=="win32"; attrs>=19.2.0; colorama;sys_platform=="win32"; importlib-metadata>=0.12;python_version<"3.8"; iniconfig; packaging; pluggy<1.0.0a1,>=0.12; py>=1.8.2; toml``
* **6.2.5**
    :Python: ``>=3.6``
    :Requires: ``atomicwrites>=1.0;sys_platform=="win32"; attrs>=19.2.0; colorama;sys_platform=="win32"; importlib-metadata>=0.12;python_version<"3.8"; iniconfig; packaging; pluggy<2.0,>=0.12; py>=1.8.2; toml``
* **7.0.0 – 7.0.1 (2 releases)**
    :Python: ``>=3.6``
    :Requires: ``atomicwrites>=1.0;sys_platform=="win32"; attrs>=19.2.0; colorama;sys_platform=="win32"; importlib-metadata>=0.12;python_version<"3.8"; iniconfig; packaging; pluggy<2.0,>=0.12; py>=1.8.2; tomli>=1.0.0``
* **7.1.0 – 7.1.2 (3 releases)**
    :Python: ``>=3.7``
    :Requires: ``atomicwrites>=1.0;sys_platform=="win32"; attrs>=19.2.0; colorama;sys_platform=="win32"; importlib-metadata>=0.12;python_version<"3.8"; iniconfig; packaging; pluggy<2.0,>=0.12; py>=1.8.2; tomli>=1.0.0``
* **7.1.3**
    :Python: ``>=3.7``
    :Requires: ``attrs>=19.2.0; colorama;sys_platform=="win32"; importlib-metadata>=0.12;python_version<"3.8"; iniconfig; packaging; pluggy<2.0,>=0.12; py>=1.8.2; tomli>=1.0.0``
* **7.2.0 – 7.2.2 (3 releases)**
    :Python: ``>=3.7``
    :Requires: ``attrs>=19.2.0; colorama;sys_platform=="win32"; exceptiongroup>=1.0.0rc8;python_version<"3.11"; importlib-metadata>=0.12;python_version<"3.8"; iniconfig; packaging; pluggy<2.0,>=0.12; tomli>=1.0.0;python_version<"3.11"``
* **7.3.0 – 7.4.4 (8 releases)**
    :Python: ``>=3.7``
    :Requires: ``colorama;sys_platform=="win32"; exceptiongroup>=1.0.0rc8;python_version<"3.11"; importlib-metadata>=0.12;python_version<"3.8"; iniconfig; packaging; pluggy<2.0,>=0.12; tomli>=1.0.0;python_version<"3.11"``
* **8.0.0 – 8.0.2 (3 releases)**
    :Python: ``>=3.8``
    :Requires: ``colorama;sys_platform=="win32"; exceptiongroup>=1.0.0rc8;python_version<"3.11"; iniconfig; packaging; pluggy<2.0,>=1.3.0; tomli>=1.0.0;python_version<"3.11"``
* **8.1.0 – 8.1.2 (3 releases)**
    :Python: ``>=3.8``
    :Requires: ``colorama;sys_platform=="win32"; exceptiongroup>=1.0.0rc8;python_version<"3.11"; iniconfig; packaging; pluggy<2.0,>=1.4; tomli>=1;python_version<"3.11"``
* **8.2.0 – 8.2.2 (3 releases)**
    :Python: ``>=3.8``
    :Requires: ``colorama;sys_platform=="win32"; exceptiongroup>=1.0.0rc8;python_version<"3.11"; iniconfig; packaging; pluggy<2.0,>=1.5; tomli>=1;python_version<"3.11"``
* **8.3.0 – 8.3.5 (6 releases)**
    :Python: ``>=3.8``
    :Requires: ``colorama;sys_platform=="win32"; exceptiongroup>=1.0.0rc8;python_version<"3.11"; iniconfig; packaging; pluggy<2,>=1.5; tomli>=1;python_version<"3.11"``
* **8.4.0 – 8.4.2 (3 releases)**
    :Python: ``>=3.9``
    :Requires: ``colorama>=0.4;sys_platform=="win32"; exceptiongroup>=1;python_version<"3.11"; iniconfig>=1; packaging>=20; pluggy<2,>=1.5; pygments>=2.7.2; tomli>=1;python_version<"3.11"``
* **9.0.0 – 9.1.1 (6 releases)**
    :Python: ``>=3.10``
    :Requires: ``colorama>=0.4;sys_platform=="win32"; exceptiongroup>=1;python_version<"3.11"; iniconfig>=1.0.1; packaging>=22; pluggy<2,>=1.5; pygments>=2.7.2; tomli>=1;python_version<"3.11"``

pytest-django
-------------
* **2.9.0 – 2.9.1 (2 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4``
    :Requires: ``pytest>=2.5``
* **3.0.0**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4,3.5``
    :Requires: ``pytest>=2.9``
* **3.1.0 – 3.1.2 (3 releases)**
    :Python: ``clf:2.7,3.2,3.3,3.4,3.5``
    :Requires: ``pytest>=2.9``
* **3.2.1**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Django: 1.8,1.9,1.10,1.11,2.0
    :Requires: ``pytest>=2.9``
* **3.3.0 – 3.3.2 (2 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Django: 1.8,1.9,1.10,1.11,2.0
    :Requires: ``pytest>=3.6``
* **3.3.3**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Django: 1.8,1.9,1.10,1.11,2.0,2.1
    :Requires: ``pytest>=3.6``
* **3.4.1**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Django: 1.8,1.9,1.10,1.11,2.0,2.1
    :Requires: ``pathlib;python_version<"3.4"; pytest>=3.6``
* **3.4.2 – 3.4.5 (4 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Django: 1.8,1.9,1.10,1.11,2.0,2.1
    :Requires: ``pathlib2;python_version<"3.4"; pytest>=3.6``
* **3.4.6**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Django: 1.8,1.9,1.10,1.11,2.0,2.1,2.2
    :Requires: ``pathlib2;python_version<"3.4"; pytest!=4.2.0,>=3.6``
* **3.4.7 – 3.7.0 (6 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Django: 1.8,1.9,1.10,1.11,2.0,2.1,2.2
    :Requires: ``pathlib2;python_version<"3.4"; pytest>=3.6``
* **3.8.0 – 3.9.0 (2 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Django: 1.8,1.9,1.10,1.11,2.0,2.1,2.2,3.0
    :Requires: ``pathlib2;python_version<"3.4"; pytest>=3.6``
* **3.10.0**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Django: 1.8,1.9,1.10,1.11,2.0,2.1,2.2,3.0,3.1
    :Requires: ``pathlib2;python_version<"3.4"; pytest>=3.6``
* **4.0.0 – 4.1.0 (2 releases)**
    :Python: ``>=3.5``
    :Django: 2.2,3.0,3.1
    :Requires: ``pytest>=5.4.0``
* **4.2.0 – 4.4.0 (3 releases)**
    :Python: ``>=3.5``
    :Django: 2.2,3.0,3.1,3.2
    :Requires: ``pytest>=5.4.0``
* **4.5.0 – 4.5.2 (3 releases)**
    :Python: ``>=3.5``
    :Django: 2.2,3.1,3.2,4.0
    :Requires: ``pytest>=5.4.0``
* **4.6.0**
    :Python: ``>=3.8``
    :Django: 3.2,4.1,4.2
    :Requires: ``pytest>=7.0.0``
* **4.7.0 – 4.8.0 (2 releases)**
    :Python: ``>=3.8``
    :Django: 3.2,4.1,4.2,5.0
    :Requires: ``pytest>=7.0.0``
* **4.9.0 – 4.10.0 (2 releases)**
    :Python: ``>=3.8``
    :Django: 4.2,5.0,5.1
    :Requires: ``pytest>=7.0.0``
* **4.11.0 – 4.11.1 (2 releases)**
    :Python: ``>=3.8``
    :Django: 4.2,5.0,5.1,5.2
    :Requires: ``pytest>=7.0.0``
* **4.12.0**
    :Python: ``>=3.10``
    :Django: 4.2,5.1,5.2,6.0
    :Requires: ``pytest>=7.0.0``

coverage
--------
* **4.0 – 4.0.3 (4 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5``
    :Requires: nothing declared
* **4.1 – 4.4.1 (9 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5,3.6``
    :Requires: nothing declared
* **4.4.2**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5,3.6,3.7``
    :Requires: nothing declared
* **4.5 – 4.5.4 (5 releases)**
    :Python: ``>=2.6,!=3.0.*,!=3.1.*,!=3.2.*,<4``
    :Requires: nothing declared
* **5.0 – 5.5 (12 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,<4``
    :Requires: nothing declared
* **6.0 – 6.2 (7 releases)**
    :Python: ``>=3.6``
    :Requires: nothing declared
* **6.3 – 7.2.7 (25 releases)**
    :Python: ``>=3.7``
    :Requires: nothing declared
* **7.3.0 – 7.6.1 (17 releases)**
    :Python: ``>=3.8``
    :Requires: nothing declared
* **7.6.2 – 7.10.7 (27 releases)**
    :Python: ``>=3.9``
    :Requires: nothing declared
* **7.11.0 – 7.15.2 (18 releases)**
    :Python: ``>=3.10``
    :Requires: nothing declared

mock
----
* **1.0.0**
    :Python: ``clf:2.4,2.5,2.6,2.7,3.1,3.2,3.3``
    :Requires: nothing declared
* **1.0.1**
    :Python: ``clf:2.5,2.6,2.7,3.1,3.2,3.3``
    :Requires: nothing declared
* **1.1.0 – 1.1.3 (4 releases)**
    :Python: ``clf:2.7,3.2,3.3,3.4,3.5``
    :Requires: nothing declared
* **1.1.4 – 2.0.0 (4 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4,3.5``
    :Requires: nothing declared
* **3.0.0**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: nothing declared
* **3.0.1**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``six``
* **3.0.2 – 3.0.5 (4 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``funcsigs>=1;python_version<"3.3"; six``
* **4.0.0 – 5.2.0 (9 releases)**
    :Python: ``>=3.6``
    :Requires: nothing declared

pbr
---
* **1.0.0 – 1.10.0 (15 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4``
    :Requires: nothing declared
* **2.0.0 – 3.1.1 (6 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5``
    :Requires: nothing declared
* **4.0.0 – 5.4.0 (19 releases)**
    :Python: ``clf:2.7,3.3,3.4,3.5``
    :Requires: nothing declared
* **5.4.1 – 5.4.5 (5 releases)**
    :Python: ``clf:2.7,3.5,3.6,3.7``
    :Requires: nothing declared
* **5.5.0 – 6.1.0 (12 releases)**
    :Python: ``>=2.6``
    :Requires: nothing declared
* **6.1.1 – 7.0.3 (5 releases)**
    :Python: ``>=2.6``
    :Requires: ``setuptools``

selenium
--------
* **3.0.0 – 3.0.2 (3 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5``
    :Requires: nothing declared
* **3.3.0 – 3.7.0 (11 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5,3.6``
    :Requires: nothing declared
* **3.8.0 – 3.14.0 (8 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: nothing declared
* **3.14.1**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``urllib3``
* **3.141.0**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: nothing declared
* **4.0.0 – 4.1.0 (2 releases)**
    :Python: ``~=3.7``
    :Requires: ``trio-websocket~=0.9; trio~=0.17; urllib3[secure]~=1.26``
* **4.1.1 – 4.4.0 (8 releases)**
    :Python: ``~=3.7``
    :Requires: ``trio-websocket~=0.9; trio~=0.17; urllib3[secure,socks]~=1.26``
* **4.4.1**
    :Python: ``~=3.7``
    :Requires: ``trio-websocket~=0.9; trio~=0.17; urllib3[socks]~=1.26``
* **4.4.2**
    :Python: ``~=3.7``
    :Requires: ``certifi~=2021.10.8; trio-websocket~=0.9; trio~=0.17; urllib3[socks]~=1.26``
* **4.4.3 – 4.7.2 (7 releases)**
    :Python: ``~=3.7``
    :Requires: ``certifi>=2021.10.8; trio-websocket~=0.9; trio~=0.17; urllib3[socks]~=1.26``
* **4.8.0 – 4.9.0 (5 releases)**
    :Python: ``>=3.7``
    :Requires: ``certifi>=2021.10.8; trio-websocket~=0.9; trio~=0.17; urllib3[socks]~=1.26``
* **4.9.1 – 4.11.2 (5 releases)**
    :Python: ``>=3.7``
    :Requires: ``certifi>=2021.10.8; trio-websocket~=0.9; trio~=0.17; urllib3[socks]>=1.26,<3``
* **4.12.0 – 4.17.1 (9 releases)**
    :Python: ``>=3.8``
    :Requires: ``certifi>=2021.10.8; trio-websocket~=0.9; trio~=0.17; urllib3[socks]>=1.26,<3``
* **4.17.2 – 4.18.1 (3 releases)**
    :Python: ``>=3.8``
    :Requires: ``certifi>=2021.10.8; trio-websocket~=0.9; trio~=0.17; typing_extensions>=4.9.0; urllib3[socks]>=1.26,<3``
* **4.19.0 – 4.21.0 (3 releases)**
    :Python: ``>=3.8``
    :Requires: ``certifi>=2021.10.8; trio-websocket~=0.9; trio~=0.17; typing_extensions>=4.9.0; urllib3[socks]<3,>=1.26``
* **4.22.0**
    :Python: ``>=3.8``
    :Requires: ``certifi>=2021.10.8; trio-websocket~=0.9; trio~=0.17; typing_extensions>=4.9.0; urllib3[socks]<3,>=1.26; websocket-client>=1.8.0``
* **4.23.0**
    :Python: ``>=3.8``
    :Requires: ``certifi>=2021.10.8; trio-websocket~=0.9; trio~=0.17; typing_extensions~=4.9.0; urllib3[socks]<3,>=1.26; websocket-client==1.8.0``
* **4.23.1 – 4.27.1 (7 releases)**
    :Python: ``>=3.8``
    :Requires: ``certifi>=2021.10.8; trio-websocket~=0.9; trio~=0.17; typing_extensions~=4.9; urllib3[socks]<3,>=1.26; websocket-client~=1.8``
* **4.28.0 – 4.32.0 (6 releases)**
    :Python: ``>=3.9``
    :Requires: ``certifi>=2021.10.8; trio-websocket~=0.9; trio~=0.17; typing_extensions~=4.9; urllib3[socks]<3,>=1.26; websocket-client~=1.8``
* **4.33.0**
    :Python: ``>=3.9``
    :Requires: ``certifi>=2025.4.26; trio-websocket~=0.12.2; trio~=0.30.0; typing_extensions~=4.13.2; urllib3[socks]~=2.4.0; websocket-client~=1.8.0``
* **4.34.0**
    :Python: ``>=3.9``
    :Requires: ``certifi>=2025.4.26; trio-websocket~=0.12.2; trio~=0.30.0; typing_extensions~=4.14.0; urllib3[socks]~=2.4.0; websocket-client~=1.8.0``
* **4.34.1 – 4.34.2 (2 releases)**
    :Python: ``>=3.9``
    :Requires: ``certifi>=2025.6.15; trio-websocket~=0.12.2; trio~=0.30.0; typing_extensions~=4.14.0; urllib3[socks]~=2.5.0; websocket-client~=1.8.0``
* **4.35.0**
    :Python: ``>=3.9``
    :Requires: ``certifi>=2025.6.15; trio-websocket~=0.12.2; trio~=0.30.0; typing_extensions~=4.14.0; urllib3[socks]<3.0,>=2.5.0; websocket-client~=1.8.0``
* **4.36.0**
    :Python: ``>=3.9``
    :Requires: ``certifi>=2025.6.15; trio-websocket<1.0,>=0.12.2; trio<1.0,>=0.30.0; typing_extensions<5.0,>=4.14.0; urllib3[socks]<3.0,>=2.5.0; websocket-client<2.0,>=1.8.0``
* **4.37.0 – 4.39.0 (3 releases)**
    :Python: ``>=3.10``
    :Requires: ``certifi>=2025.10.5; trio-websocket<1.0,>=0.12.2; trio<1.0,>=0.31.0; typing_extensions<5.0,>=4.15.0; urllib3[socks]<3.0,>=2.5.0; websocket-client<2.0,>=1.8.0``
* **4.40.0**
    :Python: ``>=3.10``
    :Requires: ``certifi>=2026.1.4; trio-typing>=0.10.0; trio-websocket<1.0,>=0.12.2; trio<1.0,>=0.31.0; types-certifi>=2021.10.8.3; types-urllib3>=1.26.25.14; typing_extensions<5.0,>=4.15.0; urllib3[socks]<3.0,>=2.6.3; websocket-client<2.0,>=1.8.0``
* **4.41.0 – 4.43.0 (3 releases)**
    :Python: ``>=3.10``
    :Requires: ``certifi>=2026.1.4; trio-websocket<1.0,>=0.12.2; trio<1.0,>=0.31.0; typing_extensions<5.0,>=4.15.0; urllib3[socks]<3.0,>=2.6.3; websocket-client<2.0,>=1.8.0``
* **4.44.0 – 4.46.0 (3 releases)**
    :Python: ``>=3.10``
    :Requires: ``certifi>=2026.2.25; trio-websocket<1.0,>=0.12.2; trio<1.0,>=0.31.0; typing_extensions<5.0,>=4.15.0; urllib3[socks]<3.0,>=2.6.3; websocket-client<2.0,>=1.8.0``

pytest-selenium
---------------
* **1.0 – 1.1 (2 releases)**
    :Python: ``clf:2.6,2.7``
    :Requires: nothing declared
* **1.2.0**
    :Python: ``clf:2.6,2.7``
    :Requires: ``pytest-html>=1.7; pytest-variables; pytest>=2.7.3; requests; selenium>=2.26.0``
* **1.2.1**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5``
    :Requires: ``pytest-html>=1.7; pytest-variables; pytest>=2.7.3; requests; selenium>=2.26.0``
* **1.3.0 – 1.6.0 (6 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5``
    :Requires: ``pytest-base-url; pytest-html>=1.7; pytest-variables; pytest>=2.7.3; requests; selenium>=2.26.0``
* **1.7.0 – 1.8.0 (2 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5``
    :Requires: ``pytest-base-url; pytest-html>=1.7; pytest-variables; pytest>=2.7.3; requests; selenium>=3.0.0``
* **1.9.0**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5``
    :Requires: ``pytest-base-url; pytest-html>=1.14.0; pytest-variables; pytest>=2.7.3; requests; selenium>=3.0.0``
* **1.9.1**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5``
    :Requires: ``pytest-base-url; pytest-html>=1.14.0; pytest-variables>=1.5.0; pytest>=2.7.3; requests; selenium>=3.0.0``
* **1.10.0**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5,3.6``
    :Requires: ``pytest-base-url; pytest-html>=1.14.0; pytest-variables>=1.5.0; pytest>=2.7.3; requests; selenium>=3.0.0``
* **1.11.0 – 1.13.0 (7 releases)**
    :Python: ``clf:2.7,3.6``
    :Requires: ``pytest-base-url; pytest-html>=1.14.0; pytest-variables>=1.5.0; pytest>=3.0; requests; selenium>=3.0.0``
* **1.14.0 – 1.15.1 (3 releases)**
    :Python: ``clf:2.7,3.6,3.7``
    :Requires: ``pytest-base-url; pytest-html>=1.14.0; pytest-variables>=1.5.0; pytest>=3.0; requests; selenium>=3.0.0``
* **1.16.0 – 1.17.0 (2 releases)**
    :Python: ``clf:2.7,3.6,3.7``
    :Requires: ``pytest-base-url; pytest-html>=1.14.0; pytest-variables>=1.5.0; pytest>=3.6; requests; selenium>=3.0.0``
* **2.0.0 – 2.0.1 (2 releases)**
    :Python: ``>=3.6``
    :Requires: ``pytest-base-url; pytest-html>=1.14.0; pytest-variables>=1.5.0; pytest>=5.0.0; requests; selenium>=3.0.0; tenacity<7,>=6``
* **3.0.0**
    :Python: ``>=3.6.2,<4.0.0``
    :Requires: ``pytest-base-url>=1.4.2,<2.0.0; pytest-html>=1.14.0; pytest-variables>=1.5.0,<2.0.0; pytest>=6.0.0,<7.0.0; requests>=2.26.0,<3.0.0; selenium>=3.0.0,<4.0.0; tenacity>=6.0.0,<7.0.0``
* **4.0.0**
    :Python: ``>=3.7,<4.0``
    :Requires: ``pytest-base-url>=2.0.0,<3.0.0; pytest-html>=2.0.0; pytest-variables>=2.0.0,<3.0.0; pytest>=6.0.0,<7.0.0; requests>=2.26.0,<3.0.0; selenium>=4.0.0,<5.0.0; tenacity>=6.0.0,<7.0.0``
* **4.0.1**
    :Python: ``>=3.7``
    :Requires: ``pytest-base-url>=2.0.0; pytest-html>=2.0.0; pytest-variables>=2.0.0; pytest>=6.0.0; requests>=2.26.0; selenium>=4.0.0; tenacity>=6.0.0``
* **4.0.2**
    :Python: ``>=3.7``
    :Requires: ``pytest-base-url>=2.0.0; pytest-html>=4.0.0; pytest-variables>=2.0.0; pytest>=6.0.0; requests>=2.26.0; selenium>=4.10.0; tenacity>=6.0.0``
* **4.1.0**
    :Python: ``>=3.8``
    :Requires: ``pytest-base-url>=2.0.0; pytest-html>=4.0.0; pytest-variables>=2.0.0; pytest>=6.0.0; requests>=2.26.0; selenium>=4.10.0; tenacity>=6.0.0``

pytest-html
-----------
* **1.0 – 1.3.2 (6 releases)**
    :Python: ``clf:2.6,2.7``
    :Requires: nothing declared
* **1.4 – 1.7 (5 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4``
    :Requires: nothing declared
* **1.8.0 – 1.10.1 (5 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4,3.5``
    :Requires: ``pytest>=2.3``
* **1.11.0 – 1.12.0 (3 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4,3.5``
    :Requires: ``ansi2html>=1.1.1; pytest>=2.3``
* **1.13.0**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4,3.5``
    :Requires: ``pytest>=2.3``
* **1.14.0**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4,3.5``
    :Requires: ``pytest-metadata; pytest>=2.3``
* **1.14.1 – 1.15.0 (3 releases)**
    :Python: ``clf:2.7,3.6``
    :Requires: ``pytest-metadata; pytest>=2.3``
* **1.15.1 – 1.19.0 (7 releases)**
    :Python: ``clf:2.7,3.6``
    :Requires: ``pytest-metadata; pytest>=3.0``
* **1.20.0 – 1.22.1 (5 releases)**
    :Python: ``clf:2.7,3.6,3.7``
    :Requires: ``pytest-metadata; pytest>=3.0``
* **2.0.0 – 2.1.1 (4 releases)**
    :Python: ``>=3.6``
    :Requires: ``pytest-metadata; pytest>=5.0``
* **3.0.0 – 3.1.1 (3 releases)**
    :Python: ``>=3.6``
    :Requires: ``pytest!=6.0.0,>=5.0; pytest-metadata``
* **3.2.0**
    :Python: ``>=3.6``
    :Requires: ``py>=1.8.2; pytest!=6.0.0,>=5.0; pytest-metadata``
* **4.0.0 – 4.1.1 (5 releases)**
    :Python: ``>=3.8``
    :Requires: ``jinja2>=3.0.0; pytest-metadata>=2.0.0; pytest>=7.0.0``
* **4.2.0**
    :Python: ``>=3.9``
    :Requires: ``jinja2>=3; pytest-metadata>=2; pytest>=7``

pytest-metadata
---------------
* **1.0.0 – 1.3.0 (4 releases)**
    :Python: ``clf:2.7,3.6``
    :Requires: nothing declared
* **1.4.0 – 1.7.0 (5 releases)**
    :Python: ``clf:2.7,3.6``
    :Requires: ``pytest>=2.9.0``
* **1.8.0**
    :Python: ``clf:2.7,3.6,3.7``
    :Requires: ``pytest>=2.9.0``
* **1.9.0 – 1.11.0 (3 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*``
    :Requires: ``pytest>=2.9.0``
* **2.0.0**
    :Python: ``>=3.7,<4.0``
    :Requires: ``pytest>=7.1.1,<8.0.0``
* **2.0.1**
    :Python: ``>=3.7.0,<3.11.0``
    :Requires: ``pytest>=3.0.0,<8.0.0``
* **2.0.2 – 2.0.4 (3 releases)**
    :Python: ``>=3.7,<4.0``
    :Requires: ``pytest>=3.0.0,<8.0.0``
* **3.0.0**
    :Python: ``>=3.7``
    :Requires: ``pytest>=7.0.0``
* **3.1.0 – 3.1.1 (2 releases)**
    :Python: ``>=3.8``
    :Requires: ``pytest>=7.0.0``

pytest-variables
----------------
* **1.0 – 1.2 (3 releases)**
    :Python: ``clf:2.6,2.7``
    :Requires: nothing declared
* **1.3 – 1.4 (2 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4,3.5``
    :Requires: ``pytest>=2.4.2``
* **1.5.0 – 1.6.1 (4 releases)**
    :Python: ``clf:2.7,3.6``
    :Requires: ``pytest>=2.4.2``
* **1.7.0**
    :Python: ``clf:2.7,3.6``
    :Requires: nothing declared
* **1.7.1**
    :Python: ``clf:2.7,3.6``
    :Requires: ``pytest>=2.4.2``
* **1.8.0 – 1.9.0 (2 releases)**
    :Python: ``clf:2.7,3.6,3.7``
    :Requires: ``pytest>=2.4.2``
* **2.0.0**
    :Python: ``>=3.7,<4.0``
    :Requires: ``pytest>=3.0.0,<8.0.0``
* **3.0.0**
    :Python: ``>=3.7``
    :Requires: ``pytest>=7.0.0``
* **3.1.0**
    :Python: ``>=3.8``
    :Requires: ``pytest>=7.0.0``

pytest-base-url
---------------
* **1.0.0**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5``
    :Requires: nothing declared
* **1.1.0 – 1.4.0 (4 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5``
    :Requires: ``pytest>=2.7.3; requests``
* **1.4.1 – 1.4.2 (2 releases)**
    :Python: ``clf:2.7,3.6``
    :Requires: ``pytest>=2.7.3; requests>=2.9``
* **2.0.0**
    :Python: ``>=3.7,<4.0``
    :Requires: ``pytest>=3.0.0,<8.0.0; requests>=2.9``
* **2.1.0**
    :Python: ``>=3.8``
    :Requires: ``pytest>=7.0.0; requests>=2.9``

werkzeug
--------
* **0.8 – 0.10.4 (16 releases)**
    :Python: ``-``
    :Requires: nothing declared
* **0.11 – 0.12.2 (19 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5``
    :Requires: nothing declared
* **0.13 – 0.14.1 (3 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5,3.6``
    :Requires: nothing declared
* **0.15.0 – 0.16.1 (9 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: nothing declared
* **1.0.0 – 1.0.1 (2 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*``
    :Requires: nothing declared
* **2.0.0 – 2.0.3 (4 releases)**
    :Python: ``>=3.6``
    :Requires: ``dataclasses;python_version<"3.7"``
* **2.1.0 – 2.1.2 (3 releases)**
    :Python: ``>=3.7``
    :Requires: nothing declared
* **2.2.0 – 2.2.3 (4 releases)**
    :Python: ``>=3.7``
    :Requires: ``MarkupSafe>=2.1.1``
* **2.3.0 – 3.0.6 (16 releases)**
    :Python: ``>=3.8``
    :Requires: ``MarkupSafe>=2.1.1``
* **3.1.0 – 3.1.3 (4 releases)**
    :Python: ``>=3.9``
    :Requires: ``MarkupSafe>=2.1.1``
* **3.1.4 – 3.1.8 (5 releases)**
    :Python: ``>=3.9``
    :Requires: ``markupsafe>=2.1.1``

fabric
------
No longer a requirement: ``Fabric==1.6.0`` was in ``requirements/dev.txt`` for
``fabfile.py``, and issue 032 deleted both. The survey stays, since this
document records what was looked at rather than what is installed, and it is
what the "1.x is Python 2 only" finding in ``upgrade-plan.rst`` rests on.

* **1.6.0 – 1.6.2 (3 releases)**
    :Python: ``clf:2.5,2.6``
    :Requires: nothing declared
* **1.6.4**
    :Python: ``clf:2.5,2.6,2.7``
    :Requires: nothing declared
* **1.7.0**
    :Python: ``clf:2.5,2.6``
    :Requires: nothing declared
* **1.7.1 – 1.7.5 (5 releases)**
    :Python: ``clf:2.5,2.6,2.7``
    :Requires: nothing declared
* **1.8.0**
    :Python: ``clf:2.5,2.6``
    :Requires: nothing declared
* **1.8.1 – 1.10.1 (10 releases)**
    :Python: ``clf:2.5,2.6,2.7``
    :Requires: nothing declared
* **1.10.2**
    :Python: ``clf:2.5,2.6,2.7``
    :Requires: ``paramiko>=1.10``
* **1.10.3 – 1.12.2 (10 releases)**
    :Python: ``clf:2.5,2.6,2.7``
    :Requires: ``paramiko>=1.10,<2.0``
* **1.13.0 – 1.13.2 (3 releases)**
    :Python: ``clf:2.5,2.6,2.7``
    :Requires: ``paramiko>=1.10,<3.0``
* **1.14.0 – 1.14.1 (2 releases)**
    :Python: ``clf:2.5,2.6,2.7``
    :Requires: ``paramiko<3.0,>=1.10``
* **1.15.0**
    :Python: ``clf:2.7,3.4,3.5,3.6,3.7,3.8``
    :Requires: ``paramiko>=2.0,<3.0; six>=1.13.0``
* **2.0.0 – 2.0.4 (5 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``cryptography>=1.1; invoke>=1.0,<2.0; paramiko>=2.4``
* **2.0.5 – 2.1.1 (3 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``cryptography>=1.1; invoke<2.0,>=1.0; paramiko>=2.4``
* **2.1.2**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``cryptography>=1.1; invoke>=1.0,<2.0; paramiko>=2.4``
* **2.1.3 – 2.1.4 (2 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``cryptography>=1.1; invoke<2.0,>=1.0; paramiko>=2.4``
* **2.1.5**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``cryptography>=1.1; invoke>=1.0,<2.0; paramiko>=2.4``
* **2.1.6**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``cryptography>=1.1; invoke<2.0,>=1.0; paramiko>=2.4``
* **2.2.0**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``cryptography>=1.1; invoke<2.0,>=1.1; paramiko>=2.4``
* **2.2.1 – 2.2.2 (2 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``cryptography>=1.1; invoke>=1.1,<2.0; paramiko>=2.4``
* **2.2.3**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``cryptography>=1.1; invoke<2.0,>=1.1; paramiko>=2.4``
* **2.3.0 – 2.4.0 (4 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: ``cryptography>=1.1; invoke>=1.1,<2.0; paramiko>=2.4``
* **2.5.0**
    :Python: ``clf:2.7,3.4,3.5,3.6,3.7``
    :Requires: ``invoke<2.0,>=1.3; paramiko>=2.4``
* **2.6.0 – 2.7.0 (2 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6,3.7``
    :Requires: ``invoke>=1.3,<2.0; paramiko>=2.4; pathlib2``
* **2.7.1**
    :Python: ``clf:2.7,3.4,3.5,3.6,3.7``
    :Requires: ``invoke<2.0,>=1.3; paramiko>=2.4; pathlib2``
* **3.0.0 – 3.0.1 (2 releases)**
    :Python: ``clf:3.6,3.7,3.8,3.9,3.10,3.11``
    :Requires: ``invoke>=2.0; paramiko>=2.4``
* **3.1.0 – 3.2.0 (2 releases)**
    :Python: ``clf:3.6,3.7,3.8,3.9,3.10,3.11``
    :Requires: ``decorator>=5; invoke>=2.0; paramiko>=2.4``
* **3.2.1 – 3.2.2 (2 releases)**
    :Python: ``clf:3.6,3.7,3.8,3.9,3.10,3.11``
    :Requires: ``decorator>=5; deprecated>=1.2; invoke>=2.0; paramiko>=2.4``
* **3.2.3**
    :Python: ``clf:3.6,3.7,3.8,3.9,3.10,3.11``
    :Requires: ``decorator>=5; deprecated>=1.2; invoke<3.0,>=2.0; paramiko>=2.4``

packaging
---------
* **20.0 – 20.4 (5 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``pyparsing>=2.0.2; six``
* **20.5 – 20.9 (5 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``pyparsing>=2.0.2``
* **21.0**
    :Python: ``>=3.6``
    :Requires: ``pyparsing>=2.0.2``
* **21.1 – 21.2 (2 releases)**
    :Python: ``>=3.6``
    :Requires: ``pyparsing<3,>=2.0.2``
* **21.3**
    :Python: ``>=3.6``
    :Requires: ``pyparsing!=3.0.5,>=2.0.2``
* **22.0 – 24.0 (5 releases)**
    :Python: ``>=3.7``
    :Requires: nothing declared
* **24.1 – 26.2 (6 releases)**
    :Python: ``>=3.8``
    :Requires: nothing declared

pluggy
------
* **0.5.0 – 0.5.2 (3 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5,3.6``
    :Requires: nothing declared
* **0.6.0 – 0.9.0 (5 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: nothing declared
* **0.10.0**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``importlib-metadata>=0.9``
* **0.11.0**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: nothing declared
* **0.12.0**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``importlib-metadata>=0.12``
* **0.13.0 – 0.13.1 (2 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: ``importlib-metadata>=0.12;python_version<"3.8"``
* **1.0.0**
    :Python: ``>=3.6``
    :Requires: ``importlib-metadata>=0.12;python_version<"3.8"``
* **1.1.0 – 1.2.0 (2 releases)**
    :Python: ``>=3.7``
    :Requires: ``importlib-metadata>=0.12;python_version<"3.8"``
* **1.3.0 – 1.5.0 (3 releases)**
    :Python: ``>=3.8``
    :Requires: nothing declared
* **1.6.0**
    :Python: ``>=3.9``
    :Requires: nothing declared

py
--
* **1.5.1 – 1.10.0 (11 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: nothing declared
* **1.11.0**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*``
    :Requires: nothing declared

attrs
-----
* **17.1.0 – 17.2.0 (2 releases)**
    :Python: ``clf:2.7,3.4,3.5``
    :Requires: nothing declared
* **17.3.0 – 17.4.0 (2 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6``
    :Requires: nothing declared
* **18.1.0 – 18.2.0 (2 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6,3.7``
    :Requires: nothing declared
* **19.1.0 – 21.1.0 (7 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: nothing declared
* **21.2.0 – 21.4.0 (3 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*``
    :Requires: nothing declared
* **22.1.0**
    :Python: ``>=3.5``
    :Requires: nothing declared
* **22.2.0**
    :Python: ``>=3.6``
    :Requires: nothing declared
* **23.1.0 – 23.2.0 (2 releases)**
    :Python: ``>=3.7``
    :Requires: ``importlib-metadata;python_version<'3.8'``
* **24.1.0 – 24.2.0 (2 releases)**
    :Python: ``>=3.7``
    :Requires: ``importlib-metadata;python_version<"3.8"``
* **24.3.0 – 25.3.0 (4 releases)**
    :Python: ``>=3.8``
    :Requires: nothing declared
* **25.4.0 – 26.1.0 (2 releases)**
    :Python: ``>=3.9``
    :Requires: nothing declared

more-itertools
--------------
* **4.0.0 – 4.1.0 (3 releases)**
    :Python: ``clf:2.7,3.2,3.3,3.4,3.5``
    :Requires: ``six<2.0.0,>=1.0.0``
* **4.2.0 – 4.3.0 (2 releases)**
    :Python: ``clf:2.7,3.2,3.3,3.4,3.5,3.6,3.7``
    :Requires: ``six<2.0.0,>=1.0.0``
* **5.0.0**
    :Python: ``clf:2.7,3.4,3.5,3.6,3.7``
    :Requires: ``six<2.0.0,>=1.0.0``
* **6.0.0 – 7.2.0 (4 releases)**
    :Python: ``>=3.4``
    :Requires: nothing declared
* **8.0.0 – 8.14.0 (17 releases)**
    :Python: ``>=3.5``
    :Requires: nothing declared
* **9.0.0 – 9.1.0 (2 releases)**
    :Python: ``>=3.7``
    :Requires: nothing declared
* **10.0.0 – 10.5.0 (6 releases)**
    :Python: ``>=3.8``
    :Requires: nothing declared
* **10.6.0 – 10.8.0 (3 releases)**
    :Python: ``>=3.9``
    :Requires: nothing declared
* **11.0.0 – 11.1.0 (4 releases)**
    :Python: ``>=3.10``
    :Requires: nothing declared

atomicwrites
------------
* **1.0.0 – 1.1.5 (3 releases)**
    :Python: ``-``
    :Requires: nothing declared
* **1.2.0 – 1.4.0 (4 releases)**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: nothing declared
* **1.4.1**
    :Python: ``clf:2.7,3.4,3.5,3.6,3.7,3.8``
    :Requires: nothing declared

zipp
----
* **0.5.0 – 0.5.2 (3 releases)**
    :Python: ``>=2.7``
    :Requires: nothing declared
* **0.6.0 – 1.0.0 (2 releases)**
    :Python: ``>=2.7``
    :Requires: ``more-itertools``
* **1.1.0 – 1.2.0 (3 releases)**
    :Python: ``>=2.7``
    :Requires: ``contextlib2;python_version<"3.4"``
* **2.0.0 – 2.0.1 (2 releases)**
    :Python: ``>=3.6``
    :Requires: ``more-itertools``
* **2.1.0 – 3.6.0 (15 releases)**
    :Python: ``>=3.6``
    :Requires: nothing declared
* **3.7.0 – 3.15.0 (12 releases)**
    :Python: ``>=3.7``
    :Requires: nothing declared
* **3.16.0 – 3.20.2 (14 releases)**
    :Python: ``>=3.8``
    :Requires: nothing declared
* **3.21.0 – 3.23.1 (4 releases)**
    :Python: ``>=3.9``
    :Requires: nothing declared
* **4.1.0**
    :Python: ``>=3.10``
    :Requires: nothing declared

importlib-metadata
------------------
* **0.12 – 0.17 (6 releases)**
    :Python: ``>=2.7,!=3.0,!=3.1,!=3.2,!=3.3``
    :Requires: ``configparser;python_version<"3"; contextlib2;python_version<"3"; pathlib2;python_version=="3.4.*"orpython_version<"3"; zipp>=0.5``
* **0.18 – 1.0.0 (7 releases)**
    :Python: ``>=2.7,!=3.0,!=3.1,!=3.2,!=3.3``
    :Requires: ``configparser>=3.5;python_version<"3"; contextlib2;python_version<"3"; pathlib2;python_version=="3.4.*"orpython_version<"3"; zipp>=0.5``
* **1.1.0**
    :Python: ``>=2.7,!=3.0,!=3.1,!=3.2,!=3.3,!=3.4``
    :Requires: ``configparser>=3.5;python_version<"3"; contextlib2;python_version<"3"; pathlib2;python_version<"3"; zipp>=0.5``
* **1.1.1**
    :Python: ``!=3.0,!=3.1,!=3.2,!=3.3,!=3.4,>=2.7``
    :Requires: ``configparser>=3.5;python_version<"3"; contextlib2;python_version<"3"; pathlib2;python_version<"3"; zipp>=0.5``
* **1.1.2**
    :Python: ``!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,>=2.7``
    :Requires: ``configparser>=3.5;python_version<"3"; contextlib2;python_version<"3"; pathlib2;python_version<"3"; zipp>=0.5``
* **1.1.3**
    :Python: ``!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,>=2.7``
    :Requires: ``configparser>=3.5;python_version<"3"; contextlib2;python_version<"3"; pathlib2;python_version=="3.4.*"orpython_version<"3"; zipp>=0.5``
* **1.2.0 – 2.1.3 (14 releases)**
    :Python: ``!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,>=2.7``
    :Requires: ``configparser>=3.5;python_version<"3"; contextlib2;python_version<"3"; pathlib2;python_version<"3"; zipp>=0.5``
* **3.0.0 – 3.1.1 (3 releases)**
    :Python: ``>=3.6``
    :Requires: ``zipp>=0.5``
* **3.2.0 – 4.8.3 (35 releases)**
    :Python: ``>=3.6``
    :Requires: ``typing-extensions>=3.6.4;python_version<"3.8"; zipp>=0.5``
* **4.9.0 – 6.7.0 (25 releases)**
    :Python: ``>=3.7``
    :Requires: ``typing-extensions>=3.6.4;python_version<"3.8"; zipp>=0.5``
* **6.8.0 – 8.4.0 (15 releases)**
    :Python: ``>=3.8``
    :Requires: ``typing-extensions>=3.6.4;python_version<"3.8"; zipp>=0.5``
* **8.5.0**
    :Python: ``>=3.8``
    :Requires: ``typing-extensions>=3.6.4;python_version<"3.8"; zipp>=3.20``
* **8.6.0 – 8.7.0 (3 releases)**
    :Python: ``>=3.9``
    :Requires: ``typing-extensions>=3.6.4;python_version<"3.8"; zipp>=3.20``
* **8.7.1**
    :Python: ``>=3.9``
    :Requires: ``zipp>=3.20``
* **8.8.0 – 9.0.0 (3 releases)**
    :Python: ``>=3.10``
    :Requires: ``zipp>=3.20``

typing-extensions
-----------------
* **3.7.2**
    :Python: ``clf:2.7,3.3,3.4,3.5,3.6``
    :Requires: ``typing>=3.6.2``
* **3.7.4**
    :Python: ``clf:2.7,3.4,3.5,3.6,3.7``
    :Requires: ``typing>=3.7.4``
* **3.7.4.1**
    :Python: ``clf:2.7,3.4,3.5,3.6,3.7``
    :Requires: ``typing>=3.7.4;python_version<"3.5"``
* **3.7.4.2 – 3.7.4.3 (2 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6,3.7,3.8,3.9``
    :Requires: ``typing>=3.7.4;python_version<"3.5"``
* **3.10.0.0 – 3.10.0.2 (3 releases)**
    :Python: ``clf:2.7,3.4,3.5,3.6,3.7,3.8,3.9,3.10``
    :Requires: ``typing>=3.7.4;python_version<"3.5"``
* **4.0.0 – 4.1.1 (4 releases)**
    :Python: ``>=3.6``
    :Requires: nothing declared
* **4.2.0 – 4.7.1 (10 releases)**
    :Python: ``>=3.7``
    :Requires: nothing declared
* **4.8.0 – 4.13.2 (10 releases)**
    :Python: ``>=3.8``
    :Requires: nothing declared
* **4.14.0 – 4.16.0 (4 releases)**
    :Python: ``>=3.9``
    :Requires: nothing declared

Python 2 backports and tooling
==============================

These existed in ``requirements/integration-tests.txt`` and
``requirements/dev.txt`` only to keep the Python 2.7 toolchain working. The
first of those two files went with the browser suite in issue 017, so most of
them are already gone; the rest are dropped at Stage 10 of the upgrade plan.
They are listed for completeness, as this inventory found them.

django-pserver
--------------
* **0.2**
    :Python: ``-``
    :Requires: nothing declared

configparser
------------
* **3.5.0 – 3.5.1 (2 releases)**
    :Python: ``clf:2.6,2.7,3.4,3.5``
    :Requires: nothing declared
* **3.5.2**
    :Python: ``clf:2.6,2.7,3.4,3.5``
    :Requires: ``ordereddict;python_version=="2.6"``
* **3.5.3**
    :Python: ``>=2.6``
    :Requires: ``ordereddict;python_version=="2.6"; ordereddict;python_version=="2.6"``
* **3.7.0 – 3.7.1 (2 releases)**
    :Python: ``>=2.6``
    :Requires: ``ordereddict;python_version=="2.6"``
* **3.7.2 – 4.0.2 (6 releases)**
    :Python: ``>=2.6``
    :Requires: nothing declared
* **5.0.0 – 5.2.0 (5 releases)**
    :Python: ``>=3.6``
    :Requires: nothing declared
* **5.3.0**
    :Python: ``>=3.7``
    :Requires: nothing declared
* **6.0.0 – 7.1.0 (5 releases)**
    :Python: ``>=3.8``
    :Requires: nothing declared
* **7.2.0**
    :Python: ``>=3.9``
    :Requires: nothing declared

contextlib2
-----------
* **0.1 – 0.4.0 (5 releases)**
    :Python: ``-``
    :Requires: nothing declared
* **0.5.0 – 0.5.2 (3 releases)**
    :Python: ``clf:2.7,3.4,3.5``
    :Requires: nothing declared
* **0.5.3 – 0.5.5 (3 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5``
    :Requires: nothing declared
* **0.6.0**
    :Python: ``>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*``
    :Requires: nothing declared
* **21.6.0**
    :Python: ``>=3.6``
    :Requires: nothing declared

funcsigs
--------
* **0.1 – 0.4 (4 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3``
    :Requires: nothing declared
* **1.0.0 – 1.0.2 (3 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5``
    :Requires: nothing declared

pathlib2
--------
* **2.0 – 2.1.0 (3 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4``
    :Requires: nothing declared
* **2.2.0 – 2.3.0 (3 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4,3.5,3.6``
    :Requires: nothing declared
* **2.3.2**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5,3.6``
    :Requires: ``scandir;python_version<"3.5"; six``
* **2.3.3 – 2.3.5 (3 releases)**
    :Python: ``clf:2.6,2.7,3.4,3.5,3.6,3.7``
    :Requires: ``scandir;python_version<"3.5"; six``
* **2.3.6**
    :Python: ``clf:2.7,3.5,3.6,3.7,3.8,3.9``
    :Requires: ``scandir;python_version<"3.5"; six``
* **2.3.7**
    :Python: ``clf:2.7,3.5,3.6,3.7,3.8,3.9``
    :Requires: ``scandir;python_version<"3.5"; six; typing;python_version<"3.5"``

scandir
-------
* **0.4 – 1.1 (7 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4``
    :Requires: nothing declared
* **1.2 – 1.4 (3 releases)**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4,3.5``
    :Requires: nothing declared
* **1.5**
    :Python: ``clf:2.6,2.7,3.2,3.3,3.4,3.5,3.6``
    :Requires: nothing declared
* **1.6 – 1.7 (2 releases)**
    :Python: ``clf:2.6,2.7,3.3,3.4,3.5,3.6``
    :Requires: nothing declared
* **1.8 – 1.9.0 (2 releases)**
    :Python: ``clf:2.6,2.7,3.4,3.5,3.6``
    :Requires: nothing declared
* **1.10.0**
    :Python: ``clf:2.7,3.4,3.5,3.6,3.7``
    :Requires: nothing declared

wcwidth
-------
* **0.0.1 – 0.1.4 (6 releases)**
    :Python: ``clf:2.7,3.3,3.4``
    :Requires: nothing declared
* **0.1.5 – 0.1.9 (5 releases)**
    :Python: ``clf:2.7,3.4,3.5``
    :Requires: nothing declared
* **0.2.0**
    :Python: ``clf:2.7,3.5,3.6,3.7,3.8``
    :Requires: ``backports.functools-lru-cache>=1.2.1;python_version<"3.2"``
* **0.2.1**
    :Python: ``clf:2.7,3.5,3.6,3.7,3.8``
    :Requires: nothing declared
* **0.2.2 – 0.2.5 (4 releases)**
    :Python: ``clf:2.7,3.5,3.6,3.7,3.8``
    :Requires: ``backports.functools-lru-cache>=1.2.1;python_version<"3.2"``
* **0.2.6**
    :Python: ``clf:2.7,3.5,3.6,3.7,3.8``
    :Requires: nothing declared
* **0.2.7 – 0.2.13 (7 releases)**
    :Python: ``clf:2.7,3.5,3.6,3.7,3.8,3.9,3.10,3.11,3.12``
    :Requires: ``backports.functools-lru-cache>=1.2.1;python_version<"3.2"``
* **0.2.14**
    :Python: ``>=3.6``
    :Requires: nothing declared
* **0.3.0 – 0.8.2 (15 releases)**
    :Python: ``>=3.8``
    :Requires: nothing declared

podman-compose
--------------
* **0.1.3 – 0.1.5 (3 releases)**
    :Python: ``clf:2.7,3.5,3.6,3.7``
    :Requires: ``pyyaml``
* **0.1.8 – 0.1.9 (2 releases)**
    :Python: ``clf:3.5,3.6,3.7``
    :Requires: ``pyyaml``
* **0.1.10 – 1.0.3 (4 releases)**
    :Python: ``clf:3.5,3.6,3.7``
    :Requires: ``python-dotenv; pyyaml``
* **1.0.6**
    :Python: ``clf:3.5,3.6,3.7,3.8,3.9,3.10``
    :Requires: ``python-dotenv; pyyaml``
* **1.1.0 – 1.2.0 (2 releases)**
    :Python: ``clf:3.7,3.8,3.9,3.10,3.11``
    :Requires: ``python-dotenv; pyyaml``
* **1.3.0 – 1.4.1 (3 releases)**
    :Python: ``clf:3.9,3.10,3.11,3.12,3.13``
    :Requires: ``python-dotenv; pyyaml``
* **1.5.0 – 1.6.0 (2 releases)**
    :Python: ``>=3.9``
    :Requires: ``python-dotenv; pyyaml``


Dependencies with no PyPI presence
==================================

Three requirements were installed from URLs rather than from PyPI, so they have
no version history to inventory. All three have since gone, each with the thing
that wanted it, so nothing under ``requirements/`` now names anything but a
package and a version (issue 031, ``Fixed``):

``django-jqm`` — **gone**
    ``https://github.com/akaihola/django-jqm/archive/1.1.0.2.zip`` — a personal
    fork. Contents: seven templates, two static files, and three near-empty
    modules (``models.py``, ``views.py``, ``__init__.py``). It was not a
    dependency to be upgraded but a copy to be taken, which is what issue 031
    did at Stage 0 of the upgrade plan: six of the templates and both static
    files are in ``jqm/`` in this repository, with the URL, the version and the
    date in ``jqm/README.rst``. It is therefore out of this inventory in the
    strongest sense — it is not a package any resolver ever sees again.

``flax`` — **gone**
    ``git+https://github.com/akaihola/django-flax`` at a pinned commit. It was
    used only by ``fabfile.py`` and superseded by ``ansible/install.yaml``, and
    issue 032 deleted the file and this requirement with it, along with the
    ``Fabric==1.6.0`` pin whose survey is above.

``podman-compose`` — **gone**
    ``https://github.com/containers/podman-compose/archive/devel.zip`` — pinned
    to a moving branch, not a release. Development tooling only: it was there
    for the browser suite's ``docker-compose.yml``, and issue 017 deleted the
    suite and ``requirements/integration-tests.txt`` together.
