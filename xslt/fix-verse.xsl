<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns="http://www.tei-c.org/ns/1.0"
    xpath-default-namespace="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs"
    version="4.0">
    <xsl:output method="xml" indent="yes"/>
    <xsl:mode on-no-match="shallow-copy"/>

    <!--
        Normalize metrical encoding in Perseus verse texts.

        - @ana='#met-*' values are converted to @met using the controlled
          vocabulary defined in perseus_verse.odd.
        - Placeholder @met values ('u', 'U') are stripped: they carry no
          metrical information and were used by encoders when the meter was
          unknown or inapplicable (e.g. English translations of Greek verse).
    -->

    <!-- @ana-based meter annotations -->
    <xsl:template match="l[@ana='#met-dact'] | l[@ana='#met-hexameter']">
        <xsl:copy>
            <xsl:apply-templates select="@* except @ana"/>
            <xsl:attribute name="met">dactylic-hexameter</xsl:attribute>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>

    <!-- Strip placeholder met values ('u', 'U' = unknown/unannotated) -->
    <xsl:template match="l[@met = ('u', 'U')]">
        <xsl:copy>
            <xsl:apply-templates select="@* except @met"/>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>
