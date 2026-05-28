#!/usr/bin/env python3
"""
MANNA Expansion — Generates thousands more questions from expanded data tables.
Merges with existing questions from generate_all.py output.
"""
import json, random, hashlib, os
random.seed(123)

# Load existing
with open("/home/claude/manna/manna_questions.json") as f:
    ALL = json.load(f)

existing_qs = set(q["question"].strip().lower() for q in ALL)

def Q(cat,diff,q,opts,cor,exp=""):
    key = q.strip().lower()
    if key not in existing_qs:
        existing_qs.add(key)
        ALL.append({"category":cat,"difficulty":diff,"question":q,"options":opts,"correct":cor,"explanation":exp})

def shuf(correct, wrongs):
    w = [x for x in wrongs if x != correct][:3]
    while len(w) < 3: w.append("None of the above")
    opts = [correct] + w[:3]
    random.shuffle(opts)
    return opts

# ============================================================================
# EXPANDED DATA TABLES
# ============================================================================

# Famous Bible quotes and who said them
QUOTES = [
    ("Am I my brother's keeper?","Cain","Genesis 4:9","Genesis & Creation","Layperson"),
    ("Here am I. Send me!","Isaiah","Isaiah 6:8","Prophets","Layperson"),
    ("The LORD is my shepherd, I shall not want.","David (Psalm 23)","Psalm 23:1","Psalms & Proverbs","Layperson"),
    ("For God so loved the world...","Jesus","John 3:16","Life of Jesus","Layperson"),
    ("I am the way, the truth, and the life.","Jesus","John 14:6","Life of Jesus","Layperson"),
    ("In the beginning was the Word.","John (the Apostle)","John 1:1","Life of Jesus","Layperson"),
    ("Let there be light.","God","Genesis 1:3","Genesis & Creation","Layperson"),
    ("It is not good for man to be alone.","God","Genesis 2:18","Genesis & Creation","Layperson"),
    ("Where you go, I will go.","Ruth","Ruth 1:16","Women of the Bible","Layperson"),
    ("The LORD gave and the LORD has taken away.","Job","Job 1:21","Psalms & Proverbs","Deacon"),
    ("How long, O LORD?","David (Psalm 13)","Psalm 13:1","Psalms & Proverbs","Deacon"),
    ("Be strong and courageous.","God to Joshua","Joshua 1:9","Battles & Wars","Layperson"),
    ("Choose this day whom you will serve.","Joshua","Joshua 24:15","Battles & Wars","Layperson"),
    ("Speak, LORD, for your servant is listening.","Samuel","1 Samuel 3:10","Prophets","Layperson"),
    ("The battle is the LORD's.","David","1 Samuel 17:47","Battles & Wars","Deacon"),
    ("Man does not live on bread alone.","Jesus (quoting Deuteronomy)","Matthew 4:4","Life of Jesus","Layperson"),
    ("You are the Christ, the Son of the living God.","Peter","Matthew 16:16","The Apostles","Layperson"),
    ("Father, forgive them, for they know not what they do.","Jesus","Luke 23:34","Life of Jesus","Layperson"),
    ("It is finished.","Jesus","John 19:30","Life of Jesus","Layperson"),
    ("My God, my God, why have you forsaken me?","Jesus (quoting Psalm 22)","Matthew 27:46","Life of Jesus","Deacon"),
    ("I have fought the good fight, I have finished the race.","Paul","2 Timothy 4:7","Paul & His Letters","Deacon"),
    ("The just shall live by faith.","Habakkuk (quoted by Paul)","Habakkuk 2:4","Prophecy & Fulfillment","Deacon"),
    ("To everything there is a season.","The Teacher (Ecclesiastes)","Ecclesiastes 3:1","Psalms & Proverbs","Layperson"),
    ("Create in me a clean heart, O God.","David","Psalm 51:10","Psalms & Proverbs","Deacon"),
    ("Trust in the LORD with all your heart.","Solomon","Proverbs 3:5","Psalms & Proverbs","Layperson"),
    ("I can do all things through Christ who strengthens me.","Paul","Philippians 4:13","Paul & His Letters","Layperson"),
    ("For the wages of sin is death.","Paul","Romans 6:23","Paul & His Letters","Deacon"),
    ("Faith is the substance of things hoped for.","Author of Hebrews","Hebrews 11:1","The Apostles","Deacon"),
    ("If God is for us, who can be against us?","Paul","Romans 8:31","Paul & His Letters","Deacon"),
    ("Vanity of vanities, all is vanity.","The Teacher / Solomon","Ecclesiastes 1:2","Psalms & Proverbs","Deacon"),
    ("Come now, let us reason together.","God (through Isaiah)","Isaiah 1:18","Prophets","Deacon"),
    ("What does the LORD require of you? To act justly, love mercy, and walk humbly.","Micah","Micah 6:8","Prophets","Deacon"),
    ("Can these bones live?","God to Ezekiel","Ezekiel 37:3","Dreams & Visions","Deacon"),
    ("Thy word is a lamp unto my feet.","Psalmist","Psalm 119:105","Psalms & Proverbs","Layperson"),
    ("The earth is the LORD's and everything in it.","David","Psalm 24:1","Psalms & Proverbs","Deacon"),
    ("Do not be afraid, for I am with you.","God (through Isaiah)","Isaiah 41:10","Prophets","Layperson"),
    ("Behold, I am doing a new thing.","God (through Isaiah)","Isaiah 43:19","Prophets","Deacon"),
    ("Go and make disciples of all nations.","Jesus","Matthew 28:19","The Apostles","Layperson"),
    ("I am the vine, you are the branches.","Jesus","John 15:5","Life of Jesus","Deacon"),
    ("Love your enemies and pray for those who persecute you.","Jesus","Matthew 5:44","Life of Jesus","Deacon"),
    ("Unless you are born again, you cannot see the kingdom of God.","Jesus","John 3:3","Life of Jesus","Deacon"),
    ("I am the bread of life.","Jesus","John 6:35","Life of Jesus","Deacon"),
    ("I am the good shepherd.","Jesus","John 10:11","Life of Jesus","Deacon"),
    ("I am the resurrection and the life.","Jesus","John 11:25","Life of Jesus","Deacon"),
    ("I am the light of the world.","Jesus","John 8:12","Life of Jesus","Deacon"),
    ("I am the door.","Jesus","John 10:9","Life of Jesus","Deacon"),
    ("Before Abraham was, I AM.","Jesus","John 8:58","Life of Jesus","Pastor"),
    ("Lord, to whom shall we go? You have the words of eternal life.","Peter","John 6:68","The Apostles","Deacon"),
    ("Silver and gold I do not have, but what I have I give you.","Peter","Acts 3:6","The Apostles","Deacon"),
    ("I am not ashamed of the gospel.","Paul","Romans 1:16","Paul & His Letters","Deacon"),
    ("He must increase, but I must decrease.","John the Baptist","John 3:30","Life of Jesus","Deacon"),
    ("Prepare the way of the LORD.","Isaiah (fulfilled by John the Baptist)","Isaiah 40:3","Prophecy & Fulfillment","Layperson"),
    ("My grace is sufficient for you.","God to Paul","2 Corinthians 12:9","Paul & His Letters","Deacon"),
    ("The truth shall set you free.","Jesus","John 8:32","Life of Jesus","Layperson"),
    ("Do not judge, or you too will be judged.","Jesus","Matthew 7:1","Life of Jesus","Layperson"),
    ("Ask and it shall be given to you.","Jesus","Matthew 7:7","Life of Jesus","Layperson"),
    ("Blessed are the meek, for they shall inherit the earth.","Jesus","Matthew 5:5","Life of Jesus","Layperson"),
    ("You are Peter, and on this rock I will build my church.","Jesus","Matthew 16:18","The Apostles","Deacon"),
    ("Take up your cross and follow me.","Jesus","Matthew 16:24","Life of Jesus","Layperson"),
    ("Render unto Caesar the things that are Caesar's.","Jesus","Matthew 22:21","Life of Jesus","Deacon"),
    ("A prophet is not without honor except in his own hometown.","Jesus","Mark 6:4","Life of Jesus","Deacon"),
    ("The sabbath was made for man, not man for the sabbath.","Jesus","Mark 2:27","Laws & Commandments","Deacon"),
    ("Let him who is without sin cast the first stone.","Jesus","John 8:7","Life of Jesus","Layperson"),
    ("I have set before you life and death. Choose life.","Moses","Deuteronomy 30:19","Laws & Commandments","Deacon"),
    ("Be still, and know that I am God.","God (Psalm 46)","Psalm 46:10","Psalms & Proverbs","Layperson"),
    ("The LORD is near to the brokenhearted.","David","Psalm 34:18","Psalms & Proverbs","Deacon"),
    ("Weeping may endure for a night, but joy comes in the morning.","David","Psalm 30:5","Psalms & Proverbs","Deacon"),
    ("As iron sharpens iron, so one person sharpens another.","Solomon","Proverbs 27:17","Psalms & Proverbs","Deacon"),
    ("A soft answer turns away wrath.","Solomon","Proverbs 15:1","Psalms & Proverbs","Deacon"),
    ("Train up a child in the way he should go.","Solomon","Proverbs 22:6","Psalms & Proverbs","Layperson"),
    ("There is nothing new under the sun.","The Teacher / Solomon","Ecclesiastes 1:9","Psalms & Proverbs","Deacon"),
]

