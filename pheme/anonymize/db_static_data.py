"""Anonymize static database data from YAML formatted file

"""
import argparse
import sys
import yaml

from pheme.anonymize.alter import anon_term
from pheme.anonymize.field_map import anon_map
from pheme.longitudinal.static_data import SUPPORTED_DAOS
from pheme.longitudinal.static_data import obj_repr, obj_loader
import pheme.longitudinal.tables as tables


def facility_anon(self):
    from .field_map import short_string, ten_digits_starting_w_1
    from .field_map import five_digits, site_string
    from .alter import fixed_length_string
    
    self.county = anon_term(term=self.county, func=short_string)
    self.npi = int(anon_term(term=self.npi, func=ten_digits_starting_w_1))
    self.zip = str(five_digits(self.zip))  # ignore cached!!
    self.organization_name = anon_term(term=self.organization_name,
                                       func=site_string)
    self.local_code = anon_term(term=self.local_code,
                                func=fixed_length_string(3))

def region_anon(self):
    from .field_map import ten_digits_starting_w_1
    from .alter import fixed_length_string

    self.region_name = anon_term(term=self.region_name,
                                 func=fixed_length_string(4))
    self.dim_facility_pk = int(anon_term(term=self.dim_facility_pk,
                                         func=ten_digits_starting_w_1))


for type in SUPPORTED_DAOS:
    klass = getattr(tables, type)
    yaml.add_representer(klass, obj_repr)
    if type == 'Facility':
        klass.anonymize = facility_anon
    elif type == 'ReportableRegion':
        klass.anonymize = region_anon
    else:
        klass.anonymize = lambda(self): None


def anonymize_file():
    """Entry point to convert yaml db file to anon version

    parameters are read from the command line.  call with '-h' for
    options and documentation

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=file, help="the file to anonymize")
    parser.add_argument("-o", "--output",
                        help="file for output, by default hits stdout")
    args = parser.parse_args()
    if args.output:
        output = open(args.output, 'wb')
    else:
        output = sys.stdout

    yaml.add_constructor(u'!DAO', obj_loader)
    objects = yaml.load(args.file.read())
    for obj in objects:
        obj.anonymize()

    output.write(yaml.dump(objects, default_flow_style=False))
    
    if args.output:
        output.close()
