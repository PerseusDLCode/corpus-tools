"""Witness page -> printed rows, each classified by typographic band.

doc/agenda.org #build/regenerate-lear; rules from doc/forum.org
#lineation/regenerate-from-witnesses and spikes/2026-09-21-regeneration.

A page's rows sit in fixed bands measured from the column's left margin in
units of row pitch u (the median vertical distance between rows):

    start      offset <= 1.7u          opens a Globe line (verse or prose)
    turnover   1.7u < offset <= 2.8u   the turnover indent
    indented   2.8u < offset <= 4.5u   indented verse: songs, rhymes, letters
    displaced  offset > 4.5u           a shared half-line, a song line set
                                       further in, or a stage direction

The spike (three pages, no songs) had start <= 2u and turnover to 4.5u.
Measured over all of Lear with the column margin taken as the body cluster's
median: no speech row falls between 1.44u and 1.88u; turnovers run
1.88-2.65u; and all 53 speech rows between 2.8u and 4.5u are song, rhyme or
letter lines, two of them following a full row (doc/agenda.org
#build/regenerate-lear, status).

and a row whose speaker prefix is followed by a gap wider than 2u is also
displaced (the second half of a shared line, set with its prefix).

The page's own marginal numbers are pulled off here too; each is attached to
the nearest row, which is the *last* row of its Globe line.

Nothing here reads a witness path: callers pass an ALTO file obtained through
src/globe/witnesses.py.
"""
from __future__ import annotations

import difflib
import re
import statistics
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

ALTO = {"a": "http://www.loc.gov/standards/alto/ns-v4#"}

START_MAX_U = 1.7  # a row this close to the margin starts a line
TURNOVER_MAX_U = 2.8  # the turnover indent ends here
INDENTED_MAX_U = 4.5  # indented verse ends here; beyond, displaced
PREFIX_GAP_U = 2.0  # prefix-to-text gap that marks a shared second half
SAME_ROW_U = 0.6  # baselines this close vertically are one printed row

PREFIX = re.compile(r"^[A-Z][a-z]{1,6}\.$")
INITIAL = re.compile(r"^[A-Z]\.$")
NUMERAL = re.compile(r"\d{1,3}")
HYPHEN_END = re.compile(r"[A-Za-z][¬-]$")


@dataclass
class Word:
    x: float
    w: float
    t: str


@dataclass
class Row:
    x: float  # left edge
    y: float  # baseline height, deskewed (read_rows); the box centre where ALTO gives no baseline
    r: float  # right edge
    words: list[Word]
    col: int = 0
    seq: int = 0  # order within the column
    num: int | None = None  # printed marginal number, if it sits on this row
    band: str = ""
    offset_u: float = 0.0
    prefix_len: int = 0  # words of speaker prefix opening the row
    pitch: float = 0.0  # the column's row pitch u
    margin: float = 0.0  # the column's left margin
    measure: float = 0.0  # the column's right edge (full measure)
    # filled by alignment
    start: int | None = None  # token index of the row's first word
    speech: bool = False
    extra: dict = field(default_factory=dict)

    @property
    def text(self) -> str:
        return " ".join(w.t for w in self.words)

    @property
    def short_u(self) -> float:
        """How far this row stops short of the column's measure, in pitches."""
        return (self.measure - self.r) / self.pitch

    def u(self, x: float) -> float:
        """Pixel x as pitches from the column margin: comparable across columns."""
        return (x - self.margin) / self.pitch

    @property
    def text_x(self) -> float:
        """Left edge of the row's text, after any speaker prefix."""
        if 0 < self.prefix_len < len(self.words):
            return self.words[self.prefix_len].x
        return self.x


@dataclass
class Page:
    printed: int
    witness: str  # "miun/kraken"
    leaf: str
    width: float
    columns: list[list[Row]]  # body rows only, marginal numbers removed
    pitch: list[float]
    margin: list[float]
    numbers: list[list[tuple[float, int]]]  # per column: (y, n)
    furniture: list[Row] = field(default_factory=list)  # running head, foot: never text
    annotations: list[tuple[int, float, float, int]] = field(default_factory=list)  # (col, x, y, n): numerals outside the frame

    @property
    def rows(self) -> list[Row]:
        return [r for c in self.columns for r in c]


# ---------------------------------------------------------------- reading


