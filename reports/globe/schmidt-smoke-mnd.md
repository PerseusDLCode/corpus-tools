# Schmidt smoke test: A Midsummer Night's Dream

Sources: shakespeare.mnd.globe.xml sha256 f0112443c2d96514; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of A Midsummer Night's Dream in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1359/1440 (94.4%) pass.
- **With a quotation:** 820/836 (98.1%) have it on the cited line.
- **Headword only:** 539/604 (89.2%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 658 |
| headword on cited line | 573 |
| quotation on cited line, with differences | 128 |
| not a citation of this play | 39 |
| headword not found near cited line | 31 |
| prose row break | 5 |
| headword off by 1 | 4 |
| quotation not found; headword not found near cited line | 1 |
| quotation elsewhere in scene | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

None.

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 5.1.107 | Mids. V, 107 | Address | headword off by 1 | 5.1.106 |  | let him approach |
| 3.1.54 | Mids. III, 1, 54 | Almanac | prose row break | 3.1.55 |  | a calendar a calendar look in the |
| 2.2.61 | Shr. Ind. 2, 61. | Apollo | not a citation of this play |  |  |  |
| 4.1.207 | IV, 1, 207 | Bellows-mender: | prose row break | 4.1.208 |  | pyramus heighho peter quince flute the |
| 5.14 | Mids. V, 14 | Body | not a citation of this play |  | as imagination bodyies forth the form of things unknown, |  |
| 3.2.426 | Mids. III, 2, 426 | By | headword off by 1 | 3.2.427 |  | nay then thou mockst me thou shalt buy this dear |
| 3.2.389 | Mids. III, 2, 389 | Cephalus | headword not found near cited line |  |  | i with the mornings love have oft made sport |
| 1.1.129 | Mids. I, 1, 129 | Cheek-roses | headword not found near cited line |  |  | how chance the roses there do fade so fast |
| 2.1.54 | Mids. II, 1, 54 | Coffe | headword not found near cited line |  |  | and tailor cries and falls into a cough |
| 1.2.98 | Mids. I, 2, 98 | Coloured | quotation not found; headword not found near cited line |  | French crown coloured beard, | crowncolor beard your perfect yellow |
| 3.1.2 | Mids. III, 1, 2 | Convenient | prose row break | 3.1.3 | convenient place, | pat pat and heres a marvellous |
| 3.114.1 | 114, 1 | Crown | not a citation of this play |  | whether doth my mind, being crowned with you, drink up the monarch's plague, this flattery, |  |
| 3.107.7 | 107, 7 | Crown | not a citation of this play |  | incertainties now crown themselves assured, |  |
| 3.115.12 | 115, 12 | Crown | not a citation of this play |  | crowning the present, doubting of the rest, |  |
| 2.2.59 | Shr. Ind. 2, 59. | Daphne | not a citation of this play |  |  |  |
| 2.1.79 | Mids. II, 1, 79 | Eagles | headword not found near cited line |  |  | and make him with fair aegle break his faith |
| 4.2.48 | Shr. Ind. 2, 48 | Echo | not a citation of this play |  |  |  |
| 5.139.12 | 139, 12 | Elsewhere | not a citation of this play |  |  |  |
| 2.1.6 | Mids. II, 1, 6 | Everywhere | headword not found near cited line |  |  | i do wander every where |
| 5.190.125 | V, 190 | Full | not a citation of this play |  |  |  |
| 5.140 | Mids. V, 140 | Grisly | not a citation of this play |  |  |  |
| 5.1.241 | Mids. V, 241 | Hearken | headword not found near cited line |  |  | well leave it to his discretion and let us listen to |
| 5.140 | Mids. V, 140 | Hight | not a citation of this play |  | this grisly beast, which lion hight by name, |  |
| 4.0 | IV Prol. 18 | Hight | not a citation of this play |  |  |  |
| 2.1.168 | Mids. II, 1, 168 | Idleness | headword not found near cited line |  |  | and maidens call it loveinidleness |
| 1.58.6 | 58, 6 | Imprison | not a citation of this play |  |  |  |
| 3.154.3 | 154, 3 | Keep | not a citation of this play |  | vowed chaste life to keep |  |
| 2.0 | II Prol. 20 | Killen | not a citation of this play |  |  |  |
| 5.1.198 | Mids. V, 198 | Leander | headword not found near cited line |  |  | and like limander am i trusty still |
| 2.1.55 | Mids. II, 1, 55 | Loffe | headword not found near cited line |  |  | and then the whole quire hold their hips and laugh |
| 5.35 | Mids. V, 35 | Manager | not a citation of this play |  | where is our usual manager of mirth? |  |
| 4.1.26 | IV, 1, 26 | Marvellous | headword not found near cited line |  |  | barbers monsieur for methinks i am mar vellous |
| 2.1.9 | Mids. II, 1, 9 | Meadow | headword not found near cited line |  |  | to dew her orbs upon the green |
| 5.1.330 | Mids. V, 330 | Moan | headword not found near cited line |  |  | and thus she means videlicet |
| 2.1.98 | Mids. II, 1, 98 | Morris-dance | headword not found near cited line |  |  | the nine mens morris is filled up with mud |
| 2.1.98 | Mids. II, 1, 98 | Morris-dance | headword not found near cited line |  |  | the nine mens morris is filled up with mud |
| 2.1.98 | Mids. II, 1, 98 | Morris-dance | headword not found near cited line |  |  | the nine mens morris is filled up with mud |
| 2.1.98 | Mids. II, 1, 98 | Morris-dance | headword not found near cited line |  |  | the nine mens morris is filled up with mud |
| 2.1.98 | Mids. II, 1, 98 | Morris-dance | headword not found near cited line |  |  | the nine mens morris is filled up with mud |
| 2.1.98 | Mids. II, 1, 98 | Morris-dance | headword not found near cited line |  |  | the nine mens morris is filled up with mud |
| 2.1.98 | Mids. II, 1, 98 | Morris-dance | headword not found near cited line |  |  | the nine mens morris is filled up with mud |
| 2.1.98 | Mids. II, 1, 98 | Morris-dance | headword not found near cited line |  |  | the nine mens morris is filled up with mud |
| 2.1.98 | Mids. II, 1, 98 | Morris-dance | headword not found near cited line |  |  | the nine mens morris is filled up with mud |
| 2.10.11 | 10, 11 | Morris-dance | not a citation of this play |  |  |  |
| 2.10.11 | 10, 11 | Morris-dance | not a citation of this play |  |  |  |
| 3.2.204 | Mids. III, 2, 204 | Neeld | headword not found near cited line |  |  | have with our needles created both one flower |
| 4.1.137 | IV, 1, 137 | Observance | headword not found near cited line |  |  | no doubt they rose up early to observe |
| 1.1.167 | I, 1, 167 | Observation | headword not found near cited line |  |  | to do observance to a morn of may |
| 4.1.137 | IV, 1, 137 | Observation | headword not found near cited line |  |  | no doubt they rose up early to observe |
| 3.1.84 | Mids. III, 1, 84 | Odorous | headword off by 1 | 3.1.85 |  | thisby the flowers of odious savors sweet |
| 4.1.126 | Shr. Ind. 1, 126. | Onion | not a citation of this play |  |  |  |
| 1.1.126 | Mids. I, 1, 126 | Over | quotation elsewhere in scene | 1.1.226 | how happy some o'er other some can be, | of something nearly that concerns yourselves |
| 3.1.197 | Mids. III, 1, 197 | Ox-beef | prose row break | 3.1.198 |  | patience well that same cowardly giant like |
| 5.1.343 | Mids. V, 343 | Parca | headword not found near cited line |  |  | o sisters three |
| 5.188.2 | V, 188 | Pat | not a citation of this play |  | it will fall pat as I told you, |  |
| 1.2.44 | Shr. Ind. 2, 44. | Pearl | not a citation of this play |  |  |  |
| 2.355.44 | II, 355 | Pearl | not a citation of this play |  |  |  |
| 5.1.77 | V, 1, 77 | Pearl | headword not found near cited line |  |  | it is not for you i have heard it over |
| 3.0 | III Prol. 21 | Quest | not a citation of this play |  |  |  |
| 3.85.3 | 85, 3 | Quill | not a citation of this play |  |  |  |
| 5.142.57 | V, 142 | Rather | not a citation of this play |  | did scare away, or rather did affright, |  |
| 2.2.4 | Mids. II, 2, 4 | Rear-mice | headword not found near cited line |  |  | some war with reremice for their leathern wings |
| 5.5.103 | 5, 103 | Right | not a citation of this play |  |  |  |
| 3.2.73 | Shr. Ind. 2, 73. | Savour | not a citation of this play |  | I smell sweet savours, |  |
| 5.142 | Mids. V, 142 | Scare | not a citation of this play |  | to scare away: |  |
| 5.1.347 | Mids. V, 347 | Shear | headword off by 1 | 5.1.348 |  | since you have shore |
| 5.1.279 | Mids. V, 279 | Stream | headword not found near cited line |  |  | for by thy gracious golden glittering gleams |
| 3.1.4 | Mids. III, 1, 4 | Tiring-house | prose row break | 3.1.5 |  | shall be our stage this hawthornbrake our |
| 5.60.9 | 60, 9 | Transfix | not a citation of this play |  |  |  |
| 2.2.107 | Mids. II, 2, 107 | Upon | headword not found near cited line |  |  | is that vile name to perish on my sword |
| 5.35 | Mids. V, 35 | Usual | not a citation of this play |  |  |  |
| 5.234.12 | V, 234 | Very | not a citation of this play |  | a very fox for his valour, |  |
| 3.123.13 | 123, 13 | Vow | not a citation of this play |  |  |  |
| 3.152.4 | 152, 4 | Vow | not a citation of this play |  |  |  |
| 5.2.65 | Shr. Ind. 2, 65. | Wane | not a citation of this play |  |  |  |
| 2.403.65 | II, 403 | Wane | not a citation of this play |  |  |  |
| 2.126.3 | 126, 3 | Wane | not a citation of this play |  | who hast by waneing grown, and therein showest thy lovers withering as thy sweet self growest, |  |
| 5.1.326 | Mids. V, 326 | Warn | headword not found near cited line |  |  | man god warrant us she for a woman god |
| 3.132.8 | 132, 8 | West | not a citation of this play |  |  |  |
| 1.54.45 | I, 54 | Wind | not a citation of this play |  |  |  |
| 2.1.38 | Shr. Ind. 1, 38. | Wrap | not a citation of this play |  |  |  |
