import datetime
import re

from pheme.util.config import Config
from pheme.anonymize.alter import fixed_length_digits, fixed_length_string
from pheme.anonymize.alter import random_date_delta, anon_term

"""Map message segments to the anonymize function needed

The anonymize map provides a lookup for any hl7 context, defining the
anon_method to apply to the respective fields.

Top level keys define the segments of interest, pointing to a
dictionary mapping each segment needing attention to a further nested
dict, defining the anon_method to apply to the component.

For example, given the following anon_map:

  anon_map['FHS']= {2: {2: dotted_sequence}}

The method 'dotted_sequence' would be applied to the value in FHS-2.2

NB - we respect HL7s 1 index rather than the default python 0 index.

"""


class FieldMap(dict):
    """Specialized container to map HL/7 segment components to values

    Stores values at leaf nodes for any segment-element.component
    provided.  Access is available at the segment (i.e. 'PID') or
    fully qualified segment-element.component value (i.e. 'PID-3.1').

    HL/7 numbering is obfuscated by segments which include the file
    encoding characters in field 2: "^~\&', as it also counts the
    intial file field separator '|'.  To simplify functioning with the
    python-hl7 libary, the indicies are altered on input for the
    segments 'MSH', 'FHS' and 'BHS'.

    """

    def assert_triplekey(self, key):
        """Parse triple key and raise ValueError if not valid

        For accessing leaves by their tripple key (HL/7
        segment-element.component) this attempt to parse the three
        distinct fields, raising an exception if not found.

        Returned values are corrected for type and the file field
        separator off by one value for segments 'MSH', 'FHS' and
        'BHS'.  Therefore, a key like 'MSH-3.2' will be stored as
        ['MSH'][2][2] to match with the HL/7 specification for
        Sending Application - Universal ID.

        """
        pat = re.compile('^([A-Z]{2}[A-Z0-9])-([\d]+)\.([\d]+)$')
        match = pat.match(key)
        try:
            segment, element, component = match.groups()
            if segment in ('MSH', 'FHS', 'BHS'):
                element = int(element) - 1
            return (segment, int(element), int(component))
        except:
            raise ValueError("Key required to match MSH-3.1 format")

    def segment_key(self, key):
        """see if key is at the segment level

        accessors provide segment or segment-element.component
        access.  this returns the segment key if it matches
        the expected pattern.  see assert_triplekey for the other
        option

        """
        pat = re.compile('^[A-Z]{2}[A-Z0-9]$')  # i.e. 'MSH' or 'PV1"
        match = pat.match(key)
        if match:
            return key
        return None

    def __setitem__(self, key, value):
        """key must match hl7 segment component pattern"""
        segment, element, component = self.assert_triplekey(key)
        if dict.__contains__(self, segment):
            d = dict.__getitem__(self, segment)
            if element in d:
                d[element][component] = value
            else:
                d[element] = {component: value}
        else:
            dict.__setitem__(self, segment, {element: {component: value}})

    def __getitem__(self, key):
        """Lookup entire segment or individual leaf nodes

        If key is of 'MSH-3.1' format, return the assocated value.
        If the key is just the segment, i.e. 'MSH', return the
        assosiated dictonary if found.

        """
        segment = self.segment_key(key)
        if segment:
            return dict.__getitem__(self, segment)

        segment, element, component = self.assert_triplekey(key)
        return dict.__getitem__(self, segment)[element][component]

    def __contains__(self, key):
        """Test for entire segment or individual leaf nodes

        If key is of 'MSH-3.1' format, test for assocated value.
        If the key is just the segment, i.e. 'MSH', test for
        associated dictionary.

        """
        segment = self.segment_key(key)
        if segment:
            return dict.__contains__(self, segment)

        segment, element, component = self.assert_triplekey(key)
        if dict.__contains__(self, segment):
            d = dict.__getitem__(self, segment)
            return element in d and component in d[element]
        return False


config = Config()
days = config.get("anonymize", "dayshift")

"""Define functions with parameters needed to anonymize fields"""
dotted_sequence = fixed_length_digits(30, (1, 7))
short_string = fixed_length_string(10)
site_string = fixed_length_string(12, prefix="Site ")
yyyymm = random_date_delta(datetime.timedelta(days=days), "%Y%m")
ymdhms = random_date_delta(datetime.timedelta(days=days), "%Y%m%d%H%M%S")
two_digits = fixed_length_digits(2)
five_digits = fixed_length_digits(5)
six_digits = fixed_length_digits(6)
ten_digits = fixed_length_digits(10)


def msg_control_id(initial):
    """specialized anon function for message control id

    message control id is a long integer made up from concatination of:
    - source identifier
    - timestamp (YYYYMMDDhhmmss)
    - counter [0000-9999]

    attempt to be consistent with the source identifier and use same
    shift for timestamp

    """
    counter = initial[-4:]
    timestamp = initial[-18:-4]
    source_id = initial[:-18]
    return anon_term(source_id, ten_digits) +\
        anon_term(timestamp, ymdhms) + counter


