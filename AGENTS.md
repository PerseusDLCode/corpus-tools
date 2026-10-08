# Project Overview

corpus-tools is a Python CLI toolkit for normalizing and auditing Perseus TEI corpora. It converts raw TEI-P5 files (often in older EpiDoc encoding) into the Perseus standard: CTS URN on `<body>`, genre-appropriate `<citeStructure>` in `<encodingDesc>`, and a `<?xml-model?>` PI pointing to the target RELAX NG schema.

## Setup

```bash
pdm install   # or: uv sync
```

All entry-point commands land in `.venv/bin/`. Use `corpus-tools` as the main entry point — **not** `pdm run set-genre` (that silently fails).

## Commands

- `corpus-tools set-genre / normalize / validate` — per-file pipeline
- `annotate-genres` — Codex API batch genre suggestion
- `generate-genre-map` — emit review CSV
- `apply-genre-map` — apply reviewed CSV to files
- `audit-refs / audit-structure / audit-schema` — read-only inspection
- `survey-corpus / validate-corpus` — schema development support
- `globe-lineation regenerate / verify / manifest / smoke` — Globe Shakespeare lineation from the witness pages (`make globe-regenerate PLAY=lr`, `make globe-verify PLAY=lr`); see below

## Key conventions

### Genre taxonomy

The `perseus-genre` taxonomy is **citation-structure-based**, not literary genre. Valid ids are structural subclasses: `prose-standard`, `prose-book-chapter`, `prose-section`, `verse-stichic`, `verse-book-line`, `drama-act-scene-line`, etc. The full list is in `../perseus-schemas/perseus_base.odd`.

Bare family names (`prose`, `verse`, `drama`) are also legal catRef targets — they mean "family default applied, needs review."

When adding a new subclass, **also update `$valid-genres` in `schematron/perseus_normalized.sch`** or the Schematron gate will reject newly normalized files.

### `--odd` is always required

All genre-aware commands take `--odd PATH_TO_perseus_base.odd`. There is no hardcoded default in the commands themselves. The Makefile default is `../perseus-schemas/perseus_base.odd`.

### `--cts-base` for csel-dev and First1KGreek

Pre-normalization files in csel-dev and First1KGreek store the CTS URN on `div[@type='edition']/@n` (not `body/@xml:base`). The pipeline's `read_existing_cts_urn` reads `body/@xml:base` and will miss it. Always pass `--cts-base URN` explicitly when normalizing these files.

### Corpus data locations

All corpus forks live in `/Users/wulfmanc/repos/gh/PerseusDLCode/data-local/`:
- `canonical-greekLit` — Greek literary texts
- `canonical-latinLit` — Latin literary texts
- `First1KGreek` — First 1K Years of Greek project
- `csel-dev` — Corpus Scriptorum Ecclesiasticorum Latinorum
- `canonical_pdlrefwk` — reference works

Each fork uses `editing` as the long-running integration branch.

### Test suite

```bash
pdm run test        # or: .venv/bin/pytest
```

357 tests (as of 2026-06-13). Tests live in `tests/`. No mocking of external tools — integration tests call real XSLT via saxonche.

## Globe lineation (`src/globe/`)

Regenerates a play's Globe line numbering from page images of the printed Globe. Design, tables and how to run it: `doc/globe-lineation.org`; witness provenance: `doc/witnesses.org`. Moved from `globe-lineation-workshop`, frozen at its tag `v1.0`; `doc/agenda.org #id` and `doc/forum.org #id` in this code refer to that workshop, not to files here. Open tasks are in canonical-engLit `doc/agenda.org` on `mvp`.

- `make globe-verify PLAY=lr` — build to a temp dir and compare with canonical-engLit's published file, ignoring only the regeneration stamp. Run it after any change to `src/globe/`.
- `make globe-regenerate PLAY=lr` — writes `out/globe/lr/` and `reports/globe/`; **refuses on a dirty tree**. The canonical build (`out/globe/*/*.globe.xml`) is gitignored: its home is canonical-engLit.
- Sibling inputs: `../canonical-engLit` (P4 sources and the published edition, which is also the shell of the next build), the witnesses, the `PerseusDLCode/globe-witnesses` repository, at `$GLOBE_WITNESSES` (default `../globe-witnesses`; never commit its `Doubleday/`; pinned by `data/globe/witness-manifest.tsv`, and the build refuses a file that differs), `../schmidt-lexicon-workshop/out/` (the Schmidt check, which regenerate runs on every build it writes: a report, never a gate), the ShakeDraCor clone at `$SHAKEDRACOR` (default `../../shakedracor`; Folger report only, skipped if absent; the play's file is pinned by the manifest too, with its commit, and the header cites the Folger from that row).
- **canonical-engLit: `mvp` only.** The build refuses unless canonical-engLit has `mvp` checked out. Work only in the `PerseusDLCode` fork (`origin`), from `mvp`; never commit to, branch from, merge into or compare against its `main`, and never push to `upstream`.
- A play's P4 source, shell, printed pages and DraCor file are its row in `data/globe/plays.tsv` (`src/globe/plays.py`); name them nowhere else.
- `shared-lines.tsv`'s `checked` column is filled by Cliff after looking at the page image; never fill it. The canonical build refuses unchecked rows.
- Byte identity depends on serialisation: keep lxml at the locked 6.1.3.

## Related repos (siblings)

- `../perseus-schemas` — TEI ODDs compiled to RELAX NG; `make` there recompiles `.rng` files
- `../data-local/` — corpus data (see above)
