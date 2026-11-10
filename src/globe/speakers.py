"""A play's speakers: data/globe/speakers.tsv.

Who speaks is data, kept apart from the Dramatis Personae the Globe prints
(DraCor, LEMDO): each speaker id the P4 gives in <sp who> becomes a
<person> or <personGrp> in <profileDesc>/<particDesc>/<listPerson>, which
<sp who="#id"> points to, and the printed roles in <front>/<castList> point
to their speakers with @corresp. The table says, for each id, what it is, its
name, and the printed role it is (if any).

Most P4s put the id on the printed <role> itself: those rows are the P4's
own statement (basis `p4`) and need no check. A few (1H4, 2H4, AWW, R2 and
parts of JC and Shrew) list the ids as empty <role/>s beside a printed list
without ids; for those, propose() matches the speaker labels against the
printed roles (basis `label`), or finds none (basis `none`). Such a row is
a proposal: Cliff fills `checked`, and the canonical build refuses a row
that is still empty. `kind` is proposed from the name (All, Lords, Citizens:
personGrp) and is part of what is checked.

    python -m globe.speakers [PLAY ...]   # propose rows; checked rows are kept
"""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from dataclasses import dataclass, fields
from pathlib import Path

from lxml import etree

from globe import p4_convert, plays

TEI = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
REPO = Path(__file__).resolve().parent.parent.parent
TABLE = REPO / "data/globe/speakers.tsv"
CORPUS = REPO.parent / "canonical-engLit"

COLUMNS = ["play", "id", "kind", "name", "role", "role_n", "basis", "checked", "note"]
KINDS = ("person", "personGrp")
BASES = ("p4", "label", "none")
HEADER = """\
# The speakers of each Globe play (src/globe/speakers.py): one row per id the
# P4 gives in <sp who>. kind: person or personGrp. name: for <persName> (or
# <name> in a group). role: the printed <role>, as the P4 has it, that this
# speaker is (empty if the Dramatis Personae does not list it); role_n: which
# role of that text (1H4 prints HENRY PERCY twice), 1 if only one. basis: p4 (the
# P4 put the id on that role), label (matched by speaker label), none.
# `checked` is filled by Cliff for label and none rows; the canonical build
# refuses one that is empty. Rows with basis p4 are checked "p4".
"""

GROUP_WORDS = {
    "all", "both", "lords", "citizens", "servants", "servingmen", "soldiers", "senators",
    "attendants", "others", "gentlemen", "ladies", "officers", "musicians", "watch", "guards",
    "conspirators", "tribunes", "people", "commons", "captains", "murderers", "witches",
    "fairies", "outlaws", "players", "apparitions", "lovers", "plebeians", "volsces",
    "romans", "goths", "sailors", "mariners", "messengers", "keepers", "huntsmen", "pages",
    "rebels", "nobles", "knights", "courtiers", "spirits", "shepherds", "masquers",
    "thieves", "travellers", "gardeners", "chorus",
}


class SpeakerError(Exception):
    """The table and the play disagree."""


@dataclass
class Row:
    play: str
    id: str
    kind: str
    name: str
    role: str
    role_n: str
    basis: str
    checked: str = ""
    note: str = ""

    @property
    def pending(self) -> bool:
        return not self.checked.strip()


def text(el) -> str:
    """An element's words, the P4's entity references resolved as the
    conversion resolves them (p4_convert.ENTITY_MAP: &AElig;geon -> Ægeon)."""
    parts: list[str] = []

    def walk(e):
        if isinstance(e, etree._Entity):
            parts.append(p4_convert.ENTITY_MAP.get(e.name, f"&{e.name};"))
        elif isinstance(e.tag, str) and e.text:
            parts.append(e.text)
        if isinstance(e.tag, str):
            for c in e:
                walk(c)
                if c.tail:
                    parts.append(c.tail)
    walk(el)
    return " ".join("".join(parts).split())


