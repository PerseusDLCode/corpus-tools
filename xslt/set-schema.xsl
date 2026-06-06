<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xpath-default-namespace="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs"
    version="4.0">
    <xsl:output method="xml" indent="yes" />
    <xsl:mode on-no-match="shallow-copy"/>

    <!-- Set the validation schema for the file from a parameter.
         Defaults to perseus_base -->
    <xsl:param name="tei-schema" as="xs:string" select="'perseus_base'" />

    <xsl:param name="schema-path-base" as="xs:string" select="'https://raw.githubusercontent.com/PerseusDLCode/perseus-schemas/main/'" />

    <xsl:variable name="schema-path" as="xs:string"
        select="concat($schema-path-base, normalize-space(translate($tei-schema, &quot;'&quot;, '')), '.rnc')"/>

    <!-- Match the xml-model PI and replace the href -->
    <xsl:template match="processing-instruction('xml-model')">
        <xsl:processing-instruction name="xml-model"
            select="concat('href=&quot;', $schema-path, '&quot; schematypens=&quot;http://relaxng.org/ns/structure/1.0&quot;')"/>
    </xsl:template>

</xsl:stylesheet>
