# auditors — retained for reference

This module was brought over from MinimumViablePerseus. Its original purpose was
to help survey the state of the corpus before normalization: does a text have a
`refsDecl`? What is its `div` structure? What milestones are present?

## Why it is no longer the primary tool

The normalization pipeline (`pipeline.py`) and genre taxonomy (`perseus_base.odd`)
now handle most of what the auditors were designed to do:

| Auditor concern | Now handled by |
|---|---|
| Does the text have a `refsDecl n="CTS"` with `citeStructure`? | `add-citeStructure.xsl` adds one as part of every pipeline run |
| Does `body` carry `@xml:base` with the CTS URN? | `set-cts-urn.xsl` sets it |
| Does `publicationStmt` have `<idno type="CTS">`? | `set-cts-urn.xsl` sets it |
| What is the div/citation structure? | The genre taxonomy (`#perseus-genre`) encodes this editorially via `set-genre.xsl`; the appropriate `citeStructure` is then selected automatically |
| Does the document point to a Perseus schema? | `set-schema.xsl` sets the `<?xml-model?>` PI |

Post-pipeline validation is being replaced by **Schematron rules** embedded in
or alongside the ODD schemas. Schematron can express the invariants that RELAX NG
cannot (e.g. "every document must have a `catRef` in `profileDesc`"), and runs
directly in Oxygen against any open document.

## Status of the classes

- **`Auditor`** (`auditor.py`) — abstract base; retained.
- **`ReferenceAuditor`** (`reference_auditor.py`) — complete; checks for CTS URN,
  `citeStructure`, and `refsDecl default`. The checks it performs overlap
  significantly with the Schematron rules being developed.
- **`StructureAuditor`** (`structure_auditor.py`) — report dataclass only; the
  auditor class was never implemented. The `proposed_cite_structure` field in the
  report is now obsolete: that decision is made editorially via the genre taxonomy.

## Retention rationale

Kept as reference for the analytical approach and the `render_text()` / `to_json()`
reporting patterns, which may inform future corpus-wide batch reporting tools.
