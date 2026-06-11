"""Token-level cross-validation of output/occurrences.csv against the canonical Quran text.

TASK.txt names JQuranTree (the corpus project's official Java API, which embeds the Tanzil
Uthmani text) as a cross-validation source. This script:

1. takes every location counted in output/occurrences.csv,
2. reconstructs the full token at that location from the morphology file
   (all segments: prefixes + stem + suffixes),
3. compares its letter skeleton against the letter skeleton of the token JQuranTree
   returns for the same chapter:verse:word.

A match for every location proves the morphology file's word indexing and forms agree
with the canonical Quran text — i.e. every counted occurrence is a real word at a real place.

Run (from repo root):
    git clone --depth 1 https://github.com/dsog/jqurantree /tmp/jqurantree
    cd /tmp/jqurantree && mkdir -p classes \
      && javac -nowarn -d classes $(find src/main/java -name "*.java") \
      && cp -r src/main/resources/* classes/ && cd -
    javac -cp /tmp/jqurantree/classes -d /tmp/jqurantree/classes validation/DumpTokens.java
    uv run python validation/validate_locations.py --prepare
    java -cp /tmp/jqurantree/classes DumpTokens /tmp/qf_locations.csv /tmp/qf_tokens.csv
    uv run python validation/validate_locations.py --compare
"""

import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import pandas as pd

from src.buckwalter import bw_to_arabic

RAW = REPO / "data" / "quranic-corpus-morphology-0.4.txt"
# every location counted anywhere: the 38-word index + the claims-audit index (notebook 04)
OCC_FILES = [REPO / "output" / "occurrences.csv", REPO / "output" / "claims_occurrences.csv"]
LOCATIONS_CSV = Path("/tmp/qf_locations.csv")
TOKENS_CSV = Path("/tmp/qf_tokens.csv")
REPORT = REPO / "validation" / "token_validation_report.txt"

ARABIC_LETTERS = set("ابتثجحخدذرزسشصضطظعغفقكلمنهويىةء")
# Hamza seats normalize to their carrier; the Uthmani dagger alif (U+0670) counts as a full
# alif letter because that is how JQuranTree's orthography model renders it.
SEAT_MAP = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ؤ": "و", "ئ": "ي", "ٰ": "ا"})


def skeleton(arabic: str) -> str:
    """Letters-only skeleton: hamza seats normalized to their carrier letter,
    diacritics and Uthmani orthography marks dropped."""
    s = arabic.translate(SEAT_MAP)
    return "".join(ch for ch in s if ch in ARABIC_LETTERS)


def load_tokens_from_morphology() -> dict[tuple[int, int, int], str]:
    """Reconstruct each token (all segments concatenated) from the raw morphology file."""
    segments: dict[tuple[int, int, int], list[tuple[int, str]]] = defaultdict(list)
    with open(RAW, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 4 or not parts[0].startswith("("):
                continue
            c, v, w, s = (int(x) for x in parts[0].strip("()").split(":"))
            segments[(c, v, w)].append((s, parts[1]))
    return {
        loc: "".join(form for _, form in sorted(segs))
        for loc, segs in segments.items()
    }


def locations_under_test() -> list[tuple[int, int, int]]:
    locs: set[tuple[int, int, int]] = set()
    for path in OCC_FILES:
        occ = pd.read_csv(path)
        locs |= {(int(c), int(v), int(w)) for c, v, w in (loc.split(":") for loc in occ["location"])}
    return sorted(locs)


def prepare() -> None:
    locs = locations_under_test()
    with open(LOCATIONS_CSV, "w") as f:
        for c, v, w in locs:
            f.write(f"{c},{v},{w}\n")
    print(f"Wrote {len(locs)} unique locations to {LOCATIONS_CSV}")


def compare() -> None:
    morph = load_tokens_from_morphology()
    locs = locations_under_test()

    jqt: dict[tuple[int, int, int], str] = {}
    with open(TOKENS_CSV, encoding="utf-8") as f:
        for line in f:
            c, v, w, token = line.rstrip("\n").split(",", 3)
            jqt[(int(c), int(v), int(w))] = token

    matches, mismatches, missing = 0, [], []
    for loc in locs:
        expected = skeleton(bw_to_arabic(morph[loc]))
        actual_raw = jqt.get(loc, "<ABSENT>")
        if actual_raw in ("<MISSING>", "<ABSENT>"):
            missing.append((loc, expected, actual_raw))
            continue
        actual = skeleton(actual_raw)
        if expected == actual:
            matches += 1
        else:
            mismatches.append((loc, expected, actual))

    lines = [
        "Token-level validation: occurrences.csv + claims_occurrences.csv vs JQuranTree (Tanzil Uthmani text)",
        f"locations checked : {len(locs)}",
        f"letter-skeleton match : {matches}",
        f"mismatches : {len(mismatches)}",
        f"missing tokens : {len(missing)}",
    ]
    for tag, rows in (("MISMATCH", mismatches), ("MISSING", missing)):
        for loc, exp, act in rows:
            lines.append(f"{tag} {loc[0]}:{loc[1]}:{loc[2]} morphology={exp!r} jqurantree={act!r}")
    report = "\n".join(lines)
    REPORT.write_text(report + "\n", encoding="utf-8")
    print(report)
    if not mismatches and not missing:
        print("\nAll counted occurrences correspond to real tokens in the canonical text.")


if __name__ == "__main__":
    if "--prepare" in sys.argv:
        prepare()
    elif "--compare" in sys.argv:
        compare()
    else:
        sys.exit("Pass --prepare or --compare (see module docstring).")
