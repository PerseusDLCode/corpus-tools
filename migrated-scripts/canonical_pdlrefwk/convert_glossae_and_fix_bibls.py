import argparse
import logging

from lxml import etree

from convert_glossae import add_corresp_attr, change_app_lemma_to_s_gloss
from correct_misplaced_bibls import correct_misplaced_bibls

logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(
	    prog="Correct Mispalced bibls",
	    description="Fixes out-of-context bibl tags by converting them to ref tags.",
	    epilog="Please use with care — mistakes happen easily.",
	)

    parser.add_argument("filename")

    args = parser.parse_args()

    filename = args.filename

    tree = etree.parse(filename)

    # LOGGER.info("add_corresp_attr()")
    # tree = add_corresp_attr(tree)

    LOGGER.info("change_app_lemma_to_s_gloss()")
    tree = change_app_lemma_to_s_gloss(tree)

    LOGGER.info("correct_misplaced_bibls()")
    tree = correct_misplaced_bibls(tree)

    with open(filename, "wb") as f:
        etree.indent(tree, space="\t")
        f.write(etree.tostring(tree, encoding="utf-8", xml_declaration=True))


if __name__ == "__main__":
	main()
