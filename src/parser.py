"""Parse the Quranic Arabic Corpus morphology file into a pandas DataFrame."""

import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "quranic-corpus-morphology-0.4.txt"


def parse_features(features_str: str) -> dict[str, str]:
    """Parse a pipe-separated FEATURES string into a dict.

    Example input: 'STEM|POS:V|PERF|PASS|LEM:qaAla|ROOT:qwl|3MS'
    Returns: {'type': 'STEM', 'POS': 'V', 'ASPECT': 'PERF', 'VOICE': 'PASS',
              'LEM': 'qaAla', 'ROOT': 'qwl', 'PGN': '3MS'}
    """
    parts = features_str.split("|")
    result: dict[str, str] = {"type": parts[0]}  # STEM, PREFIX, or SUFFIX

    for part in parts[1:]:
        if ":" in part:
            key, value = part.split(":", 1)
            result[key] = value
        else:
            # Standalone flags: could be PGN (e.g. 3MS), case (NOM/ACC/GEN),
            # gender (M/F), aspect (PERF/IMPF/IMPV), voice (ACT/PASS),
            # verb form like (II), or state (DEF/INDEF), or PCPL, etc.
            if part in ("PERF", "IMPF", "IMPV"):
                result["ASPECT"] = part
            elif part in ("ACT", "PASS"):
                result["VOICE"] = part
            elif part in ("NOM", "ACC", "GEN"):
                result["CASE"] = part
            elif part in ("DEF", "INDEF"):
                result["STATE"] = part
            elif part == "PCPL":
                result["PCPL"] = "Y"
            elif part.startswith("(") and part.endswith(")"):
                result["FORM"] = part  # verb form like (II), (IV), (X)
            elif len(part) <= 3 and part[-1:] in ("S", "D", "P"):
                # Person-gender-number like 3MS, 2FP, MP, FS, etc.
                result["PGN"] = part
            elif part in ("M", "F"):
                result["GENDER"] = part
            else:
                result[part] = "Y"  # catch-all for other flags

    return result


def parse_location(loc_str: str) -> tuple[int, int, int, int]:
    """Parse '(1:2:3:4)' into (chapter, verse, word, segment)."""
    inner = loc_str.strip("()")
    a, b, c, d = inner.split(":")
    return (int(a), int(b), int(c), int(d))


def load_morphology(path: str | Path | None = None) -> pd.DataFrame:
    """Load the morphology file and return a DataFrame of STEM entries.

    Columns: chapter, verse, word, segment, form, tag,
             POS, LEM, ROOT, ASPECT, VOICE, PGN, GENDER, CASE, STATE, FORM_NUM, PCPL,
             raw_features
    """
    path = Path(path) if path else DATA_PATH
    rows = []

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("LOCATION"):
                continue

            parts = line.split("\t")
            if len(parts) != 4:
                continue

            location, form, tag, features_str = parts

            # Only keep STEM entries
            if not features_str.startswith("STEM"):
                continue

            feat = parse_features(features_str)
            loc = parse_location(location)

            rows.append({
                "chapter": loc[0],
                "verse": loc[1],
                "word": loc[2],
                "segment": loc[3],
                "form": form,
                "tag": tag,
                "POS": feat.get("POS"),
                "LEM": feat.get("LEM"),
                "ROOT": feat.get("ROOT"),
                "ASPECT": feat.get("ASPECT"),
                "VOICE": feat.get("VOICE"),
                "PGN": feat.get("PGN"),
                "GENDER": feat.get("GENDER"),
                "CASE": feat.get("CASE"),
                "STATE": feat.get("STATE"),
                "FORM_NUM": feat.get("FORM"),
                "PCPL": feat.get("PCPL"),
                "raw_features": features_str,
            })

    df = pd.DataFrame(rows)

    # Extract number (S/D/P) from PGN column
    def extract_number(pgn) -> str | None:
        if isinstance(pgn, str) and len(pgn) >= 1 and pgn[-1] in ("S", "D", "P"):
            return pgn[-1]
        return None

    df["NUMBER"] = df["PGN"].map(extract_number)

    return df


def load_prefixes(path: str | Path | None = None) -> set[tuple[int, int, int]]:
    """Load the morphology file and return a set of (chapter, verse, word) tuples
    that have a definite article prefix (Al+)."""
    path = Path(path) if path else DATA_PATH
    definite_words: set[tuple[int, int, int]] = set()

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("LOCATION"):
                continue
            parts = line.split("\t")
            if len(parts) != 4:
                continue
            location, form, tag, features_str = parts
            if "PREFIX|Al+" in features_str:
                loc = parse_location(location)
                definite_words.add((loc[0], loc[1], loc[2]))

    return definite_words
