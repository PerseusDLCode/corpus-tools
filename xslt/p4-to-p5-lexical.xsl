<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  xmlns:map="http://www.w3.org/2005/xpath-functions/map"
  xmlns:local="local:"
  xmlns="http://www.tei-c.org/ns/1.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0"
  exclude-result-prefixes="xs map local"
  version="3.0">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:mode on-no-match="shallow-copy"/>

  <!--
    Normalised language code map: P4 informal codes -> BCP47 / ISO 639-3.
    Override by passing a different map via a tunnel parameter if needed for
    other lexica (e.g. a Latin dictionary that uses different codes).
  -->
  <xsl:variable name="lang-map" as="map(xs:string, xs:string)" select="
    map{
      'greek' : 'grc',
      'la'    : 'lat',
      'fr'    : 'fra',
      'en'    : 'eng'
    }"/>

  <!-- ============================================================
       Attribute removal
       ============================================================ -->

  <!-- P4 teiHeader/@type is not valid in P5 -->
  <xsl:template match="teiHeader/@type"/>

  <!-- P4 refsDecl/@doctype is not valid in P5 -->
  <xsl:template match="refsDecl/@doctype"/>

  <!-- P4 ref/@targOrder is not valid in P5 -->
  <xsl:template match="@targOrder"/>

  <!-- ============================================================
       id= -> xml:id=
       ============================================================ -->

  <!-- Generic @id -> @xml:id on any element that doesn't already have xml:id -->
  <xsl:template match="@id[not(parent::*/@xml:id)]">
    <xsl:attribute name="xml:id" select="."/>
  </xsl:template>

  <!-- ============================================================
       lang= -> xml:lang= with code normalisation
       ============================================================ -->

  <xsl:template match="@lang">
    <xsl:variable name="code" select="string(.)"/>
    <xsl:attribute name="xml:lang" select="($lang-map($code), $code)[1]"/>
  </xsl:template>

  <!-- language/@id -> language/@ident (priority overrides general @id rule) -->
  <xsl:template match="language/@id" priority="2">
    <xsl:variable name="code" select="string(.)"/>
    <xsl:attribute name="ident" select="($lang-map($code), $code)[1]"/>
  </xsl:template>

  <!-- ============================================================
       P4 division elements -> P5 div
       ============================================================ -->

  <xsl:template match="div0 | div1 | div2">
    <div>
      <xsl:apply-templates select="@* | node()"/>
    </div>
  </xsl:template>

  <!-- ============================================================
       refsDecl/state -> refState
       ============================================================ -->

  <xsl:template match="refsDecl/state">
    <refState>
      <xsl:apply-templates select="@unit | @n"/>
    </refState>
  </xsl:template>

  <!-- ============================================================
       trans/tr: provisional conversion pending study of P5
       Dictionary Module translation encoding.
       trans is unwrapped; tr becomes seg[@type='translation']
       so all instances are findable via //seg[@type='translation'].
       ============================================================ -->

  <xsl:template match="trans">
    <xsl:apply-templates select="node()"/>
  </xsl:template>

  <xsl:template match="tr">
    <seg type="translation">
      <xsl:apply-templates select="@* | node()"/>
    </seg>
  </xsl:template>

  <!-- ============================================================
       entry/@key -> entry/@sortKey
       P4 uses @key as a Beta Code lookup key on entries.
       P5 has no direct equivalent; @sortKey is the closest standard
       attribute (from att.sortable). Provisional — review when
       defining the Perseus citation/lookup convention for lexica.
       ============================================================ -->

  <xsl:template match="entry/@key | entryFree/@key">
    <xsl:attribute name="n" select="."/>
  </xsl:template>

  <!-- ============================================================
       anchored="yes/no" -> "true/false"  (P4 boolean -> P5 boolean)
       ============================================================ -->

  <xsl:template match="@anchored">
    <xsl:attribute name="anchored">
      <xsl:choose>
        <xsl:when test=". = 'yes'">true</xsl:when>
        <xsl:when test=". = 'no'">false</xsl:when>
        <xsl:otherwise><xsl:value-of select="."/></xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
  </xsl:template>

  <!-- ============================================================
       Normalise @type and @unit values that contain spaces
       (e.g. "alphabetic letter" violates the teidata.enumerated regex).
       Convert space-separated words to camelCase.
       ============================================================ -->

  <xsl:function name="local:camelCase" as="xs:string">
    <xsl:param name="s" as="xs:string"/>
    <xsl:variable name="words" select="tokenize(normalize-space($s), '\s+')"/>
    <xsl:value-of select="
      string-join((
        lower-case($words[1]),
        for $w in subsequence($words, 2)
          return concat(upper-case(substring($w, 1, 1)), lower-case(substring($w, 2)))
      ), '')"/>
  </xsl:function>

  <xsl:template match="@type[contains(., ' ')]">
    <xsl:attribute name="type" select="local:camelCase(.)"/>
  </xsl:template>

  <xsl:template match="@unit[contains(., ' ')]">
    <xsl:attribute name="unit" select="local:camelCase(.)"/>
  </xsl:template>

  <!-- ============================================================
       biblStruct: move idno siblings inside monogr, before imprint
       P4: <biblStruct><monogr>...<imprint/></monogr><idno/></biblStruct>
       P5: idno must be inside monogr and before imprint
       ============================================================ -->

  <xsl:template match="biblStruct[idno]">
    <biblStruct>
      <xsl:apply-templates select="@*"/>
      <xsl:for-each select="monogr">
        <monogr>
          <xsl:apply-templates select="@*"/>
          <xsl:apply-templates select="* except imprint"/>
          <xsl:apply-templates select="../idno"/>
          <xsl:apply-templates select="imprint"/>
        </monogr>
      </xsl:for-each>
      <xsl:apply-templates select="* except (monogr | idno)"/>
    </biblStruct>
  </xsl:template>

  <!-- ============================================================
       revisionDesc/change: flatten P4 respStmt + item structure
       P4: <change><date/><respStmt><name/><resp/></respStmt><item/></change>
       P5: change allows inline content; not respStmt or item
       ============================================================ -->

  <xsl:template match="revisionDesc/change">
    <change>
      <xsl:apply-templates select="@*"/>
      <xsl:apply-templates select="date"/>
      <xsl:apply-templates select="respStmt/name"/>
      <xsl:for-each select="item">
        <p><xsl:apply-templates select="node()"/></p>
      </xsl:for-each>
    </change>
  </xsl:template>

</xsl:stylesheet>
