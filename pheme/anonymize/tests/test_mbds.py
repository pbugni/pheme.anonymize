from tempfile import NamedTemporaryFile
import os

from pheme.anonymize.mbds_hl7 import MBDS_anon, message_at_a_time


# NB - the hl7 library requires batch encoding characters at[3:5] -
# just include {BHS, FHS, MSH} as first segment on any text message


def test_bhs():
    bhs = "BHS|^~\&|batchsendingapp^BSAID^ISO|"\
        "batchsendingfacility^BSFID^ISO|"\
        "batchreceivingapp^BRAID^ISO|"\
        "batchreceivingfacility^BRFID^ISO|20410209150319||||"\
        "batchcontrolid"

    components_to_hide = (
        "batchsendingapp",  # BHS-3.1
        "BSAID",  # BHS-3.2
        "batchsendingfacility",  # BHS-4.1
        "BSFID",  # BHS-4.2
        "batchreceivingapp",  # BHS-5.1
        "BRAID",  # BHS-5.2
        "batchreceivingfacility",  # BHS-6.1
        "BRFID",  # BHS-6.2
        "20410209150319",  # BHS-7.1
        "batchcontrolid",  # BHS-11.1
        )

    # test the test; confirm test string has what we're looking to change
    for component in components_to_hide:
        assert(bhs.find(component) > 0)

    mbds_anon = MBDS_anon(bhs)
    result = mbds_anon.anonymize()

    # confirm all required fields have been anonymized
    for component in components_to_hide:
        assert(result.find(component) == -1)


def test_fhs():
    fhs = "FHS|^~\&|filesendingapp^FSAID^ISO|"\
        "filesendingfacility^FSFID^ISO|filereceivingapp^FRAID^ISO|"\
        "filereceivingfacility^FRFID^ISO|20211209113014||||filecontrolid"

    components_to_hide = (
        "filesendingapp",  # FHS-3.1
        "FSAID",  # FHS-3.2
        "filesendingfacility",  # FHS-4.1
        "FSFID",  # FHS-4.2
        "filereceivingapp",  # FHS-5.1
        "FRAID",  # FHS-5.2
        "filereceivingfacility",  # FHS-6.1
        "FRFID",  # FHS-6.2
        "20211209113014",  # FHS-7.1
        "filecontrolid",  # FHS-11.1
        )

    # test the test; confirm test string has what we're looking to change
    for component in components_to_hide:
        assert(fhs.find(component) > 0)

    mbds_anon = MBDS_anon(fhs)
    result = mbds_anon.anonymize()

    # confirm all required fields have been anonymized
    for component in components_to_hide:
        assert(result.find(component) == -1)


def test_msh():
    msh = "MSH|^~\&|sendingapp^SAID|sendingfacility^SFID^NPI|"\
        "receivingapp^RAID^ISO|receivingfacility^RFID^ISO|"\
        "30301210090814||ADT^A08^ADT_A01|"\
        "1234567890303012100908143982|P|2.5|||||||||Biosurveillance-1.0"
    components_to_hide = (
        "sendingapp",  # MSH-3.1
        "SAID",  # MSH-3.2
        "sendingfacility",  # MSH-4.1
        "SFID",  # MSH-4.2
        "receivingapp",  # MSH-5.1
        "RAID",  # MSH-5.2
        "eceivingfacility",  # MSH-6.1
        "RFID",  # MSH-6.2
        "303012100908",  # MSH-7.1
        "1234567890303012100908143982",  # MSH-10.1
        )

    # test the test; confirm test string has what we're looking to change
    for component in components_to_hide:
        assert(msh.find(component) > 0)

    mbds_anon = MBDS_anon(msh)
    result = mbds_anon.anonymize()

    # confirm all required fields have been anonymized
    for component in components_to_hide:
        assert(result.find(component) == -1)


def test_evn():
    evn = "MSH|^~\&|sendingapp^SAID|sendingfacility^SFID^NPI|"\
        "receivingapp^RAID^ISO|receivingfacility^RFID^ISO|"\
        "30301210090814||ADT^A08^ADT_A01|"\
        "1234567890303012100908143982|P|2.5|||||||||Biosurveillance-1.0"\
        "\rEVN|A01|303012091749|30300706172800||||"\
        "eventfacility^EFID^NPI"
    mbds_anon = MBDS_anon(evn)
    result = mbds_anon.anonymize()
    assert(result.find("303012091749") == -1)
    assert(result.find("30300706172800") == -1)
    assert(result.find("eventfacility") == -1)
    assert(result.find("EFID") == -1)


