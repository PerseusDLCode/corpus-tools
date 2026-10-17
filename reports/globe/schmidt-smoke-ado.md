# Schmidt smoke test: Much Ado About Nothing

Sources: shakespeare.ado.globe.xml sha256 301ebc135e238631; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of Much Ado About Nothing in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 1301/1367 (95.2%) pass.
- **With a quotation:** 811/821 (98.8%) have it on the cited line.
- **Headword only:** 490/546 (89.7%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 628 |
| headword on cited line | 525 |
| quotation on cited line, with differences | 148 |
| headword not found near cited line | 28 |
| prose row break | 22 |
| quotation not found; headword not found near cited line | 6 |
| not a citation of this play | 5 |
| headword off by 1 | 2 |
| headword off by 2 | 2 |
| quotation elsewhere in scene | 1 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

None.

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 5.1.249 | V, 1, 249 | Accusation | prose row break | 5.1.250 |  | is dead upon mine and my masters false |
| 3.4.56 | Ado III, 4, 56 | Ache | headword not found near cited line |  |  | for the letter that begins them all h |
| 2.1.187 | Ado II, 1, 187 | Agent | headword off by 1 | 2.1.186 |  | against whose charms faith melteth into blood |
| 2.1.114 | Ado II, 1, 114 | Amen | headword off by 2 | 2.1.112 |  | when the dance is done answer clerk |
| 3.4.73 | Ado III, 4, 73 | Carduus Benedictus | headword off by 1 | 3.4.74 |  | get you some of this distilled |
| 5.2.103 | Shr. Ind. 2, 103. | Cheer | quotation not found; headword not found near cited line |  | here is cheer enough, | will you go hear this news signior |
| 3.2.188 | III, 2, 188 | Cheer | quotation not found; headword not found near cited line |  | wedding cheer | (no such line) |
| 4.4.70 | IV, 4, 70 | Cheer | not a citation of this play |  | one mess is like to be your cheer |  |
| 5.1.14 | V, 1, 14 | Cheer | quotation not found; headword not found near cited line |  | some cheer is toward, | in every lineament branch shape and form |
| 5.2.10 | V, 2, 10 | Cheer | quotation not found; headword not found near cited line |  | our great good cheer | shall i always keep below stairs |
| 2.1.261 | Ado II, 1, 261 | Cleave | headword not found near cited line |  |  | hercules have turned spit yea and have cleft his |
| 3.3.190 | Ado III, 3, 190 | Commodity | prose row break | 3.3.191 |  | we are like to prove a goodly |
| 3.3.25 | Ado III, 3, 25 | Comprehend | prose row break | 3.3.26 |  | lantern this is your charge you shall |
| 1.3.62 | Ado I, 3, 62 | Conference | prose row break | 1.3.63 |  | prince and claudio hand in hand in sad |
| 1.3.65 | I, 3, 65 | Confirm | headword off by 2 | 1.3.63 |  | hero for himself and having obtained her give |
| 3.2.127 | Ado III, 2, 127 | Congregation | prose row break | 3.2.128 |  | should not marry her tomorrow in the |
| 1.3.21 | Ado I, 3, 21 | Controlment | prose row break | 1.3.22 |  | show of this till you may do it without |
| 3.2.68 | III, 2, 68 | Despite | prose row break | 3.2.69 |  | yes and his ill conditions and in |
| 2.1.201 | Ado II, 1, 201 | Drovier | prose row break | 2.1.202 |  | why thats spoken like an honest |
| 2.3.132 | Ado II, 3, 132 | Encounter | prose row break | 2.3.133 |  | says shall i says she that have so oft |
| 1.3.34 | Ado I, 3, 34 | Enfranchise | prose row break | 1.3.35 |  | villain i am trusted with a muzzle and |
| 4.1.165 | Ado IV, 1, 165 | Err | headword not found near cited line |  |  | to burn the errors that these princes hold |
| 3.3.227 | III, 3, 227 | Err | headword not found near cited line |  |  | (no such line) |
| 3.137.13 | 137, 13 | Err | not a citation of this play |  |  |  |
| 3.5.33 | Ado III, 5, 33 | Except | prose row break | 3.5.34 |  | marry sir our watch tonight |
| 4.2.5 | Ado IV, 2, 5 | Exhibition | prose row break | 4.2.6 |  | nay thats certain we have the |
| 5.1.102 | Ado V, 1, 102 | Extort | headword not found near cited line |  |  | gentlemen both we will not wake your patience |
| 3.1.9 | Ado III, 1, 9 | Favourite | headword not found near cited line |  |  | forbid the sun to enter like favorites |
| 3.4.99 | Ado III, 4, 99 | Gallop | quotation elsewhere in scene | 3.4.93-94 | what pace is this thy tongue keeps? Not a false gallop | good ursula |
| 1.196.36 | I, 196 | Haggard | not a citation of this play |  |  |  |
| 4.2.39 | IV, 2, 39 | Haggard | headword not found near cited line |  |  | the watch come forth masters i charge you |
| 1.1.186 | Ado I, 1, 186 | Hare-finder | prose row break | 1.1.187 |  | the flouting jack to tell us cupid is a good |
| 3.2.45 | Shr. Ind. 2, 45. | Hawk | headword not found near cited line |  |  | no but the barbers man hath been |
| 5.2.72 | V, 2, 72 | Hawk | headword not found near cited line |  |  | friend hates |
| 2.2.4 | Ado II, 2, 4 | Impediment | prose row break | 2.2.5 |  | any bar any cross any |
| 4.2.56 | Shr. Ind. 2, 56. | Io | headword not found near cited line |  |  | mean upon his words to disgrace hero before |
| 3.4.48 | Ado III, 4, 48 | Keep | headword not found near cited line |  |  | if your husband have stables enough youll see |
| 2.1.45 | Shr. Ind. 1, 45. | Manage | headword not found near cited line |  |  | no but to the gate and there will |
| 2.3.18 | II, 3, 18 | Massy | quotation not found; headword not found near cited line |  | drawing their massy irons and cutting the web, | he lie ten nights awake carving the fashion of a |
| 1.1.30 | Ado I, 1, 30 | Montanto | headword not found near cited line |  |  | i pray you is signior mountanto |
| 3.5.67 | Ado III, 5, 67 | Noncome | prose row break | 3.5.68 |  | heres that shall drive some of them to a |
| 3.53.14 | 53, 14 | None | not a citation of this play |  | you like n., none you, for constant heart, |  |
| 3.65.13 | 65, 13 | None | not a citation of this play |  | who his spoil of beauty can forbid? O, none |  |
| 3.3.11 | Ado III, 3, 11 | Oatcake | headword not found near cited line |  |  | hugh otecake sir or george |
| 1.3.3 | I, 3, 3 | Occasion | prose row break | 1.3.4 |  | there is no measure in the |
| 3.3.174 | Ado III, 3, 174 | Over | headword not found near cited line |  |  | oer night and send her home again without a |
| 2.1.120 | Shr. Ind. 1, 120. | Overjoyed | headword not found near cited line |  |  | head |
| 5.2.12 | Shr. Ind. 2, 12. | Overleather | headword not found near cited line |  |  | mouth it catches |
| 5.2.73 | Ado V, 2, 73 | Peaceably | prose row break | 5.2.74 |  | thou and i are too wise to woo |
| 3.3.110 | Ado III, 3, 110 | Penthouse | prose row break | 3.3.111 |  | stand thee close then under this |
| 4.2.69 | Ado IV, 2, 69 | Pinion | headword not found near cited line |  |  | come let them be opinioned |
| 5.1.335 | Ado V, 1, 335 | Prohibit | prose row break | 5.1.336 |  | and if a merry meeting may be wished god |
| 4.1.198 | Ado IV, 1, 198 | Reave | headword not found near cited line |  |  | nor my bad life reft me so much of friends |
| 2.1.126 | Shr. Ind. 1, 126. | Shift | quotation not found; headword not found near cited line |  | an onion will do well for such a shift | come come do you think i do not |
| 1.1.261 | Ado I, 1, 261 | Shoulder-clapper | headword not found near cited line |  |  | clapped on the shoulder and called adam |
| 2.3.146 | Ado II, 3, 146 | Tear | headword not found near cited line |  |  | o she tore the letter into a thousand |
| 1.1.201 | Ado I, 1, 201 | Threescore | prose row break | 1.1.202 |  | suspicion shall i never see a bachelor of |
| 4.2.88 | Ado IV, 2, 88 | Three-suited: | headword not found near cited line |  |  | and one that hath two gowns and every thing |
| 1.1.283 | Ado I, 1, 283 | Tullius; | headword not found near cited line |  |  | to the tuition of god from my |
| 3.3.100 | Ado III, 3, 100 | Vigilant | headword not found near cited line |  |  | great coil tonight adieu be vigitant i beseech |
| 2.1.37 | Ado II, 1, 37 | Waiting-gentlewoman | headword not found near cited line |  |  | in my apparel and make him my waiting |
| 2.1.65 | Ado II, 1, 65 | Wayward | prose row break | 2.1.66 |  | to make an account of her life to a clod of |
| 3.3.15 | Ado III, 3, 15 | Well-favoured | headword not found near cited line |  |  | wellfavored man is the gift of fortune but to |
| 2.2.18 | Ado II, 2, 18 | Window | headword not found near cited line |  |  | chamberwindow |
| 3.3.144 | III, 3, 144 | Window | headword not found near cited line |  |  | bels priests in the old churchwindow sometime |
| 3.3.145 | Ado III, 3, 145 | Worm-eaten | prose row break | 3.3.146 |  | like the shaven hercules in the smirched |
