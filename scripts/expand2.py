#!/usr/bin/env python3
"""Expansion 2 — More questions across all categories."""
import json, random, hashlib, os
random.seed(456)

with open("/home/claude/manna/manna_questions.json") as f:
    ALL = json.load(f)
existing = set(q["question"].strip().lower() for q in ALL)

def Q(cat,diff,q,opts,cor,exp=""):
    k = q.strip().lower()
    if k not in existing:
        existing.add(k)
        ALL.append({"category":cat,"difficulty":diff,"question":q,"options":opts,"correct":cor,"explanation":exp})

def S(c,ws):
    o=[c]+list(ws[:3])
    random.shuffle(o)
    return o

# ============================================================================
# BOOK LOCATION QUESTIONS — "In which book does X happen?"
# ============================================================================
EVENTS_IN_BOOKS = [
    ("the story of creation","Genesis","Exodus","Psalms","Job","Genesis & Creation","Layperson"),
    ("the story of Cain and Abel","Genesis","Exodus","Judges","Job","Genesis & Creation","Layperson"),
    ("the flood and Noah's ark","Genesis","Exodus","Isaiah","Psalms","Genesis & Creation","Layperson"),
    ("the Tower of Babel","Genesis","Exodus","Daniel","Revelation","Genesis & Creation","Deacon"),
    ("Abraham's call to leave Ur","Genesis","Exodus","Joshua","Judges","Genesis & Creation","Deacon"),
    ("Jacob's wrestling with God","Genesis","Exodus","Judges","1 Samuel","Genesis & Creation","Deacon"),
    ("Joseph's rise in Egypt","Genesis","Exodus","Numbers","Daniel","Genesis & Creation","Layperson"),
    ("the ten plagues","Exodus","Genesis","Numbers","Leviticus","Moses & the Exodus","Layperson"),
    ("the parting of the Red Sea","Exodus","Genesis","Joshua","Numbers","Moses & the Exodus","Layperson"),
    ("the giving of the Ten Commandments","Exodus","Leviticus","Deuteronomy","Genesis","Moses & the Exodus","Layperson"),
    ("the golden calf","Exodus","Numbers","Leviticus","Deuteronomy","Moses & the Exodus","Layperson"),
    ("the laws of sacrifice","Leviticus","Exodus","Numbers","Deuteronomy","Laws & Commandments","Deacon"),
    ("the Israelite census","Numbers","Exodus","Deuteronomy","Joshua","Numbers & Genealogies","Deacon"),
    ("Balaam and his donkey","Numbers","Deuteronomy","Judges","Joshua","Miracles","Deacon"),
    ("Moses' final speeches","Deuteronomy","Exodus","Numbers","Joshua","Moses & the Exodus","Deacon"),
    ("the fall of Jericho","Joshua","Judges","1 Samuel","Exodus","Battles & Wars","Layperson"),
    ("the conquest of Canaan","Joshua","Judges","1 Samuel","Numbers","Battles & Wars","Deacon"),
    ("Deborah and Barak","Judges","Joshua","1 Samuel","Ruth","Battles & Wars","Deacon"),
    ("Samson and Delilah","Judges","1 Samuel","2 Samuel","Joshua","Battles & Wars","Layperson"),
    ("Gideon's 300 men","Judges","Joshua","1 Samuel","Numbers","Battles & Wars","Deacon"),
    ("Ruth and Naomi's story","Ruth","Judges","1 Samuel","Esther","Women of the Bible","Layperson"),
    ("Hannah's prayer for a child","1 Samuel","2 Samuel","Judges","Ruth","Women of the Bible","Deacon"),
    ("David and Goliath","1 Samuel","2 Samuel","1 Kings","Judges","Battles & Wars","Layperson"),
    ("David becoming king","2 Samuel","1 Samuel","1 Kings","1 Chronicles","Kings & Kingdoms","Deacon"),
    ("David and Bathsheba","2 Samuel","1 Samuel","1 Kings","Psalms","Kings & Kingdoms","Deacon"),
    ("Solomon building the Temple","1 Kings","2 Kings","2 Chronicles","Ezra","Kings & Kingdoms","Deacon"),
    ("Elijah on Mount Carmel","1 Kings","2 Kings","Isaiah","Judges","Kings & Kingdoms","Deacon"),
    ("Naaman healed of leprosy","2 Kings","1 Kings","Isaiah","Jeremiah","Miracles","Deacon"),
    ("the fall of Jerusalem to Babylon","2 Kings","Jeremiah","Ezekiel","Daniel","Kings & Kingdoms","Deacon"),
    ("the rebuilding of the Temple","Ezra","Nehemiah","Haggai","Zechariah","Kings & Kingdoms","Deacon"),
    ("the rebuilding of Jerusalem's walls","Nehemiah","Ezra","Haggai","Zechariah","Places & Lands","Deacon"),
    ("Esther saving the Jews","Esther","Ruth","Nehemiah","Daniel","Women of the Bible","Layperson"),
    ("Job's suffering","Job","Psalms","Ecclesiastes","Lamentations","Psalms & Proverbs","Deacon"),
    ("the Suffering Servant passage","Isaiah","Jeremiah","Psalms","Zechariah","Prophecy & Fulfillment","Deacon"),
    ("the valley of dry bones","Ezekiel","Daniel","Isaiah","Jeremiah","Dreams & Visions","Deacon"),
    ("Daniel in the lion's den","Daniel","2 Kings","Ezekiel","Judges","Miracles","Layperson"),
    ("the fiery furnace","Daniel","2 Kings","Ezekiel","Isaiah","Miracles","Layperson"),
    ("Jonah and the great fish","Jonah","Amos","Hosea","Micah","Prophets","Layperson"),
    ("the birth of Jesus","Matthew and Luke","Mark and John","Acts","Romans","Life of Jesus","Layperson"),
    ("the Sermon on the Mount","Matthew","Luke","Mark","John","Life of Jesus","Deacon"),
    ("the feeding of the 5,000","All four Gospels","Matthew only","John only","Luke only","Miracles","Deacon"),
    ("the Good Samaritan parable","Luke","Matthew","Mark","John","Parables","Deacon"),
    ("the Prodigal Son parable","Luke","Matthew","Mark","John","Parables","Deacon"),
    ("the raising of Lazarus","John","Luke","Matthew","Mark","Miracles","Deacon"),
    ("the Last Supper","All Synoptics and 1 Corinthians","John only","Acts","Romans","Life of Jesus","Deacon"),
    ("Jesus washing the disciples' feet","John","Luke","Matthew","Mark","Life of Jesus","Deacon"),
    ("the day of Pentecost","Acts","Romans","1 Corinthians","Revelation","The Apostles","Layperson"),
    ("Paul's conversion","Acts","Romans","Galatians","1 Corinthians","Paul & His Letters","Layperson"),
    ("the love chapter","1 Corinthians","Romans","Ephesians","Philippians","Paul & His Letters","Layperson"),
    ("the armor of God","Ephesians","Romans","Colossians","2 Corinthians","Paul & His Letters","Deacon"),
    ("the fruits of the Spirit","Galatians","Romans","Ephesians","Colossians","Paul & His Letters","Deacon"),
    ("the faith chapter (Hall of Faith)","Hebrews","Romans","James","1 Peter","The Apostles","Deacon"),
    ("the New Jerusalem descending","Revelation","Daniel","Isaiah","Ezekiel","Revelation & End Times","Deacon"),
    ("the letters to the seven churches","Revelation","Acts","1 Corinthians","Colossians","Revelation & End Times","Deacon"),
]
for event,book,w1,w2,w3,cat,diff in EVENTS_IN_BOOKS:
    Q(cat, diff, f"In which book of the Bible do we find {event}?", S(book,[w1,w2,w3]), book)

print(f"  After book-location Qs: {len(ALL)}")

