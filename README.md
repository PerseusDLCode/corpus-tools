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
`normalize`.

```bash
corpus-tools set-genre FILE [FILE ...] --genre GENRE [-o PATH]
```

Valid genres: `prose-historiography`, `prose-philosophy`, `prose-dialogue`,
`prose-oratory`, `prose-biography`, `prose-epistolary`, `prose-geography`,
`verse-epic`, `verse-didactic`, `verse-elegiac`, `verse-lyric-choral`,
`verse-lyric-pindaric`, `verse-lyric-monodic`, `verse-satiric`,
`verse-epigram`, `verse-iambic`, `attic-tragedy`, `attic-comedy`,
`roman-comedy`, `roman-tragedy`, `early-modern-drama`.

```bash
# Annotate in-place
corpus-tools set-genre tlg0003.tlg001.1st1K-eng1.xml --genre prose-historiography

# Annotate a batch, writing into a separate directory
corpus-tools set-genre -o annotated/ canonical-greekLit/data/tlg0003/tlg001/*.xml \
    --genre prose-historiography
```

#### `normalize`

Runs a genre-appropriate XSLT pipeline on a genre-annotated document. The
genre must already be set (via `set-genre` or manually).

```bash
corpus-tools normalize FILE [FILE ...] [-o PATH] [--cts-base URN] [--tei-schema NAME]
```

| Option | Description |
|---|---|
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
corpus-tools normalize tlg0003.tlg001.1st1K-eng1.xml

# Full workflow: annotate then normalize into a separate directory
corpus-tools set-genre --genre prose-historiography tlg0003.tlg001.1st1K-eng1.xml
corpus-tools normalize -o normalized/ tlg0003.tlg001.1st1K-eng1.xml
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

### Makefile

A `Makefile` at the project root provides convenience targets for common
batch operations. Pass `FILES="..."` and optionally `OUT=dir/`.

```bash
make help                   # list all targets

# Pipeline
make set-genre FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml" GENRE=prose-historiography
make normalize FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml" OUT=normalized/
make validate  FILES="normalized/*.xml"
make pipeline  FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml" GENRE=prose-historiography OUT=normalized/

# Audit
make audit          FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml"         # all three auditors
make audit-refs     FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml" OUT=reports/
make audit-structure FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml"
make audit-schema   FILES="canonical-greekLit/data/tlg0003/tlg001/*.xml" OUT=reports/
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
