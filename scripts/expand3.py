#!/usr/bin/env python3
"""Expansion 3 — Template-heavy generation for maximum volume."""
import json, random, hashlib, os
random.seed(789)

with open("/home/claude/manna/manna_questions.json") as f:
    ALL = json.load(f)
existing = set(q["question"].strip().lower() for q in ALL)

def Q(cat,diff,q,opts,cor,exp=""):
    k=q.strip().lower()
    if k not in existing:
        existing.add(k)
        ALL.append({"category":cat,"difficulty":diff,"question":q,"options":opts,"correct":cor,"explanation":exp})

def S(c,ws):
    o=[c]+list(ws[:3]);random.shuffle(o);return o

# ============================================================================
# TESTAMENT QUESTIONS — 66 books
# ============================================================================
OT=["Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth",
"1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra","Nehemiah",
"Esther","Job","Psalms","Proverbs","Ecclesiastes","Song of Solomon","Isaiah","Jeremiah",
"Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah","Jonah","Micah","Nahum",
"Habakkuk","Zephaniah","Haggai","Zechariah","Malachi"]
NT=["Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians",
"Galatians","Ephesians","Philippians","Colossians","1 Thessalonians","2 Thessalonians",
"1 Timothy","2 Timothy","Titus","Philemon","Hebrews","James","1 Peter","2 Peter",
"1 John","2 John","3 John","Jude","Revelation"]

for book in OT:
    diff = "Layperson" if book in ["Genesis","Exodus","Psalms","Proverbs","Isaiah","Daniel","Jonah","Esther","Ruth","Job"] else "Deacon" if book in ["Joshua","Judges","1 Samuel","2 Samuel","1 Kings","2 Kings","Jeremiah","Ezekiel","Deuteronomy","Numbers","Leviticus"] else "Pastor"
    Q("Numbers & Genealogies",diff,f"Is the book of {book} in the Old or New Testament?",S("Old Testament",["New Testament","Neither — it's Apocrypha","Both testaments"]), "Old Testament")

for book in NT:
    diff = "Layperson" if book in ["Matthew","Mark","Luke","John","Acts","Romans","Revelation","James"] else "Deacon" if book in ["1 Corinthians","2 Corinthians","Galatians","Ephesians","Philippians","Hebrews","1 Peter","1 John"] else "Pastor"
    Q("Numbers & Genealogies",diff,f"Is the book of {book} in the Old or New Testament?",S("New Testament",["Old Testament","Neither — it's Apocrypha","Both testaments"]), "New Testament")

print(f"  After testament Qs: {len(ALL)}")

# ============================================================================
# CHAPTER COUNT QUESTIONS
# ============================================================================
CHAPTERS = {
    "Genesis":50,"Exodus":40,"Leviticus":27,"Numbers":36,"Deuteronomy":34,
    "Joshua":24,"Judges":21,"Ruth":4,"1 Samuel":31,"2 Samuel":24,
    "1 Kings":22,"2 Kings":25,"Ezra":10,"Nehemiah":13,"Esther":10,
    "Job":42,"Psalms":150,"Proverbs":31,"Ecclesiastes":12,"Song of Solomon":8,
    "Isaiah":66,"Jeremiah":52,"Lamentations":5,"Ezekiel":48,"Daniel":12,
    "Hosea":14,"Joel":3,"Amos":9,"Obadiah":1,"Jonah":4,"Micah":7,"Nahum":3,
    "Habakkuk":3,"Zephaniah":3,"Haggai":2,"Zechariah":14,"Malachi":4,
    "Matthew":28,"Mark":16,"Luke":24,"John":21,"Acts":28,"Romans":16,
    "1 Corinthians":16,"2 Corinthians":13,"Galatians":6,"Ephesians":6,
    "Philippians":4,"Colossians":4,"1 Thessalonians":5,"2 Thessalonians":3,
    "1 Timothy":6,"2 Timothy":4,"Titus":3,"Philemon":1,"Hebrews":13,
    "James":5,"1 Peter":5,"2 Peter":3,"1 John":5,"2 John":1,"3 John":1,
    "Jude":1,"Revelation":22
}
all_counts = sorted(set(CHAPTERS.values()))
notable_books = ["Genesis","Exodus","Psalms","Proverbs","Isaiah","Jeremiah","Ezekiel","Daniel",
    "Matthew","Mark","Luke","John","Acts","Romans","Revelation","Job","Ruth","Obadiah","Jonah",
    "Philemon","Hebrews","James","1 Corinthians","Galatians","Ephesians","1 Peter"]
for book in notable_books:
    ch = CHAPTERS[book]
    wrongs = [str(c) for c in all_counts if c != ch]
    random.shuffle(wrongs)
    diff = "Deacon" if book in ["Genesis","Psalms","Isaiah","Revelation","Matthew","Acts"] else "Pastor"
    Q("Numbers & Genealogies",diff,f"How many chapters does the book of {book} have?",S(str(ch),wrongs[:3]),str(ch))

print(f"  After chapter Qs: {len(ALL)}")

