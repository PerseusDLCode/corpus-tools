# Schmidt smoke test: King Henry IV, Part I

Sources: shakespeare.1h4.globe.xml sha256 7b5a7fc8a4aff95b; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of King Henry IV, Part I in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1906/2009 (94.9%) pass.
- **With a quotation:** 1141/1166 (97.9%) have it on the cited line.
- **Headword only:** 765/843 (90.7%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 933 |
| headword on cited line | 792 |
| quotation on cited line, with differences | 181 |
| headword not found near cited line | 49 |
| prose row break | 24 |
| quotation not found; headword not found near cited line | 11 |
| not a citation of this play | 11 |
| quotation off by 1 | 4 |
| headword off by 1 | 2 |
| quotation in another scene | 1 |
| quotation not found; headword off by 1 | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

| Scene | Cited lines | Offset | Citations |
|---|---|---|---|
| 3.1 | 52-52 | +1 | 3 |

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 2.4.370 | H4A II, 4, 370 | Amaimon | headword not found near cited line |  |  | he of wales that gave amamon the bastinado |
| 1.2.187 | H4A I, 2, 187 | Angel | headword not found near cited line |  |  | how shall we part with them in |
| 2.2.57 | II, 2, 57 | Auditor | headword not found near cited line |  |  | hill tis going to the kings exchequer |
| 2.2.88 | H4A II, 2, 88 | Bacon-fed: | prose row break | 2.2.89 | bacon-fed knaves, | villains throats ah whoreson caterpillars |
| 4.1.99 | H4A IV, 1, 99 | Bate | quotation off by 1 | 4.1.98 | like estridges that with the wind bated, | baited like eagles having lately bathed |
| 3.3.112 | H4A III, 3, 112 | Behind. | prose row break | 3.3.113 |  | the other night i fell asleep here |
| 4.1.114 | H4A IV, 1, 114 | Bellona | headword not found near cited line |  |  | and to the fireeyed maid of smoky war |
| 5.1.123 | H4A V, 1, 123 | Bestride | headword off by 1 | 5.1.122 |  | nothing but a colossus can do thee |
| 2.4.388 | H4A II, 4, 388 | Bodge | headword not found near cited line |  |  | will not budge a foot |
| 5.1.2 | H4A V, 1, 2 | Bosky | quotation not found; headword not found near cited line |  | you bosky hill, | above yon busky hill the day looks pale |
| 2.4.287 | H4A II, 4, 287 | Bull-calf | prose row break | 2.4.288 |  | and still run and roared as ever i heard |
| 3.2.19 | Shr. Ind. 2, 19. | Burton-heath | headword not found near cited line |  |  | quit all offences with as clear excuse |
| 5.3.7 | H4A V, 3, 7 | By | headword not found near cited line |  |  | the lord of stafford dear today hath bought |
| 3.3.84 | H4A III, 3, 84 | By-drinkings | prose row break | 3.3.85 |  | besides sir john for your diet and |
| 3.1.131 | H4A III, 1, 131 | Candlestick | headword not found near cited line |  |  | i had rather hear a brazen canstick turned |
| 3.2.63 | H4A III, 2, 63 | Carp | quotation not found; headword not found near cited line |  | carping fools, | mingled his royalty with capering fools |
| 2.1.27 | H4A II, 1, 27 | Charing-cross | prose row break | 2.1.28 |  | razes of ginger to be delivered as far as |
| 3.1.29 | H4A III, 1, 29 | Cholic | headword not found near cited line |  |  | is with a kind of colic pinched and vexed |
| 2.2.26 | Shr. Ind. 2, 26. | Christendom | quotation not found; headword not found near cited line |  | the lyingest knave in C., | chewed with a tooth eight yards of uneven |
| 2.188.26 | II, 188 | Christendom | not a citation of this play |  |  |  |
| 3.2.51 | H4A III, 2, 51 | Clap | quotation not found; headword not found near cited line |  | a' would have claped i' the clout at twelve score, | and dressed myself in such humility |
| 4.2.118 | IV, 2, 118 | Commence | headword not found near cited line |  |  | (no such line) |
| 3.35.6 | 35, 6 | Compare | not a citation of this play |  |  |  |
| 3.130.14 | 130, 14 | Compare | not a citation of this play |  |  |  |
| 3.26.7 | 26, 7 | Conceit | not a citation of this play |  |  |  |
| 3.108.13 | 108, 13 | Conceit | not a citation of this play |  | finding the first conceit of love there bred, where time and outward form would show it dead, |  |
| 5.2.134 | Shr. Ind. 2, 134. | Congeal | quotation not found; headword not found near cited line |  | sadness hath congealed your blood, | (no such line) |
| 2.4.464 | H4A II, 4, 464 | Corpulent | prose row break | 2.4.465 |  | a goodly portly man i faith and a |
| 3.0 | III Prol. 6 | Couch | not a citation of this play |  |  |  |
| 3.2.127 | H4A III, 2, 127 | Courtesy | headword not found near cited line |  |  | to dog his heels and curtsy at his frowns |
| 2.4.585 | H4A II, 4, 585 | D | headword not found near cited line |  |  | item a capon 2s 2d |
| 3.1.52 | H4A III, 1, 52 | Deep | quotation off by 1 | 3.1.53 | I can call spirits from the vasty deep | peace cousin percy you will make him mad |
| 5.1.141 | H4A V, 1, 141 | Detraction | prose row break | 5.1.142 | detraction will not suffer it, | will it not live with the living no why |
| 1.3.135 | H4A I, 3, 135 | Downfallen | headword not found near cited line |  |  | but i will lift the downtrod mortimer |
| 2.4.112 | H4A II, 4, 112 | Downstairs | prose row break | 2.4.113 |  | a woman his industry is upstairs and |
| 3.2.146 | H4A III, 2, 146 | Exchange | prose row break | 3.2.145 |  | his glorious deeds for my indignities |
| 4.1.74 | H4A IV, 1, 74 | Face | quotation in another scene | 5.1.74 | to face the garment of rebellion with some fine colour, | that shows the ignorant a kind of fear |
| 2.4.364 | H4A II, 4, 364 | Forefinger | headword not found near cited line |  |  | waist i could have crept into any aldermans |
| 5.146.4 | 146, 4 | Gay | not a citation of this play |  | so costly gay |  |
| 2.1.84 | H4A II, 1, 84 | Great-oneyers | headword not found near cited line |  |  | nobility and tranquillity burgomasters and great |
| 2.4.93 | H4A II, 4, 93 | Half | headword not found near cited line |  |  | halfadozen more are at the door shall i let |
| 3.1.221 | H4A III, 1, 221 | Harnessed | headword not found near cited line |  |  | the hour before the heavenlyharnessed team |
| 1.2.181 | H4A I, 2, 181 | Harvey | headword not found near cited line |  |  | i cannot manage alone falstaff bardolph |
| 2.4.268 | H4A II, 4, 268 | Horseback-breaker | prose row break | 2.4.269 |  | this sanguine coward this bedpresser this |
| 3.2.156 | H4A III, 2, 156 | Intemperature | headword not found near cited line |  |  | the longgrown wounds of my intemperance |
| 2.4.418 | H4A II, 4, 418 | Joint-stool | headword not found near cited line |  |  | thy state is taken for a joinedstool |
| 2.4.251 | H4A II, 4, 251 | Knotty-pated | prose row break | 2.4.252 |  | palpable why thou claybrained guts thou |
| 3.1.158 | H4A III, 1, 158 | Lacquey | headword not found near cited line |  |  | that were his lackeys i cried hum and well go to |
| 1.2.9 | H4A I, 2, 9 | Leaping-house | prose row break | 1.2.10 |  | tongues of bawds and dials the signs of |
| 2.4.7 | H4A II, 4, 7 | Leashed in | quotation not found; headword not found near cited line |  | leashed in like hounds, should famine, sword and fire crouch for employment, | i am sworn brother to a leash of drawers and |
| 2.4.7 | H4A II, 4, 7 | Leashed in | headword not found near cited line |  |  | i am sworn brother to a leash of drawers and |
| 4.2.19 | H4A IV, 2, 19 | Lief | headword not found near cited line |  |  | commodity of warm slaves as had as lieve hear |
| 2.2.31 | H4A II, 2, 31 | Light | headword not found near cited line |  |  | a plague upon you all give me my horse you |
| 1.2.178 | H4A I, 2, 178 | Martlemas | headword not found near cited line |  |  | allhallown summer |
| 2.4.60 | H4A II, 4, 60 | Meditate | quotation not found; headword not found near cited line |  | meditateing that shall dye your white rose in a bloody red, | let me see about michaelmas next i |
| 2.4.383 | H4A II, 4, 383 | Metal | quotation not found; headword not found near cited line |  | good metal | well that rascal hath good mettle in |
| 2.4.148 | H4A II, 4, 148 | Mutter | quotation off by 1 | 2.4.149 | what mutter you? | plague of all cowards i say still |
| 5.1.44 | V, 1, 44 | New | quotation not found; headword not found near cited line |  | your new fallen right, | nor claim no further than your newfalln right |
| 1.2.47 | H4A I, 2, 47 | Oldcastle | headword not found near cited line |  |  | as the honey of hybla my old lad |
| 5.4.156 | V, 4, 156 | Ours | headword not found near cited line |  |  | were alive and would deny it zounds i would |
| 1.2.170 | H4A I, 2, 170 | Persuasion | prose row break | 1.2.171 |  | well god give thee the spirit of |
| 2.4.498 | H4A II, 4, 498 | Pudding | prose row break | 2.4.499 |  | guts that roasted manningtree ox with the |
| 2.4.78 | H4A II, 4, 78 | Puke-stocking | prose row break | 2.4.79 |  | crystalbutton notpated agatering |
| 5.3.36 | H4A V, 3, 36 | Ragamuffins | prose row break | 5.3.37 |  | than mine own bowels i have led my |
| 3.3.179 | III, 3, 179 | Reckon | headword not found near cited line |  |  | tavernreckonings memorandums of bawdyhouses and |
| 4.3.10 | H4A IV, 3, 10 | Respect | headword not found near cited line |  |  | if wellrespected honour bid me on |
| 4.149.9 | 149, 9 | Respect | not a citation of this play |  | what merit do I in myself respect |  |
| 1.3.73 | I, 3, 73 | Retell | headword not found near cited line |  |  | at such a time with all the rest retold |
| 1.2.182 | H4A I, 2, 182 | Rossill | headword not found near cited line |  |  | peto and gadshill shall rob those men that we |
| 4.2.41 | H4A IV, 2, 41 | Scare-crow | headword not found near cited line |  |  | dead bodies no eye hath seen such scarcecrows |
| 3.1.198 | H4A III, 1, 198 | Self-willed | prose row break | 3.1.199 |  | she is desperate here a peevish |
| 4.43.12 | 43, 12 | Sightless | not a citation of this play |  | when in dead night thy shade on sightless eyes doth stay, |  |
| 4.2.146 | Shr. Ind. 2, 146 | Slide | headword not found near cited line |  |  | (no such line) |
| 4.3.96 | H4A IV, 3, 96 | Slip | headword not found near cited line |  |  | there without ransom to lie forfeited |
| 4.5.192 | H4A IV, 5, 192 | Snatch | not a citation of this play |  | an honour snatched with boisterous hand, |  |
| 2.4.375 | H4A II, 4, 375 | Son-in-law | prose row break | 2.4.376 |  | owen owen the same and his |
| 2.4.79 | H4A II, 4, 79 | Spanish | prose row break | 2.4.80 | Spanish pouch, | pukestocking stocking caddisgarter smoothtongue |
| 2.4.340 | H4A II, 4, 340 | Spear-grass | prose row break | 2.4.341 |  | yea and to tickle our noses with |
| 2.4.6 | H4A II, 4, 6 | String | headword not found near cited line |  |  | sounded the very basestring of humility sirrah |
| 1.1.4 | H4A I, 1, 4 | Strond | headword not found near cited line |  |  | to be commenced in strands afar remote |
| 5.2.8 | H4A V, 2, 8 | Supposition | headword not found near cited line |  |  | suspicion all our lives shall be stuck full of eyes |
| 4.2.3 | H4A IV, 2, 3 | Sutton-Cophill | headword not found near cited line |  |  | through well to sutton cofil tonight |
| 3.2.112 | H4A III, 2, 112 | Swathing-clothes | headword not found near cited line |  |  | thrice hath this hotspur mars in swathling clothes |
| 2.4.252 | H4A II, 4, 252 | Tallow-catch | prose row break | 2.4.253 |  | knottypated fool thou whoreson obscene greasy |
| 3.3.178 | H4A III, 3, 178 | Tavern-reckoning | prose row break | 3.3.179 |  | if there were anything in thy pocket but |
| 1.1.22 | I, 1, 22 | That | headword not found near cited line |  |  | forthwith a power of england shall we levy |
| 3.3.212 | H4A III, 3, 212 | Thereabouts | prose row break | 3.3.213 |  | thief of the age of two and twenty or |
| 2.4.467 | H4A II, 4, 467 | Threescore | headword not found near cited line |  |  | some fifty or by r lady inclining to three score |
| 1.1.177 | 1, 177 | Unsay | headword not found near cited line |  |  | (no such line) |
| 3.0 | III Prol. 47 | Vary | not a citation of this play |  |  |  |
| 3.1.52 | H4A III, 1, 52 | Vasty | quotation off by 1 | 3.1.53 | I can call spirits from the vasty deep, | peace cousin percy you will make him mad |
| 3.1.52 | H4A III, 1, 52 | Vasty | quotation not found; headword off by 1 | 3.1.53 | can this cockpit hold the vasty fields of France? | peace cousin percy you will make him mad |
| 2.2.123 | II, 2, 123 | Vasty | quotation not found; headword not found near cited line |  | to vasty Tartar, | (no such line) |
| 2.4.105 | II, 4, 105 | Vasty | quotation not found; headword not found near cited line |  | for whom this hungry war opens his vasty jaws, | showed themselves humours since the old days |
| 2.4.105 | II, 4, 105 | Vat | headword not found near cited line |  |  | showed themselves humours since the old days |
| 5.4.88 | H4A V, 4, 88 | Weave | headword not found near cited line |  |  | illweaved ambition how much thou art shrunk |
| 2.1.60 | H4A II, 1, 60 | Wild-boar | headword not found near cited line |  |  | a franklin in the wild of kent hath brought three |
| 2.1.60 | H4A II, 1, 60 | Wild-duck | headword not found near cited line |  |  | a franklin in the wild of kent hath brought three |
| 3.3.45 | H4A III, 3, 45 | Wild-goose | headword not found near cited line |  |  | ignis fatuus or a ball of wildfire theres no |
| 2.4.148 | H4A II, 4, 148 | Woolsack | headword off by 1 | 2.4.149 |  | plague of all cowards i say still |
| 1.1.3 | 1, 3 | Worcester | headword not found near cited line |  |  | and breathe shortwinded accents of new broils |
| 1.1.3 | 1, 3 | Worcester | headword not found near cited line |  |  | and breathe shortwinded accents of new broils |
| 2.1.70 | H4A II, 1, 70 | Worship | prose row break | 2.1.71 |  | that for the hangman for i know thou |