# Who said it questions
all_speakers = list(set(s for _,s,_,_,_ in QUOTES))
for quote,speaker,ref,cat,diff in QUOTES:
    wrongs = [s for s in all_speakers if s != speaker]
    random.shuffle(wrongs)
    Q(cat, diff, f"Who said: '{quote}'?", shuf(speaker, wrongs[:3]), speaker, ref)

# Where is this quote found?
for quote,speaker,ref,cat,diff in QUOTES:
    all_refs = list(set(r for _,_,r,_,_ in QUOTES if r != ref))
    random.shuffle(all_refs)
    diff2 = "Deacon" if diff=="Layperson" else "Pastor"
    Q(cat, diff2, f"Where is this verse found: '{quote[:60]}...'?", shuf(ref, all_refs[:3]), ref)

print(f"  After quotes: {len(ALL)}")

# ============================================================================
# OCCUPATIONS / ROLES
# ============================================================================
OCCUPATIONS = [
    ("Adam","Gardener / farmer","Genesis & Creation","Layperson"),
    ("Noah","Farmer / ark builder","Genesis & Creation","Layperson"),
    ("Abraham","Herdsman / nomadic patriarch","Genesis & Creation","Deacon"),
    ("Joseph (OT)","Governor of Egypt","Genesis & Creation","Layperson"),
    ("Moses","Shepherd (in Midian), then leader of Israel","Moses & the Exodus","Deacon"),
    ("David","Shepherd, then warrior, then king","Kings & Kingdoms","Layperson"),
    ("Solomon","King and author","Kings & Kingdoms","Layperson"),
    ("Amos","Shepherd and fig-tree tender","Prophets","Deacon"),
    ("Nehemiah","Cupbearer to the Persian king","Places & Lands","Deacon"),
    ("Daniel","Government official in Babylon","Prophets","Deacon"),
    ("Peter","Fisherman","The Apostles","Layperson"),
    ("Matthew","Tax collector","The Apostles","Layperson"),
    ("Luke","Physician","The Apostles","Deacon"),
    ("Paul","Tentmaker and Pharisee","Paul & His Letters","Deacon"),
    ("Lydia","Seller of purple cloth","Women of the Bible","Deacon"),
    ("Rahab","Prostitute / innkeeper in Jericho","Women of the Bible","Deacon"),
    ("Bezalel","Craftsman / artisan of the Tabernacle","Moses & the Exodus","Pastor"),
    ("Zacchaeus","Chief tax collector","Life of Jesus","Layperson"),
    ("Joseph of Arimathea","Rich member of the Sanhedrin","Life of Jesus","Deacon"),
    ("Nicodemus","Pharisee and member of the Sanhedrin","Life of Jesus","Deacon"),
    ("Cornelius","Roman centurion","The Apostles","Deacon"),
    ("Aquila","Tentmaker (with Priscilla)","Paul & His Letters","Pastor"),
    ("Deborah","Judge and prophetess","Women of the Bible","Deacon"),
    ("Samuel","Judge, priest, and prophet","Prophets","Layperson"),
    ("Gideon","Farmer, then judge","Battles & Wars","Deacon"),
    ("Samson","Judge / Nazirite warrior","Battles & Wars","Layperson"),
    ("Elisha","Farmer before becoming prophet","Prophets","Deacon"),
    ("Ezra","Priest and scribe","Kings & Kingdoms","Deacon"),
    ("Boaz","Wealthy landowner","Women of the Bible","Deacon"),
    ("Cain","Farmer","Genesis & Creation","Layperson"),
    ("Abel","Shepherd","Genesis & Creation","Layperson"),
    ("Esther","Queen of Persia","Women of the Bible","Layperson"),
]

all_jobs = list(set(j for _,j,_,_ in OCCUPATIONS))
for person,job,cat,diff in OCCUPATIONS:
    wrongs = [j for j in all_jobs if j != job]
    random.shuffle(wrongs)
    Q(cat, diff, f"What was {person}'s occupation or role?", shuf(job, wrongs[:3]), job)

print(f"  After occupations: {len(ALL)}")

# ============================================================================
# BIBLE FIRSTS
# ============================================================================
FIRSTS = [
    ("Who was the first king of Israel?","Saul","David","Solomon","Moses","Kings & Kingdoms","Layperson"),
    ("Who was the first priest mentioned in the Bible?","Melchizedek","Aaron","Levi","Abraham","Genesis & Creation","Pastor"),
    ("Who was the first prophet?","Abraham (called a prophet in Genesis 20:7)","Moses","Samuel","Elijah","Prophets","Pastor"),
    ("What was the first miracle Jesus performed?","Turning water into wine","Healing a leper","Walking on water","Feeding 5,000","Miracles","Layperson"),
    ("Who was the first person raised from the dead in the Bible?","The widow of Zarephath's son (by Elijah)","Lazarus","Jairus' daughter","Eutychus","Miracles","Pastor"),
    ("What was the first plague of Egypt?","Water turned to blood","Frogs","Darkness","Boils","Moses & the Exodus","Layperson"),
    ("Who was the first martyr of the church?","Stephen","James","Peter","Paul","The Apostles","Layperson"),
    ("What was the first sin?","Eating the forbidden fruit","Murder","Lying","Idolatry","Genesis & Creation","Layperson"),
    ("Who was the first person to die in the Bible?","Abel","Adam","Eve","Cain","Genesis & Creation","Layperson"),
    ("What was the first thing God created?","Light","Water","Land","Angels","Genesis & Creation","Layperson"),
    ("Who was the first judge of Israel?","Othniel","Deborah","Gideon","Samson","Battles & Wars","Deacon"),
    ("What was the first commandment?","You shall have no other gods before me","Do not murder","Do not steal","Honor your parents","Laws & Commandments","Layperson"),
    ("Who was the first person to be called a Hebrew?","Abraham (Abram)","Moses","Jacob","Adam","Genesis & Creation","Deacon"),
    ("What was the first bird Noah sent from the ark?","A raven","A dove","An eagle","A sparrow","Genesis & Creation","Layperson"),
    ("Who was the first Gentile convert in Acts?","Cornelius","The Ethiopian eunuch","Lydia","The Philippian jailer","The Apostles","Deacon"),
    ("Where was the first church?","Jerusalem","Antioch","Rome","Corinth","The Apostles","Deacon"),
    ("Who gave the first prophecy of the Messiah?","God (Genesis 3:15 — the seed of the woman)","Isaiah","Moses","Abraham","Prophecy & Fulfillment","Pastor"),
    ("What was the first animal sacrificed in the Bible?","Animals God killed to clothe Adam and Eve (Genesis 3:21)","Abel's offering","Abraham's ram","The Passover lamb","Genesis & Creation","Pastor"),
    ("Who built the first city?","Cain","Nimrod","Noah","Adam","Genesis & Creation","Deacon"),
    ("Who built the first altar?","Noah (after the flood)","Abraham","Abel","Moses","Genesis & Creation","Deacon"),
]
for question,correct,w1,w2,w3,cat,diff in FIRSTS:
    Q(cat, diff, question, shuf(correct,[w1,w2,w3]), correct)

print(f"  After firsts: {len(ALL)}")