# ============================================================================
# "WHICH CAME FIRST" CHRONOLOGY QUESTIONS
# ============================================================================
CHRONO = [
    ("The creation of the world","The flood of Noah","Genesis & Creation","Layperson"),
    ("The flood of Noah","The Tower of Babel","Genesis & Creation","Layperson"),
    ("Abraham's call","The Exodus from Egypt","Genesis & Creation","Layperson"),
    ("The Exodus from Egypt","The conquest of Canaan","Moses & the Exodus","Layperson"),
    ("The period of the Judges","King Saul's reign","Battles & Wars","Deacon"),
    ("King David's reign","King Solomon's reign","Kings & Kingdoms","Layperson"),
    ("Solomon's Temple built","The kingdom divided","Kings & Kingdoms","Deacon"),
    ("The fall of the northern kingdom","The fall of Jerusalem (Judah)","Kings & Kingdoms","Deacon"),
    ("The Babylonian exile","The return under Ezra","Kings & Kingdoms","Deacon"),
    ("The rebuilding of the Temple","The rebuilding of Jerusalem's walls","Places & Lands","Deacon"),
    ("The birth of John the Baptist","The birth of Jesus","Life of Jesus","Layperson"),
    ("Jesus' baptism","Jesus' temptation in the wilderness","Life of Jesus","Deacon"),
    ("The feeding of the 5,000","The Transfiguration","Life of Jesus","Deacon"),
    ("The Triumphal Entry","The Last Supper","Life of Jesus","Deacon"),
    ("Jesus' crucifixion","Jesus' resurrection","Life of Jesus","Layperson"),
    ("Jesus' ascension","The day of Pentecost","The Apostles","Deacon"),
    ("Stephen's martyrdom","Paul's conversion","The Apostles","Deacon"),
    ("Paul's first missionary journey","Paul's letter to the Romans","Paul & His Letters","Pastor"),
    ("The destruction of Jerusalem (AD 70)","John writing Revelation","Revelation & End Times","Pastor"),
    ("Moses receiving the Law","David writing Psalms","Psalms & Proverbs","Deacon"),
    ("Elijah on Mount Carmel","Isaiah's ministry","Prophets","Deacon"),
    ("The fall of Jericho","Samson and Delilah","Battles & Wars","Deacon"),
    ("Ruth and Boaz","David and Goliath","Women of the Bible","Deacon"),
    ("Daniel in the lion's den","The return from exile","Prophets","Deacon"),
]
for ev1,ev2,cat,diff in CHRONO:
    Q(cat,diff,f"Which came first: {ev1} or {ev2}?",
      S(ev1,[ev2,"They happened at the same time","Neither is in the Bible"]),ev1)
    Q(cat,diff,f"Which came later: {ev1} or {ev2}?",
      S(ev2,[ev1,"They happened at the same time","Neither is in the Bible"]),ev2)

print(f"  After chronology Qs: {len(ALL)}")

# ============================================================================
# TWELVE TRIBES QUESTIONS
# ============================================================================
TRIBES_MOTHERS = {
    "Reuben":"Leah","Simeon":"Leah","Levi":"Leah","Judah":"Leah",
    "Dan":"Bilhah","Naphtali":"Bilhah","Gad":"Zilpah","Asher":"Zilpah",
    "Issachar":"Leah","Zebulun":"Leah","Joseph":"Rachel","Benjamin":"Rachel"
}
TRIBES_MEANINGS = {
    "Reuben":"See, a son","Simeon":"Heard","Levi":"Attached","Judah":"Praise",
    "Dan":"He judged","Naphtali":"My wrestling","Gad":"Good fortune","Asher":"Happy",
    "Issachar":"Reward","Zebulun":"Honor","Joseph":"May he add","Benjamin":"Son of my right hand"
}
TRIBES_FACTS = {
    "Reuben":("Lost his birthright for sleeping with Bilhah","Deacon"),
    "Simeon":("With Levi, massacred the men of Shechem","Deacon"),
    "Levi":("The priestly tribe — no land inheritance","Deacon"),
    "Judah":("The royal tribe — Jesus came from this line","Layperson"),
    "Dan":("First to fall into idolatry in Judges","Pastor"),
    "Naphtali":("Settled in northern Galilee","Pastor"),
    "Gad":("Settled east of the Jordan as warriors","Pastor"),
    "Asher":("Known for rich food and olive oil","Pastor"),
    "Issachar":("Known for understanding the times (1 Chronicles 12:32)","Pastor"),
    "Zebulun":("'Galilee of the nations' — Isaiah's prophecy","Pastor"),
    "Joseph":("Split into Ephraim and Manasseh for inheritance","Deacon"),
    "Benjamin":("Smallest tribe; Saul and Paul came from this tribe","Deacon"),
}

all_mothers_list = ["Leah","Rachel","Bilhah","Zilpah"]
for tribe, mother in TRIBES_MOTHERS.items():
    wrongs = [m for m in all_mothers_list if m != mother]
    Q("Numbers & Genealogies","Deacon",f"Which of Jacob's wives/concubines was the mother of {tribe}?",
      S(mother,wrongs+["Hagar"]),mother)

for tribe, meaning in TRIBES_MEANINGS.items():
    all_meanings = list(TRIBES_MEANINGS.values())
    wrongs = [m for m in all_meanings if m != meaning]
    random.shuffle(wrongs)
    Q("Numbers & Genealogies","Pastor",f"What does the tribal name '{tribe}' mean?",
      S(meaning,wrongs[:3]),meaning)

for tribe, (fact, diff) in TRIBES_FACTS.items():
    all_facts = [f for t,(f,d) in TRIBES_FACTS.items() if t != tribe]
    random.shuffle(all_facts)
    Q("Numbers & Genealogies",diff,f"What is the tribe of {tribe} known for?",
      S(fact,all_facts[:3]),fact)

print(f"  After tribes Qs: {len(ALL)}")

# ============================================================================
# KINGS OF JUDAH AND ISRAEL — extended questions
# ============================================================================
KINGS_JUDAH = [
    ("Rehoboam","Bad","Caused the kingdom to split by harsh taxation","Deacon"),
    ("Abijah","Bad","Brief reign, fought Jeroboam","Pastor"),
    ("Asa","Good","Removed idols and sought God","Deacon"),
    ("Jehoshaphat","Good","Appointed judges, allied with Ahab unwisely","Deacon"),
    ("Jehoram","Bad","Married Ahab's daughter, led Judah into idolatry","Pastor"),
    ("Ahaziah (Judah)","Bad","Killed by Jehu along with the house of Ahab","Pastor"),
    ("Athaliah","Bad","Only queen — usurped the throne, killed royal heirs","Deacon"),
    ("Joash","Good (mostly)","Repaired the Temple but later turned away","Deacon"),
    ("Amaziah","Good (mostly)","Defeated Edom but challenged Israel unwisely","Pastor"),
    ("Uzziah","Good (mostly)","Powerful but struck with leprosy for entering the Temple","Deacon"),
    ("Jotham","Good","Built the upper gate of the Temple","Pastor"),
    ("Ahaz","Bad","Practiced child sacrifice and made Assyrian alliance","Pastor"),
    ("Hezekiah","Good","Purified the Temple, trusted God against Assyria","Layperson"),
    ("Manasseh","Bad (then repented)","55-year reign of terrible idolatry, later repented in exile","Deacon"),
    ("Amon","Bad","Continued his father Manasseh's early idolatry","Pastor"),
    ("Josiah","Good","Found the Book of the Law and led the greatest reform","Layperson"),
    ("Jehoahaz","Bad","Reigned 3 months before Egypt deposed him","Pastor"),
    ("Jehoiakim","Bad","Burned Jeremiah's scroll","Pastor"),
    ("Jehoiachin","Bad","Surrendered to Nebuchadnezzar","Pastor"),
    ("Zedekiah","Bad","Last king — rebelled against Babylon, Jerusalem destroyed","Deacon"),
]

