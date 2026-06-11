"""Integration tests: the claims-audit numbers against the full corpus file.

These pin the counts behind the verdicts in notebook 04 / README section 5. The
counting conventions (definite article, pronoun suffix exclusion) mirror the
method definitions in notebooks/04_claims_audit.ipynb.
"""

import pytest

from src.parser import DATA_PATH, load_morphology, load_prefixes, load_pron_suffixes

pytestmark = pytest.mark.skipif(not DATA_PATH.exists(), reason="corpus data file not present")


@pytest.fixture(scope="module")
def df():
    return load_morphology()


@pytest.fixture(scope="module")
def definite():
    return load_prefixes()


@pytest.fixture(scope="module")
def pron_suffixed():
    return load_pron_suffixes()


def singular(df, lem):
    sub = df[df.LEM == lem]
    return sub[sub.NUMBER.isna() | (sub.NUMBER == "S")]


def test_pron_suffix_total(pron_suffixed):
    assert len(pron_suffixed) == 20146


def test_yawm_365_convention(df, pron_suffixed):
    # singular 375; exactly 10 carry a pronoun suffix (yawmu-hum etc.) -> 365
    sg = singular(df, "yawom")
    suffixed = [t for t in zip(sg.chapter, sg.verse, sg.word) if t in pron_suffixed]
    assert len(sg) == 375
    assert len(suffixed) == 10
    assert len(sg) - len(suffixed) == 365


def test_ayyam_yawmayn_30(df):
    sub = df[df.LEM == "yawom"]
    assert int(sub.NUMBER.isin(["D", "P"]).sum()) == 30  # 27 plural + 3 dual


def test_iman_kufr_25_convention(df, pron_suffixed):
    for lem, total in [("<iyma`n", 45), ("kufor", 37)]:
        sub = df[df.LEM == lem]
        unsuffixed = [t for t in zip(sub.chapter, sub.verse, sub.word) if t not in pron_suffixed]
        assert len(sub) == total
        assert len(unsuffixed) == 25


def test_bahr_barr_32_13(df, definite):
    counts = {}
    for lem in ["baHor", "bar~"]:
        sg = singular(df, lem)
        counts[lem] = sum(1 for t in zip(sg.chapter, sg.verse, sg.word) if t in definite)
    assert counts == {"baHor": 32, "bar~": 13}
    # the 13 includes the divine name al-Barr (52:28), not only "land" (12, README 2.3)
    divine = df[(df.LEM == "bar~") & (df.chapter == 52) & (df.verse == 28)]
    assert len(divine) == 1


def test_qul_qalu_332(df):
    q = df[df.LEM == "qaAla"]
    assert int(((q.ASPECT == "IMPV") & (q.PGN == "2MS")).sum()) == 332
    assert int(((q.ASPECT == "PERF") & (q.PGN == "3MP")).sum()) == 332
    assert int((df.form == "qaAlu").sum()) == 332


def test_root_level_equalities(df):
    roots = df.ROOT.value_counts()
    assert roots["nfE"] == roots["fsd"] == 50    # naf' = fasad
    assert roots["jhr"] == roots["Eln"] == 16    # jahr = 'alaniya
    assert roots["lsn"] == roots["wEZ"] == 25    # lisan = maw'iza
    assert roots["swA"] == 167                   # sayyi'at side of C05
    assert roots["SlH"] == 180                   # ... but salihat side is 180
    assert roots["$kr"] == 75 and roots["Swb"] == 77
    assert roots["jzy"] == 118 and roots["gfr"] == 234


def test_hayat_mawt_never_145(df):
    # the flagship 145/145 claim: no examined selection reaches 145 for either side
    assert int((df.LEM == "Hayaw`p").sum()) == 76
    assert int((df.LEM == "mawot").sum()) == 50
    assert int((df.ROOT == "Hyy").sum()) == 184
    assert int((df.ROOT == "mwt").sum()) == 165


def test_rajul_imraa_singular_24(df):
    assert len(singular(df, "rajul")) == 24
    assert len(singular(df, "{mora>at")) == 24


def test_salawat_plural_5(df):
    sub = df[df.LEM == "Salaw`p"]
    assert int((sub.NUMBER == "P").sum()) == 5
    assert len(sub) == 83


def test_sab_samawat_7(df):
    sw = df[df.LEM.isin(["saboE", "saboEap"])][["chapter", "verse", "word"]].values.tolist()
    sky = set(map(tuple, df[df.LEM == "samaA^'"][["chapter", "verse", "word"]].values.tolist()))
    hits = [t for t in sw if (t[0], t[1], t[2] + 1) in sky or (t[0], t[1], t[2] - 1) in sky]
    assert len(hits) == 7


def test_istiadha_root(df):
    ew = df[df.ROOT == "Ew*"]
    assert len(ew) == 17
    assert int(ew.LEM.isin(["Eu*o", ">uEiy*u"]).sum()) == 11  # the subset the 11-claim needs
