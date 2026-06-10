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
        $target: xml:id of the perseus-genre category, either a structural subclass
            (verse-book-line, verse-stichic, drama-line, drama-act-scene-line,
            prose-standard) or a bare family (verse, drama, prose) when only the family
            is known.
        $cert: when non-empty (typically "low"), the catRef is marked
            cert="$cert" resp="#corpus-tools" to flag a needs-review classification
            (family default applied, or a proposed subclass not yet verified against
            the document's structure).
        The stylesheet adds (or replaces) <textClass><catRef> in <profileDesc>.
    -->
    <xsl:param name="target" as="xs:string" select="''"/>
    <xsl:param name="cert" as="xs:string" select="''"/>

    <xsl:template match="profileDesc">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:if test="$target != ''">
                <textClass>
                    <catRef scheme="#perseus-genre" target="#{$target}">
                        <xsl:if test="$cert != ''">
                            <xsl:attribute name="cert" select="$cert"/>
                            <xsl:attribute name="resp">#corpus-tools</xsl:attribute>
                        </xsl:if>
                    </catRef>
                </textClass>
            </xsl:if>
            <xsl:apply-templates select="node()[not(self::textClass)]"/>
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>
