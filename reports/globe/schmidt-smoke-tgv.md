# Schmidt smoke test: Two Gentlemen of Verona

Sources: shakespeare.tgv.globe.xml sha256 feac8f0bb57f2742; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of Two Gentlemen of Verona in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1279/1316 (97.2%) pass.
- **With a quotation:** 800/809 (98.9%) have it on the cited line.
- **Headword only:** 479/507 (94.5%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 659 |
| headword on cited line | 507 |
| quotation on cited line, with differences | 113 |
| headword not found near cited line | 18 |
| not a citation of this play | 8 |
| quotation off by 1 | 4 |
| quotation not found; headword not found near cited line | 2 |
| headword off by 1 | 2 |
| quotation elsewhere in scene | 2 |
| prose row break | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

| Scene | Cited lines | Offset | Citations |
|---|---|---|---|
| 4.4 | 133-134 | +1 | 3 |

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 2.1.23 | Gent. II, 1, 23 | A B C | headword not found near cited line |  |  | schoolboy that had lost his a b c to weep like a |
| 2.0 | II Prol. 4 | Awful | not a citation of this play |  |  |  |
| 4.4.159 | Gentl. IV, 4, 159 | Cheek-roses | headword not found near cited line |  |  | the air hath starved the roses in her cheeks |
| 5.4.103 | Gentl. V, 4, 103 | Cleave | headword not found near cited line |  |  | how oft hast thou with perjury cleft the root |
| 5.4.103 | Gentl. V, 4, 103 | Cleave | headword not found near cited line |  |  | how oft hast thou with perjury cleft the root |
| 2.1.115 | Gentl. II, 1, 115 | Clerkly | quotation off by 1 | 2.1.114 | 'tis very clerkly done, | now trust me madam it came hardly off |
| 1.2.279 | I, 2, 279 | Dazzle | headword not found near cited line |  |  | (no such line) |
| 2.7.9 | Gentl. II, 7, 9 | Devote | quotation not found; headword not found near cited line |  | a true devoteed pilgrim, | a truedevoted pilgrim is not weary |
| 2.1.118 | Gentl. II, 1, 118 | Doubtfully | quotation off by 1 | 2.1.117 | I writ at random, very doubtfully | perchance you think too much of so much pains |
| 3.0 | III Prol. 50 | Down | not a citation of this play |  |  |  |
| 2.1.102 | Gent. II, 1, 102 | Good-morrow | headword off by 1 | 2.1.103 |  | madam and mistress a thousand |
| 1.53.14 | I, 53 | Grievously | not a citation of this play |  |  |  |
| 5.60.11 | V, 60 | Haply | not a citation of this play |  |  |  |
| 5.1.136 | Shr. Ind. 1, 136. | Haply | not a citation of this play |  |  |  |
| 5.2.171 | V, 2, 171 | Haply | headword not found near cited line |  |  | (no such line) |
| 3.1.36 | Gent. III, 1, 36 | Keep | quotation elsewhere in scene | 3.1.111 | keys kept safe, | the key whereof myself have ever kept |
| 3.1.184 | III, 1, 184 | Keep | quotation elsewhere in scene | 3.1.358 | that I'll keep shut, | fostered illumined cherished kept alive |
| 4.2.58 | Shr. Ind. 2, 58. | Lively | not a citation of this play |  | as lively painted as the deed was done, |  |
| 3.1.254 | Gent. III, 1, 254 | Love-affairs: | headword not found near cited line |  |  | of all that may concern thy loveafairs |
| 2.4.196 | Gent. II, 4, 196 | Mien | headword not found near cited line |  |  | is it mine or valentines praise |
| 4.4.134 | Gent. IV, 4, 134 | New | quotation off by 1 | 4.4.135 | full of new found oaths, | i know they are stuffed with protestations |
| 4.4.134 | Gent. IV, 4, 134 | New-found: | headword off by 1 | 4.4.135 |  | i know they are stuffed with protestations |
| 1.2.50 | Gent. I, 2, 50 | O'erlook | headword not found near cited line |  |  | and yet i would i had overlooked the letter |
| 4.2.133 | Gent. IV, 2, 133 | Over | quotation not found; headword not found near cited line |  | o'er night, | and so good rest as wretches have overnight |
| 4.4.133 | IV, 4, 133 | Protestation | quotation off by 1 | 4.4.134 | stuffed with protestations, | i will not look upon your masters lines |
| 4.2.18 | Gent. IV, 2, 18 | Quote | headword not found near cited line |  |  | how now sir proteus are you crept before us |
| 4.0 | IV Prol. 27 | Record | not a citation of this play |  |  |  |
| 2.1.22 | Gent. II, 1, 22 | Schoolboy | prose row break | 2.1.23 |  | one that had the pestilence to sigh like a |
| 3.1.56 | Gent. III, 1, 56 | Significant | headword not found near cited line |  |  | the tenor of them doth but signify |
| 1.1.4 | 1, 4 | Throughly | headword not found near cited line |  |  | to the sweet glances of thy honored love |
| 1.1.4 | 1, 4 | Throughly | headword not found near cited line |  |  | to the sweet glances of thy honored love |
| 2.4.113 | Gent. II, 4, 113 | Upon | headword not found near cited line |  |  | servant you are welcome to a worthless mistress |
| 4.3.21 | Gent. IV, 3, 21 | Vow | headword not found near cited line |  |  | upon whose grave thou vowdst pure chastity |
| 2.1.54 | Gent. II, 1, 54 | Well-favoured | headword not found near cited line |  |  | not so fair boy as wellfavored |
| 3.2.6 | Gent. III, 2, 6 | Zeal | headword not found near cited line |  |  | this weak impress of love is as a figure |
| 3.2.6 | Gent. III, 2, 6 | Zeal | headword not found near cited line |  |  | this weak impress of love is as a figure |
| 3.4.150 | III, 4, 150 | Zeal | not a citation of this play |  |  |  |
