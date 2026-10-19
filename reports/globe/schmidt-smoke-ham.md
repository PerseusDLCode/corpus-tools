# Schmidt smoke test: Hamlet

Sources: shakespeare.ham.globe.xml sha256 00e9590f7dfbe4cf; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of Hamlet in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 2771/2907 (95.3%) pass.
- **With a quotation:** 1878/1904 (98.6%) have it on the cited line.
- **Headword only:** 893/1003 (89.0%) have it on the cited line.

| Verdict | Citations |
|---|---|
| quotation on cited line | 1451 |
| headword on cited line | 948 |
| quotation on cited line, with differences | 372 |
| headword not found near cited line | 65 |
| not a citation of this play | 35 |
| prose row break | 13 |
| headword off by 1 | 7 |
| quotation off by 1 | 6 |
| quotation not found; headword not found near cited line | 5 |
| quotation elsewhere in scene | 3 |
| quotation off by 2 | 2 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

None.

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 2.2.369 | Hml. II, 2, 369 | Ado | headword not found near cited line |  |  | faith there has been much to do on |
| 1.147.369 | I, 147 | Ado | not a citation of this play |  |  |  |
| 2.1.99 | Hml. II, 1, 99 | Adoors; | headword not found near cited line |  |  | for out o doors he went without their helps |
| 2.2.333 | Hml. II, 2, 333 | Adventurous | prose row break | 2.2.334 |  | his majesty shall have tribute of me the |
| 2.2.468 | Hml. II, 2, 468 | Aeneas | headword not found near cited line |  |  | neas tale to dido and thereabout of it |
| 3.2.138 | Hml. III, 2, 138 | Ago | headword off by 1 | 3.2.139 |  | black for ill have a suit of sables o heavens |
| 3.2.226 | Hml. III, 2, 226 | Apt | headword not found near cited line |  |  | nor earth to me give food nor heaven light |
| 4.7.53 | Hml. IV, 7, 53 | Assay | quotation elsewhere in scene | 4.7.153 | 'twere better not assayed, | and in a postscript here he says alone |
| 5.2.348 | Hml. V, 2, 348 | Attachment | headword not found near cited line |  |  | is strict in his arrest o i could tell you |
| 3.0 | III Prol. 11 | Attent | not a citation of this play |  |  |  |
| 5.49.4 | 49, 4 | Audit | not a citation of this play |  | when as thy love hath cast his utmost sum, call'd to that audit by advised respects, |  |
| 5.126.11 | 126, 11 | Audit | not a citation of this play |  |  |  |
| 1.1.4 | Hml. I, 1, 4 | Barnardo | headword not found near cited line |  |  | bernardo |
| 1.2.204 | Hml. I, 2, 204 | Bestilled | headword not found near cited line |  |  | within his truncheons length whilst they distilled |
| 3.4.182 | Hml. III, 4, 182 | Blunt | headword not found near cited line |  |  | let the bloat king tempt you again to bed |
| 2.2.554 | Hml. II, 2, 554 | Bodkin | headword not found near cited line |  |  | gods bodykins man much better |
| 2.1.69 | Hml. II, 1, 69 | Buy | headword not found near cited line |  |  | my lord i have god be wi you fare you well |
| 2.2.575 | II, 2, 575 | Buy | headword not found near cited line |  |  | ay so god be wi ye now i am alone |
| 4.4.30 | IV, 4, 30 | Buy | headword not found near cited line |  |  | god be wi you sir willt please you go my lord |
| 4.5.200 | IV, 5, 200 | Buy | headword not found near cited line |  |  | and of all christian souls i pray god god be wi ye |
| 2.2.412 | Hml. II, 2, 412 | Buzz | quotation off by 1 | 2.2.411 | the actors are come hither, my lord. B., buzz | buz buz |
| 4.7.53 | Hml. IV, 7, 53 | Cháracter | quotation off by 1 | 4.7.52 | know you the hand? 'tis Hamlet's cháracter | and in a postscript here he says alone |
| 3.2.133 | Hml. III, 2, 133 | Cheerfully | headword off by 1 | 3.2.134 |  | should a man do but be merry for look you |
| 3.4.156 | Hml. III, 4, 156 | Cleave | headword not found near cited line |  |  | o hamlet thou hast cleft my heart in twain |
| 3.4.156 | Hml. III, 4, 156 | Cleave | headword not found near cited line |  |  | o hamlet thou hast cleft my heart in twain |
| 2.2.416 | Hml. II, 2, 416 | Comical | quotation not found; headword not found near cited line |  | pastoral - comical | tragedy comedy history pastoral |
| 2.2.416 | Hml. II, 2, 416 | Comical | quotation off by 2 | 2.2.418 | tragical - comical - historical - pastoral, | tragedy comedy history pastoral |
| 3.89.2 | 89, 2 | Comment | not a citation of this play |  | say that thou didst forsake me for some fault, and I will comment upon that offence, |  |
| 3.2.140 | Shr. Ind. 2, 140. | Comonty | not a citation of this play |  |  |  |
| 2.2.186 | Hml. II, 2, 186 | Conceive | prose row break | 2.2.185 |  | is a blessing but not as your daughter may |
| 3.1.1 | Hml. III, 1, 1 | Conference | headword not found near cited line |  |  | and can you by no drift of circumstance |
| 3.1.1 | Hml. III, 1, 1 | Conference | headword not found near cited line |  |  | and can you by no drift of circumstance |
| 2.2.288 | Hml. II, 2, 288 | Confession | prose row break | 2.2.289 |  | you were sent for and there is a kind of |
| 3.0 | III Prol. 56 | Conveniently | not a citation of this play |  |  |  |
| 5.1.245 | Hml. V, 1, 245 | Couch | quotation not found; headword not found near cited line |  | couch we awhile and mark, | a very noble youth mark |
| 4.7.7 | Hml. IV, 7, 7 | Criminal | headword not found near cited line |  |  | so crimeful and so capital in nature |
| 4.6.20 | IV, 6, 20 | Deal | headword not found near cited line |  |  | their prisoner they have dealt with me like |
| 5.97.8 | 97, 8 | Decease | not a citation of this play |  |  |  |
| 2.121.3 | 121, 3 | Deem | not a citation of this play |  |  |  |
| 3.1.84 | Hml. III, 1, 84 | Devoutly | quotation elsewhere in scene | 3.1.64 | devoutly to be wished, | and thus the native hue of resolution |
| 3.2.312 | Hml. III, 2, 312 | Distemper | prose row break | 3.2.313 |  | is in his retirement marvellous |
| 4.7.58 | Hml. IV, 7, 58 | Do | headword not found near cited line |  |  | thus didest thou if it be so laertes |
| 3.0 | III Prol. 42 | Dole | not a citation of this play |  |  |  |
| 1.1.119 | Hml. I, 1, 119 | Doomsday | headword off by 1 | 1.1.120 |  | upon whose influence neptunes empire stands |
| 1.101.2 | 101, 2 | Dye | not a citation of this play |  |  |  |
| 3.2.143 | III, 2, 143 | Epitaph | prose row break | 3.2.144 |  | not thinking on with the hobbyhorse whose |
| 2.2.468 | Hml. II, 2, 468 | Especially | prose row break | 2.2.469 |  | neas tale to dido and thereabout of it |
| 4.1.84 | Shr. Ind. 1, 84. | Farmer | not a citation of this play |  |  |  |
| 1.2.210 | I, 2, 210 | Farmer | headword not found near cited line |  |  | form of the thing each word made true and good |
| 3.0 | III Prol. 13 | Fine | not a citation of this play |  |  |  |
| 2.2.308 | Hml. II, 2, 308 | Forego | headword not found near cited line |  |  | forgone all custom of exercises and indeed it |
| 3.2.342 | III, 2, 342 | Forfeit | quotation not found; headword not found near cited line |  | to forfeit all your goods, | this mothers admiration impart |
| 1.5.185 | Hml. I, 5, 185 | Friending | quotation off by 1 | 1.5.186 | to express his love and friending to you, | and what so poor a man as hamlet is |
| 2.0 | II Prol. 21 | Fulfil | not a citation of this play |  |  |  |
| 4.5.199 | Hml. IV, 5, 199 | Gramercy | headword not found near cited line |  |  | god ha mercy on his soul |
| 2.1.5 | 1, 5 | Greeting | headword not found near cited line |  |  | of his behavior my lord i did intend it |
| 2.1.5 | 1, 5 | Greeting | headword not found near cited line |  |  | of his behavior my lord i did intend it |
| 4.5.14 | IV, 5, 14 | Greeting | headword not found near cited line |  |  | twere good she were spoken with for she may strew |
| 5.2.9 | V, 2, 9 | Greeting | headword not found near cited line |  |  | when our deep plots do pall and that should teach us |
| 1.3.65 | Hml. I, 3, 65 | Hatch | headword not found near cited line |  |  | of each newhatched unfledged comrade beware |
| 2.2.45 | Shr. Ind. 2, 45. | Hawk | not a citation of this play |  |  |  |
| 1.1.148 | Hml. I, 1, 148 | Hest | headword not found near cited line |  |  | and then it started like a guilty thing |
| 1.5.84 | Hml. I, 5, 84 | Howsomever | headword not found near cited line |  |  | but howsoever thou pursuest this act |
| 1.5.114 | Hml. I, 5, 114 | Illo | headword not found near cited line |  |  | so be it |
| 5.2.155 | Hml. V, 2, 155 | Impawn | headword not found near cited line |  |  | six barbary horses against the which he has |
| 5.2.155 | Hml. V, 2, 155 | Impone | prose row break | 5.2.156 |  | six barbary horses against the which he has |
| 3.0 | III Prol. 22 | Inquire | not a citation of this play |  |  |  |
| 5.2.118 | Hml. V, 2, 118 | Inventorially | prose row break | 5.2.119 |  | in you though i know to divide him |
| 1.3.83 | Hml. I, 3, 83 | Invest | headword not found near cited line |  |  | the time invites you go your servants tend |
| 3.2.131 | Hml. III, 2, 131 | Jig-maker | headword off by 1 | 3.2.132 |  | ay my lord |
| 3.2.66 | Hml. III, 2, 66 | Knee-crooking | headword not found near cited line |  |  | and crook the pregnant hinges of the knee |
| 1.1.98 | Hml. I, 1, 98 | Landless | headword not found near cited line |  |  | sharked up a list of lawless resolutes |
| 3.3.7 | Hml. III, 3, 7 | Lunes | headword not found near cited line |  |  | out of his lunacies we will ourselves provide |
| 3.2.146 | Hml. III, 2, 146 | Mallecho | quotation off by 1 | 3.2.147-148 | this is miching m.; it means mischief, | what means this my lord |
| 3.2.146 | Hml. III, 2, 146 | Miching mallecho | quotation off by 1 | 3.2.147-148 | this is m.; it means mischief, | what means this my lord |
| 1.6.64 | I, 6 | Mildew | not a citation of this play |  |  |  |
| 2.2.406 | Hml. II, 2, 406 | Monday | prose row break | 2.2.407 |  | the players mark it you say right sir o |
| 3.2.146 | Hml. III, 2, 146 | Munch | headword not found near cited line |  |  | what means this my lord |
| 1.3.65 | Hml. I, 3, 65 | New | quotation not found; headword not found near cited line |  | each new hatched comrade, | of each newhatched unfledged comrade beware |
| 3.0 | III Prol. 55 | Nill | not a citation of this play |  |  |  |
| 5.1.181 | Hml. V, 1, 181 | Now-a-days | prose row break | 5.1.182 |  | he die as we have many pocky corses |
| 3.1.136 | Hml. III, 1, 136 | Nowhere | headword not found near cited line |  |  | he may play the fool no where but ins own |
| 2.2.260 | Hml. II, 2, 260 | Nutshell | prose row break | 2.2.261 |  | o god i could be bounded in a |
| 2.2.531 | Hml. II, 2, 531 | O'erthrow | headword not found near cited line |  |  | about her lank and all oerteemed loins |
| 3.1.158 | Hml. III, 1, 158 | O'erthrow | headword not found near cited line |  |  | o what a noble mind is here oer thrown |
| 5.2.283 | Hml. V, 2, 283 | Onyx | headword not found near cited line |  |  | and in the cup an union shall he throw |
| 3.2.140 | Hml. III, 2, 140 | Outlive | prose row break | 3.2.141 |  | then theres hope a great mans memory may |
| 4.1.25 | Hml. IV, 1, 25 | Over | quotation off by 2 | 4.1.27 | pure, | oer whom his very madness like some ore |
| 2.2.416 | Hml. II, 2, 416 | Pastoral-comical | headword not found near cited line |  |  | tragedy comedy history pastoral |
| 1.3.26 | Hml. I, 3, 26 | Peculiar | quotation not found; headword not found near cited line |  | in his peculiar sect and force, | as he in his particular act and place |
| 1.1.63 | Hml. I, 1, 63 | Pole-axe | headword not found near cited line |  |  | he smote the sledded polacks on the ice |
| 3.2.414 | Hml. III, 2, 414 | Poniard | headword not found near cited line |  |  | i will speak daggers to her but use none |
| 5.1.221 | V, 1, 221 | Pooh | headword not found near cited line |  |  | and smelt so pah |
| 2.87.1 | 87, 1 | Possess | not a citation of this play |  | thou art too dear for my possessing, |  |
| 4.7.171 | Hml. IV, 7, 171 | Purple | headword off by 1 | 4.7.170 |  | that liberal shepherds give a grosser name |
| 3.0 | III Prol. 13 | Quaintly | not a citation of this play |  |  |  |
| 4.4.152 | IV, 4 | Rank | quotation elsewhere in scene | 4.4.21-22 | nor would it yield to Norway or the Pole a ranker rate, | (no such line) |
| 2.1.34 | Hml. II, 1, 34 | Reclaim | headword not found near cited line |  |  | a savageness in unreclaimed blood |
| 4.7.79 | Hml. IV, 7, 79 | Riband | headword off by 1 | 4.7.78 |  | yet needful too for youth no less becomes |
| 5.1.56 | Shr. Ind. 1, 56. | Rose-water | not a citation of this play |  |  |  |
| 3.2.137 | III, 2, 137 | Sables | headword off by 1 | 3.2.138 |  | so long nay then let the devil wear |
| 1.3.21 | Hml. I, 3, 21 | Sanctity | headword not found near cited line |  |  | the safety and health of this whole state |
| 2.2.214 | II, 2, 214 | Sanctity | headword not found near cited line |  |  | reason and sanity could not so prosperously be |
| 1.3.21 | In I, 3, 21 | Sanity | headword not found near cited line |  |  | the safety and health of this whole state |
| 3.105.12 | 105, 12 | Scope | not a citation of this play |  | three themes in one, which wondrous scope affords, |  |
| 4.6.2 | Hml. IV, 6, 2 | Sea-faring | headword not found near cited line |  |  | sailors sir they say they have letters for you |
| 4.0 | IV Prol. 2 | Settle | not a citation of this play |  |  |  |
| 3.2.416 | Hml. III, 2, 416 | Somever | headword not found near cited line |  |  | how in my words soever she be shent |
| 2.0 | II Prol. 12 | Speken | not a citation of this play |  |  |  |
| 1.5.188 | Hml. I, 5, 188 | Spite | quotation off by 1 | 1.5.189-190 | O cursed s., that ever I was born to set it right, | and still your fingers on your lips i pray |
| 2.2.616 | Hml. II, 2, 616 | Stallion | headword not found near cited line |  |  | a scullion |
| 1.5.95 | Hml. I, 5, 95 | Stiff-borne | headword not found near cited line |  |  | but bear me stiffly up remember thee |
| 2.2.401 | Hml. II, 2, 401 | Swathing-clouts | headword not found near cited line |  |  | see there is not yet out of his swaddlingclouts |
| 5.115.7 | 115, 7 | Tan | not a citation of this play |  | time, whose accidents . . . tan sacred beauty, |  |
| 5.2.84 | V, 2, 84 | That | headword not found near cited line |  |  | this waterfly |
| 1.143.4 | 143, 4 | Thing | not a citation of this play |  |  |  |
| 2.2.73 | Hml. II, 2, 73 | Threescore | headword not found near cited line |  |  | gives him three thousand crowns in annual fee |
| 4.7.28 | IV, 7, 28 | Top | headword not found near cited line |  |  | stood challenger on mount of all the age |
| 2.63.5 | 63, 5 | Travail | not a citation of this play |  | his youthful morn hath travailed on to age's steepy night, |  |
| 2.109.6 | 109, 6 | Travail | not a citation of this play |  | like him that travails, I return again, |  |
| 1.2.248 | Hml. I, 2, 248 | Treble | headword not found near cited line |  |  | let it be tenable in your silence still |
| 2.2.393 | Hml. II, 2, 393 | Uncle-father | prose row break | 2.2.394 |  | than yours you are welcome but my |
| 4.5.164 | Hml. IV, 5, 164 | Uncovered | headword not found near cited line |  |  | they bore him barefaced on the bier |
| 1.5.18 | Hml. I, 5, 18 | Unfix | headword not found near cited line |  |  | thy knotted and combined locks to part |
| 1.2.2 | Hml. I, 2, 2 | Vail | headword not found near cited line |  |  | the memory be green and that it us befitted |
| 3.56.12 | 56, 12 | View | not a citation of this play |  | that, when they see return of love, more blest may be the view |  |
| 3.141.4 | 141, 4 | View | not a citation of this play |  | who in despite of view is pleased to dote, |  |
| 3.148.11 | 148, 11 | View | not a citation of this play |  | no marvel then though I mistake my view |  |
| 1.2.142 | Hml. I, 2, 142 | Visitation | headword not found near cited line |  |  | visit her face too roughly heaven and earth |
| 1.2.198 | Hml. I, 2, 198 | Waste | headword not found near cited line |  |  | in the dead vast and middle of the night |
| 1.2.198 | Hml. I, 2, 198 | Waste | headword not found near cited line |  |  | in the dead vast and middle of the night |
| 1.2.55 | Shr. Ind. 2, 55. | Wave | not a citation of this play |  |  |  |
| 1.2.249 | Hml. I, 2, 249 | Whatsomever | headword not found near cited line |  |  | and whatsoever else shall hap tonight |
| 3.124.8 | 124, 8 | Whereto | not a citation of this play |  |  |  |
| 3.137.8 | 137, 8 | Whereto | not a citation of this play |  |  |  |
| 1.158.317 | I, 158 | Woodcock | not a citation of this play |  |  |  |
