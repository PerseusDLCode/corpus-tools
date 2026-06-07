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

</sch:schema>