# ============================================================================
# "WHICH OF THESE IS NOT..." QUESTIONS
# ============================================================================
NOTS = [
    ("Which of these is NOT one of the 12 apostles?","Barnabas","Peter","James","John","The Apostles","Deacon"),
    ("Which is NOT a plague of Egypt?","Earthquake","Frogs","Locusts","Boils","Moses & the Exodus","Deacon"),
    ("Which is NOT a fruit of the Spirit?","Prosperity","Love","Joy","Patience","Paul & His Letters","Deacon"),
    ("Which is NOT one of Jacob's sons?","Caleb","Reuben","Judah","Benjamin","Numbers & Genealogies","Deacon"),
    ("Which is NOT one of the Ten Commandments?","Tithe 10% of your income","Do not murder","Do not steal","Do not covet","Laws & Commandments","Deacon"),
    ("Which is NOT a book of the Bible?","Jasher (referenced but not canonical)","Obadiah","Philemon","Jude","Numbers & Genealogies","Pastor"),
    ("Which is NOT one of the 7 churches of Revelation?","Corinth","Ephesus","Smyrna","Laodicea","Revelation & End Times","Deacon"),
    ("Which is NOT a Gospel writer?","Paul","Matthew","Mark","Luke","Life of Jesus","Layperson"),
    ("Which is NOT a major prophet?","Amos","Isaiah","Jeremiah","Ezekiel","Prophets","Deacon"),
    ("Which is NOT a son of Noah?","Abraham","Shem","Ham","Japheth","Genesis & Creation","Layperson"),
    ("Which is NOT a parable of Jesus?","The Tale of Two Brothers","The Prodigal Son","The Good Samaritan","The Sower","Parables","Deacon"),
    ("Which is NOT in the Ark of the Covenant?","Moses' sandals","The stone tablets","Aaron's rod","A jar of manna","Moses & the Exodus","Deacon"),
    ("Which is NOT a judge of Israel?","Elijah","Gideon","Deborah","Samson","Battles & Wars","Deacon"),
    ("Which is NOT a gift of the Magi?","Silver","Gold","Frankincense","Myrrh","Life of Jesus","Layperson"),
    ("Which woman is NOT in Jesus' genealogy (Matthew 1)?","Jezebel","Rahab","Ruth","Tamar","Women of the Bible","Pastor"),
    ("Which is NOT a miracle of Elisha?","Parting the Red Sea","Healing Naaman's leprosy","Multiplying oil for a widow","Raising the Shunammite's son","Miracles","Deacon"),
    ("Which is NOT one of the Beatitudes?","Blessed are the wealthy","Blessed are the meek","Blessed are the peacemakers","Blessed are those who mourn","Life of Jesus","Deacon"),
    ("Which is NOT a name/title for Jesus?","The Pharisee","The Lamb of God","The Good Shepherd","The Prince of Peace","Life of Jesus","Deacon"),
    ("Which feast is NOT one of the seven feasts of Leviticus?","Purim","Passover","Pentecost","Tabernacles","Food, Feasts & Offerings","Deacon"),
    ("Which tribe did NOT receive land in Canaan?","Levi","Judah","Ephraim","Benjamin","Numbers & Genealogies","Deacon"),
]
for question,correct,w1,w2,w3,cat,diff in NOTS:
    Q(cat, diff, question, S(correct,[w1,w2,w3]), correct)

print(f"  After NOT-type Qs: {len(ALL)}")

# ============================================================================
# "WHAT HAPPENED NEXT/BEFORE" SEQUENCE QUESTIONS
# ============================================================================
SEQUENCES = [
    ("What happened immediately after Jesus was baptized?","He was led into the wilderness to be tempted","He chose His disciples","He turned water into wine","He preached the Sermon on the Mount","Life of Jesus","Deacon"),
    ("What happened after Peter denied Jesus three times?","He went out and wept bitterly","He was arrested","He joined the disciples","He ran away from Jerusalem","The Apostles","Deacon"),
    ("What happened after Judas betrayed Jesus?","He returned the silver and hanged himself","He fled to Rome","He repented and was forgiven","He became a priest","Life of Jesus","Deacon"),
    ("What happened after the walls of Jericho fell?","The Israelites destroyed the city but spared Rahab","They made peace with Jericho","They rebuilt the walls","They retreated","Battles & Wars","Deacon"),
    ("What happened after David killed Goliath?","Saul took him into his service and Jonathan befriended him","He immediately became king","He returned to shepherding","He went to Egypt","Kings & Kingdoms","Deacon"),
    ("What happened after Solomon died?","The kingdom split into Israel and Judah","The Temple was destroyed","Egypt invaded","The Ark was lost","Kings & Kingdoms","Layperson"),
    ("What happened after Elijah defeated the prophets of Baal?","He fled from Jezebel into the wilderness","He became king","He built a temple","He went to heaven","Kings & Kingdoms","Deacon"),
    ("What happened after Jesus rose from the dead?","He appeared to His disciples for 40 days before ascending","He immediately went to heaven","He went to Rome","He rebuilt the Temple","Life of Jesus","Deacon"),
    ("What happened after Jesus ascended?","The disciples waited in Jerusalem for the Holy Spirit","They immediately went to all nations","They elected a new leader","They returned to fishing","The Apostles","Deacon"),
    ("What happened after Stephen was stoned?","Great persecution scattered believers; Saul approved the killing","The church stopped meeting","Rome intervened","All apostles were killed","The Apostles","Deacon"),
    ("What happened after Paul's vision on the Damascus road?","He was blind for three days until Ananias healed him","He immediately preached","He went to Jerusalem","He returned to Tarsus","Paul & His Letters","Deacon"),
    ("What event preceded the Exodus?","The death of Egypt's firstborn (10th plague)","The parting of the Red Sea","The golden calf","The Ten Commandments","Moses & the Exodus","Layperson"),
    ("What did God do before creating Adam?","He created the heavens, earth, plants, animals, and everything else","He created Eve","He made the Garden","He rested","Genesis & Creation","Layperson"),
    ("What happened right after Adam and Eve ate the forbidden fruit?","They realized they were naked and hid from God","They were immediately expelled","Lightning struck","The serpent died","Genesis & Creation","Layperson"),
    ("What happened after the flood waters receded?","Noah built an altar and offered sacrifices to God","Noah built a city","Noah went to Canaan","Noah planted a vineyard immediately","Genesis & Creation","Deacon"),
]
for question,correct,w1,w2,w3,cat,diff in SEQUENCES:
    Q(cat, diff, question, S(correct,[w1,w2,w3]), correct)

print(f"  After sequence Qs: {len(ALL)}")

