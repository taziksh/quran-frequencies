# Quran Word Frequency Counter

Count occurrences of Arabic words in the Quran using the **Quranic Arabic Corpus morphology v0.4** — a linguistically tagged dataset of every word in the Quran.

> **Audited 2026-06-11.** All counts were re-derived from scratch, cross-validated against
> corpus.quran.com, and several previously published numbers corrected — see
> `notebooks/03_audit_and_full_recount.ipynb` and the "Audit corrections" section below.

## Data Source

**Quranic Arabic Corpus** (v0.4, 77,915 STEM entries)
- Website: https://corpus.quran.com
- Download: https://corpus.quran.com/download/
- File: `quranic-corpus-morphology-0.4.txt` (tab-separated)
- License: see corpus website for terms

The morphology file provides a full grammatical analysis of every word in the Quran — part of speech, lemma, root, person/gender/number, case, and more — in Buckwalter transliteration.

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
# Clone and install
git clone <this-repo>
cd quran-frequencies
uv sync

# Download data
# 1. Go to https://corpus.quran.com/download/
# 2. Download quranic-corpus-morphology-0.4.zip
# 3. Unzip into data/
unzip ~/Downloads/quranic-corpus-morphology-0.4.zip -d data/

# Run notebooks
uv run jupyter notebook
```

## Project Structure

```
quran-frequencies/
  data/                     # Morphology file (not committed)
  src/
    parser.py               # Parse morphology TSV -> pandas DataFrame
    buckwalter.py           # Buckwalter <-> Arabic Unicode conversion
  notebooks/
    01_explore_and_discover.ipynb    # Discovery, validation, counting
    02_results_and_exploration.ipynb # Results tables, open-ended exploration
    03_audit_and_full_recount.ipynb  # Audit, full method grid, cross-validation
  output/
    full_counts.csv         # The complete method grid, one row per word
    occurrences.csv         # Every counted occurrence with chapter:verse:word location
    pairs_table.png         # Regenerated pairs chart (reproducible from notebook 03)
    *.png (legacy)          # Older charts; local only, not committed (no generating code)
  validation/
    validate_locations.py   # Token-level check of every occurrence vs canonical text
    DumpTokens.java         # JQuranTree token dumper used by the script
    token_validation_report.txt
