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
        Reads the genre from <textClass><catRef scheme="#perseus-genre" target="#..."/>
        in the document's <profileDesc> and appends the appropriate <refsDecl n="CTS">
        to <encodingDesc>.

        The document MUST have been annotated with set-genre.xsl before this stylesheet
        is applied. The transformation terminates with an error if no catRef is found,
        or if the target does not match a known perseus-genre category.
    -->

    <xsl:variable name="genre-target" as="xs:string"
        select="replace(
            (//profileDesc/textClass/catRef[@scheme='#perseus-genre']/@target)[1],
            '^#', '')"/>

    <!-- Flat verse (lyric, didactic): lines directly in body, no numbered divs above them -->
    <xsl:template name="verse-citestructure">
        <refsDecl n="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="line" delim="." match="l" use="@n"/>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- Epic verse: lines grouped in numbered book divs -->
    <xsl:template name="verse-epic-citestructure">
        <refsDecl n="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="book" delim=":" match="div[@type='book']" use="@n">
                    <citeStructure unit="line" delim="." match="l" use="@n"/>
                </citeStructure>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- Greek/Roman drama: lines nested inside unnumbered structural divs; cite by line only -->
    <xsl:template name="drama-citestructure">
        <refsDecl n="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="line" delim="." match=".//l" use="@n"/>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- Early-modern drama: act → scene → line -->
    <xsl:template name="drama-early-modern-citestructure">
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

    <!-- Prose: book → chapter → section -->
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

    <xsl:template match="encodingDesc">
        <xsl:if test="$genre-target = ''">
            <xsl:message terminate="yes">
ERROR: No genre catRef found in profileDesc.
Run set-genre.xsl first to assign:
  &lt;textClass&gt;&lt;catRef scheme="#perseus-genre" target="#CATEGORY"/&gt;&lt;/textClass&gt;
Valid categories are defined in the perseus-genre taxonomy in perseus_base.odd.
            </xsl:message>
        </xsl:if>
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
            <xsl:choose>
                <xsl:when test="$genre-target = 'verse-epic'">
                    <xsl:call-template name="verse-epic-citestructure"/>
                </xsl:when>
                <xsl:when test="$genre-target = ('verse-didactic', 'verse-elegiac',
                                'verse-lyric-choral', 'verse-lyric-pindaric',
                                'verse-lyric-monodic', 'verse-satiric',
                                'verse-epigram', 'verse-iambic')">
                    <xsl:call-template name="verse-citestructure"/>
                </xsl:when>
                <xsl:when test="$genre-target = 'early-modern-drama'">
                    <xsl:call-template name="drama-early-modern-citestructure"/>
                </xsl:when>
                <xsl:when test="$genre-target = ('attic-tragedy', 'attic-comedy',
                                'roman-comedy', 'roman-tragedy')">
                    <xsl:call-template name="drama-citestructure"/>
                </xsl:when>
                <xsl:when test="$genre-target = ('prose-historiography', 'prose-philosophy',
                                'prose-dialogue', 'prose-oratory', 'prose-biography',
                                'prose-epistolary', 'prose-geography')">
                    <xsl:call-template name="prose-citestructure"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:message terminate="yes">
ERROR: Unrecognized perseus-genre category: '<xsl:value-of select="$genre-target"/>'.
Valid categories are defined in the perseus-genre taxonomy in perseus_base.odd.
                    </xsl:message>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>