# ============================================================================
# BIBLE SYMBOLS & MEANINGS
# ============================================================================
SYMBOLS = [
    ("What does the rainbow symbolize in the Bible?","God's covenant never to flood the earth again","God's power","The end times","Creation","Genesis & Creation","Layperson"),
    ("What does bread represent in communion?","Jesus' body","God's provision","The Law","Heaven","Life of Jesus","Layperson"),
    ("What does wine represent in communion?","Jesus' blood","Joy","The Spirit","Judgment","Life of Jesus","Layperson"),
    ("What does the lamb symbolize?","Jesus as the sacrificial Lamb of God","Israel","The Temple","The Holy Spirit","Life of Jesus","Layperson"),
    ("What does the dove symbolize?","The Holy Spirit / peace","Jesus","The Father","Judgment","Life of Jesus","Layperson"),
    ("What does the serpent symbolize?","Satan / temptation","Wisdom","Healing","Moses","Angels & Demons","Layperson"),
    ("What does the number 7 symbolize?","Completion / perfection","Judgment","Sin","Power","Numbers & Genealogies","Deacon"),
    ("What does the number 40 often represent?","A period of testing or trial","Victory","Perfection","Covenant","Numbers & Genealogies","Deacon"),
    ("What does the number 12 symbolize?","God's governmental authority (12 tribes, 12 apostles)","Completion","Testing","Judgment","Numbers & Genealogies","Deacon"),
    ("What do the seven lampstands in Revelation represent?","The seven churches","The seven angels","The seven seals","The seven trumpets","Revelation & End Times","Deacon"),
    ("What does the olive tree symbolize?","Israel / peace / the Holy Spirit","War","Judgment","The Temple","Prophecy & Fulfillment","Deacon"),
    ("What does leaven (yeast) often symbolize?","Sin or corrupting influence","God's kingdom","Blessing","Purity","Parables","Deacon"),
    ("What does the mustard seed symbolize?","Faith / the kingdom starting small","Sin","Wealth","Power","Parables","Layperson"),
    ("What does water baptism symbolize?","Death to sin and new life in Christ","Washing away all sins","Joining a church","Becoming a priest","Paul & His Letters","Deacon"),
    ("What does oil symbolize in the Bible?","The Holy Spirit / anointing","Wealth","Food","Healing only","Laws & Commandments","Deacon"),
    ("What does the lion symbolize regarding Jesus?","The Lion of Judah — Jesus as King","Danger","Satan","War","Revelation & End Times","Deacon"),
    ("What does salt symbolize?","Preservation and flavoring — believers' influence","Wealth","Tears","Judgment","Life of Jesus","Deacon"),
    ("What does light symbolize?","God's presence, truth, and righteousness","Heaven","Angels","The Law","Life of Jesus","Layperson"),
    ("What do thorns symbolize?","The curse of sin","Royalty","Growth","Wealth","Genesis & Creation","Deacon"),
    ("What does the cross symbolize?","Christ's sacrificial death for humanity","Roman power","Jewish law","Political rebellion","Life of Jesus","Layperson"),
]
for question,correct,w1,w2,w3,cat,diff in SYMBOLS:
    Q(cat, diff, question, shuf(correct,[w1,w2,w3]), correct)

print(f"  After symbols: {len(ALL)}")

# ============================================================================
# ALTERNATE NAMES / "ALSO KNOWN AS"
# ============================================================================
NAMES = [
    ("What is another name for Peter?","Simon / Cephas","Andrew","Bartholomew","Thaddaeus","The Apostles","Deacon"),
    ("What was Paul's original name?","Saul","Simon","Stephen","Silvanus","Paul & His Letters","Layperson"),
    ("What was Jacob renamed to?","Israel","Judah","Abraham","Isaac","Genesis & Creation","Layperson"),
    ("What is another name for the Sea of Galilee?","Sea of Tiberias / Lake Gennesaret","Dead Sea","Red Sea","Lake Merom","Places & Lands","Deacon"),
    ("What is another name for Mount Sinai?","Mount Horeb","Mount Nebo","Mount Carmel","Mount Moriah","Places & Lands","Deacon"),
    ("What was Esau also called?","Edom","Moab","Ammon","Gilead","Genesis & Creation","Deacon"),
    ("What was the land of Canaan later called?","Israel / Palestine","Egypt","Babylon","Syria","Places & Lands","Deacon"),
    ("What is another name for the Temple?","The House of God / Beit HaMikdash","The Tabernacle","The Synagogue","The Altar","Places & Lands","Deacon"),
    ("What was Abram renamed to?","Abraham","Isaac","Israel","Moses","Genesis & Creation","Layperson"),
    ("What was Sarai renamed to?","Sarah","Rebekah","Rachel","Hagar","Genesis & Creation","Deacon"),
    ("What is another name for the Devil?","Satan, Lucifer, the Accuser, the Dragon","Beelzebub only","Abaddon only","Belial only","Angels & Demons","Deacon"),
    ("What was Thomas also called?","Didymus (the Twin)","Thaddaeus","Levi","Cephas","The Apostles","Deacon"),
    ("What was Matthew also called?","Levi","Thomas","Simon","Bartholomew","The Apostles","Deacon"),
    ("Bartholomew may be the same person as whom?","Nathanael","Philip","Thomas","Thaddaeus","The Apostles","Pastor"),
    ("What is another name for the book of Revelation?","The Apocalypse","The Prophecy","The Vision","The End","Revelation & End Times","Deacon"),
    ("What was Gideon also called?","Jerubbaal","Barak","Othniel","Jephthah","Battles & Wars","Pastor"),
    ("What is the other name for Dorcas?","Tabitha","Lydia","Phoebe","Priscilla","Women of the Bible","Deacon"),
    ("What is the other name for Jethro?","Reuel","Hobab","Caleb","Midian","Moses & the Exodus","Pastor"),
    ("What was the city of Jebus later called?","Jerusalem","Bethlehem","Hebron","Samaria","Places & Lands","Pastor"),
    ("What is another name for the Holy Spirit?","The Comforter / Paraclete / Helper","The Angel","The Word","The Law","Paul & His Letters","Deacon"),
]
for question,correct,w1,w2,w3,cat,diff in NAMES:
    Q(cat, diff, question, shuf(correct,[w1,w2,w3]), correct)

print(f"  After names: {len(ALL)}")

# ============================================================================
# MORE CATEGORY-SPECIFIC QUESTIONS — BULK GENERATION
# ============================================================================