def clean_name(s: str) -> str:
    """The name a printed role or a label gives: before the first comma, its
    words in capitals set in title case ("HAMLET, son to the late" -> Hamlet;
    "Sir John FALSTAFF" -> Sir John Falstaff), a label's period dropped."""
    s = s.split(",")[0].strip().rstrip(".").strip()
    words = [w.capitalize() if w.isupper() and len(w) > 1 else w for w in s.split()]
    return " ".join(w.lower() if k and w.lower() in SMALL_WORDS else w for k, w in enumerate(words))


SMALL_WORDS = {"of", "the", "and", "to", "on", "in", "at", "with", "de", "du", "la", "le"}
TITLES = {"lady", "duchess", "queen", "countess", "mistress", "princess"}
NUMBERS = {"two", "three", "four", "five", "six", "several", "divers", "sundry", "many"}


def is_group(name: str) -> bool:
    """All, Lords, two Gardeners, Travellers, Ferdinand and Miranda: a group
    word (GROUP_WORDS), a number, or two names joined. Only listed words count, so that a name like Cassius or Pericles
    is not taken for a plural."""
    words = re.findall(r"[a-z]+", name.lower())
    return bool(words) and (words[0] in GROUP_WORDS or words[-1] in GROUP_WORDS
                            or words[0] in NUMBERS or "and" in words[1:])


def _label_words(label: str) -> list[str]:
    return [w for w in re.findall(r"[a-z]+", label.lower()) if w not in ("of", "the", "and")]


def _matches(lw: list[str], words: list[str]) -> bool:
    """Every label word begins a word of `words`, in order."""
    j = 0
    for w in words:
        if j < len(lw) and w.startswith(lw[j]):
            j += 1
    return j == len(lw)


def candidates(label: str, printed: list[str]) -> list[tuple[tuple, int]]:
    """The printed roles a speaker label could name, best first. Every word of
    the label must begin a word of the role, in order ("Count." COUNTESS of
    Rousillon; "Sec. Hun." Second Huntsman). Better: a match in the name,
    before the first comma (QUEEN to King Richard for "Queen."); more label
    words matched whole ("Wart." WART); a match at the role's first word, or
    else earlier in it (Lord Chief-Justice for "Ch. Just.", not A Servant of
    the Chief-Justice); then the shorter role (Gentleman, not First
    Gentleman)."""
    lw = _label_words(label)
    out = []
    for i, role in enumerate(printed):
        if not lw or not role:
            continue
        head = re.findall(r"[a-z]+", role.split(",")[0].lower())
        allw = re.findall(r"[a-z]+", role.lower())
        words = head if _matches(lw, head) else allw if _matches(lw, allw) else None
        if words is None:
            continue
        first = next(k for k, w in enumerate(words) if w.startswith(lw[0]))
        exact = sum(1 for w in lw if w in words)
        # "Mort." is Edmund Mortimer, not LADY MORTIMER: a role that opens with a
        # woman's title wants the label to say it
        titled = int(not (head and head[0] in TITLES and not lw[0].startswith(head[0][:3])))
        out.append(((int(words is head), exact, titled, -first, -len(words)), i))
    out.sort(key=lambda x: x[0], reverse=True)
    return out


def p4_cast(p4_root):
    """The P4's cast list (in <front> or in the body's cast division)."""
    cast = p4_root.find(".//div1[@n='cast']")
    if cast is None or cast.find("castList") is None:
        raise SpeakerError("no cast division with a castList in the P4")
    return cast