for king,quality,fact,diff in KINGS_JUDAH:
    Q("Kings & Kingdoms",diff,f"Was King {king} of Judah considered a good or bad king?",
      S(quality,["Good","Bad","Good (mostly)","Bad (then repented)"]),quality)
    all_facts = [f for k,q,f,d in KINGS_JUDAH if k != king]
    random.shuffle(all_facts)
    Q("Kings & Kingdoms",diff,f"What was King {king} of Judah known for?",
      S(fact,all_facts[:3]),fact)

KINGS_ISRAEL = [
    ("Jeroboam I","Set up golden calves at Dan and Bethel","Deacon"),
    ("Nadab","Assassinated by Baasha","Pastor"),
    ("Baasha","Warred against Judah constantly","Pastor"),
    ("Elah","Assassinated while drunk by his servant Zimri","Pastor"),
    ("Zimri","Reigned only 7 days before burning the palace on himself","Pastor"),
    ("Omri","Founded Samaria as capital, powerful but wicked","Pastor"),
    ("Ahab","Married Jezebel, promoted Baal worship, most wicked king","Deacon"),
    ("Ahaziah (Israel)","Fell through a lattice and died","Pastor"),
    ("Joram/Jehoram (Israel)","Killed by Jehu","Pastor"),
    ("Jehu","Destroyed Baal worship and Ahab's dynasty","Deacon"),
    ("Jeroboam II","Longest and most prosperous reign in the north","Pastor"),
    ("Hoshea","Last king — conquered by Assyria in 722 BC","Deacon"),
]

for king,fact,diff in KINGS_ISRAEL:
    all_facts = [f for k,f,d in KINGS_ISRAEL if k != king]
    random.shuffle(all_facts)
    Q("Kings & Kingdoms",diff,f"What was King {king} of Israel (northern kingdom) known for?",
      S(fact,all_facts[:3]),fact)

print(f"  After kings Qs: {len(ALL)}")

# ============================================================================
# JUDGES OF ISRAEL
# ============================================================================
JUDGES = [
    ("Othniel","First judge, nephew of Caleb, defeated Cushan-Rishathaim","Deacon"),
    ("Ehud","Left-handed judge who killed fat King Eglon with a hidden dagger","Deacon"),
    ("Shamgar","Killed 600 Philistines with an oxgoad","Pastor"),
    ("Deborah","Prophetess and judge who led Israel with Barak against Sisera","Layperson"),
    ("Gideon","Defeated Midianites with 300 men using trumpets, jars, and torches","Layperson"),
    ("Tola","Minor judge from Issachar who judged 23 years","Pastor"),
    ("Jair","Minor judge from Gilead with 30 sons riding 30 donkeys","Pastor"),
    ("Jephthah","Made a tragic vow that cost his daughter; defeated Ammonites","Deacon"),
    ("Ibzan","Minor judge from Bethlehem with 30 sons and 30 daughters","Pastor"),
    ("Elon","Minor judge from Zebulun who judged 10 years","Pastor"),
    ("Abdon","Minor judge with 40 sons and 30 grandsons riding 70 donkeys","Pastor"),
    ("Samson","Nazirite with supernatural strength who fought the Philistines","Layperson"),
]

for judge,fact,diff in JUDGES:
    all_facts = [f for j,f,d in JUDGES if j != judge]
    random.shuffle(all_facts)
    Q("Battles & Wars",diff,f"What was Judge {judge} known for?",S(fact,all_facts[:3]),fact)

print(f"  After judges Qs: {len(ALL)}")

# ============================================================================
# APOSTLE-SPECIFIC QUESTIONS
# ============================================================================
APOSTLE_FACTS = [
    ("Peter","Fisherman who became leader of the early church","Layperson"),
    ("Andrew","Peter's brother, first called by Jesus (per John)","Deacon"),
    ("James (son of Zebedee)","First apostle martyred — killed by Herod with a sword","Deacon"),
    ("John","The beloved disciple who wrote the Gospel, epistles, and Revelation","Deacon"),
    ("Philip","Asked Jesus 'Show us the Father' and brought Nathanael to Jesus","Deacon"),
    ("Bartholomew/Nathanael","Jesus said of him 'an Israelite in whom there is no deceit'","Deacon"),
    ("Matthew/Levi","Tax collector who left everything to follow Jesus and wrote a Gospel","Layperson"),
    ("Thomas/Didymus","Doubted the resurrection until he saw Jesus' wounds","Layperson"),
    ("James (son of Alphaeus)","Called 'James the Less' — one of the quieter apostles","Pastor"),
    ("Thaddaeus/Judas (not Iscariot)","Asked Jesus 'Why do you reveal yourself to us and not the world?'","Pastor"),
    ("Simon the Zealot","A former political revolutionary who followed Jesus","Deacon"),
    ("Judas Iscariot","The treasurer who betrayed Jesus for 30 silver coins","Layperson"),
]

for apostle,fact,diff in APOSTLE_FACTS:
    all_facts = [f for a,f,d in APOSTLE_FACTS if a != apostle]
    random.shuffle(all_facts)
    Q("The Apostles",diff,f"What is {apostle} best known for?",S(fact,all_facts[:3]),fact)