# ============================================================================
# TITLES AND NAMES OF GOD / JESUS
# ============================================================================
TITLES = [
    ("What does 'Jehovah Jireh' mean?","The LORD will provide","The LORD is my shepherd","The LORD is peace","The LORD heals","Genesis & Creation","Deacon"),
    ("What does 'Jehovah Rapha' mean?","The LORD who heals","The LORD provides","The LORD is peace","The LORD is there","Miracles","Pastor"),
    ("What does 'Jehovah Nissi' mean?","The LORD is my banner","The LORD provides","The LORD heals","The LORD is peace","Moses & the Exodus","Pastor"),
    ("What does 'Jehovah Shalom' mean?","The LORD is peace","The LORD provides","The LORD heals","The LORD is my banner","Prophets","Pastor"),
    ("What does 'Jehovah Tsidkenu' mean?","The LORD our righteousness","The LORD is there","The LORD provides","The LORD is peace","Prophets","Pastor"),
    ("What title is Jesus given in Isaiah 9:6?","Wonderful Counselor, Mighty God, Everlasting Father, Prince of Peace","King of Kings","Lord of Lords","The Alpha and Omega","Prophecy & Fulfillment","Deacon"),
    ("What does 'Lamb of God' refer to?","Jesus as the ultimate sacrifice for sin","A literal lamb","The Passover lamb only","A title for priests","Life of Jesus","Layperson"),
    ("What does 'Son of Man' mean?","A title Jesus used for Himself, emphasizing His humanity and Daniel 7 fulfillment","A common person","An angel","A prophet","Life of Jesus","Deacon"),
    ("What does 'Son of God' emphasize?","Jesus' divine nature and unique relationship with the Father","His human nature","His priestly role","His kingly role only","Life of Jesus","Deacon"),
    ("What does 'Messiah' mean?","The Anointed One","The Teacher","The Prophet","The Healer","Life of Jesus","Layperson"),
    ("What does 'Lion of Judah' represent?","Jesus as the conquering King from the tribe of Judah","A literal lion","King David","The Temple","Revelation & End Times","Deacon"),
    ("What does 'Alpha and Omega' mean about God?","He is the beginning and the end — eternal","He knows the alphabet","He is the strongest","He is the wisest","Revelation & End Times","Deacon"),
    ("What does 'Emmanuel/Immanuel' mean?","God with us","God saves","God heals","God provides","Prophecy & Fulfillment","Layperson"),
    ("What does 'Elohim' emphasize about God?","His power and majesty (plural of majesty)","His love","His mercy","His anger","Genesis & Creation","Pastor"),
    ("What does 'Adonai' mean?","Lord or Master","Father","Creator","Judge","Moses & the Exodus","Deacon"),
    ("What title did Thomas give Jesus after seeing Him risen?","'My Lord and my God'","'The Teacher'","'The Prophet'","'The King of Israel'","The Apostles","Deacon"),
    ("Jesus is called the 'Bread of Life' in which Gospel?","John","Matthew","Luke","Mark","Life of Jesus","Deacon"),
    ("Jesus is called the 'True Vine' in which Gospel?","John","Matthew","Luke","Mark","Life of Jesus","Deacon"),
    ("What does 'King of Kings' mean?","Jesus is the supreme ruler over all earthly rulers","A Roman title","David's title","Solomon's title","Revelation & End Times","Layperson"),
    ("What does 'High Priest' mean in Hebrews?","Jesus mediates between God and humanity perfectly","Aaron's successor","A Temple official","A Roman priest","The Apostles","Deacon"),
]
for question,correct,w1,w2,w3,cat,diff in TITLES:
    Q(cat, diff, question, S(correct,[w1,w2,w3]), correct)

print(f"  After titles Qs: {len(ALL)}")

# ============================================================================
# MANY MORE PER-CATEGORY HANDWRITTEN QUESTIONS
# ============================================================================

