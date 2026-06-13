from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree

from genres import GenreTaxonomy, load as load_genres

def _load_dotenv() -> None:
    """Load ANTHROPIC_API_KEY from the project-root .env without requiring python-dotenv."""
    import os
    root = Path(__file__).parent.parent.parent  # src/commands -> src -> project root
    env_file = root / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip()


_CTS_NS = "http://chs.harvard.edu/xmlns/cts"
_TEI_NS = "http://www.tei-c.org/ns/1.0"
_XML_NS = "http://www.w3.org/XML/1998/namespace"
_CTS = {"ti": _CTS_NS}
_TEI = {"tei": _TEI_NS}


# ---------------------------------------------------------------------------
# Structural signal extraction
# ---------------------------------------------------------------------------

@dataclass
class StructuralSignals:
    sp_count: int = 0
    l_count: int = 0
    p_count: int = 0
    div_types: list[str] = field(default_factory=list)

    def inferred_family(self) -> str | None:
        if self.sp_count > 0:
            return "drama"
        if self.l_count > 0 and self.l_count > self.p_count:
            return "verse"
        if self.p_count > 0:
            return "prose"
        return None


def gather_signals(work_dir: Path) -> StructuralSignals:
    signals = StructuralSignals()
    for xml_file in sorted(work_dir.glob("*.xml")):
        if xml_file.name == "__cts__.xml":
            continue
        try:
            tree = etree.parse(str(xml_file))
        except etree.XMLSyntaxError:
            continue
        signals.sp_count += len(tree.xpath("//tei:sp", namespaces=_TEI))
        signals.l_count += len(tree.xpath("//tei:l | //tei:lg", namespaces=_TEI))
        signals.p_count += len(tree.xpath("//tei:text//tei:p", namespaces=_TEI))
        for div_type in tree.xpath("//tei:div/@type", namespaces=_TEI):
            t = str(div_type)
            if t not in signals.div_types:
                signals.div_types.append(t)
    return signals


# ---------------------------------------------------------------------------
# CTS metadata helpers
# ---------------------------------------------------------------------------

def read_groupname(textgroup_cts: Path) -> str:
    try:
        tree = etree.parse(str(textgroup_cts))
        names = tree.xpath("//ti:groupname", namespaces=_CTS)
        return names[0].text.strip() if names and names[0].text else ""
    except Exception:
        return ""


def read_work_metadata(work_cts: Path) -> tuple[str, str]:
    """Return (title, first_english_description) from a work __cts__.xml."""
    try:
        tree = etree.parse(str(work_cts))
    except Exception:
        return "", ""

    titles = tree.xpath("//ti:title", namespaces=_CTS)
    title = titles[0].text.strip() if titles and titles[0].text else ""

    eng_descs = tree.xpath(
        "//ti:description[@xml:lang='eng'] | //ti:description[@xml:lang='mul']",
        namespaces={"ti": _CTS_NS, "xml": _XML_NS},
    )
    description = eng_descs[0].text.strip() if eng_descs and eng_descs[0].text else ""
    return title, description


# ---------------------------------------------------------------------------
# ODD genre description extraction
# ---------------------------------------------------------------------------

def load_genre_descriptions(odd_path: Path) -> dict[str, str]:
    """Return {genre_id: catDesc_text} for all leaf genres in the ODD."""
    tree = etree.parse(str(odd_path))
    ns = {"tei": _TEI_NS, "xml": _XML_NS}
    results = tree.xpath("//tei:taxonomy[@xml:id='perseus-genre']", namespaces=ns)
    if not results:
        return {}
    descriptions: dict[str, str] = {}
    for cat in results[0].xpath(".//tei:category[not(tei:category)]", namespaces=ns):
        cid = cat.get(f"{{{_XML_NS}}}id")
        desc_el = cat.find(f"{{{_TEI_NS}}}catDesc")
        if cid and desc_el is not None and desc_el.text:
            descriptions[cid] = " ".join(desc_el.text.split())
    return descriptions


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def build_prompt(
    author: str,
    title: str,
    description: str,
    signals: StructuralSignals,
    taxonomy: GenreTaxonomy,
    descriptions: dict[str, str],
) -> str:
    genre_lines = "\n".join(
        f"  {gid}: {descriptions.get(gid, '')}"
        for gid in sorted(taxonomy.valid)
    )
    parts = [
        f"Author: {author or 'unknown'}",
        f"Title: {title or 'unknown'}",
    ]
    if description:
        parts.append(f"Description: {description}")
    parts += [
        "",
        "Structural signals from the TEI encoding:",
        f"  speech/speaker elements (sp, speaker): {signals.sp_count}",
        f"  verse line elements (l, lg): {signals.l_count}",
        f"  paragraph elements in body (p): {signals.p_count}",
        f"  div @type values: {', '.join(signals.div_types) or 'none'}",
        "",
        "Valid genre ids (id: description):",
        genre_lines,
        "",
        "Respond with exactly one genre id from the list above, nothing else.",
    ]
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Confidence
# ---------------------------------------------------------------------------

