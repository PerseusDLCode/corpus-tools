# corpus-tools

Tools for normalizing and auditing Perseus TEI corpora.

## Setup

```bash
pdm install
# or
uv sync
```

With the virtualenv activated, all commands below are available directly.
For Makefile-driven batch workflows, see [Makefile](#makefile).

---

## Commands

### Pipeline: `corpus-tools`

Transforms TEI documents through a normalization pipeline. Operates on one
or more files; without `-o`, output overwrites the source in-place.

#### `set-genre`

Annotates a document with its Perseus genre category. Must be run before
`normalize`. Valid genre ids are defined in `perseus_base.odd`; pass its path
via `--odd`.

```bash
corpus-tools set-genre FILE [FILE ...] --genre GENRE --odd ODD [-o PATH]
```

```bash
# Annotate in-place
corpus-tools set-genre tlg0003.tlg001.1st1K-eng1.xml \
    --genre prose-standard \
    --odd ../perseus-schemas/perseus_base.odd

# Annotate a batch, writing into a separate directory
corpus-tools set-genre -o annotated/ canonical-greekLit/data/tlg0003/tlg001/*.xml \
    --genre prose-standard \
    --odd ../perseus-schemas/perseus_base.odd
```

#### `normalize`

Runs a genre-appropriate XSLT pipeline on a genre-annotated document. The
genre must already be set (via `set-genre` or manually).

```bash
corpus-tools normalize FILE [FILE ...] --odd ODD [-o PATH] [--cts-base URN] [--tei-schema NAME]
```

| Option | Description |
|---|---|
| `--odd ODD` | Path to `perseus_base.odd` (authoritative genre taxonomy). Required. |
| `-o PATH` | Output file (single input) or directory (batch). Default: overwrite in-place. |
| `--cts-base URN` | Override the auto-computed CTS URN (needed for `pdlrefwk` texts). |
| `--tei-schema NAME` | Override the schema name written into the `<?xml-model?>` PI. |

The pipeline applied depends on genre family:

| Genre family | Steps |
|---|---|
| prose | normalize-cts → set-cts-urn → add-citeStructure → set-schema(perseus_prose) |
| verse | normalize-cts → set-cts-urn → add-citeStructure → fix-verse → set-schema(perseus_verse) |
| drama | normalize-cts → set-cts-urn → add-citeStructure → set-schema(perseus_drama) |

```bash
# Normalize a single file in-place (genre must already be set)
corpus-tools normalize tlg0003.tlg001.1st1K-eng1.xml \
    --odd ../perseus-schemas/perseus_base.odd

# Full workflow: annotate then normalize into a separate directory
corpus-tools set-genre --genre prose-standard --odd ../perseus-schemas/perseus_base.odd \
    tlg0003.tlg001.1st1K-eng1.xml
corpus-tools normalize -o normalized/ --odd ../perseus-schemas/perseus_base.odd \
    tlg0003.tlg001.1st1K-eng1.xml
```

#### `validate`

Validates normalized documents against a Schematron schema. Exits non-zero
if any assertion fails.

```bash
corpus-tools validate FILE [FILE ...] [--schema SCH]
```

The default schema is `schematron/perseus_normalized.sch`, which checks that
all pipeline steps have been applied (genre annotation, CTS URN, citeStructure,
schema PI).

```bash
corpus-tools validate normalized/tlg0003.tlg001.1st1K-eng1.xml
corpus-tools validate --schema schematron/perseus_encoding.sch *.xml
```

---

### Genre annotation workflow

Before the normalization pipeline can run on a corpus at scale, every text
needs a genre assignment. This three-step workflow uses the Claude API to
suggest genres, produces a CSV for editorial review, and then applies the
reviewed assignments.

**Overview**

```
annotate-genres  →  review CSV  →  apply-genre-map  →  corpus-tools set-genre / normalize
```

Genre assignments are stored as `<ti:genre confidence="…">GENRE_ID</ti:genre>`
in each work-level `__cts__.xml` file. This keeps genre metadata with the
CTS work record rather than buried in individual TEI files, and means the
`__cts__.xml` files are the authoritative genre source for the corpus.

The genre taxonomy itself lives in `perseus_base.odd` (the `perseus-genre`
taxonomy); all three commands read it via `--odd` so there is no hardcoded
list to keep in sync.

---

#### `annotate-genres`

Walks every work-level `__cts__.xml`, collects structural signals from the
TEI files in that directory (counts of `<sp>`, `<l>`, `<p>` elements; `<div>`
types), calls the Claude API with the work's author, title, description, and
signals, and writes `<ti:genre confidence="high|medium|low">GENRE_ID</ti:genre>`
back to the `__cts__.xml`. **Resumable**: any file that already has `<ti:genre>`
is skipped, so the command can be interrupted and rerun safely.

```bash
annotate-genres DATA_DIR --odd ODD [--model MODEL] [--dry-run]
```

| Option | Description |
|---|---|
| `--odd ODD` | Path to `perseus_base.odd`. Required. |
| `--model MODEL` | Claude model id. Default: `claude-haiku-4-5-20251001` |
| `--dry-run` | Print suggestions without writing to disk. |

**Confidence levels**

| Value | Meaning |
|---|---|
| `high` | Structural signal (drama/verse/prose family) and API suggestion agree. |
| `medium` | One signal absent, or structural family and API family disagree. Flag for closer review. |
| `low` | API returned a value not in the taxonomy. Genre written as `unknown`. |

```bash
# Annotate the full corpus (takes ~30–40 min; resumable if interrupted)
annotate-genres ../data-local/canonical-greekLit/data \
    --odd ../perseus-schemas/perseus_base.odd

# Dry run to preview suggestions without writing
annotate-genres ../data-local/canonical-greekLit/data \
    --odd ../perseus-schemas/perseus_base.odd \
    --dry-run
```

---

#### `generate-genre-map`

Reads the annotated `__cts__.xml` files and emits one CSV row per TEI text
file. The `recommended_genre` column is pre-filled with `suggested_genre`;
classicists edit this column to correct any mistakes before the next step.

```bash
generate-genre-map DATA_DIR OUTPUT_CSV --odd ODD
```

**CSV columns**

| Column | Description |
|---|---|
| `urn` | CTS URN (from `body/@xml:base` if present, else derived from path). |
| `path` | Path to TEI file, relative to `DATA_DIR`. |
| `author` | Author name from the textgroup `__cts__.xml`. |
| `title` | Work title from the work `__cts__.xml`. |
| `suggested_genre` | Genre id suggested by `annotate-genres`. Blank if not yet annotated. |
| `confidence` | `high`, `medium`, or `low`. |
| `recommended_genre` | **Classicist edits this column.** Pre-filled with `suggested_genre`. |
| `notes` | Free text for editorial notes. |

```bash
generate-genre-map ../data-local/canonical-greekLit/data genres.csv \
    --odd ../perseus-schemas/perseus_base.odd
```

Send `genres.csv` to classicists. They correct the `recommended_genre` column,
leaving it blank for any text they are not yet ready to classify.

---

#### `apply-genre-map`

Reads a reviewed CSV and applies `set-genre` to each TEI file in-place.
**All `recommended_genre` values are validated against the ODD taxonomy before
any file is touched** — if any value is invalid, the command prints every
bad value and exits without modifying anything.

Run this on a working branch so the changes can be reviewed and rolled back
if needed.

```bash
apply-genre-map CSV_FILE DATA_DIR --odd ODD
```

```bash
# On a working branch
git checkout -b genre-assignments

apply-genre-map genres.csv ../data-local/canonical-greekLit/data \
    --odd ../perseus-schemas/perseus_base.odd

# Review the diff, then commit or reset
git diff --stat
```

Rows with a blank `recommended_genre` are skipped. Rows where the file is
missing or the transform fails are logged as errors; other rows continue
processing and the exit code reflects the error count.

---

#### Makefile targets

The `ODD` variable defaults to `../perseus-schemas/perseus_base.odd`.

```bash
# Annotate (set DATA_DIR; optionally override MODEL or add DRY_RUN=1)
make annotate-genres DATA_DIR=../data-local/canonical-greekLit/data
make annotate-genres DATA_DIR=../data-local/canonical-greekLit/data DRY_RUN=1

# Generate the review CSV
make generate-genre-map DATA_DIR=../data-local/canonical-greekLit/data OUTPUT_CSV=genres.csv

# Apply after classicist review (run on a working branch)
make apply-genre-map CSV_FILE=genres.csv DATA_DIR=../data-local/canonical-greekLit/data
```

---

### Audit commands

Read-only inspection tools that run auditors against documents and produce
structured reports. Unlike `validate`, findings do not affect the exit code —
the commands exit 1 only if a file cannot be parsed.

All three commands share the same flags:

| Flag | Description |
|---|---|
| `--format text\|json` | Output format (default: `text`). |
| `-o DIR` | Write one report file per input into DIR instead of stdout. |

Output filenames in `-o DIR` mode follow the pattern `<stem>-{refs,structure,schema}.{txt,json}`,
so all three audit commands can safely write to the same directory.

#### `audit-refs`

Checks citation reference declarations: CTS URN on `<body>`, presence of
`<citeStructure>`, and `<refsDecl default="true">`.

```bash
audit-refs FILE [FILE ...] [--format text|json] [-o DIR]
```

```bash
audit-refs tlg0003.tlg001.perseus-grc2.xml
audit-refs --format json -o reports/ canonical-greekLit/data/**/*.xml
```

#### `audit-structure`

Introspects the document's `<div type="textpart">` hierarchy and `<milestone>`
elements. Reports citation levels (depth, count, attribute coverage), proposes
a `citeStructure` fragment, and flags structural anomalies.

```bash
audit-structure FILE [FILE ...] [--format text|json] [-o DIR]
```

```bash
audit-structure tlg0003.tlg001.perseus-grc2.xml
audit-structure --format json -o reports/ canonical-greekLit/data/**/*.xml
```

#### `audit-schema`

Runs a Schematron schema against documents and reports all findings, including
advisory warnings and info messages (not just hard errors). `--schema` is
required.

```bash
audit-schema FILE [FILE ...] --schema SCH [--format text|json] [-o DIR]
```

```bash
# Check for encoding anomalies (e.g. empty <s/> milestone abuse)
audit-schema --schema schematron/perseus_encoding.sch tlg0003.tlg001.1st1K-eng1.xml

# Batch audit into a reports directory
audit-schema --schema schematron/perseus_encoding.sch \
    --format json -o reports/ canonical-greekLit/data/**/*.xml
```

---

### Schema development workflow

These commands support an iterative, data-driven approach to tightening the
Perseus schemas: first survey what is actually in the corpus (descriptive),
then validate against the target schemas to find gaps, then edit the ODDs and
repeat.

```
survey-corpus  →  validate-corpus  →  edit ODDs  →  make -C ../perseus-schemas  →  repeat
```

Both commands determine each file's target schema from the genre annotation in
the sibling work-level `__cts__.xml` (written by `annotate-genres`), or from a
`genres.csv`-style map passed via `--genre-map`.

#### `survey-corpus`

Walks all TEI files in the corpus and extracts element and attribute vocabulary
grouped by genre. Useful for understanding what markup is actually present before
deciding what to allow or require in the schemas.

```bash
survey-corpus DATA_DIR [--output-dir DIR] [--odd ODD] [--genre GENRE]
```

| Option | Description |
|---|---|
| `--output-dir DIR` | Where to write output CSVs (default: `survey/`). |
| `--odd ODD` | Path to `perseus_base.odd` for genre taxonomy (default: `../perseus-schemas/perseus_base.odd`). |
| `--genre GENRE` | Restrict output to files annotated with a single genre leaf. |

**Output CSVs**

| File | Contents |
|---|---|
| `elements.csv` | One row per `(element, genre)` pair: `element`, `genre`, `file_count`, `instance_count`. Sorted by `instance_count` descending. |
| `attributes.csv` | Controlled-vocabulary attribute values: `element`, `attribute`, `genre`, `value`, `count`. Covers `@type`, `@subtype`, `@unit`, `@met`, `@rend`, `@place`, `@role`, `@ident`, `@ed`, `@lang`. Up to 30 most-frequent values per `(element, attribute, genre)` triple. |
| `structure.csv` | Per-file citation structure via `StructureAuditor`: URN, genre, structural type, div subtypes, milestone units, and any structural issues. |

```bash
# Survey the full corpus (writes to survey/)
survey-corpus ../data-local/canonical-greekLit/data \
    --odd ../perseus-schemas/perseus_base.odd

# Restrict to a single genre for focused review
survey-corpus ../data-local/canonical-greekLit/data \
    --odd ../perseus-schemas/perseus_base.odd \
    --genre verse-book-line
```

---

#### `validate-corpus`

Validates every TEI file against its target Perseus RELAX NG schema using
[`jing`](https://relaxng.org/jclark/) (must be installed: `brew install
jing-trang`). Files are batched by schema family for efficiency (~5× faster
than per-file invocations). Errors are aggregated across files so systemic
gaps — elements present in the corpus but missing from the schema — rise to
the top.

```bash
validate-corpus DATA_DIR [--schema-dir DIR] [--output-dir DIR] [--odd ODD] [--genre-map CSV]
```

| Option | Description |
|---|---|
| `--schema-dir DIR` | Directory containing compiled `.rng` files (default: `../perseus-schemas`). Compile schemas first with `make -C ../perseus-schemas`. |
| `--output-dir DIR` | Where to write `rng_errors.csv` (default: `survey/`). |
| `--odd ODD` | Path to `perseus_base.odd` for genre taxonomy. |
| `--genre-map CSV` | `genres.csv`-style file used as fallback when a file has no genre annotation in `__cts__.xml`. |

**Output**

`rng_errors.csv` — one row per distinct error type:

| Column | Description |
|---|---|
| `family` | Schema family (`prose`, `verse`, or `drama`). |
| `element` | Element or attribute name extracted from the jing error message. |
| `message` | Normalized jing error (trailing `; expected …` clause stripped). |
| `instance_count` | Total occurrences across all files. |
| `file_count` | Number of distinct files where this error appears. |

```bash
# Full validation pass (compile schemas first if ODDs have changed)
make -C ../perseus-schemas

validate-corpus ../data-local/canonical-greekLit/data \
    --odd ../perseus-schemas/perseus_base.odd

# With a genre-map fallback for files not yet genre-annotated
validate-corpus ../data-local/canonical-greekLit/data \
    --odd ../perseus-schemas/perseus_base.odd \
    --genre-map genres.csv
```

---

#### Makefile targets

```bash
# Survey element/attribute vocabulary (OUT_DIR defaults to survey/)
make survey-corpus DATA_DIR=../data-local/canonical-greekLit/data
make survey-corpus DATA_DIR=../data-local/canonical-greekLit/data OUT_DIR=survey/ GENRE=verse-book-line

# Validate against target Perseus schemas
make validate-corpus DATA_DIR=../data-local/canonical-greekLit/data
make validate-corpus DATA_DIR=../data-local/canonical-greekLit/data GENRE_MAP=genres.csv
```

---

### Makefile

A `Makefile` at the project root provides convenience targets for common
batch operations. Pass `FILES="..."` and optionally `OUT=dir/`.

```bash
make help                   # list all targets

# Genre annotation (ODD defaults to ../perseus-schemas/perseus_base.odd)
make annotate-genres   DATA_DIR=../data-local/canonical-greekLit/data
make generate-genre-map DATA_DIR=../data-local/canonical-greekLit/data OUTPUT_CSV=genres.csv
make apply-genre-map   CSV_FILE=genres.csv DATA_DIR=../data-local/canonical-greekLit/data

# Pipeline
make set-genre FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml" GENRE=prose-standard
make normalize FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml" OUT=normalized/
make validate  FILES="normalized/*.xml"
make pipeline  FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml" GENRE=prose-standard OUT=normalized/

# Audit
make audit           FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml"   # all three auditors
make audit-refs      FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml" OUT=reports/
make audit-structure FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml"
make audit-schema    FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml" OUT=reports/

# Schema development
make survey-corpus    DATA_DIR=../data-local/canonical-greekLit/data OUT_DIR=survey/
make validate-corpus  DATA_DIR=../data-local/canonical-greekLit/data OUT_DIR=survey/
```

---

## XSLT stylesheets

All stylesheets are in `xslt/` and require Saxon (XSLT 2.0 via saxonche).
They use `on-no-match="shallow-copy"`, so only matched nodes are transformed.
The pipeline commands above invoke them in sequence; they can also be run
individually via `corpus-tools normalize --tei-schema` overrides.

| Stylesheet | Purpose | Parameters |
|---|---|---|
| `normalize-cts.xsl` | Remove EpiDoc `div[@type='edition']` wrappers; hoist `@subtype` to `@type` on textpart divs; strip `@xml:base` attributes | — |
| `set-cts-urn.xsl` | Set `@xml:base` on `<body>` and add `<idno type="CTS">` to `<publicationStmt>` | `cts-base` (default: auto-computed from path) |
| `add-citeStructure.xsl` | Append a genre-appropriate `<refsDecl>` with `<citeStructure>` to `<encodingDesc>` | `genre` (`prose`\|`verse`\|`drama`) |
| `fix-verse.xsl` | Convert `@ana`-encoded meter values to `@met`; strip placeholder `met="u"/"U"` | — |
| `set-schema.xsl` | Update the `<?xml-model?>` PI to point to a Perseus schema (.rng) | `tei-schema` (default: `perseus_base`) |
| `set-genre.xsl` | Add `<catRef scheme="#perseus-genre">` to `<profileDesc>` | `genre` |

`set-cts-urn.xsl` derives the CTS URN from the document's filesystem path when
`cts-base` is not supplied. It expects the path to follow the Perseus convention:
`canonical-{namespace}/data/{author}/{work}/{filename}.xml`.

---

## Schematron schemas

Two schemas live in `schematron/`:

| Schema | Purpose |
|---|---|
| `perseus_normalized.sch` | Validates that all pipeline steps have been applied (genre, CTS URN, citeStructure, schema PI). Used by `corpus-tools validate`. |
| `perseus_encoding.sch` | Advisory checks for encoding anomalies requiring human review before correction (e.g. empty `<s/>` used as a milestone). Used by `audit-schema`. |

---

## Auditors (programmatic API)

The `auditors` package provides an object-oriented API for document inspection,
used by the audit commands and available for scripting. See
[`src/auditors/README.md`](src/auditors/README.md).
