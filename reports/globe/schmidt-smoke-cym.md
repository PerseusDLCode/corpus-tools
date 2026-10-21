# Schmidt smoke test: Cymbeline

Sources: shakespeare.cym.globe.xml sha256 2be4d2b466b1e679; citations.tsv sha256 814c223b582b6752; citation_quotes.tsv sha256 ba27389f931477ca.

Every citation of Cymbeline in Schmidt's *Shakespeare-Lexicon*, checked against the regenerated edition: does the cited line contain the quotation, or (for a citation without one) the headword? Report only; nothing is fixed.

- **All citations:** 2146/2255 (95.2%) pass.
- **With a quotation:** 1242/1286 (96.6%) have it on the cited line.
- **Headword only:** 904/969 (93.3%) have it on the cited line.

| Verdict | Citations |
|---|---|
| headword on cited line | 947 |
| quotation on cited line | 930 |
| quotation on cited line, with differences | 269 |
| not a citation of this play | 49 |
| headword not found near cited line | 32 |
| quotation off by 1 | 10 |
| quotation not found; headword not found near cited line | 7 |
| headword off by 1 | 6 |
| prose row break | 3 |
| headword off by 3 | 2 |

## Runs

Stretches where 3 or more citations in a row, in one scene, are off by the same amount: where our count and the Globe's part. A positive offset means the quotation is on a later line of ours than Schmidt cites.

| Scene | Cited lines | Offset | Citations |
|---|---|---|---|
| 2.3 | 22-26 | +1 | 5 |

## Every failure

