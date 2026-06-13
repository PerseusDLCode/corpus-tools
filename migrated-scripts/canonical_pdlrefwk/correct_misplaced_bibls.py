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

def correct_misplaced_bibls(tree: etree.ElementTree) -> etree.ElementTree:
    # we need to use `xpath()` instead of `iterfind()` in order to support
    # the `ancestor::` axis
    for bibl in tree.xpath(".//tei:bibl[not(ancestor::tei:cit)]", namespaces=NAMESPACES):
        bibl.tag = "ref"

        if 'ref' in bibl.attrib:
            LOGGER.info("Deleting stray @ref attribute")
            del bibl.attrib['ref']

    return tree


def main():
    parser = argparse.ArgumentParser(
        prog="Correct Misplaced bibls",
        description="Fixes out-of-context bibl tags by converting them to ref tags.",
        epilog="Please use with care — mistakes happen easily.",
    )

    parser.add_argument("filename")

    args = parser.parse_args()

    filename = args.filename

    tree = etree.parse(filename)
    tree = correct_misplaced_bibls(tree)

    with open(filename, "wb") as f:
        etree.indent(tree, space="\t")
        f.write(etree.tostring(tree, encoding="utf-8", xml_declaration=True))


if __name__ == "__main__":
    main()
