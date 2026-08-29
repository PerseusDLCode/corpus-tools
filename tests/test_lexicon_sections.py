from __future__ import annotations

import pytest

from lexicon_sections import LexiconStructureError, flatten_lexicon_sections

# Schmidt-style: edition div alone on its own line.
SCHMIDT_STYLE = """\
    <body xml:base="urn:cts:engLit:schmidt.lexicon.perseus-eng1">
      <div type="edition" xml:lang="eng" n="urn:cts:engLit:schmidt.lexicon.perseus-eng1">

        <div type="textpart" subtype="alpha" n="A">
          <head><title>A</title></head>
          <entryFree><orth>A,</orth> foo</entryFree>
        </div>
        <div type="textpart" subtype="alpha" n="B">
          <entryFree><orth>B,</orth> bar</entryFree>
        </div>
      </div>
    </body>
"""

SCHMIDT_STYLE_EXPECTED = """\
    <body xml:base="urn:cts:engLit:schmidt.lexicon.perseus-eng1">

        <div type="section" n="A" xml:id="section-A">
          <head><title>A</title></head>
          <entryFree><orth>A,</orth> foo</entryFree>
        </div>
        <div type="section" n="B" xml:id="section-B">
          <entryFree><orth>B,</orth> bar</entryFree>
        </div>
    </body>
"""

# Onions/Dyce-style: <body> and the edition div share a line.
ONIONS_STYLE = """\
    <body><div type="edition" n="urn:cts:engLit:onions.glossary.perseus-eng1" xml:lang="eng">
          <div type="textpart" subtype="alpha" n="A">
            <entryFree><orth>A,</orth> foo</entryFree>
          </div>
    </div></body>
"""

ONIONS_STYLE_EXPECTED = """\
    <body>
          <div type="section" n="A" xml:id="section-A">
            <entryFree><orth>A,</orth> foo</entryFree>
          </div>
    </body>
"""

# Abbott-style: sections nest further divs inside them, so the edition
# div's true close is not the first </div> encountered.
ABBOTT_STYLE = """\
<body>
  <div type="edition" n="urn:cts:engLit:abbott.perseus-eng1" xml:lang="eng">
    <div type="textpart" subtype="paragraph" n="1">
      <div type="other">
        <p>nested content</p>
      </div>
    </div>
  </div>
</body>
"""

ABBOTT_STYLE_EXPECTED = """\
<body>
    <div type="section" n="1" xml:id="section-1">
      <div type="other">
        <p>nested content</p>
      </div>
    </div>
</body>
"""


def test_schmidt_style():
    result, count = flatten_lexicon_sections(SCHMIDT_STYLE)
    assert result == SCHMIDT_STYLE_EXPECTED
    assert count == 2


def test_onions_style_body_shares_line_with_edition_div():
    result, count = flatten_lexicon_sections(ONIONS_STYLE)
    assert result == ONIONS_STYLE_EXPECTED
    assert count == 1


def test_abbott_style_nested_divs_inside_sections():
    result, count = flatten_lexicon_sections(ABBOTT_STYLE)
    assert result == ABBOTT_STYLE_EXPECTED
    assert count == 1


def test_raises_when_no_edition_div():
    with pytest.raises(LexiconStructureError):
        flatten_lexicon_sections("<body><div type=\"textpart\" subtype=\"alpha\" n=\"A\"></div></body>")


def test_raises_when_multiple_edition_divs():
    text = (
        '<body><div type="edition" n="x"></div><div type="edition" n="y"></div></body>'
    )
    with pytest.raises(LexiconStructureError):
        flatten_lexicon_sections(text)