SLOPE_MIN_SPAN = 300  # pixels: baselines this long or longer measure the page's skew


def baseline(tl) -> list[tuple[float, float]]:
    """A TextLine's BASELINE polyline ("x1 y1 x2 y2 ...", or with commas)."""
    v = [float(t) for t in (tl.get("BASELINE") or "").replace(",", " ").split()]
    return list(zip(v[0::2], v[1::2]))


def read_rows(path: Path) -> tuple[list[Row], float, float]:
    """Every non-empty TextLine as a Row, and the page width and height from ALTO.

    A row's y is its baseline, carried to the middle of the page along the
    page's skew (the median slope of its long baselines). A marginal number is
    set on its line's baseline, but its box is smaller than the line's, and an
    italic speaker prefix moves a box centre too: on Trent's small, skewed
    leaves box centres put a number nearer the next row than its own (Antony
    p.929, "Eros. See you here, sir?" 30; canonical-engLit doc/agenda.org
    #build/regenerate-ant). A TextLine without a baseline keeps its box centre."""
    tree = ET.parse(path)
    page = tree.find(".//a:Page", ALTO)
    width = float(page.get("WIDTH"))
    height = float(page.get("HEIGHT"))
    found, slopes = [], []
    for tl in tree.iterfind(".//a:TextLine", ALTO):
        ws = [Word(float(s.get("HPOS")), float(s.get("WIDTH")), s.get("CONTENT"))
              for s in tl.findall("a:String", ALTO)
              if (s.get("CONTENT") or "").strip() and s.get("HPOS") is not None]  # kraken emits some empty, unplaced Strings
        if ws:
            ws.sort(key=lambda w: w.x)  # kraken does not always emit Strings left to right
            pts = baseline(tl)
            if len(pts) >= 2 and pts[-1][0] - pts[0][0] >= SLOPE_MIN_SPAN:
                slopes.append((pts[-1][1] - pts[0][1]) / (pts[-1][0] - pts[0][0]))
            found.append((tl, ws, pts))
    slope = statistics.median(slopes) if slopes else 0.0
    rows = []
    for tl, ws, pts in found:
        if pts:
            mx, my = sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts)
            y = my + slope * (width / 2 - mx)
        else:
            y = float(tl.get("VPOS")) + float(tl.get("HEIGHT")) / 2
        # the row's extent is its words', not the TextLine's box, which can
        # start well before the first word ("justicer;", p.865)
        rows.append(Row(x=ws[0].x, y=y, r=max(w.x + w.w for w in ws), words=ws))
    return rows, width, height


HEAD_GAP_U = 1.2  # an empty band this tall in the top tenth ends the running head
HEAD_ZONE = 0.1
FOOT_GAP_U = 2.0  # an empty band this tall ...
FOOT_ZONE = 0.9  # ... below this fraction of the page height starts the foot


def split_furniture(rows: list[Row], pitch: float, height: float) -> tuple[list[Row], list[Row]]:
    """Separate the running head and the page foot from the text.

    The running head (title, act or scene, folio) sits above an empty band
    wider than HEAD_GAP_U pitches in the top tenth of every page. It goes by
    position: OCR misreads the folio (p.855 as "852", p.874 as "374"), and on
    Trent's skewed leaves the head's pieces spread over most of a pitch. The
    foot is everything below an empty band wider than FOOT_GAP_U pitches in the
    bottom tenth: the scanner's watermark and printer's signature marks, which
    include numerals that would otherwise pass for marginal numbers.
    Returns (text rows, furniture rows)."""
    rows = sorted(rows, key=lambda r: r.y)
    furniture: list[Row] = []
    for k in range(1, len(rows)):
        if rows[k - 1].y > HEAD_ZONE * height:
            break
        if rows[k].y - rows[k - 1].y > HEAD_GAP_U * pitch:
            furniture, rows = rows[:k], rows[k:]
            break
    for k in range(len(rows) - 1, 0, -1):
        if rows[k].y < FOOT_ZONE * height:
            break
        if rows[k].y - rows[k - 1].y > FOOT_GAP_U * pitch:
            furniture += rows[k:]
            rows = rows[:k]
            break
    return rows, furniture


WATERMARK_RATIO = 0.75  # a row this like a watermark line, in the foot zone, is the watermark


