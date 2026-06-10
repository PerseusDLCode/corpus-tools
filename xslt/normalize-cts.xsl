<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns="http://www.tei-c.org/ns/1.0"
    xpath-default-namespace="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs"
    version="4.0">
    <xsl:output method="xml" indent="yes"/>
    <xsl:mode on-no-match="shallow-copy"/>

    
    <!-- remove EpiDoc-inspired top-level attributes -->
    <xsl:template match="div[@type='edition'] | div[@type='translation']">
        <xsl:apply-templates />
    </xsl:template>
    
    <!-- hoist div subtypes to types; lower-case so subtype="Book" -> type="book"
         (citeStructure match patterns and the structural matcher expect lowercase units) -->
    <xsl:template match="div[@type='textpart' and @subtype]">
        <xsl:copy>
            <xsl:apply-templates select="@* except (@type, @subtype)"/>
            <xsl:attribute name="type" select="lower-case(@subtype)"/>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>
    
      <!-- remove @xml:base attributes;
    CTS URNs are calculated from <citeStructure>-->
    <xsl:template match="@xml:base" />
    
    
</xsl:stylesheet>