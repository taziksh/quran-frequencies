"""Buckwalter <-> Arabic conversion."""

from src.buckwalter import AR_TO_BW, BW_TO_AR, arabic_to_bw, bw_to_arabic

# expected strings use \u escapes: combining-mark order matters and is invisible
# in rendered Arabic (BW order: shadda before its vowel)


def test_known_words():
    assert bw_to_arabic("malak") == "مَلَك"          # malak
    assert bw_to_arabic("yawom") == "يَوْم"          # yawm
    assert bw_to_arabic("EiysaY") == "عِيسَى"   # 'iysa
    assert bw_to_arabic("d~unoyaA") == "دُّنْيَا"
    assert bw_to_arabic("jan~ap") == "جَنَّة"


def test_extended_orthography():
    # QAC extended Buckwalter: Uthmani signs map to Arabic combining marks
    assert bw_to_arabic("A^") == "آ"      # alif + maddah above
    assert bw_to_arabic("x[y") == "خۢي"  # small high meem
    assert bw_to_arabic("w,") == "وۥ"      # small waw


def test_round_trip():
    for bw in ["d~unoyaA", "$ayoTa`n", "{mora>at", "<insa`n", "say~i}ap", "A^dam",
               "yusotahoza#u", "ta>omuru^n~iY^", "maj're`haA", "nu!jiY"]:
        assert arabic_to_bw(bw_to_arabic(bw)) == bw


def test_mapping_is_bijective():
    assert len(BW_TO_AR) == len(AR_TO_BW)


def test_corpus_form_inventory_fully_mapped():
    # every character that appears in the corpus FORM column has a mapping,
    # so no ASCII leaks into the published form_arabic columns
    from pathlib import Path

    data = Path(__file__).resolve().parents[1] / "data" / "quranic-corpus-morphology-0.4.txt"
    chars = set()
    for line in data.read_text(encoding="utf-8").splitlines():
        if line.startswith("(") and "\t" in line:
            chars |= set(line.split("\t")[1])
    # the one space is 37:130 (Ilyās written as two words in the Uthmani text)
    assert chars <= set(BW_TO_AR) | {" "}, \
        f"unmapped FORM chars: {sorted(chars - set(BW_TO_AR) - {' '})}"