# Apostle calling/trade
APOSTLE_TRADES = [
    ("Peter","Fisherman","Layperson"),("Andrew","Fisherman","Layperson"),
    ("James (son of Zebedee)","Fisherman","Deacon"),("John","Fisherman","Deacon"),
    ("Matthew","Tax collector","Layperson"),("Paul","Tentmaker and Pharisee","Deacon"),
    ("Luke","Physician","Deacon"),("Simon the Zealot","Political activist/revolutionary","Deacon"),
]
all_trades = ["Fisherman","Tax collector","Tentmaker","Physician","Carpenter","Shepherd","Farmer","Soldier"]
for apostle,trade,diff in APOSTLE_TRADES:
    wrongs = [t for t in all_trades if t != trade]
    random.shuffle(wrongs)
    Q("The Apostles",diff,f"What was {apostle}'s occupation before following Jesus?",S(trade,wrongs[:3]),trade)

print(f"  After apostle Qs: {len(ALL)}")

# ============================================================================
# "I AM" STATEMENTS OF JESUS (John)
# ============================================================================
I_AM = [
    ("I am the bread of life","John 6:35","Whoever comes to me will never hunger","Deacon"),
    ("I am the light of the world","John 8:12","Whoever follows me will not walk in darkness","Deacon"),
    ("I am the door/gate","John 10:9","Anyone who enters through me will be saved","Deacon"),
    ("I am the good shepherd","John 10:11","The good shepherd lays down his life for the sheep","Layperson"),
    ("I am the resurrection and the life","John 11:25","Whoever believes in me will live even though they die","Layperson"),
    ("I am the way, the truth, and the life","John 14:6","No one comes to the Father except through me","Layperson"),
    ("I am the true vine","John 15:1","Every branch in me that bears no fruit He takes away","Deacon"),
]
all_refs = [r for _,r,_,_ in I_AM]
all_meanings = [m for _,_,m,_ in I_AM]
for statement,ref,meaning,diff in I_AM:
    wrongs_r = [r for r in all_refs if r != ref]
    random.shuffle(wrongs_r)
    Q("Life of Jesus",diff,f"Where did Jesus say '{statement}'?",S(ref,wrongs_r[:3]),ref)
    wrongs_m = [m for m in all_meanings if m != meaning]
    random.shuffle(wrongs_m)
    Q("Life of Jesus","Deacon",f"What did Jesus mean by '{statement}'?",S(meaning,wrongs_m[:3]),meaning)

print(f"  After I AM Qs: {len(ALL)}")

# ============================================================================
# BEATITUDES
# ============================================================================
BEATITUDES = [
    ("Blessed are the poor in spirit","for theirs is the kingdom of heaven","Deacon"),
    ("Blessed are those who mourn","for they shall be comforted","Deacon"),
    ("Blessed are the meek","for they shall inherit the earth","Layperson"),
    ("Blessed are those who hunger and thirst for righteousness","for they shall be satisfied","Deacon"),
    ("Blessed are the merciful","for they shall receive mercy","Deacon"),
    ("Blessed are the pure in heart","for they shall see God","Deacon"),
    ("Blessed are the peacemakers","for they shall be called sons of God","Deacon"),
    ("Blessed are those who are persecuted for righteousness","for theirs is the kingdom of heaven","Deacon"),
]
all_promises = [p for _,p,_ in BEATITUDES]
for beatitude,promise,diff in BEATITUDES:
    wrongs = [p for p in all_promises if p != promise]
    random.shuffle(wrongs)
    Q("Life of Jesus",diff,f"Complete this Beatitude: '{beatitude}...'",S(promise,wrongs[:3]),promise)

print(f"  After beatitude Qs: {len(ALL)}")

# ============================================================================
# ARMOR OF GOD (Ephesians 6)
# ============================================================================
ARMOR = [
    ("Belt","Truth","Deacon"),
    ("Breastplate","Righteousness","Deacon"),
    ("Shoes/Feet","The gospel of peace","Deacon"),
    ("Shield","Faith","Deacon"),
    ("Helmet","Salvation","Deacon"),
    ("Sword","The word of God / the Spirit","Deacon"),
]
all_virtues = [v for _,v,_ in ARMOR]
for piece,virtue,diff in ARMOR:
    wrongs = [v for v in all_virtues if v != virtue]
    random.shuffle(wrongs)
    Q("Paul & His Letters",diff,f"In the Armor of God (Ephesians 6), what does the {piece.lower()} represent?",
      S(virtue,wrongs[:3]),virtue)

print(f"  After armor Qs: {len(ALL)}")

# ============================================================================
# FRUITS OF THE SPIRIT (Galatians 5:22-23)
# ============================================================================
FRUITS = ["Love","Joy","Peace","Patience","Kindness","Goodness","Faithfulness","Gentleness","Self-control"]
NOT_FRUITS = ["Prosperity","Wisdom","Power","Courage","Intelligence","Wealth","Success","Ambition","Popularity"]
for nf in NOT_FRUITS:
    real = random.sample(FRUITS,3)
    Q("Paul & His Letters","Deacon",f"Which of these is NOT a fruit of the Spirit in Galatians 5?",
      S(nf,real),nf)

print(f"  After fruit Qs: {len(ALL)}")

# ============================================================================
# SEVEN CHURCHES OF REVELATION
# ============================================================================
CHURCHES = [
    ("Ephesus","Left their first love","Remember, repent, and do the first works","Deacon"),
    ("Smyrna","Suffering and poverty, but spiritually rich","Be faithful unto death and receive the crown of life","Deacon"),
    ("Pergamum","Held fast to Christ's name but tolerated false teaching","Repent or face the sword of His mouth","Deacon"),
    ("Thyatira","Good works but tolerated the false prophetess 'Jezebel'","Hold fast and receive authority over nations","Pastor"),
    ("Sardis","A reputation for being alive but actually dead","Wake up and strengthen what remains","Pastor"),
    ("Philadelphia","Kept God's word; given an open door no one can shut","Hold on; I will keep you from the hour of trial","Deacon"),
    ("Laodicea","Lukewarm — neither hot nor cold","Be zealous and repent; I stand at the door and knock","Deacon"),
]
for church,problem,instruction,diff in CHURCHES:
    all_problems = [p for c,p,i,d in CHURCHES if c != church]
    random.shuffle(all_problems)
    Q("Revelation & End Times",diff,f"What was the problem with the church in {church}?",S(problem,all_problems[:3]),problem)
    all_instructions = [i for c,p,i,d in CHURCHES if c != church]
    random.shuffle(all_instructions)
    Q("Revelation & End Times","Pastor",f"What did Christ instruct the church in {church} to do?",S(instruction,all_instructions[:3]),instruction)