```

## How It Works

### The Corpus Format

Each line in the morphology file is a tab-separated record:

```
LOCATION    FORM    TAG    FEATURES
(1:1:1:1)   bsm     P      PREFIX|bi+
(1:1:1:2)   {sm     N      STEM|POS:N|LEM:{som|ROOT:smw|GEN
```

- **LOCATION**: `(chapter:verse:word:segment)` — a word can have multiple segments (prefix, stem, suffix)
- **FORM**: The surface form in Buckwalter transliteration
- **FEATURES**: Pipe-separated morphological tags

We only use **STEM** entries (77,915 of them). Prefixes and suffixes are ignored for counting purposes.

### Buckwalter Transliteration

The corpus uses [Buckwalter transliteration](https://en.wikipedia.org/wiki/Buckwalter_transliteration) — an ASCII encoding of Arabic script. Every Arabic letter maps to one ASCII character:

| Arabic | BW | Name |
|--------|-----|------|
| ا | A | alif |
| ب | b | ba |
| ت | t | ta |
| ث | v | tha |
| ج | j | jim |
| ح | H | ha |
| خ | x | kha |
| د | d | dal |
| ذ | * | dhal |
| ر | r | ra |
| ز | z | zayn |
| س | s | sin |
| ش | $ | shin |
| ص | S | sad |
| ض | D | dad |
| ط | T | ta (emphatic) |
| ظ | Z | za (emphatic) |
| ع | E | ayn |
| غ | g | ghayn |
| ف | f | fa |
| ق | q | qaf |
| ك | k | kaf |
| ل | l | lam |
| م | m | mim |
| ن | n | nun |
| ه | h | ha |
| و | w | waw |
| ي | y | ya |

`src/buckwalter.py` handles conversion between the two.

### Key Morphological Concepts

**Root** (`ROOT`): The 3-letter (trilateral) consonantal skeleton that Arabic words derive from. Example: root `k-t-b` (ك-ت-ب) gives rise to kitaab (book), kaatib (writer), maktaba (library), etc. Most words in Arabic share a root with semantically related words. Proper nouns typically have no root in the corpus.

**Lemma** (`LEM`): The dictionary headword form. Multiple surface forms (singular, dual, plural, different cases) map to the same lemma. Example: the lemma `yawom` (يوم, day) covers both yawm (singular) and ayyaam (plural). This is our primary counting unit.

**Part of Speech** (`POS`): The word's grammatical category:
- `N` = noun, `V` = verb, `ADJ` = adjective, `PN` = proper noun
- `T` = time adverb (e.g. yawm when used adverbially)
- `P` = preposition, `CONJ` = conjunction, etc.

**Person-Gender-Number** (`PGN`): Encodes grammatical person (1st/2nd/3rd), gender (M/F), and number (S=singular, D=dual, P=plural). Example: `3MS` = third person masculine singular. Used for:
- Number extraction: the final character (S/D/P) tells us singular vs plural
- Gender disambiguation: the Akhira lemma uses gender to separate "hereafter" (F) from "last" (M)

**Broken Plurals**: Arabic has irregular plurals that don't follow predictable patterns — e.g. rajul (man) → rijaal (men), kitaab (book) → kutub (books). Sometimes the plural has a different lemma in the corpus, so we track these separately.

**Suppletive Plurals**: Some words use an entirely different root for their plural — e.g. imra'a (woman, root: m-r-') → nisaa' (women, root: n-s-w). This is standard Arabic morphology, not an anomaly.

## Counting Methods

We apply **four counting methods uniformly** to every word in notebooks 01/02. No cherry-picking — every word gets all four counts. Notebook 03 extends this to the full grid TASK.txt asks for (per-POS, per-number, root-by-POS including verbs).

| Method | What it counts | Use case |
|--------|---------------|----------|
| **Lemma** | Exact lemma match, all grammatical forms (sg/dual/pl, all cases) | Primary count |
| **Lemma+Variants** | Same as Lemma, plus irregular-plural / variant-noun selectors stored under other lemmas | More inclusive count for words with irregular plurals |
| **SingularOnly** | Lemma match, excluding dual (D) and plural (P) forms | For comparing "the concept" without plural inflections |
| **RootNominal** | All nouns + adjectives + proper nouns + time adverbs sharing the root | Broader semantic field count |

A variant selector is either a plain lemma (e.g. `rijaAl` for `rajul`) or a `(lemma, POS, NUMBER)`
tuple when only a slice of another lemma belongs to the word — required for Izam, whose plural
عظام is tagged under `LEM:EaZiym` as `POS:N` + `MP` (see Audit corrections).

### Gender Filter (Akhira only)

One word — Akhira (the hereafter) — requires a gender filter. Its lemma `A^xir` (آخر), 155 occurrences total, conflates two genuinely different words:

- **Feminine** `A^xirap` (آخرة) = "the hereafter" — 115 occurrences
- **Masculine** `A^xir` (آخر) = "last/latter" — 40 occurrences

These are semantically distinct words that happen to share a lemma in the corpus. We filter by PGN containing "F" to isolate the hereafter meaning. This is the **only** word in our list that needs this treatment — verified by checking all other lemmas.

### What We Include and Exclude

- We count **STEM entries only** — prefixes (like the definite article al-) and suffixes (case markers, pronouns) are not separate word counts
- For root-nominal counts, we include POS types N, ADJ, PN, and T (time adverbs) — we exclude verbs (V) and particles (notebook 03 also reports root totals including verbs, and per-POS)
- Variant selectors are listed explicitly per word rather than discovered automatically
- Proper nouns with no root (Adam, Isa, Iblis, Jahannam) get `—` for root-nominal count

### Audit corrections (2026-06-11)

Re-derived from scratch in `notebooks/03_audit_and_full_recount.ipynb`; previously published numbers that were wrong:

- **Izam (bones): 2 → 15.** The corpus tags the plural عظام under `LEM:EaZiym` (the "great"
  lemma) as `POS:N` + `MP` — 13 occurrences, including the embryology verse 23:14 (twice).
  Counting `LEM:EaZom` alone misses all of them. The corpus website keeps the same filing and
  glosses those entries "[the bones]", so this is an upstream annotation decision that any
  bones count must work around.
- **Akhira masculine: 30 → 40** (lemma total is 155, not 145).
- **Barr split: "land 13 + righteous 9" → land 12 + righteous/dutiful 10.** Form-level:
  `bar~i` ×12 (all "in the land"), plus 52:28 divine name *al-Barr*, 19:14/19:32 "dutiful",
  أبرار ×6 and بررة ×1 (righteous).
- **Hayat/Mawt variant symmetry.** Mawt had been credited `mawotat`+`mamaAt` (→56) while Hayat
  got nothing; its exact counterparts `m~aHoyaA` (2) + `HayawaAn` (1) → 79 are now included
  (6:162 pairs مَحْيَا with مَمَات in one verse).
- **38 target words, not 37.**

### Data Notes

These are not uncertainties — just things worth knowing:

- **Plurals live inside lemmas**: the corpus files regular *and many broken* plurals under the
  singular's lemma with `MP`/`FP`/`MD`/`FD` flags — malak includes ملائكة (73 pl), shaytan includes
  شياطين (18 pl), yawm includes أيام (27 pl) + يومين (3 dual), jannah includes جنات (71 pl + 8 dual),
  shahr includes أشهر/شهور (7 pl + 2 dual). The SingularOnly method strips these uniformly.
- **yawma'idhin** (يومئذ, "that day", 68x) is its own lemma and is *not* part of yawm's 405.
- **niswa** (نسوة, 12:30) is tagged under `LEM:nisaA^'`, so the women-plural count (59) already includes it.
- **Root overlap**: Some roots produce many unrelated words. For example, root `mlk` gives malak (angel), malik (king), mulk (dominion) — but these are different lemmas and don't contaminate each other's lemma counts.

## Notebooks

### 01_explore_and_discover.ipynb

The main working notebook:

1. **Load data** — parse the morphology file into a pandas DataFrame
2. **Discovery** — for each of 38 target words, search by root to find all candidate lemmas
3. **Validation** — convert Buckwalter lemmas to Arabic, check sample verses, confirm meanings
4. **Counting** — apply all 4 methods uniformly, display results with notes

### 02_results_and_exploration.ipynb

Clean results and open-ended data exploration:

1. **15 original word pairs** — side-by-side comparison table
2. **Standalone words** — Qaala (said), Maghfira (forgiveness), embryology sequence
3. **Exploration** — top lemmas, proper noun coincidences, broader semantic pairs, notable number matches, verse co-occurrence analysis

### 03_audit_and_full_recount.ipynb

The audit and the authoritative full results:

1. **Audit evidence** — the bones/Akhira/Barr/Hayat findings, with every supporting row shown
2. **Full method grid** — per word: lemma, lemma+variants, singular/dual/plural, lemma-by-POS,
   root total, root-by-POS (N/ADJ/PN/V/T) → `output/full_counts.csv`
3. **Occurrence index** — every counted occurrence with chapter:verse:word → `output/occurrences.csv`
4. **Root listings** — all lemmas under every target root, with counts (per TASK.txt)
5. **Qaala verb-form breakdown** — aspect × voice × person-gender-number
6. **External cross-validation** — every target root checked against corpus.quran.com
   (~140 numbers, all exact) plus token-level validation of all 3,960 occurrences via JQuranTree

## Replicability

To verify any count:

1. Filter `output/occurrences.csv` to the word — every counted occurrence is listed with its
   chapter:verse:word location, surface form, lemma, POS, and number
2. Look up those locations in any Quran text, or on https://corpus.quran.com
   (`qurandictionary.jsp?q=ROOT` with the Buckwalter root, e.g. `q=mlk`)
3. The notebooks show every intermediate step — lemma discovery, validation, counting —
   and notebook 03 re-derives everything with asserts tying the grid to the audit

All Buckwalter strings were discovered from the data (not hardcoded from external sources) and validated by converting back to Arabic.

### Validation status (2026-06-11)

- **corpus.quran.com**: every root used by the 38 words was fetched and compared — all root
  totals and per-lemma counts matched exactly (~140 numbers across 35 roots).
- **Token level (JQuranTree)**: all **3,960** counted occurrences were checked against the
  canonical Tanzil Uthmani text via [JQuranTree](https://github.com/dsog/jqurantree), the Java
  API named in TASK.txt — every location holds a real token whose letters match the morphology
  file's reconstruction (0 mismatches, 0 missing). See `validation/` for the runnable scripts
  and `validation/token_validation_report.txt` for the report; full details in notebook 03,
  section 9.

### Tooling note

Alternatives considered: [JQuranTree](https://corpus.quran.com/java/) (the corpus project's
official Java API), [QuranTree.jl](https://aclanthology.org/2021.wanlp-1.22/) (Julia), and the
pip package [`qurancorpus`](https://github.com/assem-ch/python-qurancorpus) (abandoned; parses
only the obsolete v0.1 XML). For a Python/pandas workflow over the documented v0.4 TSV, direct
parsing is standard practice; `src/parser.py` is verified 1:1 against the raw file and against
the corpus website.