def test_dg1():
    dg1 = "MSH|^~\&|sendingapp^SAID|sendingfacility^SFID^NPI|"\
        "receivingapp^RAID^ISO|receivingfacility^RFID^ISO|"\
        "30301210090814||ADT^A08^ADT_A01|"\
        "1234567890303012100908143982|P|2.5|||||||||Biosurveillance-1.0"\
        "\rDG1|1||592.0^CALCULUS OF KIDNEY^I9||303012091749"\
        "|A^Admitting^HL70052^A^^L|||||||||1"
    mbds_anon = MBDS_anon(dg1)
    result = mbds_anon.anonymize()
    assert(result.find("303012091749") == -1)


def test_pid():
    pid = "MSH|^~\&|sendingapp^SAID|sendingfacility^SFID^NPI|"\
        "receivingapp^RAID^ISO|receivingfacility^RFID^ISO|"\
        "30301210090814||ADT^A08^ADT_A01|"\
        "1234567890303012100908143982|P|2.5|||||||||Biosurveillance-1.0"\
        "\rPID|1||patientID^^^&assigningID&ISO||\"\"|"\
        "|213005|M||"\
        "1002-5^American Indian or Alaska Native^^6^^L|"\
        "^^^WA^66123|FER-WA||||||account^^^&assigningauthority"

    components_to_hide = (
        "patientID",  # PID-3.1
        "assigningID",  # PID-3.4
        "213005",  # PID-7.1
        "66123",  # PID-11.5
        "account",  # PID-18.1
        "assigningauthority",  # PID-18.4
        )

    # test the test; confirm test string has what we're looking to change
    for component in components_to_hide:
        assert(pid.find(component) > 0)

    mbds_anon = MBDS_anon(pid)
    result = mbds_anon.anonymize()

    # confirm all required fields have been anonymized
    for component in components_to_hide:
        assert(result.find(component) == -1)


def test_pv1():
    pv1 = "MSH|^~\&|sendingapp^SAID|sendingfacility^SFID^NPI|"\
        "receivingapp^RAID^ISO|receivingfacility^RFID^ISO|"\
        "30301210090814||ADT^A08^ADT_A01|"\
        "1234567890303012100908143982|P|2.5|||||||||Biosurveillance-1.0"\
        "\rPV1|1|E^Emergency^HL70004^E^^L|"\
        "^patientroom^bed^patientfacility^status^type^building^floor|"\
        "2^Urgent^UB04FL14^UR^^L|||||||||||||||||||||||||||"\
        "|||||||||||||303002091749|303003091749"

    components_to_hide = (
        "patientroom",  # PV1-3.1
        "patientfacility",  # PV1-3.4
        "building",  # PV1-3.7
        "floor",  # PV1-3.8
        "303002091749",  # PV1-44.1
        "303003091749",  # PV1-45.1
        )

    # test the test; confirm test string has what we're looking to change
    for component in components_to_hide:
        assert(pv1.find(component) > 0)

    mbds_anon = MBDS_anon(pv1)
    result = mbds_anon.anonymize()

    # confirm all required fields have been anonymized
    for component in components_to_hide:
        assert(result.find(component) == -1)


def test_obr():
    obr = "MSH|^~\&|sendingapp^SAID|sendingfacility^SFID^NPI|"\
        "receivingapp^RAID^ISO|receivingfacility^RFID^ISO|"\
        "30301210090814||ADT^A08^ADT_A01|"\
        "1234567890303012100908143982|P|2.5|||||||||Biosurveillance-1.0"\
        "\rOBR|1|placerorderno^placerid^placeruid|"\
        "fillerorderno^fillerid^filleruid|"\
        "610-6^Bacteria identified:Prid:Pt:Body fld:Nom:Aerobic culture"\
        "^LN^CFL^Culture Body Fluid^L||30301210090814|"\
        "303008091215|303008091218||||||303008091310|"\
        "&&&PELVIS&Pelvis&L|||||||303008091322||MB|A"

    components_to_hide = (
        "placerorderno",  # OBR-2.1
        "placerid",  # OBR-2.2
        "placeruid",  # OBR-2.3
        "fillerorderno",  # OBR-3.1
        "fillerid",  # OBR-3.2
        "filleruid",  # OBR-3.3
        "30301210090814",  # OBR-6.1
        "303008091215",  # OBR-7.1
        "303008091218",  # OBR-8.1
        "303008091310",  # OBR-14.1
        "303008091322",  # OBR-22.1
        )

    # test the test; confirm test string has what we're looking to change
    for component in components_to_hide:
        assert(obr.find(component) > 0)

    mbds_anon = MBDS_anon(obr)
    result = mbds_anon.anonymize()

    # confirm all required fields have been anonymized
    for component in components_to_hide:
        assert(result.find(component) == -1)


