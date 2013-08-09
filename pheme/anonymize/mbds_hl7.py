"""Anonymize MBDS messages in HL7 2.5 format

NB - MBDS (Minimum Biosurveillance Data Set) messages are mostly
scrubbed, this is almost certainly NOT adequate to protect a generic
HL7 2.5 message.

"""
import argparse
import hl7
import sys

from pheme.anonymize.alter import anon_term
from pheme.anonymize.field_map import anon_map


class MBDS_anon(object):

    def __init__(self, msg):
        self.msg = hl7.parse(msg)

    def anonymize(self):
        """apply the anonymize map to the instance message

        returns an anonymized version of the message.

        """
        # preserve idempotence
        if hasattr(self, '_anonymized'):
            return str(unicode(self.msg))

        # apply all anon methods applicable to this message
        for hl7segment in self.msg:
            segment = str(hl7segment[0][0])  # MSH, PID, OBX, etc.
            if segment in anon_map:
                for element in anon_map[segment].keys():  # i.e. EVN-2
                    for component in anon_map[segment][element].keys():
                        anon_method = anon_map[segment][element][component]
                        # adjust hl7 one versus zero index
                        try:
                            cur_val = hl7segment[element][component - 1]
                        except IndexError:
                            # said component not in the hl7segment
                            # safe to ignore and continue
                            continue
                        hl7segment[element][component - 1] =\
                            anon_term(term=cur_val, func=anon_method)
        self._anonymized = True
        return str(unicode(self.msg))


def line_at_a_time(fileobj):
    """Generator to yield a line at a time till exhausted

    :param fileobj: open filelike obj ready to read and yield a line at a time

    """
    buffered = ''

    for input in fileobj.readlines():
        buffered += input
        while buffered.find('\r') > 0:
            line, partition, buffered = buffered.partition('\r')
            yield line

    if len(buffered):
        yield buffered
    raise StopIteration


def anonymize_file():
    """Entry point to convert hl7 batch file to anon version

    parameters are read from the command line.  call with '-h' for
    options and documentation

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=file, help="the file to anonymize")
    parser.add_argument("-o", "--output", type=file,
                        help="file for output, by default hits stdout")
    args = parser.parse_args()
    if args.output:
        output = open(args.output, 'wb')
    else:
        output = sys.stdout
    for nextline in line_at_a_time(args.file):
        parser = MBDS_anon(nextline)
        output.write(parser.anonymize())
        output.write('\r')

    if args.output:
        output.close()
