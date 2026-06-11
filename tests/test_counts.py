"""Integration tests: audited headline counts against the full corpus file.

These pin the numbers that were independently audited and externally validated
(corpus.quran.com + JQuranTree token check, 2026-06-11). If the data file or the
parser changes behavior, these fail loudly.
"""

import pytest

from src.parser import DATA_PATH, load_morphology

pytestmark = pytest.mark.skipif(not DATA_PATH.exists(), reason="corpus data file not present")


@pytest.fixture(scope="module")
def df():
    return load_morphology()


def test_stem_total(df):
    assert len(df) == 77915


def test_famous_pairs(df):
    lemma = df.LEM.value_counts()
    assert lemma["d~unoyaA"] == 115
    assert lemma["malak"] == 88
    assert lemma["$ayoTa`n"] == 88
    assert lemma["A^dam"] == 25
    assert lemma["EiysaY"] == 25


def test_akhira_gender_split(df):
    ax = df[df.LEM == "A^xir"]
    fem = ax.PGN.str.contains("F", na=False)
    assert len(ax) == 155
    assert int(fem.sum()) == 115        # the hereafter
    assert len(ax) - int(fem.sum()) == 40  # last/latter


def test_bones_corrected_count(df):
    singular = (df.LEM == "EaZom").sum()
    plural = ((df.LEM == "EaZiym") & (df.POS == "N") & (df.NUMBER == "P")).sum()
    assert int(singular) == 2
    assert int(plural) == 13
    assert int(singular + plural) == 15


def test_yawm_number_breakdown(df):
    yawm = df[df.LEM == "yawom"]
    assert len(yawm) == 405
    assert int((~yawm.NUMBER.isin(["D", "P"])).sum()) == 375
    assert int((yawm.NUMBER == "D").sum()) == 3
    assert int((yawm.NUMBER == "P").sum()) == 27


def test_qaala_verb_forms(df):
    qaala = df[(df.LEM == "qaAla") & (df.POS == "V")]
    assert len(qaala) == 1618
    assert int((qaala.ASPECT == "PERF").sum()) == 1004
    assert int((qaala.ASPECT == "IMPF").sum()) == 265
    assert int((qaala.ASPECT == "IMPV").sum()) == 349


def test_root_totals_match_website(df):
    # spot-pins from the full corpus.quran.com cross-validation
    roots = df.ROOT.value_counts()
    assert roots["mlk"] == 206
    assert roots["Axr"] == 250
    assert roots["Amn"] == 879
    assert roots["qwl"] == 1722
