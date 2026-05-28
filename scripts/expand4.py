#!/usr/bin/env python3
"""Expansion 4 — Fill underserved categories and add new patterns."""
import json, random, hashlib, os
random.seed(1010)

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
# TRUE/FALSE STYLE (4 options: True + 3 plausible wrong corrections)
# ============================================================================
TF = [
    # Genesis
    ("Genesis & Creation","Layperson","God created the world in 7 days.","False — He created in 6 days and rested on the 7th","True","False — 5 days","False — 3 days"),
    ("Genesis & Creation","Layperson","The forbidden fruit is called an apple in the Bible.","False — the Bible never names the fruit","True — it says apple","False — it says fig","False — it says grape"),
    ("Genesis & Creation","Deacon","Abraham had only one son.","False — he had Ishmael, Isaac, and 6 sons with Keturah","True","False — he had exactly 2","False — he had 12"),
    ("Genesis & Creation","Deacon","Jacob had 10 sons.","False — he had 12 sons","True","False — he had 7","False — he had 14"),
    ("Genesis & Creation","Pastor","Noah took exactly 2 of every animal.","False — clean animals were taken in sevens","True — 2 of every kind","False — he took 10","False — only land animals"),
    # Moses
    ("Moses & the Exodus","Layperson","Moses wrote the Ten Commandments himself.","False — God wrote them on stone tablets","True","False — Aaron wrote them","False — Joshua wrote them"),
    ("Moses & the Exodus","Deacon","Moses entered the Promised Land.","False — he was not allowed to enter; he died on Mount Nebo","True","False — he entered briefly","False — Joshua stopped him"),
    ("Moses & the Exodus","Deacon","The Israelites wandered for 30 years.","False — they wandered for 40 years","True — 30 years","False — 20 years","False — 50 years"),
    # Life of Jesus
    ("Life of Jesus","Layperson","Jesus was born in Nazareth.","False — He was born in Bethlehem but grew up in Nazareth","True","False — He was born in Jerusalem","False — He was born in Capernaum"),
    ("Life of Jesus","Layperson","The Bible says three wise men visited Jesus.","False — it says 'Magi' but never gives a number (tradition says 3 due to 3 gifts)","True — exactly 3","False — there were 12","False — there were 7"),
    ("Life of Jesus","Deacon","Jesus was 33 when He began His ministry.","False — He was about 30 (Luke 3:23)","True — exactly 33","False — He was 25","False — He was 40"),
    ("Life of Jesus","Deacon","Judas hanged himself AND fell headlong (Acts 1).","True — both accounts describe his death from different perspectives","False — only hanged","False — only fell","False — he was executed"),
    # Apostles
    ("The Apostles","Deacon","Paul was one of the original 12 apostles.","False — he was called later; Matthias replaced Judas","True","False — he replaced Peter","False — he was the 11th"),
    ("The Apostles","Deacon","All the apostles were fishermen.","False — Matthew was a tax collector, Paul a tentmaker, etc.","True","False — they were all farmers","False — they were all priests"),
    # Revelation
    ("Revelation & End Times","Deacon","The book of Revelation was written by Paul.","False — it was written by John","True","False — by Peter","False — by Luke"),
    ("Revelation & End Times","Deacon","666 is the only number associated with the Beast.","False — some manuscripts say 616","True — 666 is the only one","False — 999 is also used","False — 777 is used"),
    # General
    ("Numbers & Genealogies","Layperson","There are 72 books in the Protestant Bible.","False — there are 66","True","False — there are 73","False — there are 39"),
    ("Numbers & Genealogies","Deacon","The word 'Bible' appears in the Bible.","False — the word 'Bible' does not appear","True","False — only in the New Testament","False — only in Psalms"),
    ("Numbers & Genealogies","Deacon","The word 'Trinity' appears in the Bible.","False — the concept is biblical but the word isn't used","True","False — only in John","False — only in Revelation"),
    ("Psalms & Proverbs","Deacon","David wrote all 150 Psalms.","False — others including Asaph, Moses, Solomon, and anonymous authors contributed","True — all 150","False — Solomon wrote most","False — Moses wrote most"),
    ("Prophets","Deacon","Jonah was swallowed by a whale.","False — the Bible says 'a great fish' (not specifically a whale)","True — it says whale","False — it says shark","False — it says sea monster"),
    ("Women of the Bible","Layperson","Eve ate an apple.","False — the Bible says 'fruit' without specifying the type","True — Genesis says apple","False — it was a fig","False — it was a pomegranate"),
    ("Angels & Demons","Deacon","The Bible describes Satan with horns and a pitchfork.","False — that image comes from medieval art, not the Bible","True","False — only in Revelation","False — only in Daniel"),
    ("Parables","Deacon","The Good Samaritan is found in the book of Matthew.","False — it's found in Luke 10","True — Matthew 10","False — Mark 10","False — John 10"),
    ("Places & Lands","Deacon","The Garden of Eden is in Israel.","False — it's described as being in Mesopotamia (between Tigris and Euphrates)","True — near Jerusalem","False — in Egypt","False — in Jordan"),
    ("Food, Feasts & Offerings","Deacon","The Last Supper was a Passover meal.","True — Jesus celebrated Passover with His disciples","False — it was a normal dinner","False — it was a Sabbath meal","False — it was a wedding feast"),
    ("Battles & Wars","Deacon","David killed Goliath with a sword.","False — he used a sling and stone, then took Goliath's own sword","True — with a sword","False — with a spear","False — with a bow"),
    ("Laws & Commandments","Deacon","The Ten Commandments include 'Love your neighbor as yourself.'","False — that's Leviticus 19:18 and Jesus' teaching, not one of the ten","True","False — it's the 11th commandment","False — it's in the New Testament only"),
    ("Prophecy & Fulfillment","Deacon","Isaiah 53 was written after Jesus lived.","False — Isaiah lived ~700 years before Jesus","True — written in the 1st century","False — written during exile","False — written by Paul"),
    ("Dreams & Visions","Deacon","Daniel interpreted his own dreams.","Both — he interpreted others' dreams AND received his own visions from God","False — he only interpreted others'","True — only his own","False — he never had visions"),
]
for cat,diff,statement,correct,w1,w2,w3 in TF:
    Q(cat,diff,f"True or false: {statement}",S(correct,[w1,w2,w3]),correct)

