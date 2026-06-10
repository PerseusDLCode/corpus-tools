<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron"
            xmlns:tei="http://www.tei-c.org/ns/1.0"
            queryBinding="xslt2">

  <sch:title>Perseus Normalized Document Validation</sch:title>
  <sch:p>Validates that a TEI document has been fully processed by the Perseus
    normalization pipeline (set-genre → normalize-* pipeline).</sch:p>

  <sch:ns prefix="tei" uri="http://www.tei-c.org/ns/1.0"/>

  <!-- ============================================================
       Genre annotation (set-genre.xsl)
       ============================================================ -->

  <sch:pattern id="genre-annotation">
    <sch:title>Genre annotation</sch:title>
    <sch:rule context="tei:profileDesc">
      <sch:assert test="tei:textClass/tei:catRef[@scheme='#perseus-genre']" role="error">
        profileDesc must contain textClass/catRef[@scheme='#perseus-genre'].
        Run set-genre.xsl before the normalization pipeline.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="genre-category">
    <sch:title>Genre category value</sch:title>
    <sch:rule context="tei:catRef[@scheme='#perseus-genre']">
      <sch:let name="valid-genres" value="(
        'drama-line', 'drama-act-scene-line',
        'verse-stichic', 'verse-book-line',
        'prose-standard', 'prose-chapter-section', 'prose-book-section',
        'prose-book-chapter', 'prose-chapter', 'prose-chapter-verse', 'prose-section',
        'drama', 'verse', 'prose'
      )"/>
      <sch:assert test="substring-after(@target, '#') = $valid-genres" role="error">
        catRef target '<sch:value-of select="@target"/>' is not a recognized
        perseus-genre category. Valid targets are the structural subclasses and the
        bare family ids defined in the perseus-genre taxonomy in perseus_base.odd.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ============================================================
       CTS URN (set-cts-urn.xsl)
       ============================================================ -->

  <sch:pattern id="cts-xml-base">
    <sch:title>CTS URN on body</sch:title>
    <sch:rule context="tei:body">
      <sch:assert test="@xml:base" role="error">
        body must carry @xml:base with the CTS URN. Run set-cts-urn.xsl.
      </sch:assert>
      <sch:assert test="starts-with(@xml:base, 'urn:cts:')" role="error">
        body/@xml:base must be a CTS URN (starting with 'urn:cts:').
        Got: <sch:value-of select="@xml:base"/>
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="cts-idno">
    <sch:title>CTS URN in publicationStmt</sch:title>
    <sch:rule context="tei:publicationStmt">
      <sch:assert test="tei:idno[@type='CTS']" role="error">
        publicationStmt must contain idno[@type='CTS']. Run set-cts-urn.xsl.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ============================================================
       Citation structure (add-citeStructure.xsl)
       ============================================================ -->

  <sch:pattern id="refs-decl">
    <sch:title>CTS refsDecl</sch:title>
    <sch:rule context="tei:encodingDesc">
      <sch:assert test="tei:refsDecl[@n='CTS']" role="error">
        encodingDesc must contain refsDecl[@n='CTS']. Run add-citeStructure.xsl.
      </sch:assert>
      <sch:assert test="tei:refsDecl[@n='CTS']/tei:citeStructure" role="error">
        refsDecl[@n='CTS'] must contain a citeStructure element.
        Run add-citeStructure.xsl.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ============================================================
       Schema PI (set-schema.xsl)
       ============================================================ -->

  <sch:pattern id="schema-pi">
    <sch:title>Perseus schema PI</sch:title>
    <sch:rule context="processing-instruction('xml-model')">
      <sch:assert test="contains(., 'PerseusDLCode/perseus-schemas')" role="error">
        xml-model PI does not point to a Perseus schema. Run set-schema.xsl.
        Got: <sch:value-of select="."/>
      </sch:assert>
      <sch:assert test="contains(., 'schematypens')" role="error">
        xml-model PI is missing schematypens attribute. Run set-schema.xsl.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

</sch:schema>
