# Schmidt smoke test: The Comedy of Errors

Sources: shakespeare.err.globe.xml sha256 374acede74deedb4; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of The Comedy of Errors in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1127/1175 (95.9%) pass.
- **With a quotation:** 684/697 (98.1%) have it on the cited line.
- **Headword only:** 443/478 (92.7%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 552 |
| headword on cited line | 467 |
| quotation on cited line, with differences | 108 |
| headword not found near cited line | 23 |
| not a citation of this play | 11 |
| quotation off by 1 | 6 |
| prose row break | 3 |
| headword off by 3 | 1 |
| quotation not found; headword not found near cited line | 1 |
| quotation elsewhere in scene | 1 |
| headword off by 1 | 1 |
| headword off by 2 | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

| Scene | Cited lines | Offset | Citations |
|---|---|---|---|
| 4.4 | 40-45 | +1 | 3 |

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 2.1.11 | Err. II, 1, 11 | Adoor; | headword not found near cited line |  |  | because their business still lies out o door |
| 3.2.66 | Err. III, 2, 66 | Aim | headword off by 3 | 3.2.63 |  | call thyself sister sweet for i am thee |
| 5.1.404 | V, 404 | Almanac | headword not found near cited line |  |  | and you the calendars of their nativity |
| 5.2.494 | V, 2, 494 | Amount | not a citation of this play |  | whereuntil it doth amount |  |
| 5.2.494 | V, 2, 494 | Amount | not a citation of this play |  |  |  |
| 4.3.14 | Err. IV, 3, 14 | Apparel | headword not found near cited line |  |  | newapparelled |
| 5.1.382 | V, 382 | Bail | quotation off by 1 | 5.1.381 | I sent you money to be your bail | by dromio but i think he brought it not |
| 4.3.23 | Err. IV, 3, 23 | Base | quotation not found; headword not found near cited line |  | base viol, | went like a bassviol in a case of leather the |
| 4.3.23 | Err. IV, 3, 23 | Base-viol | headword not found near cited line |  |  | went like a bassviol in a case of leather the |
| 4.4.45 | Err. IV, 4, 45 | Beware | quotation off by 1 | 4.4.46 | beware the rope's end, | your end or rather the prophecy like the |
| 2.2.138 | Err. II, 2, 138 | Brow | headword not found near cited line |  |  | and tear the stained skin off my harlotbrow |
| 4.1.81 | Err. IV, 1, 81 | By | headword not found near cited line |  |  | but sirrah you shall buy this sport as dear |
| 1.2.41 | I, 2, 41 | Calendar | headword not found near cited line |  |  | here comes the almanac of my true date |
| 3.2.140 | Err. III, 2, 140 | Carrack | headword not found near cited line |  |  | spain who sent whole armadoes of caracks to |
| 3.2.91 | Shr. Ind. 2, 91. | Cicely | not a citation of this play |  |  |  |
| 5.1.241 | Err. V, 241 | Deadman | headword not found near cited line |  |  | a livingdead man this pernicious slave |
| 2.2.148 | Err. II, 2, 148 | Distain | headword not found near cited line |  |  | i live unstained thou undishonored |
| 3.1.16 | III, 1, 16 | Down | quotation elsewhere in scene | 3.1.6-7 | here's a villain that would face me down he met me on the mart, | by the wrongs i suffer and the blows i bear |
| 2.2.192 | Err. II, 2, 192 | Elvish | headword not found near cited line |  |  | we talk with goblins owls and sprites |
| 3.2.137 | Err. III, 2, 137 | Embellish | prose row break | 3.2.138 | embellished with rubies, | oh sir upon her nose all oer |
| 3.2.137 | Err. III, 2, 137 | Ember-eves | headword not found near cited line |  |  | oh sir upon her nose all oer |
| 4.3.27 | Err. IV, 3, 27 | Exploit | prose row break | 4.3.28 |  | durance he that sets up his rest to do more |
| 4.3.25 | Err. IV, 3, 25 | Fob | headword not found near cited line |  |  | them a sob and rests them he sir that takes |
| 5.1.239 | Err. V, 239 | Fortune-teller | headword not found near cited line |  |  | a threadbare juggler and a forutneteller |
| 4.2.135 | Shr. Ind. 2, 135. | Frenzy | not a citation of this play |  |  |  |
| 2.2.143 | In II, 2, 143 | Grime | headword not found near cited line |  |  | my blood is mingled with the crime of lust |
| 2.0 | II Prol. 32 | House | not a citation of this play |  |  |  |
| 2.2.14 | Shr. Ind. 2, 14. | Idle | not a citation of this play |  | heaven cease this idle humour in your honour, |  |
| 2.2.14 | Shr. Ind. 2, 14. | Idle | not a citation of this play |  | very idle words, |  |
| 4.4.31 | Err. IV, 4, 31 | Instant | quotation off by 1 | 4.4.32 | to this instant | it by my long ears i have served him from the |
| 2.2.28 | Err. II, 2, 28 | Jet | headword not found near cited line |  |  | your sauciness will jest upon my love |
| 4.4.40 | Err. IV, 4, 40 | Lame | headword off by 1 | 4.4.41 |  | beggar wont her brat and i think when he |
| 5.1.72 | Err. V, 72 | Lightness | headword not found near cited line |  |  | and thereof comes it that his head is light |
| 5.1.135 | Shr. Ind. 1, 135. | Peasant | not a citation of this play |  |  |  |
| 5.245.95 | V, 245 | Possess | not a citation of this play |  |  |  |
| 1.1.116 | Err. I, 1, 116 | Reave | headword not found near cited line |  |  | and would have reft the fishers of their prey |
| 4.4.43 | Err. IV, 4, 43 | Respect | quotation off by 1 | 4.4.44-45 | respice finem, respect your end, | come go along my wife is coming yonder |
| 1.2.59 | Shr. Ind. 2, 59. | Roam | not a citation of this play |  |  |  |
| 1.2.25 | Shr. Ind. 2, 25. | Score | not a citation of this play |  | score me up for the lyingest knave in Christendom, |  |
| 4.4.24 | Err. IV, 4, 24 | Senseless | quotation off by 1 | 4.4.25 | senseless villain, | his hands |
| 4.4.27 | Err. IV, 4, 27 | Sensible | quotation off by 1 | 4.4.28-29 | thou art sensible in nothing but blows, | might not feel your blows |
| 4.3.61 | Err. IV, 3, 61 | Spoon-meat | prose row break | 4.3.62 |  | master if you do expect |
| 2.2.99 | Err. II, 2, 99 | Tire | headword not found near cited line |  |  | spends in trimming the other that at dinner |
| 2.2.148 | Err. II, 2, 148 | Undishonoured | headword not found near cited line |  |  | i live unstained thou undishonored |
| 1.1.3 | 1, 3 | Unwilling | headword not found near cited line |  |  | merchant of syracuse plead no more |
| 1.1.3 | 1, 3 | Unwilling | headword not found near cited line |  |  | merchant of syracuse plead no more |
| 4.1.9 | 1, 9 | Upon | headword not found near cited line |  |  | and in the instant that i met with you |
| 4.1.60 | Err. IV, 1, 60 | Whe'r | headword off by 2 | 4.1.58 |  | good sir say whether youll answer me or no |