print(f"  After churches Qs: {len(ALL)}")

# ============================================================================
# TEN COMMANDMENTS — individually
# ============================================================================
COMMANDMENTS = [
    ("First","You shall have no other gods before me","Layperson"),
    ("Second","You shall not make any carved image / idol","Layperson"),
    ("Third","You shall not take the LORD's name in vain","Layperson"),
    ("Fourth","Remember the Sabbath day to keep it holy","Layperson"),
    ("Fifth","Honor your father and your mother","Layperson"),
    ("Sixth","You shall not murder","Layperson"),
    ("Seventh","You shall not commit adultery","Layperson"),
    ("Eighth","You shall not steal","Layperson"),
    ("Ninth","You shall not bear false witness (lie)","Layperson"),
    ("Tenth","You shall not covet","Layperson"),
]
all_cmds = [c for _,c,_ in COMMANDMENTS]
for ordinal,cmd,diff in COMMANDMENTS:
    wrongs = [c for c in all_cmds if c != cmd]
    random.shuffle(wrongs)
    Q("Laws & Commandments",diff,f"What is the {ordinal} Commandment?",S(cmd,wrongs[:3]),cmd)
    # Reverse: which number is this?
    all_ordinals = [o for o,c,d in COMMANDMENTS if o != ordinal]
    random.shuffle(all_ordinals)
    Q("Laws & Commandments","Deacon",f"Which commandment says '{cmd}'?",S(f"The {ordinal}",
      [f"The {o}" for o in all_ordinals[:3]]),f"The {ordinal}")

print(f"  After commandments Qs: {len(ALL)}")

# ============================================================================
# PLAGUES OF EGYPT — detailed
# ============================================================================
PLAGUES = [
    ("First","Water to blood","Layperson"),
    ("Second","Frogs","Layperson"),
    ("Third","Gnats (lice)","Deacon"),
    ("Fourth","Flies","Deacon"),
    ("Fifth","Livestock disease","Deacon"),
    ("Sixth","Boils","Deacon"),
    ("Seventh","Hail","Deacon"),
    ("Eighth","Locusts","Deacon"),
    ("Ninth","Darkness for three days","Deacon"),
    ("Tenth","Death of the firstborn","Layperson"),
]
all_plagues = [p for _,p,_ in PLAGUES]
for ordinal,plague,diff in PLAGUES:
    wrongs = [p for p in all_plagues if p != plague]
    random.shuffle(wrongs)
    Q("Moses & the Exodus",diff,f"What was the {ordinal.lower()} plague of Egypt?",S(plague,wrongs[:3]),plague)
    all_ords = [o for o,p,d in PLAGUES if o != ordinal]
    random.shuffle(all_ords)
    Q("Moses & the Exodus","Deacon",f"Which plague number was '{plague}'?",
      S(f"The {ordinal}",[ f"The {o}" for o in all_ords[:3]]),f"The {ordinal}")

print(f"  After plagues Qs: {len(ALL)}")

# ============================================================================
# FAMOUS PAIRS
# ============================================================================
PAIRS = [
    ("Who were the first two brothers?","Cain and Abel","Jacob and Esau","Moses and Aaron","Peter and Andrew","Genesis & Creation","Layperson"),
    ("Who were the twin sons of Isaac?","Jacob and Esau","Cain and Abel","Ephraim and Manasseh","Perez and Zerah","Genesis & Creation","Layperson"),
    ("Who were Moses' siblings?","Aaron and Miriam","Joshua and Caleb","Nadab and Abihu","Eleazar and Ithamar","Moses & the Exodus","Layperson"),
    ("Who were the sons of Zebedee?","James and John","Peter and Andrew","Philip and Bartholomew","Matthew and Thomas","The Apostles","Deacon"),
    ("Who were the first apostles called?","Peter and Andrew (or Andrew and another)","James and John","Matthew and Thomas","Philip and Bartholomew","The Apostles","Deacon"),
    ("Who were Abraham and Sarah's rival pair?","Hagar and Ishmael","Lot and his wife","Laban and Leah","Esau and his wife","Genesis & Creation","Deacon"),
    ("Who were the famous missionary partners?","Paul and Barnabas (then Paul and Silas)","Peter and John","James and Andrew","Matthew and Mark","Paul & His Letters","Deacon"),
    ("Who were the husband-wife ministry team?","Aquila and Priscilla","Ananias and Sapphira","Boaz and Ruth","Joseph and Mary","Paul & His Letters","Deacon"),
    ("Who were the sons of Joseph?","Ephraim and Manasseh","Reuben and Simeon","Perez and Zerah","Dan and Naphtali","Numbers & Genealogies","Deacon"),
    ("Who were the two faithful spies?","Joshua and Caleb","Moses and Aaron","Nadab and Abihu","Phinehas and Eleazar","Moses & the Exodus","Layperson"),
    ("Who were David's two notable enemies turned allies?","Abner and Mephibosheth (at different times)","Goliath and Saul","Absalom and Joab","Nathan and Gad","Kings & Kingdoms","Pastor"),
    ("Who were the two prophets at the Transfiguration?","Moses and Elijah","Abraham and David","Isaiah and Jeremiah","Samuel and Nathan","Life of Jesus","Deacon"),
    ("Who were Martha and Mary's brother?","Lazarus","Simon","Joseph","Andrew","Life of Jesus","Layperson"),
    ("Who were Ruth and Orpah?","Naomi's daughters-in-law","Sisters","Mother and daughter","Cousins","Women of the Bible","Deacon"),
    ("Who were Shadrach, Meshach, and Abednego?","Daniel's three friends in Babylon","Three prophets","Three judges","Three kings","Prophets","Layperson"),
]
for question,correct,w1,w2,w3,cat,diff in PAIRS:
    Q(cat, diff, question, S(correct,[w1,w2,w3]), correct)