def test_spm():
    spm = "MSH|^~\&|sendingapp^SAID|sendingfacility^SFID^NPI|"\
        "receivingapp^RAID^ISO|receivingfacility^RFID^ISO|"\
        "30301210090814||ADT^A08^ADT_A01|"\
        "1234567890303012100908143982|P|2.5|||||||||Biosurveillance-1.0"\
        "\rSPM|1|^fillerid||"\
        "309051001^"\
        "Body fluid sample (specimen)^SN^PARFLD^Paracentesis Fluid^L|"\
        "|||||||||||||30301210090814"

    components_to_hide = (
        "fillerid",  # SPM-2.2
        "30301210090814",  # SPM-18
        )

    # test the test; confirm test string has what we're looking to change
    for component in components_to_hide:
        assert(spm.find(component) > 0)

    mbds_anon = MBDS_anon(spm)
    result = mbds_anon.anonymize()

    # confirm all required fields have been anonymized
    for component in components_to_hide:
        assert(result.find(component) == -1)


def test_nte():
    nte = "MSH|^~\&|sendingapp^SAID|sendingfacility^SFID^NPI|"\
        "receivingapp^RAID^ISO|receivingfacility^RFID^ISO|"\
        "30301210090814||ADT^A08^ADT_A01|"\
        "1234567890303012100908143982|P|2.5|||||||||Biosurveillance-1.0"\
        "\rNTE|1||note text"
    mbds_anon = MBDS_anon(nte)
    result = mbds_anon.anonymize()
    assert(result.find("note text") == -1)


def test_obx():
    obx = "MSH|^~\&|sendingapp^SAID|sendingfacility^SFID^NPI|"\
        "receivingapp^RAID^ISO|receivingfacility^RFID^ISO|"\
        "30301210090814||ADT^A08^ADT_A01|"\
        "1234567890303012100908143982|P|2.5|||||||||Biosurveillance-1.0"\
        "\rOBX|4|TX|41852-5^Microorganism or agent identified:"\
        "Prid:Pt:XXX:Nom:^LN^RL^DFA^L|4.1|"\
        "too many dates and addresses||||||F||||^^^labcode^^L"

    mbds_anon = MBDS_anon(obx)
    result = mbds_anon.anonymize()
    assert(result.find("too many dates and addresses") == -1)
    assert(result.find("labcode") == -1)


def test_orc():
    orc = "MSH|^~\&|sendingapp^SAID|sendingfacility^SFID^NPI|"\
        "receivingapp^RAID^ISO|receivingfacility^RFID^ISO|"\
        "30301210090814||ADT^A08^ADT_A01|"\
        "1234567890303012100908143982|P|2.5|||||||||Biosurveillance-1.0"\
        "\rORC|NW|613395|19950914:C00094R||||||199509141051"

    mbds_anon = MBDS_anon(orc)
    result = mbds_anon.anonymize()
    assert(result.find("199509") == -1)


def test_reentrant():
    "same call twice shouldn't return same result"
    msh = "MSH|^~\&|sendingapp^SAID|sendingfacility^SFID^NPI|"\
        "receivingapp^RAID^ISO|receivingfacility^RFID^ISO|"\
        "303012100908||ADT^A08^ADT_A01|"\
        "1234567890303012100908143982|P|2.5|||||||||Biosurveillance-1.0"
    mbds_anon = MBDS_anon(msh)
    result = mbds_anon.anonymize()
    result2 = mbds_anon.anonymize()
    assert(result == result2)


def test_filemessage_generator():
    # nest a multi segment message in the middle of 4 others
    input = ['FHS|^~\&|fhs|components',
             'BHS|^~\&|bhs|components',
             'MSH|^~\&|msh|components',
             'EVN|one|two|three',
             'PID|four|five|six',
             'MSH|^~\&|seven|eight']
    with NamedTemporaryFile(delete=False) as testcontents:
        testcontents.write('\r'.join(input))
    output = []
    try:
        with open(testcontents.name, 'rb') as infile:
            for line in message_at_a_time(infile):
                output.append(line)
        # First two msgs should be identical (minus line term)
        assert(input[0] == output[0].rstrip())
        assert(input[1] == output[1].rstrip())

        # Next three should become one message
        assert('\r'.join(input[2:5]) == ''.join(output[2:3]).rstrip())

        # Last should also be identical
        assert(input[-1:] == output[-1:])
    finally:
        os.remove(testcontents.name)
