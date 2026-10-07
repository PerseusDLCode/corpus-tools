# Regenerating Lear's Globe lineation

`doc/agenda.org` `#build/regenerate-lear`. Run: `pdm run python src/regenerate.py lr`
(about 8 s). Witnesses: `miun/kraken` primary, `trent/kraken` second reading.
`trent/djvu` was not used.

Round 1 built the gate and stopped: 263 of 273 intervals closed, and the ten that
didn't were a numeral both witnesses misread and eight shared half-lines the page
cannot show. Round 2 supplies those from a reviewed table and finishes the build.
*(Round 1's status note said nine half-lines; its own table listed eight, and 8 + 2
numeral intervals account for the ten failing intervals. Eight is right.)*

## Result

- **The gate passes: 32 of 32 pages, all 273 intervals closing exactly.**
- **3,332 Globe lines**, each with a numbered milestone; 868 `<lb/>`; no `ed="F1"`
  milestone.
- **272 milestones carry `source="#globe-edition"`** -- the lines whose number is
  printed on the page. The rest are counted.
- **Transcribed anchors: 268 of 276** fall on a line carrying the same number, against
  212 before the table.
- Both builds validate (`jing ../perseus-schemas/perseus_drama.rng`), the output's word
  stream is the P4's, and `check_corpus.py` resolves 6/26/**3332** citations at
  act/scene/line -- the leaf count equal to the lines generated.

**Both builds are written.** All nine rows of `data/shared-lines.tsv` were checked on
the page images by Cliff (p.852, p.866, p.868 on 2026-09-22; the other six on
2026-09-23), so the canonical build is no longer refused:
`out/lr/shakespeare.lr.globe.xml` and `out/lr/shakespeare.lr.globe.review.xml`.

## The shared-lines table (`data/shared-lines.tsv`)

Nine rows: seven `shared` junctions, one `turnover`, and one `numeral`
(`doc/forum.org` `#lineation/shared-lines-table`).

**Six were proposed from the Folger** by `src/shared_lines.py`, which looks in each +1
interval for a junction the Folger marks `@part` I/F, matching on the first words of
each half. It reproduces the forum's hand check exactly: IV.2, IV.6 x2, V.3 "Thou
liest", V.3 "That ever I have felt", and III.7 -- where the Folger also picks between
the page's two candidates ("Late footed in the kingdom?" / "To whose hands..."). Only
the Folger's `xml:id`s are recorded, never its text.

One detail worth keeping: a one-word half ("Speak.", "Come.") matched *any* Folger pair
while the one-word spelling tolerance applied to it, which proposed two junctions the
hand check does not support. A half of fewer than three words now has to match exactly.

**Four rows are from the page**, where the Folger disagrees, is silent, or reads
different lines:

- **III.7 "To whose hands have you sent the lunatic king?" / "Speak."** -- a `turnover`
  row. The page prints "Speak." flush at the margin, the same unmarked continuation as
  V.3 250, and Folger `ftln-2308` ends with "Speak.", grouping it with the lunatic-king
  line. "Late footed in the kingdom?" stands alone. Found by Cliff reading the review
  build.

- **V.3 "Come." / "Come hither, captain; hark."** The Folger marks "Come hither,
  captain. Hark." `ana="#short"` (`ftln-3281`), i.e. standing alone. That is not
  decisive -- see the cross-check below -- and the count needs the fold, which the
  image (p.875) supports.
- **V.3 "Well thought on: take my sword," / "Give it the captain."** -- a `turnover`
  row, not a shared line: both halves are Edmund's. Two readings close the interval,
  and the page is ambiguous between them: the continuation is set flush at the column
  margin, where every other turnover in the play is indented about 2.3u, which had
  pointed instead to a shared half with "Alb. Haste thee, for thy life."
  **Cliff's decision <2026-09-22>: take the Folger reading**, which makes "Well thought
  on. Take my sword. Give it the Captain." one line (`ftln-3550`). The neighbouring
  lines corroborate it: "Thy token of reprieve." (249) and "Haste thee, for thy life."
  (251) each stand alone in our count, as the Folger's short lines `ftln-3549` and
  `ftln-3552` do.

  **This row rests on the Folger's line division, not its `@part`.** The forum entry
  limits Folger evidence to "`@part` at a junction and nothing else: never counts, line
  numbers or words", so `#lineation/shared-lines-table` needs amending to cover it.

**The numeral row:** p.852 prints **39** beside "Lear. How old art thou?"; both OCR
layers read "30". Confirmed by Cliff on the miun scan, 2026-09-22 -- the first row
whose `checked` column is filled.

Applying a row must close its interval exactly, and a row that matches no junction, or
more than one, is an error rather than a silent no-op. Both are tested.

