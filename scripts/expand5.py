#!/usr/bin/env python3
"""Expansion 5 — More questions for volume."""
import json, random, hashlib, os
random.seed(2024)

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
# "WHO AM I?" CLUE-BASED QUESTIONS
# ============================================================================
WAI = [
    ("I was thrown into a pit by my brothers, sold as a slave, but rose to rule Egypt.","Joseph","David","Moses","Daniel","Genesis & Creation","Layperson"),
    ("I killed a giant with a sling and a stone and later became king of Israel.","David","Joshua","Samson","Gideon","Kings & Kingdoms","Layperson"),
    ("I built an ark to save my family and animals from a worldwide flood.","Noah","Abraham","Moses","Adam","Genesis & Creation","Layperson"),
    ("I led Israel out of Egypt through a parted sea but never entered the Promised Land.","Moses","Joshua","Aaron","Caleb","Moses & the Exodus","Layperson"),
    ("I was the wisest king who built God's Temple but turned to idols later in life.","Solomon","David","Hezekiah","Josiah","Kings & Kingdoms","Layperson"),
    ("I was a judge who defeated Midian with only 300 men.","Gideon","Samson","Deborah","Ehud","Battles & Wars","Deacon"),
    ("I was swallowed by a great fish for running from God.","Jonah","Daniel","Elijah","Amos","Prophets","Layperson"),
    ("I denied Jesus three times but became the leader of the early church.","Peter","Thomas","James","Andrew","The Apostles","Layperson"),
    ("I was a Pharisee who persecuted Christians until Jesus appeared to me on a road.","Paul (Saul)","Nicodemus","Gamaliel","Stephen","Paul & His Letters","Layperson"),
    ("I was taken to heaven in a chariot of fire without dying.","Elijah","Enoch","Moses","Elisha","Prophets","Deacon"),
    ("I was a Moabite woman who stayed loyal to my mother-in-law and married Boaz.","Ruth","Esther","Rahab","Naomi","Women of the Bible","Layperson"),
    ("I hid Hebrew spies in Jericho and was saved when the walls fell.","Rahab","Deborah","Jael","Ruth","Women of the Bible","Deacon"),
    ("I was queen of Persia and saved my people from genocide.","Esther","Ruth","Deborah","Jezebel","Women of the Bible","Layperson"),
    ("I was Jacob's favorite wife and the mother of Joseph and Benjamin.","Rachel","Leah","Bilhah","Zilpah","Women of the Bible","Layperson"),
    ("I was a prophetess and judge who led Israel to victory over Sisera.","Deborah","Miriam","Huldah","Anna","Women of the Bible","Deacon"),
    ("I walked with God and was taken by Him — I never died.","Enoch","Elijah","Moses","Abraham","Genesis & Creation","Deacon"),
    ("I wrestled with God all night and was renamed Israel.","Jacob","Abraham","Moses","Joshua","Genesis & Creation","Layperson"),
    ("I was the first king of Israel but was rejected by God for disobedience.","Saul","David","Solomon","Rehoboam","Kings & Kingdoms","Layperson"),
    ("I interpreted dreams in Babylon and survived a night in a lion's den.","Daniel","Joseph","Ezekiel","Jeremiah","Prophets","Layperson"),
    ("I was Elijah's successor and asked for a double portion of his spirit.","Elisha","Elijah","Nathan","Samuel","Prophets","Deacon"),
    ("I was a tax collector who climbed a tree to see Jesus.","Zacchaeus","Matthew","Levi","Nicodemus","Life of Jesus","Layperson"),
    ("I was Jesus' friend who was raised from the dead after four days.","Lazarus","Jairus' daughter","The widow's son","Eutychus","Miracles","Layperson"),
    ("I was the oldest person in the Bible, living 969 years.","Methuselah","Noah","Adam","Seth","Numbers & Genealogies","Layperson"),
    ("I was strong as long as my hair was uncut, but Delilah betrayed my secret.","Samson","David","Gideon","Saul","Battles & Wars","Layperson"),
    ("I was a tentmaker who wrote 13 letters in the New Testament.","Paul","Peter","John","James","Paul & His Letters","Deacon"),
    ("I doubted the resurrection until I saw Jesus' nail-scarred hands.","Thomas","Peter","James","Andrew","The Apostles","Layperson"),
    ("I was the first Christian martyr, stoned while seeing heaven open.","Stephen","James","Peter","Paul","The Apostles","Layperson"),
    ("I was a shepherd boy anointed king while my older brothers watched.","David","Saul","Solomon","Gideon","Kings & Kingdoms","Layperson"),
    ("I was an angel who appeared to Mary, Zechariah, and Daniel.","Gabriel","Michael","Raphael","Uriel","Angels & Demons","Deacon"),
    ("I was the archangel who fought the dragon in Revelation.","Michael","Gabriel","Raphael","Uriel","Angels & Demons","Deacon"),
]
for clue,correct,w1,w2,w3,cat,diff in WAI:
    Q(cat,diff,f"Who am I? {clue}",S(correct,[w1,w2,w3]),correct)

