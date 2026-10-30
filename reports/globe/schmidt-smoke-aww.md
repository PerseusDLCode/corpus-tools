# Schmidt smoke test: All's Well That Ends Well

Sources: shakespeare.aww.globe.xml sha256 6c8a1f5a9ab6ba1e; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of All's Well That Ends Well in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1673/1734 (96.5%) pass.
- **With a quotation:** 1106/1120 (98.8%) have it on the cited line.
- **Headword only:** 567/614 (92.3%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 893 |
| headword on cited line | 588 |
| quotation on cited line, with differences | 192 |
| headword not found near cited line | 24 |
| prose row break | 16 |
| not a citation of this play | 10 |
| quotation not found; headword not found near cited line | 4 |
| quotation off by 1 | 2 |
| quotation elsewhere in scene | 1 |
| headword off by 1 | 1 |
| headword off by 2 | 1 |
| quotation in another scene | 1 |
| quotation off by 2 | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

None.

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 2.3.216 | II, 3, 216 | Bravely | quotation elsewhere in scene | 2.3.316 | away, and leave her bravely | too great a burthen i have now found thee |
| 2.2.66 | II, 2, 66 | Brief | headword not found near cited line |  |  | an end sir to your business give helen this |
| 4.7.57 | All's IV, 7, 57 | Broad | not a citation of this play |  |  |  |
| 4.1.102 | Shr. Ind. 1, 102. | Buttery | quotation not found; headword not found near cited line |  | take them to the buttery and give them friendly welcome, | a will betray us all unto ourselves |
| 4.3.280 | All's IV, 3, 280 | Cloister | prose row break | 4.3.281 |  | he will steal sir an egg out of a |
| 4.3.139 | IV, 3, 139 | Constraint | prose row break | 4.3.140 |  | i will confess what i know without |
| 2.5.96 | All's II, 5, 96 | Coragio | headword off by 1 | 2.5.97 |  | whilst i can shake my sword or hear the drum |
| 4.1.2 | All's IV, 1, 2 | Corner | headword not found near cited line |  |  | this hedgecorner when you sally upon him |
| 3.5.73 | All's III, 5, 73 | Corrupt | headword off by 2 | 3.5.75 |  | in the unlawful purpose he does indeed |
| 3.2.21 | III, 2, 21 | Daughter-in-law | prose row break | 3.2.22 |  | i have sent you a |
| 4.5.4 | IV, 5, 4 | Daughter-in-law | prose row break | 4.5.5 |  | youth of a nation in his colour your |
| 4.5.110 | All's IV, 5, 110 | Delicate | prose row break | 4.5.111 | delicate fine hats, | faith theres a dozen of em with |
| 4.1.57 | Shr. Ind. 1, 57. | Diaper | quotation not found; headword not found near cited line |  | another bear the ewer, the third a diaper | or to drown my clothes and say i was |
| 1.1.176 | All's I, 1, 176 | Dryly | quotation off by 1 | 1.1.174-175 | like one of our French withered pears, it looks ill, it eats dryly | drily marry tis a withered pear it was formerly |
| 3.6.29 | All's III, 6, 29 | Examination | prose row break | 3.6.30 |  | tents be but your lordship present at his |
| 4.1.2 | 1, 2 | Fate | headword not found near cited line |  |  | this hedgecorner when you sally upon him |
| 4.1.2 | 1, 2 | Fate | headword not found near cited line |  |  | this hedgecorner when you sally upon him |
| 3.63.3 | 63, 3 | Fill | not a citation of this play |  |  |  |
| 2.3.1 | 3, 1 | German | headword not found near cited line |  |  | they say miracles are past and we have |
| 4.5.73 | IV, 5, 73 | German | headword not found near cited line |  |  | was about to tell you since i heard of the good |
| 5.3.258 | All's V, 3, 258 | Go-between | headword not found near cited line |  |  | yes so please your majesty i did go |
| 1.2.48 | All's I, 2, 48 | Goer backward | headword not found near cited line |  |  | but goers backward his good remembrance sir |
| 1.3.56 | All's I, 3, 56 | Howsome'er | prose row break | 1.3.57-58 | howsome'er their hearts are severed in religion, their heads are both one, | charbon the puritan and old poysam the papist |
| 5.2.55 | Alls V, 2, 55 | Inquire | prose row break | 5.2.56 |  | coming i know by his trumpets sirrah |
| 5.3.216 | Alls V, 3, 216 | Insuit | headword not found near cited line |  |  | her infinite cunning with her modern grace |
| 5.3.330 | Alls V, 3, 330 | Keep | quotation not found; headword not found near cited line |  | keptest: | thou keptst a wife herself thyself a maid |
| 1.1.187 | 1, 187 | Keep | headword not found near cited line |  |  | his faith his sweet disaster with a world |
| 4.3.323 | All's IV, 3, 323 | Lacquey | headword not found near cited line |  |  | is in a retreat he outruns any lackey marry in |
| 1.3.177 | All's I, 3, 177 | Loveliness | headword not found near cited line |  |  | the mystery of your loneliness and find |
| 3.5.24 | All's III, 5, 24 | Maidenhood | headword not found near cited line |  |  | terrible shows in the wreck of maiden hood cannot |
| 2.3.214 | All's II, 3, 214 | Manifoldly | prose row break | 2.3.215 |  | scarfs and the bannerets about thee did |
| 2.2.25 | All's II, 2, 25 | May-day | prose row break | 2.2.26 |  | pancake for shrove tuesday a morris for |
| 2.0 | II Prol. 8 | Mite | not a citation of this play |  |  |  |
| 5.2.1 | All's V, 2, 1 | Mr. | headword not found near cited line |  |  | good monsieur lavache give my lord |
| 1.4.732 | 4, 732 | Naturally | not a citation of this play |  |  |  |
| 2.0 | II Prol. 36 | Ne | not a citation of this play |  |  |  |
| 4.3.281 | All's IV, 3, 281 | Nessus | prose row break | 4.3.282 |  | cloister for rapes and ravishments he parallels |
| 4.3.279 | All's IV, 3, 279 | On | quotation in another scene | 5.3.279 | goes off and on at pleasure, | his honesty |
| 3.4.24 | All's III, 4, 24 | Overtake | headword not found near cited line |  |  | she might have been oertaen and yet she writes |
| 2.1.100 | All's II, 1, 100 | Pandarus | headword not found near cited line |  |  | his majesty seldom fears i am cressids uncle |
| 1.1.219 | All's I, 1, 219 | Perfect | quotation off by 2 | 1.1.221-222 | I will return perfect courtier, | and i like the wear well |
| 2.1.95 | All's II, 1, 95 | Prologue-like | headword not found near cited line |  |  | thus he his special nothing ever prologues |
| 1.3.157 | All's I, 3, 157 | Rainbow | headword not found near cited line |  |  | that this distempered messenger of wet |
| 2.113.13 | 113, 13 | Replete | not a citation of this play |  | incapable of more, replete with you, |  |
| 1.2.114 | I, 2, 114 | Retrograde | headword not found near cited line |  |  | (no such line) |
| 2.3.200 | II, 3, 200 | Rousillon | prose row break | 2.3.201 |  | are you companion to the count |
| 4.80.7 | 80, 7 | Saucy | not a citation of this play |  |  |  |
| 4.128.13 | 128, 13 | Saucy | not a citation of this play |  |  |  |
| 2.1.147 | All's II, 1, 147 | Shift | headword not found near cited line |  |  | where hope is coldest and despair most fits |
| 3.5.91 | All's III, 5, 91 | Shrewdly | quotation off by 1 | 3.5.92 | he is shrewdly vexed at something, | lose our drum well |
| 1.3.157 | All's I, 3, 157 | Stream | headword not found near cited line |  |  | that this distempered messenger of wet |
| 3.5.23 | All's III, 5, 23 | Terrible | prose row break | 3.5.24 |  | them and the misery is example that so |
| 3.2.8 | All's III, 2, 8 | Toothpick | headword not found near cited line |  |  | sing pick his teeth and sing i know a man |
| 4.5.66 | All's IV, 5, 66 | Unhappiness | headword not found near cited line |  |  | a shrewd knave and an unhappy |
| 2.0 | II Prol. 31 | Unquiet | not a citation of this play |  |  |  |
| 5.72.10 | 72, 10 | Untrue | not a citation of this play |  | that you for love speak well of me untrue |  |
| 4.3.187 | All's IV, 3, 187 | Vaumond | prose row break | 4.3.188 |  | fifty each mine own company chitopher |
| 4.3.187 | All's IV, 3, 187 | Vaunt | quotation not found; headword not found near cited line |  | our play leaps o'er the vaunt and firstlings of those broils, | fifty each mine own company chitopher |
| 2.1.22 | All's II, 1, 22 | Warn | headword not found near cited line |  |  | before you serve our hearts receive your warnings |
| 1.3.40 | All's I, 3, 40 | Wickedness | prose row break | 1.3.41 |  | thy marriage sooner than thy |
| 4.1.60 | IV, 1, 60 | Window | prose row break | 4.1.61 | (window of lattice). | though i swore i leaped from the |