# GENESIS
c="Genesis & Creation"
more=[
    ("Layperson","What did God say after creating the world?","It was very good","It was finished","It was perfect","It was complete"),
    ("Layperson","Why did God send the flood?","The earth was filled with wickedness","To water the land","To create oceans","To punish one family"),
    ("Layperson","What promise did God make to Abraham about his descendants?","They would be as numerous as the stars","They would be wealthy","They would rule Egypt","They would live forever"),
    ("Deacon","Where did Abraham come from originally?","Ur of the Chaldeans","Egypt","Canaan","Babylon"),
    ("Deacon","What test did Abraham face with Isaac?","God asked him to sacrifice his son","God asked him to leave Canaan","God asked him to fight a war","God asked him to fast 40 days"),
    ("Deacon","How did Isaac and Rebekah meet?","Abraham's servant found her at a well","They met at a market","She was from Abraham's family in Canaan","Isaac found her while traveling"),
    ("Pastor","What was the covenant of pieces (Genesis 15)?","God passed between cut animals as a blazing torch, making an unconditional promise","Abraham cut a covenant with Lot","A peace treaty","A wedding ceremony"),
    ("Pastor","What does 'Beersheba' mean and why?","Well of the oath — Abraham and Abimelech swore an oath there","Well of seven — seven wells","Well of beer","Well of God"),
    ("Deacon","What was special about Isaac's birth?","Sarah was 90 years old","He was a twin","He was born in Egypt","He was adopted"),
    ("Deacon","How did Jacob get Esau's blessing?","He disguised himself with goat skins to feel hairy like Esau","He bribed Isaac","He stole a document","He fought Esau for it"),
    ("Pastor","Who was Melchizedek's role?","King of Salem and priest of God Most High","A prophet","A judge","A warrior"),
    ("Layperson","What did God create on the third day?","Dry land, seas, and plants","Animals","Fish and birds","Sun and moon"),
    ("Layperson","What did God create on the fifth day?","Fish and birds","Land animals","Plants","Humans"),
    ("Deacon","How many years did Jacob work for Rachel?","14 (7+7, tricked into marrying Leah first)","7","21","10"),
    ("Pastor","What were the names of Lot's daughters' sons?","Moab and Ben-Ammi (ancestors of Moabites and Ammonites)","Esau and Jacob","Ishmael and Isaac","Reuben and Simeon"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# MOSES
c="Moses & the Exodus"
more=[
    ("Layperson","What was the third plague of Egypt?","Gnats (or lice)","Frogs","Flies","Boils"),
    ("Layperson","What was the fourth plague?","Flies","Frogs","Gnats","Boils"),
    ("Deacon","What was the eighth plague?","Locusts","Hail","Darkness","Death of firstborn"),
    ("Deacon","Which plagues did the Egyptian magicians replicate?","Water to blood and frogs","All of them","None","Only darkness"),
    ("Deacon","What feast was established the night before the Exodus?","Passover","Unleavened Bread only","Tabernacles","Pentecost"),
    ("Layperson","What did the Israelites make from their gold jewelry at Sinai?","A golden calf","A golden ark","A golden altar","A golden crown"),
    ("Deacon","What happened to the two tablets of the Ten Commandments?","Moses smashed them in anger, then God gave new ones","They were placed in the Ark only","They were lost in the desert","They crumbled naturally"),
    ("Deacon","What was the Tabernacle?","A portable tent for worship in the wilderness","A permanent temple","A fort","A storehouse"),
    ("Pastor","Who was Oholiab?","The assistant craftsman of the Tabernacle alongside Bezalel","A Levite singer","A priest","Moses' scribe"),
    ("Deacon","What did the breastplate of the high priest contain?","12 precious stones representing the 12 tribes","7 stones","3 stones","1 large diamond"),
    ("Pastor","What were the dimensions of the Tabernacle courtyard?","100 × 50 cubits","200 × 100 cubits","50 × 50 cubits","150 × 75 cubits"),
    ("Deacon","What was unique about the tribe of Levi?","They served as priests and did not receive a territorial inheritance","They were the largest tribe","They were warriors only","They were exempt from all laws"),
    ("Pastor","What are the five books of Moses called?","The Pentateuch / Torah","The Prophets","The Writings","The Apocrypha"),
    ("Layperson","What happened when the Israelites reached the Red Sea?","They were trapped between the sea and Pharaoh's army","They swam across","They went around it","They built boats"),
    ("Deacon","How did God part the Red Sea?","Through a strong east wind all night, with Moses stretching out his hand","Moses struck the water","An earthquake","An angel pushed the water aside"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# LIFE OF JESUS
c="Life of Jesus"
more=[
    ("Layperson","How did the Magi find Jesus?","They followed a star","An angel told them","They heard from shepherds","They asked at the Temple"),
    ("Layperson","What did angels announce to the shepherds on Christmas night?","The birth of a Savior in Bethlehem","The fall of Rome","A new king in Jerusalem","The coming of Elijah"),
    ("Layperson","Where was baby Jesus laid?","In a manger","In a cradle","On a bed","In a basket"),
    ("Deacon","What happened when Jesus was presented at the Temple as a baby?","Simeon and Anna recognized Him as the Messiah","The priests rejected Him","Nothing unusual","An earthquake occurred"),
    ("Deacon","What is the significance of Jesus being from Nazareth?","A fulfillment of prophecy — 'He shall be called a Nazarene'","It was the capital","It was a priestly city","It was near Jerusalem"),
    ("Deacon","What were the three temptations Satan offered Jesus?","Turn stones to bread, jump from Temple, worship Satan for all kingdoms","Power, wealth, fame","Food, shelter, clothing","Gold, silver, bronze"),
    ("Deacon","Who were the Sadducees?","A Jewish group that denied resurrection and the supernatural","Tax collectors","Roman sympathizers","Desert monks"),
    ("Deacon","What is the Triumphal Entry?","Jesus riding into Jerusalem on a donkey while crowds waved palm branches","Jesus entering the Temple","Jesus' birth","Jesus' ascension"),
    ("Deacon","What did the crowd shout during the Triumphal Entry?","Hosanna! Blessed is He who comes in the name of the Lord!","Crucify Him!","Hail Caesar!","Release Barabbas!"),
    ("Pastor","How many times did Jesus predict His own death?","Three times","Once","Twice","Four times"),
    ("Deacon","Who denied knowing Jesus three times?","Peter","Thomas","John","James"),
    ("Deacon","What did Jesus do in the Garden of Gethsemane?","Prayed in agony — His sweat was like drops of blood","Slept","Taught His disciples","Healed the sick"),
    ("Layperson","Who sentenced Jesus to death?","Pontius Pilate","Herod","Caiaphas","Caesar"),
    ("Deacon","What did Pilate do to symbolize his innocence?","Washed his hands","Tore his robe","Covered his face","Left the room"),
    ("Layperson","What was placed on Jesus' head before crucifixion?","A crown of thorns","A golden crown","A helmet","A blindfold"),
    ("Deacon","What happened at the moment Jesus died?","The Temple curtain tore in two from top to bottom","An earthquake only","Nothing visible","The sky turned red"),
    ("Deacon","Who buried Jesus?","Joseph of Arimathea (with Nicodemus)","Peter and John","Mary Magdalene","The Roman soldiers"),
    ("Layperson","How did the disciples know Jesus had risen?","The tomb was empty and angels declared He had risen","A letter arrived","Peter had a dream","The priests announced it"),
    ("Deacon","What did Jesus say to Thomas after the resurrection?","'Put your finger here and see my hands... do not be faithless'","'Go and sin no more'","'Feed my sheep'","'Follow me'"),
    ("Layperson","What did Jesus do just before ascending to heaven?","Gave the Great Commission — 'Go and make disciples of all nations'","Healed a blind man","Built a church","Appointed Peter as pope"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# KINGS
c="Kings & Kingdoms"
more=[
    ("Layperson","What was David before he became king?","A shepherd","A soldier","A priest","A carpenter"),
    ("Deacon","How was David anointed by Samuel?","Privately, as the youngest of Jesse's sons","In the Temple before all Israel","On the battlefield","At Saul's palace"),
    ("Deacon","What was David's relationship with Saul?","Saul was jealous and tried to kill David","They were allies always","Saul mentored David","They never met"),
    ("Deacon","How did Saul die?","He fell on his own sword in battle","David killed him","The Philistines beheaded him in battle","He died of disease"),
    ("Deacon","What did Solomon ask God for?","Wisdom to govern the people","Wealth","Long life","Victory over enemies"),
    ("Deacon","How did God respond to Solomon's request?","He gave him wisdom AND wealth and honor","He gave only wisdom","He refused","He tested him first"),
    ("Deacon","What did Solomon do later in life that displeased God?","Married foreign wives who turned his heart to idols","Rebuilt the Tower of Babel","Made war on Egypt","Abandoned the Temple"),
    ("Deacon","What did Rehoboam say that caused the split?","'My father made your yoke heavy; I will add to it'","'I will be a merciful king'","'Follow me to war'","'I will lower taxes'"),
    ("Pastor","Who was the prophet Ahijah?","He prophesied the kingdom would split and gave Jeroboam 10 pieces of a cloak","A priest of Baal","David's seer","Solomon's advisor"),
    ("Deacon","What was King Asa known for?","Religious reform and removing idols from Judah","Building a new Temple","Conquering Babylon","Marrying Jezebel"),
    ("Deacon","What was King Jehoshaphat known for?","Appointing judges and seeking God before battles","Idolatry","Cruelty","Wealth only"),
    ("Pastor","What did Manasseh do during his 55-year reign?","Practiced extreme idolatry including child sacrifice","Rebuilt the Temple","Led Israel to victory","Was a righteous king"),
    ("Pastor","What happened to Manasseh later?","He was captured by Assyria, repented, and was restored","He was killed","He fled to Egypt","He never changed"),
    ("Deacon","Who was the boy king hidden from Athaliah?","Joash","Josiah","Asa","Hezekiah"),
    ("Deacon","What king built a water tunnel to prepare for Assyria?","Hezekiah","Josiah","Asa","Jehoshaphat"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# APOSTLES
c="The Apostles"
more=[
    ("Layperson","What did Jesus promise to send after He left?","The Holy Spirit","An angel","A prophet","A new leader"),
    ("Layperson","What languages did the apostles speak at Pentecost?","Languages of all the nations present","Only Hebrew","Only Greek","Only Aramaic"),
    ("Deacon","Who was the first to preach to Gentiles?","Peter (to Cornelius)","Paul","Philip","James"),
    ("Deacon","What was the result of Peter's sermon at Pentecost?","About 3,000 people were saved","100 people","The crowd dispersed","The priests believed"),
    ("Deacon","What did the early church share?","Everything — they had all things in common","Only bread","Only prayers","Only songs"),
    ("Deacon","Who were the first deacons?","The Seven in Acts 6, chosen to serve tables","The twelve apostles","Paul's companions","The elders of Judea"),
    ("Deacon","What was Stephen known for besides being the first martyr?","Being full of the Holy Spirit and performing great signs","Being the first elder","Writing letters","Healing diseases"),
    ("Pastor","What did Stephen see as he was being stoned?","Heaven opened and Jesus standing at God's right hand","An angel with a sword","A bright light","Nothing — he closed his eyes"),
    ("Deacon","What was the Ethiopian eunuch reading?","The book of Isaiah","The Psalms","The Torah","Proverbs"),
    ("Deacon","Who baptized the Ethiopian eunuch?","Philip","Peter","Paul","Stephen"),
    ("Deacon","What was Peter's response when Cornelius bowed to him?","'Stand up; I myself am also a man'","He accepted the worship","He ignored it","He blessed him"),
    ("Pastor","Who was Demas?","A co-worker who deserted Paul, 'having loved this present world'","A faithful companion","A church elder","A Roman convert"),
    ("Pastor","Who was Mark (John Mark)?","Barnabas' cousin, author of the Gospel of Mark, traveled with Paul briefly","Paul's brother","Peter's son","A Roman official"),
    ("Deacon","What dispute caused Paul and Barnabas to separate?","Whether to take John Mark on their next journey","Theology","Money","Where to travel"),
    ("Deacon","How did the apostles perform signs and wonders?","Through the power of the Holy Spirit in Jesus' name","Through magic","Through special training","Through fasting only"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# PAUL
c="Paul & His Letters"
more=[
    ("Layperson","How did Paul become a Christian?","Jesus appeared to him in a blinding light on the road to Damascus","He heard Peter preach","He read the Scriptures","He was born a Christian"),
    ("Deacon","What did Paul do before his conversion?","Persecuted Christians — he held coats at Stephen's stoning","He was a fisherman","He was a tax collector","He was a soldier"),
    ("Deacon","What is 'justification' in Romans?","Being declared righteous by God through faith in Christ","Earning salvation","Becoming sinless","Following the Law perfectly"),
    ("Deacon","What does Romans 8:28 teach?","All things work together for good for those who love God","Life is random","God only helps the righteous","Suffering is punishment"),
    ("Pastor","What is the 'mystery' Paul speaks of in Ephesians?","Gentiles are fellow heirs with Jews in Christ","A secret code","The date of Jesus' return","The identity of the Antichrist"),
    ("Deacon","What did Paul write about headcoverings?","He discussed it in 1 Corinthians 11 regarding order in worship","He never mentioned it","He forbade them","He required them for all"),
    ("Deacon","What is Paul's teaching on spiritual gifts?","Different gifts given by one Spirit for the common good (1 Cor 12)","Everyone has the same gifts","Gifts are earned","Only apostles have gifts"),
    ("Pastor","What is the 'rapture' referenced in Paul's letters?","Believers caught up to meet the Lord in the air (1 Thessalonians 4)","A feeling of joy","A type of prayer","An earthquake"),
    ("Deacon","What is Paul's teaching on grace in Ephesians 2:8-9?","Saved by grace through faith, not by works — it is a gift of God","Saved by keeping the Law","Saved by good deeds","Saved by baptism only"),
    ("Deacon","What letter discusses the role of elders and deacons?","1 Timothy","Romans","Galatians","Philippians"),
    ("Pastor","Who was Titus?","Paul's companion sent to organize the church in Crete","A Roman emperor","A Jewish priest","An Ethiopian convert"),
    ("Deacon","What is the 'body of Christ' metaphor?","The church — many parts, one body, each person with a role","A literal body","The communion bread","Jesus' physical body only"),
    ("Pastor","What did Paul mean by 'dying daily'?","Daily surrendering his life and desires to follow Christ","Literal physical suffering","A prayer practice","Fasting every day"),
    ("Deacon","Where did Paul give his farewell speech to the Ephesian elders?","Miletus","Ephesus","Athens","Corinth"),
    ("Pastor","What is the 'kenosis' in Philippians 2?","Christ emptied Himself / set aside divine privileges to become human","A type of offering","A prayer","A Jewish festival"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# More for smaller categories
# PARABLES
c="Parables"
more=[
    ("Layperson","In the parable of the Good Samaritan, who helped the wounded man?","A Samaritan","A priest","A Levite","A Pharisee"),
    ("Layperson","In the parable of the Prodigal Son, what did the father do when his son returned?","Ran to meet him, embraced him, and threw a feast","Turned him away","Made him work as a servant","Ignored him"),
    ("Deacon","Who was angry when the Prodigal Son returned?","The older brother","The father","A servant","A neighbor"),
    ("Deacon","In the parable of the Talents, what happened to the servant who buried his talent?","He was punished and his talent given to the one with ten","He was forgiven","He was praised for caution","He was given another chance"),
    ("Deacon","What did the wise builder build his house on?","Rock","Sand","Clay","Wood"),
    ("Deacon","What happened to the foolish builder's house?","It fell when storms came because it was on sand","It was robbed","It burned down","It was taken by the king"),
    ("Layperson","In the parable of the Lost Sheep, how many sheep did the shepherd have?","100","50","12","1,000"),
    ("Layperson","How many sheep were lost?","1","10","50","7"),
    ("Deacon","In the parable of the Sower, what do the thorns represent?","Worries of life and deceitfulness of wealth that choke the word","Rocky ground","The devil","Good soil"),
    ("Deacon","What does the good soil represent in the Sower?","A person who hears, understands, and produces fruit","A rich person","A priest","A farmer"),
    ("Pastor","What is the lesson of the Unjust Steward (Shrewd Manager)?","Use worldly resources wisely to build eternal relationships","Steal from the rich","Be dishonest if necessary","Money is evil"),
    ("Deacon","In the Parable of the Net (Dragnet), what does the net represent?","God's kingdom gathering all kinds — sorted at the end","A fishing business","The church only","The Temple"),
    ("Deacon","What do the ten virgins represent?","Believers waiting for Christ — five prepared, five not","Ten nations","Ten commandments","Ten tribes"),
    ("Deacon","What lesson does the Rich Man and Lazarus teach?","Our choices in life have eternal consequences; help the poor","Rich people go to hell","Poor people go to heaven","Money is sin"),
    ("Pastor","Why did Jesus teach in parables?","So those seeking truth would understand, but the disinterested would not","To entertain","To confuse everyone","Because He liked stories"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# PSALMS & PROVERBS more
c="Psalms & Proverbs"
more=[
    ("Layperson","What does Psalm 23 say about walking through the valley of death?","'I will fear no evil, for you are with me'","'I will turn back'","'I will call for help'","'I will run away'"),
    ("Deacon","What is Psalm 119 about?","The beauty and power of God's word/law — the longest psalm and chapter","King David's battles","The creation story","A prophecy of Jesus"),
    ("Deacon","What does 'The fear of the LORD is the beginning of knowledge' mean?","Reverence for God is the foundation of all true wisdom","Be literally afraid of God","God punishes the ignorant","Knowledge comes from suffering"),
    ("Deacon","What does Proverbs say about 'spare the rod'?","'Spare the rod, spoil the child' — discipline is necessary","Never discipline children","Use only praise","Physical punishment is wrong"),
    ("Deacon","What is the 'vanity' Ecclesiastes talks about?","The meaninglessness of pursuing worldly things apart from God","Mirrors","Self-obsession","Wealth specifically"),
    ("Pastor","What is a 'lament psalm'?","A psalm expressing grief, complaint, or sorrow to God","A happy psalm","A psalm of praise","A psalm for festivals"),
    ("Deacon","What Psalm was Jesus quoting when He said 'My God, why have you forsaken me?'","Psalm 22","Psalm 23","Psalm 1","Psalm 51"),
    ("Deacon","What does Psalm 46 say?","'God is our refuge and strength, an ever-present help in trouble'","'The Lord is my shepherd'","'Praise the Lord'","'Create in me a clean heart'"),
    ("Pastor","What is wisdom personified as in Proverbs?","A woman calling out in the streets","A king","A prophet","A priest"),
    ("Deacon","What does Proverbs warn about repeatedly?","The dangers of adultery, laziness, and foolish speech","Only money","Only food","Only travel"),
    ("Layperson","What is the shortest psalm?","Psalm 117 (2 verses)","Psalm 1","Psalm 23","Psalm 150"),
    ("Deacon","What Psalm says 'The fool says in his heart, there is no God'?","Psalm 14 (and Psalm 53)","Psalm 23","Psalm 1","Psalm 119"),
    ("Deacon","Who wrote Psalm 73 about the prosperity of the wicked?","Asaph","David","Solomon","Moses"),
    ("Pastor","What is the 'Sons of Korah'?","A group of Levite musicians who wrote several psalms","Korah's rebellious followers","Egyptian singers","Babylonian poets"),
    ("Layperson","What Psalm begins 'Make a joyful noise to the Lord'?","Psalm 100","Psalm 23","Psalm 1","Psalm 150"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# WOMEN more
c="Women of the Bible"
more=[
    ("Layperson","Who was Moses' older sister?","Miriam","Deborah","Zipporah","Jochebed"),
    ("Deacon","What did Miriam do after crossing the Red Sea?","Led the women in singing and dancing with tambourines","Wept","Complained","Offered a sacrifice"),
    ("Deacon","Why was Bathsheba controversial?","David committed adultery with her while she was Uriah's wife","She was a foreigner","She worshiped idols","She betrayed Israel"),
    ("Deacon","What clever plan did Esther use?","She invited the king and Haman to two banquets before revealing Haman's plot","She fled the palace","She wrote a letter","She gathered an army"),
    ("Deacon","What happened to Haman in the book of Esther?","He was hanged on the gallows he built for Mordecai","He was exiled","He was forgiven","He became king"),
    ("Pastor","Who was Tamar in 2 Samuel?","David's daughter who was violated by her half-brother Amnon","Judah's daughter-in-law","A Canaanite queen","A prophetess"),
    ("Deacon","Who was the Samaritan woman Jesus met at a well?","A woman with five past husbands whom Jesus offered 'living water'","A disciple","A prophetess","A Roman woman"),
    ("Deacon","What did Mary pour on Jesus' feet?","Very expensive perfume (nard/spikenard)","Water","Oil","Wine"),
    ("Pastor","Who was Sapphira?","Ananias' wife who lied about the price of land and died","A faithful deaconess","Peter's wife","Paul's co-worker"),
    ("Deacon","What did Elizabeth say when Mary visited her?","'Blessed are you among women, and blessed is the child you bear'","'Welcome to my home'","'Tell me everything'","'Praise the Lord'"),
    ("Deacon","Who was Rizpah?","Saul's concubine who guarded her sons' bodies from vultures","David's wife","A prophetess","A judge"),
    ("Pastor","Who was Achsah?","Caleb's daughter who asked for springs of water as her inheritance","Joshua's wife","A Moabite queen","A midwife"),
    ("Layperson","Who was Ruth's mother-in-law?","Naomi","Hannah","Sarah","Orpah"),
    ("Deacon","Who was Orpah?","Ruth's sister-in-law who turned back to Moab","Ruth's mother","Naomi's sister","A servant"),
    ("Deacon","Who was Lois?","Timothy's grandmother, a woman of faith","Paul's mother","A prophetess","Peter's wife"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# PLACES
c="Places & Lands"
more=[
    ("Layperson","What city is called the 'City of David'?","Bethlehem (also Jerusalem/Zion)","Nazareth","Jericho","Hebron"),
    ("Deacon","What is the significance of the Mount of Olives?","Jesus prayed, was arrested, ascended, and will return there","Moses received the law","The Temple was built there","David was anointed there"),
    ("Deacon","Where was Paul when he wrote to the Romans?","Corinth","Rome","Ephesus","Athens"),
    ("Deacon","What was Tarsus?","Paul's birthplace — a major city in Cilicia","A port in Greece","A Roman military camp","A Jewish settlement"),
    ("Deacon","Where is modern-day Ur?","Southern Iraq","Turkey","Egypt","Israel"),
    ("Pastor","Where was the Garden of Eden said to be?","Between the Tigris and Euphrates rivers (Mesopotamia)","In Israel","In Africa","In Egypt"),
    ("Deacon","What was Samaria's significance in Jesus' time?","A region Jews avoided due to historic enmity with Samaritans","The capital of Judah","A Roman city","A Philistine territory"),
    ("Deacon","Why did Jesus go through Samaria in John 4?","To meet the Samaritan woman and offer salvation to Samaritans too","It was the only route","He was lost","He was fleeing"),
    ("Deacon","Where did Peter have his rooftop vision?","Joppa","Caesarea","Jerusalem","Antioch"),
    ("Pastor","Where was Lystra?","A city in modern Turkey where Paul was stoned and left for dead","A port in Greece","An island","A city in Egypt"),
    ("Deacon","Where was Jesus tempted by Satan?","The Judean wilderness","The Temple","Mount Sinai","The Garden of Eden"),
    ("Layperson","What country did the Israelites escape from?","Egypt","Babylon","Assyria","Persia"),
    ("Deacon","What was Caesarea Maritima?","A Roman port city where many NT events occurred — Paul was imprisoned","David's capital","A desert oasis","A mountain fortress"),
    ("Pastor","Where was Derbe?","A city in Asia Minor (Turkey) Paul visited on missionary journeys","An island","A city in Egypt","A city in Greece"),
    ("Deacon","What is significant about the city of Capernaum?","Jesus called it 'His own city' and performed many miracles there","It was where Jesus was born","It was the capital of Judah","It was where Paul was converted"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# NUMBERS more
c="Numbers & Genealogies"
more=[
    ("Layperson","How many disciples did Jesus send out in Luke 10?","70 (or 72)","12","7","40"),
    ("Deacon","How many books did Moses write (traditional view)?","5","3","7","10"),
    ("Deacon","How many deacons were chosen in Acts 6?","7","12","5","3"),
    ("Deacon","How many missionary journeys did Paul make?","3 (plus the voyage to Rome)","2","4","5"),
    ("Pastor","What is the significance of the number 3 in the Bible?","Divine completeness — Trinity, resurrection on 3rd day","Nothing special","Bad luck","Perfection"),
    ("Pastor","What is the significance of the number 6?","The number of man — falling short of 7 (perfection)","Holiness","Completeness","Joy"),
    ("Deacon","How many sons did David have (named in Scripture)?","At least 19","12","7","3"),
    ("Deacon","How many Psalms are attributed to David?","About 73","All 150","50","100"),
    ("Deacon","How many brothers did Jesus have (named)?","4 — James, Joseph, Simon, Judas","2","None","7"),
    ("Pastor","How many times is the word 'trinity' used in the Bible?","Zero — the concept is there but not the word","Once","Three","Seven"),
    ("Deacon","How old was Noah when the flood ended?","601","600","650","700"),
    ("Deacon","How many years did the Babylonian exile last?","70","40","50","100"),
    ("Pastor","How many chapters are in the book of Isaiah?","66","40","50","100"),
    ("Deacon","How many Psalms are there?","150","100","120","200"),
    ("Pastor","How many kings ruled the united kingdom of Israel?","3 — Saul, David, Solomon","5","2","7"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# FOOD more
c="Food, Feasts & Offerings"
more=[
    ("Layperson","What did God provide along with manna in the wilderness?","Quail","Fish","Lamb","Figs"),
    ("Deacon","What does 'manna' literally mean?","'What is it?'","'Bread from heaven'","'God's food'","'White flakes'"),
    ("Deacon","What is the 'bread of the Presence'?","12 loaves placed weekly in the Tabernacle before God","Communion bread","Passover bread","Wedding bread"),
    ("Deacon","Who ate the bread of the Presence when he was hungry?","David (and his men)","Moses","Elijah","Jesus"),
    ("Deacon","What is the 'forbidden food' Adam and Eve ate?","Fruit from the Tree of Knowledge of Good and Evil — type unspecified","An apple specifically","A fig","A pomegranate"),
    ("Pastor","What are the kosher rules for fish?","Must have fins and scales","Any fish is kosher","Only freshwater fish","Only large fish"),
    ("Deacon","What did Jesus say is the true bread from heaven?","Himself — 'I am the bread of life'","Manna","The Torah","Prayer"),
    ("Deacon","What feast involves fasting and repentance?","Yom Kippur (Day of Atonement)","Passover","Tabernacles","Purim"),
    ("Pastor","What happened during the Feast of Tabernacles in John 7?","Jesus stood and cried out 'If anyone thirsts, let him come to me'","He fed 5,000","He was arrested","He healed a blind man"),
    ("Deacon","What foods are considered unclean in Leviticus?","Pork, shellfish, certain birds, and animals that don't chew cud/split hooves","Only pork","Nothing — all food was clean","Only meat"),
    ("Layperson","What did Jesus compare the kingdom of heaven to regarding yeast?","Leaven that spreads through the whole batch of dough","Bread without leaven","A loaf of bread","A grain of wheat"),
    ("Pastor","What is the 'Agape feast'?","An early Christian communal meal associated with communion","A Jewish feast","A Roman festival","A harvest celebration"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# BATTLES more
c="Battles & Wars"
more=[
    ("Deacon","Who was the first king of Israel to die in battle?","Saul","David","Ahab","Josiah"),
    ("Deacon","What king of Judah died at the Battle of Megiddo?","Josiah","Hezekiah","Asa","Manasseh"),
    ("Deacon","Who fought the Amalekites while Moses held up his arms?","Joshua","Caleb","Aaron","Hur"),
    ("Layperson","Who did Samson love that led to his downfall?","Delilah","Jezebel","Bathsheba","Ruth"),
    ("Deacon","What was the secret of Samson's strength?","His hair was never cut — a sign of his Nazirite vow","His diet","His prayers","His armor"),
    ("Deacon","How did the Philistines defeat Samson?","Delilah lured him, shaved his head, and they captured him","In open battle","By poisoning him","By ambush at night"),
    ("Deacon","How did Samson die?","He pushed apart the pillars of the Philistine temple, killing himself and thousands","In battle","Of old age","Executed by a sword"),
    ("Pastor","What was Jephthah's tragic vow?","He vowed to sacrifice whatever came out of his house first — his daughter came out","To fast for a year","To give all his wealth","To serve as priest"),
    ("Pastor","Who was Shamgar?","A judge who killed 600 Philistines with an oxgoad","A king of Moab","A prophet","A priest"),
    ("Deacon","What role did Rahab play in the battle of Jericho?","She hid the Israelite spies and was spared","She led the attack","She provided weapons","She betrayed the Israelites"),
    ("Deacon","What sign did Rahab hang from her window?","A scarlet cord","A white flag","A blue banner","A lamp"),
    ("Layperson","What did Jonathan and his armor bearer do at Michmash?","Attacked a Philistine garrison — just two of them","Spied on the enemy","Built a fort","Retreated"),
    ("Pastor","Who was Abner?","Saul's army commander who later supported David","David's advisor","A Philistine general","A prophet"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# PROPHECY more
c="Prophecy & Fulfillment"
more=[
    ("Layperson","What did the prophets predict about the Messiah?","He would be born in Bethlehem, suffer, die, and rise again","He would be a military leader only","He would come from Rome","He would rebuild the Temple"),
    ("Deacon","What does Isaiah 7:14 prophesy?","A virgin would conceive and bear a son named Immanuel","The Temple would be rebuilt","Israel would conquer Babylon","The world would end"),
    ("Deacon","How was Zechariah 9:9 fulfilled?","Jesus entered Jerusalem riding on a donkey","Jesus was born in a stable","Jesus walked on water","Jesus ascended to heaven"),
    ("Pastor","What prophet foretold the Messiah would be born of a virgin AND suffer?","Isaiah (chapters 7 and 53)","Jeremiah","Zechariah","Malachi"),
    ("Pastor","How does Psalm 69 relate to Jesus?","It prophesied 'zeal for your house will consume me' — fulfilled when Jesus cleansed the Temple","It predicts the resurrection","It describes the nativity","It foretells the ascension"),
    ("Deacon","What does 'Suffering Servant' refer to?","The Messiah who would bear the sins of humanity — fulfilled in Jesus","A human priest","A literal servant of a king","Moses"),
    ("Pastor","How many pieces of silver were prophesied?","30 — Zechariah 11:12-13, fulfilled in Judas' betrayal","20","40","50"),
    ("Pastor","What did Zechariah prophesy about the Potter's Field?","The 30 pieces would be thrown in the Temple and used to buy a potter's field","A field of wheat","A vineyard","A garden"),
    ("Deacon","What did Malachi prophesy about the coming of the Lord?","'I will send my messenger who will prepare the way' — fulfilled by John the Baptist","The Temple would be enlarged","Rain would come","A new king would rise"),
    ("Deacon","How was Hosea 11:1 fulfilled?","'Out of Egypt I called my son' — Jesus' family fled to and returned from Egypt","Israel left Egypt","Moses was born","Joseph went to Egypt"),
    ("Pastor","What does the 'Root of Jesse' prophecy mean?","The Messiah would come from Jesse's family line — David's father","A literal plant","A new kind of tree","Jesse would return to life"),
    ("Deacon","What did prophets say about the Messiah's betrayal?","He would be betrayed by a friend — Psalm 41:9, fulfilled by Judas","He would never be betrayed","His enemies would betray Him","A stranger would betray Him"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# DREAMS more
c="Dreams & Visions"
more=[
    ("Layperson","What did the wise men see that led them to Jesus?","A star","An angel","A dream only","A scroll"),
    ("Deacon","What did Isaiah see in his vision in Isaiah 6?","God on a high throne with seraphim crying 'Holy, holy, holy'","A valley of bones","Four beasts","A burning bush"),
    ("Deacon","What did Isaiah say when he saw God?","'Woe is me! I am undone, for I am a man of unclean lips'","'Here am I, send me' (that came after)","'How long, O Lord?'","'Praise the Lord'"),
    ("Pastor","What are the four living creatures in Ezekiel's vision?","Each had four faces — man, lion, ox, eagle — and four wings","Four horses","Four angels","Four demons"),
    ("Deacon","What did the handwriting on the wall at Belshazzar's feast predict?","The fall of Babylon that very night","A great victory","Seven years of plenty","Peace with Persia"),
    ("Pastor","What is the 'abomination of desolation' prophesied by Daniel?","A desecration of the Temple — historically by Antiochus and possibly future","A natural disaster","An earthquake","A flood"),
    ("Deacon","What vision did John have of heaven in Revelation 4?","A throne with God seated, surrounded by 24 elders and four living creatures","A garden","A battle","A wedding"),
    ("Deacon","What is the significance of John's vision of the New Jerusalem?","God will dwell with humanity — no more tears, death, or pain","A new earthly city","A rebuilt Temple","A political kingdom"),
    ("Layperson","What did an angel tell Joseph in a dream (Matthew 2)?","To flee to Egypt with Mary and Jesus because Herod wanted to kill the child","To go to Bethlehem","To name the child John","To stay in Nazareth"),
    ("Pastor","What did Zechariah see in his vision of the menorah?","A golden lampstand with two olive trees — symbolizing God's Spirit","A burning bush","A valley of bones","Four horsemen"),
    ("Deacon","What did God show Abraham in a vision in Genesis 15?","His descendants would be enslaved for 400 years but then freed","Immediate possession of Canaan","Wealth beyond measure","A son within one year"),
    ("Deacon","What did Gideon's enemy dream about?","A barley loaf rolling into camp and destroying a tent — symbolizing Gideon's victory","A great flood","A fire","An earthquake"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# MIRACLES more
c="Miracles"
more=[
    ("Layperson","What miracle did Jesus perform at a wedding?","Turned water into wine","Healed the bride","Fed all the guests","Raised someone from the dead"),
    ("Layperson","How did Jesus walk on water?","Through divine power — He is God","He used a raft","It was shallow","It was frozen"),
    ("Deacon","What happened when Jesus healed the paralytic lowered through the roof?","He first said 'Your sins are forgiven,' then healed him","He only healed him","He told him to go to the Temple","He prayed for three days"),
    ("Deacon","Why were the Pharisees upset when Jesus healed on the Sabbath?","They considered healing 'work' that violated Sabbath rules","They didn't believe in miracles","They were jealous of His popularity","They thought He used magic"),
    ("Deacon","What miracle involved 12 baskets of leftovers?","The feeding of the 5,000","The feeding of the 4,000","The Last Supper","The wedding at Cana"),
    ("Deacon","What miracle involved 7 baskets of leftovers?","The feeding of the 4,000","The feeding of the 5,000","The Last Supper","The wedding at Cana"),
    ("Deacon","What did the Centurion say to Jesus that amazed Him?","'Just say the word and my servant will be healed'","'Come to my house'","'Are you the Messiah?'","'I believe in you'"),
    ("Layperson","What did Jesus say to the dead Lazarus?","'Lazarus, come out!'","'Rise and walk'","'Be healed'","'Go in peace'"),
    ("Deacon","How long had Lazarus been dead?","4 days","1 day","7 days","3 days"),
    ("Deacon","What did the widow of Zarephath's flour and oil do?","They never ran out until the drought ended — Elijah's miracle","They turned to gold","They multiplied into a feast","They healed her son"),
    ("Pastor","What miracle did Elisha perform with poisoned stew?","He added flour and made it safe to eat","He prayed and it turned to wine","He threw it out","He healed those who ate it"),
    ("Pastor","What miracle involved an ax head?","Elisha made a borrowed ax head float on water","Elisha split a rock","Elisha cut down a tree miraculously","Moses struck a rock"),
    ("Layperson","What happened to the three men in the fiery furnace?","They were unharmed and a fourth figure appeared with them","They were burned","They prayed and the fire stopped","They escaped before the fire started"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# PROPHETS more
c="Prophets"
more=[
    ("Layperson","What did Jonah do instead of going to Nineveh?","Boarded a ship to Tarshish — running the opposite direction","He went to Jerusalem","He hid in a cave","He built an altar"),
    ("Layperson","What happened to Jonah on the ship?","A great storm came and he was thrown overboard","The ship sank","He fell asleep","Pirates attacked"),
    ("Deacon","What did Jonah do after Nineveh repented?","He was angry that God spared the city","He celebrated","He stayed and taught","He built a temple"),
    ("Deacon","What did God use to teach Jonah about mercy?","A plant that grew and then withered — showing God's concern for Nineveh","A dream","An angel","A scroll"),
    ("Deacon","What was Amos' background before becoming a prophet?","He was a shepherd and fig tree farmer from Tekoa","He was a priest","He was a king's son","He was a scribe"),
    ("Deacon","What did Amos preach about?","Social justice — God's judgment on nations that oppress the poor","Only future events","Only comfort","Military strategy"),
    ("Deacon","What did Daniel refuse to eat?","The king's food and wine — he ate only vegetables and water","Bread","Meat","Fish"),
    ("Deacon","How did Daniel's health compare to those who ate the king's food?","He looked healthier and stronger after 10 days","He looked weaker","No difference","He got sick"),
    ("Pastor","What is the seventy 'weeks' prophecy of Daniel 9?","490 years (70 × 7) from a decree to rebuild Jerusalem until the Messiah","70 literal weeks","70 months","A symbolic number"),
    ("Deacon","What did God tell Hosea to do?","Marry a prostitute named Gomer to illustrate God's love for unfaithful Israel","Build a temple","Fast for 40 days","Preach in Nineveh"),
    ("Deacon","What is the 'day of the LORD' that Joel describes?","A day of judgment and restoration when God intervenes dramatically","A regular Sabbath","The end of the world only","A harvest festival"),
    ("Pastor","What did Ezekiel eat in his vision?","A scroll — it tasted sweet like honey","Bread","A fruit","Manna"),
    ("Deacon","Why is Jeremiah called the 'weeping prophet'?","He wept over Jerusalem's coming destruction and the people's stubbornness","He cried at his calling","He was always sad","He wrote Lamentations only"),
    ("Pastor","What is the 'new covenant' Jeremiah spoke of?","God would write His law on hearts, not stone — fulfilled in Christ","A new set of rules","A new Temple","A new priesthood"),
    ("Deacon","What vision did Ezekiel have of God's glory leaving the Temple?","God's glory departed eastward, symbolizing His withdrawal from Israel","God's glory entered the Temple","A pillar of fire","A cloud descended"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# REVELATION more
c="Revelation & End Times"
more=[
    ("Deacon","What is the 'rapture'?","Believers caught up to meet Christ — referenced in 1 Thessalonians 4","A type of worship","A Jewish festival","An earthquake"),
    ("Deacon","What is the '1,000-year reign' of Christ?","The Millennium — Christ reigning on earth described in Revelation 20","An exact date","Heaven","A metaphor for eternity"),
    ("Pastor","What are the three main views of the Millennium?","Premillennialism, Amillennialism, Postmillennialism","Pre-trib, Mid-trib, Post-trib","Past, Present, Future","Literal, Symbolic, Allegorical"),
    ("Deacon","What are the 'bowls of wrath'?","Seven final plagues of God's judgment in Revelation 16","Communion cups","Offerings","Temple furniture"),
    ("Deacon","What is the 'marriage supper of the Lamb'?","The celebration of Christ's union with His church in heaven","A Last Supper repeat","A Jewish wedding","A feast in the Temple"),
    ("Pastor","What does the 'woman clothed with the sun' in Revelation 12 represent?","Israel (or the church) — the mother of the Messiah","Mary literally","An angel","The moon goddess"),
    ("Deacon","What is the 'second death' in Revelation?","The lake of fire — eternal separation from God","Physical death","Spiritual sleep","Reincarnation"),
    ("Pastor","What is the meaning of the white stone in Revelation 2?","A symbol of acquittal, new identity, or intimate knowledge from Christ","A building block","A weapon","A counting device"),
    ("Deacon","What does the phrase 'Behold, I stand at the door and knock' mean?","Jesus inviting people (or the Laodicean church) to open their hearts","A literal door","The gate of heaven","The Temple door"),
    ("Deacon","What happens to Satan at the end of Revelation?","He is thrown into the lake of fire forever","He is forgiven","He is imprisoned","He escapes"),
    ("Pastor","What does the number 144,000 represent?","12 tribes × 12,000 — either literal Israelites or symbolic of all believers","An army","Angels","Martyrs only"),
    ("Deacon","What is 'the great white throne judgment'?","The final judgment where all are judged by what is written in the books","A heavenly court","An angel's throne","A new government"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# ANGELS more
c="Angels & Demons"
more=[
    ("Deacon","What did Satan tempt Jesus with on the mountain?","All the kingdoms of the world if Jesus would worship him","Wealth","Food","A throne in heaven"),
    ("Deacon","What was Jesus' reply to Satan's temptation of worship?","'Worship the Lord your God and serve Him only'","'I will not'","'Get behind me'","'You are a liar'"),
    ("Deacon","What did Satan quote to Jesus during the temptation?","Scripture — 'He will command His angels concerning you'","A pagan poem","A Roman law","A prophecy of Daniel"),
    ("Pastor","What is 'binding the strong man' in Jesus' teaching?","Before plundering Satan's domain, one must first bind Satan","A literal rope","A type of exorcism","A Jewish custom"),
    ("Deacon","What did Jesus say He saw when the 70 returned?","'I saw Satan fall like lightning from heaven'","'I saw angels singing'","'I saw the Temple rebuilt'","'I saw the kingdom come'"),
    ("Pastor","What is the role of the 'accuser' (Satan)?","He accuses believers before God — Job 1, Zechariah 3, Revelation 12","He tempts only","He destroys only","He rules earth"),
    ("Deacon","What did the angel do for Elijah when he was depressed?","Brought him food and water and let him rest","Healed his body","Gave him a sword","Took him to heaven"),
    ("Layperson","Do angels have wings in the Bible?","Some do (seraphim, cherubim) but others appear as ordinary men","All angels have wings","No angels have wings","Only Gabriel has wings"),
    ("Pastor","What is a 'guardian angel'?","A concept derived from Matthew 18:10 and Hebrews 1:14 — angels assigned to protect","A fictional idea","An Old Testament role","A title for Gabriel"),
    ("Deacon","What angel appeared to Zechariah (John the Baptist's father)?","Gabriel","Michael","Raphael","An unnamed angel"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# LAWS more
c="Laws & Commandments"
more=[
    ("Deacon","What did Jesus teach about anger in the Sermon on the Mount?","Anger against a brother is like murder in the heart","Anger is always justified","Only physical violence counts","Anger is a minor sin"),
    ("Deacon","What did Jesus teach about lust?","Looking lustfully is adultery in the heart","Only actions matter","Temptation isn't sin","Lust is natural"),
    ("Deacon","What did Jesus teach about oaths?","Let your yes be yes and no be no — don't swear elaborate oaths","Always swear by God","Oaths are sacred and required","Never make promises"),
    ("Deacon","What is the 'new commandment' Jesus gave?","Love one another as I have loved you","Keep the Sabbath","Don't eat unclean food","Fast twice a week"),
    ("Pastor","What did Paul teach about the Law in Galatians?","The Law was a guardian until Christ came — now we live by faith","The Law is abolished","The Law still saves","Keep half the Law"),
    ("Deacon","What did the Jerusalem Council decide about Gentile believers?","They should avoid food sacrificed to idols, blood, strangled animals, and sexual immorality — but not full Jewish law","Full circumcision required","No rules at all","Full Torah observance"),
    ("Pastor","What is the 'law of the harvest' (Galatians 6:7)?","You reap what you sow","Plant more to get more","Harvest every 7 years","Share your harvest"),
    ("Deacon","What does 'love fulfills the law' mean (Romans 13:10)?","If you love your neighbor, you naturally obey the commandments about human relations","Love replaces all rules","Love means no consequences","Love is optional"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# ============================================================================
# FINAL SAVE
# ============================================================================
for i, q in enumerate(ALL):
    q["id"] = hashlib.md5(f"{q['category']}-{q['difficulty']}-{q['question'][:50]}-{i}".encode()).hexdigest()[:12]

from collections import Counter
cc = Counter(q["category"] for q in ALL)
dc = Counter((q["category"], q["difficulty"]) for q in ALL)

print(f"\n{'='*60}")
print(f"TOTAL UNIQUE QUESTIONS: {len(ALL)}")
print(f"{'='*60}")
for cat in sorted(cc.keys()):
    l=dc.get((cat,"Layperson"),0);d=dc.get((cat,"Deacon"),0);p=dc.get((cat,"Pastor"),0)
    print(f"  {cat}: {cc[cat]:4d} (L:{l:3d} D:{d:3d} P:{p:3d})")

with open("/home/claude/manna/manna_questions.json","w") as f:
    json.dump(ALL, f, indent=2)
print(f"\nSaved: {os.path.getsize('/home/claude/manna/manna_questions.json')/1024:.0f} KB")
