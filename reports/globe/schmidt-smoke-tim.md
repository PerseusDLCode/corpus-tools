# Schmidt smoke test: Timon of Athens

Sources: shakespeare.tim.globe.xml sha256 c22729e4d7c887e6; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of Timon of Athens in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1441/1495 (96.4%) pass.
- **With a quotation:** 904/926 (97.6%) have it on the cited line.
- **Headword only:** 537/569 (94.4%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 756 |
| headword on cited line | 562 |
| quotation on cited line, with differences | 123 |
| headword not found near cited line | 20 |
| not a citation of this play | 12 |
| quotation off by 1 | 7 |
| prose row break | 4 |
| quotation not found; headword not found near cited line | 4 |
| headword off by 1 | 3 |
| headword off by 3 | 1 |
| quotation elsewhere in scene | 1 |
| quotation off by 2 | 1 |
| quotation in another scene | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

| Scene | Cited lines | Offset | Citations |
|---|---|---|---|
| 2.2 | 32-36 | +1 | 3 |

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 5.114.4 | 114, 4 | Alchemy | not a citation of this play |  | your love taught it this a., to make of monsters cherubins, |  |
| 1.1.62 | Tim. I, 1, 62 | Apemantus | headword off by 3 | 1.1.59 |  | most rich in timons nod i saw them speak together |
| 2.2.117 | Tim. II, 2, 117 | Artificial | prose row break | 2.2.118 | his artificial stone, | a philosopher with two stones moe thans |
| 3.1.7 | Tim. III, 1, 7 | Bason | headword not found near cited line |  |  | honest flaminius you are very respectively |
| 1.2.36 | Shr. Ind. 2, 36. | Beck | not a citation of this play |  | ready at thy beck |  |
| 3.5.22 | Tim. III, 5, 22 | Behoove | headword not found near cited line |  |  | he did behave his anger ere twas spent |
| 1.1.25 | Tim. I, 1, 25 | Chase | headword not found near cited line |  |  | each bound it chafes what have you there |
| 2.2.225 | Tim. II, 2, 225 | Coldblooded | headword not found near cited line |  |  | their blood is caked tis cold it seldom flows |
| 4.3.160 | Tim. IV, 3, 160 | Currance | headword not found near cited line |  |  | smells from the general weal make curldpate ruffians bald |
| 2.2.37 | Tim. II, 2, 37 | Date-broke: | quotation off by 1 | 2.2.38 | date-broke bonds, | how goes the world that i am thus encountered |
| 2.153.6 | 153, 6 | Dateless | not a citation of this play |  | a dateless lively heat, still to endure, |  |
| 2.2.151 | Tim. II, 2, 151 | Dear-loved: | headword not found near cited line |  |  | and your great flow of debts my loved lord |
| 1.1.89 | Tim. I, 1, 89 | Decline | quotation off by 1 | 1.1.88 | not one accompanying his declineing foot, | tis common |
| 4.1.2 | 1, 2 | Defeat | headword not found near cited line |  |  | that girdlest in those wolves dive in the earth |
| 4.1.2 | 1, 2 | Defeat | headword not found near cited line |  |  | that girdlest in those wolves dive in the earth |
| 3.3.40 | III, 3, 40 | Defeat | quotation not found; headword not found near cited line |  | my stronger guilt defeats my strong intent, | now to guard sure their master |
| 3.1.49 | Tim. III, 1, 49 | Difference | headword not found near cited line |  |  | ist possible the world should so much differ |
| 3.0 | III Prol. 49 | Dive | not a citation of this play |  |  |  |
| 4.3.444 | Tim. IV, 3, 444 | Dung | headword not found near cited line |  |  | that feeds and breeds by a composture stolen |
| 1.1.209 | Tim. I, 1, 209 | Eater | headword not found near cited line |  |  | o they eat lords so they come by |
| 2.2.36 | Tim. II, 2, 36 | Encounter | quotation off by 1 | 2.2.37-38 | that I am thus encountered with clamorous demands of date-broke bonds, | ill wait upon you instantly come hither pray you |
| 4.3.12 | Tim IV, 3, 12 | Enlard | headword not found near cited line |  |  | it is the pasture lards the rothers sides |
| 3.1.7 | Tim. III, 1, 7 | Ewer | headword off by 1 | 3.1.6 |  | honest flaminius you are very respectively |
| 2.2.32 | Tim. II, 2, 32 | Expressly | headword off by 1 | 2.2.33 |  | your steward puts me off my lord |
| 3.1.154 | 1, 154 | Faithfulness | headword not found near cited line |  |  | (no such line) |
| 3.1.9 | Tim. III, 1, 9 | Fill | quotation off by 1 | 3.1.8 | fill me some wine, | and how does that honourable complete |
| 4.111.10 | 111, 10 | Infection | not a citation of this play |  | I will drink potions of eisel 'gainst my strong infection |  |
| 2.2.34 | Tim. II, 2, 34 | Keep | headword off by 1 | 2.2.35 |  | give me breath |
| 1.2.154 | Tim. I, 2, 154 | Lively | quotation not found; headword not found near cited line |  | lively lustre, | you have added worth unto t and lustre |
| 4.3.309 | Tim. IV, 3, 309 | Meddler | headword not found near cited line |  |  | an thou hadst hated medlars sooner |
| 4.3.504 | Tim. IV, 3, 504 | Mistake | headword not found near cited line |  |  | one honest manmistake me notbut one |
| 1.1.41 | Tim. I, 1, 41 | Mo | quotation not found; headword not found near cited line |  | look, moe, | look more |
| 2.1.7 | II, 1, 7 | Mo | quotation not found; headword not found near cited line |  | twenty moe, | if i would sell my horse and buy twenty more |
| 4.3.398 | IV, 3, 398 | Mo | quotation elsewhere in scene | 4.3.435-436 | he slays moe than you rob, | moe things like men eat timon and abhor them |
| 1.2.100 | Tim. I, 2, 100 | Needless | prose row break | 1.2.101 |  | neer have need of em they were the most |
| 5.92.12 | 92, 12 | Palm | not a citation of this play |  |  |  |
| 2.0 | II Prol. 35 | Pelf | not a citation of this play |  |  |  |
| 5.1.5 | Tim. V, 1, 5 | Phrynia | headword not found near cited line |  |  | certain alcibiades reports it phyrnia |
| 5.147.8 | 147, 8 | Physic | not a citation of this play |  |  |  |
| 3.5.78 | Tim. III, 5, 78 | Purchase | quotation off by 1 | 3.5.77 | though his right arm might purchase his own time, | and be in debt to none yet more to move you |
| 5.1.7 | Tim. V, 1, 7 | Quantity | prose row break | 5.1.8 |  | enriched poor straggling soldiers with great |
| 3.5.78 | Tim. III, 5, 78 | Right | quotation off by 1 | 3.5.77 | his right arm, | and be in debt to none yet more to move you |
| 1.1.22 | Tim. I, 1, 22 | Slip | quotation off by 2 | 1.1.20 | a thing sliped idly from me, | from whence tis nourished the fire i the flint |
| 4.3.134 | Tim. IV, 3, 134 | Sluttish | headword not found near cited line |  |  | and to make whores a bawd hold up you sluts |
| 5.2.223 | Tim. V, 2, 223 | Sour | quotation in another scene | 5.1.223 | lips, let sour words go by, | (no such line) |
| 2.2.169 | Tim. II, 2, 169 | Spin | headword not found near cited line |  |  | with drunken spilth of wine when every room |
| 4.90.3 | 90, 3 | Spite | not a citation of this play |  | join with the spite of fortune, |  |
| 4.90.3 | 90, 3 | Spite | not a citation of this play |  | when other petty griefs have done their spite |  |
| 1.1.74 | Tim. I, 1, 74 | Steepy | quotation off by 1 | 1.1.75-76 | bowing his head against the steepy mount to climb his happiness, | with one man beckoned from the rest below |
| 2.2.81 | Tim. II, 2, 81 | Superscription | prose row break | 2.2.82 |  | prithee apemantus read me the |
| 3.4.112 | Tim. III, 4, 112 | Ullorxa | headword not found near cited line |  |  | lucius lucullus and sempronius |
| 4.3.442 | Tim. IV, 3, 442 | Vaporous | headword not found near cited line |  |  | the seas a thief whose liquid surge resolves |
| 2.55.5 | 55, 5 | Wasteful | not a citation of this play |  | when wasteful war shall statues overturn, |  |
| 5.130.4 | 130, 4 | Wire | not a citation of this play |  |  |  |
