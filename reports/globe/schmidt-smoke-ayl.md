# Schmidt smoke test: As You Like It

Sources: shakespeare.ayl.globe.xml sha256 97f901496078673b; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of As You Like It in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1464/1565 (93.5%) pass.
- **With a quotation:** 880/911 (96.6%) have it on the cited line.
- **Headword only:** 584/654 (89.3%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 696 |
| headword on cited line | 616 |
| quotation on cited line, with differences | 152 |
| headword not found near cited line | 41 |
| not a citation of this play | 12 |
| quotation not found; headword not found near cited line | 12 |
| headword off by 1 | 11 |
| quotation off by 1 | 9 |
| prose row break | 8 |
| headword off by 3 | 3 |
| quotation elsewhere in scene | 2 |
| quotation off by 2 | 2 |
| quotation in another scene | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

| Scene | Cited lines | Offset | Citations |
|---|---|---|---|
| 1.1 | 92-93 | -1 | 4 |

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 5.4 | V, 4, 202 | Abandon | not a citation of this play |  | at your -- ed cave, |  |
| 2.2.117 | Shr. Ind. 2, 117 | Abandon | quotation not found; headword not found near cited line |  | abandoned from your bed, | (no such line) |
| 1.2 | As I, 2, 246 | Adopt | not a citation of this play |  | to be adopted heir to Frederick, |  |
| 4.1.220 | IV, 1, 220 | Aliena | headword off by 1 | 4.1.221 |  | let him be judge how deep i am in love ill |
| 3.2.100 | Shr. Ind. 2, 100. | Amen | headword not found near cited line |  |  | but the fair of rosalind |
| 2.1.40 | Shr. Ind. 1, 40. | Attendant | quotation in another scene | 2.2.5 | (the ladies, her attendants of her chamber). | in piteous chase and thus the hairy fool |
| 2.1.39 | Shr. Ind. 1, 39. | Banquet | headword not found near cited line |  |  | coursed one another down his innocent nose |
| 5.2.138 | Shr. Ind. 2, 138. | Bar | quotation not found; headword not found near cited line |  | merriment, which bars a thousand harms, | (no such line) |
| 4.1.215 | As IV, 1, 215 | Bastard | headword off by 1 | 4.1.216 |  | pour affection in it runs out |
| 4.3.103 | As IV, 3, 103 | Befall. | headword not found near cited line |  |  | lo what befel he threw his eye aside |
| 4.3.103 | As IV, 3, 103 | Befall. | headword not found near cited line |  |  | lo what befel he threw his eye aside |
| 3.3.105 | As III, 3, 105 | Begone | headword off by 3 | 3.3.102 |  | knave of them all shall flout me out of my calling |
| 3.1.95 | Shr. Ind. 1, 95. | Behaviour | headword not found near cited line |  |  | (no such line) |
| 1.2.36 | As I, 2, 36 | Benefit | headword off by 1 | 1.2.37 |  | henceforth be bestowed equally |
| 3.2.186 | As III, 2, 186 | Berhyme | prose row break | 3.2.187 |  | what i found on a palmtree i was never so |
| 1.2.20 | Shr. Ind. 2, 20. | Birth | headword not found near cited line |  |  | dies thou shalt be his heir for what he hath |
| 4.1.213 | As IV, 1, 213 | Bottomless | quotation off by 1 | 4.1.214-215 | or rather b., that as fast as you pour affection in, it runs out, | of portugal |
| 3.2.273 | As III, 2, 273 | Buy | headword not found near cited line |  |  | god be wi you lets meet as little as |
| 4.1.31 | IV, 1, 31 | Buy | headword not found near cited line |  |  | nay then god be wi you an you talk |
| 5.3.41 | V, 3, 41 | Buy | headword not found near cited line |  |  | time lost to hear such a foolish song god be |
| 3.3.108 | As III, 3, 108 | Calling | headword off by 3 | 3.3.105 |  | (no such line) |
| 2.7.53 | As II, 7, 53 | Cannon | headword not found near cited line |  |  | he that a fool doth very wisely hit |
| 3.52.9 | 52, 9 | Chest | not a citation of this play |  |  |  |
| 3.65.10 | 65, 10 | Chest | not a citation of this play |  |  |  |
| 3.0 | III Prol. 36 | Clap | not a citation of this play |  |  |  |
| 4.1.216 | As IV, 1, 216 | Conceive | headword off by 1 | 4.1.217 |  | no that same wicked bastard of venus |
| 1.2.179 | As I, 2, 179 | Conceive | quotation elsewhere in scene | 1.2.278-279 | what he is, more suits you to conceive | the wrestler |
| 3.1.107 | Shr. Ind. 1, 107. | Conduct | headword not found near cited line |  |  | (no such line) |
| 3.2.357 | As III, 2, 357 | Coney | headword not found near cited line |  |  | as the cony that you see dwell where |
| 2.1.64 | As. II, 1, 64 | Contemplation | not a citation of this play |  |  |  |
| 2.7.31 | As II, 7, 31 | Contemplative | headword not found near cited line |  |  | that fools should be so deepcontemplative |
| 5.14.12 | 14, 12 | Convert | not a citation of this play |  | if from thyself to store thou wouldst convert |  |
| 4.1.209 | As IV, 1, 209 | Deep | headword off by 1 | 4.1.210 |  | o coz coz coz my pretty little coz that |
| 2.2.129 | Shr. Ind. 2, 129. | Despite | headword not found near cited line |  |  | (no such line) |
| 1.2.29 | As I, 2, 29 | Earnest | quotation off by 1 | 1.2.30 | in good e.: | marry i prithee do to make sport |
| 3.45.5 | 45, 5 | Element | not a citation of this play |  |  |  |
| 1.2.35 | As I, 2, 35 | Equally | headword off by 1 | 1.2.36 |  | fortune from her wheel that her gifts may |
| 3.2.8 | As III, 2, 8 | Everywhere | headword not found near cited line |  |  | shall see thy virtue witnessed every where |
| 5.1.29 | As V, 1, 29 | Excellent | prose row break | 5.1.30 |  | so so is good very good very |
| 3.3.107 | III, 3, 107 | Fantastical | quotation off by 2 | 3.3.104-105 | a fantastical knave, | (no such line) |
| 4.3.25 | As IV, 3, 25 | Freestone-coloured | headword not found near cited line |  |  | a freestonecolored hand i verily did think |
| 1.28.9 | I, 28 | Goth | not a citation of this play |  |  |  |
| 3.2.127 | Shr. Ind. 2, 127. | Hardly | headword not found near cited line |  |  | be half ripe and thats the right virtue of the |
| 1.1.178 | I, 1, 178 | Hardly | headword not found near cited line |  |  | be so long this wrestler shall clear all nothing |
| 2.1.213 | As II, 1, 213 | High | quotation not found; headword not found near cited line |  | if thou proceed as high as word, | (no such line) |
| 2.2.144 | Shr. Ind. 2, 144. | History | quotation not found; headword not found near cited line |  | it is a kind of history | (no such line) |
| 1.1.93 | As I, 1, 93 | Holla | headword off by 1 | 1.1.92 |  | calls your worship |
| 4.3.27 | IV, 3, 27 | Housewife | headword not found near cited line |  |  | she has a huswifes hand but thats no matter |
| 3.5.53 | As III, 5, 53 | Ill-favoured | quotation not found; headword not found near cited line |  | ill-favoured children, | that makes the world full of illfavored children |
| 1.1.81 | As I, 1, 81 | In | quotation off by 1 | 1.1.80 | get you in, | be troubled with you you shall have some part |
| 4.3.90 | As IV, 3, 90 | Inquire | headword not found near cited line |  |  | the owner of the house i did enquire for |
| 1.3.59 | As I, 3, 59 | Joul | quotation not found; headword not found near cited line |  | they may joul horns together, | tell me whereon the likelihood depends |
| 3.2.99 | As III, 2, 99 | Keep | headword not found near cited line |  |  | let no fair be kept in mind |
| 5.3.38 | As V, 3, 38 | Keep | headword not found near cited line |  |  | you are deceived sir we kept |
| 3.2.314 | As III, 2, 314 | Lacquey | headword not found near cited line |  |  | like a saucy lackey and under that habit play the |
| 1.2.44 | As I, 2, 44 | Lineament | headword off by 1 | 1.2.45 |  | office to natures fortune reigns in gifts of the |
| 1.2.128 | Shr. Ind. 2, 128. | Loath | headword not found near cited line |  |  | tale |
| 3.2.31 | Shr. Ind. 2, 31. | Lunacy | headword not found near cited line |  |  | nature nor art may complain of good breeding or |
| 3.5.82 | As III, 5, 82 | Might | quotation off by 1 | 3.5.81 | now I find thy saw of might | who ever loved that loved not at first sight |
| 3.123.2 | 123, 2 | Might | not a citation of this play |  | thy pyramids built up with newer might |  |
| 1.2.37 | I, 2, 37 | Mightily | quotation elsewhere in scene | 1.2.218-219 | that have so mightily persuaded him from the first, | i would we could do so for her benefits |
| 3.3.74 | As III, 3, 74 | Mr. | headword not found near cited line |  |  | good even good master whatye |
| 1.2.30 | As I, 2, 30 | Neither | headword off by 1 | 1.2.31 |  | withal but love no man in good earnest nor no |
| 1.1.93 | As I, 1, 93 | Neither | quotation off by 1 | 1.1.91-92 | I will physic your rankness, and yet give no thousand crowns neither | calls your worship |
| 5.4.182 | As V, 4, 182 | New | quotation not found; headword not found near cited line |  | this new fallen dignity, | meantime forget this newfalln dignity |
| 2.7.2 | As II, 7, 2 | Nowhere | headword not found near cited line |  |  | for i can no where find him like a man |
| 3.2.139 | As III, 2, 139 | Outstretch | headword not found near cited line |  |  | that the stretching of a span |
| 3.2.164 | As III, 2, 164 | Parishioners | prose row break | 3.2.165 |  | homily of love have you wearied your |
| 5.1.67 | Shr. Ind. 1, 67. | Pastime | headword not found near cited line |  |  | come away away |
| 1.1.68 | I, 1, 68 | Pastime | headword not found near cited line |  |  | let me go i say |
| 1.1.73 | As I, 1, 73 | Peasant | headword off by 1 | 1.1.72 |  | gentlemanlike qualities the spirit of my father |
| 2.1.63 | Shr. Ind. 1, 63. | Persuade | headword not found near cited line |  |  | in their assigned and native dwellingplace |
| 3.2.82 | 2, 82 | Petitionary | headword not found near cited line |  |  | that is another simple sin in you |
| 3.2.354 | III, 2, 354 | Petticoat | prose row break | 3.2.355 |  | in the skirts of the forest like fringe upon a |
| 1.1.92 | As I, 1, 92 | Physic | quotation off by 1 | 1.1.91 | I will physic your rankness, | no thousand crowns neither holla dennis |
| 1.1.17 | As I, 1, 17 | Plentifully | prose row break | 1.1.18 |  | him as i besides this nothing that he so |
| 1.1.36 | Shr. Ind. 1, 36. | Practise | quotation not found; headword not found near cited line |  | I will practise on this drunken man, | which god made a poor unworthy brother of |
| 1.1.74 | As I, 1, 74 | Quality | quotation off by 1 | 1.1.72-73 | hiding from me all gentleman-like qualityes, | grows strong in me and i will no longer endure |
| 1.1.92 | As I, 1, 92 | Rankness | quotation off by 1 | 1.1.91 | I will physic your rankness | no thousand crowns neither holla dennis |
| 5.4.82 | As V, 4, 82 | Reproof | prose row break | 5.4.83 |  | answer i spake not true this is called the |
| 3.5.82 | III, 5, 82 | Saw | quotation off by 1 | 3.5.81 | now I find thy saw of might, | who ever loved that loved not at first sight |
| 4.1.48 | As IV, 1, 48 | Shoulder-clapper | headword not found near cited line |  |  | him that cupid hath clapped him o the shoulder |
| 3.2.393 | As III, 2, 393 | Sink | headword not found near cited line |  |  | blue eye and sunken which you have not an |
| 3.2.393 | As III, 2, 393 | Sink | headword not found near cited line |  |  | blue eye and sunken which you have not an |
| 3.1.3 | Shr. Ind. 1, 3 | Sly | headword not found near cited line |  |  | i should not seek an absent argument |
| 2.2.50 | Shr. Ind. 2, 50. | Stag | headword not found near cited line |  |  | (no such line) |
| 2.5.18 | As II, 5, 18 | Staple | quotation not found; headword not found near cited line |  | with massy staples and corresponsive and fulfilling bolts, | desire you to sing come more another stanzo |
| 1.2.162 | As I, 2, 162 | Successfully | prose row break | 1.2.163 |  | alas he is too young yet he looks |
| 4.39.12 | 39, 12 | Sweetly | not a citation of this play |  | which time and thoughts so sweetly doth deceive, |  |
| 5.1.16 | Shr. Ind. 1, 16. | Tender | quotation not found; headword not found near cited line |  | tender well my hounds, | god ye good even william |
| 2.2.59 | Shr. Ind. 2, 59. | Thorny | quotation not found; headword not found near cited line |  | a thorny wood, | (no such line) |
| 1.2.48 | As I, 2, 48 | Though | headword not found near cited line |  |  | that nature hath given us wit to flout at |
| 2.1.24 | Shr. Ind. 1, 24. | To-day | headword not found near cited line |  |  | should in their own confines with forked heads |
| 4.1.76 | Shr. Ind. 1, 76 | Travail | headword not found near cited line |  |  | when they are out they will spit and for lovers |
| 4.2.73 | IV, 2, 73 | Travail | quotation not found; headword not found near cited line |  | (travailing some journey). | (no such line) |
| 4.5.51 | IV, 5, 51 | Travail | not a citation of this play |  |  |  |
| 3.2.393 | As III, 2, 393 | Unquestionable | prose row break | 3.2.394 |  | blue eye and sunken which you have not an |
| 5.3.37 | As V, 3, 37 | Untimeable | headword not found near cited line |  |  | was very untuneable |
| 3.5.87 | III, 5, 87 | Wherever | headword off by 1 | 3.5.86 |  | if you do sorrow at my grief in love |
| 1.1.22 | I, 1 | Willing | headword off by 3 | 1.1.25 |  | gentility with my education this is it adam |
| 3.3.104 | As III, 3, 104 | Wind | quotation off by 2 | 3.3.102 | wind away, be gone, I say, | tis no matter neer a fantastical |