## The eight junctions on the page

Each junction was read on the miun scan (2026-09-22). In every case the first half
ends well short of the measure and the second half is set at the ordinary speech
indent, not displaced -- and in every case the page shows why it could not be
displaced:

| junction | page | why the second half is not displaced |
|---|---|---|
| III.7 "…lunatic king?" / "Speak." | 866 | a flush continuation, not a shared half: Regan's line runs the measure and hyphenates into its turnover, then "Speak." sits flush at the margin |
| IV.2 "What like, offensive." / "Then shall you go no further." | 868 | the second half runs the full measure |
| IV.6 "Is done to cure it." / "[Kneeling] O you mighty gods!" | 871 | the bracketed stage direction makes the half too wide |
| IV.6 "To boot, and boot!" / "A proclaim'd prize! Most happy!" | 872 | *Enter OSWALD.* intervenes on its own row; the marginal 230 sits on the second half |
| V.3 "Come." / "Come hither, captain; hark." | 875 | "Come."'s row is filled to the measure by *[Exeunt Lear and Cordelia, guarded.* |
| V.3 "Thou liest." / "In wisdom I should ask thy name;" | 876 | the second half is too wide to follow a quarter-measure first half |
| V.3 "Well thought on: take my sword," / "Give it the captain." | 877 | a flush continuation, like III.7's "Speak."; the marginal 250 sits on the first row |
| V.3 "That ever I have felt." / "[Kneeling] O my good master!" | 878 | the bracketed stage direction again |

Two observations worth keeping:

- **The page does displace when it can.** On p.871, three lines above the junction,
  "Glou. With all my heart." is pushed right as a displaced half. So the ordinary indent
  at these eight junctions is the compositor's answer to a half that will not fit, not
  his habit.
- **A bracketed stage direction at the head of the second half** accounts for three of
  the eight (IV.6 ×2, V.3 878), and one more is blocked by a stage direction filling the
  first half's row (V.3 875).

**Could a junction of this kind have been missed?** Not in any interval that closes: an
unfolded one leaves +1, and all 273 intervals close. The only stretch the gate cannot
see is a scene's tail after its last printed numeral -- **122 lines, 3.7% of the play**,
the longest being IV.7 (18 lines after the numeral on line 80) and I.4 (11).

## Output

One run writes two files (`out/lr/`, tracked in git so successive runs diff):

- `shakespeare.lr.globe.xml` -- canonical, no comments.
- `shakespeare.lr.globe.review.xml` -- the same, plus `<!-- REVIEW kind: detail -->` at
  the point each concerns. Removing them gives the canonical bytes back, which the
  build asserts and a test checks.

Comments in this run: 32 `page`, 6 `shared` and 2 table `turnover` (each now recording
who checked it and when), 4 `numeral`, 1 `witness`, 4 measured `turnover`, 159 `words`,
8 `anchor`, 42 `verse-prose`.

**Provenance.** CLAUDE.md's output contract asks for an `<encodingDesc>/<appInfo>`
stamp, but `perseus-schemas/perseus_drama.rng` -- the schema the file declares -- has no
`appInfo`, and `jing` rejects it. The stamp goes in `<revisionDesc>/<change>` instead,
carrying the same facts (tool, version, workshop commit, source sha256s) and the words
`DO NOT EDIT`. **CLAUDE.md's wording should be updated, or the ODD extended.** Decided
with Cliff before implementing.

`out/` is refused from a dirty tree, per CLAUDE.md; `--scratch=DIR` is for development
runs.

## The Folger cross-check (`-folger-check.tsv`)

The Folger marks a shared line `@part` I/F and a line that stands alone, metrically
short, `ana="#short"`. The two are mutually exclusive in its encoding, so together they
are its whole opinion about short lines. `src/folger_check.py` aligns its spoken words
to the P4's (95% align) and locates each of its lines among ours. **It reports; the
page decides.**

Across the play:

| | |
|---|---|
| our Globe lines folding two speeches | **231** |
| of those, the Folger marks the junction `@part` I/F | 183 |
| marks a half `ana="#short"`, i.e. contradicts the fold | **41** |
| says nothing | 7 |
| the Folger's own I/F pairs | 202 |
| of those, both halves inside one Globe line of ours | 181 |
| split across two of our lines | 6 |

**This is the measure of how far `#short` can be trusted.** Among the 41 it
contradicts is II.1.111 "Is he pursued?" / "Ay, my good lord.", which
`#oracle/shared-verse-lines` records as verified by hand against the printed page in
July: the marginal 111 is printed beside the second row. So the Folger and the Globe
simply differ about the lineation of short exchanges, often enough that `#short` cannot
outrank the page's own typography. It remains useful as evidence for a table row at a
junction *the page cannot show*, which is what the forum entry allows.

