<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns="http://www.tei-c.org/ns/1.0"
    xpath-default-namespace="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs"
    version="4.0">
    <xsl:output method="xml" indent="yes"/>
    <xsl:mode on-no-match="shallow-copy"/>

    <xsl:param name="cts-base" as="xs:string" select="''"/>
    <xsl:param name="genre" as="xs:string" select="'prose'"/>

    <xsl:template name="prose-citestructure">
        <refsDecl n="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="book" delim=":" match="div[@type='book']" use="@n">
                    <citeStructure unit="chapter" delim="." match="div[@type='chapter']" use="@n">
                        <citeStructure unit="section" delim="." match="div[@type='section']" use="@n"/>
                    </citeStructure>
                </citeStructure>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- REVIEW: adjust match/unit hierarchy for your verse texts -->
    <xsl:template name="verse-citestructure">
        <refsDecl n="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="book" delim=":" match="div[@type='book']" use="@n">
                    <citeStructure unit="line" delim="." match="l" use="@n"/>
                </citeStructure>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- REVIEW: adjust match/unit hierarchy for your drama texts -->
    <xsl:template name="drama-citestructure">
        <refsDecl n="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="act" delim=":" match="div[@type='act']" use="@n">
                    <citeStructure unit="scene" delim="." match="div[@type='scene']" use="@n">
                        <citeStructure unit="line" delim="." match="l" use="@n"/>
                    </citeStructure>
                </citeStructure>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <xsl:template match="encodingDesc">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
            <xsl:choose>
                <xsl:when test="$genre = 'verse'">
                    <xsl:call-template name="verse-citestructure"/>
                </xsl:when>
                <xsl:when test="$genre = 'drama'">
                    <xsl:call-template name="drama-citestructure"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:call-template name="prose-citestructure"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>
