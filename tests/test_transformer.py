from pathlib import Path

import pytest

from transformer import transform
from tei import TEIDocument


class TestTransform:
    def test_returns_string(self, thucydides_grc):
        result = transform(thucydides_grc.path, "normalize-cts.xsl")
        assert isinstance(result, str)

    def test_result_is_xml(self, thucydides_grc):
        result = transform(thucydides_grc.path, "normalize-cts.xsl")
        assert result.startswith("<?xml")

    def test_result_is_nonempty(self, thucydides_grc):
        result = transform(thucydides_grc.path, "normalize-cts.xsl")
        assert len(result) > 0

    def test_normalize_cts_removes_spurious_extent(self, thucydides_grc):
        result = transform(thucydides_grc.path, "normalize-cts.xsl")
        assert "<extent>" not in result

    def test_normalize_cts_removes_edition_wrapper(self, thucydides_grc):
        # The stylesheet strips div[@type='edition'], leaving only its children
        result = transform(thucydides_grc.path, "normalize-cts.xsl")
        assert 'type="edition"' not in result

    def test_normalize_cts_hoists_and_lowercases_subtype(self, tmp_path):
        # EpiDoc textpart/@subtype is hoisted to @type and lower-cased so a
        # capitalized subtype="Book" (e.g. Homer) becomes type="book".
        doc = tmp_path / "epic.xml"
        doc.write_text(
            '<TEI xmlns="http://www.tei-c.org/ns/1.0"><text>'
            '<body xml:base="urn:cts:test">'
            '<div type="edition">'
            '<div type="textpart" subtype="Book" n="1">'
            '<l n="1">x</l></div></div>'
            "</body></text></TEI>",
            encoding="utf-8",
        )
        result = transform(doc, "normalize-cts.xsl")
        assert 'type="book"' in result
        assert 'type="Book"' not in result
        assert "subtype=" not in result
        assert 'type="edition"' not in result
        assert 'type="textpart"' not in result

    def test_all_eight_documents_transform_without_error(
        self,
        tlg0001_tlg001_perseus_grc2,
        tlg0003_tlg001_perseus_grc2,
        tlg0011_tlg001_perseus_grc2,
        tlg0057_tlg069_1st1K_grc1,
        tlg0086_tlg034_perseus_grc2,
        tlg0086_tlg034_perseus_eng2,
        phi1017_phi007_perseus_lat2,
        phi2331_phi013_perseus_lat2,
    ):
        for doc in [
            tlg0001_tlg001_perseus_grc2,
            tlg0003_tlg001_perseus_grc2,
            tlg0011_tlg001_perseus_grc2,
            tlg0057_tlg069_1st1K_grc1,
            tlg0086_tlg034_perseus_grc2,
            tlg0086_tlg034_perseus_eng2,
            phi1017_phi007_perseus_lat2,
            phi2331_phi013_perseus_lat2,
        ]:
            result = transform(doc.path, "normalize-cts.xsl")
            assert result, f"Empty result for {doc.path.name}"


class TestTEIDocumentTransform:
    def test_convenience_method_returns_string(self, thucydides_grc):
        result = thucydides_grc.transform("normalize-cts.xsl")
        assert isinstance(result, str)

    def test_convenience_method_matches_direct_call(self, thucydides_grc):
        direct = transform(thucydides_grc.path, "normalize-cts.xsl")
        via_doc = thucydides_grc.transform("normalize-cts.xsl")
        assert direct == via_doc