# GENESIS (more)
c = "Genesis & Creation"
more = [
    ("Layperson","What day did God rest?","The seventh","The sixth","The eighth","The first"),
    ("Layperson","What was Adam's job in the Garden of Eden?","To tend and keep it","To name the animals only","To guard the gate","To build shelter"),
    ("Layperson","How many sons of Noah are named?","3 — Shem, Ham, Japheth","2","4","12"),
    ("Deacon","What did God do when He saw the world's wickedness before the flood?","He was grieved and decided to destroy it with a flood","He immediately destroyed it","He sent prophets","He ignored it"),
    ("Deacon","Who was Laban?","Rachel and Leah's father, Jacob's uncle","Abraham's brother","Isaac's servant","A king of Canaan"),
    ("Deacon","What did Joseph's brothers tell their father happened to him?","That a wild animal killed him","That he drowned","That he ran away","That he died of illness"),
    ("Deacon","Why was Joseph put in prison in Egypt?","Potiphar's wife falsely accused him","He stole food","He tried to escape","He insulted Pharaoh"),
    ("Deacon","What did God tell Abraham to do with Isaac on Mount Moriah?","Offer him as a sacrifice","Build an altar of stones","Pray for three days","Leave him there"),
    ("Deacon","What replaced Isaac on the altar?","A ram caught in a thicket","A lamb","A bull","A dove"),
    ("Pastor","What covenant did God make with Noah?","Never to destroy the earth with a flood again","To give him the land of Canaan","To make his descendants as many as the stars","To send a Messiah through his line"),
    ("Pastor","What are the names of Ishmael's twelve sons?","Nebaioth, Kedar, Adbeel, Mibsam, Mishma, Dumah, Massa, Hadad, Tema, Jetur, Naphish, Kedemah","Reuben through Benjamin","The twelve apostles","The twelve judges"),
    ("Pastor","How old was Terah when he died?","205","175","200","150"),
    ("Deacon","What did Esau do for a living?","He was a skillful hunter","He was a shepherd","He was a farmer","He was a builder"),
    ("Deacon","Who was Benjamin?","Jacob's youngest son, born to Rachel","Jacob's firstborn","Joseph's son","Judah's son"),
    ("Deacon","What happened to Rachel when Benjamin was born?","She died in childbirth","She was healed","She rejoiced","She named him Reuben"),
    ("Pastor","What name did Rachel give Benjamin before she died?","Ben-Oni (son of my sorrow)","Benjamin","Benaiah","Ben-Ammi"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# MOSES more
c = "Moses & the Exodus"
more = [
    ("Layperson","What did Moses see that made him curious on Mount Horeb?","A bush that burned but did not burn up","A bright star","A golden pillar","A rainbow"),
    ("Layperson","What did God tell Moses to do with his sandals?","Take them off — he was on holy ground","Put them on to protect his feet","Leave them as an offering","Throw them away"),
    ("Layperson","How many times did Moses go to Pharaoh?","Multiple times — once for each plague","Once","Twice","Three times"),
    ("Deacon","What were the names of the Hebrew midwives who defied Pharaoh?","Shiphrah and Puah","Miriam and Jochebed","Hagar and Keturah","Ruth and Naomi"),
    ("Deacon","What did the Israelites borrow from the Egyptians before leaving?","Gold, silver, and clothing","Weapons","Chariots","Food only"),
    ("Deacon","What is the Song of Miriam?","A song of praise after crossing the Red Sea","A lullaby for baby Moses","A prayer for forgiveness","A psalm of David"),
    ("Deacon","What was the manna described as tasting like?","Wafers made with honey","Plain bread","Bitter herbs","Meat"),
    ("Pastor","What was special about Moses' face after meeting God?","It shone so brightly he wore a veil","It turned white","It was scarred","Nothing visible happened"),
    ("Pastor","How many judges did Jethro advise Moses to appoint?","Judges over thousands, hundreds, fifties, and tens","12 judges","70 elders","7 judges"),
    ("Pastor","What is the Aaronic blessing?","'The LORD bless you and keep you...' (Numbers 6:24-26)","The Ten Commandments","The Shema","The Song of Moses"),
    ("Layperson","What did the Israelites complain about most in the wilderness?","Food and water","The weather","Moses' leadership","The length of the journey"),
    ("Deacon","What happened when the people looked at the bronze serpent?","They were healed from snake bites","They gained strength","They saw visions","Nothing happened"),
    ("Pastor","What color were the threads in the Tabernacle curtains?","Blue, purple, and scarlet","White only","Gold and silver","Red and black"),
    ("Layperson","What did the Ten Commandments come written on?","Two stone tablets","Papyrus scrolls","A golden plate","Animal skins"),
    ("Deacon","What did the pillar of cloud/fire represent?","God's presence guiding Israel","A natural phenomenon","An angel","The Ark of the Covenant"),
    ("Layperson","What is the third commandment about?","Not taking God's name in vain","Not making idols","Keeping the Sabbath","Honoring parents"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# LIFE OF JESUS more
c = "Life of Jesus"
more = [
    ("Layperson","What did the shepherds do after the angels told them about Jesus?","They went to see the baby in the manger","They stayed with their sheep","They told the priests","They went home"),
    ("Layperson","Who tried to kill baby Jesus?","King Herod","Pontius Pilate","Caesar Augustus","Pharaoh"),
    ("Layperson","Where did Mary and Joseph flee with baby Jesus?","Egypt","Nazareth","Bethlehem","Rome"),
    ("Layperson","What was Jesus' earthly father's occupation?","Carpenter","Fisherman","Farmer","Tentmaker"),
    ("Layperson","At what event did Jesus turn water into wine?","A wedding","A funeral","A feast","A Sabbath meal"),
    ("Layperson","What did Jesus say to Lazarus?","'Lazarus, come out!'","'Rise and walk'","'Be healed'","'Your sins are forgiven'"),
    ("Layperson","Who washed Jesus' feet with her tears?","A sinful woman (Luke 7)","Martha","Mary Magdalene","The Samaritan woman"),
    ("Deacon","What was Zacchaeus known for?","Being a short tax collector who climbed a tree to see Jesus","Being blind","Being a leper","Being a fisherman"),
    ("Deacon","What happened at the Pool of Siloam?","Jesus healed a blind man who washed there","Jesus was baptized","Peter walked on water","A paralytic was healed"),
    ("Deacon","What did Jesus say about the Temple?","'Destroy this temple and in three days I will raise it up'","'This is my Father's house only'","'Build a new temple'","'The Temple will last forever'"),
    ("Deacon","What did Jesus write in the sand?","The Bible doesn't say what He wrote","A list of sins","The woman's name","A commandment"),
    ("Deacon","Who was Lazarus?","Brother of Mary and Martha whom Jesus raised from the dead","A beggar in a parable","A tax collector","A Pharisee"),
    ("Deacon","What did Jesus do before washing the disciples' feet?","Removed His outer garment and tied a towel around His waist","Prayed","Sang a hymn","Blessed the bread"),
    ("Pastor","How many 'I AM' statements does Jesus make in John?","7","3","5","12"),
    ("Pastor","What is the Olivet Discourse?","Jesus' teaching about the end times on the Mount of Olives","The Sermon on the Mount","The Last Supper teaching","Paul's speech in Athens"),
    ("Pastor","Who was Caiaphas?","The high priest who orchestrated Jesus' trial","A Roman governor","A Pharisee","A disciple"),
    ("Layperson","What did Jesus do with five loaves and two fish?","Fed 5,000 people","Fed 12 apostles","Made a sacrifice","Gave them to the poor"),
    ("Layperson","What happened when Jesus was baptized?","The heavens opened, the Spirit descended like a dove, God spoke","An earthquake occurred","The river parted","Fire came from heaven"),
    ("Deacon","What did the voice from heaven say at Jesus' baptism?","'This is my beloved Son, in whom I am well pleased'","'Follow Him'","'He is the Messiah'","'Listen to Him'"),
    ("Pastor","What Old Testament figure appeared with Elijah at the Transfiguration?","Moses","Abraham","David","Isaiah"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# APOSTLES more
c = "The Apostles"
more = [
    ("Layperson","What happened on the day of Pentecost?","The Holy Spirit came upon the believers","Jesus ascended","The Temple was rebuilt","Paul was converted"),
    ("Layperson","What appeared over the apostles' heads at Pentecost?","Tongues of fire","Halos","Crowns","Stars"),
    ("Layperson","What did the apostles do after receiving the Holy Spirit?","Spoke in other languages","Healed the sick immediately","Went to Rome","Built a church"),
    ("Deacon","Who was Saul before he became Paul?","A Pharisee who persecuted Christians","A fisherman","A tax collector","A Roman soldier"),
    ("Deacon","What was Philip the evangelist known for?","Baptizing the Ethiopian eunuch on the road to Gaza","Walking on water","Being the first martyr","Writing a Gospel"),
    ("Deacon","Who was Apollos?","An eloquent preacher taught by Priscilla and Aquila","One of the 12 apostles","A Roman official","A high priest"),
    ("Deacon","What did Peter's vision of the sheet mean?","God was showing that Gentiles were not 'unclean'","A new diet was permitted","The law was abolished","A famine was coming"),
    ("Pastor","How did James (brother of John) die?","Killed with a sword by Herod Agrippa I","Crucified","Stoned","Died of old age"),
    ("Pastor","What was the first church council about?","Whether Gentile believers must follow Jewish law (Acts 15)","Who should lead the church","Whether to accept Paul","Tax collection"),
    ("Pastor","Who were the 'Seven' chosen to serve in Acts 6?","Stephen, Philip, Prochorus, Nicanor, Timon, Parmenas, Nicolaus","The twelve apostles","Paul's traveling companions","The elders of Jerusalem"),
    ("Deacon","What happened to Ananias and Sapphira?","They lied about money and died","They were exiled","They became apostles","They were healed"),
    ("Deacon","Who led the Jerusalem church?","James (brother of Jesus)","Peter","John","Paul"),
    ("Layperson","How did the apostles choose Judas' replacement?","They cast lots","They voted","Jesus appeared and chose","They drew straws"),
    ("Deacon","What was special about the Ethiopian eunuch?","He was reading Isaiah and Philip explained it to him","He was a king","He was blind","He was a priest"),
    ("Pastor","Who was Gamaliel?","A respected Pharisee teacher who advised caution about the apostles","A Roman governor","A Greek philosopher","A Sadducee priest"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# PAUL more
c = "Paul & His Letters"
more = [
    ("Layperson","What happened to Paul on the road to Damascus?","He was blinded by a bright light and heard Jesus' voice","He was arrested","He found a scroll","He met Peter"),
    ("Layperson","Who restored Paul's sight?","Ananias","Peter","Barnabas","Luke"),
    ("Deacon","What did Paul preach at the Areopagus in Athens?","About the 'unknown god' — declaring the true God","About the resurrection only","Against Greek philosophy","About Jewish law"),
    ("Deacon","Who was Silas?","Paul's traveling companion and co-author of letters","A church leader in Rome","A false prophet","A centurion"),
    ("Deacon","What happened to Paul and Silas in the Philippian jail?","An earthquake opened the doors; the jailer was converted","They escaped","They were executed","Angels freed them"),
    ("Deacon","What is the 'love chapter' of the Bible?","1 Corinthians 13","Romans 8","John 3","Ephesians 5"),
    ("Deacon","What are the fruits of the Spirit?","Love, joy, peace, patience, kindness, goodness, faithfulness, gentleness, self-control","Faith, hope, love","Wisdom, knowledge, understanding","Healing, prophecy, tongues"),
    ("Deacon","In which letter does Paul discuss the resurrection at length?","1 Corinthians 15","Romans 6","Philippians 3","Colossians 1"),
    ("Pastor","What is Paul's 'hymn of Christ' about?","Christ's humility and exaltation (Philippians 2:5-11)","A song of praise","A prayer for healing","A prophecy"),
    ("Pastor","To which church did Paul write about the 'armor of God'?","Ephesus","Corinth","Rome","Philippi"),
    ("Pastor","What was the Judaizer controversy?","Whether Gentile Christians must be circumcised and follow the Law","Whether to eat meat offered to idols","Whether women could teach","Whether to pay taxes to Rome"),
    ("Pastor","What is justification by faith?","Being declared righteous before God through faith, not works","Earning salvation through obedience","Being sinless","Becoming a priest"),
    ("Layperson","Which letter did Paul write from prison to the Philippians?","Philippians","Romans","Galatians","Corinthians"),
    ("Deacon","What letter did Paul write to a slave owner about his runaway slave?","Philemon","Titus","Timothy","Colossians"),
    ("Pastor","What were Paul's 'prison epistles'?","Ephesians, Philippians, Colossians, Philemon","Romans, Galatians","1-2 Timothy, Titus","1-2 Thessalonians"),
    ("Deacon","What did Paul say about marriage in 1 Corinthians 7?","It is good to marry, but singleness allows undivided devotion to God","Everyone must marry","Marriage is wrong","Only priests should be single"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# REVELATION more
c = "Revelation & End Times"
more = [
    ("Layperson","What does 'Revelation' mean?","Unveiling or revealing","Destruction","Prophecy","History"),
    ("Layperson","What does the book of Revelation describe?","Visions of the end times and God's ultimate victory","The life of Jesus","The history of Israel","Paul's journeys"),
    ("Deacon","What is the Millennium in Revelation?","A 1,000-year reign of Christ","A 100-year period","An eternal kingdom","7 years of tribulation"),
    ("Deacon","What is the Great Tribulation?","A period of intense suffering before Christ's return","The flood","The exile","The plagues of Egypt"),
    ("Deacon","What is 'Babylon the Great' in Revelation?","A symbol of the world's corrupt system opposing God","A literal city","Rome only","Jerusalem"),
    ("Deacon","What happens when the seventh trumpet sounds?","Loud voices proclaim the kingdom of God","Silence","An earthquake","The beast appears"),
    ("Pastor","What are the letters to the seven churches about?","Praise, warning, and instruction to each church","Future prophecies only","Historical accounts","Rules for worship"),
    ("Pastor","Which church was told it was 'neither hot nor cold'?","Laodicea","Ephesus","Smyrna","Pergamum"),
    ("Pastor","Which church was told it had 'left its first love'?","Ephesus","Sardis","Thyatira","Philadelphia"),
    ("Pastor","What does the rider on the white horse in Revelation 19 represent?","Christ returning in victory","Conquest/the Antichrist","Peace","An angel"),
    ("Deacon","What is the Book of Life?","God's record of those who will enter heaven","The Bible itself","The Torah","The book of Psalms"),
    ("Deacon","What does 'Alpha and Omega' mean?","The first and last — beginning and end","The strongest","The wisest","The holiest"),
    ("Pastor","What are Gog and Magog?","Nations that rebel against God in the final battle","Two demons","Fallen angels","Roman legions"),
    ("Deacon","What tree is in the New Jerusalem?","The Tree of Life","The Tree of Knowledge","An olive tree","A fig tree"),
    ("Layperson","What is the last book of the Bible?","Revelation","Malachi","Jude","3 John"),
    ("Layperson","What is the last word of the Bible?","Amen","Peace","Love","God"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# ANGELS & DEMONS more
c = "Angels & Demons"
more = [
    ("Layperson","What did the angel tell Mary?","She would give birth to the Son of God","To flee to Egypt","To go to the Temple","To marry Joseph immediately"),
    ("Layperson","What did angels tell the shepherds?","'Glory to God in the highest, and peace on earth'","'Follow the star'","'Go to the Temple'","'Fear the Romans'"),
    ("Deacon","What did Satan tempt Jesus with first in the wilderness?","Turning stones into bread","Jumping from the Temple","Ruling all kingdoms","Turning water to wine"),
    ("Deacon","How did Jesus respond to each temptation?","With Scripture — 'It is written...'","With miracles","With silence","With prayer"),
    ("Deacon","What role do angels play in Revelation?","They deliver judgments, make announcements, and worship God","They fight demons only","They write the book","They rule nations"),
    ("Deacon","What angel shut the lions' mouths for Daniel?","An angel of God (unnamed)","Michael","Gabriel","Raphael"),
    ("Pastor","What is the 'angel of the LORD' in the Old Testament?","Possibly a pre-incarnate appearance of Christ (Christophany)","Always Gabriel","Always Michael","A human messenger"),
    ("Pastor","What happened when Satan tried to take the body of Moses?","Michael the archangel rebuked him (Jude 1:9)","God destroyed Satan","Nothing — this isn't in the Bible","Gabriel intervened"),
    ("Pastor","What did the angels do at the empty tomb?","Told the women Jesus had risen","Rolled away the stone only","Guarded the tomb","Sang hymns"),
    ("Deacon","Who is the 'prince of this world' according to Jesus?","Satan","Caesar","Herod","The high priest"),
    ("Deacon","What did the angel Gabriel tell Zechariah?","His wife Elizabeth would have a son (John the Baptist)","The Temple would be destroyed","To flee Jerusalem","To anoint David"),
    ("Pastor","What are the 'living creatures' around God's throne in Revelation?","Four creatures — lion, ox, man, eagle — with six wings and many eyes","Twelve angels","Seven spirits","Two cherubim"),
    ("Deacon","What did the angel do to Balaam's donkey?","Stood in the road with a sword — only the donkey could see him","Killed it","Blessed it","Rode it"),
    ("Pastor","What is spiritual warfare according to Ephesians 6?","Our struggle against spiritual forces of evil, not flesh and blood","Physical battles for territory","Arguments between churches","Prayer only"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# LAWS & COMMANDMENTS more
c = "Laws & Commandments"
more = [
    ("Layperson","What does 'Honor your father and mother' promise?","Long life in the land","Wealth","Many children","A palace"),
    ("Layperson","What does 'You shall not covet' mean?","Don't desire what belongs to others","Don't steal","Don't lie","Don't worship idols"),
    ("Deacon","What is the Sabbath?","The seventh day of rest, from Friday evening to Saturday evening","Sunday","Any day of prayer","The first day of the week"),
    ("Deacon","What did Jesus say about the Sabbath?","The Sabbath was made for man, not man for the Sabbath","It was abolished","It must be kept strictly","It should be moved to Sunday"),
    ("Deacon","What is the 'Golden Rule'?","Do unto others as you would have them do unto you","Love God above all","Keep the Sabbath","Do not steal"),
    ("Deacon","What did the Pharisees add to the Law?","Hundreds of extra rules and traditions","Nothing","New commandments","A new covenant"),
    ("Deacon","What is the dietary law called?","Kashrut (kosher laws)","Halakha","Mitzvot","Shabbat"),
    ("Pastor","What animal was required for the Day of Atonement scapegoat?","A goat","A lamb","A bull","A dove"),
    ("Pastor","What is the 'lex talionis'?","'Eye for eye, tooth for tooth' — proportional justice","Love your neighbor","Turn the other cheek","An offering law"),
    ("Pastor","What did gleaning laws require?","Leaving edges of fields unharvested for the poor","Double harvest","Burning leftover crops","Storing grain for 7 years"),
    ("Deacon","What are the two tablets of the Ten Commandments about?","The first 4: our relationship with God; the last 6: with others","5 and 5","Laws and punishments","Blessings and curses"),
    ("Layperson","Which commandment forbids making idols?","The second","The first","The third","The fourth"),
    ("Layperson","Which commandment forbids lying?","The ninth — 'You shall not bear false witness'","The eighth","The seventh","The tenth"),
    ("Pastor","What were the Noahide Laws?","Seven laws given to Noah applicable to all humanity","The Ten Commandments","The 613 mitzvot","Dietary laws"),
    ("Deacon","What did Jesus say was the summary of all the Law and Prophets?","Love God and love your neighbor","Keep the Sabbath","Don't eat unclean food","Sacrifice daily"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# PROPHECY more
c = "Prophecy & Fulfillment"
more = [
    ("Layperson","What did Isaiah prophesy about a virgin?","A virgin would conceive and bear a son called Immanuel","A virgin would become queen","A virgin would lead Israel","A virgin would build the Temple"),
    ("Deacon","Where did Micah say the Messiah would be born?","Bethlehem Ephrathah","Jerusalem","Nazareth","Hebron"),
    ("Deacon","What did Zechariah prophesy about the Messiah's entry?","He would come riding on a donkey","He would come on a white horse","He would come from the clouds","He would come from Egypt"),
    ("Deacon","What does Isaiah 53 describe?","A suffering servant who bears the sins of many","A conquering king","A priestly figure","A prophet rejected only by pagans"),
    ("Deacon","What did Jeremiah prophesy about a 'new covenant'?","God would write His law on their hearts, not on stone","A new Temple","A new king","New dietary laws"),
    ("Pastor","What does Genesis 3:15 prophesy?","The seed of the woman would crush the serpent's head","Adam would return to Eden","Eve would have many children","The serpent would be forgiven"),
    ("Pastor","How was Psalm 22 fulfilled?","Its details match Jesus' crucifixion — pierced hands, divided garments, mocked","It describes David's battle","It predicts the exile","It describes Solomon's reign"),
    ("Deacon","What prophet said 'They will look on me whom they have pierced'?","Zechariah","Isaiah","Jeremiah","Daniel"),
    ("Deacon","What did Isaiah prophesy about the Messiah being buried?","He would be with a rich man in His death","He would be buried in a cave","He would not be buried","He would be buried at sea"),
    ("Pastor","What are the 'Servant Songs' of Isaiah?","Four passages in Isaiah (42, 49, 50, 52-53) about the Messiah","Psalms of David","Songs of Solomon","Lamentations"),
    ("Deacon","What prophet predicted 70 years of exile?","Jeremiah","Isaiah","Ezekiel","Daniel"),
    ("Pastor","What did Daniel's vision of the Son of Man coming on clouds foreshadow?","Jesus' ascension, return, and authority","The fall of Babylon","The Roman conquest","The Maccabean revolt"),
    ("Deacon","What did Joel prophesy about the Spirit?","God would pour out His Spirit on all people — fulfilled at Pentecost","The Spirit would leave Israel","Only priests would receive it","The Spirit would bring judgment only"),
    ("Pastor","What does the 'Branch' prophecy refer to?","The Messiah from David's line (Jeremiah 23, Zechariah 3 & 6)","A literal tree","The Tree of Life","Solomon's Temple"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# FOOD & FEASTS more
c = "Food, Feasts & Offerings"
more = [
    ("Layperson","What did Jesus say at the Last Supper about the bread?","'This is my body'","'This is my gift'","'Eat and remember Moses'","'Bread sustains the body'"),
    ("Layperson","What did Jesus say about the wine at the Last Supper?","'This is my blood of the new covenant'","'Wine brings joy'","'Remember the Exodus'","'Pour it out as an offering'"),
    ("Deacon","What was the significance of the Passover lamb?","It foreshadowed Jesus, the Lamb of God","It was only a cultural tradition","It represented Moses","It symbolized wealth"),
    ("Deacon","What is a grain offering?","An offering of flour, oil, and frankincense — no blood","A harvest celebration","Bread for the priests","A tithe of wheat"),
    ("Deacon","What is a peace offering?","A voluntary offering of thanksgiving shared in a meal","A treaty between nations","An offering after war","A daily offering"),
    ("Pastor","What is the drink offering?","Wine poured out as a libation alongside other sacrifices","Drinking wine at feasts","Water from the Temple","A toast to the king"),
    ("Deacon","What did John the Baptist eat in the wilderness?","Locusts and wild honey","Bread and water","Manna","Figs and dates"),
    ("Deacon","What did Elijah's ravens bring him?","Bread and meat","Fish","Manna","Fruit"),
    ("Pastor","What are the 'bitter herbs' of Passover?","Herbs eaten to remember the bitterness of slavery in Egypt","Medicine","Herbs for healing","Seasonings for the lamb"),
    ("Deacon","What is the 'cup of blessing' in 1 Corinthians?","The communion cup — participation in Christ's blood","A toast at weddings","A Passover tradition only","A priest's cup"),
    ("Deacon","Why was the fruit of the tree of knowledge forbidden?","God tested Adam and Eve's obedience","It was poisonous","It belonged to someone else","It wasn't ripe"),
    ("Pastor","What was the 'meal offering' of Cain?","He offered fruit of the ground (not accepted by God)","He offered a lamb","He offered gold","He offered wine"),
    ("Pastor","Why was Abel's offering accepted over Cain's?","Abel offered the firstborn of his flock — a blood sacrifice of faith","He offered more","He prayed longer","He was older"),
    ("Deacon","What feast involves living in temporary shelters?","Sukkot / Tabernacles","Passover","Purim","Pentecost"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# BATTLES more
c = "Battles & Wars"
more = [
    ("Layperson","How many days did the Israelites march around Jericho?","7 days (once each day, seven times on the 7th day)","1 day","3 days","40 days"),
    ("Deacon","What strategy did God give Joshua to conquer Ai?","An ambush behind the city","A frontal attack","Surround and wait","Burn it from afar"),
    ("Deacon","Why did Israel lose the first battle of Ai?","Achan had stolen devoted things from Jericho","They didn't pray","They were outnumbered","They used wrong weapons"),
    ("Deacon","What did Achan steal?","A cloak, silver, and a bar of gold","The Ark","A sword","Manna"),
    ("Deacon","Who was Barak?","The military leader who fought alongside Deborah","A judge who succeeded Gideon","Samson's father","A Philistine general"),
    ("Pastor","How did Ehud defeat King Eglon?","He was left-handed and hid a sword on his right side","He used poison","He ambushed him at night","He challenged him to single combat"),
    ("Deacon","What did Samson use to kill 1,000 Philistines?","The jawbone of a donkey","A sword","His bare hands","A club"),
    ("Deacon","What was the source of Samson's strength?","His Nazirite vow (symbolized by his uncut hair)","His muscles","A magic ring","His diet"),
    ("Deacon","Who cut Samson's hair?","Delilah arranged for it — a man shaved his head","Delilah herself","A Philistine soldier","His mother"),
    ("Layperson","How did David defeat Goliath specifically?","Slung a stone that hit him in the forehead, then used Goliath's sword","Shot an arrow","Threw a spear","Used a sword"),
    ("Deacon","How tall was Goliath?","Over 9 feet (six cubits and a span)","7 feet","12 feet","15 feet"),
    ("Pastor","Who was Joab's role in David's kingdom?","Commander of David's army","Chief priest","Royal scribe","Tax collector"),
    ("Deacon","Who defeated the Midianites with only 300 men?","Gideon","David","Joshua","Samson"),
    ("Pastor","What test did God use to select Gideon's 300?","How they drank water from a stream","Their height","Their strength","Their weapons skill"),
    ("Deacon","What enemy did Saul fight throughout his reign?","The Philistines","The Egyptians","The Babylonians","The Moabites"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# PSALMS & PROVERBS more
c = "Psalms & Proverbs"
more = [
    ("Layperson","What is Psalm 23 about?","God as our shepherd who provides and protects","The creation of the world","The Exodus","The Temple"),
    ("Layperson","What does Psalm 1 say about the blessed person?","They meditate on God's law day and night","They are wealthy","They have many children","They live in Jerusalem"),
    ("Deacon","What does Proverbs say about a 'fool'?","A fool despises wisdom and instruction","A fool is always poor","A fool cannot read","A fool is always sick"),
    ("Deacon","What is the message of Psalm 51?","A prayer of repentance — David after his sin with Bathsheba","A victory song","A creation hymn","A wisdom psalm"),
    ("Deacon","What does Proverbs say about 'pride'?","Pride goes before destruction, a haughty spirit before a fall","Pride is a virtue","Pride builds nations","Pride pleases God"),
    ("Deacon","What Psalm says 'The heavens declare the glory of God'?","Psalm 19","Psalm 23","Psalm 119","Psalm 1"),
    ("Pastor","What is a messianic psalm?","A psalm that prophetically points to Jesus","Any psalm by David","A psalm with music","A psalm of praise"),
    ("Deacon","What is Psalm 91 about?","God's protection — 'He who dwells in the shelter of the Most High'","David's battles","Solomon's wisdom","The Exodus"),
    ("Deacon","What does Proverbs say about the 'tongue'?","Death and life are in the power of the tongue","The tongue is always good","The tongue cannot sin","The tongue only speaks truth"),
    ("Deacon","What is Psalm 139 about?","God's intimate, all-knowing, ever-present care","The law","The Temple","Battles"),
    ("Pastor","What are the Hallel psalms?","Psalms 113-118, sung at Jewish festivals","Psalms 1-10","Psalms 150","Psalms of David only"),
    ("Pastor","What is the 'Shepherd's Psalm' besides Psalm 23?","Psalm 100 — 'We are his people, the sheep of his pasture'","Psalm 1","Psalm 51","Psalm 119"),
    ("Deacon","What does Ecclesiastes conclude?","Fear God and keep His commandments — this is the whole duty of man","Life is meaningless","Enjoy pleasure","Seek wisdom above all"),
    ("Deacon","What does Song of Solomon celebrate?","Romantic love between a bride and groom","God's creation","Military victory","Temple worship"),
    ("Pastor","Who was Asaph?","A Levite musician who wrote several psalms","A king","A prophet","A priest"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# WOMEN more
c = "Women of the Bible"
more = [
    ("Layperson","Who said 'Where you go I will go'?","Ruth to Naomi","Mary to Joseph","Sarah to Abraham","Eve to Adam"),
    ("Layperson","Who was the queen that saved the Jews in Persia?","Esther","Ruth","Deborah","Jezebel"),
    ("Layperson","Who was the mother of John the Baptist?","Elizabeth","Mary","Anna","Martha"),
    ("Deacon","What did Hannah do after Samuel was weaned?","Gave him to serve at the Tabernacle under Eli","Kept him at home","Sent him to school","Took him to Egypt"),
    ("Deacon","Who hid the Israelite spies in Jericho?","Rahab","Deborah","Jael","Ruth"),
    ("Deacon","What did Jael do to Sisera?","Drove a tent peg through his temple while he slept","Poisoned him","Stabbed him with a sword","Dropped a millstone on him"),
    ("Deacon","Who was Vashti?","The Persian queen who refused the king's summons, replaced by Esther","Esther's sister","A prophetess","A servant"),
    ("Deacon","What did Mary Magdalene do when she saw the risen Jesus?","Recognized Him when He said her name","Doubted it was Him","Ran away","Fainted"),
    ("Deacon","Who anointed Jesus with expensive perfume?","Mary of Bethany","Martha","Mary Magdalene","The Samaritan woman"),
    ("Pastor","What song did Hannah pray after dedicating Samuel?","A prayer of praise that foreshadows Mary's Magnificat","Psalm 23","The Song of Moses","A lament"),
    ("Pastor","What is the Magnificat?","Mary's song of praise in Luke 1 — 'My soul magnifies the Lord'","A psalm of David","A prayer of Hannah","A hymn of the early church"),
    ("Deacon","Who was Haman's enemy in the book of Esther?","Mordecai (Esther's cousin)","Nehemiah","Daniel","Zerubbabel"),
    ("Deacon","What risk did Esther take to save her people?","She approached the king without being summoned — punishable by death","She fled Persia","She fought in battle","She refused to marry"),
    ("Layperson","Who sat at Jesus' feet while Martha served?","Mary of Bethany","Mary Magdalene","Elizabeth","Anna"),
    ("Layperson","What did Martha say to Jesus when Lazarus died?","'If you had been here, my brother would not have died'","'Why did you let this happen?'","'I don't believe anymore'","'Please bring him back'"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# PLACES more
c = "Places & Lands"
more = [
    ("Layperson","Where was Jesus crucified?","Just outside Jerusalem at Golgotha","Inside the Temple","In Bethlehem","On the Mount of Olives"),
    ("Layperson","Where was the Temple built?","Jerusalem — on Mount Moriah","Bethlehem","Hebron","Samaria"),
    ("Deacon","Where was Paul shipwrecked?","Malta","Crete","Cyprus","Sicily"),
    ("Deacon","What was special about the city of Antioch?","Believers were first called 'Christians' there","The Temple was there","Moses was born there","David was crowned there"),
    ("Deacon","What was Caesarea known for?","A Roman port city where Peter preached to Cornelius","David's capital","A site of miracles","The birthplace of Paul"),
    ("Deacon","Where did Abraham almost sacrifice Isaac?","Mount Moriah","Mount Sinai","Mount Nebo","Mount Carmel"),
    ("Pastor","What is Qumran known for?","The Dead Sea Scrolls were found there","Jesus was baptized there","Moses died there","Solomon's mines"),
    ("Deacon","Where did Jacob have his dream of a ladder?","Bethel","Beersheba","Shechem","Hebron"),
    ("Deacon","Where did the early church meet?","In homes and the Temple courts","In synagogues only","In purpose-built churches","Outdoors only"),
    ("Deacon","What happened at the Jordan River?","Israel crossed into Canaan; Jesus was baptized","Moses parted it","The walls fell","David fought Goliath"),
    ("Pastor","Where was the Decapolis?","A region of ten Greek cities east of the Jordan","A Roman province in Italy","A city in Egypt","A fortress in Jerusalem"),
    ("Layperson","Where did Jonah's great fish spit him out?","On dry land (near Nineveh)","In the sea","On an island","In a river"),
    ("Deacon","Where was the Tabernacle before the Temple was built?","Shiloh (primarily)","Jerusalem","Bethel","Hebron"),
    ("Pastor","Where is Armageddon?","The plain of Megiddo in northern Israel","A mountain in Judah","A desert in Egypt","A city in Babylon"),
    ("Deacon","What river flows through the Jordan Valley?","The Jordan River","The Nile","The Euphrates","The Tigris"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# NUMBERS & GENEALOGIES more
c = "Numbers & Genealogies"
more = [
    ("Layperson","How many brothers did Joseph have?","11","12","10","7"),
    ("Deacon","Who was the youngest of Jacob's sons?","Benjamin","Joseph","Dan","Zebulun"),
    ("Deacon","Which tribe provided the priests?","Levi","Judah","Benjamin","Ephraim"),
    ("Deacon","Which tribe did Jesus come from?","Judah","Levi","Benjamin","Ephraim"),
    ("Deacon","Who was David's great-grandmother?","Ruth","Rahab","Naomi","Tamar"),
    ("Pastor","How many generations does Matthew list from Abraham to Jesus?","42 (3 sets of 14)","40","33","70"),
    ("Pastor","How many generations from Adam to Noah?","10","7","12","20"),
    ("Deacon","How many books did Paul write?","13","7","21","9"),
    ("Deacon","How many minor prophets are there?","12","7","15","10"),
    ("Deacon","How many major prophets are there?","5 (Isaiah, Jeremiah, Lamentations, Ezekiel, Daniel)","4","3","7"),
    ("Layperson","How many Gospels are there?","4","3","5","7"),
    ("Deacon","How many letters are in the New Testament?","21","27","13","14"),
    ("Pastor","What is significant about the number 153 fish caught in John 21?","Scholars debate — possibly represents all types of fish / all nations","It's the number of known fish species","It's a code","It's Peter's lucky number"),
    ("Deacon","How old was David when he became king?","30","20","40","25"),
    ("Pastor","How long did David reign total?","40 years (7 in Hebron, 33 in Jerusalem)","33 years","50 years","20 years"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# KINGS more
c = "Kings & Kingdoms"
more = [
    ("Deacon","Who anointed Saul as king?","Samuel","Nathan","Elijah","Eli"),
    ("Deacon","Why did God reject Saul?","He disobeyed — offered sacrifice himself and spared Agag","He worshiped idols","He fled battle","He murdered innocents"),
    ("Deacon","Who was Goliath?","A Philistine giant champion warrior","A Moabite king","An Ammonite general","An Amalekite warrior"),
    ("Deacon","What did David take from Goliath after killing him?","His head and his sword","His armor only","His spear","His shield"),
    ("Deacon","Who was Jonathan to David?","His closest friend and Saul's son","His brother","His general","His priest"),
    ("Deacon","What covenant did Jonathan make with David?","A covenant of loyalty and friendship","A military alliance","A trade agreement","A peace treaty"),
    ("Deacon","What did the Queen of Sheba visit Solomon for?","To test his wisdom and see his wealth","To declare war","To form an alliance","To buy gold"),
    ("Pastor","What did Elijah do on Mount Carmel?","Built an altar, poured water on it, and God sent fire","Parted the sea","Healed a leper","Raised the dead"),
    ("Pastor","How did Jezebel die?","Thrown from a window and eaten by dogs","Struck by lightning","Died of disease","Killed in battle"),
    ("Pastor","Who was Omri?","A powerful king of Israel, father of Ahab","A prophet","A priest","A judge"),
    ("Deacon","What happened when the kingdom split?","10 tribes formed the north (Israel), 2 formed the south (Judah)","6 and 6","9 and 3","7 and 5"),
    ("Deacon","What king found the Book of the Law in the Temple?","Josiah","Hezekiah","Asa","Jehoshaphat"),
    ("Deacon","What did Josiah do after finding the Book of the Law?","Tore his robes, repented, and led religious reform","Ignored it","Burned it","Sent it to Babylon"),
    ("Pastor","Who was Jehu?","The king anointed to destroy Ahab's dynasty","A prophet","A priest","A governor"),
    ("Deacon","What was Hezekiah's tunnel?","A water tunnel he built to prepare Jerusalem for siege","A prison","An escape route","A mine"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# MIRACLES more
c = "Miracles"
more = [
    ("Layperson","What happened when Jesus touched the blind man's eyes?","He could see","He could hear","He was healed of leprosy","He walked"),
    ("Layperson","How did Jesus calm the storm?","He spoke to the wind and waves — 'Peace, be still'","He prayed","He sang","He raised his hands"),
    ("Deacon","What miracle did Elisha perform with oil for a widow?","Multiplied her oil to fill many jars to pay her debts","Turned water to oil","Made oil burn forever","Created oil from nothing"),
    ("Deacon","How was Naaman healed of leprosy?","By washing seven times in the Jordan River as Elisha instructed","By touching Elisha's cloak","By sacrificing a lamb","By praying at the Temple"),
    ("Deacon","What miracle happened to Elijah at the brook Cherith?","Ravens brought him bread and meat","Fish leaped into his hands","Water turned to wine","A tree bore instant fruit"),
    ("Deacon","What happened when Peter's shadow fell on the sick?","They were healed","Nothing","They died","They saw visions"),
    ("Pastor","What happened when Paul was bitten by a viper on Malta?","He was completely unharmed","He was healed after prayer","He died briefly","His hand swelled temporarily"),
    ("Deacon","Who did Peter raise from the dead?","Dorcas/Tabitha","Eutychus","Lazarus","Jairus' daughter"),
    ("Pastor","Who fell out a window during Paul's sermon and was raised?","Eutychus","Timothy","Silas","Titus"),
    ("Deacon","What miracle did Jesus do for the woman with the issue of blood?","She was healed when she touched His garment","He spoke and she was healed","He laid hands on her","He sent her to wash in a pool"),
    ("Deacon","How many lepers came back to thank Jesus?","Only 1 out of 10","All 10","5","None"),
    ("Layperson","What did Jesus do to Lazarus?","Raised him from the dead after 4 days","Healed his blindness","Healed his leprosy","Fed him"),
    ("Deacon","What happened to the fig tree Jesus cursed?","It withered immediately","It bore fruit","It caught fire","Nothing happened"),
    ("Pastor","What does the feeding of the 5,000 appear in?","All four Gospels — the only miracle besides the resurrection in all four","Only Matthew and John","Only the Synoptics","Only John"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# PROPHETS more
c = "Prophets"
more = [
    ("Layperson","What happened to Jonah when he ran from God?","He was swallowed by a great fish","He drowned","He was struck by lightning","He fell asleep"),
    ("Layperson","Where did God tell Jonah to go?","Nineveh","Tarshish","Jerusalem","Babylon"),
    ("Layperson","What happened when Jonah preached in Nineveh?","The entire city repented","They killed him","They ignored him","They worshiped him"),
    ("Deacon","What did Hosea's marriage to Gomer symbolize?","God's faithful love despite Israel's unfaithfulness","The new covenant","The law of Moses","The exile"),
    ("Deacon","What was Jeremiah called?","The weeping prophet","The fiery prophet","The silent prophet","The shepherd prophet"),
    ("Deacon","What did Ezekiel see in the valley of dry bones?","The bones coming together and coming to life — symbolizing Israel's restoration","A battle","A funeral","A flood"),
    ("Deacon","What were Daniel's friends' Babylonian names?","Shadrach, Meshach, and Abednego","Belteshazzar, Arioch, and Darius","Nebuchadnezzar, Belshazzar, and Cyrus","Daniel, Ezekiel, and Jeremiah"),
    ("Deacon","What were Daniel's friends' Hebrew names?","Hananiah, Mishael, and Azariah","Abraham, Isaac, and Jacob","Shadrach, Meshach, Abednego","Daniel, Ezra, Nehemiah"),
    ("Deacon","What did Daniel do when praying was outlawed?","He kept praying three times a day facing Jerusalem","He prayed secretly","He stopped praying","He fled"),
    ("Deacon","What happened to Daniel in the lion's den?","God shut the lions' mouths and he was unharmed","He fought the lions","He escaped through a window","He tamed the lions"),
    ("Pastor","What is the book of Lamentations about?","Mourning over the destruction of Jerusalem","Celebrating a victory","Praising God's creation","Prophesying the Messiah"),
    ("Pastor","What did Ezekiel act out to prophesy the siege of Jerusalem?","He built a model of Jerusalem and lay on his side for days","He wept publicly","He shaved his head","He fasted for 40 days"),
    ("Pastor","What did Jeremiah buy while Jerusalem was being besieged?","A field — as a sign that land would be bought again","A new scroll","A donkey","Incense"),
    ("Deacon","What writing appeared on the wall at Belshazzar's feast?","MENE MENE TEKEL UPHARSIN","HOLY HOLY HOLY","THE END IS NEAR","REPENT AND BELIEVE"),
    ("Deacon","What did the writing on the wall mean?","God had numbered, weighed, and divided Belshazzar's kingdom","Praise God","Build a temple","Flee Babylon"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

# DREAMS more
c = "Dreams & Visions"
more = [
    ("Layperson","What did Joseph's brothers' sheaves do in his dream?","Bowed down to his sheaf","Caught fire","Blew away","Grew taller"),
    ("Deacon","What did the seven fat cows in Pharaoh's dream represent?","Seven years of plenty","Seven kings","Seven plagues","Seven nations"),
    ("Deacon","What did the seven thin cows represent?","Seven years of famine","Seven wars","Seven plagues","Seven exiles"),
    ("Deacon","Why was Pharaoh troubled by his dreams?","No one in Egypt could interpret them","They were nightmares","He forgot them","They contradicted his plans"),
    ("Deacon","Who recommended Joseph to Pharaoh as a dream interpreter?","The cupbearer who had been in prison with Joseph","The baker","A priest","Pharaoh's wife"),
    ("Deacon","What did Nebuchadnezzar's statue dream mean?","Four successive world empires ending with God's eternal kingdom","Four seasons","Four elements","Four directions"),
    ("Pastor","What were the four metals of the statue?","Gold (head), silver (chest), bronze (belly), iron (legs), clay mix (feet)","All gold","Silver and gold only","Bronze and iron only"),
    ("Deacon","What did the dry bones coming to life symbolize?","Israel's national restoration and spiritual revival","A literal resurrection","A battle","The creation of Adam"),
    ("Deacon","What did Peter's sheet vision lead to?","The gospel being preached to Gentiles — starting with Cornelius","A new diet","A new Temple","Peter going to Rome"),
    ("Pastor","What did Daniel's four beasts represent?","Four world empires (like the statue — Babylon, Medo-Persia, Greece, Rome)","Four seasons","Four angels","Four plagues"),
    ("Layperson","Who interpreted Pharaoh's dreams?","Joseph","Moses","Daniel","Aaron"),
    ("Layperson","What happened after Joseph interpreted the dreams correctly?","Pharaoh made him second-in-command of Egypt","He was freed and sent home","He became a priest","Nothing changed"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,shuf(c1,[c2,c3,c4]),c1)

print(f"\n  After all expansions: {len(ALL)}")

# ============================================================================
# FINAL: ASSIGN IDS, COUNT, SAVE
# ============================================================================
for i, q in enumerate(ALL):
    q["id"] = hashlib.md5(f"{q['category']}-{q['difficulty']}-{q['question'][:50]}-{i}".encode()).hexdigest()[:12]

from collections import Counter
cat_counts = Counter(q["category"] for q in ALL)
diff_counts = Counter((q["category"], q["difficulty"]) for q in ALL)

print(f"\n{'='*60}")
print(f"TOTAL UNIQUE QUESTIONS: {len(ALL)}")
print(f"{'='*60}")
for cat in sorted(cat_counts.keys()):
    l = diff_counts.get((cat,"Layperson"),0)
    d = diff_counts.get((cat,"Deacon"),0)
    p = diff_counts.get((cat,"Pastor"),0)
    print(f"  {cat}: {cat_counts[cat]:4d} (L:{l:3d} D:{d:3d} P:{p:3d})")

out_path = "/home/claude/manna/manna_questions.json"
with open(out_path, "w") as f:
    json.dump(ALL, f, indent=2)
print(f"\nSaved to {out_path}")
print(f"File size: {os.path.getsize(out_path)/1024:.0f} KB")