def split_watermark(rows: list[Row], watermark, height: float) -> tuple[list[Row], list[Row]]:
    """Take off the scanner's watermark where the foot rule did not: the
    Michigan scans print "Digitized by / UNIVERSITY OF MICHIGAN" and "Original
    from / UNIVERSITY OF MICHIGAN" under every leaf, and on Antony p.915 the
    text and the printer's signature run so low that no gap of FOOT_GAP_U
    pitches stands above them, so the watermark stayed in the text and its "OF"
    counted as a line (canonical-engLit doc/agenda.org #build/regenerate-ant).
    A row in the foot zone whose text is like a watermark line, OCR errors and
    all ("JNIVERSITY OF MICHIGA", "Original fro"), is furniture. Returns (text
    rows, watermark rows)."""
    marks = [m.lower() for m in watermark]

    def like(r: Row) -> bool:
        t = r.text.lower()
        return any(difflib.SequenceMatcher(None, t, m).ratio() >= WATERMARK_RATIO for m in marks)
    if not marks:
        return rows, []
    off = [r for r in rows if r.y > FOOT_ZONE * height and like(r)]
    return [r for r in rows if not any(r is o for o in off)], off


GUTTER_REACH = 0.1  # the gutter is sought this fraction of the text width either side of the midpoint


