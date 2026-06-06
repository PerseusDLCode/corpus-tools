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
        $target: xml:id of the genre category in the perseus-genre taxonomy, e.g.:
            prose-historiography, attic-tragedy, verse-epic, verse-didactic, …
        The stylesheet adds (or replaces) <textClass><catRef> in <profileDesc>.
    -->
    <xsl:param name="target" as="xs:string" select="''"/>

    <xsl:template match="profileDesc">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:if test="$target != ''">
                <textClass>
                    <catRef scheme="#perseus-genre" target="#{$target}"/>
                </textClass>
            </xsl:if>
            <xsl:apply-templates select="node()[not(self::textClass)]"/>
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>