The 6 pairs the Folger shares and we do not are the converse case, listed in the TSV;
each falls in an interval that closes, so the page's count supports ours. III.7 is one
of them, and reading it is what caught the error below.

## Old against new

- **268 of 276 transcribed anchors** agree. Of the eight that don't, **seven are
  confirmed by the page's own numerals**: on five (I.4 340, II.4 130, III.4 130,
  III.6 60, IV.6 240) the page prints that very numeral on the line we number so, and
  two more (III.6 79, V.3 161) sit inside intervals that close on both sides.
  - **III.4 130 -> 144** is the known "Poor Tom" transcription problem (CLAUDE.md).
  - **II.4 130 -> 131** is a defect of the current P5, not of the P4: the P4's terminal
    marker labels "Reg. I am glad to see your highness." 130, exactly as the page does.
  - The rest are P4 anchors sitting on a different line from the page's numeral -- the
    phenomenon `#lineation/regenerate-from-witnesses` records under the stability
    premise.
- **IV.7 99 is the one the page cannot confirm.** The scene's last printed numeral is
  on line 80 of 98, and the P4's anchor falls in the ungated tail after it. The P4
  counts one line more than the page in that scene; its prose rows are keyed
  differently, as elsewhere in the P4.

## `@part` against the page (`-part-vs-page.tsv`)

The build never adds or alters P4 markup, so a shared line's two halves carry `@part`
only where the P4 had it. The shared structure itself is recorded by the milestone and
`<lb/>` pattern: one numbered milestone on the first half, and the second half's `<l>`
opening with `<lb/>`.

`@part` was added by the P4's encoding process rather than by the keyboarders (Cliff,
2026-09-22), so it carries none of the double-keyed text's authority. Against the page:

| | |
|---|---|
| shared lines the page shows | **231** |
| `@part` marks both halves | 215 |
| marks one half only | 3 |
| marks neither | 13 |
| `@part` pairs the page does **not** fold | 5 |

**21 disagreements**, each listed in the report with what the page shows. The five the
P4 marks and the page does not include III.4.187 "Child Rowland to the dark tower
came," -- a song line -- and V.3.232 "Touches us not with pity. [Exit Gentleman."

One case is worth noting for the next play. IV.6 871 ("Is done to cure it." /
"[Kneeling] O you mighty gods!") is *not* a disagreement: the P4 marks that pair, though
the page cannot show the junction and a table row was needed for the count. So `@part`
would have proposed that row on its own. **For Antony and the rest, the proposer could
take P4 `@part` as a second source of candidate rows**, beside the Folger -- as evidence
for a row, never as authority, exactly as the Folger is used.

## Other reports

- **`-word-disagreements.tsv`: 488**, of which **159 have both witnesses against the
  P4** ("hollownwss", "forest/forests", "loved/love"). Those 159 are the `words` review
  comments; one-witness disagreements stay in the TSV as OCR noise. The P4 is never
  corrected.
- **`-verse-prose.tsv`: 42 findings**, reported only: 31 continuation rows inside a
  `<p>`, 11 `<l>` elements holding two Globe line starts.
- **`-gate.tsv`**, **`-intervals.tsv`** (every interval, with the numeral reading used),
  **`-borderline-rows.tsv`** (4 turnover decisions near the 1.0u cut, all agreeing with
  the P4's `<l>`).

## Tests

`pdm run pytest`: **123 passed, 6 skipped** (the retired mdp cases). New this round:

- `tests/test_emit_tei.py` -- one test per placement convention, plus the review-build
  round trip and the stamp.
- `tests/test_shared_lines.py` -- the proposer reproduces the forum's hand check; the
  table on disk closes every interval; a row matching no junction is an error.
- `tests/test_regenerate_lear.py` -- the gate passes with the table and fails without it
  exactly where it did; milestone count and numbering; `@source` count; the review
  build's kinds; the canonical build carries no comments.

**Mutation check.** Eleven deliberate breaks of the new rules -- hoisting, insertion
order, `@source`, the speaker skip, review insertion, the fold's number carry, table
folding, the numeral override, the short-half match, and two more -- each made a test
fail. Two survived at first and were fixed rather than excused: nothing asserted the
review build actually carries comments, and `shared_lines.find_junction` was dead code
superseded by `apply_table` (now removed).

## Still open

- The header, for `#build/tei-header-lineation-prose`: `sourceDesc` still names Nelson
  Doubleday, and `editorialDecl` describes F1 milestones this build drops.
- Antony is the next build, and the first real test of whether these rules generalise;
  Titus and Richard II stay held out (`#phase2/held-out`).
