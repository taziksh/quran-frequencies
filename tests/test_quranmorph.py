"""Integration tests: QuranMorph cross-annotation check (notebook 06 / README 5.2).

QuranMorph (Akra, Hammouda & Jarrar 2025, arXiv:2506.18148, CC BY 4.0) is an independent
manual lemmatization of the Quran. These tests pin the alignment and the key correspondence
results.
"""

from pathlib import Path

import pandas as pd
import pytest

from src.parser import DATA_PATH, load_morphology

QM_PATH = Path(__file__).parent.parent / "data" / "quranmorph" / "quran-dataset.csv"

pytestmark = pytest.mark.skipif(
    not (DATA_PATH.exists() and QM_PATH.exists()), reason="corpus data files not present"
)


@pytest.fixture(scope="module")
def df():
    return load_morphology()


@pytest.fixture(scope="module")
def qm():
    return pd.read_csv(QM_PATH)


@pytest.fixture(scope="module")
def qml(qm):
    return qm.set_index(["surah_number", "verse_number", "word_position"]).qabas_lemma


def locs(df, lemma, gender=None, pos=None, number=None):
    sub = df[df.LEM == lemma]
    if gender:
        sub = sub[sub.PGN.str.contains(gender, na=False)]
    if pos:
        sub = sub[sub.POS == pos]
    if number:
        sub = sub[sub.NUMBER == number]
    return list(zip(sub.chapter, sub.verse, sub.word))


def test_word_alignment(df, qm):
    assert len(qm) == 77429
    qm_words = qm.groupby(["surah_number", "verse_number"]).word_position.max()
    qac_words = df.groupby(["chapter", "verse"]).word.max()
    qm_words.index.names = qac_words.index.names = ["c", "v"]
    assert len(qm_words) == 6236
    assert (qm_words == qac_words).all()


def test_headline_agreements(df, qm, qml):
    totals = qm.qabas_lemma.value_counts()
    for qac_lemma, expected in [
        ("yawom", 405), ("raHomap", 114), ("$ayoTa`n", 88), ("<iyma`n", 45),
        ("Salaw`p", 83), ("n~aAs", 241), ("A^dam", 25), ("EiysaY", 25),
    ]:
        mapped = qml.loc[locs(df, qac_lemma)].value_counts()
        assert int(totals[mapped.index].sum()) == expected, qac_lemma


def test_akhira_scheme_dependence(df, qml, qm):
    # QAC's 115 feminine 'hereafter' words map to two QM lemmas (100 + 15); the QM union
    # also covers 'last' (155 total) — no QuranMorph selection yields 115.
    fem = qml.loc[locs(df, "A^xir", gender="F")].value_counts()
    assert sorted(fem.values.tolist(), reverse=True) == [100, 15]
    totals = qm.qabas_lemma.value_counts()
    assert int(totals[fem.index].sum()) == 155


def test_barr_split_corroborated(df, qml):
    # QuranMorph independently splits barr into land (12) and dutiful/righteous (10)
    dist = qml.loc[locs(df, "bar~")].value_counts()
    assert sorted(dist.values.tolist(), reverse=True) == [12, 10]


def test_bones_filing_replicates(df, qml):
    # the 13 plural 'bones' rows sit under the 'great' lemma in QuranMorph too
    bones = qml.loc[locs(df, "EaZiym", pos="N", number="P")]
    assert len(bones) == 13 and bones.nunique() == 1


def test_merges_match_variant_selections(df, qml, qm):
    totals = qm.qabas_lemma.value_counts()
    rajul = qml.loc[locs(df, "rajul")].value_counts()
    assert int(totals[rajul.index].sum()) == 57   # rajul + rijal (notebook 03 lemma+variants)
    shajar = qml.loc[locs(df, "$ajar")].value_counts()
    assert int(totals[shajar.index].sum()) == 26  # both tree lemmas merged
