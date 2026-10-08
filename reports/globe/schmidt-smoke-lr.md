# Schmidt smoke test: King Lear

Sources: shakespeare.lr.globe.xml sha256 6c3286b393ca0c93; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of King Lear in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 2163/2286 (94.6%) pass.
- **With a quotation:** 1305/1344 (97.1%) have it on the cited line.
- **Headword only:** 858/942 (91.1%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 1031 |
| headword on cited line | 883 |
| quotation on cited line, with differences | 249 |
| headword not found near cited line | 50 |
| not a citation of this play | 30 |
| prose row break | 14 |
| quotation not found; headword not found near cited line | 9 |
| quotation off by 1 | 9 |
| headword off by 1 | 6 |
| quotation elsewhere in scene | 4 |
| quotation not found; headword off by 1 | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

| Scene | Cited lines | Offset | Citations |
|---|---|---|---|
| 5.3 | 111-114 | -1 | 4 |

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 1.2.83 | Lr. I, 2, 83 | Abominable | prose row break | 1.2.84 |  | sirrah seek him ill apprehend him |
| 3.6.8 | Lr. III, 6, 8 | Acheron | headword not found near cited line |  |  | is an angler in the lake of darkness pray |
| 4.4 | Lr. IV, 4, 7 | Acre | not a citation of this play |  | searchevery acre in the high-grown field, |  |
| 3.2.112 | Shr. Ind. 2, 112. | Al'ce | not a citation of this play |  | Alice: |  |
| 5.3.83 | Lr. V, 3, 83 | Arrest | headword off by 1 | 5.3.82 |  | on capital treason and in thine attaint |
| 1.2.47 | Lr. I, 2, 47 | Assáy | headword not found near cited line |  |  | he wrote this but as an essay or taste of my virtue |
| 4.3.26 | Lr. IV, 3, 26 | Behoove | quotation not found; headword not found near cited line |  | to become | if all could so become it made she no verbal question |
| 2.0 | II Prol. 10 | Benison | not a citation of this play |  |  |  |
| 1.91.8 | 91, 8 | Better | not a citation of this play |  | all these I better in one general best, |  |
| 2.4.226 | Lr. II, 4, 226 | Bile | headword not found near cited line |  |  | which i must needs call mine thou art a boil |
| 2.132.3 | 132, 3 | Black | not a citation of this play |  | have put on black |  |
| 5.58.14 | 58, 14 | Blame | not a citation of this play |  |  |  |
| 5.70.1 | 70, 1 | Blame | not a citation of this play |  |  |  |
| 5.103.5 | 103, 5 | Blame | not a citation of this play |  |  |  |
| 2.4.170 | Lr. II, 4, 170 | Blister | headword not found near cited line |  |  | to fall and blast her pride |
| 3.86.11 | 86, 11 | Boast | not a citation of this play |  |  |  |
| 3.91.12 | 91, 12 | Boast | not a citation of this play |  |  |  |
| 5.154.2 | 154, 2 | Brand | not a citation of this play |  | his heart-inflaming brand |  |
| 4.2.85 | Lr. IV, 2, 85 | Building | headword off by 1 | 4.2.86 |  | but being widow and my gloucester with her |
| 4.4.4 | Lr. IV, 4, 4 | Burr-dock | headword not found near cited line |  |  | with burdocks hemlock nettles cuckoo flowers |
| 1.2.125 | Lr. I, 2, 125 | Carefully | prose row break | 1.2.126 |  | edmund it shall lose thee nothing do it |
| 1.4.175 | Lr. I, 4, 175 | Cleave | quotation not found; headword not found near cited line |  | clove: | the egg when thou clovest thy crown i the |
| 4.1.4 | 1, 4 | Cliff | headword not found near cited line |  |  | stands still in esperance lives not in fear |
| 4.1.4 | 1, 4 | Cliff | headword not found near cited line |  |  | stands still in esperance lives not in fear |
| 3.0 | III Prol. 15 | Dearn | not a citation of this play |  |  |  |
| 5.80.14 | 80, 14 | Decay | not a citation of this play |  | my love was my decay |  |
| 1.4.65 | Lr. I, 4, 65 | Dependant | prose row break | 1.4.66 |  | kindness appears as well in the general |
| 1.4.2 | Lr. I, 4, 2 | Diffuse | headword not found near cited line |  |  | that can my speech defuse my good intent |
| 1.1.177 | Lr. I, 1, 177 | Disaster | headword not found near cited line |  |  | to shield thee from diseases of the world |
| 1.2.161 | Lr. I, 2, 161 | Dissipation | prose row break | 1.2.162 | dissipation of cohorts, | needless diffidences banishment of friends |
| 1.2.158 | Lr. I, 2, 158 | Dissolution | prose row break | 1.2.159 | dissolutions of ancient amities, | the child and the parent death dearth |
| 3.4.59 | Lr. III, 4, 59 | Do de | headword not found near cited line |  |  | bless thy five wits toms acold o do de |
| 3.6.77 | III, 6, 77 | Do de | headword not found near cited line |  |  | do de de de sessa come march to wakes |
| 2.4.54 | Lr. II, 4, 54 | Dollar | headword not found near cited line |  |  | but for all this thou shalt have as many dolours |
| 4.1.94 | Shr. Ind. 1, 94. | Doubtful | not a citation of this play |  | I am doubtful of your modesties, |  |
| 2.1.9 | Lr. II, 1, 9 | Ear-bussing | quotation not found; headword not found near cited line |  | ear-bussing arguments, | for they are yet but earkissing arguments |
| 1.2.27 | Lr. I, 2, 27 | Earnestly | quotation off by 1 | 1.2.28 | why so earnestly seek you to put up that letter? | so please your lordship none |
| 2.1.56 | Lr. II, 1, 56 | Encounter | headword not found near cited line |  |  | bold in the quarrels right roused to the en counter |
| 1.1.301 | Lr. I, 1, 301 | Engraft | headword not found near cited line |  |  | longengraffed condition but therewithal the unruly |
| 4.6.71 | IV, 6, 71 | Enrage | quotation not found; headword not found near cited line |  | (thereat). | horns whelked and waved like the enridged sea |
| 4.105.8 | 105, 8 | Express | not a citation of this play |  |  |  |
| 4.106.7 | 106, 7 | Express | not a citation of this play |  |  |  |
| 4.108.4 | 108, 4 | Express | not a citation of this play |  |  |  |
| 4.140.3 | 140, 3 | Express | not a citation of this play |  |  |  |
| 1.1.76 | Lr. I, 1, 76 | Felicitate | quotation off by 1 | 1.1.77-78 | I am alone felicitate in your dear highness' love, | which the most precious square of sense possesses |
| 2.115.4 | 115, 4 | Flame | not a citation of this play |  |  |  |
| 4.6.243 | Lr. IV, 6, 243 | Folk | headword not found near cited line |  |  | poor volk pass an chud ha bin zwaggered out |
| 4.1.58 | Lr. IV, 1, 58 | Footpath | quotation off by 1 | 4.1.57 | (the footpath way). | both stile and gate horseway and |
| 4.6.245 | IV, 6, 245 | Fortnight | headword not found near cited line |  |  | vortnight nay come not near th old man |
| 2.2.107 | Shr. Ind. 2, 107. | Good-man | not a citation of this play |  | my men should call me lord: I am your good-man |  |
| 2.4.90 | II, 4, 90 | Hard | headword not found near cited line |  |  | they have travelled all the night mere fetches |
| 3.6.82 | Lr. III, 6, 82 | Hardness | quotation not found; headword not found near cited line |  | that makes this hardness | in nature that makes these hard hearts |
| 4.4.4 | Lr. IV, 4, 4 | Hardock | headword not found near cited line |  |  | with burdocks hemlock nettles cuckoo flowers |
| 5.3.135 | Lr. V, 3, 135 | Illustrious | headword not found near cited line |  |  | conspirant gainst this highillustrious prince |
| 5.3.51 | Lr. V, 3, 51 | Impréss | headword off by 1 | 5.3.50 |  | which do command them with him i sent the queen |
| 5.3.51 | Lr. V, 3, 51 | Impréss | headword off by 1 | 5.3.50 |  | which do command them with him i sent the queen |
| 3.4.140 | Lr. III, 4, 140 | Imprison | prose row break | 3.4.141 |  | tithing to tithing and stock punished and |
| 4.7.32 | Lr. IV, 7, 32 | Jar | headword not found near cited line |  |  | to be opposed against the warring winds |
| 3.6.54 | Lr. III, 6, 54 | Joint-stool | prose row break | 3.6.55 |  | cry you mercy i took you for a |
| 2.4.255 | II, 4, 255 | Keep | quotation not found; headword not found near cited line |  | to keep her still, and men in awe, | but kept a reservation to be followed |
| 2.1.54 | Lr. II, 1, 54 | Latch | headword not found near cited line |  |  | my unprovided body lanced mine arm |
| 1.4.154 | Lr. I, 4, 154 | Least | headword not found near cited line |  |  | that lord that counselled thee |
| 1.1.306 | Lr. I, 1, 306 | Leave-taking | prose row break | 1.1.307 |  | there is further compliment of |
| 1.102.2 | 102, 2 | Less | not a citation of this play |  | I love not less |  |
| 5.3.112 | Lr. V, 3, 112 | List | quotation off by 1 | 5.3.110-111 | if any man of quality or degree within the lists of the army will maintain, | edmund supposed earl of gloucester that he is |
| 5.3.114 | Lr. V, 3, 114 | Manifold | quotation off by 1 | 5.3.113 | a manifold traitor, | sound of the trumpet he is bold in his defence |
| 4.7.48 | Lr. IV, 7, 48 | Melt | headword not found near cited line |  |  | do scald like molten lead sir do you know me |
| 1.2.159 | Lr. I, 2, 159 | Menaces | prose row break | 1.2.160 |  | dissolutions of ancient amities divisions in state |
| 1.22.90 | I, 22 | Mere | not a citation of this play |  |  |  |
| 3.3.6 | Lr. III, 3, 6 | Neither | headword off by 1 | 3.3.5 |  | entreat for him nor any way sustain him |
| 1.2.38 | Lr. I, 2, 38 | O'erread | prose row break | 1.2.39 |  | letter from my brother that i have not all |
| 3.2.92 | III, 2, 92 | O'errule | quotation not found; headword not found near cited line |  | s. | come to great confusion |
| 5.1.39 | Lr. V, 1, 39 | O'ertake | headword not found near cited line |  |  | hear me one word ill overtake you speak |
| 2.2.177 | Lr. II, 2, 177 | O'erwatched | headword not found near cited line |  |  | losses their remedies all weary and oer watched |
| 3.4.78 | Lr. III, 4, 78 | Pelicock | headword off by 1 | 3.4.77 |  | pillicock sat on pillicockhill |
| 3.2.57 | Lr. III, 2, 57 | Pen | headword not found near cited line |  |  | hast practised on mans life close pentup guilts |
| 1.1.183 | Lr. I, 1, 183 | Plaited | quotation elsewhere in scene | 1.1.283 | time shall unfold what plaited cunning hides, | fare thee well king sith thus thou wilt appear |
| 5.3.94 | Lr. V, 3, 94 | Pledge | quotation off by 1 | 5.3.93 | there is my pledge | ere i taste bread thou art in nothing less |
| 4.0 | IV Prol. 44 | Pregnant | not a citation of this play |  |  |  |
| 1.2.24 | Lr. I, 2, 24 | Prescribe | headword not found near cited line |  |  | and the king gone tonight subscribed his power |
| 2.1.122 | Lr. II, 1, 122 | Prize | headword not found near cited line |  |  | occasions noble gloucester of some poise |
| 1.1.5 | Lr. I, 1, 5 | Quality | quotation off by 1 | 1.1.6 | qualityes are so weighed, | which of the dukes he values most for equalities |
| 5.3.111 | Lr. V, 3, 111 | Quality | quotation off by 1 | 5.3.110 | any man of quality or degree, | within the lists of the army will maintain upon |
| 3.4.55 | Lr. III, 4, 55 | Ratsbane | prose row break | 3.4.56 |  | under his pillow and halters in his pew set |
| 1.1.163 | Lr. I, 1, 163 | Recreant | quotation elsewhere in scene | 1.1.169 | hear me, recreant | thou swearst thy gods in vain o vassal miscreant dear sir forbear |
| 1.1.151 | Lr. I, 1, 151 | Reserve | quotation not found; headword not found near cited line |  | reserve thy state, | when majesty stoops to folly reverse thy doom |
| 1.1.242 | Lr. I, 1, 242 | Respect | quotation elsewhere in scene | 1.1.251 | respects of fortune are his love, | when it is mingled with regards that stand |
| 1.3.91 | I, 3, 91 | Royalty | headword not found near cited line |  |  | (no such line) |
| 2.4.304 | Lr. II, 4, 304 | Rustle | headword not found near cited line |  |  | do sorely ruffle for many miles about |
| 5.3.171 | V, 3, 171 | Scourge | headword not found near cited line |  |  | make instruments to plague us |
| 4.2.50 | Lr. IV, 2, 50 | Sea-monster | headword not found near cited line |  |  | like monsters of the deep milklivered man |
| 4.0 | IV Prol. 40 | Slaughter | not a citation of this play |  |  |  |
| 4.3.2 | IV, 3, 2 | Slaughter | headword not found near cited line |  |  | gone back know you the reason |
| 4.6.190 | Lr. IV, 6, 190 | Son-in-law | headword not found near cited line |  |  | and when i have stoln upon these sonsinlaw |
| 3.4.60 | Lr. III, 4, 60 | Star-blasting | prose row break | 3.4.61 |  | do de do de bless thee from whirlwinds |
| 3.68.13 | 68, 13 | Store | not a citation of this play |  | him as for a map doth nature s., to show false art what beauty was of yore, |  |
| 2.2.19 | Lr. II, 2, 19 | Superfinical | quotation not found; headword not found near cited line |  | superfinical rogue, | whoreson glassgazing superserviceable finical |
| 5.3.113 | Lr. V, 3, 113 | Suppose | quotation off by 1 | 5.3.112 | Edmund, supposed Earl of Gloster, | a manifold traitor let him appear by the third |
| 2.150.2 | 150, 2 | Sway | not a citation of this play |  | with insufficiency my heart to sway |  |
| 4.6.6 | Lr. IV, 6 | Sweeten | quotation elsewhere in scene | 4.6.132-133 | an ounce of civet, to sweeten my imagination, | by your eyes anguish so may it be indeed |
| 4.6.6 | Lr. IV, 6 | Sweeten | headword not found near cited line |  |  | by your eyes anguish so may it be indeed |
| 4.1.192 | IV, 1, 192 | Taste | headword not found near cited line |  |  | (no such line) |
| 4.26.11 | 26, 11 | Tattered | not a citation of this play |  | puts apparel on my tattered loving, |  |
| 2.2.150 | Lr. II, 2, 150 | Temnest | headword not found near cited line |  |  | is such as basest and contemnedst wretches |
| 2.4.103 | Lr. II, 4, 103 | Tend | headword not found near cited line |  |  | would with his daughter speak commands her service |
| 2.4.174 | Lr. II, 4, 174 | Tender-hested | headword not found near cited line |  |  | thy tenderdefted nature shall not give |
| 1.4.322 | Lr. I, 4, 322 | Tent | headword not found near cited line |  |  | the untented woundings of a fathers curse |
| 2.4.259 | II, 4, 259 | That | headword not found near cited line |  |  | those wicked creatures yet do look wellfavoured |
| 1.121.9 | 121, 9 | That | not a citation of this play |  | I am that I am, |  |
| 1.4.242 | Lr. I, 4, 242 | Transport | headword not found near cited line |  |  | these dispositions that of late transform you |
| 1.4.234 | Lr. I, 4, 234 | Trow | headword not found near cited line |  |  | for you know nuncle |
| 2.3.21 | Lr. II, 3, 21 | Turlygod | quotation not found; headword off by 1 | 2.3.20 | turlupin: | thats something yet edgar i nothing am |
| 3.4.111 | Lr. III, 4, 111 | Unaccommodated | prose row break | 3.4.112-113 | unaccommodated man is no more but such a poor, bare, forked animal, | sophisticated thou art the thing itself |
| 2.2.133 | Lr. II, 2, 133 | Unreverend | headword not found near cited line |  |  | you stubborn ancient knave you reverend braggart |
| 2.13.13 | 13, 13 | Unthrift | not a citation of this play |  |  |  |
| 2.4.171 | Lr. II, 4, 171 | Upon | headword not found near cited line |  |  | o the blest gods so will you wish on me |
| 2.4.75 | Lr. II, 4, 75 | Upward | headword not found near cited line |  |  | great one that goes up the hill let him draw thee |
| 2.2.129 | Lr. II, 2, 129 | Vail | headword not found near cited line |  |  | for him attempting who was selfsubdued |
| 4.0 | IV Prol. 29 | Vail | not a citation of this play |  |  |  |
| 4.1.65 | Lr. IV, 1, 65 | Waiting-women | prose row break | 4.1.66 |  | since possesses chambermaids and |
| 4.6.10 | Lr. IV, 6, 10 | Well-spoken | headword not found near cited line |  |  | but in my garments methinks youre better spoken |
| 3.6.17 | Lr. III, 6, 17 | Whizzing | headword not found near cited line |  |  | come hissing in upon em |
| 3.4.125 | Lr. III, 4, 125 | Wold | headword not found near cited line |  |  | s withold footed thrice the old |