print(f"  After Who Am I: {len(ALL)}")

# ============================================================================
# COMPARISON QUESTIONS — "How is X different from Y?"
# ============================================================================
COMPARE = [
    ("How are Elijah and Elisha different?","Elijah was taken to heaven; Elisha performed twice as many miracles and died naturally","They're the same person","Elisha came first","Elijah performed more miracles","Prophets","Deacon"),
    ("What's the difference between the Pharisees and Sadducees?","Pharisees believed in resurrection and angels; Sadducees did not","They believed the same things","Sadducees were stricter","Pharisees rejected the Torah","Life of Jesus","Deacon"),
    ("What's the difference between the first and second Temple?","Solomon built the first; Zerubbabel rebuilt the second after exile (later expanded by Herod)","They were the same building","The second was larger than the first","Moses built the first","Kings & Kingdoms","Deacon"),
    ("How does Matthew's genealogy of Jesus differ from Luke's?","Matthew traces through Joseph's line from Abraham; Luke traces through Mary's line to Adam","They are identical","Matthew starts with David","Luke starts with Abraham","Numbers & Genealogies","Pastor"),
    ("What's the difference between a prophet and a priest?","A prophet speaks God's word to the people; a priest represents the people before God","They're the same role","Priests are higher","Prophets are political leaders","Prophets","Deacon"),
    ("How are Cain and Abel different?","Cain was a farmer whose offering was rejected; Abel was a shepherd whose offering was accepted","They both farmed","Abel was older","Cain was a shepherd","Genesis & Creation","Layperson"),
    ("What's the difference between the Ark of the Covenant and Noah's Ark?","Noah's Ark was a huge boat; the Ark of the Covenant was a gold-covered box in the Tabernacle","They're the same object","Both were boats","Both held animals","Moses & the Exodus","Layperson"),
    ("How are Isaac and Ishmael different?","Isaac was the son of promise (Sarah); Ishmael was born of Hagar","They were twins","Ishmael was the chosen one","Isaac came first","Genesis & Creation","Deacon"),
    ("What is the difference between justification and sanctification?","Justification is being declared righteous; sanctification is the process of becoming holy","They mean the same thing","Sanctification comes first","Justification is a human effort","Paul & His Letters","Pastor"),
    ("How are mercy and grace different?","Mercy is not getting the punishment we deserve; grace is getting blessings we don't deserve","They're the same","Grace means justice","Mercy means reward","Paul & His Letters","Deacon"),
]
for q,correct,w1,w2,w3,cat,diff in COMPARE:
    Q(cat,diff,q,S(correct,[w1,w2,w3]),correct)

print(f"  After comparisons: {len(ALL)}")

# ============================================================================
# LOTS MORE PER-CATEGORY — Bulk handwritten
# ============================================================================

