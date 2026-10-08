# Schmidt smoke test: Antony and Cleopatra

Sources: shakespeare.ant.globe.xml sha256 32b4768b70742369; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of Antony and Cleopatra in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1913/2037 (93.9%) pass.
- **With a quotation:** 1111/1148 (96.8%) have it on the cited line.
- **Headword only:** 802/889 (90.2%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 843 |
| headword on cited line | 828 |
| quotation on cited line, with differences | 242 |
| headword not found near cited line | 51 |
| not a citation of this play | 38 |
| headword off by 1 | 13 |
| prose row break | 10 |
| quotation elsewhere in scene | 5 |
| quotation off by 1 | 3 |
| quotation not found; headword not found near cited line | 3 |
| quotation in another scene | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

None.

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 1.4 | Ant. I, 4, 9 | Abstract | not a citation of this play |  | a man who is the abstract of all faults, |  |
| 3.6.94 | Ant. III, 6, 94 | Adulterous | headword off by 1 | 3.6.93 |  | in his abominations turns you off |
| 4.14.53 | Ant. IV, 14, 53 | Aeneas | headword not found near cited line |  |  | dido and her neas shall want troops |
| 2.6.16 | Ant. II, 6, 16 | All-honoured | headword not found near cited line |  |  | made the allhonored honest roman brutus |
| 1.2.154 | Ant. I, 2, 154 | Almanac | prose row break | 1.2.155 |  | they are greater storms and tempests than |
| 3.6.74 | Ant. III, 6, 74 | Amintas | headword not found near cited line |  |  | of comagene polemon and amyntas |
| 2.6.68 | Ant. II, 6, 68 | Apollodorus | headword off by 1 | 2.6.69 |  | then so much have i heard |
| 4.25.8 | 25, 8 | At | not a citation of this play |  | at a frown they in their glory die, |  |
| 4.127.10 | 127, 10 | At | not a citation of this play |  | they morners seem at such as . . ., |  |
| 3.22.12 | 22, 12 | Basan: | not a citation of this play |  |  |  |
| 1.3.84 | Ant. I, 3, 84 | Behoove | headword not found near cited line |  |  | how this herculean roman does become |
| 1.58.11 | 58, 11 | Belong | not a citation of this play |  | to you it doth belong yourself to pardon, |  |
| 3.3.35 | Ant. III, 3, 35 | Brown | prose row break | 3.3.36 | (browner). | her hair what color |
| 3.7.74 | Ant. III, 7, 74 | Caelius | headword not found near cited line |  |  | publicola and clius are for sea |
| 3.6.6 | Ant. III, 6, 6 | Caesarion | headword not found near cited line |  |  | csarion whom they call my fathers son |
| 3.13.162 | III, 13, 162 | Caesarion | headword not found near cited line |  |  | dissolve my life the next csarion smite |
| 4.70.7 | 70, 7 | Canker | not a citation of this play |  | canker vice the sweetest buds doth love, |  |
| 4.95.2 | 95, 2 | Canker | not a citation of this play |  | like a canker in the fragrant rose, |  |
| 4.99.12 | 99, 12 | Canker | not a citation of this play |  | a vengeful canker eat him up to death, |  |
| 3.0 | III Prol. 16 | Careful | not a citation of this play |  |  |  |
| 3.1.81 | III, 1, 81 | Careful | headword not found near cited line |  |  | (no such line) |
| 3.7.24 | III, 7, 24 | Celerity | prose row break | 3.7.25-26 | celerity is never more admired than by the negligent, | and take in toryne you have heard ont sweet |
| 3.7.74 | Ant. III, 7, 74 | Celius | headword not found near cited line |  |  | publicola and clius are for sea |
| 5.2.120 | Ant. V, 2, 120 | Chance | prose row break | 5.2.117-119 | what injuries you did us, we shall remember as things but done by chance | sole sir o the world |
| 5.2.120 | Ant. V, 2, 120 | Chance | quotation elsewhere in scene | 5.2.173-174 | I shall show the cinders of my spirits through the ashes of my c., | sole sir o the world |
| 4.12.46 | Ant. IV, 12, 46 | Club | prose row break | 4.12.45 |  | subdue my worthiest self the witch shall die |
| 3.73.3 | 73, 3 | Cold | not a citation of this play |  | shake against the cold |  |
| 1.5.74 | Ant. I, 5, 74 | Coldblooded | headword not found near cited line |  |  | when i was green in judgment cold in blood |
| 2.6.58 | Ant. II, 6, 58 | Composition | headword off by 1 | 2.6.59 |  | i hope so lepidus thus we are agreed |
| 4.0 | IV Prol. 30 | Contend | not a citation of this play |  |  |  |
| 2.0 | II Prol. 9 | Conversation | not a citation of this play |  |  |  |
| 2.2.181 | Ant. II, 2, 181 | Countenance | prose row break | 2.2.182 |  | ay sir we did sleep day out of |
| 4.4.13 | Ant. IV, 4, 13 | Daff | headword not found near cited line |  |  | to dafft for our repose shall hear a storm |
| 4.4.13 | Ant. IV, 4, 13 | Daff | headword not found near cited line |  |  | to dafft for our repose shall hear a storm |
| 3.1.119 | Shr. Ind. 1, 119. | Decline | not a citation of this play |  | with declineing head into his bosom, |  |
| 4.12.12 | Ant. IV, 12 | Deject | quotation elsewhere in scene | 4.12.6-7 | Antony is valiant, and dejected, | they cast their caps up and carouse together |
| 4.12.12 | Ant. IV, 12 | Deject | headword not found near cited line |  |  | they cast their caps up and carouse together |
| 5.1.1 | 1, 1 | Deride | headword not found near cited line |  |  | go to him dolabella bid him yield |
| 2.2.179 | Ant. II, 2, 179 | Disgest | headword not found near cited line |  |  | are so well digested you stayed well by t in |
| 2.2.208 | Ant. II, 2, 208 | Divers-coloured | headword not found near cited line |  |  | with diverscolored fans whose wind did seem |
| 4.4.13 | Ant. IV, 4, 13 | Doff | headword not found near cited line |  |  | to dafft for our repose shall hear a storm |
| 4.12.37 | Ant. IV, 12, 37 | Dolt | headword not found near cited line |  |  | for poorst diminutives for doits and let |
| 5.2.334 | Ant. V, 2, 334 | Dread | headword off by 1 | 5.2.335 |  | touch their effects in this thyself art coming |
| 1.1.35 | Ant. I, 1, 35 | Dung | headword not found near cited line |  |  | kingdoms are clay our dungy earth alike |
| 4.0 | IV Prol. 13 | Earn | not a citation of this play |  |  |  |
| 2.6.39 | Ant. II, 6, 39 | Edge | headword off by 1 | 2.6.38 |  | our targes undinted |
| 1.2.88 | Ant. I, 2, 88 | Enobarbus | prose row break | 1.2.87 |  | madam |
| 4.6.16 | Ant. IV, 6, 16 | Entertainment | quotation off by 1 | 4.6.17-18 | have e., but no honourable trust, | csar hath hanged him canidius and the rest |
| 2.0 | II Prol. 36 | Escapen | not a citation of this play |  |  |  |
| 1.2.106 | Ant. I, 2, 106 | Eúphrates | prose row break | 1.2.105 |  | his conquering banner shook from syria |
| 2.7.135 | Ant. II, 7, 135 | Father-house | headword not found near cited line |  |  | you have my fathers house but what we are friends |
| 2.7.135 | Ant. II, 7, 135 | Father-house | headword not found near cited line |  |  | you have my fathers house but what we are friends |
| 4.8.23 | Ant. IV, 8, 23 | Favourable | quotation not found; headword not found near cited line |  | favouring hand, | commend unto his lips thy favoring hand |
| 4.14.14 | Ant. IV, 14 | Forked | quotation elsewhere in scene | 4.14.5 | a forked mountain, | yet cannot hold this visible shape my knave |
| 4.14.14 | Ant. IV, 14 | Forked | headword not found near cited line |  |  | yet cannot hold this visible shape my knave |
| 2.133.7 | 133, 7 | Forsake | not a citation of this play |  |  |  |
| 1.2.53 | Ant. I, 2, 53 | Fruitfulness | headword not found near cited line |  |  | nay if an oily palm be not a fruitful |
| 4.6.9 | Ant. IV, 6, 9 | Fury | headword off by 1 | 4.6.10 |  | plant those that have revolted in the van |
| 3.1.68 | III, 1, 68 | Fury | headword not found near cited line |  |  | (no such line) |
| 5.5.8 | V, 5, 8 | Fury | not a citation of this play |  |  |  |
| 2.3.19 | Ant. II, 3, 19 | Genius | headword not found near cited line |  |  | thy demon thats thy spirit which keeps thee is |
| 4.2.33 | Ant. IV, 2, 33 | Godild | headword not found near cited line |  |  | and the gods yield you fort what mean you sir |
| 4.12.46 | Ant. IV, 12, 46 | Grasp | headword off by 1 | 4.12.45 |  | subdue my worthiest self the witch shall die |
| 3.0 | III Prol. 47 | Grizzled | not a citation of this play |  |  |  |
| 3.0 | III Prol. 47 | Grizzly | not a citation of this play |  | Grisly |  |
| 2.6.54 | II, 6, 54 | Harsh | quotation off by 1 | 2.6.55 | harsh fortune, | there is a change upon you well i know not |
| 2.7.4 | Ant. II, 7, 4 | High-coloured | headword not found near cited line |  |  | lepidus is highcolored |
| 2.7.141 | Ant. II, 7, 141 | Hoo | headword not found near cited line |  |  | ho says a theres my cap |
| 3.13.28 | Ant. III, 13, 28 | Horned | quotation elsewhere in scene | 3.13.128 | the horned herd, | ourselves alone ill write it follow me |
| 1.2.92 | Ant. I, 2, 92 | Idleness | quotation in another scene | 1.3.91 | but that your royalty holds idleness your subject, I should take you for idleness itself, | fulvia thy wife first came into the field |
| 1.2.92 | Ant. I, 2, 92 | Idleness | headword not found near cited line |  |  | fulvia thy wife first came into the field |
| 4.6.12 | IV, 6, 12 | Jezebel | headword not found near cited line |  |  | alexas did revolt and went to jewry on |
| 3.10.14 | Ant. III, 10, 14 | Junius | headword not found near cited line |  |  | the breese upon her like a cow in june |
| 3.0 | III Prol. 46 | Keel | not a citation of this play |  |  |  |
| 5.2.80 | Ant. V, 2, 80 | Keep | headword not found near cited line |  |  | a sun and moon which kept their course and lighted |
| 1.1.258 | I, 1, 258 | Kindle | quotation not found; headword not found near cited line |  | r. | (no such line) |
| 1.2.104 | Ant. I, 2, 104 | Labienus | prose row break | 1.2.103 |  | this is stiff newshath with his parthian force |
| 4.15.15 | Ant. IV, 15 | Level | quotation elsewhere in scene | 4.15.65-66 | young boys and girls are level now with men, | but antonys hath triumphed on itself |
| 4.15.15 | Ant. IV, 15 | Level | headword not found near cited line |  |  | but antonys hath triumphed on itself |
| 2.6.48 | Ant. II, 6, 48 | Liberal-conceited | headword not found near cited line |  |  | and am well studied for a liberal thanks |
| 4.12.45 | Ant. IV, 12, 45 | Lichas | headword off by 1 | 4.12.44 |  | and with those hands that grasped the heaviest club |
| 4.14.33 | Ant. IV, 14, 33 | Life-rendering | headword not found near cited line |  |  | between her heart and lips she rendered life |
| 3.11.5 | Ant. III, 11, 5 | Load | headword not found near cited line |  |  | laden with gold take that divide it fly |
| 5.2.123 | V, 2, 123 | Load | headword not found near cited line |  |  | been laden with like frailties which before |
| 3.11.5 | Ant. III, 11, 5 | Load | headword not found near cited line |  |  | laden with gold take that divide it fly |
| 5.2.123 | V, 2, 123 | Load | headword not found near cited line |  |  | been laden with like frailties which before |
| 3.3.36 | Ant. III, 3, 36 | Low | headword off by 1 | 3.3.37 |  | brown madam and her forehead |
| 1.2.94 | Ant. I, 2, 94 | Lucius | prose row break | 1.2.93 |  | ay |
| 3.0 | III Prol. 43 | Lychorida | not a citation of this play |  |  |  |
| 3.1.6 | III, 1, 6 | Lychorida | headword not found near cited line |  |  | whilst yet with parthian blood thy sword is warm |
| 1.4.48 | Ant. I, 4, 48 | Menelaus | headword not found near cited line |  |  | menecrates and menas famous pirates |
| 3.0 | III Prol. 46 | Mood | not a citation of this play |  |  |  |
| 2.4.26 | II, 4, 26 | Natural | quotation not found; headword not found near cited line |  | natural luck, | (no such line) |
| 3.152.3 | 152, 3 | New | not a citation of this play |  | new faith torn in vowing new hate after new love bearing, |  |
| 3.152.3 | 152, 3 | New | not a citation of this play |  |  |  |
| 3.0 | III Prol. 17 | Oppose | not a citation of this play |  |  |  |
| 4.12.21 | Ant. IV, 12, 21 | Pannel | headword not found near cited line |  |  | that spanieled me at heels to whom i gave |
| 5.147.9 | 147, 9 | Past | not a citation of this play |  | now reason is past care, |  |
| 4.0 | IV Prol. 40 | Peerless | not a citation of this play |  |  |  |
| 4.9.30 | Ant. IV, 9, 30 | Reach | headword not found near cited line |  |  | the hand of death hath raught him hark the drums |
| 4.4.30 | Ant. IV, 4, 30 | Rebukable | headword not found near cited line |  |  | this is a soldiers kiss rebukeable |
| 1.2.94 | Shr. Ind. 2, 94. | Reckon | not a citation of this play |  | you know no house, nor no such men as you have reckoned up, |  |
| 5.122.8 | 122, 8 | Record | not a citation of this play |  | thy record never can be missed, |  |
| 4.123.11 | 123, 11 | Record | not a citation of this play |  | records and what we see doth lie, |  |
| 1.111.8 | 111, 8 | Renew | not a citation of this play |  | wish I were renewed, |  |
| 1.78.14 | 78, 14 | Rude | not a citation of this play |  | my rude ignorance, |  |
| 5.62.12 | 62, 12 | Self | not a citation of this play |  | self so self-loving were iniquity, |  |
| 1.1.125 | Shr. Ind. 1, 125. | Shower | not a citation of this play |  |  |  |
| 3.45.8 | 45, 8 | Sink | not a citation of this play |  | my life sinks down to death, |  |
| 3.7.42 | III, 7, 42 | Soldiership | headword off by 1 | 3.7.43 |  | most worthy sir you therein throw away |
| 4.8.20 | Ant. IV, 8, 20 | Something-settled | headword not found near cited line |  |  | do something mingle with our younger brown yet ha we |
| 4.15.79 | Ant. IV, 15, 79 | Sottish | headword not found near cited line |  |  | patience is scottish and impatience does |
| 4.12.47 | IV, 12, 47 | Subdue | quotation off by 1 | 4.12.45-46 | with those hands . . . subdue my worthiest self, | to the young roman boy she hath sold me and i fall |
| 4.12.4 | Ant. IV, 12, 4 | Swallow | headword off by 1 | 4.12.3 |  | in cleopatras sails their nests the augurers |
| 1.5.48 | Ant. I, 5, 48 | Termagant | headword not found near cited line |  |  | and soberly did mount an armgaunt steed |
| 2.2.21 | Shr. Ind. 2, 21 | Transmutation | not a citation of this play |  | by education a card-maker, by transmutation a bear-herd, |  |
| 3.6.28 | Ant. III, 6, 28 | Triumpherate | headword not found near cited line |  |  | that lepidus of the triumvirate |
| 5.2.311 | Ant. V, 2, 311 | Unpolished | headword not found near cited line |  |  | unpolicied o eastern star peace peace |
| 2.1.50 | Ant. II, 1, 50 | Upon | headword off by 1 | 2.1.51 |  | bet as our gods will havet it only stands |
| 1.6.5 | 6, 5 | Use | not a citation of this play |  | that use is not forbidden usury which happies those that pay the willing loan, |  |
| 1.30.4 | 30, 4 | Waste | not a citation of this play |  | with old woes new wail my dear time's waste |  |
| 4.3.17 | Ant. IV, 3, 17 | Watchman | headword off by 1 | 4.3.18 |  | now leaves him |
| 2.6.97 | Ant. II, 6, 97 | Water-thieves | headword not found near cited line |  |  | and you by land |
| 2.6.102 | Ant. II, 6, 102 | Whatsome'er | headword not found near cited line |  |  | all mens faces are true what someer |
