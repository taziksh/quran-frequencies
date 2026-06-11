"""Integration tests: base-rate statistics behind README section 5.1 / notebook 05."""

import pytest

from src.parser import DATA_PATH, load_morphology

pytestmark = pytest.mark.skipif(not DATA_PATH.exists(), reason="corpus data file not present")


@pytest.fixture(scope="module")
def lemma_counts():
    return load_morphology().LEM.value_counts()


@pytest.fixture(scope="module")
def root_counts():
    return load_morphology().ROOT.value_counts()


def equal_pairs(counts, min_count):
    m = counts[counts >= min_count].value_counts()
    return int(sum(k * (k - 1) // 2 for k in m))


def test_vocabulary_sizes(lemma_counts, root_counts):
    assert len(lemma_counts) == 4832
    assert len(root_counts) == 1642
    assert int((lemma_counts == 1).sum()) == 1994  # hapax lemmas


def test_equal_pair_abundance(lemma_counts, root_counts):
    assert equal_pairs(lemma_counts, 10) == 8594
    assert equal_pairs(root_counts, 10) == 2817


def test_celebrated_value_multiplicity(lemma_counts, root_counts):
    mult = lemma_counts.value_counts()
    assert mult[88] == 4    # malak, shaytan + mathal, fa'ala
    assert mult[25] == 12   # incl. Adam, Isa
    assert mult[115] == 1   # dunya only (akhira's 115 is a gendered slice of A^xir)
    assert mult[114] == 1   # rahma only
    rmult = root_counts.value_counts()
    assert rmult[16] == 14  # jahr/'alaniya are 1 of 91 possible root pairs at 16
    assert rmult[50] == 3   # nfE, fsd + Tyb
