from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

from globe import emit_tei, manifest, plays, regenerate, schmidt_smoke

# The regeneration stamp: the one <change> in <revisionDesc> that may differ
# between a build and the published file (its date, commit and the shell's
# sha256). Everything else must be byte-identical.
STAMP = re.compile(rb'<change when="[^"]*"><ab>' + re.escape(emit_tei.STAMP_PREFIX.encode())
                   + rb"[^<]*</ab></change>")


def without_stamp(xml: bytes) -> bytes:
    found = STAMP.findall(xml)
    if len(found) != 1:
        raise ValueError(f"expected one regeneration stamp, found {len(found)}")
    return STAMP.sub(b"<change/>", xml)


def verify(play: str, flags: list[str]) -> int:
    """Build into a temporary directory and compare the canonical build with
    canonical-engLit's published file, ignoring only the regeneration stamp."""
    published = regenerate.CORPUS / plays.get(play).shell
    with tempfile.TemporaryDirectory(prefix=f"globe-verify-{play}-") as tmp:
        if regenerate.main(play, f"--scratch={tmp}", *flags) != 0:
            print(f"globe verify {play}: the build failed", file=sys.stderr)
            return 1
        built_path = Path(tmp) / play / published.name
        if not built_path.is_file():
            print(f"globe verify {play}: no canonical build was written", file=sys.stderr)
            return 1
        old, new = without_stamp(published.read_bytes()), without_stamp(built_path.read_bytes())
    if old != new:
        a, b = old.decode().splitlines(), new.decode().splitlines()
        n = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
        print(f"globe verify {play}: FAILED -- the build differs from {published} beyond the stamp, "
              f"first at line {n + 1}:\n  published: {a[n] if n < len(a) else '<end>'}\n"
              f"  built:     {b[n] if n < len(b) else '<end>'}", file=sys.stderr)
        return 1
    print(f"globe verify {play}: OK -- the build equals {published} except in the stamp", file=sys.stderr)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="globe-lineation",
        description="Regenerate a play's Globe lineation from the witness pages (doc/globe-lineation.org).",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_ in [
        ("regenerate", "build into out/globe/PLAY and write reports/globe; refuses on a dirty tree"),
        ("verify", "build to a temporary directory and compare with canonical-engLit's published file"),
    ]:
        p = sub.add_parser(name, help=help_)
        p.add_argument("play")
        p.add_argument("--allow-pending", action="store_true")
        p.add_argument("--any-corpus-branch", action="store_true",
                       help="build against canonical-engLit on a branch other than mvp (development only)")
        if name == "regenerate":
            p.add_argument("--scratch", metavar="DIR", help="write builds and reports under DIR instead")
    p = sub.add_parser("manifest", help="rewrite the play's rows in data/globe/witness-manifest.tsv")
    p.add_argument("play")
    p = sub.add_parser("smoke", help="check Schmidt's citations of PLAY against out/globe/PLAY")
    p.add_argument("play")
    p.add_argument("out_dir", nargs="?", type=Path, default=regenerate.REPO / "reports" / "globe")
    args = parser.parse_args()

    if args.command == "manifest":
        sys.exit(manifest.main(args.play))
    if args.command == "smoke":
        rows, sources = schmidt_smoke.run(args.play)
        schmidt_smoke.write(rows, sources, args.out_dir, args.play)
        print(schmidt_smoke.summary(rows), file=sys.stderr)
        sys.exit(0)
    flags = [f for f, on in [("--allow-pending", args.allow_pending),
                             ("--any-corpus-branch", args.any_corpus_branch)] if on]
    if args.command == "verify":
        sys.exit(verify(args.play, flags))
    if args.scratch:
        flags.append(f"--scratch={args.scratch}")
    sys.exit(regenerate.main(args.play, *flags))