| Cited | Schmidt | Headword | Verdict | Found at | Quotation | Our line |
|---|---|---|---|---|---|---|
| 1.1.24 | Cymb. I, 0, 24 | Accordingly | headword not found near cited line |  |  | endows a man but he you speak him far |
| 3.4.60 | Cymb. III, 4, 60 | Aeneas | headword not found near cited line |  |  | true honest men being heard like false neas |
| 4.2.293 | IV, 4, 293 | After-hours | headword not found near cited line |  |  | ods pittikins can it be six mile yet |
| 3.5.95 | Cymb. III, 5, 95 | All-worthy | quotation off by 1 | 3.5.94 | O, my all-worthy lord! All-worthy villain! | discover where thy mistress is at once |
| 1.4.52 | Cymb. I, 4, 52 | Arbitrement | prose row break | 1.4.53 |  | faith yes to be put to the |
| 2.97.4 | 97, 4 | Bareness | not a citation of this play |  | old December's bareness |  |
| 5.52.4 | 52, 4 | Blunt | not a citation of this play |  | blunting the fine point of seldom pleasure, |  |
| 5.115.7 | 115, 7 | Blunt | not a citation of this play |  | blunt the sharpest intents, |  |
| 2.75.10 | 75, 10 | By | not a citation of this play |  |  |  |
| 2.3.24 | Cymb. II, 3, 24 | Chaliced | quotation off by 1 | 2.3.25 | chaliced flowers, | his steeds to water at those springs |
| 2.89.6 | 89, 6 | Change | not a citation of this play |  | to set a form upon desired change |  |
| 2.93.6 | 93, 6 | Change | not a citation of this play |  | I cannot know thy change |  |
| 1.105.11 | 105, 11 | Change | not a citation of this play |  | and in this change is my invention spent, |  |
| 3.5.86 | III, 5, 86 | Close | quotation off by 1 | 3.5.85 | close villain, | ill have this secret from thy heart or rip |
| 2.0 | II Prol. 34 | Coast | not a citation of this play |  |  |  |
| 2.1.60 | II, 1, 60 | Coast | headword not found near cited line |  |  | cannot take two from twenty for his heart |
| 3.1.73 | III, 1, 73 | Coast | headword not found near cited line |  |  | behoves me keep at utterance i am perfect |
| 5.0 | V Prol. 15 | Coast | not a citation of this play |  |  |  |
| 5.3.19 | V, 3, 19 | Coast | headword not found near cited line |  |  | he with two striplings lads more like to run |
| 3.6.14 | 6, 14 | Conquest | quotation not found; headword not found near cited line |  | to be death's conquest | is worse in kings than beggars my dear lord |
| 3.74.11 | 74, 11 | Conquest | not a citation of this play |  | the coward conquest of a wretch's knife, |  |
| 1.4.65 | Cymb. I, 4, 65 | Constant-qualified | headword not found near cited line |  |  | qualified and less attemptable than any |
| 3.0 | III Prol. 7 | Cricket | not a citation of this play |  |  |  |
| 5.4.171 | Cymb. V, 4, 171 | Debitor and Creditor | headword not found near cited line |  |  | thousands in a trice you have no true debtor and |
| 3.0 | III Prol. 59 | Deck | not a citation of this play |  |  |  |
| 4.1.57 | IV, 1, 57 | Deck | headword not found near cited line |  |  | (no such line) |
| 5.1.115 | V, 1, 115 | Deck | headword not found near cited line |  |  | (no such line) |
| 4.92.8 | 92, 8 | Depend | not a citation of this play |  | a better state to me belongs than that which on thy humour doth depend |  |
| 4.101.3 | 101, 3 | Depend | not a citation of this play |  |  |  |
| 5.5.178 | V, 5, 178 | Description | headword off by 1 | 5.5.177 |  | proved us unspeaking sots nay nay to the purpose |
| 2.101.4 | 101, 4 | Dignify | not a citation of this play |  | both truth and beauty on my love depends; so dost thou too, and therein dignifyed, |  |
| 3.0 | III Prol. 19 | Diligence | not a citation of this play |  |  |  |
| 3.0 | III Prol. 2 | Din | not a citation of this play |  |  |  |
| 3.6.55 | Cymb. III, 6, 55 | Dirty | headword off by 1 | 3.6.54 |  | as tis no better reckoned but of those |
| 5.5.384 | V, 5, 384 | Distinctively | headword not found near cited line |  |  | distinction should be rich in where how lived you |
| 1.5.82 | Cymb. I, 5, 82 | Do | headword off by 3 | 1.5.85 |  | to taste of too so so well done well done |
| 3.5.159 | Cymb. III, 5, 159 | Duteous | quotation off by 1 | 3.5.158 | be but duteous | preferment shall tender itself to thee my revenge is |
| 3.6.43 | Cymb. III, 6, 43 | Earthly | headword off by 1 | 3.6.44 |  | by jupiter an angel or if not |
| 5.19.7 | 19, 7 | Fade | not a citation of this play |  | all her fadeing sweets, |  |
| 5.146.6 | 146, 6 | Fade | not a citation of this play |  | why so large cost dost thou upon thy fadeing mansion spend? |  |
| 3.7.6 | Cymb. III, 7, 6 | Fallen-off | headword not found near cited line |  |  | the fallnoff britons that we do incite |
| 3.6.60 | Cymb. III, 6, 60 | Fidele | headword off by 1 | 3.6.61 |  | whats your name |
| 4.2.270 | Cymb. IV, 2, 270 | Flash | headword not found near cited line |  |  | fear no more the lightningflash |
| 2.3.126 | Cymb. II, 3, 126 | Foil | quotation off by 1 | 2.3.127 | with a base slave, | the consequence o the crown and must not soil |
| 1.4.21 | Cymb. I, 4, 21 | Fortify | prose row break | 1.4.22 |  | are wonderfully to extend him be it but to |
| 2.0 | II Prol. 23 | Full | not a citation of this play |  |  |  |
| 5.33.4 | 33, 4 | Gíld | not a citation of this play |  |  |  |
| 5.3.37 | Cymb. V, 3, 37 | Gin | headword not found near cited line |  |  | damned in the first beginners gan to look |
| 2.3.22 | Cymb. II, 3, 22 | Gin | headword off by 1 | 2.3.23 |  | hark hark the lark at heavens gate sings |
| 5.5.197 | V, 5, 197 | Gin | headword not found near cited line |  |  | gan in your duller britain operate |
| 3.133.6 | 133, 6 | Hard | not a citation of this play |  | my next self thou harder hast engrossed, |  |
| 4.2.168 | Cymb. IV, 2, 168 | Hasty | headword off by 3 | 4.2.165 |  | ild let a parish of such clotens blood |
| 5.5.184 | Cymb. V, 5, 184 | Honoured | headword not found near cited line |  |  | upon his honored finger to attain |
| 4.0 | IV Prol. 1 | Imagine | not a citation of this play |  |  |  |
| 4.63.2 | 63, 2 | Injurious | not a citation of this play |  | with time's injurious hand crushed, |  |
| 4.2.100 | Cymb. IV, 2, 100 | Inland | headword not found near cited line |  |  | yield rustic mountaineer |
| 5.5.392 | Cymb. V, 5, 392 | Interrogatory | headword not found near cited line |  |  | will serve our long intergatories see |
| 2.3.78 | Cymb. II, 3, 78 | Keep | headword not found near cited line |  |  | can it not do and undo i will make |
| 1.120.7 | 120, 7 | Leisure | not a citation of this play |  | I have no leisure taken to weigh how once I suffered, |  |
| 4.0 | IV Prol. 52 | Leonine | not a citation of this play |  |  |  |
| 2.3.25 | Cymb. II, 3, 25 | Mary-buds | quotation off by 1 | 2.3.26-27 | and winking mary-buds begin to ope their golden eyes, | on chaliced flowers that lies |
| 3.5.168 | Cymb. III, 5, 168 | Meed | quotation off by 1 | 3.5.167 | labour be his meed | (no such line) |
| 4.1.26 | Cymb. IV, 1, 26 | Meeting-place | prose row break | 4.1.27 |  | hand this is the very description of their |
| 3.1.36 | Cymb. III, 1, 36 | Mo | quotation not found; headword not found near cited line |  | mo kings, | that time and as i said there is no moe such |
| 5.3.72 | V, 3, 72 | Mo | quotation not found; headword not found near cited line |  | moe ministers, | sweet words or hath more ministers than we |
| 3.0 | III Prol. 11 | Mould | not a citation of this play |  |  |  |
| 1.4.97 | Cymb. I, 4, 97 | Neighbour | quotation not found; headword not found near cited line |  | neighbouring ponds, | you know strange fowl light upon neigh boring |
| 1.91.3 | 91, 3 | New | not a citation of this play |  | new fangled ill, |  |
| 3.141.2 | 141, 2 | Note | not a citation of this play |  | they in thee a thousand errors note |  |
| 2.2.11 | Cymb. II, 2, 11 | O'erlaboured | headword not found near cited line |  |  | the crickets sing and mans oer labored sense |
| 2.3.26 | Cymb. II, 3, 26 | Ope | headword off by 1 | 2.3.27 |  | and winking marybuds begin |
| 2.4.84 | Cymb. II, 4, 84 | Outgo | headword not found near cited line |  |  | was as another nature dumb outwent her |
| 4.133.13 | 133, 13 | Pen | not a citation of this play |  |  |  |
| 3.51.10 | 51, 10 | Perfect | not a citation of this play |  | desire, of perfectest love being made, |  |
| 4.146.3 | 146, 3 | Pine | not a citation of this play |  | why doest thou pine within and suffer dearth, |  |
| 4.146.3 | 146, 3 | Pine | not a citation of this play |  |  |  |
| 5.1.50 | Shr. Ind. 1, 50. | Procure | not a citation of this play |  | procure me music ready, |  |
| 3.78.9 | 78, 9 | Proud | not a citation of this play |  |  |  |
| 3.4.162 | Cymb. III, 4, 162 | Quarrellous | headword not found near cited line |  |  | as quarrelous as the weasel nay you must |
| 4.2.224 | Cymb. IV, 2, 224 | Raddock | headword not found near cited line |  |  | outsweetened not thy breath the ruddock would |
| 3.3.103 | Cymb. III, 3, 103 | Reave | headword not found near cited line |  |  | thou reftst me of my lands euriphile |
| 3.0 | III Prol. 35 | Region | not a citation of this play |  |  |  |
| 4.4.4 | IV, 4, 4 | Region | quotation not found; headword not found near cited line |  | from region to region | have we in hiding us this way the romans |
| 5.277.226 | V, 277 | Richly | not a citation of this play |  | three of your argosies are richly come to harbour, |  |
| 2.8.30 | II, 8, 30 | Richly | not a citation of this play |  | a vessel richly fraught, |  |
| 5.4.45 | Cymb. V, 4, 45 | Rip | headword not found near cited line |  |  | that from me was posthumus ript |
| 4.99.11 | 99, 11 | Robbery | not a citation of this play |  |  |  |
| 3.4.82 | Cymb. III, 4, 82 | Scaffold | headword not found near cited line |  |  | obedient as the scabbard what is here |
| 4.2.35 | Cymb. IV, 2, 35 | Sea-monster | headword not found near cited line |  |  | the imperious seas breed monsters for the dish |
| 5.104.6 | 104, 6 | Season | not a citation of this play |  |  |  |
| 5.3.78 | Cymb. V, 3, 78 | Shoulder-clapper | headword not found near cited line |  |  | once touch my shoulder great the slaughter is |
| 4.0 | IV Prol. 21 | Silk | not a citation of this play |  |  |  |
| 5.0 | V Prol. 8 | Silk | not a citation of this play |  |  |  |
| 3.5.168 | Cymb. III, 5, 168 | Slowness | quotation off by 1 | 3.5.166-167 | this fool's speed be crossed with slowness | (no such line) |
| 5.1.88 | Shr. Ind. 1, 88. | Soto | not a citation of this play |  |  |  |
| 5.40.14 | 40, 14 | Spite | not a citation of this play |  | kill me with spites, yet we must not be foes, |  |
| 1.14.12 | 14, 12 | Store | not a citation of this play |  | truth and beauty shall together thrive, if from thyself to store thou wouldst convert, |  |
| 4.90.11 | 90, 11 | Taste | not a citation of this play |  | so shall I taste at first the very worst of fortune's might, |  |
| 3.5.160 | Cymb. III, 5, 160 | Tender | quotation off by 1 | 3.5.158-159 | be but duteous, and true preferment shall tender itself to thee, | now at milford would i had wings to follow it |
| 5.2.56 | V, 2, 56 | Tickle | quotation not found; headword not found near cited line |  | the devil Luxury . . . tickles these together, | (no such line) |
| 1.4.45 | Cymb. I, 4, 45 | Troien | headword not found near cited line |  |  | upon importance of so slight and trivial a nature |
| 5.5.177 | Cymb. V, 5, 177 | Trull | headword not found near cited line |  |  | were cracked of kitchentrulls or his description |
| 5.4.15 | Cymb. V, 4, 15 | Unconstrained | headword not found near cited line |  |  | desired more than constrained to satisfy |
| 4.147.12 | 147, 12 | Vainly | not a citation of this play |  | my thoughts and my discourse as madmen's are, at random from the truth vainly expressed, |  |
| 5.1.101 | Shr. Ind. 1, 101. | Very | not a citation of this play |  | were he the veryest antic in the world, |  |
| 5.2.64 | V, 2, 64 | Very | quotation not found; headword not found near cited line |  | thou hast the veryest shrew of all, | (no such line) |
| 2.3.23 | Cymb. II, 3, 23 | Water | quotation off by 1 | 2.3.24 | his steeds to water at those springs, | and phoebus gins arise |
| 2.4.24 | Cymb. II, 4, 24 | Wing-led | headword not found near cited line |  |  | now mingled with their courages will make known |
| 4.2.62 | Shr. Ind. 2, 62. | Workmanly | not a citation of this play |  | so workmanly the blood and tears are drawn, |  |
