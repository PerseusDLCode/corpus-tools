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
        Meter is properly encoded using the met attribute;
        Persesus texts sometimes use the ana attribute.
        
        TODO: establish fixed vocabulary for Greek and Latin
        meter in the schemas.
    -->
        
    
    <!-- properly encode dactylic meter -->
    <xsl:template match="l[@ana='#met-dact']">
        <xsl:copy>
            <xsl:apply-templates select="@* except @ana"/>
            <xsl:attribute name="met">dact</xsl:attribute>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>

    <!-- properly encode hexameter -->
    <xsl:template match="l[@ana='#met-hexameter']">
        <xsl:copy>
            <xsl:apply-templates select="@* except @ana"/>
            <xsl:attribute name="met">hexameter</xsl:attribute>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>
    
    
    
</xsl:stylesheet>