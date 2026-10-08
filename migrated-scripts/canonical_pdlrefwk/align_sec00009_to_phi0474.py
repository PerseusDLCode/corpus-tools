# DEPRECATED — See up-to-date script in atlas-data-prep

import csv

from pathlib import Path

from lxml import etree

DIR = Path(__file__).resolve().parent.parent / "data" / "sec00009"
NAMESPACES = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "ti": "http://chs.harvard.edu/xmlns/cts",
    "xml": "http://www.w3.org/XML/1998/namespace",
}
SUBDIRS = [d for d in DIR.iterdir() if d.is_dir()]


def read_file(path: Path) -> etree.ElementTree:
    return etree.parse(path)


def collect_glosses(tei_file: Path, work_urn_fragment: str):
    tree = read_file(tei_file)

    glosses: tuple[str, str, str] = []

    for textpart in tree.iterfind(
        ".//tei:div[@subtype='section']", namespaces=NAMESPACES
    ):
        for s_el in textpart.iterfind(".//tei:s", namespaces=NAMESPACES):
            lemma = etree.tostring(s_el, method="text", encoding="unicode").strip()
            ana = s_el.get("ana")
            xpath = f".//tei:gloss[@xml:id='{ana.replace("#", "")}']"
            gloss = textpart.find(xpath, namespaces=NAMESPACES)

            assert gloss is not None, f"No gloss found for {ana} in {work_urn_fragment}"

            phi0474_urn = None
            textpart_corresp = textpart.get("corresp")

            if textpart_corresp is not None:
                if textpart_corresp.startswith(work_urn_fragment):
                    phi0474_urn = textpart_corresp
                else:
                    print(
                        f"Incomplete @corresp attribute on {etree.tostring(textpart)}."
                    )

                    maybe_corresp = f"{work_urn_fragment}:{textpart_corresp}"

                    print(f"Does this look correct? {maybe_corresp}")
                    user_response = input(
                        "Type 'y' to accept; otherwise, enter the URN manually.\n\n"
                    )

                    if user_response.lower() == "y":
                        phi0474_urn = maybe_corresp
                    else:
                        phi0474_urn = user_response
            else:
                textpart_n = textpart.get("n")
                phi0474_urn = f"{urn_prefix}:{textpart_n}"

            glosses.append(
                (
                    phi0474_urn,
                    lemma,
                    etree.tostring(
                        gloss, xml_declaration=False, encoding="unicode"
                    ).strip(),
                )
            )

    return glosses


def get_about_urn(cts_file: Path):
    tree = read_file(cts_file)

    about_el = tree.find(".//ti:about", namespaces=NAMESPACES)

    return about_el.get("urn")

APPROVED_WORK_FRAGMENTS = ["sec002", "sec003a"]

def main():
    for d in SUBDIRS:
        # sec001 is the introduction, which we
        # don't need to align
        if d.name not in APPROVED_WORK_FRAGMENTS:
            continue
        cts_file = d / "__cts__.xml"
        tei_file = d / f"sec00009.{d.name}.perseus-eng1.xml"

        about_urn = get_about_urn(cts_file)

        glosses = collect_glosses(tei_file, about_urn)

        with open(f"sec00009.{d.name}.jsonl", "w", newline="") as f:
            writer = csv.writer(
                f, delimiter=",", quotechar="'", quoting=csv.QUOTE_MINIMAL
            )

            writer.writerow(["phi0474_urn", "lemma", "gloss"])
            writer.writerows(glosses)


if __name__ == "__main__":
    main()
