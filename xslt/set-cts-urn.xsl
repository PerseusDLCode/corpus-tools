<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns="http://www.tei-c.org/ns/1.0"
    xpath-default-namespace="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs"
    version="4.0">
    <xsl:output method="xml" indent="yes"/>
    <xsl:mode on-no-match="shallow-copy"/>

    <!-- Override only when the auto-computed URN would be wrong (e.g. pdlrefwk) -->
    <xsl:param name="cts-base" as="xs:string" select="''"/>

    <xsl:variable name="effective-cts-base" as="xs:string" select="
        if ($cts-base != '') then $cts-base
        else concat(
            'urn:cts:',
            replace(base-uri(/), '^.*canonical[-_]([^/]+)/.*$', '$1'),
            ':',
            replace(base-uri(/), '^.*/([^/]+)\.xml$', '$1'))"/>

    <xsl:template match="body">
        <xsl:copy>
            <xsl:apply-templates select="@* except @xml:base"/>
            <xsl:attribute name="xml:base" select="$effective-cts-base"/>
            <xsl:apply-templates select="node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="publicationStmt">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()[not(self::idno[@type='CTS'])]"/>
            <idno type="CTS"><xsl:value-of select="$effective-cts-base"/></idno>
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>
