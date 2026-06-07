# auditors

Programmatic inspection tools for Perseus TEI documents. Each auditor
takes a `TEIDocument`, runs a set of checks or rules, and returns a
structured report with `render_text()` and `to_json()` methods.

The audit CLI commands (`audit-refs`, `audit-structure`, `audit-schema`)
are thin wrappers around this package.

---

## Auditor classes

### `ReferenceAuditor`

Checks citation reference declarations.

```python
from tei import TEIDocument
from auditors import ReferenceAuditor

doc = TEIDocument("tlg0003.tlg001.perseus-grc2.xml")
report = ReferenceAuditor(doc).audit()
print(report.render_text())
```

**Report fields:** `path`, `base_urn`, `refsDecl_count`, `refsDecl_ids`,
`refsDecl_has_cite_structure`, `has_cite_structures`, `has_default_refsDecl`, `issues`.

**Rules applied:**

| ID | Role | Check |
|---|---|---|
| `REF001` | warning | `<body>/@xml:base` is absent or not a CTS URN |
| `REF002` | info | No `<citeStructure>` found (legacy `<cRefPattern>` only) |
| `REF003` | warning | No `<refsDecl default="true">` present |

**Helper methods** (also available independently):
`doc_has_refsDecls()`, `doc_has_cite_structures()`,
`doc_has_default_refsDecl()`, `default_refsDecl_is_citeStructure()`.

---

### `StructureAuditor`

Introspects the document's `<div type="textpart">` hierarchy and
`<milestone>` elements.

```python
from auditors import StructureAuditor

report = StructureAuditor(doc).audit()
print(report.render_text())
```

**Report fields:** `path`, `base_urn`, `structural_type`, `citation_levels`
(list of `CitationLevel`), `milestones` (list of `MilestoneInfo`),
`cref_patterns`, `issues`, `proposed_cite_structure`.

`structural_type` is one of `"div-based"`, `"milestone-based"`, `"mixed"`,
or `"unknown"`.

`proposed_cite_structure` is an advisory XML fragment suggesting a
`<refsDecl>` based on the observed div hierarchy.

**Rules applied:**

| ID | Role | Check |
|---|---|---|
| `STR001` | warning | No `<div type="textpart">` or `<milestone>` found |
| `STR002` | info | Both divs and milestones present (mixed structure) |
| `STR003` | warning | Any `<div type="textpart">` lacks `@n` |
| `STR004` | warning | Any `<div type="textpart">/@xml:base` does not start with the document's base URN |

---

### `SchematronAuditor`

Runs a Schematron schema against the document and reports all findings,
including advisory warnings and info messages.

```python
from pathlib import Path
from auditors import SchematronAuditor

sch = Path("schematron/perseus_encoding.sch")
report = SchematronAuditor(doc, sch).audit()
print(report.render_text())
```

**Report fields:** `path`, `sch_path`, `findings` (list of
`SchematronAuditFinding`).

Each finding has `kind` (`"failed-assert"` or `"successful-report"`),
`role` (`"error"`, `"warning"`, `"info"`, or `""`), `location`, `test`,
and `message`.

**Filter methods:** `report.errors()`, `report.warnings()`.

Unlike `corpus-tools validate`, which exits non-zero on any hard failure,
`SchematronAuditor` captures all findings regardless of role. Use it for
advisory review; use `validate` as a pipeline gate.

---

## Rule-based auditing (`RuleAuditor`)

`RuleAuditor` is the underlying engine used by `ReferenceAuditor` and
`StructureAuditor`. Use it directly to compose custom rule sets.

```python
from auditors import RuleAuditor, audit_rule
from auditors.rule_auditor import RuleAuditFinding

@audit_rule("CUSTOM001", role="warning")
def check_has_title(doc):
    titles = doc.root.xpath("//tei:titleStmt/tei:title", namespaces=NS)
    if not titles:
        return RuleAuditFinding(
            rule_id="CUSTOM001",
            role="warning",
            message="No <title> found in <titleStmt>.",
        )
    return None

report = RuleAuditor(doc, [check_has_title]).audit()
```

A rule function takes a `TEIDocument` and returns one of:
- `None` — no finding
- `RuleAuditFinding` — a single finding
- `list[RuleAuditFinding]` — multiple findings

The `@audit_rule(rule_id, role)` decorator attaches metadata (`_rule_id`,
`_role`) to the function; it does not alter the calling signature.

**Report fields:** `path`, `findings`.
**Filter methods:** `report.errors()`, `report.warnings()`, `report.infos()`.

---

## Base class

All auditors extend `Auditor[T]` from `auditor.py`:

```python
class Auditor(ABC, Generic[T]):
    def __init__(self, doc: TEIDocument) -> None: ...
    @abstractmethod
    def audit(self) -> T: ...
```

`SchematronAuditor` takes an additional `sch_path: Path` argument;
`RuleAuditor` takes `rules: list[Callable]`.
