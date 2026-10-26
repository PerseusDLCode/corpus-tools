# Schmidt smoke test: The Winter's Tale

Sources: shakespeare.wt.globe.xml sha256 90d7ffb37427ae47; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of The Winter's Tale in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1889/1946 (97.1%) pass.
- **With a quotation:** 1190/1208 (98.5%) have it on the cited line.
- **Headword only:** 699/738 (94.7%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 926 |
| headword on cited line | 740 |
| quotation on cited line, with differences | 223 |
| headword not found near cited line | 21 |
| prose row break | 14 |
| not a citation of this play | 8 |
| quotation off by 1 | 5 |
| headword off by 1 | 4 |
| quotation not found; headword not found near cited line | 3 |
| quotation off by 3 | 1 |
| quotation elsewhere in scene | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

None.

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 4.3.133 | Wint. IV, 3, 133 | A | quotation off by 1 | 4.3.134 | your sad tires in a mile-a, | and merrily hent the stilea |
| 4.4.324 | IV, 4, 324 | A | quotation off by 3 | 4.4.327 | of the newest and finest wear-a, | my dainty duck my deara |
| 4.4.324 | IV, 4, 324 | A | quotation elsewhere in scene | 4.4.330 | that doth utter all men's ware-a, | my dainty duck my deara |
| 2.3.117 | Wint. II, 3, 117 | Accusation | quotation off by 1 | 2.3.118 | to produce more accusation | but this most cruel usage of your queen |
| 4.4.60 | Wint. IV, 4, 60 | Afire | headword not found near cited line |  |  | on his shoulder and his her face o fire |
| 1.1.134 | I, 1, 134 | Antioch | headword not found near cited line |  |  | (no such line) |
| 1.1.134 | I, 1, 134 | Antiochus | headword not found near cited line |  |  | (no such line) |
| 1.1.3 | I, 1, 3 | Antiochus | headword not found near cited line |  |  | services are now on foot you shall see as i have |
| 3.3.70 | Wint. III, 3, 70 | Barn | headword not found near cited line |  |  | will what have we here mercy on s a barne |
| 4.3.20 | Wint. IV, 3, 20 | Bowget | headword not found near cited line |  |  | and bear the sowskin budget |
| 4.4.720 | Wint. IV, 4, 720 | Brother-in-law | prose row break | 4.4.721 |  | me to go about to make me the kings |
| 5.3.289 | V, 3, 289 | Caparison | headword not found near cited line |  |  | (no such line) |
| 3.2.197 | Wint. III, 2, 197 | Cleave | headword not found near cited line |  |  | thoughts high for one so tender cleft the heart |
| 5.1.18 | Shr. Ind. 1, 18. | Couple | not a citation of this play |  | couple Clowder with the deep-mouthed brach, |  |
| 4.81.10 | 81, 10 | Create | not a citation of this play |  |  |  |
| 2.3.146 | Wint. II, 3, 146 | Credit | quotation off by 1 | 2.3.147 | give us better credit | youre liars all |
| 4.3.40 | Wint. IV, 3, 40 | Currant | prose row break | 4.3.41 |  | feast three pound of sugar five pound of |
| 4.2.350 | 2, 350 | Dainty | headword not found near cited line |  |  | (no such line) |
| 2.3.140 | Wint. II, 3, 140 | Dash | headword off by 1 | 2.3.141 |  | the bastard brains with these my proper hands |
| 2.3.195 | II, 3, 195 | Delphos | headword off by 1 | 2.3.196 |  | an hour since cleomenes and dion |
| 3.1.2 | III, 1, 2 | Delphos | headword not found near cited line |  |  | fertile the isle the temple much surpassing |
| 2.3.194 | II, 3, 194 | Dion | headword off by 1 | 2.3.195 |  | from those you sent to the oracle are come |
| 2.1.125 | II, 1, 125 | Easy | quotation not found; headword not found near cited line |  | the easy yielding spirit of this woman, | go do our bidding hence |
| 2.3.138 | Wint. II, 3, 138 | Encounter | headword off by 1 | 2.3.139 |  | with what thou else callst thine if thou refuse |
| 5.2.41 | Wint. V, 2, 41 | Evidence | prose row break | 5.2.42 | evidences, | shows above her breeding and many other |
| 4.86.13 | 86, 13 | File | not a citation of this play |  | when your countenance filed up his line, |  |
| 2.3.87 | II, 3, 87 | Fill | quotation not found; headword not found near cited line |  | have your mouth filled up, | for as the case now stands it is a curse |
| 3.3.78 | Wint. III, 3, 78 | Hallo | prose row break | 3.3.79 |  | for pity yet ill tarry till my son come he |
| 2.1.143 | Wint. II, 1, 143 | Honour-flawed | headword not found near cited line |  |  | i would landdamn him be she honorflawed |
| 1.2.436 | Wint. I, 2, 436 | Impawn | headword not found near cited line |  |  | shall bear along unpawned away tonight |
| 4.4.756 | Wint. IV, 4, 756 | Infoldings | headword not found near cited line |  |  | in these enfoldings hath not my gait in it the |
| 2.3.166 | Wint. II, 3, 166 | Innocent | quotation off by 1 | 2.3.167 | to save the innocent | ill pawn the little blood which i have left |
| 4.4.518 | Wint. IV, 4, 518 | Irremovable | headword not found near cited line |  |  | ill hear you by and by hes irremoveable |
| 1.1.38 | Wint. I, 1, 38 | Mamillius | prose row break | 1.1.39 |  | unspeakable comfort of your young prince |
| 3.3.117 | Wint. III, 3, 117 | New | quotation not found; headword not found near cited line |  | I met with things new born, | mettest with things dying i with things |
| 3.3.14 | III, 3, 14 | O' | quotation off by 1 | 3.3.15 | rid o' the business, | ill follow instantly i am glad at heart |
| 5.2.126 | Wint. V, 2, 126 | Over-fond | prose row break | 5.2.127 |  | and i know not what but he at that time |
| 1.2.424 | Wint. I, 2, 424 | Overswear | headword not found near cited line |  |  | that eer was heard or read swear his thought over |
| 4.4.338 | Wint. IV, 4, 338 | Plentifully | prose row break | 4.4.339 |  | that know little but bowling it will please |
| 3.3.68 | Wint. III, 3, 68 | Sea-side | prose row break | 3.3.69 |  | master if any where i have them tis by the |
| 5.2.106 | Wint. V, 2, 106 | Senior-junior | headword not found near cited line |  |  | julio romano who had he himself eternity and |
| 4.3.35 | Wint. IV, 3, 35 | Shear | headword not found near cited line |  |  | hundred shorn what comes the wool to |
| 4.2.55 | Wint. IV, 2, 55 | Simplicity | prose row break | 4.2.56 |  | question with the shepherd from whose |
| 5.2.57 | Wint. V, 2, 57 | Son-in-law | prose row break | 5.2.58 |  | bohemia forgiveness then embraces his |
| 1.2.389 | Wint. I, 2, 389 | Speed | headword not found near cited line |  |  | i have looked on thousands who have sped the better |
| 4.4.196 | Wint. IV, 4, 196 | Stretch-mouthed | prose row break | 4.4.197 |  | her and thump her and where some |
| 4.2.20 | Wint. IV, 2, 20 | Thankful | prose row break | 4.2.21 |  | considered as too much i cannot to be more |
| 4.3.44 | Wint. IV, 3, 44 | Three-man: | prose row break | 4.3.45 | three-man song-men, | four and twenty nosegays for the shearers |
| 1.2.416 | Wint. I, 2, 416 | Tice | headword not found near cited line |  |  | to vice you tot that you have touched his queen |
| 4.105.5 | 105, 5 | To-day | not a citation of this play |  |  |  |
| 1.80.4 | 80, 4 | Tongue-tied | not a citation of this play |  | a better spirit doth use your name . . . to make me tongue-tied |  |
| 1.85.1 | 85, 1 | Tongue-tied | not a citation of this play |  | my tongue-tied Muse in manners holds her still, |  |
| 1.140.2 | 140, 2 | Tongue-tied | not a citation of this play |  | do not press my tongue-tied patience with too much disdain, |  |
| 4.4.780 | Wint. IV, 4, 780 | Toothpick | headword not found near cited line |  |  | the picking ons teeth |
| 4.2.119 | Shr. Ind. 2, 119. | Undress | not a citation of this play |  | undress you, |  |
| 1.1.37 | Wint. I, 1, 37 | Unspeakable | prose row break | 1.1.38 |  | malice or matter to alter it you have an |
| 5.1.59 | Wint. V, 1, 59 | Vex | headword not found near cited line |  |  | where were offenders now appear soulvexed |
