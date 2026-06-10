<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron"
            xmlns:tei="http://www.tei-c.org/ns/1.0"
            queryBinding="xslt2">

  <sch:title>Perseus Encoding Anomaly Review</sch:title>
  <sch:p>Advisory checks that flag encoding patterns requiring human review
    before correction. Findings here are not pipeline errors; they are issues
    to investigate and resolve editorially.</sch:p>

  <sch:ns prefix="tei" uri="http://www.tei-c.org/ns/1.0"/>

  <!-- ============================================================
       Sentence markup
       ============================================================ -->

  <sch:pattern id="empty-s-milestone">
    <sch:title>Empty s element used as milestone</sch:title>
    <sch:rule context="tei:s">
      <sch:report test="not(node())" role="warning">
        Empty &lt;s/&gt; used as a sentence milestone rather than a segment.
        Investigate the encoder's intent before correcting; consider replacing
        with &lt;milestone unit="sentence"/&gt; or restructuring as a wrapping element.
      </sch:report>
    </sch:rule>
  </sch:pattern>

  <!-- ============================================================
       Legacy (TEI P4) elements
       Elements carried over from the P4 corpus that are not part of
       the curated Perseus P5 schema. They are flagged here so editors
       can migrate them by hand; they remain invalid against the RNG.
       Together these account for ~99% of remaining validate-corpus
       errors on canonical-greekLit (said ~101K, docAuthor ~8.4K, reg ~4.3K).
       ============================================================ -->

  <sch:pattern id="legacy-said">
    <sch:title>P4 legacy element: said</sch:title>
    <sch:rule context="tei:said">
      <sch:report test="true()" role="warning">
        &lt;said&gt; is a TEI P4 element not in the Perseus P5 schema.
        Migrate to &lt;q&gt; for quoted speech. Review @direct (direct vs.
        reported discourse) and preserve @who before converting.
      </sch:report>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="legacy-docAuthor">
    <sch:title>P4 legacy element: docAuthor</sch:title>
    <sch:rule context="tei:docAuthor">
      <sch:report test="true()" role="warning">
        &lt;docAuthor&gt; is not part of the curated Perseus P5 schema.
        For a work's author, use &lt;author&gt; inside titleStmt. Check the
        containing context before converting (title page vs. bibliographic).
      </sch:report>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="legacy-reg">
    <sch:title>P4 legacy element: reg</sch:title>
    <sch:rule context="tei:reg">
      <sch:report test="true()" role="warning">
        Standalone &lt;reg&gt; is not allowed in the Perseus P5 schema.
        Pair the regularization with the original reading inside a choice:
        &lt;choice&gt;&lt;orig&gt;…&lt;/orig&gt;&lt;reg&gt;…&lt;/reg&gt;&lt;/choice&gt;.
      </sch:report>
    </sch:rule>
  </sch:pattern>

  <!-- ============================================================
       Genre classification needs review
       ============================================================ -->

  <sch:pattern id="genre-needs-review">
    <sch:title>Genre set to family default / unverified subclass</sch:title>
    <sch:rule context="tei:catRef[@scheme='#perseus-genre']">
      <sch:report test="@cert='low' or substring-after(@target, '#') = ('drama', 'verse', 'prose')"
                  role="warning">
        Genre classification needs review: the catRef targets a bare family
        ('<sch:value-of select="substring-after(@target, '#')"/>') or is marked
        cert="low". The family-default citeStructure was applied but no structural
        subclass has been verified against the document's actual citation structure.
      </sch:report>
    </sch:rule>
  </sch:pattern>

</sch:schema>
