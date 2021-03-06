from nose.tools import raises

from pheme.anonymize.field_map import (
    FieldMap,
    msg_control_id,
    type_and_magnitude,
    ten_digits_starting_w_1
    )


def test_valid_set():
    fm = FieldMap()
    key = 'EVN-3.1'

    func = lambda(x): x
    fm[key] = func
    assert(key in fm)
    assert(func == fm[key])

def test_type_and_magnitude_int():
    an_int = '80'
    result = int(type_and_magnitude(an_int))
    assert(result > 9 and result < 100)

def test_type_and_magnitude_float():
    a_float = '98.6'
    result = float(type_and_magnitude(a_float))
    assert(result > 9 and result < 100)
    assert(type_and_magnitude(a_float).count('.') == 1)

@raises(ValueError)
def test_invalid_key():
    fm = FieldMap()
    fm['MSH'] = lambda(x): x


def test_segment_access():
    fm = FieldMap()

    fm['PID-7.1'] = '7.1'
    fm['PID-7.4'] = '7.4'

    assert('PID' in fm)
    segment = fm['PID']
    assert(len(segment[7]) == 2)
    assert(segment[7][1] == '7.1' and segment[7][4] == '7.4')


def test_msgcontrolid():
    # 1234567890 3030/12/10 09:08:14 3982")
    input = "1234567890" + "30301210090814" + "3982"
    fixed = msg_control_id("1234567890303012100908143982")
    assert(fixed[-4:] == input[-4:])
    assert(fixed[:10] != input[:10])
    assert(len(fixed) == len(input))


def test_npi():
    # 10 digit NPI was causing integer overflow...
    input = '1234554321'
    result = ten_digits_starting_w_1(input)
    assert(len(input) == len(result))
    assert(input.startswith('1'))
