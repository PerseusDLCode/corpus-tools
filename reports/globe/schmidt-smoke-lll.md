# Schmidt smoke test: Love's Labor's Lost

Sources: shakespeare.lll.globe.xml sha256 238f4300583b2954; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of Love's Labor's Lost in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1872/1997 (93.7%) pass.
- **With a quotation:** 1150/1187 (96.9%) have it on the cited line.
- **Headword only:** 722/810 (89.1%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 908 |
| headword on cited line | 781 |
| quotation on cited line, with differences | 183 |
| headword not found near cited line | 59 |
| prose row break | 16 |
| not a citation of this play | 15 |
| quotation not found; headword not found near cited line | 12 |
| headword off by 1 | 11 |
| quotation off by 1 | 9 |
| quotation elsewhere in scene | 2 |
| headword off by 3 | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

| Scene | Cited lines | Offset | Citations |
|---|---|---|---|
| 4.3 | 42-45 | -1 | 3 |
| 4.3 | 212-215 | +1 | 3 |
| 5.2 | 892-895 | +1 | 5 |

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 5.1.26 | LLL V, 1, 26 | Abhominable | prose row break | 5.1.27 | abominable: | neigh abbreviated ne this is |
| 5.1.27 | LLL V, 1, 27 | Abominable | headword not found near cited line |  |  | abhominable which he would call abbominable it insinuateth |
| 3.67 | LLL III, 67 | Acute | not a citation of this play |  | a most acute juvenal, |  |
| 5.1.4 | LLL V, 1, 4 | Affectation | headword not found near cited line |  |  | pleasant without scurrility witty with out affection |
| 4.3.14 | LLL IV, 3, 14 | Allycholly | quotation not found; headword not found near cited line |  | Mallicholie | me to rhyme and to be melancholy and here is |
| 5.1.101 | Shr. Ind. 1, 101. | Antic | quotation not found; headword not found near cited line |  | were he the veriest antic in the world, | my familiar i do assure ye very good friend |
| 5.2.37 | Shr. Ind. 2, 37. | Apollo | headword not found near cited line |  |  | i am compared to twenty thousand fairs |
| 4.3.209 | LLL IV, 3, 209 | Audience. | quotation off by 1 | 4.3.210 | dismiss this audience | are pickpurses in love and we deserve to die |
| 4.3.187 | LLL IV, 3, 187 | Away | headword off by 1 | 4.3.186 |  | a true man or a thief that gallops so |
| 1.1.101 | LLL I, 1, 101 | Bite | quotation off by 1 | 1.1.100 | a frost that bites the firstborn infants of the spring, | well say i am why should proud |
| 1.1.234 | LLL I, 1, 234 | Black-oppressing | prose row break | 1.1.235 |  | sablecoloured melancholy i did commend the |
| 5.2.619 | LLL V, 2, 619 | Bone | headword not found near cited line |  |  | the carvedbone face on a flask |
| 3.1.36 | III Prol. 36 | Can | headword not found near cited line |  |  | negligent student learn her by heart |
| 5.2.140 | Shr. Ind. 2, 140. | Christmas | quotation not found; headword not found near cited line |  | a Christmas gambold or a tumbling-trick, | and mock for mock is only my intent |
| 5.2.19 | Shr. Ind. 2, 19. | Christopher | headword not found near cited line |  |  | whats your dark meaning mouse of this light word |
| 5.2.655 | LLL V, 2, 655 | Cleave | headword not found near cited line |  |  | no cloven |
| 5.2.655 | LLL V, 2, 655 | Cleave | quotation not found; headword not found near cited line |  | cloven lemon, | no cloven |
| 5.2.603 | LLL V, 2, 603 | Clepe | headword not found near cited line |  |  | judas maccabaeus clipt is plain judas |
| 5.2.580 | LLL V, 2, 580 | Close-stool | prose row break | 5.2.581 |  | lion that holds his pollaxe sitting on a |
| 4.2.156 | LLL IV, 2, 156 | Colourable | quotation off by 1 | 4.2.155 | I do fear colourable colours, | colorable colors but to return to the verses |
| 4.2.45 | LLL IV, 2, 45 | Comfort | quotation off by 1 | 4.2.44 | god comfort thy capacity, | allusion holds in the exchange |
| 1.2.67 | LLL I, 2, 67 | Comfort | prose row break | 1.2.68 |  | sigh methinks i should outswear cupid |
| 5.1.6 | LLL V, 1, 6 | Converse | prose row break | 5.1.7 |  | opinion and strange without heresy i did |
| 1.1.20 | Shr. Ind. 1, 20. | Corner | quotation elsewhere in scene | 1.1.156-157 | at the hedge-corner, | that his own hand may strike his honour down |
| 4.3.58 | LLL IV, 3, 58 | Corner-cap | quotation elsewhere in scene | 4.3.53 | thou makest the triumviry, the corner-cap of society, | o rhymes are guards on wanton cupids hose |
| 4.3.87 | LLL IV, 3, 87 | Cote | headword not found near cited line |  |  | her amber hair for foul hath amber quoted |
| 5.2.221 | LLL V, 2, 221 | Courtesy | headword not found near cited line |  |  | curtsy sweet hearts and so the measure ends |
| 3.1.103 | LLL III, 103 | Cunning | quotation off by 1 | 3.1.104 | to sell a bargain well is as cunning as fast and loose, | sir your pennyworth is good an your goose be fat |
| 3.1.140 | LLL III, 140 | D | headword not found near cited line |  |  | of this inkle one penny no ill give you |
| 1.2.136 | LLL I, 2, 136 | Day-woman | prose row break | 1.2.137 |  | keep her at the park she is allowed for the |
| 1.1.23 | LLL I, 1, 23 | Deep-divorcing: | headword not found near cited line |  |  | subscribe to your deep oaths and keep it too |
| 1.1.23 | LLL I, 1, 23 | Deep-drawing | quotation not found; headword not found near cited line |  | deep-drawing barks, | subscribe to your deep oaths and keep it too |
| 1.1.221 | LLL I, 1, 221 | Deputation | headword not found near cited line |  |  | great deputy the welkins |
| 5.2.523 | LLL V, 2, 523 | Description | headword off by 1 | 5.2.522 |  | anointed i implore so much expense |
| 5.2.895 | LLL V, 2, 895 | Dialogue | headword off by 1 | 5.2.896 |  | years but most esteemed greatness will you |
| 5.1.145 | LLL V, 1, 145 | Do | headword off by 3 | 5.1.148 |  | audience hiss you may cry well done |
| 3.1.182 | LLL III, 182 | Don | quotation not found; headword not found near cited line |  | Don Cupid, | this seniorjunior giantdwarf dan cupid |
| 4.3.215 | LLL IV, 3, 215 | Ebb | headword off by 1 | 4.3.216 |  | as true we are as flesh and blood can be |
| 1.1.246 | LLL I, 1, 246 | Ebon-coloured | headword not found near cited line |  |  | eboncolored ink which here thou viewest |
| 3.1.144 | LLL III, 144 | Exceedingly | prose row break | 3.1.145 | well: | o my good knave costard |
| 4.2.14 | LLL IV, 2, 14 | Explication | prose row break | 4.2.15 |  | of insinuation as it were in via in way of |
| 4.2.50 | IV, 2, 50 | Extemporal | prose row break | 4.2.51 | extemporal epitaph, | sir nathaniel will you hear an |
| 5.1.26 | Shr. Ind. 1, 26. | Fleet | headword not found near cited line |  |  | neigh abbreviated ne this is |
| 5.2.50 | 2, 50 | Fleet | headword not found near cited line |  |  | some thousand verses of a faithful lover |
| 5.97.2 | 97, 2 | Fleet | not a citation of this play |  | from thee, the pleasure of the fleeting year, |  |
| 4.3.215 | LLL IV, 3, 215 | Flow | headword off by 1 | 4.3.216 |  | as true we are as flesh and blood can be |
| 4.3.212 | LLL IV, 3, 212 | Folk | headword off by 1 | 4.3.213 |  | will these turtles be gone hence sirs away |
| 2.1.93 | II, 1 | Forage | headword not found near cited line |  |  | is too high to be yours and welcome to the wide |
| 5.1.3 | 1, 3 | Generous | headword not found near cited line |  |  | at dinner have been sharp and sententious |
| 5.1.3 | 1, 3 | Generous | headword not found near cited line |  |  | at dinner have been sharp and sententious |
| 1.1.129 | LLL I, 1, 129 | Gentlety | headword not found near cited line |  |  | a dangerous law against gentility |
| 5.2.652 | LLL V, 2, 652 | Gíld | headword not found near cited line |  |  | a gilt nutmeg |
| 4.3.106 | LLL IV, 3, 106 | Gin | quotation not found; headword not found near cited line |  | gan; can in | all unseen can passage find |
| 4.3.106 | LLL IV, 3, 106 | Gin | headword not found near cited line |  |  | all unseen can passage find |
| 5.2.49 | Shr. Ind. 2, 49. | Greyhound | headword not found near cited line |  |  | yes madam and moreover |
| 5.2.52 | V, 2, 52 | Greyhound | headword not found near cited line |  |  | vilely compiled profound simplicity |
| 5.2.545 | LLL V, 2, 545 | Hedge-priest | prose row break | 5.2.546 |  | the pedant the braggart the |
| 5.1.49 | LLL V, 1, 49 | Horn-book | prose row break | 5.1.50 |  | yes yeshe teaches boys the |
| 2.1.99 | Shr. Ind. 1, 99. | Impatient | headword not found near cited line |  |  | not for the world fair madam by my will |
| 2.1.152 | II, 152 | Impatient | headword not found near cited line |  |  | a yielding gainst some reason in my breast |
| 3.2.29 | III, 2, 29 | Impatient | not a citation of this play |  |  |  |
| 4.3.222 | LLL IV, 3, 222 | Ind | headword not found near cited line |  |  | that like a rude and savage man of inde |
| 2.225 | LLL II, 225 | Jangle | not a citation of this play |  | good wits will be jangleing, |  |
| 3.67.8 | III, 67 | Juvenal | not a citation of this play |  |  |  |
| 4.3.45 | LLL IV, 3, 45 | Listen | quotation off by 1 | 4.3.44 | listen | now in thy likeness one more fool appear |
| 1.1.53 | Shr. Ind. 1, 53 | Low | quotation not found; headword not found near cited line |  | with a low submissive reverence, | you swore to that biron and to the rest |
| 4.1.114 | Shr. Ind. 1, 114. | Low | quotation not found; headword not found near cited line |  | with soft low tongue, | hang me by the neck if horns that year miscarry |
| 5.1.63 | Shr. Ind. 1, 63. | Lunatic | headword not found near cited line |  |  | snip snap quick and home it rejoiceth my |
| 2.289.63 | II, 289 | Lunatic | not a citation of this play |  |  |  |
| 5.1.74 | V, 1, 74 | Lunatic | headword not found near cited line |  |  | an i had but one penny in the |
| 5.2.724 | LLL V, 2, 724 | Marcade | headword not found near cited line |  |  | welcome mercade |
| 5.2.22 | Shr. Ind. 2, 22. | Marian | headword not found near cited line |  |  | youll mar the light by taking it in snuff |
| 5.1.61 | LLL V, 1, 61 | Mediterraneum | prose row break | 5.1.62 |  | now by the salt wave of the |
| 4.3.42 | IV, 3, 42 | Mortal | headword off by 1 | 4.3.41 |  | how shall she know my griefs ill drop the paper |
| 5.15.14 | 15, 14 | New | not a citation of this play |  | as he takes from you, I engraft you new |  |
| 5.53.8 | 53, 8 | New | not a citation of this play |  | on Helen's cheek all art of beauty set, and you in Grecian tires are painted new |  |
| 5.68.12 | 68, 12 | New | not a citation of this play |  | robbing no old to dress his beauty new |  |
| 5.153.9 | 153, 9 | New | not a citation of this play |  | love's brand new fired, |  |
| 1.1.239 | LLL I, 1, 239 | Nourishment | prose row break | 1.1.240 |  | birds best peck and men sit down to that |
| 3.1.3 | III Prol. 3 | O'erfed | headword not found near cited line |  |  | concolinel |
| 1.2.190 | LLL I, 2, 190 | Orthography | headword not found near cited line |  |  | rhyme for i am sure i shall turn sonnet |
| 5.2.776 | LLL V, 2, 776 | Party-coated | headword not found near cited line |  |  | which particoated presence of loose love |
| 5.2.315 | LLL V, 2, 315 | Pea | headword not found near cited line |  |  | this fellow pecks up wit as pigeons pease |
| 1.2.160 | LLL I, 2, 160 | Pen | headword not found near cited line |  |  | let me not be pent up sir i will fast |
| 1.101.7 | 101, 7 | Pencil | not a citation of this play |  |  |  |
| 4.1.67 | LLL IV, 1, 67 | Penelophon | headword not found near cited line |  |  | indubitate beggar zenelophon and he it was |
| 3.1.17 | LLL III, 17 | Penthouse-like | prose row break | 3.1.18 |  | love by smelling love with your hat |
| 5.2.67 | LLL V, 2, 67 | Pertaunt-like | headword not found near cited line |  |  | so perttauntlike would i oersway his state |
| 4.3.208 | LLL IV, 3, 208 | Pick-purse | headword off by 1 | 4.3.209 |  | he he and you and you my liege and i |
| 4.2.57 | LLL IV, 2, 57 | Pleasing | quotation off by 1 | 4.2.58 | a pretty pleasing pricket, | argues facility |
| 4.2.142 | Shr. Ind. 2, 142. | Pleasing | quotation not found; headword not found near cited line |  | more pleasing stuff, | and here he hath framed a letter to a sequent of |
| 4.3.102 | IV, 3, 102 | Pleasing | quotation not found; headword not found near cited line |  | a gown more quaint, more pleasing | love whose month is ever may |
| 5.2.893 | LLL V, 2, 893 | Plough | headword off by 1 | 5.2.894 |  | leave i am a votary i have vowed to |
| 5.2.580 | LLL V, 2, 580 | Pole-axe | headword not found near cited line |  |  | lion that holds his pollaxe sitting on a |
| 4.2.58 | LLL IV, 2, 58 | Praiseful | headword not found near cited line |  |  | the preyful princess pierced and pricked a pretty pleasing pricket |
| 4.2.71 | LLL IV, 2, 71 | Primater | headword not found near cited line |  |  | memory nourished in the womb of pia mater |
| 5.2.760 | LLL V, 2, 760 | Profitable | headword not found near cited line |  |  | is not by much so wholesomeprofitable |
| 5.2.871 | LLL V, 2, 871 | Prosperously | headword not found near cited line |  |  | a jests prosperity lies in the ear |
| 5.2.618 | LLL V, 2, 618 | Pummel | headword not found near cited line |  |  | the pommel of caesars falchion |
| 5.1.125 | Shr. Ind. 1, 125. | Rain | headword not found near cited line |  |  | worthies sir as concerning some entertainment |
| 1.1.233 | LLL I, 1, 233 | Sable-coloured | prose row break | 1.1.234 | sable-coloured melancholy, | so it is besieged with |
| 4.3.168 | IV, 3, 168 | Salomon | headword not found near cited line |  |  | and profound solomon to tune a jig |
| 5.1.28 | LLL V, 1, 28 | Sanity | headword not found near cited line |  |  | me of insanie anne intelligis domine to make |
| 4.1.121 | LLL IV, 1, 121 | Saying | prose row break | 4.1.122 |  | shall i come upon thee with an old |
| 4.3.44 | LLL IV, 3, 44 | Shade | quotation off by 1 | 4.3.43 | sweet leaves, shade folly, | what longaville and reading listen ear |
| 5.2.107 | LLL V, 2, 107 | Shoulder-clapper | headword not found near cited line |  |  | with that all laughed and clapped him on the shoulder |
| 4.3.28 | LLL IV, 3, 28 | Smite | headword not found near cited line |  |  | as thy eyebeams when their fresh rays have smote |
| 5.1.137 | Shr. Ind. 1, 137. | Spleen | quotation not found; headword not found near cited line |  | abate their over-merry spleen | pardon sir error he is not quantity |
| 4.3.343 | LLL IV, 3, 343 | String | headword not found near cited line |  |  | as bright apollos lute strung with his hair |
| 4.1.53 | Shr. Ind. 1, 53. | Submissive | headword not found near cited line |  |  | i have a letter from monsieur biron to one lady rosaline |
| 5.1.28 | Shr. Ind. 1, 28. | Superbus | headword not found near cited line |  |  | me of insanie anne intelligis domine to make |
| 4.2.65 | LLL IV, 2, 65 | Talon | headword not found near cited line |  |  | if a talent be a claw look how |
| 1.1.185 | LLL I, 1, 185 | Thirdborough | headword not found near cited line |  |  | i am his graces tharborough but i would see his |
| 3.2.140 | Shr. Ind. 2, 140 | Tumbling-trick | not a citation of this play |  | a Christmas gambold or a tumbling-trick |  |
| 4.2.90 | LLL IV, 2, 90 | Turf | headword not found near cited line |  |  | conceit in a tuft of earth fire enough for a flint |
| 4.3.54 | LLL IV, 3, 54 | Tymbria | headword not found near cited line |  |  | the shape of loves tyburn that hangs up simplicity |
| 5.1.2 | 1, 2 | Vilely | headword not found near cited line |  |  | i praise god for you sir your reasons |
| 5.1.2 | 1, 2 | Vilely | headword not found near cited line |  |  | i praise god for you sir your reasons |
| 3.67 | LLL III, 67 | Volable | not a citation of this play |  |  |  |
| 3.67 | LLL III, 67 | Voluble | not a citation of this play |  | a most acute juvenal; voluble and free of grace, |  |
| 5.2.892 | V, 2, 892 | Votary | headword off by 1 | 5.2.893 |  | i will kiss thy royal finger and take |
| 5.2.892 | V, 2, 892 | Vow | quotation off by 1 | 5.2.893-894 | I have vowed to Jaquenetta to hold the plough, | i will kiss thy royal finger and take |
| 5.2.892 | V, 2, 892 | Vow | headword off by 1 | 5.2.893 |  | i will kiss thy royal finger and take |
| 3.2.54 | Shr. Ind. 2, 54. | Wanton | not a citation of this play |  | seem to move and wanton with her breath, |  |
| 5.2.602 | V, 2, 602 | Ycleped | headword not found near cited line |  |  | judas i am ycliped maccabaeus |
