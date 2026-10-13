# Schmidt smoke test: Richard II

Sources: shakespeare.r2.globe.xml sha256 c8d8b91b1ae3a96c; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of Richard II in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1758/1811 (97.1%) pass.
- **With a quotation:** 1026/1049 (97.8%) have it on the cited line.
- **Headword only:** 732/762 (96.1%) have it on the cited line.

| Verdict | Citations |
|---|---|
| headword on cited line | 773 |
| quotation on cited line | 757 |
| quotation on cited line, with differences | 228 |
| headword not found near cited line | 24 |
| not a citation of this play | 16 |
| quotation not found; headword not found near cited line | 8 |
| quotation elsewhere in scene | 2 |
| quotation off by 1 | 1 |
| quotation off by 2 | 1 |
| headword off by 1 | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

None.

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 2.1.280 | R2 II, 1, 280 | Arundel | headword not found near cited line |  |  | (no such line) |
| 4.1.23 | IV, 1 | Bagot | headword not found near cited line |  |  | either i must or have mine honor soiled |
| 1.1.180 | R2 I, 1, 180 | Bar | quotation not found; headword not found near cited line |  | a jewel in a ten times bared up chest, | a jewel in a tentimesbarrdup chest |
| 5.2.46 | R2 V, 2, 46 | Blossom | headword not found near cited line |  |  | welcome my son who are the violets now |
| 2.1.260 | R2 II, 1, 260 | Burdenous | quotation not found; headword not found near cited line |  | burdenous taxations, | his burthenous taxation notwithstanding |
| 1.2.38 | R2 I, 2, 38 | Cause | quotation off by 1 | 1.2.39 | caused his death, | his deputy anointed in his sight |
| 1.2.70 | R2 I, 2, 70 | Cheer | headword not found near cited line |  |  | and what hear there for welcome but my groans |
| 1.2.38 | R2 I, 2, 38 | Deputation | headword not found near cited line |  |  | his deputy anointed in his sight |
| 4.1.65 | R2 IV, 65 | Dishonourable | headword not found near cited line |  |  | surrey thou list dishonorable boy |
| 4.1.210 | R2 IV, 210 | Duteous | quotation not found; headword not found near cited line |  | release all duteous oaths, | with mine own breath release all dutys rites |
| 4.94 | R2 IV, 94 | Ensign | not a citation of this play |  |  |  |
| 1.2.72 | R2 I, 2, 72 | Everywhere | headword not found near cited line |  |  | to seek out sorrow that dwells every where |
| 3.2.88 | R2 III, 2, 88 | Favourite | headword not found near cited line |  |  | ye favorites of a king are we not high |
| 1.3.150 | R2 I, 3, 150 | Fly-slow | headword not found near cited line |  |  | thy sly slow hours shall not determinate |
| 1.3.222 | I, 3, 222 | Hollo | headword not found near cited line |  |  | shall be extinct with age and endless night |
| 2.2.126 | R2 II, 2, 126 | Impossible | headword not found near cited line |  |  | is all unpossible |
| 2.107.3 | 107, 3 | Lease | not a citation of this play |  | the lease of my true love, |  |
| 2.124.10 | 124, 10 | Lease | not a citation of this play |  | it fears not policy, that heretic, which works on leases of short-numbered hours, |  |
| 2.146.5 | 146, 5 | Lease | not a citation of this play |  | why so large cost, having so short a l., dost thou upon thy fading mansion spend? |  |
| 3.2.8 | R2 III, 2, 8 | Long Purples | headword not found near cited line |  |  | as a longparted mother with her child |
| 1.72.2 | 72, 2 | Merit | not a citation of this play |  | what merit lived in me, |  |
| 1.88.2 | 88, 2 | Merit | not a citation of this play |  | place my merit in the eye of scorn, |  |
| 1.108.4 | 108, 4 | Merit | not a citation of this play |  | that may express my love or thy dear merit |  |
| 1.149.9 | 149, 9 | Merit | not a citation of this play |  | what merit do I in myself respect, |  |
| 5.2.45 | V, 2, 45 | New | quotation off by 2 | 5.2.47 | the new come spring, | and lasting fealty to the newmade king |
| 2.3.130 | II, 3, 130 | Patent | headword not found near cited line |  |  | and yet my letterspatents give me leave |
| 5.1.97 | V, 1, 97 | Plague | headword not found near cited line |  |  | give me mine own again twere no good part |
| 5.5.27 | V, 5, 27 | Plague | quotation not found; headword not found near cited line |  | I'll plague thee for that word, | that many have and others must sit there |
| 1.3.3 | R2 I, 3 | Point | quotation elsewhere in scene | 1.3.146-147 | his golden beams to you here lent shall point on me and gild my banishment, | the duke of norfolk sprightfully and bold |
| 1.3.3 | R2 I, 3 | Point | headword off by 1 | 1.3.2 |  | the duke of norfolk sprightfully and bold |
| 3.0 | III Prol. 4 | Pompous | not a citation of this play |  |  |  |
| 3.2.106 | R2 III, 2, 106 | Season | headword not found near cited line |  |  | like an unseasonable stormy day |
| 2.2.3 | R2 II, 2, 3 | Self-harming | headword not found near cited line |  |  | to lay aside lifeharming heaviness |
| 3.2.80 | III, 2, 80 | Serious | quotation not found; headword not found near cited line |  | he did it with a serious mind, | all souls that will be safe fly from my side |
| 3.2.80 | III, 2, 80 | Serious | quotation not found; headword not found near cited line |  | not worth his serious considering, | all souls that will be safe fly from my side |
| 2.1.156 | R2 II, 1, 156 | Shag-haired | headword not found near cited line |  |  | we must supplant those rough rugheaded kerns |
| 5.2.25 | Shr. Ind. 2, 25 | Sheer | not a citation of this play |  | if she say I am not fourteen pence on the score for sheer ale, |  |
| 3.2.84 | R2 III, 2, 84 | Sluggard | headword not found near cited line |  |  | awake thou coward majesty thou sleepest |
| 5.6.8 | R2 V, 6, 8 | Spencer | headword not found near cited line |  |  | the heads of oxford salisbury blunt and kent |
| 4.94 | R2 IV, 94 | Stream | not a citation of this play |  | streaming the ensign of the Christian cross against black pagans, |  |
| 1.3.227 | R2 I, 3, 227 | Sudden | headword not found near cited line |  |  | shorten my days thou canst with sullen sorrow |
| 1.3.227 | R2 I, 3, 227 | Sudden-bold | quotation not found; headword not found near cited line |  | Sudden | shorten my days thou canst with sullen sorrow |
| 5.5.72 | R2 V, 5, 72 | Ten | quotation elsewhere in scene | 5.5.67-68 | hail, royal prince! Thanks, noble peer; the cheapest of us is ten groats too dear, | i was a poor groom of thy stable king |
| 1.1.180 | R2 I, 1, 180 | Ten-times-barred-up | headword not found near cited line |  |  | a jewel in a tentimesbarrdup chest |
| 3.32.14 | 32, 14 | Theirs | not a citation of this play |  |  |  |
| 3.3.56 | R2 III, 3, 56 | Thunder | headword not found near cited line |  |  | of fire and water when their slumbering shock |
| 3.4.45 | R2 III, 4, 45 | Unpruned | headword not found near cited line |  |  | her fruittrees all upturned her hedges ruined |
| 1.3.134 | R2 I, 3, 134 | Untutored | headword not found near cited line |  |  | which so roused up with boisterous untuned drums |
| 1.3.234 | R2 I, 3, 234 | Verdict | quotation not found; headword not found near cited line |  | whereto my tongue a party verdict gave, | whereto thy tongue a partyverdict gave |
| 3.125.4 | 125, 4 | Waste | not a citation of this play |  | more short than waste or ruining, |  |
| 3.129.1 | 129, 1 | Waste | not a citation of this play |  | the expense of spirit in a waste of shame is lust in action, |  |
| 3.0 | III Prol. 35 | Yravish | not a citation of this play |  |  |  |
| 3.0 | III Prol. 1 | Yslake | not a citation of this play |  |  |  |
