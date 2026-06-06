# Setup

```bash
pdm install
```

# Tools

1. [analysis](#analysis)
2. [transformers](#transformers)

---

## analysis

### analyze-milestones

Traverse a TEI corpus and compile per-document JSON reports on `<milestone>`,
`<div>`, and structural element usage.

```bash
pdm run analyze-milestones --source_dir data/canonical-greekLit --output_dir milestone-reports/
```

Each output file (`<stem>.json`) contains:

```json
{
  "filename": "tlg0011.tlg001.perseus-grc2",
  "milestones": [{"unit": "card", "frequency": 42}],
  "divs": [
    {"div_type": "textpart", "subtypes": [{"subtype": "book", "frequency": 3}]}
  ]
}
```

---

## transformers

### stylesheets

All stylesheets are in `xslt/` and require Saxon (XSLT 4.0). They use
`on-no-match="shallow-copy"`, so only matched nodes are transformed.

| Stylesheet | Purpose | Parameters |
|---|---|---|
| `normalize-cts.xsl` | Remove EpiDoc `div[@type='edition']` wrappers; hoist `@subtype` to `@type` on textpart divs; strip `@xml:base` attributes | — |
| `set-cts-urn.xsl` | Set `@xml:base` on `<body>` and add `<idno type="CTS">` to `<publicationStmt>` | `cts-base` (default: auto-computed from path) |
| `add-citeStructure.xsl` | Append a genre-appropriate `<refsDecl>` to `<encodingDesc>` | `genre` (`prose`\|`verse`\|`drama`, default: `prose`) |
| `fix-verse.xsl` | Convert `@ana`-encoded meter values to `@met`; strip placeholder `met="u"/"U"` | — |
| `set-schema.xsl` | Update the `<?xml-model?>` PI to point to a Perseus schema | `tei-schema` (default: `perseus_base`), `schema-path-base` |

`set-cts-urn.xsl` derives the CTS URN from the document's filesystem path when
`cts-base` is empty. It expects the path to follow the Perseus convention:
`canonical-{namespace}/data/{author}/{work}/{filename}.xml`, where the filename
encodes the full CTS work identifier (e.g. `tlg0003.tlg001.1st1K-eng1`).

### command-line pipelines

`corpus-tools` provides three named pipelines that chain the stylesheets above.
Install with `pdm install`, then run via `pdm run corpus-tools` (or `corpus-tools`
with the virtualenv activated).

```
corpus-tools {normalize-prose|normalize-verse|normalize-drama} [OPTIONS] FILE [FILE ...]
```

**Pipelines:**

| Pipeline | Steps |
|---|---|
| `normalize-prose` | normalize-cts → set-cts-urn → add-citeStructure(prose) → set-schema(perseus_prose) |
| `normalize-verse` | normalize-cts → set-cts-urn → add-citeStructure(verse) → fix-verse → set-schema(perseus_verse) |
| `normalize-drama` | normalize-cts → set-cts-urn → add-citeStructure(drama) → set-schema(perseus_drama) |

**Options:**

| Option | Description |
|---|---|
| `-o PATH` | Output file (single input) or directory (batch). Default: overwrite in-place. |
| `--cts-base URN` | Override auto-computed CTS URN (e.g. for `pdlrefwk` texts). |
| `--tei-schema NAME` | Override the schema name written into the `<?xml-model?>` PI. |

**Examples:**

```bash
# Normalize a single prose file in-place
corpus-tools normalize-prose canonical-greekLit/data/tlg0003/tlg001/tlg0003.tlg001.1st1K-eng1.xml

# Normalize a verse file, writing output separately
corpus-tools normalize-verse -o /tmp/out.xml canonical-greekLit/data/tlg0012/tlg001/tlg0012.tlg001.perseus-grc2.xml

# Batch-normalize all Latin prose files into a separate directory
corpus-tools normalize-prose -o normalized/ canonical-latinLit/data/**/*.xml

# Override URN for a reference work
corpus-tools normalize-prose --cts-base urn:cts:pdlrefwk:viaf88890045.phi001.perseus-eng1 myfile.xml
```