print(f"  After pairs Qs: {len(ALL)}")

# ============================================================================
# MISCELLANEOUS FILL-INS PER CATEGORY (to balance)
# ============================================================================

# More FOOD
c="Food, Feasts & Offerings"
more=[
    ("Deacon","What is the 'Feast of Weeks' another name for?","Pentecost / Shavuot","Passover","Tabernacles","Trumpets"),
    ("Deacon","What animal was the primary Passover sacrifice?","A lamb without blemish","A bull","A goat","A dove"),
    ("Pastor","What is the 'wave offering'?","A portion lifted and waved before the LORD as a dedication","A goodbye offering","An ocean-side sacrifice","A prayer gesture"),
    ("Deacon","What did Ruth gather in Boaz's field?","Leftover grain (gleaning)","Flowers","Stones","Wood"),
    ("Pastor","What is 'firstfruits'?","The first portion of the harvest, offered to God before eating the rest","The best fruit","A title for Jesus","A feast of wine"),
    ("Deacon","What did Abigail bring David to prevent bloodshed?","Bread, wine, sheep, grain, raisin cakes, and fig cakes","Gold","Weapons","A letter"),
    ("Deacon","What did the ravens bring Elijah?","Bread and meat, morning and evening","Fish","Manna","Fruit"),
    ("Deacon","What did Jesus say about fasting?","Don't look gloomy — wash your face, anoint your head","Fast every day","Never fast","Fast only on Sabbath"),
    ("Pastor","What is the 'heave offering'?","A portion of a sacrifice lifted up and given to the priest","A stone thrown in worship","A burnt offering","A peace offering"),
    ("Deacon","What food did the Israelites crave in the wilderness?","The fish, cucumbers, melons, leeks, onions, and garlic of Egypt","Pizza","Bread","Lamb"),
    ("Layperson","What is the significance of bread and wine at communion?","They represent Jesus' body and blood given for us","They represent harvest","They represent creation","They represent Israel"),
    ("Deacon","What did Ezekiel eat in his vision?","A scroll that tasted like honey","Manna","Bread","A fruit"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# More ANGELS & DEMONS
c="Angels & Demons"
more=[
    ("Layperson","What is Satan also called?","The devil, the serpent, the dragon, the accuser","Only Lucifer","Only Beelzebub","Only the tempter"),
    ("Deacon","How did Satan appear to Eve?","As a serpent","As an angel of light","As a man","As a lion"),
    ("Deacon","What does the Bible say about Satan's original state?","He was an angel who fell through pride","He was always evil","He was a human who became a demon","He was created evil"),
    ("Pastor","What does Isaiah 14 say about Lucifer's fall?","'How you have fallen from heaven, morning star' — fallen through pride","He was cast out for stealing","He challenged Michael","He destroyed a city"),
    ("Pastor","What does Ezekiel 28 describe about the 'king of Tyre'?","Often interpreted as describing Satan — a guardian cherub in Eden who fell","A literal king only","A prophet","An angel who remained faithful"),
    ("Deacon","What power does Satan have according to the Bible?","He can tempt, accuse, and deceive, but is limited by God's sovereignty","Unlimited power","No power at all","Power over nature"),
    ("Deacon","What did Jesus call Satan?","'The father of lies' and 'a murderer from the beginning'","'The prince of peace'","'The angel of light'","'The morning star'"),
    ("Pastor","What are 'principalities and powers' Paul mentions?","Spiritual forces of evil in the heavenly realms","Roman rulers","Jewish authorities","Church leaders"),
    ("Deacon","What happened when Jesus cast out the legion of demons?","They entered a herd of pigs that ran into the sea","They vanished","They entered the townspeople","They went to another region"),
    ("Deacon","Where did the demon-possessed pigs incident happen?","The region of the Gadarenes/Gerasenes","Jerusalem","Capernaum","Nazareth"),
    ("Pastor","What is 'Gehenna'?","The Greek word for hell — based on the Valley of Hinnom outside Jerusalem","A Greek city","A type of demon","An angel"),
    ("Deacon","What does the Bible say happens to demons at the end?","They will be thrown into the lake of fire with Satan","They will be forgiven","They will be destroyed","They will become human"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# More LAWS
c="Laws & Commandments"
more=[
    ("Deacon","What is the difference between clean and unclean animals?","Clean animals could be eaten and sacrificed; unclean could not","Clean are wild, unclean are domestic","Clean are large, unclean are small","There is no difference"),
    ("Deacon","What was the purpose of the Day of Atonement?","Annual cleansing of all Israel's sins through sacrifice","A harvest celebration","A national holiday","A time to rest"),
    ("Pastor","What was the scapegoat?","One of two goats on Atonement Day — sins confessed on it, then released into the wilderness","A sacrifice burned on the altar","A goat for food","A pet"),
    ("Deacon","What did Jesus teach about divorce?","Moses allowed it for hard hearts, but God's intent was permanent marriage","Divorce is always fine","Divorce is always sinful","He didn't address it"),
    ("Deacon","What are the 'clean' and 'unclean' rules about?","Ritual purity for worship — what you eat, touch, and how you prepare for God's presence","Personal hygiene only","Cooking methods","Social class"),
    ("Pastor","What is the 'law of the leper'?","A detailed process for a healed leper to be declared clean by a priest","A law banning lepers","A cure for leprosy","A prayer for healing"),
    ("Deacon","What did Jesus say about the greatest in the kingdom?","Whoever humbles himself like a child","The strongest","The wisest","The richest"),
    ("Deacon","What is the purpose of the Law according to Paul?","It reveals sin and shows our need for a Savior","It saves us","It replaces grace","It only applies to Jews"),
    ("Pastor","What are 'blue tassels' (tzitzit)?","Fringes on garments to remind Israelites of God's commandments","Decorations","Priestly garments only","A sign of wealth"),
    ("Deacon","What did Jesus say about the Sabbath to the Pharisees?","'The Son of Man is Lord of the Sabbath'","'The Sabbath is abolished'","'Keep it more strictly'","'It applies only to priests'"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# More PROPHECY
c="Prophecy & Fulfillment"
more=[
    ("Layperson","Did the Old Testament predict Jesus' birth, death, and resurrection?","Yes — hundreds of prophecies point to Jesus","No","Only His birth","Only His death"),
    ("Deacon","What psalm describes lots being cast for the Messiah's clothing?","Psalm 22","Psalm 23","Psalm 1","Psalm 119"),
    ("Deacon","How was Zechariah 12:10 fulfilled?","Jesus was 'pierced' on the cross — 'they will look on me whom they have pierced'","In the Temple","During the Exodus","At the Transfiguration"),
    ("Pastor","What is the 'Immanuel sign' in Isaiah?","A virgin would conceive — a sign of God's presence and plan","A rainbow","A star","A voice from heaven"),
    ("Deacon","Which prophecy predicts the Messiah as 'a man of sorrows'?","Isaiah 53","Psalm 22","Zechariah 9","Micah 5"),
    ("Pastor","What is 'typology' in biblical prophecy?","Old Testament persons, events, or things that foreshadow Christ","A type of writing","A genealogy method","A translation technique"),
    ("Pastor","How is Isaac a 'type' of Christ?","Both were sons promised by God, willing sacrifices on a mountain","Both were shepherds","Both were kings","Both lived in Egypt"),
    ("Pastor","How is Joseph a 'type' of Christ?","Both were rejected by brothers, sold for silver, exalted to save many","Both were priests","Both were prophets","Both wrote psalms"),
    ("Deacon","What prophet said 'A star shall come out of Jacob'?","Balaam (Numbers 24:17)","Isaiah","Micah","Jeremiah"),
    ("Deacon","What did the prophet Simeon prophesy about baby Jesus?","He was 'a light for revelation to the Gentiles and glory for Israel'","He would be a warrior","He would rule Rome","He would rebuild the Temple"),
    ("Pastor","What does 'the stone the builders rejected' refer to?","Christ — rejected by Jewish leaders but becomes the cornerstone","The Temple foundation","A literal stone","Peter"),
    ("Deacon","Where is the 'suffering servant' passage?","Isaiah 52:13-53:12","Psalm 22","Zechariah 9","Jeremiah 31"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# More PLACES
c="Places & Lands"
more=[
    ("Deacon","What is the 'Promised Land'?","Canaan — the land God promised to Abraham and his descendants","Egypt","Babylon","Moab"),
    ("Deacon","What is the 'Fertile Crescent'?","The arc of rich land from Egypt through Canaan to Mesopotamia","A valley in Israel","The Garden of Eden","The Nile Delta"),
    ("Deacon","Where was Haran?","A city in northern Mesopotamia where Abraham's family settled","A city in Egypt","A city in Canaan","A city in Persia"),
    ("Pastor","What was Lachish?","A fortified city in Judah conquered by Assyria and Babylon","A city in Egypt","A port in Phoenicia","A mountain in Galilee"),
    ("Deacon","Where was the wilderness of Judea?","The barren region between Jerusalem and the Dead Sea","Northern Galilee","The Sinai peninsula","East of the Jordan"),
    ("Deacon","What is the Sea of Galilee also called?","Lake Gennesaret, Sea of Tiberias, Lake Kinneret","The Dead Sea","The Mediterranean","The Red Sea"),
    ("Deacon","What is the Dead Sea known for?","The lowest point on earth; extremely salty; no fish live in it","Fresh water","Major trade route","Fish abundance"),
    ("Pastor","Where was Galatia?","A region in central Asia Minor (Turkey)","A city in Greece","An island in the Mediterranean","A province in Egypt"),
    ("Deacon","Where is the Valley of Elah?","Where David fought Goliath — in the lowlands of Judah","Mount Sinai","The Jordan Valley","North of Jerusalem"),
    ("Deacon","What happened at Caesarea Philippi?","Peter confessed Jesus as the Christ","Jesus was baptized","Paul was converted","The Temple was rebuilt"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# More PSALMS
c="Psalms & Proverbs"
more=[
    ("Deacon","Which Psalm says 'The heavens declare the glory of God'?","Psalm 19","Psalm 23","Psalm 1","Psalm 119"),
    ("Deacon","What is Psalm 51 about?","David's prayer of repentance after his sin with Bathsheba","A creation hymn","A battle song","A wedding psalm"),
    ("Deacon","What Psalm starts 'Blessed is the man who does not walk in the counsel of the wicked'?","Psalm 1","Psalm 23","Psalm 119","Psalm 100"),
    ("Pastor","What is Psalm 110 about?","A messianic psalm — 'The LORD said to my Lord, sit at my right hand'","David's battles","Solomon's wisdom","The creation"),
    ("Deacon","What does Proverbs 31 describe?","A woman of noble character","A wise king","A brave warrior","A good farmer"),
    ("Deacon","What does Ecclesiastes say about time?","There is a time for everything — a season for every activity under heaven","Time is meaningless","Time is infinite","Time stands still"),
    ("Deacon","What is the 'Song of Songs' about?","Romantic love between a bride and groom — also interpreted as God's love for His people","Military conquest","The creation","Temple worship"),
    ("Pastor","What does 'a threefold cord is not easily broken' mean?","Relationships are stronger with God at the center (Ecclesiastes 4:12)","Ropes should be braided","Three is a holy number","Build with strong materials"),
    ("Deacon","What Psalm is known as the 'creation psalm'?","Psalm 104","Psalm 23","Psalm 1","Psalm 119"),
    ("Deacon","What Psalm is a prayer for God's mercy and forgiveness?","Psalm 51","Psalm 23","Psalm 100","Psalm 150"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# More WOMEN
c="Women of the Bible"
more=[
    ("Deacon","What did Deborah prophesy about the battle with Sisera?","The glory would go to a woman — Jael killed Sisera","Israel would lose","Barak would be the hero","The battle would last 7 days"),
    ("Deacon","How did Ruth end up in Bethlehem?","She followed Naomi from Moab after both their husbands died","She was born there","She was kidnapped","She ran away from Moab"),
    ("Deacon","What was Ruth's famous declaration to Naomi?","'Where you go I will go; your people shall be my people, your God my God'","'I will stay in Moab'","'Send me away'","'I will find another husband'"),
    ("Deacon","How did Ruth meet Boaz?","She gleaned in his field and he noticed her loyalty to Naomi","At a wedding","In the Temple","Through Naomi's arrangement only"),
    ("Layperson","What was the name of Moses' sister who watched his basket?","Miriam","Deborah","Zipporah","Hannah"),
    ("Deacon","Who was the only female judge of Israel?","Deborah","Miriam","Huldah","Esther"),
    ("Layperson","What brave act did Esther perform?","She risked her life by approaching the king uninvited to save her people","She fought in battle","She fled Persia","She wrote a book"),
    ("Pastor","What did Priscilla and Aquila do for Apollos?","Took him aside and explained the gospel more accurately","Rebuked him publicly","Reported him to the elders","Ignored him"),
    ("Deacon","Who was Timothy's grandmother?","Lois","Eunice","Anna","Phoebe"),
    ("Pastor","Who was Rahab's notable descendant?","King David (and ultimately Jesus)","Moses","Abraham","Joshua"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# More MIRACLES
c="Miracles"
more=[
    ("Layperson","How many people did Jesus feed with 5 loaves and 2 fish?","About 5,000 men plus women and children","1,000","500","10,000"),
    ("Deacon","What did the disciples say before Jesus calmed the storm?","'Teacher, don't you care if we drown?'","'Let's go back'","'Pray for us'","'Row harder'"),
    ("Deacon","What happened to the man with Legion?","After demons left, he was found sitting, clothed, and in his right mind","He died","He ran away","He became a priest"),
    ("Deacon","What did the formerly blind man tell the Pharisees?","'One thing I know: I was blind but now I see'","'Jesus is a prophet'","'I don't know who healed me'","'It was just medicine'"),
    ("Deacon","What happened when Jesus healed on the Sabbath?","Religious leaders were angry and plotted against Him","Everyone praised God","The Temple was closed","Nothing controversial"),
    ("Deacon","What did Peter do after Jesus healed the lame man?","Preached to the crowd about Jesus' power","Ran away","Stayed silent","Asked for money"),
    ("Pastor","What is significant about Jesus healing the man born blind?","It showed Jesus' power over lifelong conditions and revealed spiritual blindness of leaders","It was His first miracle","It happened on a mountain","It was in the Temple"),
    ("Deacon","How did Jesus raise the widow's son at Nain?","He touched the coffin and said 'Young man, I say to you, arise'","He prayed for three days","He wept","He sang a psalm"),
    ("Deacon","What happened when Elisha's bones touched a dead man?","The dead man came back to life","Nothing happened","The bones turned to dust","A light appeared"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# More DREAMS
c="Dreams & Visions"
more=[
    ("Deacon","What did the image in Nebuchadnezzar's dream represent?","Successive world empires — Babylon, Medo-Persia, Greece, Rome","Four seasons","The four elements","Four patriarchs"),
    ("Deacon","What destroyed the statue in the dream?","A rock cut without hands — representing God's eternal kingdom","An earthquake","Lightning","A sword"),
    ("Pastor","What do the 'four beasts' of Daniel 7 represent?","Four successive empires (same as the statue — different symbolism)","Four angels","Four plagues","Four prophets"),
    ("Deacon","What did Peter's vision teach the early church?","That God accepts people from every nation — Gentiles are not unclean","A new diet","New Temple rules","That pork is permitted"),
    ("Pastor","What is the 'seventy weeks' vision of Daniel?","A prophetic timeline pointing to the Messiah — 490 years","A literal 70 weeks","A punishment period","A festival schedule"),
    ("Layperson","Who dreamed his brothers' sheaves bowed to his?","Joseph","Jacob","David","Abraham"),
    ("Pastor","What vision did Stephen have as he was dying?","He saw heaven open and Jesus standing at God's right hand","A bright light","An angel","A rainbow"),
    ("Deacon","What did the seraphim cry in Isaiah's vision?","'Holy, holy, holy is the LORD of hosts'","'Glory to God'","'Amen'","'Hallelujah'"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# More NUMBERS
c="Numbers & Genealogies"
more=[
    ("Deacon","What tribe did the priests come from?","Levi","Judah","Benjamin","Ephraim"),
    ("Deacon","What tribe did the kings of Judah come from?","Judah","Levi","Benjamin","Ephraim"),
    ("Deacon","What tribe did Saul come from?","Benjamin","Judah","Levi","Ephraim"),
    ("Deacon","What tribe did Paul come from?","Benjamin","Judah","Levi","Dan"),
    ("Deacon","What two tribes formed the southern kingdom?","Judah and Benjamin","Judah and Levi","Judah and Simeon","Judah and Reuben"),
    ("Deacon","How many minor prophets are there?","12","7","15","10"),
    ("Pastor","How many chapters in the shortest book of the OT?","1 (Obadiah)","2","3","5"),
    ("Pastor","How many verses in the shortest book of the NT?","13 or 14 (2 John or 3 John)","5","25","50"),
    ("Deacon","How many days was Jesus seen after His resurrection?","40 days","3 days","7 days","50 days"),
    ("Deacon","How many people were in the upper room before Pentecost?","About 120","12","70","500"),
    ("Pastor","How many people saw the risen Christ at once (per 1 Cor 15)?","More than 500","120","12","70"),
    ("Deacon","How many letters did John write?","3 (1 John, 2 John, 3 John) plus Revelation","2","5","1"),
    ("Deacon","How many plagues could Egyptian magicians replicate?","2 (water to blood and frogs)","All 10","None","5"),
    ("Pastor","What is the total number of people saved on the ark?","8","12","6","10"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# ============================================================================
# SAVE
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
