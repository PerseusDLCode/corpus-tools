# Schmidt smoke test: Macbeth

Sources: shakespeare.mac.globe.xml sha256 b1fe3bb74e3718c4; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of Macbeth in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1511/1559 (96.9%) pass.
- **With a quotation:** 934/952 (98.1%) have it on the cited line.
- **Headword only:** 577/607 (95.1%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 758 |
| headword on cited line | 598 |
| quotation on cited line, with differences | 155 |
| headword not found near cited line | 17 |
| not a citation of this play | 13 |
| headword off by 1 | 6 |
| quotation off by 1 | 5 |
| quotation not found; headword not found near cited line | 3 |
| quotation elsewhere in scene | 3 |
| headword off by 2 | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

None.

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 2.2.24 | Mcb. II, 2, 24 | Address | headword off by 1 | 2.2.25 |  | that they did wake each other i stood and heard them |
| 3.1.137 | Mcb. III, 1, 137 | Apart | headword off by 1 | 3.1.138 |  | than is his fathers must embrace the fate |
| 3.5.33 | Mcb. III, 5, 33 | Away | headword not found near cited line |  |  | is mortals chiefest enemy |
| 2.3.4 | Mcb. II, 3, 4 | Belzebub | headword not found near cited line |  |  | knock whos there i the name of beelzebub |
| 4.3.162 | Mcb. IV, 3, 162 | Betimes | headword not found near cited line |  |  | i know him now good god btimes remove |
| 3.1.133 | Mcb. III, 1, 133 | Botch | quotation off by 1 | 3.1.134 | to leave no rubs nor botches in the work, | that i require a clearness and with him |
| 3.1.89 | Mcb. III, 1, 89 | Bow | quotation off by 1 | 3.1.90 | whose heavy hand hath bowed you to the grave, | to pray for this good man and for his issue |
| 5.3.50 | Mcb. V, 3, 50 | Castalion-King-Urinal | headword not found near cited line |  |  | come sir dispatch if thou couldst doctor cast |
| 1.5.26 | Mcb. I, 5, 26 | Chástise | quotation off by 1 | 1.5.27-29 | that I may chástise with the valour of my tongue all that impedes thee from the golden round, | than wishest should be undone hie thee hither |
| 3.0 | III Prol. 17 | Coign | not a citation of this play |  |  |  |
| 4.128.4 | 128, 4 | Concord | not a citation of this play |  |  |  |
| 3.1.75 | Mcb. III, 1, 75 | Consider | headword off by 1 | 3.1.76 |  | it was so please your highness well then now |
| 5.3.55 | Mcb. V, 3, 55 | Cyme | headword not found near cited line |  |  | what rhubarb senna or what purgative drug |
| 4.64.1 | 64, 1 | Deface | not a citation of this play |  |  |  |
| 5.3.21 | Mcb. V, 3, 21 | Disease | headword not found near cited line |  |  | will cheer me ever or disseat me now |
| 5.154.12 | 154, 12 | Diseased | not a citation of this play |  |  |  |
| 4.1.39 | Mcb. IV, 1, 39 | Do | headword not found near cited line |  |  | o well done i commend your pains |
| 2.2.19 | Mcb. II, 2, 19 | Donalbain | headword off by 1 | 2.2.20 |  | hark |
| 2.6.158 | 6, 158 | Farmer | not a citation of this play |  |  |  |
| 3.1.24 | Mcb. III, 1, 24 | Fill | quotation off by 1 | 3.1.25 | fill up the time, | ist far you ride |
| 1.3.39 | Mcb. I, 3, 39 | Fores | headword not found near cited line |  |  | how far ist called to forres what are these |
| 2.2.62 | Mcb. II, 2, 62 | Incarnardine | headword not found near cited line |  |  | the multitudinous seas incarnadine |
| 2.2.89 | Shr. Ind. 2, 89. | Leet | not a citation of this play |  | you would present her at the leet |  |
| 5.1.71 | Shr. Ind. 1, 71. | Less | not a citation of this play |  | he is no less than what we say he is, |  |
| 2.3.56 | Mcb. II, 3, 56 | Limit | quotation off by 1 | 2.3.57 | 'tis my limited service, | this is the door ill make so bold to call |
| 2.153.6 | 153, 6 | Lively | not a citation of this play |  | a dateless lively heat, |  |
| 3.4.125 | Mcb. III, 4, 125 | Maggot-pie | headword not found near cited line |  |  | by magot pies and choughs and rooks brought forth |
| 1.7.21 | Mcb. I, 7, 21 | New | quotation not found; headword not found near cited line |  | a new born babe, | and pity like a naked newborn babe |
| 3.1.42 | Mcb. III, 1, 42 | Ourself | headword off by 1 | 3.1.43 |  | till seven at night to make society |
| 1.1.1 | Mcb. I, 1 | Paddock | quotation elsewhere in scene | 1.1.9 | Paddock calls, | when shall we three meet again |
| 1.1.1 | Mcb. I, 1 | Paddock | headword not found near cited line |  |  | when shall we three meet again |
| 2.4.115 | II, 4, 115 | Pronounce | quotation not found; headword not found near cited line |  | as 't please yourself pronounce their office, | (no such line) |
| 5.3.54 | Mcb. V, 3, 54 | Pull | headword not found near cited line |  |  | that should applaud again pullt off i say |
| 1.3.57 | Mcb. I, 3, 57 | Rap | quotation elsewhere in scene | 1.3.142 | how our partner's rap | that he seems rapt withal to me you speak not |
| 5.1.37 | V, 1, 37 | Riddle | headword not found near cited line |  |  | what comes from her to satisfy my remembrance |
| 5.1.37 | V, 1, 37 | Riddle | headword not found near cited line |  |  | what comes from her to satisfy my remembrance |
| 5.61.8 | 61, 8 | Scope | not a citation of this play |  | to find out shames and idle hours in me, the scope and tenour of thy jealousy, |  |
| 3.2.13 | Mcb. III, 2, 13 | Scorch | headword not found near cited line |  |  | we have scotched the snake not killed it |
| 4.2.146 | Shr. Ind. 2, 146 | Slip | not a citation of this play |  | let the world slip |  |
| 4.1.6 | 1, 6 | Slip | quotation not found; headword not found near cited line |  | let the world slide, | toad that under cold stone |
| 3.0 | III Prol. 2 | Snores | not a citation of this play |  |  |  |
| 4.2.57 | Shr. Ind. 2, 57. | Surprise | not a citation of this play |  | was beguiled and surprised, |  |
| 4.2.55 | Mcb. IV, 2, 55 | Swearer | quotation elsewhere in scene | 4.2.46-48 | what is a traitor? Why, one that swears and lies . . . Then the liars and swearers are fools, | why the honest men |
| 4.2.55 | Mcb. IV, 2, 55 | Swearer | headword off by 1 | 4.2.56 |  | why the honest men |
| 1.57.1 | 57, 1 | Tend | not a citation of this play |  | what should I do but tend upon the hours and times of your desire? |  |
| 1.5.36 | Mcb. I, 5, 36 | Tending: | headword off by 2 | 1.5.38 |  | one of my fellows had the speed of him |
| 1.5.36 | Mcb. I, 5, 36 | Tenedos | headword not found near cited line |  |  | one of my fellows had the speed of him |
| 5.1.66 | Mcb. V, 1, 66 | That | headword not found near cited line |  |  | yet i have known those which have walked in |
