# Schmidt smoke test: Othello

Sources: shakespeare.oth.globe.xml sha256 46071431f2b93960; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of Othello in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1893/1999 (94.7%) pass.
- **With a quotation:** 1222/1257 (97.2%) have it on the cited line.
- **Headword only:** 671/742 (90.4%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 962 |
| headword on cited line | 694 |
| quotation on cited line, with differences | 237 |
| headword not found near cited line | 49 |
| not a citation of this play | 32 |
| quotation not found; headword not found near cited line | 7 |
| quotation off by 1 | 6 |
| prose row break | 5 |
| headword off by 1 | 4 |
| quotation elsewhere in scene | 3 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

None.

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 4.1.5 | IV, 1, 5 | A-bed | headword not found near cited line |  |  | naked in bed iago and not mean harm |
| 3.2.125 | Shr. Ind. 2, 125. | Absént | not a citation of this play |  | that I should yet absént me from your bed, |  |
| 1.2.78 | Oth. I, 2, 78 | Abut | quotation not found; headword not found near cited line |  | whose high upreared and abuting fronts the perilous narrow ocean parts asunder, | for an abuser of the world a practiser |
| 2.1.110 | Oth. II, 1, 110 | Adoors; | headword not found near cited line |  |  | come on come on you are pictures out of doors |
| 1.2.43 | I, 2, 43 | Affirm | headword not found near cited line |  |  | and many of the consuls raised and met |
| 5.2.117 | V, 2, 117 | Affirm | quotation not found; headword not found near cited line |  | I must not blush to affirm it, | o falsely falsely murdered alas what cry is that |
| 4.145.8 | 145, 8 | Anew | not a citation of this play |  | and taught it thus anew to greet, |  |
| 5.2.206 | Oth. V, 2, 206 | A-twain | quotation not found; headword not found near cited line |  | in twain). shore his old thread a-twain | shore his old thread in twain did he live now |
| 4.3.95 | Oth. IV, 3, 95 | Balance | headword not found near cited line |  |  | their wives have sense like them they see and smell |
| 5.103.3 | 103, 3 | Bare | not a citation of this play |  | the argument all bare is of more worth than . . ., |  |
| 5.103.3 | 103, 3 | Bare | not a citation of this play |  |  |  |
| 2.4.304 | Oth. II, 4, 304 | Befall. | not a citation of this play |  |  |  |
| 2.50.14 | 50, 14 | Behind. | not a citation of this play |  | my grief lies onward, and my joy behind |  |
| 5.2.25 | Oth. V, 2, 25 | Bethink | quotation off by 1 | 5.2.26 | if you bethink yourself of any crime, | have you prayed tonight desdemona ay my lord |
| 2.60.10 | 60, 10 | Brow | not a citation of this play |  | time delves the parallels in beauty's brow |  |
| 1.3.189 | Oth. I, 3, 189 | Buy | headword not found near cited line |  |  | due to the moor my lord god be wi you i have done |
| 3.3.375 | III, 3, 375 | Buy | headword not found near cited line |  |  | god be wi you take mine office o wretched fool |
| 1.2.50 | Oth. I, 2, 50 | Carrack | headword not found near cited line |  |  | faith he tonight hath boarded a land carack |
| 2.2.7 | Oth. II, 2, 7 | Celebration | prose row break | 2.2.8 |  | for besides these beneficial news it is the |
| 5.2.164 | Oth. V, 2, 164 | Clay-brained | headword not found near cited line |  |  | as ignorant as dirt thou hast done a deed |
| 5.107.3 | 107, 3 | Control | not a citation of this play |  | not mine own fears, nor the prophetic soul of the wide world . . . can yet the lease of my true love control |  |
| 1.2.68 | Oth. I, 2, 68 | Dearlings | headword not found near cited line |  |  | the wealthy curled darlings of our nation |
| 1.1.235 | 1, 235 | Delicate | headword not found near cited line |  |  | (no such line) |
| 1.3.369 | Oth. I, 3, 369 | Depend | prose row break | 1.3.370 |  | wilt thou be fast to my hopes if i |
| 2.3.160 | Oth. II, 3, 160 | Diablo | headword off by 1 | 2.3.161 |  | help masters heres a goodly watch indeed |
| 4.2.61 | Oth. IV, 2, 61 | Discard | quotation off by 1 | 4.2.59-60 | the fountain from the which my current runs, to be discarded thence! | or keep it as a cistern for foul toads |
| 1.3.155 | Oth. I, 3, 155 | Distinctively | headword not found near cited line |  |  | but not intentively i aid consent |
| 4.1.28 | Oth. IV, 1, 28 | Door-keeper | headword not found near cited line |  |  | convinced or supplied them cannot choose |
| 4.1.77 | Oth. IV, 1, 77 | Erewhile | headword not found near cited line |  |  | whilst you were here oerwhelmed with your grief |
| 1.1.137 | I, 1, 137 | Err | headword not found near cited line |  |  | in an extravagant and wheeling stranger |
| 1.1.138 | Oth. I, 1, 138 | Everywhere | headword not found near cited line |  |  | of here and every where straight satisfy yourself |
| 1.1.57 | Shr. Ind. 1, 57. | Ewer | not a citation of this play |  |  |  |
| 2.350.57 | II, 350 | Ewer | not a citation of this play |  |  |  |
| 2.1.65 | Oth. II, 1, 65 | Excellency | headword not found near cited line |  |  | does tire the ingener how now who has put in |
| 4.1.257 | Oth. IV, 1, 257 | Eysell | headword not found near cited line |  |  | each drop she falls would prove a crocodile |
| 4.2.54 | Oth. IV, 2, 54 | Fixture | headword not found near cited line |  |  | a fixed figure for the time of scorn |
| 1.361.83 | I, 361 | Fleer | not a citation of this play |  |  |  |
| 4.2.63 | Oth. IV, 2, 63 | Gender | quotation off by 1 | 4.2.61-62 | a cistern for foul toads to knot and gender in, | patience thou young and roselipped cherubin |
| 4.2.63 | Oth. IV, 2, 63 | General | headword not found near cited line |  |  | patience thou young and roselipped cherubin |
| 4.2.63 | Oth. IV, 2, 63 | General | quotation not found; headword not found near cited line |  | the general doom, | patience thou young and roselipped cherubin |
| 1.1.131 | I, 1 | Giving-out | quotation elsewhere in scene | 1.1.142 | Give | we have your wrong rebuke do not believe |
| 3.3.100 | Oth. III, 3, 100 | Go-between | headword not found near cited line |  |  | o yes and went between us very oft |
| 2.0 | II Prol. 22 | Hap | not a citation of this play |  |  |  |
| 2.1.3 | Oth. II, 1, 3 | Haven | headword not found near cited line |  |  | i cannot twixt the heaven and the main |
| 3.4.165 | Oth. III, 4, 165 | Hereabout | headword not found near cited line |  |  | i will go seek him cassio walk here about |
| 2.3.80 | Oth. II, 3, 80 | Hollander | prose row break | 2.3.81 |  | your german and your swagbellied |
| 3.2.69 | Shr. Ind. 2, 69. | Inferior | not a citation of this play |  |  |  |
| 2.3.42 | Oth. II, 3, 42 | Infortunate | headword not found near cited line |  |  | innovation it makes here i am unfortunate in |
| 5.2.283 | V, 2, 283 | Infortunate | headword not found near cited line |  |  | where is this rash and most unfortunate man |
| 3.3.423 | Oth. III, 3, 423 | Inside | headword not found near cited line |  |  | as if he plucked up kisses by the roots |
| 1.3.154 | Oth I, 3, 154 | Instinctively | headword not found near cited line |  |  | whereof by parcels she had something heard |
| 1.3.154 | Oth I, 3, 154 | Instinctively | headword not found near cited line |  |  | whereof by parcels she had something heard |
| 1.1.113 | Oth. I, 1, 113 | Jennet | quotation off by 1 | 1.1.114 | jennets for germans, | to you youll have coursers for cousins and |
| 5.2.347 | Oth. V, 2, 347 | Judean | headword not found near cited line |  |  | like the base indian threw a pearl away |
| 1.2.50 | Oth. I, 2, 50 | Land-carrack | headword not found near cited line |  |  | faith he tonight hath boarded a land carack |
| 4.1.280 | Oth. IV, 1, 280 | Lightness | headword not found near cited line |  |  | are his wits safe is he not light of brain |
| 5.2.88 | Oth. V, 2, 88 | Linger | quotation off by 1 | 5.2.87 | linger in thy pain, | so so |
| 2.3.213 | Oth. II, 3, 213 | Loose | headword not found near cited line |  |  | shall lose me what in a town of war |
| 1.2.68 | Oth. I, 2, 68 | Minion | headword not found near cited line |  |  | the wealthy curled darlings of our nation |
| 3.3.70 | Oth. III, 3, 70 | Mutter | quotation elsewhere in scene | 3.3.416-417 | there are a kind of men so loose of soul, that in their sleeps will mutter their affairs, | or stand so mammering on what michael cassio |
| 3.4.40 | Oth. III, 4, 40 | Number | quotation elsewhere in scene | 3.4.69-71 | a sibyl that had numbered in the world the sun to course two hundred compasses, | a sequester from liberty fasting and prayer |
| 4.3.75 | Oth. IV, 3, 75 | Od | quotation not found; headword not found near cited line |  | od's pity, | exhibition but for the whole world why who |
| 3.146.14 | 146, 14 | Once | not a citation of this play |  | death once dead, there's no more dying, |  |
| 2.45.8 | 45, 8 | Oppress | not a citation of this play |  | my life sinks down to death, oppressed with melancholy, |  |
| 3.0 | III Prol. 29 | Oppress | not a citation of this play |  |  |  |
| 4.2.139 | Oth. IV, 2, 139 | Outrageous | headword not found near cited line |  |  | the moors abused by some most villanous knave |
| 2.3.54 | Oth. II, 3, 54 | Outward | headword not found near cited line |  |  | whom love hath turned almost the wrong side out |
| 2.147.9 | 147, 9 | Past | not a citation of this play |  | past cure, |  |
| 4.1.150 | Oth. IV, 1, 150 | Perfúme | prose row break | 4.1.151 |  | tis such another fitchew marry a |
| 2.86.6 | 86, 6 | Pitch | not a citation of this play |  | to write above a mortal pitch |  |
| 2.88.2 | 88, 2 | Place | not a citation of this play |  | merit in the eye of scorn, |  |
| 1.3.151 | Oth. I, 3, 151 | Plight | headword not found near cited line |  |  | took once a pliant hour and found good means |
| 1.3.46 | Oth. I, 3, 46 | Post-horse | headword not found near cited line |  |  | write from us to him postposthaste dispatch |
| 3.12.3 | 12, 3 | Prime | not a citation of this play |  | past prime |  |
| 3.70.8 | 70, 8 | Prime | not a citation of this play |  | a pure unstained prime |  |
| 1.2.21 | Oth. I, 2, 21 | Provulgate | headword not found near cited line |  |  | i shall promulgate i fetch my life and being |
| 1.2.72 | I, 2, 72 | Purchase | quotation not found; headword not found near cited line |  | I sought the purchase of a glorious beauty, | judge me the world if tis not gross in sense |
| 3.3.259 | Oth. III, 3, 259 | Quantity | headword not found near cited line |  |  | and knows all qualities with a learned spirit |
| 1.1.159 | I, 1, 159 | Quest | headword not found near cited line |  |  | lead to the sagittary the raised search |
| 1.1.57 | Oth. I, 1, 57 | Roderigo | headword off by 1 | 1.1.56 |  | were i the moor i would not be iago |
| 1.2.46 | I, 2, 46 | Search | headword off by 1 | 1.2.47 |  | the senate hath sent about three several quests |
| 1.3.331 | Oth. I, 3, 331 | Sensuality | prose row break | 1.3.332 |  | not one scale of reason to poise another of |
| 3.2.48 | Shr. Ind. 2, 48. | Shrill | not a citation of this play |  | thy hounds shall make the welkin answer them and fetch shrill echoes from the hollow earth, |  |
| 5.1.4 | 1, 4 | Slimy | headword not found near cited line |  |  | it makes us or it mars us think on that |
| 5.1.4 | 1, 4 | Slimy | headword not found near cited line |  |  | it makes us or it mars us think on that |
| 5.2.16 | Oth. V, 2, 16 | Smell | headword off by 1 | 5.2.15 |  | ah balmy breath that doth almost persuade |
| 3.3.469 | Oth. III, 3, 469 | Soever | headword not found near cited line |  |  | what bloody business ever i greet thy love |
| 3.0 | III Prol. 21 | Stead | not a citation of this play |  |  |  |
| 4.0 | IV Prol. 41 | Stead | not a citation of this play |  |  |  |
| 3.4.51 | Oth. III, 4, 51 | Sullen | headword not found near cited line |  |  | i have a salt and sorry rheum offends me |
| 4.12.11 | 12, 11 | Sweet | not a citation of this play |  | sweets and beauties do themselves forsake, |  |
| 4.19.7 | 19, 7 | Sweet | not a citation of this play |  | the wide world and all her fading sweets, |  |
| 4.95.4 | 95, 4 | Sweet | not a citation of this play |  | in what sweets dost thou thy sins enclose, |  |
| 4.102.12 | 102, 12 | Sweet | not a citation of this play |  | sweets grown common lose their dear delight, |  |
| 4.125.7 | 125, 7 | Sweet | not a citation of this play |  | for compound sweet forgoing simple savour, |  |
| 5.2.203 | V, 2, 203 | Terrible | headword not found near cited line |  |  | i know this act shows horrible and grim |
| 2.3.160 | Oth. II, 3, 160 | That | quotation off by 1 | 2.3.161 | who's that which rings the bell? | help masters heres a goodly watch indeed |
| 2.1.280 | Oth. II, 1, 280 | Truncheon | headword not found near cited line |  |  | and haply may strike at you provoke him that |
| 3.3.396 | In III, 3, 396 | Tup | headword not found near cited line |  |  | behold her topped death and damnation o |
| 5.2.136 | V, 2, 136 | Tup | headword not found near cited line |  |  | cassio did top her ask thy husband else |
| 2.3.311 | Oth. II, 3, 311 | Unordinate | headword not found near cited line |  |  | inordinate cup is unblessed and the ingredient is |
| 3.4.133 | Oth. III, 4, 133 | Unraised | quotation not found; headword not found near cited line |  | the flat unraised spirits, | and certainly in strange unquietness |
| 3.3.365 | Oth. III, 3, 365 | Weak-hinged | headword not found near cited line |  |  | that the probation bear no hinge nor loop |
| 2.107.2 | 107, 2 | Wide | not a citation of this play |  |  |  |
| 2.137.10 | 137, 10 | Wide | not a citation of this play |  |  |  |
| 2.0 | II Prol. 12 | Writ | not a citation of this play |  |  |  |