def compute_confidence(
    genre: str, signals: StructuralSignals, taxonomy: GenreTaxonomy
) -> str:
    if genre not in taxonomy.valid:
        return "low"
    structural = signals.inferred_family()
    if structural is None:
        return "medium"
    return "high" if taxonomy.family(genre) == structural else "medium"


# ---------------------------------------------------------------------------
# Writing back to __cts__.xml
# ---------------------------------------------------------------------------

def write_genre(work_cts: Path, genre: str, confidence: str) -> None:
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(work_cts), parser)
    root = tree.getroot()

    # Remove any existing ti:genre element
    for old in root.findall(f"{{{_CTS_NS}}}genre"):
        root.remove(old)

    genre_el = etree.SubElement(root, f"{{{_CTS_NS}}}genre")
    genre_el.set("confidence", confidence)
    genre_el.text = genre

    tree.write(
        str(work_cts),
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True,
    )


# ---------------------------------------------------------------------------
# Per-work annotation
# ---------------------------------------------------------------------------

def annotate_work(
    work_cts: Path,
    client,
    taxonomy: GenreTaxonomy,
    descriptions: dict[str, str],
    model: str,
    dry_run: bool,
) -> tuple[str, str] | None:
    """Annotate one work. Returns (genre, confidence), or None if already annotated."""
    tree = etree.parse(str(work_cts))
    existing = tree.xpath("//ti:genre", namespaces=_CTS)
    if existing:
        return None  # already annotated, skip

    textgroup_cts = work_cts.parent.parent / "__cts__.xml"
    author = read_groupname(textgroup_cts)
    title, description = read_work_metadata(work_cts)
    signals = gather_signals(work_cts.parent)

    prompt = build_prompt(author, title, description, signals, taxonomy, descriptions)

    response = client.messages.create(
        model=model,
        max_tokens=64,
        system=(
            "You are a classical scholar classifying ancient texts by genre. "
            "Respond with exactly one genre id from the provided list, nothing else."
        ),
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip().rstrip(".")

    genre = raw if raw in taxonomy.valid else "unknown"
    confidence = compute_confidence(genre, signals, taxonomy)

    if not dry_run:
        write_genre(work_cts, genre, confidence)

    return genre, confidence


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _work_urn(work_cts: Path) -> str:
    try:
        root = etree.parse(str(work_cts)).getroot()
        return root.get("urn") or str(work_cts)
    except Exception:
        return str(work_cts)


def _is_work_level(path: Path, data_dir: Path) -> bool:
    """True if path is at depth textgroup/work/__cts__.xml relative to data_dir."""
    try:
        parts = path.relative_to(data_dir).parts
        return len(parts) == 3
    except ValueError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="annotate-genres",
        description=(
            "Suggest genres for CTS works via the Claude API and write "
            "<ti:genre> to each work-level __cts__.xml. "
            "Resumable: files already annotated are skipped."
        ),
    )
    parser.add_argument(
        "data_dir", type=Path, metavar="DATA_DIR",
        help="Root data directory (e.g. canonical-greekLit/data).",
    )
    parser.add_argument(
        "--odd", required=True, type=Path, metavar="ODD",
        help="Path to perseus_base.odd (authoritative genre taxonomy).",
    )
    parser.add_argument(
        "--model", default="claude-haiku-4-5-20251001", metavar="MODEL",
        help="Claude model id (default: claude-haiku-4-5-20251001).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print suggestions without writing to disk.",
    )
    args = parser.parse_args()

    try:
        import anthropic
    except ImportError:
        print(
            "ERROR: anthropic package not installed. Run: uv add anthropic",
            file=sys.stderr,
        )
        sys.exit(1)

    _load_dotenv()

    taxonomy = load_genres(args.odd)
    descriptions = load_genre_descriptions(args.odd)
    client = anthropic.Anthropic()

    work_files = sorted(
        p for p in args.data_dir.rglob("__cts__.xml")
        if _is_work_level(p, args.data_dir)
    )

    total = len(work_files)
    annotated = skipped = errors = 0

    for work_cts in work_files:
        urn = _work_urn(work_cts)
        try:
            result = annotate_work(
                work_cts, client, taxonomy, descriptions, args.model, args.dry_run
            )
            if result is None:
                skipped += 1
            else:
                genre, confidence = result
                prefix = "[dry-run] " if args.dry_run else ""
                print(f"{prefix}{urn} → {genre} ({confidence})")
                annotated += 1
        except Exception as exc:
            print(f"ERROR: {urn}: {exc}", file=sys.stderr)
            errors += 1

    label = "would annotate" if args.dry_run else "annotated"
    print(
        f"\nDone. {annotated} {label}, {skipped} already done, "
        f"{errors} errors. Total: {total}.",
        file=sys.stderr,
    )
    sys.exit(errors)


if __name__ == "__main__":
    main()