print(f"  After T/F Qs: {len(ALL)}")

# ============================================================================
# "FILL THE BLANK" VERSE COMPLETIONS
# ============================================================================
BLANKS = [
    ("Life of Jesus","Layperson","'For God so loved the ___ that He gave His only Son...'","world","church","people","Jews"),
    ("Life of Jesus","Layperson","'I am the ___, the truth, and the life.'","way","light","bread","door"),
    ("Psalms & Proverbs","Layperson","'The LORD is my ___; I shall not want.'","shepherd","king","father","light"),
    ("Psalms & Proverbs","Layperson","'The fear of the LORD is the beginning of ___.","wisdom/knowledge","strength","wealth","life"),
    ("Paul & His Letters","Deacon","'For the wages of sin is ___, but the gift of God is eternal life.'","death","pain","suffering","darkness"),
    ("Paul & His Letters","Layperson","'I can do all things through ___ who strengthens me.'","Christ","God","prayer","faith"),
    ("Paul & His Letters","Deacon","'And now these three remain: faith, hope, and ___. But the greatest is ___.","love... love","hope... hope","faith... faith","grace... grace"),
    ("Life of Jesus","Deacon","'In the beginning was the ___, and the ___ was with God.'","Word... Word","Light... Light","Spirit... Spirit","Truth... Truth"),
    ("Psalms & Proverbs","Deacon","'Trust in the LORD with all your ___ and lean not on your own understanding.'","heart","mind","strength","soul"),
    ("Life of Jesus","Deacon","'You are the ___ of the world. A city set on a hill cannot be hidden.'","light","salt","hope","way"),
    ("Life of Jesus","Deacon","'You are the ___ of the earth. But if it loses its saltiness...'","salt","light","bread","seed"),
    ("Prophecy & Fulfillment","Deacon","'For unto us a child is born, unto us a ___ is given.'","son","king","prophet","priest"),
    ("Life of Jesus","Layperson","'Ask and it shall be ___; seek and you shall find.'","given to you","yours","done","answered"),
    ("Genesis & Creation","Layperson","'In the ___ God created the heavens and the earth.'","beginning","first day","morning","darkness"),
    ("Moses & the Exodus","Layperson","'Let my ___ go!' — Moses to Pharaoh.","people","nation","brothers","slaves"),
    ("Paul & His Letters","Deacon","'By ___ you have been saved, through faith — and this is not from yourselves.'","grace","works","law","sacrifice"),
    ("Life of Jesus","Deacon","'Greater ___ has no one than this: to lay down one's life for friends.'","love","faith","courage","strength"),
    ("The Apostles","Deacon","'But you will receive ___ when the Holy Spirit comes upon you.'","power","wisdom","peace","visions"),
    ("Psalms & Proverbs","Deacon","'Your ___ is a lamp to my feet and a light to my path.'","word","law","love","spirit"),
    ("Life of Jesus","Layperson","'Do not ___, or you too will be judged.'","judge","steal","lie","covet"),
    ("Revelation & End Times","Deacon","'I am the ___ and the Omega, the Beginning and the End.'","Alpha","First","Light","Word"),
    ("Paul & His Letters","Deacon","'Do not be ___ — God cannot be mocked. A man reaps what he sows.'","deceived","proud","lazy","afraid"),
    ("Psalms & Proverbs","Deacon","'___ goes before destruction, a haughty spirit before a fall.'","Pride","Anger","Envy","Greed"),
    ("Life of Jesus","Layperson","'Blessed are the ___, for they shall inherit the earth.'","meek","strong","rich","wise"),
    ("Life of Jesus","Deacon","'Blessed are the ___ in heart, for they shall see God.'","pure","humble","brave","wise"),
    ("Prophets","Deacon","'What does the LORD require? To act justly, love ___, and walk humbly.'","mercy","truth","faith","hope"),
    ("Paul & His Letters","Deacon","'The fruit of the Spirit is love, joy, ___, patience, kindness...'","peace","power","wisdom","grace"),
    ("Life of Jesus","Layperson","'Come to me, all who are ___ and heavy laden, and I will give you rest.'","weary","sinful","lost","poor"),
    ("Life of Jesus","Deacon","'I am the vine; you are the ___.'","branches","fruit","leaves","roots"),
    ("Psalms & Proverbs","Deacon","'Delight yourself in the LORD, and He will give you the ___ of your heart.'","desires","peace","wisdom","strength"),
]
for cat,diff,q,c1,c2,c3,c4 in BLANKS:
    Q(cat,diff,f"Complete the verse: {q}",S(c1,[c2,c3,c4]),c1)