def gutter(rows: list[Row]) -> float:
    """The x between the columns: the middle of the widest stretch, near the
    midpoint of the 5th-percentile left edge and the 95th-percentile right
    edge, that the fewest words cover (none, but for a running head across
    the page). The midpoint alone is no gutter on a skewed leaf: Michigan's
    Love's Labour's Lost p.141 puts its right column's foot at x=1430-1434,
    left of a midpoint of 1433.5, and the first word of five of its rows
    went to the left column ("to board. sense")."""
    xs = sorted(r.x for r in rows)
    rs = sorted(r.r for r in rows)
    lo, hi = xs[len(xs) // 20], rs[-len(rs) // 20]
    mid, reach = (lo + hi) / 2, GUTTER_REACH * (hi - lo)
    a, b = int(mid - reach), int(mid + reach) + 1
    cover = [0] * (b - a)
    for r in rows:
        for w in r.words:
            for x in range(max(a, int(w.x)), min(b, int(w.x + w.w) + 1)):
                cover[x - a] += 1
    least = min(cover)
    best, run = None, None  # (length, start) of the widest run at the least cover
    for i, c in enumerate(cover + [least + 1]):
        if c == least and run is None:
            run = i
        elif c != least and run is not None:
            if best is None or i - run > best[0]:
                best = (i - run, run)
            run = None
    return a + best[1] + best[0] / 2


def split_columns(rows: list[Row]) -> list[list[Row]]:
    """Two columns, split midway between the 5th-percentile left edge and the
    95th-percentile right edge; each sorted top to bottom. A row whose words
    straddle the split is two rows: the segmenter sometimes runs one baseline
    across the gutter (p.866, "...but let them tion: we are bound...")."""
    split = gutter(rows)
    pieces = []
    for r in rows:
        left = [w for w in r.words if w.x < split]
        right = [w for w in r.words if w.x >= split]
        if left and right:
            pieces += [Row(x=ws[0].x, y=r.y, r=max(w.x + w.w for w in ws), words=ws) for ws in (left, right)]
        else:
            pieces.append(r)
    return [sorted([r for r in pieces if (r.x < split) == (c == 0)], key=lambda r: r.y) for c in (0, 1)]


# ---------------------------------------------------------------- preparing


def take_marginal_numbers(col: list[Row]) -> tuple[list[Row], list[tuple[float, int]]]:
    """Rows made only of 1-3 digit tokens are marginal numbers. Returns the
    remaining rows and the (y, n) numbers. Trailing numerals inside a row are
    taken separately, once pitch is known (take_trailing_numbers)."""
    nums, body = [], []
    for r in col:
        if all(NUMERAL.fullmatch(w.t) for w in r.words):
            nums.append((r.y, int(r.words[0].t), r.words[0].x))
        else:
            body.append(r)
    return body, nums


def take_trailing_numbers(body: list[Row]) -> list[tuple[float, int]]:
    """A marginal number the segmenter put on the same baseline as its row."""
    nums = []
    for r in body:
        if len(r.words) > 1 and NUMERAL.fullmatch(r.words[-1].t):
            w = r.words.pop()
            r.r = max(x.x + x.w for x in r.words)
            nums.append((r.y, int(w.t), w.x))
    return nums


ANNOTATION_U = 0.5  # a numeral this far beyond the measure is outside the printed frame


def split_annotations(nums, measure: float, pitch: float):
    """Printed marginal numbers sit inside the frame, within 1.7u of the
    measure in both witnesses. A numeral further out than ANNOTATION_U beyond
    it is a reader's pen mark (miun p.861 has two, a "7" read as "1" and a
    "15"), not print. Returns (printed, annotations), each as (y, n, x)."""
    printed = [t for t in nums if t[2] <= measure + ANNOTATION_U * pitch]
    return printed, [t for t in nums if t[2] > measure + ANNOTATION_U * pitch]


def row_pitch(body: list[Row]) -> float:
    return statistics.median(b.y - a.y for a, b in zip(body, body[1:]) if b.y > a.y)


def merge_same_row(body: list[Row], pitch: float) -> list[Row]:
    """Baselines at the same height in a column are one printed row. The
    segmenter splits a row at a wide gap: a speaker prefix set apart from a
    shared half ("Lear." beside "Ask her forgiveness?"), or a stage direction
    set at the right of a speech row ("Her. Again!" ... "[Third trumpet."), and
    does not always order the pieces by height. Rows whose centres lie within
    SAME_ROW_U pitches of the first row of a group are joined, words left to
    right. (Generalises the spike's lone-prefix merge.)"""
    groups: list[list[Row]] = []
    for r in sorted(body, key=lambda r: r.y):
        if groups and r.y - groups[-1][0].y < pitch * SAME_ROW_U:
            groups[-1].append(r)
        else:
            groups.append([r])
    out = []
    for g in groups:
        if len(g) == 1:
            out.append(g[0])
            continue
        g.sort(key=lambda r: r.x)
        widest = max(g, key=lambda r: r.r - r.x)
        out.append(Row(x=g[0].x, y=widest.y, r=max(r.r for r in g),
                       words=[w for r in g for w in r.words]))
    return out


def join_hyphenation(body: list[Row]) -> None:
    """A word broken across rows is moved whole to the second row, so the row
    break -- and any milestone or <lb/> there -- falls before the whole word.
    Its second part begins in lower case; OCR also reads a dash as the
    hyphen mark ("We'll teach you—" as "you¬", p.858), and there the next row
    begins a new speech ("Kent.")."""
    for a, b in zip(body, body[1:]):
        if not a.words or not b.words:
            continue
        last = a.words[-1].t
        if HYPHEN_END.search(last) and b.words[0].t[:1].islower():
            frag = a.words.pop().t[:-1]
            first = b.words[0]
            b.words[0] = Word(first.x, first.w, frag + first.t)
            b.extra["completes_word"] = True  # lineate.continues


MARGIN_BAND_U = 0.75  # rows this close to the leftmost edge of the body cluster make it up


MARGIN_MIN_ROWS = 4  # left edges within MARGIN_BAND_U of each other that make a margin


def column_margin(body: list[Row], pitch: float) -> float:
    """The column's left margin: the median left edge of the body cluster, the
    leftmost MARGIN_MIN_ROWS or more rows whose left edges lie within
    MARGIN_BAND_U pitches of each other. A few rows hanging into the margin
    are not a cluster (p.860 col 2, p.861 col 1). The 10th-percentile edge,
    used before, is not the margin where fewer rows than that are flush: the
    left column of Love's Labour's Lost p.141 is one-row speeches set at the
    speaker indent, with six rows flush of 70, and its turnovers read as
    starts."""
    xs = sorted(r.x for r in body)
    band = MARGIN_BAND_U * pitch
    for i, base in enumerate(xs):
        cluster = [x for x in xs[i:] if x < base + band]
        if len(cluster) >= MARGIN_MIN_ROWS:
            return statistics.median(cluster)
    base = xs[len(xs) // 10]  # too few rows to cluster
    return statistics.median(x for x in xs if x < base + band)


MARGIN_NEAR = 10  # flush rows either side of a row that give its local margin


MARGIN_HANG_U = 0.5  # a row this far left of its fitted margin says the fit is wrong


def local_margins(body: list[Row], pitch: float, speakers: set[str] = frozenset()) -> list[float]:
    """Each row's left margin: a line fitted to the flush rows nearest it.

    The column's margin is not one x for the whole column. On Trent's leaves
    it drifts about half a pitch from top to bottom (Antony p.923: flush rows
    at x=37 near the head, 48 near the foot), which put turnovers at the foot
    of the column (2.3-2.65u) past the indented band's edge (2.8u) and made
    lines of them (canonical-engLit doc/agenda.org #build/regenerate-ant). The
    flush rows are the body cluster (column_margin); for each row, the
    2*MARGIN_NEAR of them nearest it in height give a local slope (least
    squares) and a robust level (the median of x - slope*y), so a stray row
    moves nothing. A column with too few flush rows keeps one margin. A line
    over the whole column was tried and failed: the top of a page of prose,
    with few flush rows, set its slope (p.943).

    Speech starts ("Tra. Even he") can sit inside the flush band, and where
    flush rows are few they set the margin at the speech indent: on
    Michigan's p.236 (The Taming of the Shrew) the margin drifts most of a
    pitch down the column, and at its head the flush rows then hang a pitch
    into the margin and the turnovers read as starts. Where a row hangs more
    than MARGIN_HANG_U into its fitted margin, the fit is made again without
    the rows opening with a speaker's prefix (the prefix's shape and a P4
    speaker name, or an initial and a name: "K. Edw.", "L. Grey."). Only
    then: leaving them out everywhere moves margins the published plays were
    built on (Hamlet pp.817-833 on Trent), and in Cymbeline's masque (p.970)
    speeches are set flush. Where too few rows are left to fit a line, the
    margin is the median of those rows and the rows that hung: 3 Henry VI
    p.540 col.1 is speeches and their turnovers, with one row at the margin
    ('Till youth take leave', 0.84u left of the fit); and The Taming of the
    Shrew p.253 col.2, where 'toward.' and 'froward.', turnovers, had read
    as lines after V.2's last numeral."""
    m0 = column_margin(body, pitch)
    flush = [r for r in body if abs(r.x - m0) < MARGIN_BAND_U * pitch]
    out = _fit_margins(body, flush, m0)
    hang = [r for r, m in zip(body, out) if (r.x - m) / pitch < -MARGIN_HANG_U]
    if hang:
        rest = [r for r in flush if not opens_with_prefix(r, speakers)]
        if len(rest) >= 2 * MARGIN_NEAR:
            out = _fit_margins(body, rest, m0)
        else:
            out = [statistics.median(r.x for r in rest + hang)] * len(body)
    return out


def opens_with_prefix(r: Row, speakers: set[str]) -> bool:
    """Does the row open with a speaker's prefix: one shaped like one that is
    a P4 speaker name ("Tra."), or an initial and a capitalised word with a
    period ("K. Edw.", "L. Grey.", and the OCR's "K. Edzv.")?"""
    from globe.tokens import norm  # page_rows otherwise needs nothing from the TEI side
    ws = r.words
    if not ws:
        return False
    if PREFIX.match(ws[0].t) and norm(ws[0].t) in speakers:
        return True
    return (len(ws) > 1 and bool(INITIAL.match(ws[0].t))
            and ws[1].t[:1].isupper() and ws[1].t.endswith("."))


def _fit_margins(body: list[Row], flush_rows: list[Row], m0: float) -> list[float]:
    flush = [(r.y, r.x) for r in flush_rows]
    if len(flush) < 2 * MARGIN_NEAR:
        return [m0] * len(body)
    out = []
    for r in body:
        near = sorted(flush, key=lambda p: abs(p[0] - r.y))[:2 * MARGIN_NEAR]
        my = statistics.mean(y for y, _ in near)
        vy = sum((y - my) ** 2 for y, _ in near)
        b = sum((y - my) * x for y, x in near) / vy if vy else 0.0
        out.append(statistics.median(x - b * y for y, x in near) + b * r.y)
    return out


def column_measure(body: list[Row]) -> float:
    """The column's full measure: the 90th-percentile row right edge."""
    rs = sorted(r.r for r in body)
    return rs[int(len(rs) * 0.9)]


def attach_numbers(body: list[Row], nums) -> None:
    for y, n, *_ in nums:
        min(body, key=lambda r: abs(r.y - y)).num = n


def classify_band(offset_u: float, prefix_gap_u: float | None = None) -> str:
    """The band for a row offset `offset_u` row-pitches from the margin.
    `prefix_gap_u` is the gap after a leading speaker prefix, if there is one."""
    if offset_u > INDENTED_MAX_U:
        return "displaced"
    if offset_u > TURNOVER_MAX_U:
        return "indented"
    if offset_u > START_MAX_U:
        return "turnover"
    if prefix_gap_u is not None and prefix_gap_u > PREFIX_GAP_U:
        return "displaced"
    return "start"


def _within_one_edit(a: str, b: str) -> bool:
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) > len(b):
        a, b = b, a
    i = 0
    while i < len(a) and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:] or (len(a) == len(b) and a[i + 1:] == b[i + 1:])


