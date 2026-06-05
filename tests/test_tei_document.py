from pathlib import Path

import pytest
from lxml import etree

from tei import TEIDocument, TEI_NS


TEI_TAG = f"{{{TEI_NS}}}TEI"


class TestPath:
    def test_path_is_path_object(self, thucydides_grc):
        assert isinstance(thucydides_grc.path, Path)

    def test_path_preserves_filename(self, thucydides_grc):
        assert thucydides_grc.path.name == "tlg0003.tlg001.perseus-grc2.xml"


class TestRoot:
    def test_root_is_element(self, thucydides_grc):
        assert isinstance(thucydides_grc.root, etree._Element)

    def test_root_tag_is_tei(self, thucydides_grc):
        assert thucydides_grc.root.tag == TEI_TAG


class TestBaseUrn:
    def test_base_urn_thucydides(self, thucydides_grc):
        assert thucydides_grc.base_urn == "urn:cts:greekLit:tlg0003.tlg001.perseus-grc2"

    def test_base_urn_homer(self, tlg0001_tlg001_perseus_grc2):
        assert tlg0001_tlg001_perseus_grc2.base_urn == "urn:cts:greekLit:tlg0001.tlg001.perseus-grc2"

    def test_base_urn_aristotle_grc(self, tlg0086_tlg034_perseus_grc2):
        assert tlg0086_tlg034_perseus_grc2.base_urn == "urn:cts:greekLit:tlg0086.tlg034.perseus-grc2"

    def test_base_urn_virgil(self, phi1017_phi007_perseus_lat2):
        assert phi1017_phi007_perseus_lat2.base_urn == "urn:cts:latinLit:phi1017.phi007.perseus-lat2"

    def test_base_urn_absent_returns_empty_string(self, phi2331_phi013_perseus_lat2):
        assert phi2331_phi013_perseus_lat2.base_urn == ""

    def test_base_urn_absent_grc(self, tlg0057_tlg069_1st1K_grc1):
        assert tlg0057_tlg069_1st1K_grc1.base_urn == ""

    def test_base_urn_absent_eng(self, tlg0086_tlg034_perseus_eng2):
        assert tlg0086_tlg034_perseus_eng2.base_urn == ""

    def test_base_urn_is_cts_urn(self, thucydides_grc):
        assert thucydides_grc.base_urn.startswith("urn:cts:")


class TestRefsDecls:
    def test_single_refs_decl(self, thucydides_grc):
        assert len(thucydides_grc.refsDecls) == 1

    def test_multiple_refs_decls(self, phi1017_phi007_perseus_lat2):
        assert len(phi1017_phi007_perseus_lat2.refsDecls) == 2

    def test_multiple_refs_decls_aristotle(self, tlg0086_tlg034_perseus_grc2):
        assert len(tlg0086_tlg034_perseus_grc2.refsDecls) == 2

    def test_refs_decls_are_elements(self, thucydides_grc):
        for rd in thucydides_grc.refsDecls:
            assert isinstance(rd, etree._Element)


class TestCiteStructures:
    def test_has_cite_structure(self, thucydides_grc):
        assert len(thucydides_grc.cite_structures) == 1

    def test_no_cite_structures_sophocles(self, tlg0011_tlg001_perseus_grc2):
        assert len(tlg0011_tlg001_perseus_grc2.cite_structures) == 0

    def test_no_cite_structures_virgil(self, phi1017_phi007_perseus_lat2):
        assert len(phi1017_phi007_perseus_lat2.cite_structures) == 0

    def test_no_cite_structures_aristotle_grc(self, tlg0086_tlg034_perseus_grc2):
        assert len(tlg0086_tlg034_perseus_grc2.cite_structures) == 0

    def test_cite_structures_are_elements(self, thucydides_grc):
        for cs in thucydides_grc.cite_structures:
            assert isinstance(cs, etree._Element)


class TestDefaultRefsDecl:
    def test_has_default_refs_decl(self, thucydides_grc):
        assert len(thucydides_grc.default_refsDecl) == 1

    def test_no_default_refs_decl_virgil(self, phi1017_phi007_perseus_lat2):
        assert len(phi1017_phi007_perseus_lat2.default_refsDecl) == 0

    def test_no_default_refs_decl_sophocles(self, tlg0011_tlg001_perseus_grc2):
        assert len(tlg0011_tlg001_perseus_grc2.default_refsDecl) == 0

    def test_default_refs_decl_is_element(self, thucydides_grc):
        assert isinstance(thucydides_grc.default_refsDecl[0], etree._Element)
