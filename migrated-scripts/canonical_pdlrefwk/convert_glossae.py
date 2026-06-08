import argparse
import logging
import re

from collections import Counter

from lxml import etree
from lxml.builder import ElementMaker


NAMESPACES = {"tei": "http://www.tei-c.org/ns/1.0"}
URN_SUBSTITUTIONS = {
    "Soph. OC": "urn:cts:greekLit:tlg0011.tlg007",
    "Soph. OT": "urn:cts:greekLit:tlg0011.tlg004",
}

logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger(__name__)

NON_WORD_REGEX = re.compile(r"\W+")

E = ElementMaker(
    namespace="http://www.tei-c.org/ns/1.0", nsmap={None: "http://www.tei-c.org/ns/1.0"}
)

S = E.mentioned
GLOSS = E.gloss

TEI_APP_TAG = "{%s}app" % NAMESPACES["tei"]


def convert_glossa(s: str) -> str:
    """
    Convert a glossa — currently encoded as an <app> containing a <lem> —
    to an <s> lemma followed by a <gloss> glossa.
    """

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


def add_corresp_attr(tree: etree.ElementTree) -> etree.ElementTree:
    commentary_node = tree.find(".//tei:div[@type='commentary']", namespaces=NAMESPACES)

    if commentary_node is None:
        raise "Unable to find commentary node!"

    base_urn = commentary_node.get("n")
    for textpart in tree.iterfind(
        ".//tei:div[@type='textpart']", namespaces=NAMESPACES
    ):
        if textpart.get("corresp") is None:
            if (
                textpart.get("subtype") == "section"
                and textpart.get("n").lower() == "introduction"
            ):
                parent = textpart.getparent()
                textpart.attrib["corresp"] = parent.get("corresp")
            else:
                textpart.attrib["corresp"] = (
                    f"{base_urn}:{textpart.get('n').replace('_', '-')}"
                )

    return tree


def change_app_lemma_to_s_gloss(tree: etree.ElementTree) -> etree.ElementTree:
    citations = []

    for app in tree.iterfind(".//tei:app", namespaces=NAMESPACES):
        textpart_parent = app.xpath(
            "./ancestor::tei:div[@type='textpart'][1]", namespaces=NAMESPACES
        )[0]
        n = textpart_parent.get("n")
        lem = app.find("./tei:lem", namespaces=NAMESPACES)
        lemma = etree.tostring(lem, method="text", encoding="unicode")
        citation = lemma.split(" ")

        if len(citation) > 1:
            first = citation[0]
            last = citation[-1]
            citation = [first, last]

        citation_str = f"{'_'.join(citation)}_{n}"
        citation_str = re.sub(NON_WORD_REGEX, "", citation_str)

        if citation_str in citations:
            count = Counter(citations)[citation_str]
            citations.append(citation_str)
            citation_str = f"{citation_str}_{count + 1}"
        else:
            citations.append(citation_str)

        s_element = S(lemma, *app.attrib, ana=f"#{citation_str}")

        siblings = []

        for sib in app.itersiblings():
            if sib.tag == TEI_APP_TAG:
                break
            siblings.append(sib)

        gloss_element = GLOSS(app.tail, *siblings)

        gloss_element.set("{http://www.w3.org/XML/1998/namespace}id", citation_str)

        app.getparent().replace(app, s_element)
        s_element.addnext(gloss_element)

    return tree


def main():
    parser = argparse.ArgumentParser(
        prog="ConvertGlossae",
        description="Converts app-lemma combinations to s-gloss pairs. See https://github.com/PerseusDL/canonical_pdlrefwk/issues/99 for more info.",
        epilog="Please use with care — mistakes happen easily.",
    )

    parser.add_argument("filename")

    args = parser.parse_args()

    filename = args.filename

    tree = etree.parse(filename)
    tree = change_app_lemma_to_s_gloss(tree)

    with open(filename, "wb") as f:
        etree.indent(tree, space="\t")
        f.write(etree.tostring(tree, encoding="utf-8", xml_declaration=True))


if __name__ == "__main__":
    main()
