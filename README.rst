pheme.util
==========

Public Health EHR Message Engine (PHEME), HL/7 anonymize library.

Series of tools to remove all remaining privacy concerns from HL/7
test messages used in the PHEME name-space packages.

NB - this was designed around the HITSP BIOSURVEILLANCE GUIDE
published in 2008.  Attempts to use this library to anonymize HL/7
messages should certainly include a careful review of the fields
getting attention.  See the `anon_map` in `pheme.anonymize.field_map.py`

License
-------

BSD 3 clause license - See LICENSE
