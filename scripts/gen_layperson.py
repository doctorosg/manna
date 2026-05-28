#!/usr/bin/env python3
"""Generate 1000+ Layperson questions — accessible, fun, well-known Bible content."""
import json, random, hashlib, os, re
random.seed(7777)

with open("/home/claude/manna/manna_questions.json") as f:
    ALL = json.load(f)
existing = set(q["question"].strip().lower() for q in ALL)
start_count = len(ALL)

def Q(cat,diff,q,opts,cor,exp=""):
    k=q.strip().lower()
    if k not in existing:
        existing.add(k)
        ALL.append({"category":cat,"difficulty":"Layperson","question":q,"options":opts,"correct":cor,"explanation":exp})

def S(c,ws):
    o=[c]+list(ws[:3]);random.shuffle(o);return o

# ============================================================================
# GENESIS — Everyone knows these stories
# ============================================================================
c="Genesis & Creation"
qs=[
    ("How long did God take to create everything and rest?","7 days total","6 days total","10 days","1 day"),
    ("What was the very first thing God created?","Light","Water","Earth","Animals"),
    ("What did God do on the seventh day?","He rested","He created humans","He created the sea","He created the sun"),
    ("Where did Adam and Eve live before they sinned?","The Garden of Eden","The city of Babylon","Mount Sinai","The land of Canaan"),
    ("Who tempted Eve to eat the forbidden fruit?","The serpent","An angel","Adam","A lion"),
    ("What happened after Adam and Eve ate the fruit?","They were sent out of the Garden","Nothing changed","They became angels","They fell asleep"),
    ("Why did God send the great flood?","People had become very wicked","To water the crops","To fill the oceans","To test Noah"),
    ("How many people were on Noah's ark?","8","12","2","20"),
    ("What was the rainbow a sign of?","God's promise never to flood the whole earth again","Good weather","A new creation","The end of winter"),
    ("What did people try to build at the Tower of Babel?","A tower to reach heaven","A palace","A bridge","A wall"),
    ("Why did God scatter the people at Babel?","They were too proud and united against God","They built too slowly","They ran out of bricks","An earthquake happened"),
    ("Who did God call to leave his homeland and go to a new land?","Abraham","Moses","Noah","David"),
    ("What did God promise Abraham?","Descendants as many as the stars","A golden palace","Eternal youth","A mighty army"),
    ("Why did Abraham almost sacrifice Isaac?","God was testing his faith","Isaac had sinned","It was a local custom","Sarah told him to"),
    ("What did God provide instead of Isaac?","A ram caught in a thicket","A dove","A lamb from the flock","Nothing — He stopped the sacrifice"),
    ("Why was Joseph's coat special?","It was a coat of many colors given by his father","It was made of gold","It was armor","It was invisible"),
    ("Why did Joseph's brothers hate him?","Their father favored him and he had dreams of ruling over them","He stole from them","He was lazy","He was too tall"),
    ("Where did Joseph end up after his brothers sold him?","Egypt","Babylon","Rome","Canaan"),
    ("What special ability did Joseph have?","He could interpret dreams","He could fly","He could heal the sick","He could speak all languages"),
    ("What did Joseph become in Egypt?","Second in command to Pharaoh","A slave forever","A priest","A soldier"),
    ("Did Joseph forgive his brothers?","Yes — he said God meant it for good","No — he imprisoned them","He never saw them again","He punished them"),
    ("Who was the twin brother of Jacob?","Esau","Joseph","Reuben","Judah"),
    ("What did Jacob dream about at Bethel?","A stairway/ladder reaching to heaven with angels","A golden city","A burning bush","A talking animal"),
    ("How many sons did Jacob have?","12","10","7","3"),
    ("What happened to Sodom and Gomorrah?","God destroyed them with fire and brimstone","They became great cities","They were flooded","Nothing"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# ============================================================================
# MOSES — The Exodus story
# ============================================================================
c="Moses & the Exodus"
qs=[
    ("Why was baby Moses put in a basket on the river?","Pharaoh ordered all Hebrew baby boys to be killed","His parents were traveling","The river was holy","He needed a bath"),
    ("Who found baby Moses in the basket?","Pharaoh's daughter","A fisherman","Moses' aunt","A shepherd"),
    ("What did God appear as when He spoke to Moses?","A burning bush that didn't burn up","A bright star","A cloud","A talking animal"),
    ("What did God tell Moses to do?","Go to Pharaoh and demand he free the Israelites","Build an ark","Go to war","Write the Psalms"),
    ("What excuse did Moses give God?","He said he was not a good speaker","He was too old","He was too young","He didn't know the way"),
    ("Who helped Moses speak to Pharaoh?","His brother Aaron","His wife Zipporah","Joshua","Caleb"),
    ("What was the very last plague God sent on Egypt?","Death of every firstborn son","Darkness","Locusts","Hail"),
    ("What did the Israelites put on their doorposts to be safe?","Lamb's blood","Water","Oil","Flour"),
    ("What happened to the Egyptian army at the Red Sea?","The waters closed on them and they drowned","They crossed safely","They turned back","They surrendered"),
    ("What did God give the Israelites to eat in the desert?","Manna from heaven","Pizza","Bread from Egypt","Fish"),
    ("What appeared on the stone tablets God gave Moses?","The Ten Commandments","A map to the Promised Land","A list of names","A drawing of the Temple"),
    ("Why did Moses break the stone tablets?","He was angry because the people were worshiping a golden calf","He tripped","They were too heavy","God told him to"),
    ("How long did the Israelites wander in the wilderness?","40 years","10 years","100 years","7 years"),
    ("Why couldn't Moses enter the Promised Land?","He disobeyed God by striking the rock","He was too old","He got lost","He chose to stay"),
    ("What led the Israelites through the wilderness by day?","A pillar of cloud","A map","A compass","An angel on a horse"),
    ("What led them at night?","A pillar of fire","The moon","Stars","A lantern"),
    ("What did the people worship while Moses was on the mountain?","A golden calf","A stone idol","A bronze snake","A wooden statue"),
    ("Who took over as leader after Moses died?","Joshua","Aaron","Caleb","Miriam"),
    ("Where did Moses see the Promised Land from?","Mount Nebo","Mount Sinai","Mount Everest","Mount Ararat"),
    ("What was the first plague God sent on Egypt?","The Nile River turned to blood","Frogs everywhere","Total darkness","Locusts"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# ============================================================================
# LIFE OF JESUS — Christmas, miracles, Easter
# ============================================================================
c="Life of Jesus"
qs=[
    ("Where was Jesus born?","Bethlehem","Jerusalem","Nazareth","Rome"),
    ("Where was Jesus laid after He was born?","In a manger","In a palace","In a hospital","In a synagogue"),
    ("Who visited Jesus on the night He was born?","Shepherds","Kings","Soldiers","Priests"),
    ("What gifts did the wise men bring?","Gold, frankincense, and myrrh","Silver, bronze, and iron","Food, water, and wine","Clothes, blankets, and toys"),
    ("Who wanted to kill baby Jesus?","King Herod","Pontius Pilate","Caesar","Pharaoh"),
    ("Where did Jesus grow up?","Nazareth","Bethlehem","Jerusalem","Egypt"),
    ("What was Joseph's (Jesus' earthly father's) job?","Carpenter","Fisherman","Farmer","Priest"),
    ("Who baptized Jesus?","John the Baptist","Peter","Paul","Moses"),
    ("What happened when Jesus was baptized?","A dove came down and God's voice said 'This is my Son'","Nothing special","It rained","The river dried up"),
    ("How long did Jesus fast in the desert?","40 days","7 days","3 days","100 days"),
    ("Who tempted Jesus in the desert?","Satan","An angel","A serpent","A pharisee"),
    ("What was Jesus' first miracle?","Turning water into wine at a wedding","Healing a blind man","Walking on water","Feeding 5,000"),
    ("How many disciples did Jesus choose?","12","7","10","3"),
    ("What did Jesus feed 5,000 people with?","5 loaves of bread and 2 fish","A huge feast","Manna from heaven","Nothing — they fasted"),
    ("What did Jesus do during a storm on the sea?","He calmed the wind and waves by speaking to them","He swam to shore","He prayed until it stopped","He slept through it"),
    ("Who walked on water with Jesus?","Peter","John","James","Andrew"),
    ("What happened to Peter on the water?","He started sinking when he lost faith","He walked perfectly","He swam instead","He flew"),
    ("Who did Jesus raise from the dead?","Lazarus","Moses","Abraham","Peter"),
    ("How long had Lazarus been dead?","4 days","1 day","7 days","1 hour"),
    ("What did Jesus ride into Jerusalem on?","A donkey","A horse","A camel","A chariot"),
    ("What did the crowd wave when Jesus entered Jerusalem?","Palm branches","Flags","Swords","Flowers"),
    ("What did Jesus do at the Last Supper?","He shared bread and wine with His disciples","He performed a miracle","He preached a sermon","He sang songs"),
    ("Who betrayed Jesus?","Judas Iscariot","Peter","Thomas","Matthew"),
    ("How much was Jesus betrayed for?","30 pieces of silver","100 gold coins","10 pieces of silver","Nothing"),
    ("How did Judas identify Jesus to the soldiers?","He kissed Him","He pointed at Him","He called His name","He described His clothes"),
    ("Who denied knowing Jesus three times?","Peter","Thomas","John","James"),
    ("What animal crowed after Peter's denial?","A rooster","A dove","An eagle","A crow"),
    ("Who sentenced Jesus to death?","Pontius Pilate","King Herod","Caesar","The high priest"),
    ("What was placed on Jesus' head before crucifixion?","A crown of thorns","A gold crown","A helmet","A blindfold"),
    ("Where was Jesus crucified?","Golgotha (the Place of the Skull)","The Temple","Mount Sinai","The Garden of Eden"),
    ("How many days was Jesus in the tomb?","3","7","1","40"),
    ("Who was the first person to see Jesus alive after the resurrection?","Mary Magdalene","Peter","John","Thomas"),
    ("What did Jesus tell His followers to do before He ascended?","Go and make disciples of all nations","Build a church","Write the Bible","Stay in Jerusalem forever"),
    ("How did Jesus leave earth after the resurrection?","He ascended into heaven","He walked away","He disappeared","He sailed away"),
    ("What did Jesus promise to send after He left?","The Holy Spirit","An angel","A new prophet","A letter"),
    ("What did Thomas say when he doubted the resurrection?","He wouldn't believe until he saw Jesus' wounds","He said it was a dream","He called it a lie","He left the group"),
    ("What famous prayer did Jesus teach His disciples?","The Lord's Prayer (Our Father)","Psalm 23","The Shema","The Beatitudes"),
    ("What did Jesus say is the greatest commandment?","Love God with all your heart, soul, and mind","Do not steal","Keep the Sabbath","Honor your parents"),
    ("What did Jesus say is the second greatest commandment?","Love your neighbor as yourself","Do not murder","Do not lie","Give to the poor"),
    ("Who did Jesus say is our 'neighbor' in the Good Samaritan story?","Anyone in need — even our enemies","Only our friends","Only our family","Only people from our town"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# ============================================================================
# FAMOUS STORIES — well-known to everyone
# ============================================================================

# BATTLES
c="Battles & Wars"
qs=[
    ("How did David kill the giant Goliath?","With a sling and a stone to the forehead","With a sword","With a spear","With his bare hands"),
    ("How tall was Goliath?","Over 9 feet tall","6 feet tall","12 feet tall","7 feet tall"),
    ("What did David take to face Goliath?","Five smooth stones and a sling","A sword and shield","A bow and arrows","A spear"),
    ("What fell down when the Israelites marched around Jericho?","The walls of the city","The gate","The tower","The army"),
    ("How many days did the Israelites march around Jericho?","7 days","1 day","40 days","3 days"),
    ("What did the Israelites blow while marching around Jericho?","Trumpets","Drums","Nothing","Flutes"),
    ("What was Samson's source of strength?","His hair — he was under a Nazirite vow","His muscles","A magic ring","His diet"),
    ("Who tricked Samson into revealing his secret?","Delilah","Jezebel","Bathsheba","Ruth"),
    ("How did Samson die?","He pushed down the pillars of a temple, killing himself and the Philistines","In battle with a sword","Of old age","He was poisoned"),
    ("Who fought with an army of only 300 men and won?","Gideon","David","Joshua","Samson"),
    ("What unusual weapons did Gideon's men use?","Trumpets, clay jars, and torches","Swords","Slings","Bows"),
    ("Who was the female judge who led Israel to victory?","Deborah","Ruth","Esther","Miriam"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# KINGS
c="Kings & Kingdoms"
qs=[
    ("Who was the first king of Israel?","Saul","David","Solomon","Moses"),
    ("Who was the greatest king of Israel?","David","Solomon","Saul","Hezekiah"),
    ("What instrument did King David play?","The harp","The trumpet","The drum","The flute"),
    ("What did Solomon ask God for?","Wisdom","Wealth","A long life","A big army"),
    ("What famous building did Solomon construct?","The Temple in Jerusalem","The Tower of Babel","Noah's Ark","The walls of Jericho"),
    ("How did Solomon prove his wisdom with two women and a baby?","He threatened to cut the baby in half — the real mother gave it up","He asked the baby","He used a lie detector","He prayed for an answer"),
    ("What evil queen promoted false gods in Israel?","Jezebel","Esther","Delilah","Bathsheba"),
    ("What prophet called fire from heaven to defeat false prophets?","Elijah","Elisha","Isaiah","Moses"),
    ("Who took over from Saul as king?","David","Solomon","Jonathan","Samuel"),
    ("What sin did King David commit?","Adultery with Bathsheba and murder of her husband","Idol worship","Stealing from the Temple","Fleeing from battle"),
    ("What happened when the kingdom split after Solomon?","It became two kingdoms — Israel in the north and Judah in the south","It became three kingdoms","Nothing happened","Egypt took over"),
    ("Which empire destroyed Jerusalem and took the people into exile?","Babylon","Rome","Persia","Egypt"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# PROPHETS
c="Prophets"
qs=[
    ("What happened to Jonah when he ran from God?","He was swallowed by a huge fish","He drowned","He got lost","He was struck by lightning"),
    ("How many days was Jonah inside the fish?","3 days","7 days","1 day","40 days"),
    ("Where did God want Jonah to go?","Nineveh","Jerusalem","Egypt","Rome"),
    ("Did the people of Nineveh listen to Jonah?","Yes — the whole city repented","No — they ignored him","They killed him","They laughed at him"),
    ("Who was thrown into a den of lions?","Daniel","Jonah","David","Moses"),
    ("What happened to Daniel in the lion's den?","God shut the lions' mouths and Daniel was safe","He fought the lions","He escaped through a hole","He tamed the lions"),
    ("Who were Daniel's three friends thrown into a furnace?","Shadrach, Meshach, and Abednego","Peter, James, and John","Abraham, Isaac, and Jacob","Moses, Aaron, and Joshua"),
    ("What happened to the three men in the fiery furnace?","They were unharmed and a fourth person appeared with them","They burned up","They escaped","The fire went out"),
    ("What prophet saw a valley of dry bones come to life?","Ezekiel","Isaiah","Jeremiah","Daniel"),
    ("What prophet is called 'the weeping prophet'?","Jeremiah","Isaiah","Ezekiel","Amos"),
    ("Which prophet predicted Jesus would be born in Bethlehem?","Micah","Isaiah","Jeremiah","Daniel"),
    ("Which prophet wrote about a 'suffering servant'?","Isaiah","Jeremiah","Ezekiel","Malachi"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# APOSTLES
c="The Apostles"
qs=[
    ("What happened on the Day of Pentecost?","The Holy Spirit came on the believers like fire","Jesus returned","The Temple was rebuilt","An earthquake struck"),
    ("What appeared over the apostles' heads at Pentecost?","Tongues of fire","Stars","Crowns","Halos"),
    ("Who was the first Christian to be killed for his faith?","Stephen","Peter","Paul","James"),
    ("How did Stephen die?","He was stoned to death","He was crucified","He was beheaded","He drowned"),
    ("Who held the coats of those who stoned Stephen?","Saul (later called Paul)","Peter","John","Barnabas"),
    ("How many people believed after Peter's first sermon?","About 3,000","About 100","About 12","About 500"),
    ("Which apostle was a tax collector?","Matthew","Peter","John","James"),
    ("Which apostle was known as 'the doubter'?","Thomas","Peter","Judas","Andrew"),
    ("Which apostle denied Jesus three times?","Peter","Thomas","Judas","John"),
    ("Who replaced Judas as an apostle?","Matthias","Paul","Barnabas","Stephen"),
    ("What were most of the apostles before following Jesus?","Fishermen","Farmers","Soldiers","Priests"),
    ("Who was Jesus' closest inner circle of three?","Peter, James, and John","Matthew, Mark, and Luke","Andrew, Philip, and Thomas","Judas, Simon, and Thaddaeus"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# PAUL
c="Paul & His Letters"
qs=[
    ("What was Paul's name before he became a Christian?","Saul","Simon","Stephen","Silas"),
    ("What happened to Paul on the road to Damascus?","A bright light blinded him and Jesus spoke to him","He was arrested","He found a treasure","He met Peter"),
    ("Was Paul one of the original 12 apostles?","No — he was called later","Yes — he was the leader","Yes — he replaced Judas","Yes — he was the youngest"),
    ("What famous chapter about love did Paul write?","1 Corinthians 13","Romans 8","John 3","Psalm 23"),
    ("What did Paul say is the greatest of faith, hope, and love?","Love","Faith","Hope","All are equal"),
    ("How did Paul often write his letters?","From prison","From a palace","From a boat","From the Temple"),
    ("What did Paul do for work besides preaching?","He was a tentmaker","He was a fisherman","He was a farmer","He was a soldier"),
    ("How did Paul escape from Damascus after his conversion?","He was lowered over the wall in a basket","He walked out the gate","He disguised himself","An angel freed him"),
    ("What happened to Paul and Silas in jail at Philippi?","An earthquake opened the doors and the jailer believed","They escaped","They were executed","Nothing happened"),
    ("What verse says 'I can do all things through Christ'?","Philippians 4:13","Romans 8:28","John 3:16","Psalm 23:1"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# WOMEN
c="Women of the Bible"
qs=[
    ("Who was the mother of Jesus?","Mary","Martha","Elizabeth","Anna"),
    ("Who was the first woman?","Eve","Sarah","Mary","Ruth"),
    ("What loyal woman said 'Where you go, I will go'?","Ruth","Esther","Mary","Martha"),
    ("Who was the queen that saved the Jewish people in Persia?","Esther","Ruth","Deborah","Jezebel"),
    ("Who was the mother of Samuel?","Hannah","Sarah","Rebekah","Rachel"),
    ("What did Hannah pray for?","A son","Wealth","Health","A husband"),
    ("Who was the judge and leader of Israel?","Deborah","Ruth","Esther","Miriam"),
    ("Who hid the Israelite spies in Jericho?","Rahab","Ruth","Deborah","Mary"),
    ("Who was Jesus' friend who loved to sit at His feet and listen?","Mary of Bethany","Martha","Mary Magdalene","Elizabeth"),
    ("Who was the first person to see Jesus alive after Easter?","Mary Magdalene","Peter","John","Thomas"),
    ("Which woman had a strong faith and betrayed Samson?","Delilah tricked him — she did not have faith","Ruth","Esther","Deborah"),
    ("What relative of Mary was the mother of John the Baptist?","Elizabeth","Anna","Martha","Joanna"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# PARABLES
c="Parables"
qs=[
    ("What is a parable?","A short story with a spiritual lesson","A miracle","A prayer","A law"),
    ("Who told parables?","Jesus","Moses","Paul","David"),
    ("In the Good Samaritan, who helped the injured man?","A Samaritan — an unlikely hero","A priest","A Levite","A soldier"),
    ("What is the lesson of the Good Samaritan?","Love and help everyone, even strangers and enemies","Only help your friends","Avoid dangerous roads","Call for help"),
    ("In the Prodigal Son, what did the younger son waste?","His inheritance on wild living","His father's tools","His brother's money","The family farm"),
    ("What did the father do when the Prodigal Son came home?","Ran to him, hugged him, and threw a party","Turned him away","Made him work as a servant","Punished him"),
    ("What is the lesson of the Prodigal Son?","God welcomes back anyone who repents","Don't waste money","Stay home","Never forgive"),
    ("In the Sower parable, where did the best seeds grow?","In good soil","On the path","Among thorns","On rocky ground"),
    ("What does the good soil represent?","A person who hears God's word and lives by it","A farmer","A priest","A garden"),
    ("What is the lesson of the Mustard Seed?","God's kingdom starts small but grows very large","Small things don't matter","Plant more seeds","Farming is holy"),
    ("What did the wise man build his house on?","Rock","Sand","Clay","Wood"),
    ("What happened to the foolish man's house built on sand?","It fell down when the storm came","It stood strong","It floated away","It caught fire"),
    ("In the Lost Sheep parable, how many sheep were lost?","1 out of 100","10 out of 100","50 out of 100","99 out of 100"),
    ("What does the shepherd do when he finds the lost sheep?","Celebrates and carries it home on his shoulders","Punishes it","Leaves it","Sells it"),
    ("What is the lesson of the Lost Sheep?","God searches for every lost person and rejoices when they return","Sheep are valuable","Shepherds work hard","Don't wander off"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# MIRACLES
c="Miracles"
qs=[
    ("What was Jesus' first miracle?","Turning water into wine","Healing a blind man","Walking on water","Raising the dead"),
    ("Where did Jesus turn water into wine?","At a wedding in Cana","At the Temple","At a funeral","In the desert"),
    ("How many people did Jesus feed with a boy's lunch?","About 5,000 men plus women and children","100","1,000","500"),
    ("What food did the boy have?","5 loaves and 2 fish","Bread and butter","Fruit and cheese","Rice and beans"),
    ("How many baskets of leftovers were there?","12","5","7","0"),
    ("Who did Jesus bring back to life after 4 days?","Lazarus","Peter","Moses","Paul"),
    ("What did Jesus say to the storm on the sea?","'Peace, be still!'","'Stop now!'","'Go away!'","'Calm down!'"),
    ("What happened to the fig tree Jesus cursed?","It withered and died","It grew fruit","It caught fire","Nothing"),
    ("How did Jesus heal the blind man in John 9?","He made mud and put it on his eyes","He touched his head","He prayed from far away","He used medicine"),
    ("What miracle did Elijah perform on Mount Carmel?","God sent fire from heaven to burn the sacrifice","He parted the sea","He healed a leper","He raised the dead"),
    ("Who was healed of leprosy by washing in the Jordan River?","Naaman","David","Moses","Elijah"),
    ("What happened to Peter's mother-in-law when Jesus visited?","She was healed of a fever","She cooked dinner","She was already well","She was sleeping"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# PSALMS & PROVERBS
c="Psalms & Proverbs"
qs=[
    ("Who wrote most of the Psalms?","David","Moses","Solomon","Paul"),
    ("What Psalm says 'The LORD is my shepherd'?","Psalm 23","Psalm 1","Psalm 100","Psalm 119"),
    ("What does Psalm 23 promise?","God cares for us like a shepherd cares for sheep","Life will be easy","We will never suffer","We will be rich"),
    ("Who wrote most of the Proverbs?","Solomon","David","Moses","Abraham"),
    ("What does Proverbs say is the beginning of wisdom?","The fear of the LORD","Going to school","Reading books","Being old"),
    ("What Psalm says 'Make a joyful noise to the Lord'?","Psalm 100","Psalm 23","Psalm 1","Psalm 150"),
    ("What is the shortest verse in the Bible?","'Jesus wept' (John 11:35)","'Pray always'","'God is love'","'Amen'"),
    ("What does 'The Lord is my shepherd, I shall not want' mean?","God provides everything we need","We should own sheep","We will never be hungry","Shepherds are holy"),
    ("What book says 'To everything there is a season'?","Ecclesiastes","Psalms","Proverbs","Job"),
    ("What book tells the story of a man who suffered but kept faith in God?","Job","Jonah","Jeremiah","Joel"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# REVELATION
c="Revelation & End Times"
qs=[
    ("Who wrote the book of Revelation?","John","Paul","Peter","Luke"),
    ("What is the book of Revelation about?","Visions of the end times and God's ultimate victory","The life of Jesus","The history of Israel","Paul's journeys"),
    ("What number is associated with the Beast?","666","777","999","333"),
    ("What is the last book of the Bible?","Revelation","Malachi","Jude","Acts"),
    ("What is the final battle called?","Armageddon","Jericho","Babel","Megiddo"),
    ("Who wins at the end of Revelation?","God wins — good triumphs over evil","Satan","No one","It's unclear"),
    ("What is the New Jerusalem?","A heavenly city where God lives with His people forever","A rebuilt earthly city","A planet","A garden"),
    ("What will there be none of in heaven?","No more tears, death, mourning, or pain","No more music","No more food","No more angels"),
    ("What does 'Alpha and Omega' mean?","The beginning and the end","The first and second","The strong and weak","The old and new"),
    ("Where was John when he wrote Revelation?","The island of Patmos","Rome","Jerusalem","Egypt"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# ANGELS & DEMONS
c="Angels & Demons"
qs=[
    ("Which angel told Mary she would have a baby?","Gabriel","Michael","Raphael","Uriel"),
    ("What did the angels tell the shepherds on Christmas?","The Savior has been born in Bethlehem","Run and hide","Go to Jerusalem","Stay with your sheep"),
    ("Who is the main enemy of God in the Bible?","Satan (the devil)","Pharaoh","Goliath","Herod"),
    ("What did Satan do in the Garden of Eden?","Tempted Eve to eat the forbidden fruit","Created the garden","Killed an animal","Planted a tree"),
    ("What does the Bible say about angels?","They are God's messengers and servants","They are dead people","They are imaginary","They only appear in dreams"),
    ("What angel is described as an archangel?","Michael","Gabriel","Raphael","Uriel"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# LAWS & COMMANDMENTS
c="Laws & Commandments"
qs=[
    ("How many commandments did God give Moses?","10","7","12","5"),
    ("What is the first commandment?","You shall have no other gods before me","Do not steal","Do not lie","Honor your parents"),
    ("Which commandment says to honor your parents?","The fifth","The first","The tenth","The seventh"),
    ("Which commandment says 'Do not steal'?","The eighth","The sixth","The ninth","The fifth"),
    ("What did Jesus say was the most important commandment?","Love God with all your heart, soul, and mind","Keep the Sabbath","Do not murder","Give to the poor"),
    ("What is the 'Golden Rule'?","Treat others the way you want to be treated","Always tell the truth","Give gold to the poor","Follow all the rules"),
    ("Where did God give the Ten Commandments?","Mount Sinai","Mount Everest","Jerusalem","The Garden of Eden"),
    ("What were the commandments written on?","Two stone tablets","Paper","A scroll","A golden plate"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# PLACES
c="Places & Lands"
qs=[
    ("Where was Jesus born?","Bethlehem","Nazareth","Jerusalem","Jericho"),
    ("Where did Jesus grow up?","Nazareth","Bethlehem","Jerusalem","Capernaum"),
    ("What city is called 'the Holy City'?","Jerusalem","Rome","Bethlehem","Athens"),
    ("What country were the Israelites slaves in?","Egypt","Babylon","Rome","Persia"),
    ("What river was Jesus baptized in?","The Jordan River","The Nile","The Euphrates","The Red Sea"),
    ("Where did Jonah NOT want to go?","Nineveh","Tarshish","Jerusalem","Egypt"),
    ("What sea did Moses part?","The Red Sea","The Dead Sea","The Mediterranean","The Sea of Galilee"),
    ("What land did God promise to Abraham?","Canaan (the Promised Land)","Egypt","Babylon","Rome"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# FOOD, FEASTS
c="Food, Feasts & Offerings"
qs=[
    ("What bread-like food did God send from heaven?","Manna","Pizza","Cake","Crackers"),
    ("What meal do Christians share to remember Jesus' death?","Communion / the Lord's Supper","Passover only","A feast","Breakfast"),
    ("What does the bread represent in communion?","Jesus' body","God's creation","Heaven","The Law"),
    ("What does the wine represent in communion?","Jesus' blood","Joy","The Spirit","Water"),
    ("What holiday remembers Israel's escape from Egypt?","Passover","Christmas","Easter","Hanukkah"),
    ("What was the Passover lamb?","A lamb sacrificed so the angel of death would pass over","A pet","A golden idol","A wild animal"),
    ("What food did Esau trade his birthright for?","A bowl of stew","Bread","Fish","Fruit"),
    ("What did Jesus multiply to feed thousands?","Loaves and fish","Bread and wine","Manna","Figs and dates"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# NUMBERS
c="Numbers & Genealogies"
qs=[
    ("How many books are in the Bible?","66","72","50","100"),
    ("How many apostles did Jesus choose?","12","7","10","3"),
    ("How many tribes of Israel were there?","12","10","7","14"),
    ("How many days was Jesus in the tomb?","3","7","1","40"),
    ("How many commandments did God give?","10","7","12","5"),
    ("How many plagues hit Egypt?","10","7","3","12"),
    ("How many days was Jonah in the fish?","3","7","1","40"),
    ("How many times did Peter deny Jesus?","3","2","1","7"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# DREAMS & VISIONS
c="Dreams & Visions"
qs=[
    ("Who interpreted Pharaoh's dreams about cows and grain?","Joseph","Moses","Daniel","Aaron"),
    ("What did Pharaoh's dream of seven fat cows mean?","Seven years of plenty","Seven kings","Seven plagues","Seven nations"),
    ("What did Jacob dream about at Bethel?","A stairway to heaven with angels going up and down","A burning bush","A golden city","A great flood"),
    ("Who had dreams that his family would bow down to him?","Joseph","David","Solomon","Moses"),
    ("What did God tell Joseph (Mary's husband) in a dream?","Don't be afraid to marry Mary — her baby is from God","Go to Egypt","Build a temple","Name the baby John"),
    ("Who had a vision of dry bones coming to life?","Ezekiel","Daniel","Isaiah","Jeremiah"),
    ("Who was called by God's voice at night as a boy?","Samuel","David","Moses","Joseph"),
    ("What did the wise men dream about after visiting Jesus?","Not to go back to King Herod","To bring more gifts","To stay in Bethlehem","To tell everyone"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# PROPHECY
c="Prophecy & Fulfillment"
qs=[
    ("Did the Old Testament predict Jesus' birth?","Yes — hundreds of years before","No","Only vaguely","Only His death"),
    ("Which prophet said a virgin would have a son?","Isaiah","Jeremiah","Moses","David"),
    ("What name did Isaiah say the child would be called?","Immanuel — meaning 'God with us'","Jesus","Messiah","King"),
    ("Which prophet predicted Jesus would be born in Bethlehem?","Micah","Isaiah","Daniel","Malachi"),
    ("What does 'Messiah' or 'Christ' mean?","The Anointed One — God's chosen savior","A teacher","A king only","A prophet only"),
    ("Did Jesus fulfill Old Testament prophecies?","Yes — He fulfilled hundreds of them","No","Only a few","We don't know"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# WORDS OF JESUS
c="Words of Jesus & OT Roots"
qs=[
    ("What did Jesus say about Himself: 'I am the ___ of life'?","Bread","Light","Way","Water"),
    ("What did Jesus call Himself: 'I am the good ___'?","Shepherd","Teacher","King","Friend"),
    ("What did Jesus say: 'I am the ___, the truth, and the life'?","Way","Light","Door","Bread"),
    ("Where did Jesus get many of His teachings from?","The Old Testament","Greek philosophy","Roman law","His own new ideas"),
    ("When Jesus was tempted, He answered Satan with quotes from which book?","Deuteronomy","Psalms","Isaiah","Genesis"),
    ("What did Jesus say on the cross from Psalm 22?","'My God, my God, why have you forsaken me?'","'It is finished'","'Father, forgive them'","'Into your hands I commit my spirit'"),
]
for q,c1,c2,c3,c4 in qs: Q(c,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# ============================================================================
# FAMOUS VERSE COMPLETION — everyone knows these
# ============================================================================
verses=[
    ("Life of Jesus","'For God so loved the ___ that He gave His only Son...'","world","church","people","Jews"),
    ("Psalms & Proverbs","'The LORD is my ___; I shall not want.'","shepherd","king","father","friend"),
    ("Life of Jesus","'Jesus said, I am the way, the ___, and the life.'","truth","light","hope","love"),
    ("Paul & His Letters","'I can do all things through ___ who strengthens me.'","Christ","God","prayer","faith"),
    ("Life of Jesus","'Ask, and it shall be ___ to you.'","given","shown","told","sent"),
    ("Life of Jesus","'Let he who is without ___ cast the first stone.'","sin","blame","fault","guilt"),
    ("Life of Jesus","'Do not ___, or you too will be judged.'","judge","steal","lie","covet"),
    ("Psalms & Proverbs","'Be still, and know that I am ___.'","God","here","near","watching"),
    ("Life of Jesus","'Come to me, all you who are ___ and burdened, and I will give you rest.'","weary","sinful","lost","poor"),
    ("Psalms & Proverbs","'Trust in the LORD with all your ___.'","heart","mind","strength","soul"),
    ("Paul & His Letters","'For the wages of sin is ___.'","death","pain","shame","poverty"),
    ("Paul & His Letters","'And now these three remain: faith, hope, and ___.'","love","joy","peace","grace"),
    ("Life of Jesus","'Blessed are the ___, for they shall inherit the earth.'","meek","strong","rich","bold"),
    ("Psalms & Proverbs","'Thy ___ is a lamp unto my feet.'","word","light","love","truth"),
    ("Genesis & Creation","'In the ___ God created the heavens and the earth.'","beginning","first day","morning","start"),
    ("Moses & the Exodus","'Let my ___ go!' said Moses to Pharaoh.","people","nation","brothers","children"),
    ("Life of Jesus","'Love your ___ as yourself.'","neighbor","friend","family","brother"),
    ("Life of Jesus","'I am the ___ of the world.'","light","hope","king","bread"),
    ("Paul & His Letters","'By ___ you have been saved, through faith.'","grace","works","law","prayer"),
    ("Life of Jesus","'Go and make ___ of all nations.'","disciples","friends","churches","laws"),
]
for cat,q,c1,c2,c3,c4 in verses:
    Q(cat,"Layperson",f"Complete the verse: {q}",S(c1,[c2,c3,c4]),c1)

# ============================================================================
# BASIC "WHO" QUESTIONS
# ============================================================================
whos=[
    ("Life of Jesus","Who is the Son of God?","Jesus","Moses","David","Paul"),
    ("Genesis & Creation","Who built the ark?","Noah","Moses","Abraham","David"),
    ("Genesis & Creation","Who was the first man?","Adam","Noah","Abraham","Moses"),
    ("Life of Jesus","Who baptized Jesus?","John the Baptist","Peter","Paul","James"),
    ("Kings & Kingdoms","Who killed Goliath?","David","Saul","Joshua","Samson"),
    ("Moses & the Exodus","Who parted the Red Sea?","Moses","Joshua","Elijah","Noah"),
    ("Prophets","Who was swallowed by a big fish?","Jonah","Daniel","Moses","Noah"),
    ("Prophets","Who survived the lion's den?","Daniel","David","Samson","Moses"),
    ("Genesis & Creation","Who was sold by his brothers into slavery?","Joseph","Benjamin","Moses","David"),
    ("Women of the Bible","Who was the mother of Jesus?","Mary","Martha","Elizabeth","Sarah"),
    ("The Apostles","Who denied Jesus three times?","Peter","Thomas","Judas","John"),
    ("The Apostles","Who betrayed Jesus for silver?","Judas Iscariot","Peter","Thomas","Andrew"),
    ("Women of the Bible","Who saved the Jews in Persia?","Esther","Ruth","Deborah","Miriam"),
    ("Kings & Kingdoms","Who was the wisest king?","Solomon","David","Saul","Hezekiah"),
    ("Life of Jesus","Who carried Jesus' cross?","Simon of Cyrene","Peter","John","Paul"),
]
for cat,q,c1,c2,c3,c4 in whos:
    Q(cat,"Layperson",q,S(c1,[c2,c3,c4]),c1)

# ============================================================================
# FINALIZE
# ============================================================================
for i, q in enumerate(ALL):
    q["id"] = hashlib.md5(f"{q['category']}-{q['difficulty']}-{q['question'][:50]}-{i}".encode()).hexdigest()[:12]

from collections import Counter
dc = Counter(q["difficulty"] for q in ALL)
new_count = len(ALL) - start_count

print(f"\n{'='*60}")
print(f"NEW LAYPERSON QUESTIONS: {new_count}")
print(f"GRAND TOTAL: {len(ALL)} questions")
print(f"  Layperson: {dc['Layperson']}  Deacon: {dc['Deacon']}  Pastor: {dc['Pastor']}")
print(f"{'='*60}")

with open("/home/claude/manna/manna_questions.json","w") as f:
    json.dump(ALL, f, indent=2)
import shutil
shutil.copy("/home/claude/manna/manna_questions.json","/home/claude/manna/Manna/Resources/manna_questions.json")
print(f"Saved: {os.path.getsize('/home/claude/manna/manna_questions.json')/1024:.0f} KB")
