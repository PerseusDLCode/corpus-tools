# Schmidt smoke test: Romeo and Juliet

Sources: shakespeare.rom.globe.xml sha256 2f5a6d64c41e1f99; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of Romeo and Juliet in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1661/1750 (94.9%) pass.
- **With a quotation:** 951/987 (96.4%) have it on the cited line.
- **Headword only:** 710/763 (93.1%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 764 |
| headword on cited line | 740 |
| quotation on cited line, with differences | 157 |
| headword not found near cited line | 31 |
| not a citation of this play | 26 |
| quotation off by 1 | 11 |
| headword off by 1 | 8 |
| quotation not found; headword not found near cited line | 7 |
| prose row break | 6 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

| Scene | Cited lines | Offset | Citations |
|---|---|---|---|
| 2.2 | 151-156 | +1 | 3 |

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 3.1.171 | Rom. III, 1, 171 | Agincourt | headword not found near cited line |  |  | his agile arm beats down their fatal points and |
| 3.1.171 | Rom. III, 1, 171 | Agincourt | headword not found near cited line |  |  | his agile arm beats down their fatal points and |
| 4.7.92 | IV, 7, 92 | Agincourt | not a citation of this play |  |  |  |
| 1.1.141 | Rom. I, 1, 141 | All-cheering | quotation off by 1 | 1.1.140 | the all-cheering sun, | should in the furthest east begin to draw |
| 3.5.182 | Rom. III, 5, 182 | Ally | headword not found near cited line |  |  | of fair demesnes youthful and nobly trained |
| 5.3.216 | Rom. V, 3, 216 | Ambiguity | quotation off by 1 | 5.3.217 | till we can clear these ambiguityies, | seal up the mouth of outrage for a while |
| 5.2.4 | Rom. V, 2, 4 | Barefoot | quotation off by 1 | 5.2.5 | a barefoot brother, | or if his mind be writ give me his letter |
| 4.3.8 | Rom. IV, 3, 8 | Behooveful | headword not found near cited line |  |  | as are behoveful for our state tomorrow |
| 1.111.11 | 111, 11 | Bitterness | not a citation of this play |  | no bitterness that I will bitter think, |  |
| 1.1.96 | Rom. I, 1, 96 | Broil | headword not found near cited line |  |  | three civil brawls bred of an airy word |
| 1.4.56 | Rom. I, 4, 56 | Burgomaster | headword not found near cited line |  |  | on the forefinger of an alderman |
| 2.2.151 | Rom. II, 2, 151 | By | headword off by 1 | 2.2.152 |  | i do beseech thee |
| 2.2.38 | Shr. Ind. 2, 38. | Caged | not a citation of this play |  | caged nightingales, |  |
| 3.5.136 | Rom. III, 5, 136 | Calm | quotation off by 1 | 3.5.137 | a sudden calm | who raging with thy tears and they with them |
| 2.0 | Rom. II Chor. | Charm | not a citation of this play |  | bewitched by the charm of looks, |  |
| 2.0 | Rom. II Chor. | Charm | not a citation of this play |  |  |  |
| 4.4.26 | Rom. IV, 4, 26 | Chat | headword off by 1 | 4.4.25 |  | make haste the bridegroom he is come already |
| 5.3.12 | Rom. V, 3, 12 | Circuit | quotation not found; headword not found near cited line |  | (sweet tomb that in thy circuit dost contain the perfect model of eternity, | sweet flower with flowers thy bridal bed i strew |
| 2.4.16 | Rom. II, 4, 16 | Cleave | headword not found near cited line |  |  | of his heart cleft with the blind bowboys |
| 2.4.16 | Rom. II, 4, 16 | Cleave | headword not found near cited line |  |  | of his heart cleft with the blind bowboys |
| 5.3.68 | Rom. V, 3, 68 | Commiseration | headword not found near cited line |  |  | i do defy thy conjurations |
| 2.0 | Rom. II Chor. | Complain | not a citation of this play |  | to his foe supposed he must complain |  |
| 2.0 | Rom. II Chor. | Complain | not a citation of this play |  |  |  |
| 2.4.51 | Rom. II, 4, 51 | Conceive | prose row break | 2.4.52 |  | the slip sir the slip can you not |
| 3.5.129 | Rom. III, 5, 129 | Conduit | quotation off by 1 | 3.5.130 | a c., girl? | it rains downright |
| 1.4.84 | Rom. I, 4, 84 | Countermine | headword not found near cited line |  |  | of breaches ambuscadoes spanish blades |
| 1.1.157 | Rom. I, 1, 157 | Discovery | quotation off by 1 | 1.1.156 | so far from sounding and discovery | as is the bud bit with an envious worm |
| 5.6.2 | 6, 2 | Distill | not a citation of this play |  | let not winter's ragged hand deface in thee thy summer, ere thou be distilled, |  |
| 5.54.14 | 54, 14 | Distill | not a citation of this play |  | my verse distills your truth, |  |
| 5.119.2 | 119, 2 | Distill | not a citation of this play |  | Siren tears, distilled from limbecks foul as hell within, |  |
| 3.5.66 | Rom. III, 5, 66 | Down | quotation off by 1 | 3.5.67 | is she not down so late? | who ist that calls is it my lady mother |
| 3.5.128 | Rom. III, 5, 128 | Downfall | headword not found near cited line |  |  | but for the sunset of my brothers son |
| 3.5.126 | Rom. III, 5, 126 | Drizzle | quotation off by 1 | 3.5.127 | doth drizzle dew, | and see how he will take it at your hands |
| 2.4.34 | Rom. II, 4, 34 | Fashion-monger | prose row break | 2.4.35 |  | afflicted with these strange flies these |
| 2.4.34 | Rom. II, 4, 34 | Fashion-monging | prose row break | 2.4.35 |  | afflicted with these strange flies these |
| 1.4.85 | Rom. I, 4, 85 | Fathom | headword not found near cited line |  |  | of healths fivefathom deep and then anon |
| 2.0 | Rom. II Chor. | Gape | not a citation of this play |  | young affection gapes to be his heir, |  |
| 2.0 | Rom. II Chor. | Gape | not a citation of this play |  |  |  |
| 1.2.58 | Rom. I, 2, 58 | Godgigoden | headword not found near cited line |  |  | god gi godden i pray sir can you |
| 1.21.12 | 21, 12 | Gold | not a citation of this play |  | those gold candles, |  |
| 2.5.57 | Rom. II, 5, 57 | Handsome | prose row break | 2.5.58 |  | gentleman and a courteous and a kind and a |
| 2.4.100 | Rom. II, 4, 100 | Hare-finder | headword not found near cited line |  |  | against the hair |
| 2.4.100 | Rom. II, 4, 100 | Hare-finder | headword not found near cited line |  |  | against the hair |
| 1.1.109 | Rom. I, 1, 109 | Judgment-place | headword not found near cited line |  |  | to old freetown our common judgementplace |
| 4.1.36 | Rom. IV, 1, 36 | Leisure | quotation off by 1 | 4.1.37 | are you at leisure now? | it may be so for it is not mine own |
| 1.1.185 | Rom. I, 1, 185 | Lightness | headword off by 1 | 1.1.184 |  | misshapen chaos of wellseeming forms |
| 4.4.21 | Rom. IV, 4, 21 | Loggerhead | headword off by 1 | 4.4.20 |  | the county will be here with music straight |
| 1.1.7 | I, 1, 7 | Macbéth | quotation not found; headword not found near cited line |  | heath: | i strike quickly being moved |
| 1.2.65 | I, 2, 65 | Macbéth | quotation not found; headword not found near cited line |  | death: | ye say honestly rest you merry |
| 3.5.4 | III, 5, 4 | Macbéth | headword not found near cited line |  |  | nightly she sings on yond pomegranatetree |
| 3.1.49 | Rom. III, 1, 49 | Minstrel | prose row break | 3.1.50 |  | consort what dost thou make us |
| 2.4.22 | Rom. II, 4, 22 | Minum | headword not found near cited line |  |  | distance and proportion rests me his minim |
| 3.1.124 | Rom. III, 1, 124 | Mo | quotation not found; headword not found near cited line |  | mo days, | this days black fate on more days doth depend |
| 2.30.4 | 30, 4 | New | not a citation of this play |  | and with old woes new wail my dear time's waste, |  |
| 2.30.4 | 30, 4 | New | not a citation of this play |  | which I new pay as if not paid before, |  |
| 2.52.12 | 52, 12 | New | not a citation of this play |  | by new unfolding his imprisoned pride, |  |
| 2.0 | II Prol. 12 | New | not a citation of this play |  | her new beloved, |  |
| 2.1.38 | Rom. II, 1, 38 | Open-arse | headword not found near cited line |  |  | an open et caetera thou a poperin pear |
| 2.4.35 | Rom. II, 4, 35 | Pardonmees | quotation not found; headword not found near cited line |  | 'pardon me': | fashionmongers these perdonamis who stand so much |
| 1.2.52 | Rom. I, 2, 52 | Plantain | headword not found near cited line |  |  | your plaintainleaf is excellent for that |
| 2.4.64 | Rom. II, 4, 64 | Fump | quotation off by 1 | 2.4.65-66 | till thou hast worn out thy p. | why then is my pump well flowered |
| 5.3.261 | Rom. V, 3, 261 | Scare | headword off by 1 | 5.3.262 |  | and bear this work of heaven with patience |
| 2.2.156 | Rom. II, 2, 156 | Schoolboy | headword off by 1 | 2.2.157 |  | a thousand times the worse to want thy light |
| 3.0 | III Prol. 16 | Search | not a citation of this play |  |  |  |
| 1.1.220 | Rom. I, 1, 220 | Seduce | headword not found near cited line |  |  | nor ope her lap to saintseducing gold |
| 1.1.135 | Rom. I, 1, 135 | Self | quotation not found; headword not found near cited line |  | my weary self | pursued my humour not pursuing his |
| 1.3.33 | Rom. I, 3, 33 | Shakespeare | headword not found near cited line |  |  | shake quoth the dovehouse twas no need i trow |
| 1.3.33 | Rom. I, 3, 33 | Shakespeare | headword not found near cited line |  |  | shake quoth the dovehouse twas no need i trow |
| 2.4.136 | Rom. II, 4, 136 | Soho | headword not found near cited line |  |  | a bawd a bawd a bawd so ho |
| 1.1.204 | Rom. I, 1, 204 | Somewhere | headword not found near cited line |  |  | this is not romeo hes some other where |
| 4.5.138 | Rom. IV, 5, 138 | Soundpost | prose row break | 4.5.139 |  | pretty too what say you james |
| 3.5.127 | Rom. III, 5, 127 | Sunset | headword off by 1 | 3.5.128 |  | when the sun sets the air doth drizzle dew |
| 2.0 | Rom. II Chor. | Suppose | not a citation of this play |  | to his foe supposed he must complain, |  |
| 2.0 | Rom. II Chor. | Suppose | not a citation of this play |  |  |  |
| 2.0 | Rom. II Chor. | Sweet | not a citation of this play |  | tempering extremities with extreme sweet |  |
| 2.0 | Rom. II Chor. | Sweet | not a citation of this play |  |  |  |
| 1.118.5 | 118, 5 | Sweetness | not a citation of this play |  | being full of your s., to bitter sauces did I frame my feeding, |  |
| 2.0 | Rom. II Chor. | Temper | not a citation of this play |  | tempering extremities with extreme sweet, |  |
| 2.0 | Rom. II Chor. | Temper | not a citation of this play |  |  |  |
| 1.1.94 | Rom. I, 1, 94 | Temper | headword not found near cited line |  |  | throw your mistempered weapons to the ground |
| 2.2.153 | Rom. II, 2, 153 | Thrive | quotation off by 1 | 2.2.154 | so thrive my soul, | to cease thy suit and leave me to my grief |
| 1.60.1 | 60, 1 | Towards | not a citation of this play |  | as the waves make towards the pebbled shore, |  |
| 2.1.39 | Rom. II, 1, 39 | Truckle-bed | headword not found near cited line |  |  | romeo good night ill to my tucklebed |
| 2.1.39 | Rom. II, 1, 39 | Trundle-bed | headword not found near cited line |  |  | romeo good night ill to my tucklebed |
| 1.2.3 | 2, 3 | Unharmed | headword not found near cited line |  |  | for men so old as we to keep the peace |
| 1.2.72 | Rom. I, 2, 72 | Valentio | headword off by 1 | 1.2.71 |  | daughters my fair niece rosaline livia signior |
| 1.5.19 | Rom. I, 5, 19 | Walk | headword not found near cited line |  |  | unplagued with corns will have a bout with you |
| 1.2.27 | Rom. I, 2, 27 | Well-appointed | quotation not found; headword not found near cited line |  | Appoint | when wellapparelled april on the heel |
| 5.3.3 | Rom. V, 3, 3 | Yew | headword not found near cited line |  |  | under yond yewtrees lay thee all along |
