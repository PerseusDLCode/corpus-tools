# Schmidt smoke test: King Henry VIII.

Sources: shakespeare.h8.globe.xml sha256 32e15e6c29693bd0; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of King Henry VIII. in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1620/1656 (97.8%) pass.
- **With a quotation:** 947/958 (98.9%) have it on the cited line.
- **Headword only:** 673/698 (96.4%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 756 |
| headword on cited line | 696 |
| quotation on cited line, with differences | 168 |
| headword not found near cited line | 20 |
| not a citation of this play | 7 |
| quotation not found; headword not found near cited line | 4 |
| headword off by 1 | 2 |
| quotation elsewhere in scene | 2 |
| quotation off by 1 | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

None.

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 5.1.120 | V, 1, 120 | Accuser | headword off by 1 | 5.1.121 |  | i should have taen some pains to bring together |
| 3.0 | III Prol. 24 | Choice-drawn | not a citation of this play |  |  |  |
| 4.4.43 | 4, 43 | Dowdy | not a citation of this play |  |  |  |
| 1.4.4 | H8 I, 4 | Easy | quotation elsewhere in scene | 1.4.17 | they should find easy penance, | in all this noble bevy has brought with her |
| 2.2.39 | H8 II, 2, 39 | Everywhere | headword not found near cited line |  |  | these news are every where every tongue speaks em |
| 1.3.57 | H8 I, 3, 57 | Everywhere | headword not found near cited line |  |  | his dews fall every where no doubt hes noble |
| 1.4.6 | H8 I, 4, 6 | Firstling | quotation not found; headword not found near cited line |  | our play leaps o'er the vaunt and firstlings of those broils, beginning in the middle, | as first good company good wine good welcome |
| 3.2.423 | H8 III, 2, 423 | Forego | headword not found near cited line |  |  | must i then leave you must i needs forgo |
| 2.2.112 | H8 II, 2, 112 | Freely | headword off by 1 | 2.2.113 |  | a woman of less place might ask by law |
| 1.3.66 | H8 I, 3, 66 | Guilford | headword not found near cited line |  |  | for i was spoke to with sir henry guildford |
| 1.4.9 | I, 4, 9 | Guilford | headword not found near cited line |  |  | clapped wings to me you are young sir harry guildford |
| 2.2.1 | 2, 1 | Have-at-him | quotation elsewhere in scene | 2.2.11 | Have | my lord the horses your lordship |
| 2.2.1 | 2, 1 | Have-at-him | headword not found near cited line |  |  | my lord the horses your lordship |
| 2.2.1 | 2, 1 | Have-at-him | headword not found near cited line |  |  | my lord the horses your lordship |
| 1.2.147 | H8 I, 2, 147 | Henton | headword not found near cited line |  |  | by a vain prophecy of nicholas hopkins |
| 3.2.143 | Shr. Ind. 2, 143. | Household | quotation not found; headword not found near cited line |  | it is more pleasing stuff. What, household stuff? | to have you therein my companion sir |
| 2.280.143 | II, 280 | Household | not a citation of this play |  | and bring you from a wild Kate to a Kate conformable as other household Kates, |  |
| 1.68.10 | 68, 10 | Itself | not a citation of this play |  | without all ornament, itself and true, |  |
| 1.94.10 | 94, 10 | Itself | not a citation of this play |  | though to itself it only live and die, |  |
| 5.2.18 | H8 V, 2, 18 | Lacquey | headword not found near cited line |  |  | mong boys grooms and lackeys but their pleasures |
| 5.1.124 | H8 V, 1, 124 | Over | quotation not found; headword not found near cited line |  | to triumph over: | if they shall fail i with mine enemies |
| 3.2.250 | H8 III, 2, 250 | Patent | headword not found near cited line |  |  | tied it by letterspatents now wholl take it |
| 2.150.1 | 150, 1 | Powerful | not a citation of this play |  | this powerful might, |  |
| 5.3.153 | H8 V, 3, 153 | Respect | quotation off by 1 | 5.3.154 | well, well, my lords, respect him, | im sure in me |
| 3.2.357 | H8 III, 2, 357 | Ripen | headword not found near cited line |  |  | his greatness is aripening nips his root |
| 5.4.55 | H8 V, 4, 55 | Strond | headword not found near cited line |  |  | succour which were the hope o the strand |
| 3.1.2 | 1, 2 | Suspiration | headword not found near cited line |  |  | sing and disperse em if thou canst leave working song |
| 3.1.2 | 1, 2 | Suspiration | headword not found near cited line |  |  | sing and disperse em if thou canst leave working song |
| 5.4.80 | H8 V, 4, 80 | Tear | headword not found near cited line |  |  | not being torn apieces we have done |
| 3.0 | III Prol. 52 | Travail | not a citation of this play |  |  |  |
| 3.1.14 | III, 1, 14 | Travail | quotation not found; headword not found near cited line |  | make swift the pangs of my queen's travails, | fall asleep or hearing die |
| 5.3.151 | H8 V, 3, 151 | Trial-fire | headword not found near cited line |  |  | if there be faith in men meant for his trial |
| 4.1.80 | H8 IV, 1, 80 | Weave | headword not found near cited line |  |  | could say this is my wife there all were woven |
| 2.2.2 | H8 II, 2, 2 | Well-chosen | headword not found near cited line |  |  | sent for with all the care i had i saw well |
| 1.1.167 | H8 I, 1, 167 | Wince | headword not found near cited line |  |  | did break i the rinsing faith and so it did |
| 1.1.167 | H8 I, 1, 167 | Wrench | headword not found near cited line |  |  | did break i the rinsing faith and so it did |