def propose(play: str) -> list[Row]:
    p4 = p4_convert.parse_p4(CORPUS / plays.get(play).p4)
    roles = list(p4_cast(p4).iter("role"))
    labels: dict[str, Counter] = {}
    for sp in p4.iter("sp"):
        lab = sp.find("speaker")
        for who in (sp.get("who") or "").split():
            labels.setdefault(who, Counter())[text(lab) if lab is not None else ""] += 1
    printed = [text(r) for r in roles if text(r) and not r.get("id")]
    # what a label is matched against: the role with its description, which
    # may hold the name the label abbreviates (HENRY PERCY / surnamed HOTSPUR)
    described = [text(r.getparent()) if r.getparent().tag == "castItem" else text(r)
                 for r in roles if text(r) and not r.get("id")]
    order = [r.get("id") for r in roles if r.get("id")] + [w for w in labels if w not in
                                                           {r.get("id") for r in roles}]
    by_id = {r.get("id"): text(r) for r in roles if r.get("id")}

    def label_of(rid):
        return labels[rid].most_common(1)[0][0] if rid in labels else ""

    # Placeholders claim printed roles most specific label first: more words,
    # then fewer candidates ("Lady N." before "North.", "Wart." before "War.").
    cands = {rid: candidates(label_of(rid), described) for rid in order if not by_id.get(rid)}
    claim: dict[str, tuple[int, list[int]]] = {}
    taken: set[int] = set()
    for rid in sorted(cands, key=lambda r: (-len(_label_words(label_of(r))), len(cands[r]))):
        free = [i for _, i in cands[rid] if i not in taken]
        if free:
            taken.add(free[0])
            claim[rid] = (free[0], [i for _, i in cands[rid] if i != free[0]])
    # which role of its text each speaker is: by id where the P4 put it on the
    # role, by position among the printed roles where a label claimed it
    occurrence: dict[int, int] = {}
    seen: Counter = Counter()
    for k, r in enumerate(roles):
        if text(r):
            seen[text(r)] += 1
            occurrence[k] = seen[text(r)]
    unid = [k for k, r in enumerate(roles) if text(r) and not r.get("id")]
    role_n = {r.get("id"): occurrence[k] for k, r in enumerate(roles) if r.get("id") and text(r)}
    for rid, (i, _) in claim.items():
        role_n[rid] = occurrence[unid[i]]
    rows: list[Row] = []
    for rid in order:
        label = label_of(rid)
        others: list[int] = []
        if by_id.get(rid):
            role, basis, checked = by_id[rid], "p4", "p4"
            name = clean_name(role)
        else:
            if rid in claim:
                i, others = claim[rid]
                role, basis, name = printed[i], "label", clean_name(printed[i])
            else:
                role, basis, name = "", "none", clean_name(label) or rid
            checked = ""
        notes = [] if rid in labels else ["never speaks"]
        if label and basis != "p4":
            notes.insert(0, f"label {label!r}")
            if basis == "label" and others:
                notes.append("or: " + " | ".join(printed[k] for k in others))
        note = "; ".join(notes)
        rows.append(Row(play, rid, "personGrp" if is_group(name) else "person", name, role,
                        str(role_n.get(rid, 1)) if role else "", basis, checked, note))
    return rows


def read_table(path: Path = TABLE) -> list[Row]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader((x for x in f if not x.startswith("#")), delimiter="\t")
        rows = [Row(**{k: r.get(k) or "" for k in COLUMNS}) for r in reader]
    for r in rows:
        if r.kind not in KINDS or r.basis not in BASES:
            raise SpeakerError(f"speakers.tsv: {r.play} {r.id}: kind {r.kind!r}, basis {r.basis!r}")
    return rows


def for_play(rows: list[Row], play: str) -> list[Row]:
    return [r for r in rows if r.play == play]


def write_table(rows: list[Row], path: Path = TABLE) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(HEADER)
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(COLUMNS)
        for r in rows:
            w.writerow([getattr(r, c.name) for c in fields(Row)])


def particdesc(rows: list[Row]):
    """<particDesc><listPerson> for a play's rows, in table order."""
    pd = etree.Element(f"{TEI}particDesc")
    lp = etree.SubElement(pd, f"{TEI}listPerson")
    for r in rows:
        el = etree.SubElement(lp, f"{TEI}{r.kind}")
        el.set(XML_ID, r.id)
        etree.SubElement(el, f"{TEI}persName" if r.kind == "person" else f"{TEI}name").text = r.name
    return pd


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    wanted = argv or list(plays.read())
    old = read_table()
    kept = {(r.play, r.id): r for r in old if not r.pending or r.basis == "p4"}
    out = [r for r in old if r.play not in wanted]
    for play in wanted:
        for r in propose(play):
            out.append(kept.get((play, r.id), r))
    order = {p: i for i, p in enumerate(plays.read())}
    out.sort(key=lambda r: order.get(r.play, 999))  # stable: each play's rows stay in cast order
    write_table(out)
    pending = [r for r in out if r.pending]
    print(f"{len(out)} speakers, {len(pending)} to check", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