# ANGELS
c="Angels & Demons"
more=[
    ("Layperson","Who is the most famous angel in the Christmas story?","Gabriel — who announced Jesus' birth to Mary","Michael","Raphael","The angel of death"),
    ("Deacon","What did angels do after Jesus was tempted?","They came and attended/ministered to Him","They left","They spoke to Satan","They sang"),
    ("Deacon","What happened when angels appeared to people in the Bible?","People were usually terrified — angels said 'Do not be afraid'","People were calm","People bowed and worshiped","People ignored them"),
    ("Pastor","Are demons fallen angels?","Most scholars say yes — they are angels who rebelled with Satan","No — they are a separate creation","They are ghosts","They are symbolic only"),
    ("Deacon","What did Jesus say about Satan when the disciples cast out demons?","'I saw Satan fall like lightning from heaven'","'Satan is powerless'","'Ignore Satan'","'Satan has won'"),
    ("Pastor","What is the 'great dragon' in Revelation 12?","Satan — that ancient serpent who deceives the whole world","A literal dragon","A Roman emperor","A natural disaster"),
    ("Deacon","Can Satan read our minds?","The Bible doesn't say he can — he is not omniscient like God","Yes — he knows all thoughts","Yes — he is all-knowing","He can read only Christians' minds"),
    ("Deacon","What power did Jesus give the disciples over demons?","Authority to cast them out in His name","The power to negotiate","The ability to see them","The ability to become them"),
    ("Pastor","What is exorcism in the Bible?","Casting out demons through the authority of Jesus' name","A magic ritual","A priestly ceremony","A sacrifice"),
    ("Deacon","What happened when the sons of Sceva tried to exorcise?","The demon overpowered them — 'Jesus I know, Paul I know, but who are you?'","They succeeded","Nothing happened","They were killed"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# FOOD
c="Food, Feasts & Offerings"
more=[
    ("Layperson","What did God forbid Adam and Eve to eat?","The fruit of the Tree of Knowledge of Good and Evil","All fruit","Meat","Bread"),
    ("Deacon","What happened when Jesus broke bread with the disciples at Emmaus?","Their eyes were opened and they recognized Him","He performed a miracle","He gave a sermon","Nothing special"),
    ("Deacon","What does 'breaking bread' symbolize in Acts?","Christian fellowship and communion","Literal bread-breaking","A Jewish custom only","Sharing a meal with strangers"),
    ("Deacon","What is the 'Lord's Supper' or 'Communion'?","A remembrance of Jesus' death through bread (body) and wine (blood)","A feast","A Jewish Sabbath meal","A Sunday dinner"),
    ("Pastor","What is 'transubstantiation' vs 'symbolic' view?","Whether communion bread/wine literally become Christ's body/blood or symbolize it","A type of prayer","A baptism debate","A psalm interpretation"),
    ("Deacon","What food did the prophet Elisha purify?","Poisonous stew — he added flour to make it safe","Bad water","Moldy bread","Sour wine"),
    ("Deacon","What did Jesus say about not worrying about food?","'Life is more than food' — seek God's kingdom first","Stockpile food","Fast always","Eat whatever you want"),
    ("Layperson","What is the 'bread of life'?","Jesus — He said 'I am the bread of life' in John 6","Manna","Communion bread","A type of wheat"),
    ("Pastor","What is the 'wedding supper of the Lamb'?","The heavenly celebration of Christ's union with His church","A Jewish wedding custom","A Passover meal","A feast in the Temple"),
    ("Deacon","What is the 'cup of the new covenant'?","The wine at the Last Supper representing Jesus' blood shed for forgiveness","A Passover tradition only","A priestly ritual","A Temple offering"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# KINGS
c="Kings & Kingdoms"
more=[
    ("Layperson","Who was the most famous king of Israel?","David","Solomon","Saul","Hezekiah"),
    ("Layperson","What was David known for besides being king?","Writing Psalms and being 'a man after God's own heart'","Building the Temple","Conquering Egypt","Writing Proverbs"),
    ("Deacon","What was David's greatest sin?","Adultery with Bathsheba and murder of her husband Uriah","Worshiping idols","Fleeing from Saul","Numbering the people"),
    ("Deacon","How did David respond when Nathan confronted him?","He repented deeply — 'I have sinned against the LORD'","He denied it","He killed Nathan","He fled"),
    ("Deacon","What was the consequence of David's sin?","The child born to Bathsheba died, and sword would never depart from his house","Nothing happened","He lost the throne","He was exiled"),
    ("Deacon","Why did Absalom rebel against David?","Partly because David failed to discipline Amnon for assaulting Tamar","He wanted wealth","He disagreed on religion","Foreign influence"),
    ("Deacon","What was the Queen of Sheba impressed by?","Solomon's wisdom and the magnificence of his court","His army","His height","His age"),
    ("Deacon","What foreign ruler released the Jews from Babylonian exile?","Cyrus of Persia","Nebuchadnezzar","Darius","Alexander"),
    ("Deacon","What prophet was active during the reign of King Ahab?","Elijah","Isaiah","Jeremiah","Amos"),
    ("Pastor","What was the 'Deuteronomistic History'?","Joshua through 2 Kings — telling Israel's story through the lens of obedience/disobedience","A book Moses wrote","A Roman history","A Greek manuscript"),
    ("Deacon","What happened when Hezekiah was sick?","Isaiah told him he would die, but Hezekiah prayed and God added 15 years","He died immediately","He recovered on his own","A priest healed him"),
    ("Deacon","Who was Nehemiah?","Cupbearer to the Persian king who led the rebuilding of Jerusalem's walls","A priest","A prophet","A king"),
    ("Deacon","Who was Ezra?","A priest and scribe who led spiritual reform after the exile","A king","A prophet","A warrior"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# LAWS
c="Laws & Commandments"
more=[
    ("Layperson","What are the Ten Commandments?","10 laws God gave Moses on Mount Sinai for how to live","Rules made by Moses","Roman laws","Church traditions"),
    ("Layperson","Where are the Ten Commandments found?","Exodus 20 and Deuteronomy 5","Genesis 1","Leviticus 1","Numbers 1"),
    ("Deacon","What is the difference between moral, civil, and ceremonial law?","Moral = universal ethics; civil = Israel's national laws; ceremonial = worship/sacrifice laws","There is no difference","Only moral law exists","Only ceremonial law exists"),
    ("Deacon","What did Jesus do with the ceremonial law?","He fulfilled it — He was the ultimate sacrifice, making animal sacrifices unnecessary","He abolished all law","He added to it","He ignored it"),
    ("Deacon","What did the early church decide about circumcision for Gentiles?","It was not required for salvation (Acts 15)","It was required","Only adults needed it","It was replaced by baptism"),
    ("Deacon","What is the 'law of love'?","Jesus' teaching that love for God and neighbor fulfills all the law","A Roman legal code","A specific commandment","A psalmic concept"),
    ("Pastor","What is the 'Holiness Code' in Leviticus?","Leviticus 17-26 — laws about holy living covering every aspect of life","The Ten Commandments","A priestly manual","A later addition"),
    ("Deacon","What did Jesus teach about the law in Matthew 5?","He deepened it — not just actions but heart attitudes matter","He replaced it entirely","He simplified it to 2 rules","He said it was outdated"),
    ("Pastor","What is the 'covenant of works' vs 'covenant of grace'?","Works: obedience for blessing (Adam); Grace: salvation through faith (Christ)","Two different Bibles","Jewish vs Christian law","Old vs new commandments"),
    ("Deacon","Why did Jesus criticize the Pharisees about the law?","They kept the letter but missed the spirit — outward obedience without inner transformation","They didn't keep it at all","They were too lenient","They were Sadducees"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# PROPHECY
c="Prophecy & Fulfillment"
more=[
    ("Deacon","How many Old Testament prophecies does Jesus fulfill?","Over 300","About 10","About 50","About 3"),
    ("Deacon","What did Isaiah say about the Messiah's birth?","A virgin would conceive and bear a son called Immanuel","He would be born in a palace","He would come from Egypt","He would be a warrior"),
    ("Deacon","What did Micah prophesy about Bethlehem?","'Out of you will come a ruler who will shepherd my people Israel'","It would be destroyed","It would become the capital","It would be forgotten"),
    ("Pastor","What is dual fulfillment in prophecy?","A prophecy that has both an immediate and a future fulfillment","Two prophets saying the same thing","A prophecy that fails","A repeated prophecy"),
    ("Deacon","How was Psalm 16 fulfilled?","'You will not let your Holy One see decay' — Jesus' body did not decay in the tomb","David lived forever","The Temple was rebuilt","Israel won a battle"),
    ("Deacon","What did Zechariah prophesy about the Messiah's entry?","'Rejoice! Your king comes, humble, riding on a donkey'","On a horse","In a chariot","Walking"),
    ("Pastor","How does Isaiah 11 describe the Messiah?","A 'shoot from the stump of Jesse' — the Spirit resting on Him","A mighty warrior","A wealthy king","A Levite priest"),
    ("Deacon","What does 'the day of the LORD' refer to?","God's future intervention in judgment and salvation","A Jewish holiday","Every Sabbath","The day Jesus was born"),
    ("Pastor","What is the 'new covenant' compared to the 'old'?","Old: law written on stone, external; New: law written on hearts, internal, through the Spirit","Same thing, different name","Old is better","New is only for Gentiles"),
    ("Deacon","What did Malachi prophesy last in the Old Testament?","God would send Elijah before the great and terrible day of the LORD","The Temple would be rebuilt","Israel would conquer Rome","A new king from Babylon"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# PLACES
c="Places & Lands"
more=[
    ("Layperson","What is the Holy Land?","The region of Israel/Palestine — land promised to Abraham","Egypt","Rome","Babylon"),
    ("Deacon","What was Galilee known for in Jesus' time?","The northern region where Jesus did most of His ministry — considered rural","The capital","A desert","An island"),
    ("Deacon","What was Judea known for?","The southern region containing Jerusalem and the Temple","A Roman province only","A Greek city","An Egyptian territory"),
    ("Deacon","What was the 'Promised Land' like?","A land 'flowing with milk and honey' — fertile and abundant","A desert","A frozen wasteland","A small island"),
    ("Deacon","Where is the Mount of Olives?","East of Jerusalem, across the Kidron Valley","North of Bethlehem","West of Jericho","South of Hebron"),
    ("Pastor","What was Masada?","A mountain fortress where Jewish rebels made a last stand against Rome in AD 73","A city in Egypt","A port in Phoenicia","A temple in Samaria"),
    ("Deacon","Where was the early church based?","Jerusalem initially, then spreading to Antioch, Ephesus, Rome, and beyond","Rome only","Bethlehem","Nazareth"),
    ("Deacon","What made the Jordan River significant?","Israel crossed it to enter Canaan; Jesus was baptized in it","It was the longest river","It had gold","It was the border of Egypt"),
    ("Pastor","Where was Pergamum?","A city in Asia Minor — 'where Satan's throne is' (Revelation)","A Greek island","A Roman suburb","An Egyptian city"),
    ("Deacon","What was the Via Dolorosa?","The traditional route Jesus walked carrying His cross to Golgotha","A Roman road","A Jewish marketplace","A river crossing"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# PSALMS
c="Psalms & Proverbs"
more=[
    ("Layperson","What is a psalm?","A song, poem, or prayer in the book of Psalms","A law","A prophecy","A story"),
    ("Layperson","How were Psalms used in ancient Israel?","Sung in worship at the Temple and in daily life","Read silently","Only by priests","Only at funerals"),
    ("Deacon","What types of Psalms are there?","Praise, lament, thanksgiving, wisdom, royal, and messianic","Only praise","Only prayer","Only prophecy"),
    ("Deacon","What is the theme of Psalm 139?","God knows us completely — He is all-knowing and ever-present","Military victory","The creation of the world","The Exodus"),
    ("Deacon","What does Psalm 37 teach?","Don't worry about evildoers — trust God and He will act","Fight your enemies","Avoid all people","Money brings happiness"),
    ("Deacon","What is the theme of Psalm 103?","Praise God for His forgiveness, healing, and love","A battle prayer","A creation hymn","A wedding song"),
    ("Pastor","What are the Penitential Psalms?","Psalms 6, 32, 38, 51, 102, 130, 143 — expressing deep repentance","Praise psalms","Royal psalms","Wisdom psalms"),
    ("Deacon","What does Proverbs teach about friendship?","'A friend loves at all times, and a brother is born for adversity'","Avoid all friends","Friends are unnecessary","Only trust family"),
    ("Deacon","What does Proverbs teach about money?","'The borrower is slave to the lender' — be wise with finances","Money is evil","Hoard everything","Spend freely"),
    ("Pastor","What is the 'acrostic' structure in Hebrew poetry?","Each line or section begins with successive letters of the Hebrew alphabet","Rhyming","Meter","Parallel lines only"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# NUMBERS
c="Numbers & Genealogies"
more=[
    ("Layperson","Who are in the genealogy of Jesus?","Abraham, David, Ruth, Rahab, Tamar, Mary, and many others","Only kings","Only priests","Only prophets"),
    ("Deacon","Why do Matthew and Luke have different genealogies for Jesus?","Matthew traces Joseph's legal line; Luke traces Mary's bloodline (most scholars say)","One is wrong","They cover different periods","They list the same people"),
    ("Deacon","What women are named in Jesus' genealogy in Matthew?","Tamar, Rahab, Ruth, Bathsheba (wife of Uriah), and Mary","Only Mary","None","Sarah and Rebekah"),
    ("Deacon","How many books are in the Hebrew Bible (Tanakh)?","24 (same content as 39 OT books, counted differently)","39","27","66"),
    ("Deacon","What does 'Tanakh' stand for?","Torah (Law), Nevi'im (Prophets), Ketuvim (Writings)","The three patriarchs","Three temples","Three covenants"),
    ("Pastor","How is the number 7 used throughout the Bible?","Creation (7 days), feasts (7th day/year), Revelation (7 churches/seals/trumpets/bowls)","Only in Genesis","Only in Revelation","Rarely used"),
    ("Deacon","How many times did Naaman dip in the Jordan?","7","3","1","12"),
    ("Deacon","How many times did Israel march around Jericho total?","13 (once each for 6 days, then 7 times on day 7)","7","14","40"),
    ("Pastor","What is gematria?","A system assigning numerical values to Hebrew/Greek letters — sometimes used in interpretation","A type of prayer","A musical notation","A building technique"),
    ("Deacon","How many sons did Haman have (book of Esther)?","10","7","12","3"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# MIRACLES
c="Miracles"
more=[
    ("Layperson","What is a miracle in the Bible?","A supernatural act of God that reveals His power and purpose","A magic trick","A natural event","A coincidence"),
    ("Deacon","Why did Jesus perform miracles?","To reveal God's kingdom, show compassion, and confirm His identity as Messiah","To show off","To gain followers only","To start a religion"),
    ("Deacon","Did the apostles continue performing miracles after Jesus left?","Yes — through the power of the Holy Spirit in Jesus' name","No — miracles stopped","Only Peter did","Only Paul did"),
    ("Deacon","What did Jesus say to the healed leper?","'Go show yourself to the priest and offer the gift Moses commanded'","'Tell everyone'","'Stay here'","'Follow me'"),
    ("Deacon","What did the feeding miracles teach?","Jesus is the Bread of Life — God provides abundantly for all needs","That bread is holy","That fishing is important","That farming matters"),
    ("Deacon","What happened when Jesus healed the ten lepers?","Only one (a Samaritan) came back to thank Him","All came back","None came back","Five came back"),
    ("Pastor","What is the significance of Jesus healing on the Sabbath?","He showed that mercy and compassion are more important than rigid Sabbath rules","He was breaking the Law","He was testing the Pharisees","It was accidental"),
    ("Deacon","What was special about the miracle at the Pool of Bethesda?","Jesus healed a man who had been an invalid for 38 years","It was the first miracle","It was in Egypt","It involved angels only"),
    ("Deacon","What did the man born blind do after Jesus healed him?","Washed in the Pool of Siloam as Jesus instructed, then could see","Went to the Temple","Followed Jesus immediately","Went home"),
    ("Deacon","What miracle did Jesus perform that caused the Jewish leaders to plot His death?","Raising Lazarus from the dead — they feared everyone would follow Jesus","Walking on water","Feeding 5,000","Healing a blind man"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# DREAMS
c="Dreams & Visions"
more=[
    ("Layperson","Why did Joseph's brothers hate him?","His dreams showed they would bow to him, and their father favored him","He was lazy","He stole from them","He was disobedient"),
    ("Deacon","What is the significance of Ezekiel's dry bones vision?","God can restore even what seems completely dead — Israel would live again","A literal army","A new creation","The end of the world"),
    ("Deacon","What did God promise in Ezekiel's new temple vision?","God's glory would return and He would dwell with His people forever","A bigger temple","More sacrifices","Earthly wealth"),
    ("Pastor","What are 'apocalyptic visions'?","Dramatic revelations about the end times using symbolic imagery","Predictions about weather","Military strategies","Scientific discoveries"),
    ("Deacon","How did God communicate with prophets?","Through dreams, visions, direct speech, angels, and the Holy Spirit","Only through dreams","Only through angels","Only through nature"),
    ("Deacon","What did Amos see in his visions?","A plumb line (measuring Israel's faithfulness), locusts, fire, and a basket of fruit","A rainbow","A garden","A river"),
    ("Pastor","What did Zechariah's eight night visions reveal?","God's plan to restore Israel, rebuild the Temple, and bring the Messiah","Military conquest","Agricultural abundance","A new exodus"),
    ("Deacon","What happened when Isaiah had his throne room vision?","A seraph touched his lips with a coal, cleansing his sin, and he volunteered to go","He ran away","He was struck blind","He wrote a psalm"),
]
for d,q,c1,c2,c3,c4 in more: Q(c,d,q,S(c1,[c2,c3,c4]),c1)

# APOSTLES more
c="The Apostles"
more=[
    ("Layperson","What did Jesus tell His apostles to do?","Go into all the world and preach the gospel to every creature","Stay in Jerusalem","Build a temple","Write books"),
    ("Deacon","What was the early church known for?","Sharing everything, breaking bread together, praying, and performing signs","Building churches","Organizing political movements","Writing laws"),
    ("Deacon","How were the apostles persecuted?","Beaten, imprisoned, and eventually most were martyred","They were praised","They were left alone","They were exiled only"),
    ("Deacon","What did Peter say when told to stop preaching?","'We must obey God rather than men'","'We will stop'","'Let us pray about it'","'We need permission'"),
    ("Deacon","What was the role of deacons in the early church?","To serve the practical needs of the community so apostles could focus on preaching","To preach only","To collect taxes","To guard the Temple"),
    ("Pastor","What is 'apostolic succession'?","The belief that authority passes from the apostles to later church leaders","A voting system","A prophecy","A military tradition"),
    ("Deacon","Who was Silas?","Paul's companion who was imprisoned with him in Philippi","One of the twelve","A Roman guard","A Jewish priest"),
    ("Deacon","What did John write besides the Gospel and Revelation?","Three epistles (1, 2, 3 John)","Only the Gospel","Nothing else","A psalm"),
    ("Deacon","What was James (brother of Jesus) known for?","Leading the Jerusalem church and writing the epistle of James","Being one of the twelve","Being a Pharisee","Being a priest"),
    ("Deacon","How did the book of Acts end?","With Paul preaching in Rome under house arrest — no conclusion to his trial","With Paul's death","With Peter's sermon","With Jesus' ascension"),
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