def _is_speaker_word(w: str, speakers: set[str]) -> bool:
    """A word that is a speaker prefix: shaped like one ("Glou."), a P4 speaker
    name ("Lear", its period lost to OCR), or, ending in a period, within one
    OCR error of a name of three or more letters ("Aló.", "A1b." for "Alb.")."""
    from globe.tokens import norm  # page_rows otherwise needs nothing from the TEI side
    n = norm(w)
    if PREFIX.match(w) or n in speakers:
        return True
    return w.endswith(".") and len(n) >= 2 and any(
        len(s) >= 3 and _within_one_edit(n, s) for s in speakers)


def prefix_length(r: Row, speakers: set[str]) -> int:
    """Words of speaker prefix opening the row: two words that spell a P4
    speaker name ("Old Man."), or one speaker word (_is_speaker_word). Only the
    gap after it decides anything, so a name opening a line of text ("Kent, on
    thy life") is harmless."""
    from globe.tokens import norm
    ws = r.words
    if len(ws) > 2 and ws[1].t.endswith("."):
        two = norm(ws[0].t) + norm(ws[1].t)
        if two in speakers or any(len(s) >= 6 and _within_one_edit(two, s) for s in speakers):
            return 2  # "Old Man.", "Third Sery."
    if len(ws) > 1 and _is_speaker_word(ws[0].t, speakers):
        return 1
    return 0