print(f"  After blanks Qs: {len(ALL)}")

# ============================================================================
# EXTENDED PER-CATEGORY QUESTIONS — targeting low counts
# ============================================================================

# PARABLES (currently only 84 — need more)
c="Parables"
more=[
    ("Layperson","What is a parable?","A short story that teaches a spiritual lesson","A prophecy","A miracle","A prayer"),
    ("Layperson","Who taught using parables?","Jesus","Moses","Paul","David"),
    ("Layperson","In the Lost Coin parable, how many coins did the woman have?","10","100","7","3"),
    ("Layperson","What does the woman do when she finds the lost coin?","Calls friends to rejoice with her","Hides it","Gives it to the Temple","Buys bread"),
    ("Deacon","In the parable of the Sower, what do the seeds on the path represent?","Those who hear but the devil snatches the word away","Rocky ground","Thorns","Good soil"),
    ("Deacon","What does the rocky soil represent?","Those who receive the word with joy but have no root and fall away in trouble","The path","Thorns","Good soil"),
    ("Deacon","In the Parable of the Wheat and Tares, who sowed the tares?","An enemy (the devil)","The farmer","A servant","The wind"),
    ("Deacon","When are the tares separated from the wheat?","At the harvest (the end of the age)","Immediately","After one year","Never"),
    ("Deacon","What does the pearl of great price represent?","The kingdom of heaven — worth giving everything for","Wealth","A literal pearl","The Temple"),
    ("Deacon","In the Parable of the Talents, how many talents did the first servant receive?","5","10","1","3"),
    ("Deacon","What did the servant with one talent do?","Buried it in the ground","Invested it","Lost it","Gave it away"),
    ("Deacon","What did the master say to the faithful servants?","'Well done, good and faithful servant'","'You may rest now'","'Take more'","'Go tell others'"),
    ("Pastor","What is unique about the Parable of the Growing Seed (Mark 4)?","It's only found in Mark — the kingdom grows mysteriously on its own","It's in all four Gospels","It's about a literal farm","It teaches about money"),
    ("Deacon","What happened to the invited guests in the Wedding Banquet parable?","They refused to come, so the host invited everyone from the streets","They all attended","They fought over seats","They brought gifts"),
    ("Pastor","What is unusual about the Parable of the Shrewd Manager?","Jesus seems to commend dishonesty — but the lesson is about wise use of resources","It's the longest parable","It's the only funny parable","It contradicts other teachings"),
    ("Deacon","In the Rich Man and Lazarus, where did Lazarus go after death?","Abraham's bosom / paradise","The rich man's house","Back to earth","Nowhere"),
    ("Deacon","Could the rich man cross to Lazarus?","No — a great chasm was fixed between them","Yes, after repenting","Yes, with an angel","Yes, after 1000 years"),
    ("Deacon","What did the rich man ask Abraham to do?","Send Lazarus to warn his brothers","Let him cross over","Send water","Forgive him"),
    ("Deacon","In the Good Samaritan, who passed by the wounded man first?","A priest","A Levite","A merchant","A soldier"),
    ("Deacon","Who passed by second?","A Levite","A priest","A Pharisee","A Sadducee"),
    ("Deacon","Why was it surprising that a Samaritan helped?","Jews and Samaritans were bitter enemies","Samaritans were poor","Samaritans were violent","Samaritans were strangers"),
    ("Layperson","What did the father give the Prodigal Son when he returned?","A ring, robe, sandals, and a feast with a fattened calf","A lecture","Work to do","Nothing"),
    ("Deacon","What did the Prodigal Son end up doing at his lowest point?","Feeding pigs — the ultimate shame for a Jew","Begging","Stealing","Sleeping in streets"),
    ("Pastor","What does the Prodigal Son's far country represent?","A life of sin far from God","A literal foreign land","Egypt","Babylon"),
    ("Deacon","In the Ten Virgins, what did the foolish virgins lack?","Extra oil for their lamps","Lamps","Wicks","Knowledge of the groom"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# PAUL (need more Layperson)
c="Paul & His Letters"
more=[
    ("Layperson","Where did Paul write many of his letters from?","Prison","A church","A school","His home"),
    ("Layperson","What chapter is called the 'love chapter'?","1 Corinthians 13","Romans 8","John 3","Psalm 23"),
    ("Layperson","What does Paul say about love in 1 Corinthians 13?","Love is patient, love is kind...","Love is a feeling","Love is weakness","Love is optional"),
    ("Layperson","How did Paul escape Damascus after his conversion?","Lowered in a basket through the city wall","He walked out","He rode a horse","An angel freed him"),
    ("Layperson","What did Paul preach everywhere he went?","Jesus Christ crucified and risen","Jewish Law","Roman citizenship","Greek philosophy"),
    ("Deacon","What did Paul and Barnabas disagree about?","Taking John Mark on their next journey","Theology","Which cities to visit","Money"),
    ("Deacon","Where did Paul give his famous speech about the 'unknown god'?","Athens — at the Areopagus","Rome","Corinth","Ephesus"),
    ("Deacon","What riot happened in Ephesus?","Silversmiths rioted because Paul's preaching hurt their idol business","A food riot","A political riot","A religious festival"),
    ("Deacon","What was the 'thorn in Paul's flesh'?","An unspecified affliction — God said 'My grace is sufficient'","Blindness","A broken leg","Persecution only"),
    ("Deacon","What did Paul say about running the race?","Run to win — discipline your body like an athlete","Walk slowly","Rest often","Let others run"),
    ("Layperson","How many shipwrecks did Paul experience?","At least 3 (2 Corinthians 11:25)","1","None","5"),
    ("Deacon","What is the key verse of Romans?","'For all have sinned and fall short of the glory of God' (3:23)","'In the beginning'","'God is love'","'Faith without works is dead'"),
    ("Deacon","What does Galatians teach about freedom?","Christ set us free from the Law — stand firm in that freedom","Freedom means no rules","Freedom only for Jews","Freedom from Rome"),
    ("Pastor","What is Paul's theology of 'adoption'?","Believers are adopted as God's children with full inheritance rights","A metaphor for baptism","A Jewish practice","A Roman custom only"),
    ("Layperson","Did Paul ever meet Jesus in person during Jesus' earthly ministry?","No — he met the risen Christ on the Damascus road","Yes — he was a disciple","Yes — he saw the crucifixion","Yes — he was at the Last Supper"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# REVELATION (need more Layperson)
c="Revelation & End Times"
more=[
    ("Layperson","Who wins at the end of Revelation?","God and His people — good triumphs over evil","Satan","No one","It's unclear"),
    ("Layperson","What does Revelation promise to those who overcome?","Eternal life, the tree of life, a new name, and the New Jerusalem","Wealth","Power on earth","Earthly kingdoms"),
    ("Layperson","Is the book of Revelation meant to frighten Christians?","No — it's meant to encourage believers that God wins in the end","Yes — it's a warning of doom","It's only for scholars","It's not for today"),
    ("Layperson","What is heaven described as in Revelation?","A place with no more tears, death, mourning, crying, or pain","Floating on clouds","A garden only","A city of gold only"),
    ("Deacon","What is the 'tribulation'?","A period of great suffering and God's judgment before Christ's return","A single event","A metaphor","Past history only"),
    ("Deacon","What does 'second coming' mean?","Jesus will return to earth visibly and bodily","A spiritual return only","A metaphor","Reincarnation"),
    ("Deacon","What are the '24 elders' in Revelation?","Heavenly beings around God's throne — possibly representing all believers","24 apostles","Jewish and Gentile leaders","Angels"),
    ("Pastor","What is the 'Antichrist'?","A future world leader who opposes Christ — described in Daniel, 2 Thessalonians, Revelation","A demon only","A past figure only","A metaphor for sin"),
    ("Pastor","What does 'premillennialism' teach?","Christ returns BEFORE the 1,000-year reign and rules on earth","Christ returns after the millennium","There is no millennium","The millennium is symbolic"),
    ("Deacon","What is the 'new heaven and new earth'?","God's complete renewal of creation — described in Revelation 21","A different planet","A metaphor","Heaven only"),
    ("Layperson","What is the 'throne room' scene in Revelation?","A vision of God on His throne surrounded by worship","A court trial","A battle","A feast"),
    ("Deacon","What does the Lamb with seven horns and seven eyes represent?","Jesus Christ — perfect power and perfect knowledge","A literal lamb","An angel","A symbol of Israel"),
    ("Pastor","What is 'inaugurated eschatology'?","The kingdom has already begun in Christ but is not yet fully realized","A future-only view","A past-only view","A political theory"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# GENESIS more
c="Genesis & Creation"
more=[
    ("Layperson","How did God create the world?","By speaking — 'Let there be...'","By hand","By thought alone","Through angels"),
    ("Layperson","What did God say after each day of creation?","'It was good'","'It is done'","'Be fruitful'","Nothing"),
    ("Layperson","What was the first thing God said to Adam?","'Be fruitful and multiply' (with Eve)","'Do not eat'","'Name the animals'","'Build a shelter'"),
    ("Deacon","How did God make Adam?","From the dust of the ground and breathed life into him","From water","From light","From nothing"),
    ("Deacon","What was Adam's first task?","Naming the animals","Building a house","Planting a garden","Worshiping"),
    ("Deacon","What happened after the Fall?","God cursed the serpent, ground, and added pain to childbirth; He made garments","Nothing changed","They were immediately expelled","They died"),
    ("Deacon","What did God say to the serpent?","'On your belly you shall go, and dust you shall eat'","'You shall rule the earth'","'You are forgiven'","'Leave this place'"),
    ("Pastor","What is the 'protoevangelium' (first gospel) in Genesis 3:15?","The promise that the woman's seed would crush the serpent's head","Adam's repentance","Eve's prayer","Noah's covenant"),
    ("Deacon","Why did God confuse languages at Babel?","The people were uniting in prideful rebellion against God","They spoke too loud","They built too high","They worshiped idols"),
    ("Layperson","Who was Abraham's first son?","Ishmael","Isaac","Jacob","Esau"),
    ("Deacon","What did Sarah do when God said she'd have a son?","She laughed","She cried","She prayed","She denied it"),
    ("Deacon","What did Abraham name the place where God provided a ram?","Jehovah Jireh (The LORD Will Provide)","Bethel","Moriah","Beersheba"),
    ("Layperson","What was Joseph known for in Egypt?","Interpreting dreams and managing the famine","Building pyramids","Leading the army","Writing laws"),
    ("Layperson","How did Joseph's brothers react when they learned who he was?","They were terrified, but Joseph forgave them","They ran away","They fought him","They didn't believe him"),
    ("Deacon","What final act did Joseph perform for his father Jacob?","Took his body back to Canaan for burial as Jacob requested","Buried him in Egypt","Built a monument","Named a city after him"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# MOSES more
c="Moses & the Exodus"
more=[
    ("Layperson","What did the Israelites celebrate the night before leaving Egypt?","The first Passover","A farewell feast","A fast","Nothing"),
    ("Layperson","What happened to the Egyptian army at the Red Sea?","The waters closed over them and they drowned","They retreated","They surrendered","They followed Israel to Canaan"),
    ("Deacon","What did the Israelites complain about at Marah?","The water was bitter","The food was bad","It was too hot","Moses was too slow"),
    ("Deacon","How did God make the bitter water sweet?","Moses threw a piece of wood into it","He struck it","He prayed over it","Aaron blessed it"),
    ("Deacon","What covenant did God make at Sinai?","If Israel obeyed, they would be His special people, a kingdom of priests","A land covenant only","A promise of wealth","A military alliance"),
    ("Deacon","What were the two censuses in Numbers about?","Counting men able to go to war","Counting animals","Counting possessions","Counting families"),
    ("Pastor","What is the Shema (Deuteronomy 6:4-5)?","'Hear O Israel: the LORD our God, the LORD is one. Love Him with all your heart'","The Ten Commandments","A song of Moses","A priestly blessing"),
    ("Deacon","What was the pillar of cloud and fire?","God's visible presence guiding and protecting Israel","A natural phenomenon","An angel","A signal fire"),
    ("Layperson","What did God provide when the people had no water?","Water from a rock when Moses struck/spoke to it","Rain","A river appeared","Melted snow"),
    ("Deacon","Why were the Levites chosen to serve God?","They rallied to Moses after the golden calf incident","They were the largest tribe","They were the smartest","They volunteered"),
    ("Pastor","What is the 'Book of the Covenant' (Exodus 21-23)?","Laws God gave along with the Ten Commandments covering civil and ceremonial matters","The book of Genesis","A hidden scroll","A contract with Egypt"),
    ("Layperson","How did God speak to Moses?","Face to face, as a man speaks to a friend","Through dreams only","Through angels only","Through thunder only"),
    ("Deacon","What three offices did Moses hold?","Prophet, priest (interceding), and leader/judge","King, priest, prophet","Warrior, builder, teacher","Farmer, shepherd, priest"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# BATTLES more
c="Battles & Wars"
more=[
    ("Layperson","What instrument did the Israelites play marching around Jericho?","Trumpets (ram's horns/shofars)","Drums","Harps","Flutes"),
    ("Deacon","What did Gideon do with a fleece to test God?","Put out a fleece — asked for dew on fleece/dry ground, then reversed","Threw it in a river","Burned it","Wore it into battle"),
    ("Deacon","What weapons did Gideon's 300 men carry?","Trumpets, clay jars, and torches","Swords and shields","Slings and stones","Bows and arrows"),
    ("Layperson","How did David know he could beat Goliath?","He had killed a lion and a bear while protecting his sheep","He was trained by Saul","An angel told him","He had special armor"),
    ("Deacon","What did Goliath say to David?","'Am I a dog that you come at me with sticks?'","'You are too small'","'Run away, boy'","'Bring your army'"),
    ("Deacon","What happened after David killed Goliath?","The Philistine army fled and Israel pursued them","Peace was declared","Saul rewarded David immediately","Nothing happened"),
    ("Deacon","Who was Absalom's revolt against?","His own father, King David","Solomon","Saul","The Philistines"),
    ("Deacon","How did Absalom die?","His hair caught in a tree and Joab killed him","In battle","By David's hand","He fell from a horse"),
    ("Pastor","What was the Battle of Carchemish?","Egypt's defeat by Babylon (605 BC) — ending Egyptian dominance","Israel vs Philistia","Judah vs Israel","Assyria vs Egypt"),
    ("Deacon","Who was Joshua's first battle after crossing the Jordan?","Jericho","Ai","Gibeon","Hazor"),
    ("Pastor","How did Jehoshaphat win without fighting?","He sent singers ahead praising God — God set ambushes among the enemies","He prayed all night","He built a wall","He negotiated peace"),
    ("Layperson","What weapon did Samson use to defeat 1,000 Philistines?","The jawbone of a donkey","A sword","His bare hands","A club"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# LIFE OF JESUS more
c="Life of Jesus"
more=[
    ("Layperson","What did Jesus teach His disciples to pray?","The Lord's Prayer — 'Our Father, who art in heaven...'","Psalm 23","The Shema","A song of praise"),
    ("Layperson","What is the Lord's Prayer about?","Praising God, asking for daily needs, forgiveness, and protection","Only asking for things","Only praise","Only confession"),
    ("Deacon","What did Jesus say about worry?","Look at the birds — God feeds them; don't worry about tomorrow","Worry is good","Plan everything","Trust only yourself"),
    ("Deacon","What did Jesus teach about prayer?","Pray in private, don't use vain repetition, and persist","Only pray in public","Pray once a day","Don't bother God"),
    ("Deacon","What is the Golden Rule Jesus taught?","Do to others what you would have them do to you","An eye for an eye","Love only your friends","Keep all the laws"),
    ("Deacon","What did Jesus say about enemies?","Love your enemies and pray for those who persecute you","Defeat your enemies","Ignore your enemies","Run from your enemies"),
    ("Deacon","What did Jesus do when He entered Jerusalem the last time?","Wept over the city because it didn't recognize the time of God's coming","Celebrated","Healed everyone","Went straight to the Temple"),
    ("Deacon","What did Jesus predict about the Temple?","Not one stone would be left on another — it would be completely destroyed","It would last forever","It would be enlarged","It would be moved"),
    ("Deacon","What cup did Jesus pray about in Gethsemane?","The cup of suffering — 'Not my will but yours be done'","A literal cup","The cup of blessing","A Passover cup"),
    ("Pastor","What is the 'Johannine Comma'?","A textual variant in 1 John about the Trinity — debated by scholars","A punctuation mark","A Greek verb","A Hebrew letter"),
    ("Layperson","What did Jesus promise about the Holy Spirit?","He would send a Helper/Comforter who would guide them into all truth","A new Temple","A new king","A new law"),
    ("Deacon","What is the 'Great Commission'?","Jesus' command to make disciples of all nations, baptizing and teaching them","The Ten Commandments","The Sermon on the Mount","Paul's mission"),
    ("Layperson","What was the sign above Jesus' cross?","'Jesus of Nazareth, King of the Jews'","'This is a criminal'","'Messiah'","'Son of God'"),
    ("Deacon","In how many languages was the sign above the cross written?","3 — Aramaic/Hebrew, Latin, and Greek","1","2","4"),
    ("Deacon","What did Jesus say about children?","'Let the little children come to me' and 'the kingdom belongs to such as these'","'Send them away'","'They must wait'","'Teach them the Law first'"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# NUMBERS more (reduce over-representation)
# WOMEN more
c="Women of the Bible"
more=[
    ("Layperson","What makes Ruth special in Bible history?","She was a non-Israelite who became an ancestor of King David and Jesus","She was the first queen","She was the first prophetess","She built the Temple"),
    ("Deacon","What was Boaz to Ruth?","Her kinsman-redeemer — he married her and restored Naomi's family line","Her brother","Her servant","Her neighbor"),
    ("Deacon","What is a 'kinsman-redeemer'?","A close relative who redeems family property and marries a widow to continue the family line","A judge","A priest","A prophet"),
    ("Layperson","Who was the only woman to rule Judah?","Athaliah — she usurped the throne","Deborah","Esther","Jezebel"),
    ("Deacon","What did Naomi tell Ruth to do at the threshing floor?","Lie at Boaz's feet and uncover them — a custom requesting marriage/redemption","Dance","Sing","Harvest grain"),
    ("Pastor","Who was Tamar who dressed as a prostitute?","Judah's daughter-in-law — she deceived him to continue the family line after he wronged her","A Canaanite queen","A priestess","David's daughter"),
    ("Layperson","Who was the woman at the well?","A Samaritan woman with five past husbands whom Jesus offered living water","Mary Magdalene","Martha","Rahab"),
    ("Deacon","What did the woman at the well do after meeting Jesus?","Told her whole town about Him — 'Come see a man who told me everything I've done'","Kept it secret","Ran away","Ignored Him"),
    ("Pastor","Who was Jezebel in Revelation?","A symbolic name for a false prophetess in the church at Thyatira","The literal OT queen","An angel","A Roman woman"),
    ("Deacon","Who was the woman who anointed Jesus' feet with tears?","A sinful woman in Luke 7 — Jesus forgave her sins","Martha","Mary Magdalene","Joanna"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# PROPHETS more
c="Prophets"
more=[
    ("Deacon","Why was Elijah fed by ravens?","He was hiding from King Ahab during a drought he had prophesied","He was in prison","He was lost","He was fasting"),
    ("Deacon","What did God tell Elijah after the victory on Mount Carmel?","Elijah fled from Jezebel and God spoke to him in a still small voice at Horeb","Elijah became king","Elijah died","Elijah went to heaven immediately"),
    ("Deacon","What did Elijah leave for Elisha?","His cloak/mantle — symbolizing the passing of prophetic authority","A scroll","A sword","A crown"),
    ("Deacon","What did Elisha ask for when Elijah was taken up?","A double portion of Elijah's spirit","Wisdom","Long life","Wealth"),
    ("Deacon","How many miracles did Elisha perform?","About twice as many as Elijah (tradition says 14 vs 7)","The same number","Fewer","None"),
    ("Pastor","What is the 'suffering servant' debate?","Whether Isaiah 53 refers to the Messiah, Israel as a nation, or both","Whether Isaiah wrote it","Whether it's prophecy or history","Whether it's literal"),
    ("Deacon","Why did God judge the northern kingdom?","Persistent idolatry — worshiping golden calves, Baal, and other gods","One specific sin","For being too powerful","For not paying tribute"),
    ("Deacon","Why did God judge Judah?","Idolatry, injustice, and breaking the covenant despite prophetic warnings","For losing battles","For being too small","For not building temples"),
    ("Deacon","What makes a 'major prophet' major?","The length of their book — not their importance","They were more important","They lived longer","They performed more miracles"),
    ("Layperson","Who is the prophet most associated with Christmas?","Isaiah — 'For unto us a child is born' and 'a virgin shall conceive'","Jeremiah","Micah only","Malachi"),
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
