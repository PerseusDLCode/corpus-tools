# Schmidt smoke test: The Tempest

Sources: shakespeare.tmp.globe.xml sha256 2231dee9085e3257; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of The Tempest in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1683/1766 (95.3%) pass.
- **With a quotation:** 1142/1180 (96.8%) have it on the cited line.
- **Headword only:** 541/586 (92.3%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 882 |
| headword on cited line | 609 |
| quotation on cited line, with differences | 192 |
| not a citation of this play | 36 |
| headword not found near cited line | 25 |
| quotation off by 1 | 6 |
| headword off by 1 | 5 |
| prose row break | 5 |
| quotation not found; headword not found near cited line | 3 |
| quotation off by 2 | 1 |
| quotation elsewhere in scene | 1 |
| quotation in another scene | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

| Scene | Cited lines | Offset | Citations |
|---|---|---|---|
| 2.2 | 126-130 | -1 | 6 |

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 5.276 | Tp. V, 276 | Acknowledge | not a citation of this play |  | this thing of darkness I acknowledge mine, |  |
| 5.304 | Tp. V, 304 | Away | not a citation of this play |  | go quick away |  |
| 4.1.224 | Tp. IV, 224 | Belong | quotation off by 1 | 4.1.225-226 | we know what belongs to a frippery, | let it alone thou fool it is but trash |
| 3.2.38 | III, 2, 38 | Bite | headword off by 1 | 3.2.37 |  | prithee |
| 5.241.83 | V, 241 | Bravely | not a citation of this play |  | was't well done? b., my diligence, |  |
| 4.112 | Tp. IV, 112 | Bunch | not a citation of this play |  | vines with clustering bunches, |  |
| 3.1.17 | Tp. III, 1, 17 | Burn | headword off by 1 | 3.1.18 |  | burnt up those logs that you are enjoined to pile |
| 3.1.15 | Tp. III, 1, 15 | Busyless | headword not found near cited line |  |  | most busy lest when i do it alas now pray you |
| 2.2.126 | II, 2, 126 | Butt | quotation off by 1 | 2.2.125 | boat).*I escaped upon a butt of sack, | sailors heaved oerboard by this bottle which i |
| 2.2.126 | II, 2, 126 | Butt | headword off by 1 | 2.2.125 |  | sailors heaved oerboard by this bottle which i |
| 2.2.129 | Tp. II, 2, 129 | Cast | quotation off by 1 | 2.2.128 | since I was cast ashore, | ill swear upon that bottle to be thy true |
| 3.2.49 | III, 2, 49 | Cheat | prose row break | 3.2.50 |  | tyrant a sorcerer that by his cunning hath |
| 5.1.4 | Shr. Ind. 1, 4. | Chronicle | not a citation of this play |  |  |  |
| 1.2.277 | Tp. I, 2, 277 | Cleave | headword not found near cited line |  |  | into a cloven pine within which rift |
| 2.2.13 | II, 2, 13 | Cleave | headword not found near cited line |  |  | all wound with adders who with cloven tongues |
| 4.112.175 | IV, 112 | Cluster | not a citation of this play |  | vines with clustering bunches, |  |
| 1.2.297 | Tp. I, 2, 297 | Corresponsive | quotation not found; headword not found near cited line |  | massy staples and corresponsive and fulfilling bolts, | i will be correspondent to command |
| 2.2.149 | Tp. II, 2, 149 | Credulous | prose row break | 2.2.150 |  | monster the man i the moon a most poor |
| 1.2.259 | Tp. I, 2, 259 | Crooked | headword not found near cited line |  |  | was grown into a hoop hast thou forgot her |
| 1.49.441 | I, 49 | Delicate | not a citation of this play |  |  |  |
| 1.1.70 | Shr. Ind. 1, 70. | Diligence | not a citation of this play |  | he shall think by our true diligence he is no less than what we say he is, |  |
| 5.241 | Tp. V, 241 | Diligence | not a citation of this play |  | was't well done? Bravely, my diligence |  |
| 2.1.17 | Tp. II, 1, 17 | Dollar | quotation off by 2 | 2.1.19 | dolour: | comes to the entertainer |
| 1.2.29 | Shr. Ind. 2, 29. | Droop | not a citation of this play |  | that makes your servants droop |  |
| 2.1.63 | Tp. II, 1, 63 | Dye | headword not found near cited line |  |  | freshness and glosses being rather newdyed |
| 2.2.131 | Tp. II, 2, 131 | Earthly | prose row break | 2.2.130 | the liquor is not earthly | here swear then how thou escapedst |
| 1.2.125 | Tp. I, 2, 125 | Extol | headword not found near cited line |  |  | should presently extirpate me and mine |
| 4.1.225 | Tp. IV, 225 | Frippery | headword off by 1 | 4.1.226 |  | o ho monster we know what belongs |
| 5.280 | Tp. V, 280 | Gíld | not a citation of this play |  | this grand liquor that hath gílded them, |  |
| 5.280.274 | V, 280 | Grand | not a citation of this play |  | this grand liquor, |  |
| 1.2.17 | Shr. Ind. 2, 17. | Infuse | not a citation of this play |  | infused with so foul a spirit, |  |
| 1.1.46 | Tp. I, 1, 46 | Insolent | prose row break | 1.1.47 |  | hang cur hang you whoreson |
| 4.1.60 | Tp. IV, 60 | Iris | headword not found near cited line |  |  | ceres most bounteous lady thy rich leas |
| 2.1.118 | Tp. II, 1, 118 | Keep | quotation not found; headword not found near cited line |  | he kept his head above the waves, | bove the contentious waves he kept and oared |
| 2.1.118 | Tp. II, 1, 118 | Keep | quotation elsewhere in scene | 2.1.299 | to keep them living, | bove the contentious waves he kept and oared |
| 5.33.35 | V, 33 | Lake | not a citation of this play |  |  |  |
| 2.2.73 | Tp. II, 2, 73 | Leather | headword not found near cited line |  |  | that ever trod on neatsleather |
| 5.10 | Tp. V, 10 | Line-grove | not a citation of this play |  |  |  |
| 4.231 | Tp. IV, 231 | Luggage | not a citation of this play |  | to dote thus on such luggage |  |
| 5.1.298 | V, 298 | Luggage | quotation off by 1 | 5.1.299 | bestow your luggage where you found it, | go to away |
| 3.2.37 | Tp. III, 2, 37 | Natural | prose row break | 3.2.35-36 | that a monster should be such a natural | lo lo again bite him to death i |
| 5.1.95 | Shr. Ind. 1, 95. | Odd | not a citation of this play |  | over-eyeing of his odd behaviour, |  |
| 3.2.75 | III, 2, 75 | Odd | quotation not found; headword not found near cited line |  | some odd humour pricks him to this fashion, | where the quick freshes are |
| 2.2.127 | Tp. II, 2, 127 | O'erboard | headword off by 1 | 2.2.126 |  | made of the bark of a tree with mine own hands |
| 3.3.98 | Tp. III, 3, 98 | Orgillous | headword not found near cited line |  |  | that deep and dreadful organpipe pronounced |
| 5.212.4 | V, 212 | Ourselves | not a citation of this play |  |  |  |
| 4.1.38 | IV, 1, 38 | Over | headword not found near cited line |  |  | oer whom i give thee power here to this place |
| 4.1.32 | IV Prol. 32 | Paphos | headword not found near cited line |  |  | sit then and talk with her she is thine own |
| 4.1.61 | Tp. IV, 1, 61 | Pea | headword not found near cited line |  |  | of wheat rye barley vetches oats and pease |
| 4.74 | Tp. IV, 74 | Peacock | not a citation of this play |  |  |  |
| 4.1.64 | Tp. IV, 64 | Peonied | headword not found near cited line |  |  | thy banks with pioned and twilled brims |
| 5.1.299 | V, 1 | Project | headword not found near cited line |  |  | hence and bestow your luggage where you found it |
| 5.1.299 | V, 1 | Project | headword not found near cited line |  |  | hence and bestow your luggage where you found it |
| 5.1.46 | Tp. V, 46 | Promontory | headword not found near cited line |  |  | with his own bolt the strongbased promon tory |
| 5.189.159 | V, 189 | Providence | not a citation of this play |  |  |  |
| 5.132 | Tp. V, 132 | Rank | not a citation of this play |  | I do forgive thy rankest fault, |  |
| 4.1.82 | Tp. IV, 82 | Scarf | headword not found near cited line |  |  | rich scaff to my proud earth why hath thy queen |
| 5.187 | Tp. V, 187 | Sever | not a citation of this play |  |  |  |
| 5.256 | Tp. V, 256 | Shift | not a citation of this play |  | every man shift for all the rest, |  |
| 4.1.19 | Shr. Ind. 1, 19. | Silver | not a citation of this play |  |  |  |
| 2.96.13 | 96, 13 | Sort | not a citation of this play |  |  |  |
| 2.2.176 | Tp. II, 2, 176 | Staniel | headword not found near cited line |  |  | young scamels from the rock wilt thou go with me |
| 1.1.192 | Tp. I, 1, 192 | Task | quotation in another scene | 1.2.192 | to thy strong bidding task Ariel and all his quality, | (no such line) |
| 3.2.3 | Shr. Ind. 2, 3. | Taste | not a citation of this play |  | taste of these conserves, |  |
| 2.1.254 | Tp. II, 1, 254 | Theirs | headword not found near cited line |  |  | in yours and my discharge what stuff is this how say you |
| 5.264.63 | V, 264 | Thing | not a citation of this play |  | what things are these, |  |
| 5.264.63 | V, 264 | Thing | not a citation of this play |  | this thing of darkness, |  |
| 5.264.63 | V, 264 | Thing | not a citation of this play |  | this is as strange a thing as e'er I looked on, |  |
| 4.1.12 | Shr. Ind. 1, 12. | Thirdborough | not a citation of this play |  |  |  |
| 5.178.27 | V, 178 | Though | not a citation of this play |  | though the seas threaten, they are merciful, |  |
| 4.1.3 | Tp. IV, 3 | Thread | headword not found near cited line |  |  | have given you here a thrid of mine own life |
| 1.1.17 | Shr. Ind. 1, 17 | Trash | not a citation of this play |  |  |  |
| 2.2.140 | Tp. II, 2, 140 | Unaptness | headword not found near cited line |  |  | hast thou not dropped from heaven |
| 5.1.221 | Tp. V, 221 | Unluckily | headword not found near cited line |  |  | the best news is that we have safely found |
| 2.2.126 | II, 2, 126 | Upon | quotation off by 1 | 2.2.125 | I escaped upon a butt of sack, | sailors heaved oerboard by this bottle which i |
| 2.2.130 | Tp. II, 2, 130 | Upon | quotation off by 1 | 2.2.129 | I'll swear upon that bottle, | subject for the liquor is not earthly |
| 2.2.10 | II, 2, 10 | Urchin | headword not found near cited line |  |  | and after bite me then like hedgehogs which |
| 4.135.3 | 135, 3 | Vex | not a citation of this play |  | more than enough am I that vex thee still, |  |
| 4.148.10 | 148, 10 | Vex | not a citation of this play |  | how can love's eye be true, that is so vexed with watching and with tears? |  |
| 5.10 | Tp. V, 10 | Weather-fend | not a citation of this play |  | the line-grove which weather-fends your cell, |  |
| 4.1.21 | IV Prol. 21 | Weave | headword not found near cited line |  |  | the union of your bed with weeds so loathly |
| 1.150.5 | 150, 5 | Whence | not a citation of this play |  | whence hast thou this becoming of things ill, |  |
| 5.1.111 | Tp. V, 111 | Whe'r | headword not found near cited line |  |  | a hearty welcome whether thou best he or no |
