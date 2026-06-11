"""Unit tests for the morphology parser, on a 16-line verbatim corpus excerpt."""

from pathlib import Path

import pandas as pd
import pytest

from src.parser import load_morphology, load_prefixes, parse_features, parse_location

FIXTURE = Path(__file__).parent / "fixtures" / "mini_morphology.txt"


def test_parse_location():
    assert parse_location("(2:14:10:1)") == (2, 14, 10, 1)


def test_parse_features_noun():
    feat = parse_features("STEM|POS:N|LEM:{som|ROOT:smw|M|GEN")
    assert feat == {"type": "STEM", "POS": "N", "LEM": "{som", "ROOT": "smw",
                    "GENDER": "M", "CASE": "GEN"}


def test_parse_features_verb():
    feat = parse_features("STEM|POS:V|IMPF|(IV)|LEM:>an*ara|ROOT:n*r|2MS|MOOD:JUS")
    assert feat["ASPECT"] == "IMPF"
    assert feat["FORM"] == "(IV)"
    assert feat["PGN"] == "2MS"
    assert feat["MOOD"] == "JUS"  # MOOD is a key:value field, never confused with PGN


def test_parse_features_participle_and_voice():
    feat = parse_features("STEM|POS:N|PASS|PCPL|LEM:magoDuwb|ROOT:gDb|M|GEN")
    assert feat["VOICE"] == "PASS"
    assert feat["PCPL"] == "Y"


def test_parse_features_bare_plural_flag():
    # demonstratives like >uwla`^}ik carry a bare P (plural) flag
    feat = parse_features("STEM|POS:DEM|LEM:>uwla`^}ik|P")
    assert feat["PGN"] == "P"


@pytest.fixture(scope="module")
def df():
    return load_morphology(FIXTURE)


def test_only_stem_entries_loaded(df):
    # 16 lines in the fixture: 12 STEM + 2 PREFIX + 1 SUFFIX + header
    assert len(df) == 12
    assert (df.raw_features.str.startswith("STEM")).all()


def test_number_extraction(df):
    by_lem = df.set_index("LEM")
    assert by_lem.loc["$ayoTa`n", "NUMBER"] == "P"      # MP -> plural
    assert by_lem.loc["wa`liday", "NUMBER"] == "D"      # MD -> dual
    assert by_lem.loc[">uwla`^}ik", "NUMBER"] == "P"    # bare P -> plural
    assert pd.isna(by_lem.loc["{som", "NUMBER"])        # unmarked -> singular
    assert by_lem.loc["r~aHoma`n", "NUMBER"] == "S"     # MS -> singular


def test_bones_quirk_representable(df):
    # the EiZa`m (bones plural) row must be selectable as LEM=EaZiym & POS=N & NUMBER=P
    bones = df[(df.LEM == "EaZiym") & (df.POS == "N") & (df.NUMBER == "P")]
    assert len(bones) == 1
    assert bones.iloc[0]["form"] == "EiZa`mFA"


def test_verb_aspects(df):
    qaala = df[df.LEM == "qaAla"]
    assert set(qaala.ASPECT) == {"PERF", "IMPV"}


def test_load_prefixes():
    definite = load_prefixes(FIXTURE)
    assert (1, 1, 3) in definite      # {l (Al+) before r~aHoma`ni
    assert (1, 1, 1) not in definite  # bi+ is not the definite article
