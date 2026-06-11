"""Buckwalter <-> Arabic conversion."""

from src.buckwalter import AR_TO_BW, BW_TO_AR, arabic_to_bw, bw_to_arabic


def test_known_words():
    assert bw_to_arabic("malak") == "مَلَك"
    assert bw_to_arabic("yawom") == "يَوْم"
    assert bw_to_arabic("EiysaY") == "عِيسَى"
    # combining marks in BW order: shadda (~) precedes the vowel
    assert bw_to_arabic("d~unoyaA") == "دُّنْيَا"
    assert bw_to_arabic("jan~ap") == "جَنَّة"


def test_round_trip():
    for bw in ["d~unoyaA", "$ayoTa`n", "{mora>at", "<insa`n", "say~i}ap", "A^dam"]:
        # ^ (maddah) has no Arabic mapping and passes through unchanged in both directions
        assert arabic_to_bw(bw_to_arabic(bw)) == bw


def test_mapping_is_bijective():
    assert len(BW_TO_AR) == len(AR_TO_BW)


def test_unmapped_chars_pass_through():
    # corpus-specific orthography marks have no Unicode mapping and must survive
    assert bw_to_arabic("A^") == "ا^"
    assert bw_to_arabic("x[y") == "خ[ي"
