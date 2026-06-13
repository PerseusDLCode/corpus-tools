# corpus-tools

Tools for normalizing and auditing Perseus TEI corpora.

## Setup

```bash
pdm install
# or
uv sync
```

With the virtualenv activated, all commands below are available directly.
For Makefile-driven batch operations, see [Makefile](#makefile).

---

## Tools

| Command | Purpose |
|---|---|
| `corpus-tools set-genre` | Annotate a TEI document with its Perseus structural genre |
| `corpus-tools normalize` | Run the genre-appropriate normalization pipeline |
| `corpus-tools validate` | Schematron validation — pipeline gate |
| `annotate-genres` | Claude API batch genre suggestion for a whole corpus |
| `generate-genre-map` | Emit one CSV row per file for classicist review |
| `apply-genre-map` | Apply a reviewed CSV to TEI files in-place |
| `audit-refs` | Inspect CTS citation reference declarations |
| `audit-structure` | Inspect div/milestone citation hierarchy |
| `audit-schema` | Run a Schematron schema and report all findings |
| `survey-corpus` | Extract element/attribute vocabulary by genre |
| `validate-corpus` | Validate files against target RELAX NG schemas via jing |

The genre taxonomy (used by all genre-aware commands via `--odd`) is the
`perseus-genre` structural-citation taxonomy defined in `perseus_base.odd`.
Valid genre ids are structural subclasses like `prose-standard`,
`verse-stichic`, `drama-act-scene-line` — not literary genres.

---

## Workflows

### Normalizing a new corpus

The main pipeline for bringing a new corpus to the Perseus standard:

```
annotate-genres → generate-genre-map → [classicist review] → apply-genre-map → normalize → validate
```

```bash
# 1. Suggest genres via Claude API (resumable; skips files already annotated)
annotate-genres DATA_DIR --odd ../perseus-schemas/perseus_base.odd

# 2. Emit a CSV for review
generate-genre-map DATA_DIR genres.csv --odd ../perseus-schemas/perseus_base.odd

# 3. Classicists review and edit the recommended_genre column in genres.csv

# 4. Apply assignments (validate-before-write; run on a working branch)
git checkout -b genre-assignments
apply-genre-map genres.csv DATA_DIR --odd ../perseus-schemas/perseus_base.odd

# 5. Normalize all annotated files
corpus-tools normalize DATA_DIR/**/*.xml --odd ../perseus-schemas/perseus_base.odd

# 6. Validate
corpus-tools validate DATA_DIR/**/*.xml
```

### Normalizing individual files

When a corpus is already annotated and you need to add or fix individual texts:

```bash
corpus-tools set-genre FILE --genre prose-standard --odd ../perseus-schemas/perseus_base.odd
corpus-tools normalize FILE --odd ../perseus-schemas/perseus_base.odd
corpus-tools validate FILE
```

### Schema development loop

```
survey-corpus → validate-corpus → edit ODDs → make -C ../perseus-schemas → repeat
```

```bash
make -C ../perseus-schemas              # compile ODD → RNG (must run first)
survey-corpus DATA_DIR --odd ../perseus-schemas/perseus_base.odd
validate-corpus DATA_DIR --odd ../perseus-schemas/perseus_base.odd
# Edit ODDs, recompile, repeat
```

---

## Command reference

### `corpus-tools set-genre`

Annotates a document with its Perseus genre category. Must be run before
`normalize`. Valid genre ids are defined in `perseus_base.odd`; pass its
path via `--odd`.

```bash
corpus-tools set-genre FILE [FILE ...] --genre GENRE --odd ODD [-o PATH]
```

```bash
# Annotate in-place
corpus-tools set-genre tlg0003.tlg001.1st1K-grc1.xml \
    --genre prose-standard \
    --odd ../perseus-schemas/perseus_base.odd

# Annotate a batch, writing into a separate directory
corpus-tools set-genre -o annotated/ canonical-greekLit/data/tlg0003/tlg001/*.xml \
    --genre prose-standard \
    --odd ../perseus-schemas/perseus_base.odd
```

---

### `corpus-tools normalize`

Runs the genre-appropriate XSLT pipeline on a genre-annotated document.
The genre must already be set (via `set-genre` or manually).

```bash
corpus-tools normalize FILE [FILE ...] --odd ODD [-o PATH] [--cts-base URN] [--tei-schema NAME]
```

| Option | Description |
|---|---|
| `--odd ODD` | Path to `perseus_base.odd` (authoritative genre taxonomy). Required. |
| `-o PATH` | Output file (single input) or directory (batch). Default: overwrite in-place. |
| `--cts-base URN` | Override the auto-computed CTS URN. Required for csel-dev and First1KGreek files. |
| `--tei-schema NAME` | Override the schema name written into the `<?xml-model?>` PI. |

The pipeline applied depends on genre family:

| Genre family | Steps |
|---|---|
| prose | normalize-cts → set-cts-urn → add-citeStructure → set-schema(perseus_prose) |
| verse | normalize-cts → set-cts-urn → add-citeStructure → fix-verse → set-schema(perseus_verse) |
| drama | normalize-cts → set-cts-urn → add-citeStructure → set-schema(perseus_drama) |

```bash
corpus-tools normalize tlg0003.tlg001.1st1K-grc1.xml \
    --odd ../perseus-schemas/perseus_base.odd

# csel-dev and First1KGreek files require --cts-base (URN is on div/@n, not body/@xml:base)
corpus-tools normalize stoa0245c.stoa001.csel_lat.xml \
    --odd ../perseus-schemas/perseus_base.odd \
    --cts-base urn:cts:latinLit:stoa0245c.stoa001.csel_lat
```

---

### `corpus-tools validate`

Validates normalized documents against a Schematron schema. Exits non-zero
if any assertion fails.

```bash
corpus-tools validate FILE [FILE ...] [--schema SCH]
```

The default schema is `schematron/perseus_normalized.sch`, which checks that
all pipeline steps have been applied (genre annotation, CTS URN, citeStructure,
schema PI).

```bash
corpus-tools validate tlg0003.tlg001.1st1K-grc1.xml
corpus-tools validate --schema schematron/perseus_encoding.sch *.xml
```

---

### `annotate-genres`

Walks every work-level `__cts__.xml`, collects structural signals from the
TEI files in that directory (counts of `<sp>`, `<l>`, `<p>` elements;
`<div>` types), calls the Claude API with the work's author, title,
description, and signals, and writes
`<ti:genre confidence="high|medium|low">GENRE_ID</ti:genre>` back to the
`__cts__.xml`. **Resumable**: files that already have `<ti:genre>` are
skipped.

```bash
annotate-genres DATA_DIR --odd ODD [--model MODEL] [--dry-run]
```

| Option | Description |
|---|---|
| `--odd ODD` | Path to `perseus_base.odd`. Required. |
| `--model MODEL` | Claude model id. Default: `claude-haiku-4-5-20251001`. |
| `--dry-run` | Print suggestions without writing to disk. |

| Confidence | Meaning |
|---|---|
| `high` | Structural signal and API suggestion agree. |
| `medium` | One signal absent, or structural family and API family disagree. |
| `low` | API returned a value not in the taxonomy. Genre written as `unknown`. |

```bash
annotate-genres ../data-local/canonical-greekLit/data \
    --odd ../perseus-schemas/perseus_base.odd

annotate-genres ../data-local/canonical-greekLit/data \
    --odd ../perseus-schemas/perseus_base.odd \
    --dry-run
```

Genre assignments are stored in the work-level `__cts__.xml` files as
`<ti:genre>` elements. These are the authoritative genre source for
`generate-genre-map` and `apply-genre-map`.

---

### `generate-genre-map`

Reads annotated `__cts__.xml` files and emits one CSV row per TEI text
file. The `recommended_genre` column is pre-filled with `suggested_genre`;
classicists edit this column before `apply-genre-map`.

```bash
generate-genre-map DATA_DIR OUTPUT_CSV --odd ODD
```

| Column | Description |
|---|---|
| `urn` | CTS URN (from `body/@xml:base` if present, else derived from path). |
| `path` | Path to TEI file, relative to `DATA_DIR`. |
| `author` | Author name from the textgroup `__cts__.xml`. |
| `title` | Work title from the work `__cts__.xml`. |
| `suggested_genre` | Genre id from `annotate-genres`. Blank if not yet annotated. |
| `confidence` | `high`, `medium`, or `low`. |
| `recommended_genre` | **Classicists edit this column.** Pre-filled with `suggested_genre`. |
| `notes` | Free text for editorial notes. |

```bash
generate-genre-map ../data-local/canonical-greekLit/data genres.csv \
    --odd ../perseus-schemas/perseus_base.odd
```

---

### `apply-genre-map`

Reads a reviewed CSV and runs `set-genre` on each TEI file in-place.
**All `recommended_genre` values are validated against the ODD taxonomy
before any file is touched** — if any value is invalid, the command prints
every bad value and exits without modifying anything.

```bash
apply-genre-map CSV_FILE DATA_DIR --odd ODD
```

```bash
git checkout -b genre-assignments
apply-genre-map genres.csv ../data-local/canonical-greekLit/data \
    --odd ../perseus-schemas/perseus_base.odd
git diff --stat
```

Rows with a blank `recommended_genre` are skipped. P4 files (`<TEI.2>` root)
are detected and skipped with a `SKIP (P4 <TEI.2>)` message. Errors are
logged per-file; processing continues and the exit code reflects the error count.

---

### `audit-refs`

Read-only. Checks citation reference declarations: CTS URN on `<body>`,
presence of `<citeStructure>`, and `<refsDecl default="true">`. Exits 1
only if a file cannot be parsed.

```bash
audit-refs FILE [FILE ...] [--format text|json] [-o DIR]
```

```bash
audit-refs tlg0003.tlg001.1st1K-grc1.xml
audit-refs --format json -o reports/ canonical-greekLit/data/**/*.xml
```

---

### `audit-structure`

Read-only. Introspects the document's `<div type="textpart">` hierarchy and
`<milestone>` elements. Reports citation levels (depth, count, attribute
coverage), proposes a `citeStructure` fragment, and flags structural anomalies.

```bash
audit-structure FILE [FILE ...] [--format text|json] [-o DIR]
```

```bash
audit-structure tlg0003.tlg001.1st1K-grc1.xml
audit-structure --format json -o reports/ canonical-greekLit/data/**/*.xml
```

---

### `audit-schema`

Read-only. Runs a Schematron schema against documents and reports all
findings including advisory warnings and info messages (not just hard errors).
Unlike `corpus-tools validate`, findings do not affect the exit code.

```bash
audit-schema FILE [FILE ...] --schema SCH [--format text|json] [-o DIR]
```

```bash
audit-schema --schema schematron/perseus_encoding.sch tlg0003.tlg001.1st1K-eng1.xml
audit-schema --schema schematron/perseus_encoding.sch \
    --format json -o reports/ canonical-greekLit/data/**/*.xml
```

All three audit commands share `--format text|json` and `-o DIR`. Output
filenames follow `<stem>-{refs,structure,schema}.{txt,json}`, so all three
can safely write to the same directory.

---

### `survey-corpus`

Walks all TEI files and extracts element and attribute vocabulary grouped by
genre. Useful for understanding what markup is actually present before
tightening the schemas.

```bash
survey-corpus DATA_DIR [--output-dir DIR] [--odd ODD] [--genre GENRE]
```

| Option | Description |
|---|---|
| `--output-dir DIR` | Where to write output CSVs (default: `survey/`). |
| `--odd ODD` | Path to `perseus_base.odd` for genre taxonomy. |
| `--genre GENRE` | Restrict output to files annotated with a single genre. |

**Output CSVs**

| File | Contents |
|---|---|
| `elements.csv` | `(element, genre)` pairs with file and instance counts. |
| `attributes.csv` | Controlled-vocabulary attribute values: `@type`, `@subtype`, `@unit`, `@met`, `@rend`, `@place`, `@role`, `@ident`, `@ed`, `@lang`. Up to 30 most-frequent values per `(element, attribute, genre)` triple. |
| `structure.csv` | Per-file citation structure: URN, genre, structural type, div subtypes, milestone units, issues. |

```bash
survey-corpus ../data-local/canonical-greekLit/data \
    --odd ../perseus-schemas/perseus_base.odd

survey-corpus ../data-local/canonical-greekLit/data \
    --odd ../perseus-schemas/perseus_base.odd \
    --genre verse-book-line
```

---

### `validate-corpus`

Validates every TEI file against its target Perseus RELAX NG schema using
[`jing`](https://relaxng.org/jclark/) (must be installed: `brew install
jing-trang`). Files are batched by schema family. Errors are aggregated
across files so systemic gaps rise to the top.

```bash
validate-corpus DATA_DIR [--schema-dir DIR] [--output-dir DIR] [--odd ODD] [--genre-map CSV]
```

| Option | Description |
|---|---|
| `--schema-dir DIR` | Directory containing compiled `.rng` files (default: `../perseus-schemas`). Compile first with `make -C ../perseus-schemas`. |
| `--output-dir DIR` | Where to write `rng_errors.csv` (default: `survey/`). |
| `--odd ODD` | Path to `perseus_base.odd` for genre taxonomy. |
| `--genre-map CSV` | `genres.csv`-style fallback for files not yet annotated in `__cts__.xml`. |

**Output:** `rng_errors.csv` — one row per distinct error type with `family`,
`element`, `message`, `instance_count`, `file_count`.

```bash
make -C ../perseus-schemas   # compile schemas if ODDs have changed
validate-corpus ../data-local/canonical-greekLit/data \
    --odd ../perseus-schemas/perseus_base.odd
```

---

## Makefile

Convenience targets for common batch operations. `ODD` defaults to
`../perseus-schemas/perseus_base.odd`.

```bash
make help   # list all targets with descriptions
```

```bash
# Genre annotation
make annotate-genres    DATA_DIR=../data-local/canonical-greekLit/data
make generate-genre-map DATA_DIR=../data-local/canonical-greekLit/data OUTPUT_CSV=genres.csv
make apply-genre-map    CSV_FILE=genres.csv DATA_DIR=../data-local/canonical-greekLit/data

# Pipeline
make set-genre   FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml" GENRE=prose-standard
make normalize   FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml" OUT=normalized/
make validate    FILES="normalized/*.xml"
make pipeline    FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml" GENRE=prose-standard OUT=normalized/

# Audit
make audit           FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml"
make audit-refs      FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml" OUT=reports/
make audit-structure FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml"
make audit-schema    FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml" OUT=reports/

# Schema development
make survey-corpus   DATA_DIR=../data-local/canonical-greekLit/data
make validate-corpus DATA_DIR=../data-local/canonical-greekLit/data
```

---

## XSLT stylesheets

All stylesheets are in `xslt/` and require Saxon (XSLT 2.0 via saxonche).
The pipeline commands invoke them in sequence; they can also be run individually.

| Stylesheet | Purpose | Parameters |
|---|---|---|
| `normalize-cts.xsl` | Remove EpiDoc `div[@type='edition']` wrappers; hoist `@subtype` to `@type` on textpart divs; strip `@xml:base` | — |
| `set-cts-urn.xsl` | Set `@xml:base` on `<body>`; add `<idno type="CTS">` to `<publicationStmt>` | `cts-base` (default: auto-derived from path) |
| `add-citeStructure.xsl` | Append genre-appropriate `<refsDecl>` with `<citeStructure>` to `<encodingDesc>` | `genre` (`prose`\|`verse`\|`drama`) |
| `fix-verse.xsl` | Convert `@ana`-encoded meter values to `@met`; strip placeholder `met="u"/"U"` | — |
| `set-schema.xsl` | Update the `<?xml-model?>` PI to point to a Perseus schema (.rng) | `tei-schema` (default: `perseus_base`) |
| `set-genre.xsl` | Add `<catRef scheme="#perseus-genre">` to `<profileDesc>` | `genre` |
| `p4-to-p5-lexical.xsl` | Lexical P4 → P5 conversion (preprocessing only; not in main pipeline) | — |

`set-cts-urn.xsl` derives the CTS URN from the filesystem path when
`cts-base` is not supplied, expecting
`canonical-{namespace}/data/{author}/{work}/{filename}.xml`.

---

## Schematron schemas

| Schema | Purpose |
|---|---|
| `schematron/perseus_normalized.sch` | Pipeline gate: validates that genre annotation, CTS URN, citeStructure, and schema PI are all present. Used by `corpus-tools validate`. |
| `schematron/perseus_encoding.sch` | Advisory checks for encoding anomalies requiring human review before correction. Used by `audit-schema`. |

---

## Auditors (programmatic API)

The `auditors` package provides an object-oriented API for document inspection,
used by the audit commands and available for scripting. See
[`src/auditors/README.md`](src/auditors/README.md).
