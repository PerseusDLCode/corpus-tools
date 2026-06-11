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

    <!-- verse-stichic: lines directly in body, no numbered divs above them -->
    <xsl:template name="verse-stichic-cs">
        <refsDecl n="CTS" xml:id="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="line" delim=":" match="l" use="@n"/>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- verse-book-line (epic): lines grouped in numbered book divs -->
    <xsl:template name="verse-book-line-cs">
        <refsDecl n="CTS" xml:id="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="book" delim=":" match="div[@type='book']" use="@n">
                    <citeStructure unit="line" delim="." match="l" use="@n"/>
                </citeStructure>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- drama-line (classical): lines nested inside unnumbered structural divs; cite by line only -->
    <xsl:template name="drama-line-cs">
        <refsDecl n="CTS" xml:id="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="line" delim=":" match=".//l" use="@n"/>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- drama-act-scene-line (early modern): act → scene → line -->
    <xsl:template name="drama-act-scene-line-cs">
        <refsDecl n="CTS" xml:id="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="act" delim=":" match="div[@type='act']" use="@n">
                    <citeStructure unit="scene" delim="." match="div[@type='scene']" use="@n">
                        <citeStructure unit="line" delim="." match="l" use="@n"/>
                    </citeStructure>
                </citeStructure>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- prose-standard: book → chapter → section -->
    <xsl:template name="prose-standard-cs">
        <refsDecl n="CTS" xml:id="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="book" delim=":" match="div[@type='book']" use="@n">
                    <citeStructure unit="chapter" delim="." match="div[@type='chapter']" use="@n">
                        <citeStructure unit="section" delim="." match="div[@type='section']" use="@n"/>
                    </citeStructure>
                </citeStructure>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- prose-chapter-section: chapter → section (no book) -->
    <xsl:template name="prose-chapter-section-cs">
        <refsDecl n="CTS" xml:id="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="chapter" delim=":" match="div[@type='chapter']" use="@n">
                    <citeStructure unit="section" delim="." match="div[@type='section']" use="@n"/>
                </citeStructure>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- prose-book-section: book → section (no chapter) -->
    <xsl:template name="prose-book-section-cs">
        <refsDecl n="CTS" xml:id="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="book" delim=":" match="div[@type='book']" use="@n">
                    <citeStructure unit="section" delim="." match="div[@type='section']" use="@n"/>
                </citeStructure>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- prose-book-chapter: book → chapter (no section) -->
    <xsl:template name="prose-book-chapter-cs">
        <refsDecl n="CTS" xml:id="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="book" delim=":" match="div[@type='book']" use="@n">
                    <citeStructure unit="chapter" delim="." match="div[@type='chapter']" use="@n"/>
                </citeStructure>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- prose-chapter-verse: chapter → verse (New Testament and biblical-style texts) -->
    <xsl:template name="prose-chapter-verse-cs">
        <refsDecl n="CTS" xml:id="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="chapter" delim=":" match="div[@type='chapter']" use="@n">
                    <citeStructure unit="verse" delim="." match="div[@type='verse']" use="@n"/>
                </citeStructure>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- prose-epistle: single epistle/letter level (subtype='epistle' or 'letter') -->
    <xsl:template name="prose-epistle-cs">
        <refsDecl n="CTS" xml:id="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="epistle" delim=":" match=".//div[@type='textpart'][@subtype='epistle' or @subtype='letter']" use="@n"/>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- prose-paragraph: single paragraph level (EpiDoc div[@type='textpart'][@subtype='paragraph']) -->
    <xsl:template name="prose-paragraph-cs">
        <refsDecl n="CTS" xml:id="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="paragraph" delim=":" match=".//div[@type='textpart'][@subtype='paragraph']" use="@n"/>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- prose-fragment: single fragment level (EpiDoc div[@type='textpart'][@subtype='fragment']) -->
    <xsl:template name="prose-fragment-cs">
        <refsDecl n="CTS" xml:id="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="fragment" delim=":" match=".//div[@type='textpart'][@subtype='fragment']" use="@n"/>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- prose-chapter: single chapter level -->
    <xsl:template name="prose-chapter-cs">
        <refsDecl n="CTS" xml:id="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="chapter" delim=":" match="div[@type='chapter']" use="@n"/>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- prose-section: single section level -->
    <xsl:template name="prose-section-cs">
        <refsDecl n="CTS" xml:id="CTS">
            <citeStructure match="/TEI/text/body" use="@xml:base">
                <citeStructure unit="section" delim=":" match="div[@type='section']" use="@n"/>
            </citeStructure>
        </refsDecl>
    </xsl:template>

    <!-- Suppress existing CTS refsDecl; encodingDesc template emits a fresh one -->
    <xsl:template match="encodingDesc/refsDecl[@n='CTS']"/>

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
                <!-- structural subclasses -->
                <xsl:when test="$genre-target = 'verse-book-line'">
                    <xsl:call-template name="verse-book-line-cs"/>
                </xsl:when>
                <xsl:when test="$genre-target = 'verse-stichic'">
                    <xsl:call-template name="verse-stichic-cs"/>
                </xsl:when>
                <xsl:when test="$genre-target = 'drama-act-scene-line'">
                    <xsl:call-template name="drama-act-scene-line-cs"/>
                </xsl:when>
                <xsl:when test="$genre-target = 'drama-line'">
                    <xsl:call-template name="drama-line-cs"/>
                </xsl:when>
                <xsl:when test="$genre-target = 'prose-standard'">
                    <xsl:call-template name="prose-standard-cs"/>
                </xsl:when>
                <xsl:when test="$genre-target = 'prose-chapter-section'">
                    <xsl:call-template name="prose-chapter-section-cs"/>
                </xsl:when>
                <xsl:when test="$genre-target = 'prose-book-section'">
                    <xsl:call-template name="prose-book-section-cs"/>
                </xsl:when>
                <xsl:when test="$genre-target = 'prose-book-chapter'">
                    <xsl:call-template name="prose-book-chapter-cs"/>
                </xsl:when>
                <xsl:when test="$genre-target = 'prose-chapter-verse'">
                    <xsl:call-template name="prose-chapter-verse-cs"/>
                </xsl:when>
                <xsl:when test="$genre-target = 'prose-epistle'">
                    <xsl:call-template name="prose-epistle-cs"/>
                </xsl:when>
                <xsl:when test="$genre-target = 'prose-fragment'">
                    <xsl:call-template name="prose-fragment-cs"/>
                </xsl:when>
                <xsl:when test="$genre-target = 'prose-paragraph'">
                    <xsl:call-template name="prose-paragraph-cs"/>
                </xsl:when>
                <xsl:when test="$genre-target = 'prose-chapter'">
                    <xsl:call-template name="prose-chapter-cs"/>
                </xsl:when>
                <xsl:when test="$genre-target = 'prose-section'">
                    <xsl:call-template name="prose-section-cs"/>
                </xsl:when>
                <!-- bare family targets: apply the family default citeStructure
                     (the catRef is separately marked cert="low" / needs review) -->
                <xsl:when test="$genre-target = 'verse'">
                    <xsl:call-template name="verse-stichic-cs"/>
                </xsl:when>
                <xsl:when test="$genre-target = 'drama'">
                    <xsl:call-template name="drama-line-cs"/>
                </xsl:when>
                <xsl:when test="$genre-target = 'prose'">
                    <xsl:call-template name="prose-standard-cs"/>
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
