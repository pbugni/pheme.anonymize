import datetime
import random
import string

from pheme.anonymize.termcache import lookup_term, store_term


def fixed_length_string(length, prefix=''):
    """generates function for random string of fixed length

    :param length: the static length of string the returned
      function will produce
    :param prefix: optional prefix for all returned strings

    returns a function to create a string of specified length,
    prefixed if requested.  The first character is capitalized
    regardless of prefix setting.

    """
    if (length < len(prefix)):
        raise ValueError("length of prefix exceeds total string length")

    def fixed_len(initial):
        "returns string of fixed len - initial is ignored"
        assert(initial)  # don't populate non existing field
        result = list(prefix)
        while len(result) < length:
            result.append(random.choice(string.ascii_lowercase))
        return ''.join(result).capitalize()

    return fixed_len


def fixed_length_digits(length, pointfrequency=None):
    """generates function for random string of digits fixed length

    :param length: the static length of string the returned
      function will produce
    :param pointfrequency: touple of ints defining min and max segment
      length before dropping another point '.'

    returns a function to create a string of specified length,
    prefixed if requested.  The first character is capitalized
    regardless of prefix setting.

    """
    if pointfrequency:
        if len(pointfrequency) != 2 or\
            not all(map(lambda(i): isinstance(i, int),
                        pointfrequency)):
            raise ValueError("pointfrequency not two-tuple of ints")
        else:
            pointchoice = range(*pointfrequency)
    else:
        pointchoice = [length]

    def fixed_len(initial):
        "returns string of digits and dots of fixed len"
        assert(initial)  # don't populate non existing field
        result = []
        i = 0
        nextpoint = random.choice(pointchoice)
        while i < length:
            if i == nextpoint:
                result.append('.')
                nextpoint = i + 1 + random.choice(pointchoice)
            else:
                result.append(random.choice(string.digits))
            i += 1
        return ''.join(result)

    return fixed_len


def random_date_delta(delta_ballpark, format=None):
    """generates function to modify a date by some ballpark amount

    :param delta_ballpark: datetime.timedelta to use as ballpark
      shift.  Actual delta randomly generated within 10% of given
      ballpark.  Must be at least 5 years, in either direction, to
      ensure unpredictable shift.
    :param format: optional datetime format string for output.  if
      defined, the input to the generated function is expected to be
      in the same format.

    In order to maintain the strict order of messages, once a delta
    has been calculated for a given delta_ballpark, it guarenteed to
    be reused.  To force a change, provide a different delta_ballpark
    or remove it from the cache.  Look for key values prefixed
    "date_delta".

    returns a function that will modify any given datetime by a fixed
    amount.  enables shifting all datetime fields by the same, yet
    unpredictable amount, to maintain order of events, etc.

    """
    cached_key = "date_delta-%s" % delta_ballpark

    def calculate_delta(ballpark_seconds):
        ballpark_seconds = delta_ballpark.total_seconds()
        if abs(ballpark_seconds) < \
                datetime.timedelta(days=(5 * 365)).total_seconds():
            raise ValueError("insignificant ballpark, increase delta "
                             "magnitude to ensure unpredictable results")
        fudge = .10 * ballpark_seconds
        delta = random.triangular(ballpark_seconds - fudge,
                                  ballpark_seconds + fudge)
        store_term(cached_key, delta)
        return delta

    delta = lookup_term(cached_key)
    if delta is None:
        delta = calculate_delta(delta_ballpark)

    def datetime_shift(initial):
        """returns initial datetime modified by delta

        :param initial: a datetime object to modify, or if format was
          defined when generating this method, a string in said format

        """
        assert(initial)  # don't populate non existing field
        if format:
            try:
                initial = datetime.datetime.strptime(initial, format)
            except ValueError:
                # handly sloppy input when missing time
                if format == '%Y%m%d%H%M%S' and len(initial) == 8:
                    initial = datetime.datetime.strptime(initial, '%Y%m%d')
                else:
                    raise
        result = initial + datetime.timedelta(seconds=delta)
        return result.strftime(format) if format else result

    return datetime_shift


def anon_term(term, func):
    """lookup or anonomize any term, cache and return cached values

    :param term: term, or string, or date or whatever to anonymize
    :param func: callable to produce appropriate random version of term

    Returns the anonymized version of the term.  Multiple calls with the
    same term return the same anonymized result, regardless of func.

    """
    # difficult to tell if object supports len
    try:
        termlen = len(term)
    except TypeError:
        termlen = 1
    if term is None or termlen == 0:
        return term

    cached = lookup_term(term)
    if cached is not None:
        return cached
    else:
        value = func(term)
        store_term(term, value)
        return value
