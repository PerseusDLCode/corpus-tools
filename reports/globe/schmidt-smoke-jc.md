# Schmidt smoke test: Julius Cæsar

Sources: shakespeare.jc.globe.xml sha256 bee4bef0bc3d7163; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of Julius Cæsar in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1129/1184 (95.4%) pass.
- **With a quotation:** 637/648 (98.3%) have it on the cited line.
- **Headword only:** 492/536 (91.8%) have it on the cited line.

| Verdict | Citations |
|---|---|
| headword on cited line | 517 |
| quotation on cited line | 491 |
| quotation on cited line, with differences | 121 |
| headword not found near cited line | 24 |
| not a citation of this play | 21 |
| headword off by 1 | 5 |
| quotation off by 1 | 2 |
| quotation not found; headword not found near cited line | 2 |
| headword off by 3 | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

None.

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 1.2.112 | Caes. I, 2, 112 | Aeneas | headword not found near cited line |  |  | i as neas our great ancestor |
| 4.3.28 | Caes. IV, 3, 28 | Bait | headword not found near cited line |  |  | than such a roman brutus bay not me |
| 5.1.71 | Caes. V, 1, 71 | Birth-day | headword off by 1 | 5.1.72 |  | messala |
| 2.2.30 | Caes. II, 2, 30 | Blaze | headword off by 1 | 2.2.31 |  | when beggars die there are no comets seen |
| 2.120.3 | 120, 3 | Bow | not a citation of this play |  | needs must I under my transgression bow |  |
| 3.2.110 | Caes. III, 2, 110 | Brutish | quotation off by 1 | 3.2.109 | O judgment, thou art fled to brutish beasts, | and men have lost their reason bear with me |
| 1.2.1 | Caes. I, 2, 1 | Calphurnia | headword not found near cited line |  |  | calpurnia peace ho csar speaks calpurnia |
| 2.4.35 | Caes. II, 4, 35 | Crowd | quotation off by 1 | 2.4.34-36 | the throng will crowd a feeble man almost to death, | of senators of prtors common suitors |
| 1.2.305 | Caes. I, 2, 305 | Disgest | headword not found near cited line |  |  | which gives men stomach to digest his words |
| 1.2.138 | Caes. I, 2, 138 | Dishonourable | headword not found near cited line |  |  | to find ourselves dishonorable graves |
| 5.1.76 | Caes. V, 1, 76 | Epicurus | headword off by 1 | 5.1.77 |  | upon one battle all our liberties |
| 2.97.4 | 97, 4 | Everywhere | not a citation of this play |  |  |  |
| 2.100.12 | 100, 12 | Everywhere | not a citation of this play |  |  |  |
| 2.102.4 | 102, 4 | Everywhere | not a citation of this play |  |  |  |
| 1.3.129 | Caes. I, 3, 129 | Favoured | headword not found near cited line |  |  | in favors like the work we have in hand |
| 1.2.83 | Shr. Ind. 2, 83. | Fay | not a citation of this play |  | by my fay |  |
| 4.3.89 | IV, 3, 89 | Friendly | headword off by 1 | 4.3.90 |  | you love me not i do not like your faults |
| 5.3.29 | Caes. V, 3, 29 | Gad | headword not found near cited line |  |  | with horsemen that make to him on the spur |
| 1.3.21 | Caes. I, 3, 21 | Glaze | headword not found near cited line |  |  | who glared upon me and went surly by |
| 2.2.67 | Caes. II, 2, 67 | Grey-beard | headword not found near cited line |  |  | to be afraid to tell graybeards the truth |
| 1.3.124 | Caes. I, 3, 124 | Honourable-dangerous | headword not found near cited line |  |  | of honorabledangerous consequence |
| 5.5.79 | Caes. V, 5, 79 | Honourably | quotation not found; headword not found near cited line |  | ordered honourably | most like a soldier ordered honorably |
| 5.128.5 | 128, 5 | Leap | not a citation of this play |  |  |  |
| 2.1.17 | Shr. Ind. 1, 17. | Merriman | not a citation of this play |  |  |  |
| 2.2.4 | 2, 4 | Merriment | headword not found near cited line |  |  | my lord |
| 2.2.4 | 2, 4 | Merriment | headword not found near cited line |  |  | my lord |
| 5.3.101 | V, 3, 101 | Mo | quotation not found; headword not found near cited line |  | mo tears, | should breed thy fellow friends i owe more tears |
| 4.55.2 | 55, 2 | Outlive | not a citation of this play |  |  |  |
| 4.101.11 | 101, 11 | Outlive | not a citation of this play |  |  |  |
| 4.1.95 | Shr. Ind. 1, 95. | Overeye | not a citation of this play |  | overeyeing of his odd behaviour, |  |
| 5.1.80 | Caes. V, 1, 80 | Perch | headword off by 1 | 5.1.81 |  | coming from sardis on our former ensign |
| 2.147.5 | 147, 5 | Physician | not a citation of this play |  |  |  |
| 1.3.143 | Caes. I, 3, 143 | Praetor | headword not found near cited line |  |  | and look you lay it in the prtors chair |
| 2.4.35 | II, 4, 35 | Praetor | headword not found near cited line |  |  | of senators of prtors common suitors |
| 5.3.74 | Caes. V, 3, 74 | Ram | headword not found near cited line |  |  | the noble brutus thrusting this report |
| 3.0 | III Prol. 1 | Rout | not a citation of this play |  |  |  |
| 1.4.10 | 4, 10 | Self | not a citation of this play |  | thou of thyself thy sweet self dost deceive, |  |
| 1.126.4 | 126, 4 | Self | not a citation of this play |  | as thy sweet self growest, |  |
| 1.151.4 | 151, 4 | Self | not a citation of this play |  |  |  |
| 3.0 | III Prol. 51 | Shriek | not a citation of this play |  |  |  |
| 5.1.87 | Caes. V, 1, 87 | Sick-fallen | headword not found near cited line |  |  | as we were sickly prey their shadows seem |
| 5.126.2 | 126, 2 | Sickle | not a citation of this play |  |  |  |
| 4.2.24 | Caes. IV, 2, 24 | Sink | headword off by 3 | 4.2.27 |  | make gallant show and promise of their mettle |
| 1.57.7 | 57, 7 | Sour | not a citation of this play |  | nor think the bitterness of absence sour |  |
| 1.94.13 | 94, 13 | Sour | not a citation of this play |  | sweetest things turn sourest by their deeds, |  |
| 4.3.115 | Caes. IV, 3, 115 | Temper | headword not found near cited line |  |  | when grief and blood illtempered vexeth him |
| 5.3.21 | Caes. V, 3, 21 | Thick-sighted | headword not found near cited line |  |  | my sight was ever thick regard titinius |
| 1.1.44 | Caes. I, 1, 44 | Top | headword not found near cited line |  |  | to towers and windows yea to chimneytops |
| 4.0 | IV Prol. 7 | Train | not a citation of this play |  |  |  |
| 1.2.288 | I, 2, 288 | Trophy | headword not found near cited line |  |  | could tell you more news too marullus and |
| 4.0 | IV Prol. 45 | Unborn | not a citation of this play |  |  |  |
| 5.1.58 | Caes. V, 1, 58 | Upon | headword not found near cited line |  |  | i was not born to die on brutus sword |
| 2.2.80 | II, 2, 80 | Warn | headword not found near cited line |  |  | and these does she apply for warnings and portents |
| 1.1.66 | Caes. I, 1, 66 | Whe'r | headword not found near cited line |  |  | see whether their basest metal be not moved |
| 5.3.97 | V, 3, 97 | Whe'r | headword not found near cited line |  |  | look whether he have not crowned dead cassius |
