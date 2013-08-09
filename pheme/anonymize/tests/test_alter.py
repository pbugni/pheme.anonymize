import datetime
from nose.tools import raises

from pheme.anonymize.alter import ALPHA
from pheme.anonymize.alter import fixed_length_string, fixed_length_digits
from pheme.anonymize.alter import random_date_delta, anon_term
from pheme.anonymize.termcache import delete_term


@raises(ValueError)
def test_too_long_prefix():
    "expect ValueError when prefix len exceeds lenght"
    fixed_length_string(length=10, prefix='longer than 10')


def test_prefix():
    result = fixed_length_string(length=3, prefix='tom')('initial value')
    assert (len(result) == 3)
    assert (result == 'Tom')


def test_string_func():
    "generate a fair number, expect all choices in short, all unique in long"
    short = fixed_length_string(1)
    longer = fixed_length_string(100)

    short_results = {}
    longer_results = {}

    num = 2000
    for i in range(num):
        s = short("input")
        l = longer("input")
        short_results[s] = True
        longer_results[l] = True
    assert(len(short_results) == len(ALPHA))
    assert(len(longer_results) == num)


def test_dotted_func():
    "long list of digits with lots of dots"
    dotted_func = fixed_length_digits(1024, (1, 16))
    result = dotted_func('meaningless input')
    assert(len(result) == 1024)
    assert(result.count('.') > 1024 / 16)


def test_nodot_func():
    "no dots works too"
    nodot_func = fixed_length_digits(1024)
    result = nodot_func('whee')
    assert(len(result) == 1024)
    assert(result.count('.') == 0)


@raises(ValueError)
def test_invalid_pointfrequency():
    fixed_length_digits(1024, (1, 'end'))


def test_date_delta_predictability():
    """call many times expecting unique (random) results"""
    now = datetime.datetime.now()
    results = {}

    num = 500
    ten_years = datetime.timedelta(days=3650)
    for i in range(num):
        datetime_shift = random_date_delta(ten_years)
        x = datetime_shift(now)
        results[x] = True
        # Must remove cached delta to generate new.
        delete_term("date_delta-%s" % ten_years)
    assert(len(results) == num)


def test_date_delta_cache():
    """cached delta should maintain order"""
    datetime_shift = random_date_delta(datetime.timedelta(days=3650))

    now = datetime.datetime.now()
    hour_ago = now - datetime.timedelta(hours=1)
    min_ago = now - datetime.timedelta(minutes=1)

    adjusted_now = datetime_shift(now)
    adjusted_hour_ago = datetime_shift(hour_ago)
    adjusted_min_ago = datetime_shift(min_ago)

    assert(adjusted_min_ago - min_ago == adjusted_hour_ago - hour_ago)
    assert(adjusted_hour_ago + datetime.timedelta(hours=1) ==
           adjusted_now)


@raises(ValueError)
def test_small_delta():
    "should raise as delta isn't big enough"
    random_date_delta(datetime.timedelta(seconds=1000))


def test_cached_term():
    "two calls return same altered result"
    random_f = fixed_length_string(25)
    input = "Bob. G Longbottom"
    first = anon_term(input, random_f)
    second = anon_term(input, random_f)
    assert(first != input)
    assert(first == second)


def test_cached_date():
    "two calls return same altered date"
    random_f = random_date_delta(datetime.timedelta(days=5000))
    input = datetime.datetime.now()
    first = anon_term(input, random_f)
    second = anon_term(input, random_f)
    assert(first != input)
    assert(isinstance(first, datetime.datetime))
    assert(first == second)


def test_datetime_format():
    "confirm format works for random_date_delta"
    formated_date_anon = random_date_delta(datetime.timedelta(days=3650),
                                           format="%Y%m")
    input = "196908"
    result = formated_date_anon(input)
    assert(len(result) == 6)
    assert(int(result) > 197707 and int(result) < 198009)