def facility_subcomponents(initial):
    """specialized anon function for PID-3.4 and 3.6

    Some facility components make use of sub-component separator '&'.
    Handle here as a shortcut to extending the depth of the anon
    engine.

    Take care to check the cache for the first two sub-components as
    they are also stand alone components (i.e. MSH-4.1, MSH-4.2) and
    we'd like to substitute in the same values.

    """
    if initial is None or len(initial) == 0:
        return initial
    parts = initial.split('&')
    if len(parts) < 3:
        return anon_term(initial, dotted_sequence)
    return '&'.join((anon_term(parts[0], site_string),
                     anon_term(parts[1], dotted_sequence),
                     parts[2]))


def zipcode(initial):
    """specialized anon function for zip codes

    keep first three digits, random last two

    """
    if initial is None or len(initial) == 0:
        return initial
    if len(initial) >= 3:
        return initial[:3] + two_digits(initial)
    return five_digits(initial)


def type_and_magnitude(initial):
    """return string matching type and magnitude

    If initial looks like an integer, return string form of integer of
    same magnitude.  Same idea for floating point values.  Otherwise
    return a random short_string.

    """
    if initial is None or len(initial) == 0:
        return initial
    try:
        value = int(initial)
        return anon_term(initial, fixed_length_digits(len(initial)))
    except ValueError:
        try:
            value = float(initial)
            lenb4 = initial.find('.')
            return anon_term(initial, fixed_length_digits(len(initial),
                                                          (lenb4, lenb4+1)))
        except ValueError:
            return short_string(initial)


anon_map = FieldMap()
anon_map['BHS-3.1'] = short_string
anon_map['BHS-3.2'] = dotted_sequence
anon_map['BHS-4.1'] = short_string
anon_map['BHS-4.2'] = dotted_sequence
anon_map['BHS-5.1'] = short_string
anon_map['BHS-5.2'] = dotted_sequence
anon_map['BHS-6.1'] = short_string
anon_map['BHS-6.2'] = dotted_sequence
anon_map['BHS-7.1'] = ymdhms
anon_map['BHS-11.1'] = dotted_sequence

anon_map['FHS-3.1'] = short_string
anon_map['FHS-3.2'] = dotted_sequence
anon_map['FHS-4.1'] = short_string
anon_map['FHS-4.2'] = dotted_sequence
anon_map['FHS-5.1'] = short_string
anon_map['FHS-5.2'] = dotted_sequence
anon_map['FHS-6.1'] = short_string
anon_map['FHS-6.2'] = dotted_sequence
anon_map['FHS-7.1'] = ymdhms
anon_map['FHS-11.1'] = dotted_sequence

anon_map['MSH-3.1'] = ten_digits
anon_map['MSH-3.2'] = dotted_sequence
anon_map['MSH-4.1'] = site_string
anon_map['MSH-4.2'] = ten_digits
anon_map['MSH-5.1'] = short_string
anon_map['MSH-5.2'] = dotted_sequence
anon_map['MSH-6.1'] = short_string
anon_map['MSH-6.2'] = dotted_sequence
anon_map['MSH-7.1'] = ymdhms
anon_map['MSH-10.1'] = dotted_sequence

anon_map['EVN-2.1'] = ymdhms
anon_map['EVN-3.1'] = ymdhms
anon_map['EVN-7.1'] = site_string
anon_map['EVN-7.2'] = ten_digits

anon_map['PID-3.1'] = six_digits
anon_map['PID-3.4'] = facility_subcomponents
anon_map['PID-3.6'] = facility_subcomponents
anon_map['PID-7.1'] = yyyymm
anon_map['PID-11.5'] = zipcode
anon_map['PID-18.1'] = six_digits
anon_map['PID-18.4'] = facility_subcomponents

anon_map['PV1-3.2'] = six_digits
anon_map['PV1-3.4'] = short_string
anon_map['PV1-3.7'] = short_string
anon_map['PV1-3.8'] = two_digits
anon_map['PV1-19.1'] = six_digits
anon_map['PV1-19.4'] = facility_subcomponents
anon_map['PV1-19.6'] = facility_subcomponents
anon_map['PV1-44.1'] = ymdhms
anon_map['PV1-45.1'] = ymdhms

anon_map['DG1-5.1'] = ymdhms

anon_map['OBR-2.1'] = ten_digits
anon_map['OBR-2.2'] = dotted_sequence
anon_map['OBR-2.3'] = dotted_sequence
anon_map['OBR-3.1'] = ten_digits
anon_map['OBR-3.2'] = dotted_sequence
anon_map['OBR-3.3'] = dotted_sequence
anon_map['OBR-6.1'] = ymdhms
anon_map['OBR-7.1'] = ymdhms
anon_map['OBR-8.1'] = ymdhms
anon_map['OBR-14.1'] = ymdhms
anon_map['OBR-22.1'] = ymdhms

anon_map['OBX-5.1'] = type_and_magnitude
anon_map['OBX-14.1'] = ymdhms
anon_map['OBX-15.4'] = short_string

anon_map['ORC-3.1'] = dotted_sequence
anon_map['ORC-9.1'] = ymdhms

anon_map['SPM-2.2'] = dotted_sequence
anon_map['SPM-18.1'] = ymdhms

anon_map['NTE-3.1'] = short_string