def prefix_gap(r: Row) -> float | None:
    """Pixel gap between a leading speaker prefix and the next word, or None."""
    if not r.prefix_len:
        return None
    a, b = r.words[r.prefix_len - 1], r.words[r.prefix_len]
    return b.x - (a.x + a.w)


def prepare_column(col: list[Row], speakers: set[str] = frozenset()):
    body, nums = take_marginal_numbers(col)
    pitch = row_pitch(body)
    nums += take_trailing_numbers(body)
    body = merge_same_row(body, pitch)
    join_hyphenation(body)
    body = [r for r in body if r.words]
    margin = column_margin(body, pitch)  # the column's, for the Page; each row has its own
    measure = column_measure(body)
    nums, annotations = split_annotations(nums, measure, pitch)
    attach_numbers(body, nums)
    for r, local in zip(body, local_margins(body, pitch, speakers)):
        r.pitch, r.margin, r.measure = pitch, local, measure
        r.prefix_len = prefix_length(r, speakers)
        r.offset_u = (r.x - local) / pitch
        gap = prefix_gap(r)
        r.band = classify_band(r.offset_u, None if gap is None else gap / pitch)
    return body, pitch, margin, nums, annotations


def read_page(path: Path, printed: int, witness: str, leaf: str, speakers: set[str] = frozenset(),
              watermark=()) -> Page:
    rows, width, height = read_rows(path)
    rough = statistics.median(row_pitch(c) for c in split_columns(rows))
    rows, furniture = split_furniture(rows, rough, height)
    rows, marks = split_watermark(rows, watermark, height)
    furniture += marks
    cols, pitches, margins, numbers, annotations = [], [], [], [], []
    for c, col in enumerate(split_columns(rows)):
        body, pitch, margin, nums, notes = prepare_column(col, speakers)
        annotations += [(c + 1, x, y, n) for y, n, x in notes]
        for i, r in enumerate(body):
            r.col, r.seq = c + 1, i + 1
        cols.append(body)
        pitches.append(pitch)
        margins.append(margin)
        numbers.append(nums)
    return Page(printed, witness, leaf, width, cols, pitches, margins, numbers, furniture, annotations)
