import argparse
import logging

from lxml import etree

NAMESPACES = {"tei": "http://www.tei-c.org/ns/1.0"}
URN_SUBSTITUTIONS = {
    "Soph. OC": "urn:cts:greekLit:tlg0011.tlg007",
    "Soph. OT": "urn:cts:greekLit:tlg0011.tlg004",
}


logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger(__name__)


def convert_citation(s: str) -> str:
    """
    Convert a natural language citation, such
    as `"Soph. OC 437"` to a CTS URN like
    `"urn:cts:greekLit:tlg0011.tlg007:437"`.
    """

    # Iterate through the URN_SUBSTITUTIONS
    # provided above, checking for a match
    # on the keys. As soon as a match is found,
    # replace it in the citation, stripping the
    # result in case of extra spaces. The remaining
    # part of the string should be the citation
    # component of a URN, which we can append to
    # the URN prefix provided as the value from the
    # matching key in URN_SUBSTITUTIONS.
    for nat, urn in URN_SUBSTITUTIONS.items():
        if nat in s:
            n = s.replace(nat, "").strip()

            # Some citations might reference an
            # entire work, so we'll need to return
            # the whole URN.
            if len(n) > 0:
                return f"{urn}:{n}"
            else:
                return urn

    return s


def add_refs_to_bibls(tree: etree.ElementTree) -> etree.ElementTree:
    for bibl in tree.iterfind(".//tei:bibl", namespaces=NAMESPACES):
        n = bibl.get("n")

        if n is None:
            LOGGER.warning(f"@n attribute not found at {etree.tostring(bibl)}")
            continue

        ref_urn = convert_citation(n)

        bibl.set("ref", ref_urn)

    return tree


def main():
    parser = argparse.ArgumentParser(
        prog="ConvertCitations",
        description="Converts bibl@n attributes to URN bibl@ref attributes",
        epilog="Please use with care — mistakes happen easily.",
    )

    parser.add_argument("filename")

    args = parser.parse_args()

    filename = args.filename

    tree = etree.parse(filename)
    tree = add_refs_to_bibls(tree)

    with open(filename, "wb") as f:
        etree.indent(tree, space="\t")
        f.write(etree.tostring(tree, encoding="utf-8", xml_declaration=True))


if __name__ == "__main__":
    main()
