# Schmidt smoke test: Measure for Measure

Sources: shakespeare.mm.globe.xml sha256 232389531dce409f; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of Measure for Measure in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1682/1770 (95.0%) pass.
- **With a quotation:** 1153/1189 (97.0%) have it on the cited line.
- **Headword only:** 529/581 (91.0%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 953 |
| headword on cited line | 554 |
| quotation on cited line, with differences | 175 |
| not a citation of this play | 28 |
| headword not found near cited line | 20 |
| prose row break | 15 |
| quotation off by 1 | 14 |
| headword off by 1 | 5 |
| quotation elsewhere in scene | 4 |
| headword off by 2 | 1 |
| quotation not found; headword not found near cited line | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

| Scene | Cited lines | Offset | Citations |
|---|---|---|---|
| 3.2 | 48-55 | -1 | 6 |
| 3.2 | 72-75 | -1 | 3 |

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 3.1.201 | III, 1, 201 | Accusation | prose row break | 3.1.202 |  | the matter now stands he will avoid your |
| 5.408 | Meas. V, 408 | Adjudge | not a citation of this play |  | he adjudged your brother, |  |
| 3.2.66 | III, 2, 66 | Amiss | quotation off by 1 | 3.2.65 | 'tis not amiss | farewell go say i sent thee thither for debt |
| 3.2.72 | Meas. III, 2, 72 | Antiquity | quotation off by 1 | 3.2.71 | bawd is he doubtless, and of antiquity too, | bawdborn farewell good pompey commend me |
| 5.59 | Meas. V, 59 | Badness | not a citation of this play |  |  |  |
| 3.2.77 | Meas. III, 2, 77 | Bail | prose row break | 3.2.75-76 | your good worship will be my bail | no indeed will i not pompey it is |
| 3.2.44 | Meas. III, 2, 44 | Bail | quotation off by 1 | 3.2.43 | I cry bail | gentleman and a friend of mine |
| 5.92.7 | 92, 7 | Belong | not a citation of this play |  | a better state to me belongs than that which on thy humour doth depend, |  |
| 5.350 | Meas. V, 350 | Bolt | not a citation of this play |  | lay bolts enough upon him! |  |
| 2.2.20 | Shr. Ind. 2, 20. | Card-maker | not a citation of this play |  |  |  |
| 3.1.52 | Shr. Ind. 1, 52. | Chance | not a citation of this play |  |  |  |
| 3.2.50 | Meas. III, 2, 50 | Clutch | quotation off by 1 | 3.2.48-49 | putting the hand in the pocket and extracting it clutched, | reply ha what sayest thou to this tune matter |
| 1.2.8 | Meas. I, 2, 8 | Commandment | prose row break | 1.2.9 |  | sanctimonious pirate that went to sea with the ten |
| 5.428 | Meas. V, 428 | Confiscation | not a citation of this play |  |  |  |
| 1.66.311 | I, 66 | Conflict | not a citation of this play |  |  |  |
| 5.428 | Meas. V, 428 | Confutation | not a citation of this play |  |  |  |
| 4.3.14 | Meas. IV, 3, 14 | Copper-spur | prose row break | 4.3.15 |  | young master deepvow and master |
| 4.3.133 | Meas. IV, 3, 133 | Covent | headword not found near cited line |  |  | one of our convent and his confessor |
| 4.1.92 | Shr. Ind. 1, 92. | Cunning | not a citation of this play |  | some sport wherein your cunning can assist me much, |  |
| 2.4.1 | Meas. II, 4, 1 | Devotement | headword not found near cited line |  |  | when i would pray and think i think and pray |
| 3.1.246 | Meas. III, 1, 246 | Discovery | quotation elsewhere in scene | 3.1.236 | pretending in her discoveryies of dishonour, | brother but keeps you from dishonour in doing it |
| 4.6.12 | IV, 6, 12 | Dizzy | headword not found near cited line |  |  | he shall not pass you twice have the trumpets sounded |
| 5.256.33 | V, 256 | Do | not a citation of this play |  | do with your injuries as seems you best, |  |
| 1.2.50 | Meas. I, 2, 50 | Dollar | headword not found near cited line |  |  | to three thousand dolours a year |
| 3.2.72 | Meas. III, 2, 72 | Doubtless | quotation off by 1 | 3.2.71 | bawd he is doubtless | bawdborn farewell good pompey commend me |
| 1.2.192 | Meas. I, 2, 192 | Encouragement | prose row break | 1.2.193 |  | i pray she may as well for the |
| 3.1.91 | Meas. III, 1, 91 | Enew | headword not found near cited line |  |  | nips youth i the head and follies doth emmew |
| 2.132.7 | 132, 7 | Even | not a citation of this play |  |  |  |
| 3.2.50 | Meas. III, 2, 50 | Extract | quotation off by 1 | 3.2.48-49 | putting the hand in the pocket and extracting it clutched, | reply ha what sayest thou to this tune matter |
| 2.4.122 | Meas. II, 4, 122 | Fedary | headword not found near cited line |  |  | if not a feodary but only he |
| 5.126.51 | V, 126 | Ghostly | not a citation of this play |  |  |  |
| 5.1.346 | Meas. V, 346 | Gloze | headword not found near cited line |  |  | hark how the villain would close now |
| 5.1.328 | Meas. V, 328 | Good-man | prose row break | 5.1.329 | good-man baldpate, | tis he my lord come hither |
| 5.276 | Meas. V, 276 | Handle | not a citation of this play |  | if you handled her, |  |
| 2.1.12 | Shr. Ind. 1, 12 | Headborough | not a citation of this play |  |  |  |
| 3.2.60 | Meas. III, 2, 60 | Herself | headword off by 1 | 3.2.59 |  | why tis good it is the right of it it |
| 5.1.263 | Meas. V, 263 | Hood | headword not found near cited line |  |  | cucullus non facit monachum honest |
| 1.5.85 | I, 5, 85 | Increase | not a citation of this play |  |  |  |
| 3.2.10 | Meas. III, 2, 10 | Innocency | prose row break | 3.2.11 |  | too to signify that craft being richer than |
| 4.1.17 | Meas. IV, 1, 17 | Inquire | headword off by 1 | 4.1.16 |  | me here today much upon this time have i |
| 5.1.249 | Meas. V, 249 | Instate | quotation elsewhere in scene | 5.1.427-429 | for his possessions . . . we do instate and widow you withal, | let him be sent for |
| 4.1.130 | Shr. Ind. 1, 130. | Instruction | not a citation of this play |  | I'll give thee more instructions, |  |
| 3.2.75 | Meas. III, 2, 75 | Keep | quotation off by 1 | 3.2.74 | you will keep the house, | i hope sir your good worship will be |
| 3.2.75 | Meas. III, 2, 75 | Keep | quotation off by 1 | 3.2.74 | you will keep the house, | i hope sir your good worship will be |
| 3.2.214 | Meas. III, 2, 214 | Keep | quotation off by 1 | 3.2.215 | myself, | old come philip and jacob i have kept it |
| 3.2.186 | Meas. III, 2, 186 | Lecherous | prose row break | 3.2.187 |  | build in his houseeaves because they are |
| 5.459 | Meas. V, 459 | Merely | not a citation of this play |  | but m.: |  |
| 3.2.52 | Meas. III, 2, 52 | Method | quotation off by 1 | 3.2.50-51 | what sayest thou to this tune, matter and m.? | ha what sayest thou trot is the world as it |
| 5.2.67 | Shr. Ind. 2, 67. | O'errun | not a citation of this play |  | the tears . . . o'errun her lovely face, |  |
| 5.428 | Meas. V, 428 | Ours | not a citation of this play |  |  |  |
| 3.68.1 | 68, 1 | Outwear | not a citation of this play |  | thus is his cheek the map of days outworn, |  |
| 4.3.157 | Meas. IV, 3, 157 | Pale-hearted | headword not found near cited line |  |  | o pretty isabella i am pale at mine |
| 3.1.209 | Meas. III, 1, 209 | Peradventure | prose row break | 3.1.210 |  | and much please the absent duke if |
| 3.0 | III Prol. 15 | Perch | not a citation of this play |  |  |  |
| 2.1.263 | Meas. II, 1, 263 | Plain-dealing | headword not found near cited line |  |  | tent and prove a shrewd caesar to you in plain |
| 3.2.58 | Meas. III, 2, 58 | Procure | quotation off by 1 | 3.2.57 | procures she still? | troth sir she hath eaten up all her beef |
| 2.0 | II Prol. 29 | Promise | not a citation of this play |  |  |  |
| 3.1.271 | III, 1, 271 | Prosperous | prose row break | 3.1.272 |  | already and i trust it will grow to a most |
| 4.4.5 | 4, 5 | Public | headword not found near cited line |  |  | heaven his wisdom be not tainted and why |
| 3.6.11 | III, 6, 11 | Public | not a citation of this play |  | in the public eye, |  |
| 3.2.48 | Meas III, 2, 48 | Pygmalion | headword off by 1 | 3.2.47 |  | made woman to be had now for putting the hand |
| 1.1.91 | Shr. Ind. 1, 91. | Rather | not a citation of this play |  | the rather for I have some sport in hand, |  |
| 5.1.522 | Meas. V, 522 | Recompense | prose row break | 5.1.523 |  | made you a duke good my lord do not |
| 2.1.258 | Meas. II, 1, 258 | Requital | prose row break | 2.1.259 |  | thank you good pompey and in |
| 2.1.169 | Meas. II, 1, 169 | Respect | quotation off by 1 | 2.1.170-172 | the house is a respected house, this is a respected fellow, and his mistress is a respected woman, | say you to it |
| 2.1.169 | Meas. II, 1, 169 | Respect | quotation elsewhere in scene | 2.1.176-177 | the time is yet to come that she was ever respected with man, woman, or child, | say you to it |
| 2.1.169 | Meas. II, 1, 169 | Respect | quotation elsewhere in scene | 2.1.178-179 | she was respected with him before he married with her, | say you to it |
| 2.1.169 | Meas. II, 1, 169 | Respect | headword off by 2 | 2.1.171 |  | say you to it |
| 5.3.143 | V, 3 | Return | not a citation of this play |  |  |  |
| 5.424 | Meas. V, 424 | Safeguard | not a citation of this play |  | to the safeguard of your honour, |  |
| 3.1.89 | III, 1, 89 | Sainted | headword not found near cited line |  |  | in base appliances this outwardsainted deputy |
| 4.1.63 | Meas. IV, 1, 63 | Scape | headword not found near cited line |  |  | upon thy doings thousand escapes of wit |
| 2.4.9 | Meas. II, 4, 9 | Sear | headword not found near cited line |  |  | grown feared and tedious yea my gravity |
| 2.1.92 | Meas. II, 1, 92 | Stewed | prose row break | 2.1.93 |  | longing saving your honours reverence for |
| 2.1.162 | Meas. II, 1, 162 | Suppose | headword off by 1 | 2.1.163 |  | why no |
| 4.1.76 | Meas. IV, 1, 76 | Tilth | headword not found near cited line |  |  | our corns to reap for yet our tithes to sow |
| 5.141.25 | V, 141 | Touch | not a citation of this play |  | free from touch or soil with her, |  |
| 3.2.55 | Meas. III, 2, 55 | Trick | quotation off by 1 | 3.2.52-54 | is the world as it was, man? which is the way? is it sad, and few words, or how? the trick of it? | still thus and thus still worse |
| 3.2.53 | Meas. III, 2, 53 | Trot | headword off by 1 | 3.2.52 |  | was man which is the way is it sad and |
| 3.2.60 | Meas. III, 2, 60 | Tub | prose row break | 3.2.59 | she is herself in the tub | why tis good it is the right of it it |
| 2.1.82 | Meas. II, 1, 82 | Uncleanliness | prose row break | 2.1.83 |  | accused in fornication adultery and all |
| 3.2.63 | Meas. III, 2, 63 | Unshunned | quotation off by 1 | 3.2.62 | an unshunned consequence, | be so art going to prison pompey |
| 4.6.4 | Meas. IV, 6, 4 | Vailful | headword not found near cited line |  |  | he says to veil full purpose be ruled by him |
| 4.5.8 | Meas. IV, 5, 8 | Valencius | headword not found near cited line |  |  | to valentinus rowland and to crassus |
| 5.1.9 | 1, 9 | Vouch | headword not found near cited line |  |  | o your desert speaks loud and i should wrong it |
| 5.1.9 | 1, 9 | Vouch | headword not found near cited line |  |  | o your desert speaks loud and i should wrong it |
| 3.1.300 | III, 1, 300 | Vouch | quotation not found; headword not found near cited line |  | which, I dare v., is more than that he hath, | (no such line) |
| 4.3.104 | Meas. IV, 3, 104 | Weald | headword not found near cited line |  |  | by cold gradation and wellbalanced form |
