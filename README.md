# Setup

```bash
pdm install
```

# Tools
1. [analyze-milestones]](#analyze-milestones)





## analyze-milestones

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
