#!/usr/bin/env python3
"""
MANNA Bible Trivia — 10,000 Question Generator
Combines handwritten questions with template-generated questions from Bible data tables.
"""
import json, random, hashlib, os
random.seed(42)

ALL = []
def Q(cat,diff,q,opts,cor,exp=""):
    ALL.append({"category":cat,"difficulty":diff,"question":q,"options":opts,"correct":cor,"explanation":exp})

def shuf(correct, wrongs):
    w = [x for x in wrongs if x != correct][:3]
    opts = [correct] + w
    random.shuffle(opts)
    return opts

# ============================================================================
# BIBLE DATA TABLES
# ============================================================================

FATHERS = {
    "Seth":"Adam","Enosh":"Seth","Kenan":"Enosh","Mahalalel":"Kenan",
    "Jared":"Mahalalel","Enoch":"Jared","Methuselah":"Enoch","Lamech":"Methuselah",
    "Noah":"Lamech","Shem":"Noah","Ham":"Noah","Japheth":"Noah",
    "Abraham":"Terah","Isaac":"Abraham","Jacob":"Isaac","Esau":"Isaac",
    "Reuben":"Jacob","Simeon":"Jacob","Levi":"Jacob","Judah":"Jacob",
    "Dan":"Jacob","Naphtali":"Jacob","Gad":"Jacob","Asher":"Jacob",
    "Issachar":"Jacob","Zebulun":"Jacob","Joseph":"Jacob","Benjamin":"Jacob",
    "Ephraim":"Joseph","Manasseh":"Joseph","Moses":"Amram","Aaron":"Amram",
    "Gershom":"Moses","Eliezer":"Moses","Nadab":"Aaron","Abihu":"Aaron",
    "Eleazar":"Aaron","Ithamar":"Aaron","Phinehas":"Eleazar",
    "Obed":"Boaz","Jesse":"Obed","David":"Jesse","Solomon":"David",
    "Rehoboam":"Solomon","Abijah":"Rehoboam","Asa":"Abijah",
    "Jehoshaphat":"Asa","Jehoram":"Jehoshaphat","Uzziah":"Amaziah",
    "Jotham":"Uzziah","Ahaz":"Jotham","Hezekiah":"Ahaz",
    "Manasseh":"Hezekiah","Amon":"Manasseh","Josiah":"Amon",
    "Samuel":"Elkanah","Saul":"Kish","Jonathan":"Saul","Mephibosheth":"Jonathan",
    "Absalom":"David","Adonijah":"David","John the Baptist":"Zechariah",
    "James":"Zebedee","John (Apostle)":"Zebedee","Joshua":"Nun",
    "Caleb":"Jephunneh","Timothy":"(mother Eunice, father Greek)",
    "Ishmael":"Abraham","Perez":"Judah","Hezron":"Perez",
    "Ram":"Hezron","Amminadab":"Ram","Nahshon":"Amminadab",
    "Salmon":"Nahshon","Boaz":"Salmon"
}

MOTHERS = {
    "Cain":"Eve","Abel":"Eve","Seth":"Eve","Isaac":"Sarah","Ishmael":"Hagar",
    "Jacob":"Rebekah","Esau":"Rebekah","Joseph":"Rachel","Benjamin":"Rachel",
    "Reuben":"Leah","Simeon":"Leah","Levi":"Leah","Judah":"Leah",
    "Dan":"Bilhah","Naphtali":"Bilhah","Gad":"Zilpah","Asher":"Zilpah",
    "Issachar":"Leah","Zebulun":"Leah","Moses":"Jochebed","Aaron":"Jochebed",
    "Samuel":"Hannah","Samson":"(wife of Manoah)","Solomon":"Bathsheba",
    "Obed":"Ruth","Jesus":"Mary","John the Baptist":"Elizabeth",
    "Timothy":"Eunice","Perez":"Tamar","Ephraim":"Asenath","Manasseh":"Asenath"
}

WIVES = {
    "Adam":"Eve","Abraham":"Sarah","Isaac":"Rebekah","Jacob":"Rachel and Leah",
    "Joseph":"Asenath","Moses":"Zipporah","Boaz":"Ruth","Elkanah":"Hannah",
    "David":"Michal, Abigail, Bathsheba (and others)","Solomon":"Pharaoh's daughter (and 700 others)",
    "Ahab":"Jezebel","Hosea":"Gomer","Joseph (NT)":"Mary",
    "Aquila":"Priscilla","Nabal":"Abigail","Uriah":"Bathsheba",
    "Lapidoth":"Deborah","Aaron":"Elisheba","Salmon":"Rahab",
    "Amram":"Jochebed","Zechariah (priest)":"Elizabeth"
}

AGES_AT_DEATH = {
    "Adam":930,"Seth":912,"Enosh":905,"Kenan":910,"Mahalalel":895,
    "Jared":962,"Methuselah":969,"Lamech (Gen 5)":777,"Noah":950,
    "Abraham":175,"Sarah":127,"Isaac":180,"Jacob":147,"Joseph":110,
    "Moses":120,"Joshua":110,"Aaron":123
}

HEBREW_GREEK = {
    "Elohim":("God (plural of majesty)","Pastor","Hebrew"),
    "Ruach":("Spirit, wind, or breath","Pastor","Hebrew"),
    "Shalom":("Peace, wholeness, completeness","Deacon","Hebrew"),
    "Hesed":("Lovingkindness or steadfast love","Pastor","Hebrew"),
    "Torah":("Law or instruction","Deacon","Hebrew"),
    "Shema":("Hear or listen","Deacon","Hebrew"),
    "Adonai":("Lord or Master","Deacon","Hebrew"),
    "Hallelujah":("Praise the LORD","Layperson","Hebrew"),
    "Amen":("So be it, truly","Layperson","Hebrew"),
    "Selah":("A musical pause in the Psalms","Deacon","Hebrew"),
    "Bara":("Created from nothing","Pastor","Hebrew"),
    "Nephesh":("Soul or living being","Pastor","Hebrew"),
    "Mashiach":("Messiah, the Anointed One","Deacon","Hebrew"),
    "Tsedaqah":("Righteousness","Pastor","Hebrew"),
    "Qadosh":("Holy, set apart","Pastor","Hebrew"),
    "Immanuel":("God with us","Layperson","Hebrew"),
    "Golgotha":("Place of the skull","Deacon","Aramaic"),
    "Maranatha":("Come, O Lord","Pastor","Aramaic"),
    "Agape":("Unconditional, selfless love","Deacon","Greek"),
    "Logos":("The Word","Deacon","Greek"),
    "Christos":("Christ, the Anointed One","Layperson","Greek"),
    "Ekklesia":("Church or assembly","Pastor","Greek"),
    "Baptizo":("To immerse or baptize","Deacon","Greek"),
    "Parakletos":("Helper, Advocate, Comforter","Pastor","Greek"),
    "Euangelion":("Gospel or good news","Deacon","Greek"),
    "Koinonia":("Fellowship or communion","Pastor","Greek"),
    "Metanoia":("Repentance, change of mind","Pastor","Greek"),
    "Doulos":("Servant or slave","Pastor","Greek"),
    "Bethlehem":("House of bread","Deacon","Hebrew"),
    "Bethel":("House of God","Deacon","Hebrew"),
    "Peniel":("Face of God","Pastor","Hebrew"),
    "Israel":("He who wrestles with God","Deacon","Hebrew"),
    "Babel":("Confusion","Deacon","Hebrew"),
    "Ichabod":("The glory has departed","Pastor","Hebrew"),
    "Ebenezer":("Stone of help","Pastor","Hebrew"),
    "Beersheba":("Well of the oath","Pastor","Hebrew"),
    "Gethsemane":("Oil press","Pastor","Hebrew/Aramaic"),
    "Abba":("Father (intimate)","Deacon","Aramaic"),
    "Hosanna":("Save us, we pray","Deacon","Hebrew"),
    "Sabbath":("Rest","Layperson","Hebrew"),
}

BOOKS_INFO = {
    "Genesis":("The creation, the patriarchs, and Israel's origins","Moses (traditional)","OT","Layperson"),
    "Exodus":("Israel's escape from Egypt and the giving of the Law","Moses (traditional)","OT","Layperson"),
    "Leviticus":("Laws for priests, sacrifices, and holiness","Moses (traditional)","OT","Deacon"),
    "Numbers":("The wilderness wanderings and two censuses","Moses (traditional)","OT","Deacon"),
    "Deuteronomy":("Moses' farewell speeches restating the Law","Moses (traditional)","OT","Deacon"),
    "Joshua":("The conquest and division of the Promised Land","Joshua (traditional)","OT","Layperson"),
    "Judges":("The cycle of sin, oppression, and deliverance","Samuel (traditional)","OT","Deacon"),
    "Ruth":("A Moabite woman's loyalty and redemption","Unknown","OT","Layperson"),
    "1 Samuel":("The rise of Samuel, Saul, and David","Unknown","OT","Deacon"),
    "2 Samuel":("David's reign as king of Israel","Unknown","OT","Deacon"),
    "1 Kings":("Solomon's reign and the divided kingdom","Unknown","OT","Deacon"),
    "2 Kings":("The fall of Israel and Judah","Unknown","OT","Deacon"),
    "1 Chronicles":("Israel's history from Adam to David","Ezra (traditional)","OT","Pastor"),
    "2 Chronicles":("The kings of Judah through the exile","Ezra (traditional)","OT","Pastor"),
    "Ezra":("The return from exile and rebuilding the Temple","Ezra","OT","Deacon"),
    "Nehemiah":("Rebuilding Jerusalem's walls","Nehemiah","OT","Deacon"),
    "Esther":("A Jewish queen who saved her people in Persia","Unknown","OT","Layperson"),
    "Job":("Suffering, faith, and God's sovereignty","Unknown","OT","Deacon"),
    "Psalms":("Songs, prayers, and poetry","David and others","OT","Layperson"),
    "Proverbs":("Wisdom sayings for daily life","Solomon (primarily)","OT","Layperson"),
    "Ecclesiastes":("The meaning of life — 'vanity of vanities'","Solomon (traditional)","OT","Deacon"),
    "Song of Solomon":("A love poem between a bride and groom","Solomon (traditional)","OT","Deacon"),
    "Isaiah":("Prophecies of judgment and the coming Messiah","Isaiah","OT","Deacon"),
    "Jeremiah":("Warnings before Jerusalem's fall","Jeremiah","OT","Deacon"),
    "Lamentations":("Mourning over Jerusalem's destruction","Jeremiah (traditional)","OT","Deacon"),
    "Ezekiel":("Visions and prophecies during the Babylonian exile","Ezekiel","OT","Deacon"),
    "Daniel":("Faithfulness in exile and apocalyptic visions","Daniel","OT","Deacon"),
    "Hosea":("God's faithful love shown through a broken marriage","Hosea","OT","Pastor"),
    "Joel":("The day of the LORD and the outpouring of the Spirit","Joel","OT","Pastor"),
    "Amos":("Social justice and judgment on Israel","Amos","OT","Pastor"),
    "Obadiah":("Judgment on Edom — the shortest OT book","Obadiah","OT","Pastor"),
    "Jonah":("A reluctant prophet and God's mercy on Nineveh","Jonah","OT","Layperson"),
    "Micah":("Justice, mercy, and walking humbly with God","Micah","OT","Pastor"),
    "Nahum":("The fall of Nineveh","Nahum","OT","Pastor"),
    "Habakkuk":("A prophet questioning God about injustice","Habakkuk","OT","Pastor"),
    "Zephaniah":("The coming day of the LORD","Zephaniah","OT","Pastor"),
    "Haggai":("A call to rebuild the Temple after exile","Haggai","OT","Pastor"),
    "Zechariah":("Messianic visions and restoration","Zechariah","OT","Pastor"),
    "Malachi":("The final OT prophet's warnings about faithfulness","Malachi","OT","Pastor"),
    "Matthew":("Jesus as the promised Messiah for Jewish readers","Matthew","NT","Layperson"),
    "Mark":("Jesus as a servant and man of action — the shortest Gospel","Mark","NT","Deacon"),
    "Luke":("Jesus as the Son of Man for all people","Luke","NT","Deacon"),
    "John":("Jesus as the divine Son of God","John","NT","Layperson"),
    "Acts":("The early church and the spread of the gospel","Luke","NT","Layperson"),
    "Romans":("Salvation by faith and God's righteousness","Paul","NT","Deacon"),
    "1 Corinthians":("Addressing divisions and problems in Corinth","Paul","NT","Deacon"),
    "2 Corinthians":("Paul's defense of his ministry and apostleship","Paul","NT","Pastor"),
    "Galatians":("Freedom from the Law through faith in Christ","Paul","NT","Deacon"),
    "Ephesians":("The church as the body of Christ","Paul","NT","Deacon"),
    "Philippians":("Joy and unity in Christ — written from prison","Paul","NT","Deacon"),
    "Colossians":("The supremacy and sufficiency of Christ","Paul","NT","Pastor"),
    "1 Thessalonians":("Encouragement and the return of Christ","Paul","NT","Deacon"),
    "2 Thessalonians":("Clarifying the day of the Lord","Paul","NT","Pastor"),
    "1 Timothy":("Instructions for church leadership","Paul","NT","Deacon"),
    "2 Timothy":("Paul's final letter before his death","Paul","NT","Deacon"),
    "Titus":("Church order and good works in Crete","Paul","NT","Pastor"),
    "Philemon":("An appeal for the runaway slave Onesimus","Paul","NT","Deacon"),
    "Hebrews":("Christ's superiority over the old covenant","Unknown","NT","Deacon"),
    "James":("Faith without works is dead","James","NT","Deacon"),
    "1 Peter":("Hope and holiness in the midst of suffering","Peter","NT","Deacon"),
    "2 Peter":("Warnings against false teachers","Peter","NT","Pastor"),
    "1 John":("God is love and God is light","John","NT","Deacon"),
    "2 John":("Warning against false teachers — second shortest NT book","John","NT","Pastor"),
    "3 John":("Hospitality and truth — shortest NT book","John","NT","Pastor"),
    "Jude":("Contending for the faith against false teachers","Jude","NT","Pastor"),
    "Revelation":("Apocalyptic visions of the end times","John","NT","Deacon"),
}

MIRACLES_DATA = [
    ("Water into wine","Cana","John 2:1-11","Life of Jesus","Layperson"),
    ("Feeding 5,000","Near Bethsaida","John 6:1-14","Life of Jesus","Layperson"),
    ("Walking on water","Sea of Galilee","Matthew 14:22-33","Life of Jesus","Layperson"),
    ("Raising Lazarus","Bethany","John 11:1-44","Life of Jesus","Layperson"),
    ("Calming the storm","Sea of Galilee","Mark 4:35-41","Life of Jesus","Layperson"),
    ("Healing blind Bartimaeus","Jericho","Mark 10:46-52","Life of Jesus","Deacon"),
    ("Healing the paralytic","Capernaum","Mark 2:1-12","Life of Jesus","Layperson"),
    ("Great catch of fish","Sea of Galilee","Luke 5:1-11","Life of Jesus","Deacon"),
    ("Withered hand healed","A synagogue","Mark 3:1-6","Life of Jesus","Deacon"),
    ("Woman with issue of blood","On the road","Mark 5:25-34","Life of Jesus","Deacon"),
    ("Raising widow's son at Nain","Nain","Luke 7:11-17","Life of Jesus","Deacon"),
    ("Healing ten lepers","Samaria/Galilee border","Luke 17:11-19","Life of Jesus","Deacon"),
    ("Centurion's servant healed","Capernaum","Matthew 8:5-13","Life of Jesus","Deacon"),
    ("Syrophoenician woman's daughter","Region of Tyre","Mark 7:24-30","Life of Jesus","Deacon"),
    ("Feeding 4,000","Decapolis","Mark 8:1-10","Life of Jesus","Deacon"),
    ("Man born blind healed","Jerusalem","John 9:1-12","Life of Jesus","Deacon"),
    ("Cursing the fig tree","Near Bethany","Mark 11:12-14","Life of Jesus","Deacon"),
    ("Coin in fish's mouth","Capernaum","Matthew 17:24-27","Life of Jesus","Pastor"),
    ("Malchus' ear healed","Gethsemane","Luke 22:50-51","Life of Jesus","Pastor"),
    ("Man at pool of Bethesda","Jerusalem","John 5:1-15","Life of Jesus","Pastor"),
    ("Deaf and mute man healed","Decapolis","Mark 7:31-37","Life of Jesus","Pastor"),
    ("Raising Jairus' daughter","Capernaum","Mark 5:21-43","Life of Jesus","Deacon"),
    ("Post-resurrection catch of fish","Sea of Tiberias","John 21:1-14","Life of Jesus","Pastor"),
    ("Transfiguration","A high mountain","Matthew 17:1-8","Life of Jesus","Deacon"),
    ("Moses parting the Red Sea","Red Sea","Exodus 14","Moses & the Exodus","Layperson"),
    ("Water from the rock","Rephidim/Meribah","Exodus 17","Moses & the Exodus","Layperson"),
    ("Manna from heaven","Wilderness","Exodus 16","Moses & the Exodus","Layperson"),
    ("Aaron's rod buds","Before the Tabernacle","Numbers 17","Moses & the Exodus","Deacon"),
    ("Burning bush","Mount Horeb","Exodus 3","Moses & the Exodus","Layperson"),
    ("Ten plagues of Egypt","Egypt","Exodus 7-12","Moses & the Exodus","Layperson"),
    ("Jordan River parted","Jordan River","Joshua 3","Battles & Wars","Deacon"),
    ("Walls of Jericho fall","Jericho","Joshua 6","Battles & Wars","Layperson"),
    ("Sun stands still","Gibeon","Joshua 10","Battles & Wars","Deacon"),
    ("Elijah calls fire from heaven","Mount Carmel","1 Kings 18","Miracles","Layperson"),
    ("Elijah fed by ravens","Brook Cherith","1 Kings 17","Miracles","Deacon"),
    ("Elijah raises the widow's son","Zarephath","1 Kings 17","Miracles","Deacon"),
    ("Widow's oil multiplied (Elisha)","A widow's house","2 Kings 4:1-7","Miracles","Deacon"),
    ("Naaman healed of leprosy","Jordan River","2 Kings 5","Miracles","Deacon"),
    ("Elisha raises the Shunammite's son","Shunem","2 Kings 4:8-37","Miracles","Deacon"),
    ("Floating ax head","Jordan River","2 Kings 6:1-7","Miracles","Pastor"),
    ("Elisha's bones raise a dead man","Elisha's tomb","2 Kings 13:20-21","Miracles","Pastor"),
    ("Daniel in the lion's den","Babylon","Daniel 6","Miracles","Layperson"),
    ("Three men in the fiery furnace","Babylon","Daniel 3","Miracles","Layperson"),
    ("Balaam's donkey speaks","Road to Moab","Numbers 22","Miracles","Deacon"),
    ("Samson's strength","Various","Judges 14-16","Miracles","Layperson"),
    ("Peter walks on water","Sea of Galilee","Matthew 14:28-31","Miracles","Deacon"),
    ("Peter's shadow heals","Jerusalem","Acts 5:15","Miracles","Pastor"),
    ("Paul bitten by snake, unharmed","Malta","Acts 28:3-6","Miracles","Deacon"),
    ("Peter raises Tabitha/Dorcas","Joppa","Acts 9:36-42","Miracles","Deacon"),
    ("Paul raises Eutychus","Troas","Acts 20:7-12","Miracles","Pastor"),
    ("Philip transported","Road to Gaza","Acts 8:39-40","Miracles","Pastor"),
]

PARABLES_DATA = [
    ("The Good Samaritan","Luke 10:25-37","Love your neighbor — even your enemy","Layperson"),
    ("The Prodigal Son","Luke 15:11-32","God's boundless forgiveness","Layperson"),
    ("The Sower","Matthew 13:1-23","People receive God's word differently","Layperson"),
    ("The Mustard Seed","Matthew 13:31-32","God's kingdom starts tiny but grows huge","Layperson"),
    ("The Lost Sheep","Luke 15:1-7","God pursues every lost person","Layperson"),
    ("The Talents","Matthew 25:14-30","Use what God gives you faithfully","Layperson"),
    ("The Wise and Foolish Builders","Matthew 7:24-27","Build your life on God's word","Layperson"),
    ("The Lost Coin","Luke 15:8-10","Heaven rejoices over one sinner who repents","Layperson"),
    ("The Pearl of Great Price","Matthew 13:45-46","The kingdom is worth everything","Deacon"),
    ("The Ten Virgins","Matthew 25:1-13","Be ready for Christ's return","Deacon"),
    ("The Wheat and Tares","Matthew 13:24-30","Good and evil coexist until judgment","Deacon"),
    ("The Unforgiving Servant","Matthew 18:21-35","Forgive as you have been forgiven","Deacon"),
    ("The Rich Fool","Luke 12:13-21","Don't store up earthly treasures","Deacon"),
    ("The Vineyard Workers","Matthew 20:1-16","God's grace isn't earned by merit","Deacon"),
    ("The Wedding Banquet","Matthew 22:1-14","Many are invited, few accept","Deacon"),
    ("The Fig Tree","Luke 13:6-9","Bear fruit or face judgment","Deacon"),
    ("The Leaven","Matthew 13:33","The kingdom permeates everything","Deacon"),
    ("The Pharisee and Tax Collector","Luke 18:9-14","God honors humility, not self-righteousness","Deacon"),
    ("The Rich Man and Lazarus","Luke 16:19-31","Eternal consequences of ignoring the poor","Deacon"),
    ("The Sheep and Goats","Matthew 25:31-46","Serving others is serving Christ","Deacon"),
    ("The Hidden Treasure","Matthew 13:44","The kingdom is worth any sacrifice","Deacon"),
    ("The Narrow Door","Luke 13:22-30","Enter through the narrow way","Deacon"),
    ("The Unjust Judge","Luke 18:1-8","Persist in prayer and don't give up","Pastor"),
    ("The Dragnet","Matthew 13:47-50","Judgment separates good from evil","Pastor"),
    ("The Two Debtors","Luke 7:41-43","Greater forgiveness produces greater love","Pastor"),
    ("The Shrewd Manager","Luke 16:1-13","Use worldly resources wisely for eternity","Pastor"),
    ("The Growing Seed","Mark 4:26-29","God's kingdom grows mysteriously","Pastor"),
    ("The Wicked Tenants","Matthew 21:33-46","Israel's rejection of God's messengers","Pastor"),
    ("The Minas","Luke 19:11-27","Be faithful with what's entrusted","Pastor"),
    ("The Friend at Midnight","Luke 11:5-8","Be bold and persistent in prayer","Pastor"),
    ("The Two Sons","Matthew 21:28-32","Actions matter more than words","Deacon"),
    ("The Barren Fig Tree","Luke 13:6-9","God is patient but expects fruit","Deacon"),
]

WOMEN_DATA = {
    "Eve":("First woman, mother of all living","Genesis","Layperson"),
    "Sarah":("Abraham's wife, mother of Isaac at age 90","Genesis","Layperson"),
    "Hagar":("Sarah's Egyptian servant, mother of Ishmael","Genesis","Deacon"),
    "Rebekah":("Isaac's wife who helped Jacob get the blessing","Genesis","Layperson"),
    "Rachel":("Jacob's beloved wife, mother of Joseph and Benjamin","Genesis","Layperson"),
    "Leah":("Jacob's first wife, mother of Judah and five other sons","Genesis","Deacon"),
    "Miriam":("Moses' sister, prophetess, led worship after Red Sea","Exodus","Deacon"),
    "Rahab":("Prostitute in Jericho who hid the Israelite spies","Joshua","Deacon"),
    "Deborah":("Judge and prophetess who led Israel to victory over Sisera","Judges","Deacon"),
    "Ruth":("Moabite who was loyal to Naomi, great-grandmother of David","Ruth","Layperson"),
    "Naomi":("Ruth's mother-in-law who returned from Moab to Bethlehem","Ruth","Layperson"),
    "Hannah":("Mother of Samuel, prayed fervently for a child","1 Samuel","Layperson"),
    "Bathsheba":("Wife of Uriah, then David; mother of Solomon","2 Samuel","Deacon"),
    "Jezebel":("Evil queen who promoted Baal worship in Israel","1 Kings","Layperson"),
    "Esther":("Jewish queen who saved her people from Haman's plot","Esther","Layperson"),
    "Mary, mother of Jesus":("Virgin who bore the Son of God","Gospels","Layperson"),
    "Mary Magdalene":("Devoted follower of Jesus, first to see Him risen","Gospels","Layperson"),
    "Martha":("Sister of Mary and Lazarus, served Jesus in Bethany","Luke/John","Deacon"),
    "Mary of Bethany":("Sat at Jesus' feet, anointed Him with perfume","Luke/John","Deacon"),
    "Elizabeth":("Mother of John the Baptist, relative of Mary","Luke","Deacon"),
    "Delilah":("Betrayed Samson by learning the secret of his strength","Judges","Layperson"),
    "Abigail":("Wise woman who prevented David from bloodshed, became his wife","1 Samuel","Deacon"),
    "Jael":("Killed the enemy general Sisera with a tent peg","Judges","Deacon"),
    "Priscilla":("Co-worker with Paul, taught Apollos with her husband Aquila","Acts","Pastor"),
    "Lydia":("First European convert, dealer in purple cloth in Philippi","Acts","Deacon"),
    "Tamar (Genesis)":("Judah's daughter-in-law, ancestor of David and Jesus","Genesis","Pastor"),
    "Huldah":("Prophetess consulted when the Book of the Law was found","2 Kings","Pastor"),
    "Anna":("84-year-old prophetess who recognized baby Jesus in the Temple","Luke","Deacon"),
    "Phoebe":("Deaconess of the church at Cenchreae, commended by Paul","Romans","Pastor"),
    "Dorcas/Tabitha":("Disciple in Joppa raised from death by Peter","Acts","Deacon"),
    "Jochebed":("Moses' mother who hid him in a basket","Exodus","Deacon"),
    "Zipporah":("Moses' wife, daughter of Jethro","Exodus","Deacon"),
    "Vashti":("Persian queen who refused the king's command, replaced by Esther","Esther","Deacon"),
    "Michal":("Saul's daughter, David's first wife who despised his dancing","1-2 Samuel","Pastor"),
    "The Samaritan woman":("Met Jesus at the well, told her whole town about Him","John 4","Layperson"),
    "The woman caught in adultery":("Jesus said 'Let him who is without sin cast the first stone'","John 8","Layperson"),
}

PLACES_DATA = {
    "Jerusalem":("The holy city, site of the Temple and Jesus' crucifixion","Layperson"),
    "Bethlehem":("Birthplace of Jesus and King David","Layperson"),
    "Nazareth":("Where Jesus grew up","Layperson"),
    "Capernaum":("Jesus' home base of ministry in Galilee","Deacon"),
    "Jericho":("First city conquered in Canaan — walls fell down","Layperson"),
    "Bethany":("Home of Mary, Martha, and Lazarus","Deacon"),
    "Gethsemane":("Garden where Jesus prayed before His arrest","Layperson"),
    "Golgotha":("Where Jesus was crucified — 'Place of the Skull'","Layperson"),
    "Mount Sinai":("Where God gave Moses the Ten Commandments","Layperson"),
    "Mount Carmel":("Where Elijah confronted the prophets of Baal","Deacon"),
    "Mount Ararat":("Where Noah's ark came to rest","Layperson"),
    "Mount Nebo":("Where Moses saw the Promised Land and died","Deacon"),
    "Mount Moriah":("Where Abraham nearly sacrificed Isaac","Deacon"),
    "Mount of Olives":("Where Jesus ascended to heaven","Deacon"),
    "Babylon":("Empire that destroyed Jerusalem in 586 BC","Layperson"),
    "Egypt":("Where Israel was enslaved for 400 years","Layperson"),
    "Nineveh":("City Jonah was reluctantly sent to preach to","Layperson"),
    "Damascus":("Where Saul/Paul was converted","Deacon"),
    "Antioch":("Where believers were first called 'Christians'","Deacon"),
    "Corinth":("Greek city where Paul planted a church and wrote letters","Deacon"),
    "Ephesus":("Major city of Paul's ministry in Asia Minor","Deacon"),
    "Rome":("Capital of the empire where Paul was imprisoned","Deacon"),
    "Tarshish":("Where Jonah tried to flee instead of going to Nineveh","Deacon"),
    "Ur":("Abraham's original homeland in Mesopotamia","Deacon"),
    "Hebron":("Where Abraham settled and David first reigned","Deacon"),
    "Samaria":("Capital of the northern kingdom, later a mixed region","Deacon"),
    "Bethel":("Where Jacob dreamed of a ladder to heaven","Deacon"),
    "Shiloh":("Where the Tabernacle was kept before the Temple","Pastor"),
    "Beersheba":("Southern boundary of Israel","Pastor"),
    "Dan":("Northern boundary of Israel","Pastor"),
    "Philippi":("Where Paul and Silas were jailed and freed by earthquake","Deacon"),
    "Thessalonica":("Where Paul started a church amid persecution","Deacon"),
    "Patmos":("Island where John wrote the book of Revelation","Deacon"),
    "Emmaus":("Road where two disciples met the risen Jesus","Deacon"),
    "Cana":("Where Jesus performed His first miracle — water to wine","Layperson"),
    "Dothan":("Where Joseph was thrown into a pit by his brothers","Pastor"),
    "Kadesh Barnea":("Where Israel refused to enter the Promised Land","Pastor"),
    "Shechem":("Where Jacob bought land and where Israel later gathered","Pastor"),
    "Caesarea Philippi":("Where Peter confessed Jesus as the Christ","Pastor"),
    "Tyre and Sidon":("Phoenician cities visited by Jesus and condemned by prophets","Pastor"),
}

FEASTS_DATA = {
    "Passover":("Commemorates Israel's deliverance from Egypt","Nisan 14","Exodus 12","Layperson"),
    "Unleavened Bread":("Seven days eating bread without yeast after Passover","Nisan 15-21","Leviticus 23","Deacon"),
    "Firstfruits":("Offering the first grain of harvest to God","Day after Sabbath during UB","Leviticus 23","Pastor"),
    "Pentecost / Shavuot":("Wheat harvest; giving of the Law; Holy Spirit came","50 days after Firstfruits","Acts 2","Deacon"),
    "Trumpets / Rosh Hashanah":("Blowing of trumpets, sacred assembly","Tishri 1","Leviticus 23","Deacon"),
    "Day of Atonement / Yom Kippur":("Annual atonement for all Israel's sins","Tishri 10","Leviticus 16","Deacon"),
    "Tabernacles / Sukkot":("Living in booths to remember the wilderness","Tishri 15-21","Leviticus 23","Deacon"),
    "Purim":("Celebrates deliverance through Queen Esther","Adar 14-15","Esther 9","Deacon"),
    "Hanukkah / Dedication":("Rededication of the Temple after the Maccabees","Kislev 25","John 10:22 (NT mention)","Pastor"),
}

DREAMS_DATA = [
    ("Jacob","A ladder reaching to heaven with angels","Genesis 28","Layperson"),
    ("Joseph (OT)","His brothers' sheaves bowing to his","Genesis 37","Layperson"),
    ("Joseph (OT)","Sun, moon, and 11 stars bowing to him","Genesis 37","Deacon"),
    ("Pharaoh","Seven fat cows devoured by seven thin cows","Genesis 41","Layperson"),
    ("Pharaoh","Seven full heads of grain devoured by seven thin ones","Genesis 41","Deacon"),
    ("Pharaoh's baker","Three baskets on his head with birds eating","Genesis 40","Deacon"),
    ("Pharaoh's cupbearer","A vine with three branches bearing grapes","Genesis 40","Deacon"),
    ("Solomon","God offered him anything — he chose wisdom","1 Kings 3","Deacon"),
    ("Nebuchadnezzar","A great statue of gold, silver, bronze, iron, clay","Daniel 2","Deacon"),
    ("Nebuchadnezzar","A great tree that was cut down","Daniel 4","Deacon"),
    ("Daniel","Four beasts rising from the sea","Daniel 7","Pastor"),
    ("Daniel","A ram and a goat — representing kingdoms","Daniel 8","Pastor"),
    ("Ezekiel","A valley of dry bones coming to life","Ezekiel 37","Deacon"),
    ("Ezekiel","A wheel within a wheel, covered with eyes","Ezekiel 1","Pastor"),
    ("Isaiah","God on a throne with seraphim crying 'Holy, holy, holy'","Isaiah 6","Deacon"),
    ("Peter","A sheet of unclean animals — 'Do not call anything impure'","Acts 10","Deacon"),
    ("Paul","A man from Macedonia saying 'Come over and help us'","Acts 16","Deacon"),
    ("John","The risen Christ among seven golden lampstands","Revelation 1","Deacon"),
    ("Joseph (NT)","An angel saying Mary's child was from the Holy Spirit","Matthew 1","Layperson"),
    ("The Magi","Warned not to return to Herod","Matthew 2","Layperson"),
    ("Pilate's wife","She suffered in a dream about Jesus","Matthew 27","Pastor"),
    ("Ananias","Told to go to Straight Street and heal Saul","Acts 9","Pastor"),
    ("Cornelius","An angel telling him to send for Peter","Acts 10","Pastor"),
    ("Samuel","God called his name three times at night","1 Samuel 3","Layperson"),
    ("Moses","A bush on fire but not consumed — God's presence","Exodus 3","Layperson"),
    ("Elijah","God in a still small voice — not in wind, earthquake, or fire","1 Kings 19","Deacon"),
    ("Micaiah","God on His throne sending a lying spirit to Ahab's prophets","1 Kings 22","Pastor"),
    ("Zechariah","Eight night visions including a flying scroll and lampstand","Zechariah 1-6","Pastor"),
    ("Abraham","A deep sleep, smoking firepot and blazing torch between pieces","Genesis 15","Pastor"),
    ("Gideon","A Midianite dreamed of a barley loaf tumbling into camp","Judges 7","Pastor"),
]

PROPHETS_INFO = {
    "Isaiah":("Judah","The suffering servant and coming Messiah","Major","Layperson"),
    "Jeremiah":("Judah","The weeping prophet who warned of Jerusalem's fall","Major","Layperson"),
    "Ezekiel":("Babylon (exile)","Dramatic visions — dry bones, wheels, future temple","Major","Deacon"),
    "Daniel":("Babylon (exile)","Faithfulness in exile, apocalyptic visions","Major","Layperson"),
    "Hosea":("Northern Israel","Married an unfaithful wife to mirror God's love","Minor","Deacon"),
    "Joel":("Judah","Day of the LORD and the outpouring of the Spirit","Minor","Deacon"),
    "Amos":("Northern Israel","A shepherd who preached social justice","Minor","Deacon"),
    "Obadiah":("Edom","Judgment on Edom — the shortest OT book","Minor","Pastor"),
    "Jonah":("Nineveh","Ran from God, swallowed by a great fish","Minor","Layperson"),
    "Micah":("Judah","'What does the LORD require? Act justly, love mercy, walk humbly'","Minor","Deacon"),
    "Nahum":("Nineveh","Foretold the destruction of Nineveh","Minor","Pastor"),
    "Habakkuk":("Judah","Questioned God about injustice — 'the just shall live by faith'","Minor","Pastor"),
    "Zephaniah":("Judah","The coming day of the LORD","Minor","Pastor"),
    "Haggai":("Post-exile Judah","Urged the people to rebuild the Temple","Minor","Pastor"),
    "Zechariah":("Post-exile Judah","Messianic visions and promises of restoration","Minor","Pastor"),
    "Malachi":("Post-exile Judah","Last OT prophet — 'I will send my messenger'","Minor","Deacon"),
    "Elijah":("Northern Israel","Confronted Baal worship, called fire from heaven","Non-writing","Layperson"),
    "Elisha":("Northern Israel","Performed twice as many miracles as Elijah","Non-writing","Deacon"),
    "Samuel":("Israel","Last judge, anointed both Saul and David","Non-writing","Layperson"),
    "Nathan":("Judah","Confronted David about Bathsheba with a parable","Non-writing","Deacon"),
}

# NUMBERS & SPECIFIC FACTS
NUMBERS_FACTS = [
    ("How many books are in the Bible (Protestant canon)?","66","39","73","27","Layperson"),
    ("How many books are in the Old Testament?","39","27","66","46","Layperson"),
    ("How many books are in the New Testament?","27","39","22","31","Layperson"),
    ("How many tribes of Israel were there?","12","10","7","14","Layperson"),
    ("How many apostles did Jesus choose?","12","7","10","14","Layperson"),
    ("How many days and nights was Jesus in the tomb?","3","2","1","7","Layperson"),
    ("How many days did Jesus fast in the wilderness?","40","30","7","21","Layperson"),
    ("How many days did it rain during Noah's flood?","40","7","100","150","Layperson"),
    ("How many commandments did God give Moses?","10","7","12","5","Layperson"),
    ("How many plagues struck Egypt?","10","7","12","9","Layperson"),
    ("How many years did the Israelites wander?","40","30","50","70","Layperson"),
    ("How many stones did David pick up to fight Goliath?","5","1","3","7","Deacon"),
    ("How many lepers did Jesus heal at once?","10","7","3","12","Deacon"),
    ("How many loaves fed the 5,000?","5","7","2","12","Layperson"),
    ("How many fish fed the 5,000?","2","5","3","7","Deacon"),
    ("How many loaves fed the 4,000?","7","5","12","3","Deacon"),
    ("How many baskets were left after feeding the 5,000?","12","7","5","3","Deacon"),
    ("How many baskets were left after feeding the 4,000?","7","12","5","3","Deacon"),
    ("How many silver coins betrayed Jesus?","30","20","40","50","Layperson"),
    ("How many days between Jesus' resurrection and ascension?","40","3","7","50","Deacon"),
    ("How many days after the ascension was Pentecost?","10","40","7","50","Deacon"),
    ("How many chapters in the book of Psalms?","150","100","120","200","Deacon"),
    ("How many proverbs did Solomon speak according to 1 Kings?","3,000","1,000","500","150","Pastor"),
    ("How many songs did Solomon compose?","1,005","150","500","3,000","Pastor"),
    ("How many years did Solomon take to build the Temple?","7","10","20","3","Deacon"),
    ("How many years did Solomon take to build his palace?","13","7","20","10","Pastor"),
    ("How many times did Peter deny Jesus?","3","2","1","7","Layperson"),
    ("How many times did Jesus ask Peter 'Do you love me?'","3","2","7","1","Deacon"),
    ("How many churches does Revelation address?","7","12","5","10","Deacon"),
    ("How many seals in Revelation?","7","12","4","10","Deacon"),
    ("How many trumpets in Revelation?","7","12","4","10","Deacon"),
    ("How many bowls of wrath in Revelation?","7","12","4","10","Pastor"),
    ("How many spies did Moses send to Canaan?","12","10","7","2","Deacon"),
    ("How many judges are named in the book of Judges?","12","7","15","10","Pastor"),
    ("How old was Jesus when He began His ministry?","About 30","33","25","40","Deacon"),
    ("How many days was Jonah in the belly of the great fish?","3","7","1","40","Layperson"),
    ("How many wives did Solomon have?","700","300","100","1,000","Layperson"),
    ("How many concubines did Solomon have?","300","700","100","500","Deacon"),
    ("At what age did Josiah become king?","8","12","16","20","Deacon"),
    ("At what age did Joash become king?","7","8","12","16","Pastor"),
    ("How many sons did Jesse have?","8","7","12","6","Deacon"),
    ("How old was Abraham when God called him to leave Ur?","75","80","65","100","Deacon"),
    ("How many people were saved on Noah's ark?","8","12","6","10","Deacon"),
    ("How many chapters in the longest book of the Bible (Psalms)?","150","120","100","176","Deacon"),
    ("What is the longest chapter in the Bible?","Psalm 119 (176 verses)","Psalm 150","Genesis 1","Revelation 22","Pastor"),
    ("What is the shortest verse in the Bible (English)?","'Jesus wept' (John 11:35)","'Pray continually' (1 Thess 5:17)","'Rejoice always' (1 Thess 5:16)","'Amen' (Rev 22:21)","Layperson"),
    ("How many fruits of the Spirit are listed in Galatians 5?","9","7","12","10","Deacon"),
    ("How many pieces of armor in Ephesians 6?","6","7","5","4","Deacon"),
    ("How many beatitudes are in Matthew 5?","8 (or 9)","7","10","12","Deacon"),
    ("How many times does the Bible say to forgive? (Matthew 18)","70 times 7 (or 77)","7 times","100 times","Unlimited (no number given)","Deacon"),
]

# ============================================================================
# NOW GENERATE ALL QUESTIONS USING DATA + TEMPLATES
# ============================================================================

print("Generating questions from data tables...")

# --- Template: "Who was the father of X?" ---
father_items = list(FATHERS.items())
random.shuffle(father_items)
for child, father in father_items[:80]:
    all_fathers = list(set(FATHERS.values()))
    wrongs = [f for f in all_fathers if f != father][:10]
    random.shuffle(wrongs)
    diff = "Deacon" if child in ["Methuselah","Phinehas","Caleb","Hezron","Ram","Nahshon","Salmon","Perez"] else "Layperson" if child in ["Isaac","Jacob","Moses","David","Solomon","Jesus","Samuel","Joseph"] else "Deacon"
    # Assign to Numbers & Genealogies
    Q("Numbers & Genealogies", diff, f"Who was the father of {child}?",
      shuf(father, wrongs[:3]), father)

# --- Template: "Who was the mother of X?" ---
for child, mother in list(MOTHERS.items())[:30]:
    all_mothers = list(set(MOTHERS.values()))
    wrongs = [m for m in all_mothers if m != mother]
    random.shuffle(wrongs)
    diff = "Layperson" if child in ["Jesus","Moses","Isaac","Samuel","Jacob","Esau","Cain","Abel","Seth"] else "Deacon"
    Q("Numbers & Genealogies", diff, f"Who was the mother of {child}?",
      shuf(mother, wrongs[:3]), mother)

# --- Template: "How old was X when they died?" ---
for person, age in AGES_AT_DEATH.items():
    wrong_ages = [str(a) for a in AGES_AT_DEATH.values() if a != age]
    random.shuffle(wrong_ages)
    diff = "Pastor" if person in ["Seth","Enosh","Kenan","Mahalalel","Jared","Lamech (Gen 5)"] else "Deacon"
    Q("Numbers & Genealogies", diff, f"How old was {person} when they died?",
      shuf(str(age), wrong_ages[:3]), str(age))

# --- Template: "What does [Hebrew/Greek word] mean?" ---
for word, (meaning, diff, lang) in HEBREW_GREEK.items():
    all_meanings = [m for w,(m,d,l) in HEBREW_GREEK.items() if w != word]
    random.shuffle(all_meanings)
    cat = "Psalms & Proverbs" if word in ["Selah","Hallelujah","Shalom"] else "Laws & Commandments" if word in ["Torah","Sabbath","Qadosh"] else "Life of Jesus" if word in ["Christos","Immanuel","Golgotha","Hosanna","Logos"] else "Paul & His Letters" if word in ["Agape","Ekklesia","Koinonia","Metanoia","Doulos","Parakletos","Euangelion","Baptizo","Maranatha","Abba"] else "Places & Lands" if word in ["Bethlehem","Bethel","Peniel","Beersheba","Gethsemane","Babel","Israel"] else "Genesis & Creation" if word in ["Elohim","Ruach","Bara","Tehom","Nephesh","Tohu"] else "Prophecy & Fulfillment" if word in ["Mashiach","Immanuel"] else "Moses & the Exodus" if word in ["Adonai","YHWH","Shema"] else "Numbers & Genealogies"
    Q(cat, diff, f"What does the {lang} word '{word}' mean?",
      shuf(meaning, all_meanings[:3]), meaning)

# --- Template: "What is the book of X about?" ---
for book, (about, author, testament, diff) in BOOKS_INFO.items():
    other_abouts = [a for b,(a,au,t,d) in BOOKS_INFO.items() if b != book]
    random.shuffle(other_abouts)
    cat = "Psalms & Proverbs" if book in ["Psalms","Proverbs","Ecclesiastes","Song of Solomon","Job"] else "Prophets" if book in list(PROPHETS_INFO.keys()) or book in ["Lamentations"] else "Paul & His Letters" if author == "Paul" else "The Apostles" if book in ["Acts","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Hebrews"] else "Revelation & End Times" if book == "Revelation" else "Life of Jesus" if book in ["Matthew","Mark","Luke","John"] else "Genesis & Creation" if book == "Genesis" else "Moses & the Exodus" if book in ["Exodus","Leviticus","Numbers","Deuteronomy"] else "Kings & Kingdoms" if book in ["1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles"] else "Places & Lands"
    Q(cat, diff, f"What is the book of {book} primarily about?",
      shuf(about, other_abouts[:3]), about)

# --- Template: "Who wrote the book of X?" (where author is meaningful) ---
authored_books = [(b,au) for b,(ab,au,t,d) in BOOKS_INFO.items() if au not in ["Unknown"]]
random.shuffle(authored_books)
for book, author in authored_books[:40]:
    all_authors = list(set([au for b,(ab,au,t,d) in BOOKS_INFO.items()]))
    wrongs = [a for a in all_authors if a != author]
    random.shuffle(wrongs)
    diff = "Deacon" if book in ["Romans","Acts","Psalms","Proverbs","Isaiah","Jeremiah"] else "Pastor"
    cat = "Paul & His Letters" if author == "Paul" else "Prophets" if book in list(PROPHETS_INFO.keys()) else "Psalms & Proverbs" if book in ["Psalms","Proverbs"] else "Life of Jesus" if book in ["Matthew","Mark","Luke","John"] else "Numbers & Genealogies"
    Q(cat, diff, f"Who is the traditional author of the book of {book}?",
      shuf(author, wrongs[:3]), author)

# --- Template: Miracles questions ---
for name, place, ref, cat_assign, diff in MIRACLES_DATA:
    # "Where did X miracle happen?"
    all_places = list(set([p for n,p,r,c,d in MIRACLES_DATA]))
    wrongs = [p for p in all_places if p != place]
    random.shuffle(wrongs)
    Q("Miracles", diff, f"Where did the miracle of {name.lower()} take place?",
      shuf(place, wrongs[:3]), place, ref)
    # "In which book/reference is X miracle found?"
    all_refs = list(set([r.split(":")[0] if ":" in r else r for n,p,r,c,d in MIRACLES_DATA]))
    ref_short = ref.split(":")[0] if ":" in ref else ref
    wrongs_ref = [r for r in all_refs if r != ref_short]
    random.shuffle(wrongs_ref)
    if len(wrongs_ref) >= 3:
        Q("Miracles", diff, f"Where in the Bible is the miracle of {name.lower()} recorded?",
          shuf(ref, [f"{w}:1-10" for w in wrongs_ref[:3]]), ref)

# --- Template: Parables questions ---
for name, ref, meaning, diff in PARABLES_DATA:
    # "What is the main lesson of X?"
    all_meanings = [m for n,r,m,d in PARABLES_DATA if m != meaning]
    random.shuffle(all_meanings)
    Q("Parables", diff, f"What is the main lesson of the parable of {name}?",
      shuf(meaning, all_meanings[:3]), meaning, ref)
    # "Where is the parable of X found?"
    all_refs = [r for n,r,m,d in PARABLES_DATA if r != ref]
    random.shuffle(all_refs)
    diff2 = "Deacon" if diff == "Layperson" else "Pastor"
    Q("Parables", diff2, f"Where in the Bible is the parable of {name} found?",
      shuf(ref, all_refs[:3]), ref)

# --- Template: Women of the Bible ---
for name, (desc, book, diff) in WOMEN_DATA.items():
    all_descs = [d for n,(d,b,df) in WOMEN_DATA.items() if n != name]
    random.shuffle(all_descs)
    Q("Women of the Bible", diff, f"Who was {name} in the Bible?",
      shuf(desc, all_descs[:3]), desc)
    # Where are they found?
    all_books = list(set([b for n,(d,b,df) in WOMEN_DATA.items()]))
    wrongs = [b for b in all_books if b != book]
    random.shuffle(wrongs)
    diff2 = "Deacon" if diff == "Layperson" else "Pastor"
    Q("Women of the Bible", diff2, f"In which book(s) does {name} primarily appear?",
      shuf(book, wrongs[:3]), book)

# --- Template: Places ---
for place, (desc, diff) in PLACES_DATA.items():
    all_descs = [d for p,(d,df) in PLACES_DATA.items() if p != place]
    random.shuffle(all_descs)
    Q("Places & Lands", diff, f"What is {place} known for in the Bible?",
      shuf(desc, all_descs[:3]), desc)

# --- Template: Feasts ---
for feast, (desc, timing, ref, diff) in FEASTS_DATA.items():
    all_descs = [d for f,(d,t,r,df) in FEASTS_DATA.items() if f != feast]
    random.shuffle(all_descs)
    Q("Food, Feasts & Offerings", diff, f"What does the feast of {feast} celebrate?",
      shuf(desc, all_descs[:3]), desc, ref)
    # Timing question
    all_times = [t for f,(d,t,r,df) in FEASTS_DATA.items() if t != timing]
    random.shuffle(all_times)
    if len(all_times) >= 3:
        Q("Food, Feasts & Offerings", "Pastor", f"When is {feast} observed in the Jewish calendar?",
          shuf(timing, all_times[:3]), timing)

# --- Template: Dreams & Visions ---
for dreamer, content, ref, diff in DREAMS_DATA:
    all_contents = [c for d,c,r,df in DREAMS_DATA if c != content]
    random.shuffle(all_contents)
    Q("Dreams & Visions", diff, f"What did {dreamer} see in their dream/vision?",
      shuf(content, all_contents[:3]), content, ref)
    # Who had this dream?
    all_dreamers = list(set([d for d,c,r,df in DREAMS_DATA]))
    wrongs = [d for d in all_dreamers if d != dreamer]
    random.shuffle(wrongs)
    if len(wrongs) >= 3:
        Q("Dreams & Visions", diff, f"Who had the dream/vision of: {content.lower()}?",
          shuf(dreamer, wrongs[:3]), dreamer, ref)

# --- Template: Prophets ---
for prophet, (location, desc, ptype, diff) in PROPHETS_INFO.items():
    # What did this prophet prophesy about?
    all_descs = [d for p,(l,d,t,df) in PROPHETS_INFO.items() if p != prophet]
    random.shuffle(all_descs)
    Q("Prophets", diff, f"What was the prophet {prophet} primarily known for?",
      shuf(desc, all_descs[:3]), desc)
    # Where did they prophesy?
    all_locs = list(set([l for p,(l,d,t,df) in PROPHETS_INFO.items()]))
    wrongs = [l for l in all_locs if l != location]
    random.shuffle(wrongs)
    if len(wrongs) >= 3:
        diff2 = "Deacon" if diff == "Layperson" else "Pastor"
        Q("Prophets", diff2, f"Where did the prophet {prophet} primarily minister?",
          shuf(location, wrongs[:3]), location)
    # Major or minor?
    all_types = ["Major","Minor","Non-writing"]
    wrongs_t = [t for t in all_types if t != ptype]
    Q("Prophets", diff, f"Is {prophet} classified as a Major, Minor, or Non-writing prophet?",
      shuf(ptype, wrongs_t + ["Apocalyptic"][:1]), ptype)

# --- Template: Numbers ---
for question, correct, w1, w2, w3, diff in NUMBERS_FACTS:
    Q("Numbers & Genealogies", diff, question, shuf(correct, [w1,w2,w3]), correct)

print(f"  Template-generated questions: {len(ALL)}")

# ============================================================================
# HANDWRITTEN QUESTIONS — Core quality questions per category
# ============================================================================
# (Adding the rich handwritten ones from earlier data + more)

# GENESIS
c = "Genesis & Creation"
hw = [
    ("Layperson","What did God create on the first day?",["Light","Water","Land","Animals"],"Light"),
    ("Layperson","What was the name of the first man?",["Adam","Noah","Abraham","Moses"],"Adam"),
    ("Layperson","What was the name of the first woman?",["Eve","Sarah","Mary","Ruth"],"Eve"),
    ("Layperson","In which garden did Adam and Eve live?",["Eden","Gethsemane","Babylon","Canaan"],"Eden"),
    ("Layperson","Who built the ark?",["Noah","Abraham","Moses","Adam"],"Noah"),
    ("Layperson","What sign did God place in the sky after the flood?",["A rainbow","A star","A cloud","Fire"],"A rainbow"),
    ("Layperson","Who sold his birthright for stew?",["Esau","Jacob","Reuben","Joseph"],"Esau"),
    ("Layperson","Who was sold into slavery by his brothers?",["Joseph","Benjamin","Judah","Dan"],"Joseph"),
    ("Deacon","What did Rachel steal from Laban?",["Household idols","Silver","Sheep","Scrolls"],"Household idols"),
    ("Deacon","Where did Jacob wrestle with God?",["Peniel","Bethel","Hebron","Shechem"],"Peniel"),
    ("Deacon","What was Nimrod known as?",["A mighty hunter","A wise king","A priest","A builder"],"A mighty hunter"),
    ("Deacon","Which brother offered to stay in Benjamin's place?",["Judah","Reuben","Levi","Simeon"],"Judah"),
    ("Pastor","What wood was Noah's ark made from?",["Gopher wood","Cedar","Oak","Acacia"],"Gopher wood"),
    ("Pastor","How many men did Abraham take to rescue Lot?",["318","300","500","200"],"318"),
    ("Pastor","Who was Tubal-Cain?",["A forger of bronze and iron","Builder of Babel","A warrior","A herdsman"],"A forger of bronze and iron"),
    ("Pastor","What does 'El Shaddai' mean?",["God Almighty","God Most High","God Everlasting","God Who Sees"],"God Almighty"),
]
for item in hw:
    if len(item)==5: d,question,opts,cor,exp = item; Q(c,d,question,opts,cor,exp)
    else: d,question,opts,cor = item; Q(c,d,question,opts,cor)

# MOSES & EXODUS
c = "Moses & the Exodus"
hw = [
    ("Layperson","Who led the Israelites out of Egypt?",["Moses","Joshua","Abraham","Aaron"],"Moses"),
    ("Layperson","What body of water did Moses part?",["The Red Sea","The Jordan","The Nile","The Dead Sea"],"The Red Sea"),
    ("Layperson","What was the last plague of Egypt?",["Death of the firstborn","Darkness","Locusts","Boils"],"Death of the firstborn"),
    ("Layperson","What did the Israelites worship while Moses was on the mountain?",["A golden calf","A bronze serpent","A stone idol","A wooden statue"],"A golden calf"),
    ("Layperson","What food did God provide in the wilderness?",["Manna","Bread","Figs","Wheat"],"Manna"),
    ("Layperson","What holiday commemorates the Exodus?",["Passover","Yom Kippur","Sukkot","Hanukkah"],"Passover"),
    ("Layperson","What did God tell Moses His name was?",["I AM WHO I AM","The Almighty","Jehovah","El Shaddai"],"I AM WHO I AM"),
    ("Deacon","What tribe was Moses from?",["Levi","Judah","Benjamin","Ephraim"],"Levi"),
    ("Deacon","Why couldn't Moses enter the Promised Land?",["He struck the rock instead of speaking to it","He worshiped the calf","He doubted","He killed an Egyptian"],"He struck the rock instead of speaking to it"),
    ("Deacon","How many spies were sent to Canaan?",["12","10","7","2"],"12"),
    ("Deacon","What happened to Korah?",["The earth swallowed him","Struck by lightning","Exiled","Plague killed him"],"The earth swallowed him"),
    ("Deacon","Who held up Moses' arms against Amalek?",["Aaron and Hur","Joshua and Caleb","Miriam and Aaron","Eleazar and Phinehas"],"Aaron and Hur"),
    ("Pastor","How old was Moses when he confronted Pharaoh?",["80","40","60","100"],"80"),
    ("Pastor","What were Moses' two sons named?",["Gershom and Eliezer","Nadab and Abihu","Manasseh and Ephraim","Phinehas and Ithamar"],"Gershom and Eliezer"),
    ("Pastor","Who was the chief craftsman of the Tabernacle?",["Bezalel","Oholiab","Hiram","Huram"],"Bezalel"),
    ("Pastor","What were the Urim and Thummim?",["Sacred lots for divine decisions","Precious stones","Names of tablets","Musical instruments"],"Sacred lots for divine decisions"),
]
for item in hw:
    if len(item)==5: d,question,opts,cor,exp = item; Q(c,d,question,opts,cor,exp)
    else: d,question,opts,cor = item; Q(c,d,question,opts,cor)

# KINGS & KINGDOMS
c = "Kings & Kingdoms"
hw = [
    ("Layperson","Who was the first king of Israel?",["Saul","David","Solomon","Samuel"],"Saul"),
    ("Layperson","Who killed Goliath?",["David","Saul","Jonathan","Joshua"],"David"),
    ("Layperson","What weapon did David use against Goliath?",["A sling and stone","A sword","A spear","A bow"],"A sling and stone"),
    ("Layperson","Who was the wisest king?",["Solomon","David","Hezekiah","Josiah"],"Solomon"),
    ("Layperson","What did Solomon build in Jerusalem?",["The Temple","The Ark","The walls","A palace only"],"The Temple"),
    ("Layperson","What instrument did David play?",["The harp/lyre","The trumpet","The drum","The flute"],"The harp/lyre"),
    ("Layperson","What woman did David sin with?",["Bathsheba","Abigail","Michal","Jezebel"],"Bathsheba"),
    ("Layperson","What evil queen promoted Baal worship?",["Jezebel","Athaliah","Delilah","Herodias"],"Jezebel"),
    ("Layperson","Into how many kingdoms did Israel split after Solomon?",["Two","Three","Four","It didn't split"],"Two"),
    ("Layperson","Which empire destroyed the Temple and conquered Judah?",["Babylon","Assyria","Persia","Rome"],"Babylon"),
    ("Deacon","How did Elijah leave the earth?",["Taken up in a chariot of fire","Died on Carmel","Disappeared","Buried by God"],"Taken up in a chariot of fire"),
    ("Deacon","Who was Rehoboam?",["Solomon's son who split the kingdom","David's grandson","A judge","A northern king"],"Solomon's son who split the kingdom"),
    ("Deacon","Who was the prophet who confronted David?",["Nathan","Samuel","Gad","Elijah"],"Nathan"),
    ("Deacon","What king saw 185,000 Assyrians destroyed?",["Hezekiah","Josiah","Asa","Jehoshaphat"],"Hezekiah"),
    ("Pastor","How long did David reign in Hebron?",["7 years","3 years","10 years","2 years"],"7 years"),
    ("Pastor","What was Solomon's other name?",["Jedidiah","Lemuel","Agur","Ethan"],"Jedidiah"),
    ("Pastor","How many years to build the Temple?",["7","10","20","3"],"7"),
    ("Pastor","How many good kings ruled the northern kingdom?",["None","Two","Five","One"],"None"),
    ("Pastor","When did Assyria conquer the northern kingdom?",["722 BC","586 BC","605 BC","400 BC"],"722 BC"),
    ("Pastor","When was Jerusalem destroyed by Babylon?",["586 BC","722 BC","605 BC","538 BC"],"586 BC"),
]
for item in hw:
    if len(item)==5: d,question,opts,cor,exp = item; Q(c,d,question,opts,cor,exp)
    else: d,question,opts,cor = item; Q(c,d,question,opts,cor)

# LIFE OF JESUS
c = "Life of Jesus"
hw = [
    ("Layperson","Where was Jesus born?",["Bethlehem","Nazareth","Jerusalem","Capernaum"],"Bethlehem"),
    ("Layperson","Who was Jesus' earthly mother?",["Mary","Martha","Elizabeth","Anna"],"Mary"),
    ("Layperson","Who baptized Jesus?",["John the Baptist","Peter","Paul","Andrew"],"John the Baptist"),
    ("Layperson","How many days did Jesus fast in the wilderness?",["40","30","7","21"],"40"),
    ("Layperson","What was Jesus' first miracle?",["Turning water into wine","Healing a blind man","Walking on water","Feeding 5,000"],"Turning water into wine"),
    ("Layperson","In which river was Jesus baptized?",["The Jordan","The Nile","The Euphrates","The Red Sea"],"The Jordan"),
    ("Layperson","What did Jesus ride into Jerusalem on?",["A donkey","A horse","A chariot","A camel"],"A donkey"),
    ("Layperson","Who betrayed Jesus?",["Judas Iscariot","Peter","Thomas","Matthew"],"Judas Iscariot"),
    ("Layperson","For how many silver coins was Jesus betrayed?",["30","20","40","50"],"30"),
    ("Layperson","Where was Jesus crucified?",["Golgotha","Gethsemane","Bethany","Mount Zion"],"Golgotha"),
    ("Layperson","How many days was Jesus in the tomb?",["3","2","1","7"],"3"),
    ("Layperson","Who visited Jesus' tomb first on Easter morning?",["Mary Magdalene","Peter","John","The other Mary"],"Mary Magdalene"),
    ("Layperson","What did Jesus say on the cross: 'Father, forgive them...'?",["'...for they know not what they do'","'...for they have sinned'","'...for they are lost'","'...for they are ignorant'"],"'...for they know not what they do'"),
    ("Deacon","Where did Jesus grow up?",["Nazareth","Bethlehem","Jerusalem","Capernaum"],"Nazareth"),
    ("Deacon","Who were the Magi?",["Wise men from the East who brought gifts to baby Jesus","Roman soldiers","Jewish priests","Shepherds from Bethlehem"],"Wise men from the East who brought gifts to baby Jesus"),
    ("Deacon","What three gifts did the Magi bring?",["Gold, frankincense, and myrrh","Gold, silver, and bronze","Bread, wine, and oil","Incense, spices, and silk"],"Gold, frankincense, and myrrh"),
    ("Deacon","What happened at Jesus' transfiguration?",["His face shone, Moses and Elijah appeared","He walked on water","He fed thousands","He healed the blind"],"His face shone, Moses and Elijah appeared"),
    ("Deacon","Who were the three apostles at the Transfiguration?",["Peter, James, and John","Peter, Andrew, and James","Matthew, Mark, and Luke","John, Thomas, and Philip"],"Peter, James, and John"),
    ("Deacon","What is the Sermon on the Mount?",["Jesus' major teaching in Matthew 5-7","A sermon by Peter","Paul's letter to Rome","Jesus' farewell discourse"],"Jesus' major teaching in Matthew 5-7"),
    ("Deacon","What did Jesus do in the Temple that angered the leaders?",["Overturned the money changers' tables","Healed on the Sabbath","Claimed to be God","Ate with sinners"],"Overturned the money changers' tables"),
    ("Deacon","Who helped carry Jesus' cross?",["Simon of Cyrene","Peter","John","Barabbas"],"Simon of Cyrene"),
    ("Deacon","What did Jesus say to the thief on the cross?",["'Today you will be with me in paradise'","'Father, forgive him'","'Go and sin no more'","'Your faith has saved you'"],"'Today you will be with me in paradise'"),
    ("Pastor","What did Jesus say at age 12 in the Temple?",["'I must be about my Father's business'","'I am the Son of God'","'Destroy this temple and I will rebuild it'","'The Spirit is upon me'"],"'I must be about my Father's business'"),
    ("Pastor","How many days between Jesus' resurrection and ascension?",["40","3","7","50"],"40"),
    ("Pastor","What mountain did Jesus ascend from?",["Mount of Olives","Mount Sinai","Mount Tabor","Mount Zion"],"Mount of Olives"),
    ("Pastor","What are the 'I AM' statements in John?",["Seven declarations like 'I am the bread of life'","Three parables","The beatitudes","Prophecies of His return"],"Seven declarations like 'I am the bread of life'"),
    ("Pastor","Who was Barabbas?",["A criminal released instead of Jesus","A Pharisee","A Roman soldier","A disciple"],"A criminal released instead of Jesus"),
    ("Pastor","What was the Sanhedrin?",["The Jewish ruling council that tried Jesus","A Roman court","A Pharisee school","A synagogue"],"The Jewish ruling council that tried Jesus"),
]
for item in hw:
    if len(item)==5: d,question,opts,cor,exp = item; Q(c,d,question,opts,cor,exp)
    else: d,question,opts,cor = item; Q(c,d,question,opts,cor)

# THE APOSTLES
c = "The Apostles"
hw = [
    ("Layperson","How many apostles did Jesus choose?",["12","7","10","14"],"12"),
    ("Layperson","Which apostle denied Jesus three times?",["Peter","Thomas","Judas","John"],"Peter"),
    ("Layperson","Which apostle doubted the resurrection?",["Thomas","Peter","James","Andrew"],"Thomas"),
    ("Layperson","Which apostle was a tax collector?",["Matthew","Peter","John","James"],"Matthew"),
    ("Layperson","Which two apostles were brothers and fishermen?",["Peter and Andrew","James and John","Philip and Bartholomew","Matthew and Thomas"],"Peter and Andrew"),
    ("Layperson","Who replaced Judas as an apostle?",["Matthias","Paul","Barnabas","Stephen"],"Matthias"),
    ("Layperson","Where were believers first called Christians?",["Antioch","Jerusalem","Rome","Corinth"],"Antioch"),
    ("Layperson","Who was the first Christian martyr?",["Stephen","James","Peter","Paul"],"Stephen"),
    ("Deacon","What did Peter see in his vision at Joppa?",["A sheet of unclean animals","A ladder to heaven","A burning bush","A scroll"],"A sheet of unclean animals"),
    ("Deacon","Who was the first Gentile convert?",["Cornelius","The Ethiopian eunuch","Lydia","The Philippian jailer"],"Cornelius"),
    ("Deacon","What happened to Peter and John at the Beautiful Gate?",["They healed a lame man","They were arrested","They saw a vision","They were beaten"],"They healed a lame man"),
    ("Deacon","Who was Barnabas?",["An encourager who traveled with Paul","One of the twelve","A Pharisee","A Roman convert"],"An encourager who traveled with Paul"),
    ("Deacon","What happened to James (son of Zebedee)?",["Killed by Herod with a sword","Died of old age","Martyred in India","Crucified upside down"],"Killed by Herod with a sword"),
    ("Deacon","Who was the beloved disciple?",["John","Peter","James","Andrew"],"John"),
    ("Pastor","What were Peter's two original names?",["Simon and Cephas","Saul and Simon","Andrew and Simon","Levi and Simon"],"Simon and Cephas"),
    ("Pastor","Where did Peter preach at Pentecost?",["Jerusalem","Antioch","Rome","Caesarea"],"Jerusalem"),
    ("Pastor","How many were added to the church on Pentecost?",["About 3,000","About 5,000","About 500","About 120"],"About 3,000"),
    ("Pastor","Who was Ananias (in Acts 5)?",["A man who lied about the price of land and died","Paul's healer","A high priest","A deacon"],"A man who lied about the price of land and died"),
]
for item in hw:
    if len(item)==5: d,question,opts,cor,exp = item; Q(c,d,question,opts,cor,exp)
    else: d,question,opts,cor = item; Q(c,d,question,opts,cor)

# PAUL & HIS LETTERS
c = "Paul & His Letters"
hw = [
    ("Layperson","What was Paul's name before his conversion?",["Saul","Simon","Stephen","Silas"],"Saul"),
    ("Layperson","On what road was Paul converted?",["The road to Damascus","The road to Jerusalem","The road to Rome","The road to Antioch"],"The road to Damascus"),
    ("Layperson","Who was Paul's most frequent travel companion?",["Barnabas (early), then Silas and Timothy","Peter","John","Luke only"],"Barnabas (early), then Silas and Timothy"),
    ("Layperson","How many missionary journeys did Paul take?",["3 (plus the journey to Rome)","2","5","1"],"3 (plus the journey to Rome)"),
    ("Deacon","What trade did Paul practice?",["Tentmaking","Fishing","Carpentry","Farming"],"Tentmaking"),
    ("Deacon","In which city was Paul shipwrecked on the way to Rome?",["Malta","Crete","Cyprus","Rhodes"],"Malta"),
    ("Deacon","Who wrote most of the New Testament letters?",["Paul","Peter","John","James"],"Paul"),
    ("Deacon","What did Paul say is the greatest virtue in 1 Corinthians 13?",["Love","Faith","Hope","Patience"],"Love"),
    ("Deacon","What city was Paul from?",["Tarsus","Damascus","Jerusalem","Antioch"],"Tarsus"),
    ("Deacon","Was Paul a Roman citizen?",["Yes","No","Only after conversion","Only in Judea"],"Yes"),
    ("Deacon","Who was Timothy to Paul?",["His spiritual son and co-worker","His biological son","His brother","His teacher"],"His spiritual son and co-worker"),
    ("Pastor","Who was Onesimus?",["A runaway slave Paul sent back to Philemon","A church leader","A fellow prisoner","A Roman guard"],"A runaway slave Paul sent back to Philemon"),
    ("Pastor","Where was Paul imprisoned when he wrote Philippians?",["Rome (traditional)","Jerusalem","Caesarea","Ephesus"],"Rome (traditional)"),
    ("Pastor","What does Paul call the 'armor of God'?",["Belt of truth, breastplate of righteousness, shield of faith, etc.","Sword and shield","A robe and crown","Helmet and sandals only"],"Belt of truth, breastplate of righteousness, shield of faith, etc."),
    ("Pastor","What thorn in the flesh did Paul mention?",["An unspecified affliction God didn't remove","Blindness","A broken leg","Persecution from Rome"],"An unspecified affliction God didn't remove"),
    ("Pastor","How many letters did Paul write (in the NT canon)?",["13","7","21","9"],"13"),
]
for item in hw:
    if len(item)==5: d,question,opts,cor,exp = item; Q(c,d,question,opts,cor,exp)
    else: d,question,opts,cor = item; Q(c,d,question,opts,cor)

# REVELATION & END TIMES
c = "Revelation & End Times"
hw = [
    ("Layperson","Who wrote the book of Revelation?",["John","Paul","Peter","James"],"John"),
    ("Layperson","Where was John when he wrote Revelation?",["The island of Patmos","Jerusalem","Rome","Ephesus"],"The island of Patmos"),
    ("Layperson","How many churches does Revelation address?",["7","12","5","3"],"7"),
    ("Layperson","What is the number of the Beast in Revelation?",["666","777","999","616"],"666"),
    ("Layperson","What is the final battle called in Revelation?",["Armageddon","Gethsemane","Megiddo","Babel"],"Armageddon"),
    ("Deacon","What are the Four Horsemen of the Apocalypse?",["Conquest, War, Famine, Death","Plague, War, Famine, Fire","Faith, Hope, Love, Truth","Judgment, Mercy, Wrath, Grace"],"Conquest, War, Famine, Death"),
    ("Deacon","What is the New Jerusalem?",["The heavenly city that descends from God","A rebuilt Temple","A new church","A political kingdom"],"The heavenly city that descends from God"),
    ("Deacon","How many seals does the Lamb open?",["7","12","4","10"],"7"),
    ("Deacon","What does the angel say after opening the seventh seal?",["There was silence in heaven for half an hour","A great earthquake shook the earth","Thunder and lightning","A new song was sung"],"There was silence in heaven for half an hour"),
    ("Deacon","Who are the two witnesses in Revelation 11?",["Two prophets (possibly Moses and Elijah)","Peter and Paul","Michael and Gabriel","Jesus and the Spirit"],"Two prophets (possibly Moses and Elijah)"),
    ("Pastor","What does 'Armageddon' mean?",["Mount Megiddo — a battlefield in Israel","Final war","Lake of fire","Dragon's lair"],"Mount Megiddo — a battlefield in Israel"),
    ("Pastor","What is cast into the lake of fire in Revelation 20?",["Death, Hades, the devil, the beast, and the false prophet","Only Satan","Only the beast","All humans"],"Death, Hades, the devil, the beast, and the false prophet"),
    ("Pastor","What are the 7 churches of Revelation?",["Ephesus, Smyrna, Pergamum, Thyatira, Sardis, Philadelphia, Laodicea","Jerusalem, Rome, Corinth, Galatia, Ephesus, Philippi, Colossae","Antioch, Damascus, Alexandria, Athens, Thessalonica, Crete, Malta"],"Ephesus, Smyrna, Pergamum, Thyatira, Sardis, Philadelphia, Laodicea"),
    ("Pastor","What is the mark of the Beast?",["A mark on the forehead or right hand needed to buy/sell","A seal on the heart","A tattoo of 666","A brand on the arm"],"A mark on the forehead or right hand needed to buy/sell"),
    ("Pastor","What is the 'Great White Throne' judgment?",["The final judgment of all the dead before God","An earthly court","A heavenly celebration","A coronation"],"The final judgment of all the dead before God"),
]
for item in hw:
    if len(item)==5: d,question,opts,cor,exp = item; Q(c,d,question,opts,cor,exp)
    else: d,question,opts,cor = item; Q(c,d,question,opts,cor)

# ANGELS & DEMONS
c = "Angels & Demons"
hw = [
    ("Layperson","Which angel told Mary she would bear Jesus?",["Gabriel","Michael","Raphael","Uriel"],"Gabriel"),
    ("Layperson","Which archangel is named in the Bible?",["Michael","Gabriel","Raphael","Uriel"],"Michael","Gabriel is called an angel but not specifically 'archangel' in most translations."),
    ("Layperson","Who was the angel that tempted Eve?",["Satan (the serpent)","Gabriel","A fallen angel","Beelzebub"],"Satan (the serpent)"),
    ("Layperson","What did angels announce to the shepherds?",["The birth of Jesus","The fall of Rome","The coming of Moses","A new king of Israel"],"The birth of Jesus"),
    ("Layperson","Who wrestled with Jacob at Peniel?",["An angel (or God)","A man from Esau's camp","A demon","A stranger"],"An angel (or God)"),
    ("Deacon","What are seraphim?",["Angels with six wings who worship God","Fallen angels","Guardian angels","Warrior angels"],"Angels with six wings who worship God"),
    ("Deacon","What are cherubim?",["Angelic beings who guard God's presence","Baby angels with wings","Harps of heaven","A type of worship song"],"Angelic beings who guard God's presence"),
    ("Deacon","What did the angel do to Peter in prison?",["Led him out through locked gates","Struck the guards dead","Made him invisible","Gave him a sword"],"Led him out through locked gates"),
    ("Deacon","Who is Beelzebub?",["A name for Satan, meaning 'lord of the flies'","A Philistine god only","An archangel","A human king"],"A name for Satan, meaning 'lord of the flies'"),
    ("Deacon","What did Satan do in the book of Job?",["Afflicted Job with God's permission to test his faith","Killed Job","Destroyed the Temple","Tempted Eve"],"Afflicted Job with God's permission to test his faith"),
    ("Pastor","How many angels fell with Satan according to Revelation 12?",["A third of the stars/angels","Half","A quarter","All but seven"],"A third of the stars/angels"),
    ("Pastor","What does 'Lucifer' mean?",["Morning star / light bearer","Dark prince","Fallen one","Serpent"],"Morning star / light bearer"),
    ("Pastor","Who is the angel of the abyss named in Revelation 9?",["Abaddon / Apollyon","Gabriel","Michael","Azrael"],"Abaddon / Apollyon"),
    ("Pastor","What did Michael the archangel dispute with Satan about?",["The body of Moses","The soul of Job","The throne of heaven","The Ark of the Covenant"],"The body of Moses"),
    ("Pastor","What is a legion of demons?",["The name given by demons Jesus cast out of a man — implying thousands","A Roman military unit only","A single powerful demon","A curse"],"The name given by demons Jesus cast out of a man — implying thousands"),
]
for item in hw:
    if len(item)==5: d,question,opts,cor,exp = item; Q(c,d,question,opts,cor,exp)
    else: d,question,opts,cor = item; Q(c,d,question,opts,cor)

# LAWS & COMMANDMENTS
c = "Laws & Commandments"
hw = [
    ("Layperson","What is the first commandment?",["You shall have no other gods before me","Do not murder","Do not steal","Honor your father and mother"],"You shall have no other gods before me"),
    ("Layperson","What is the command about the Sabbath?",["Remember the Sabbath day, to keep it holy","Go to the Temple","Pray three times a day","Fast every week"],"Remember the Sabbath day, to keep it holy"),
    ("Layperson","Which commandment says 'Do not murder'?",["The sixth","The fifth","The seventh","The eighth"],"The sixth"),
    ("Layperson","Which commandment says 'Do not steal'?",["The eighth","The sixth","The ninth","The seventh"],"The eighth"),
    ("Layperson","What did Jesus say was the greatest commandment?",["Love the Lord your God with all your heart, soul, and mind","Do not murder","Keep the Sabbath","Honor your parents"],"Love the Lord your God with all your heart, soul, and mind"),
    ("Layperson","What was the second greatest commandment?",["Love your neighbor as yourself","Do not bear false witness","Do not covet","Remember the Sabbath"],"Love your neighbor as yourself"),
    ("Deacon","What is the Shema?",["'Hear O Israel, the LORD our God, the LORD is one'","The Ten Commandments","A prayer for forgiveness","A blessing before meals"],"'Hear O Israel, the LORD our God, the LORD is one'"),
    ("Deacon","How many laws are traditionally counted in the Torah?",["613","10","365","100"],"613"),
    ("Deacon","What did Jesus say about the Law?",["He came not to abolish but to fulfill it","He came to replace it","He came to ignore it","He came to simplify it"],"He came not to abolish but to fulfill it"),
    ("Deacon","What were the Pharisees known for?",["Strict interpretation and observance of the Law","Rejecting the resurrection","Collaborating with Rome","Being priests"],"Strict interpretation and observance of the Law"),
    ("Deacon","What is the Year of Jubilee?",["Every 50th year: debts forgiven, slaves freed, land returned","A weekly festival","A monthly celebration","A 7-year cycle"],"Every 50th year: debts forgiven, slaves freed, land returned"),
    ("Pastor","What animals are considered 'clean' to eat?",["Those that chew cud AND have split hooves","All four-legged animals","Only birds","Only fish"],"Those that chew cud AND have split hooves"),
    ("Pastor","What is the cities of refuge law?",["Someone who accidentally killed could flee to designated cities for safety","Prisons for criminals","Temples for worship","Military bases"],"Someone who accidentally killed could flee to designated cities for safety"),
    ("Pastor","How many cities of refuge were there?",["6","3","12","7"],"6"),
    ("Pastor","What did the Sabbath year require?",["The land was to rest — no farming every 7th year","Everyone fasted","All debts were doubled","A new king was crowned"],"The land was to rest — no farming every 7th year"),
]
for item in hw:
    if len(item)==5: d,question,opts,cor,exp = item; Q(c,d,question,opts,cor,exp)
    else: d,question,opts,cor = item; Q(c,d,question,opts,cor)

# PROPHECY & FULFILLMENT
c = "Prophecy & Fulfillment"
hw = [
    ("Layperson","Which prophet foretold Jesus would be born in Bethlehem?",["Micah","Isaiah","Jeremiah","Malachi"],"Micah"),
    ("Layperson","Which prophet wrote about a virgin conceiving a son?",["Isaiah","Jeremiah","Ezekiel","Daniel"],"Isaiah"),
    ("Layperson","Who prophesied a voice crying in the wilderness?",["Isaiah","Micah","Joel","Amos"],"Isaiah"),
    ("Layperson","What prophet predicted the Messiah would ride a donkey?",["Zechariah","Isaiah","Malachi","Hosea"],"Zechariah"),
    ("Deacon","Which prophet foretold the Messiah would be betrayed for 30 silver coins?",["Zechariah","Isaiah","Jeremiah","Malachi"],"Zechariah"),
    ("Deacon","Isaiah 53 describes the Messiah as what?",["A suffering servant","A conquering king","A priest","A prophet"],"A suffering servant"),
    ("Deacon","Which psalm prophesied 'They pierced my hands and feet'?",["Psalm 22","Psalm 23","Psalm 110","Psalm 69"],"Psalm 22"),
    ("Deacon","Which prophet foretold the new covenant written on hearts?",["Jeremiah","Isaiah","Ezekiel","Malachi"],"Jeremiah"),
    ("Deacon","What did Malachi prophesy about Elijah?",["God would send Elijah before the great day of the LORD","Elijah would return as king","Elijah would rebuild the Temple","Elijah would write new laws"],"God would send Elijah before the great day of the LORD"),
    ("Pastor","How many Messianic prophecies are traditionally counted?",["Over 300","About 50","About 100","About 12"],"Over 300"),
    ("Pastor","What prophet said 'Out of Egypt I called my son'?",["Hosea","Isaiah","Jeremiah","Micah"],"Hosea"),
    ("Pastor","Which psalm says 'The LORD said to my Lord: Sit at my right hand'?",["Psalm 110","Psalm 22","Psalm 2","Psalm 45"],"Psalm 110"),
    ("Pastor","Isaiah 7:14 names the child what?",["Immanuel","Wonderful Counselor","Prince of Peace","Mighty God"],"Immanuel"),
    ("Pastor","Daniel's 70 weeks prophecy is about what?",["The timeline to the Messiah's coming","The length of exile","The rebuilding of the Temple","The end of the world"],"The timeline to the Messiah's coming"),
]
for item in hw:
    if len(item)==5: d,question,opts,cor,exp = item; Q(c,d,question,opts,cor,exp)
    else: d,question,opts,cor = item; Q(c,d,question,opts,cor)

# FOOD, FEASTS & OFFERINGS
c = "Food, Feasts & Offerings"
hw = [
    ("Layperson","What did God provide as food in the wilderness?",["Manna and quail","Bread and fish","Figs and dates","Milk and honey"],"Manna and quail"),
    ("Layperson","What did Jesus multiply to feed 5,000?",["Five loaves and two fish","Seven loaves","Bread and wine","Manna"],"Five loaves and two fish"),
    ("Layperson","What did Jesus share at the Last Supper?",["Bread and wine","A lamb","Fish and bread","Manna"],"Bread and wine"),
    ("Layperson","What food did Esau sell his birthright for?",["A bowl of red stew/lentils","Bread","A roasted lamb","Figs"],"A bowl of red stew/lentils"),
    ("Layperson","What was the Passover lamb?",["A lamb sacrificed and eaten to remember the Exodus","A golden idol","A symbol on the Temple","A type of bread"],"A lamb sacrificed and eaten to remember the Exodus"),
    ("Deacon","What is unleavened bread?",["Bread without yeast — eaten during Passover","Bread with extra yeast","Burnt bread","Bread made with honey"],"Bread without yeast — eaten during Passover"),
    ("Deacon","What did Elijah eat before his 40-day journey to Horeb?",["Cake and water provided by an angel","Manna","Bread and fish","Figs"],"Cake and water provided by an angel"),
    ("Deacon","What is a burnt offering?",["An animal completely consumed by fire as worship to God","A grain offering","A peace offering","A sin offering"],"An animal completely consumed by fire as worship to God"),
    ("Deacon","What is a tithe?",["Giving one-tenth of income/produce to God","Giving everything","A weekly feast","An annual sacrifice"],"Giving one-tenth of income/produce to God"),
    ("Deacon","What did the widow of Zarephath share with Elijah?",["Her last bit of flour and oil","A lamb","Fish","Water only"],"Her last bit of flour and oil"),
    ("Pastor","What five types of offerings are described in Leviticus?",["Burnt, grain, peace, sin, and guilt","Burnt, bread, wine, incense, and firstfruits","Animal, grain, drink, incense, and wave","Morning, evening, Sabbath, new moon, and annual"],"Burnt, grain, peace, sin, and guilt"),
    ("Pastor","What grain was NOT used for offerings?",["Honey and leaven were forbidden","Wheat was forbidden","Barley was forbidden","All grains were acceptable"],"Honey and leaven were forbidden"),
    ("Pastor","What is the 'showbread' (bread of the Presence)?",["12 loaves placed in the Tabernacle each Sabbath","Bread for the poor","Communion bread","Passover bread"],"12 loaves placed in the Tabernacle each Sabbath"),
    ("Pastor","What did Daniel and his friends eat instead of the king's food?",["Vegetables and water","Bread and wine","Fruit only","Nothing — they fasted"],"Vegetables and water"),
]
for item in hw:
    if len(item)==5: d,question,opts,cor,exp = item; Q(c,d,question,opts,cor,exp)
    else: d,question,opts,cor = item; Q(c,d,question,opts,cor)

# BATTLES & WARS
c = "Battles & Wars"
hw = [
    ("Layperson","What fell when the Israelites marched around Jericho?",["The walls","The gate","The tower","The army"],"The walls"),
    ("Layperson","Who defeated Goliath?",["David","Saul","Joshua","Samson"],"David"),
    ("Layperson","What strong man fought the Philistines?",["Samson","David","Joshua","Gideon"],"Samson"),
    ("Layperson","Who brought down the temple on the Philistines?",["Samson","David","Joshua","Elijah"],"Samson"),
    ("Layperson","How many times did Israel march around Jericho on the final day?",["7","1","3","13"],"7"),
    ("Deacon","Who defeated the Midianites with 300 men?",["Gideon","David","Joshua","Samson"],"Gideon"),
    ("Deacon","What weapons did Gideon's men use?",["Trumpets, jars, and torches","Swords and shields","Slings and stones","Spears and bows"],"Trumpets, jars, and torches"),
    ("Deacon","Who was the judge who defeated Sisera's army?",["Deborah (with Barak)","Gideon","Samson","Othniel"],"Deborah (with Barak)"),
    ("Deacon","Who killed Sisera?",["Jael — with a tent peg through his temple","Deborah","Barak","Samson"],"Jael — with a tent peg through his temple"),
    ("Deacon","What happened when Joshua commanded the sun to stand still?",["It stood still so Israel could win the battle","Nothing happened","An eclipse occurred","Night fell early"],"It stood still so Israel could win the battle"),
    ("Deacon","Who was the commander of Saul's army?",["Abner","Joab","David","Jonathan"],"Abner"),
    ("Pastor","What trick did the Gibeonites use to make peace with Joshua?",["Pretended to be from far away with stale bread and worn clothes","Sent a peace offering","Surrendered their weapons","Offered their daughters"],"Pretended to be from far away with stale bread and worn clothes"),
    ("Pastor","How did Ehud kill King Eglon?",["Stabbed him with a hidden left-handed sword","Poisoned his food","Shot him with an arrow","Pushed him from a tower"],"Stabbed him with a hidden left-handed sword"),
    ("Pastor","What king of Judah trusted God and saw the Assyrian army destroyed?",["Hezekiah","Josiah","Asa","Jehoshaphat"],"Hezekiah"),
    ("Pastor","How many Assyrian soldiers were killed by the angel of the LORD?",["185,000","100,000","50,000","200,000"],"185,000"),
]
for item in hw:
    if len(item)==5: d,question,opts,cor,exp = item; Q(c,d,question,opts,cor,exp)
    else: d,question,opts,cor = item; Q(c,d,question,opts,cor)

# PSALMS & PROVERBS
c = "Psalms & Proverbs"
hw = [
    ("Layperson","Who wrote most of the Psalms?",["David","Solomon","Moses","Asaph"],"David"),
    ("Layperson","What Psalm begins 'The LORD is my shepherd'?",["Psalm 23","Psalm 1","Psalm 119","Psalm 91"],"Psalm 23"),
    ("Layperson","Who wrote most of Proverbs?",["Solomon","David","Moses","Daniel"],"Solomon"),
    ("Layperson","What does Proverbs say is the beginning of wisdom?",["The fear of the LORD","Education","Experience","Prayer"],"The fear of the LORD"),
    ("Layperson","'The LORD is my shepherd, I shall not...'",["want","fear","fail","die"],"want"),
    ("Deacon","What Psalm is the longest chapter in the Bible?",["Psalm 119","Psalm 150","Psalm 23","Psalm 1"],"Psalm 119"),
    ("Deacon","What is Psalm 119 structured around?",["The Hebrew alphabet — 22 sections of 8 verses each","The Ten Commandments","The twelve tribes","The seven days of creation"],"The Hebrew alphabet — 22 sections of 8 verses each"),
    ("Deacon","What does 'Selah' mean in the Psalms?",["A musical pause or interlude","Amen","Hallelujah","The end"],"A musical pause or interlude"),
    ("Deacon","What is the Proverbs 31 woman known for?",["Being a virtuous, hardworking wife and mother","Being a queen","Being a prophetess","Being a warrior"],"Being a virtuous, hardworking wife and mother"),
    ("Deacon","What does Ecclesiastes say is 'vanity of vanities'?",["Everything under the sun — all is vanity","Only wealth","Only work","Only pleasure"],"Everything under the sun — all is vanity"),
    ("Pastor","Who is Agur in Proverbs 30?",["A sage whose sayings are collected in Proverbs 30","Solomon's pen name","A king","A priest"],"A sage whose sayings are collected in Proverbs 30"),
    ("Pastor","What are the Psalms of Ascent?",["Psalms 120-134, sung going up to Jerusalem","Psalms 1-10","The final five Psalms","David's war psalms"],"Psalms 120-134, sung going up to Jerusalem"),
    ("Pastor","Who wrote Psalm 90?",["Moses","David","Solomon","Asaph"],"Moses"),
    ("Pastor","What is an imprecatory psalm?",["A psalm calling for God's judgment on enemies","A praise psalm","A thanksgiving psalm","A wisdom psalm"],"A psalm calling for God's judgment on enemies"),
]
for item in hw:
    if len(item)==5: d,question,opts,cor,exp = item; Q(c,d,question,opts,cor,exp)
    else: d,question,opts,cor = item; Q(c,d,question,opts,cor)

print(f"  Handwritten questions added. Total: {len(ALL)}")

# ============================================================================
# DEDUP + ASSIGN IDS + BALANCE + OUTPUT
# ============================================================================

# Deduplicate by question text
seen = set()
deduped = []
for q in ALL:
    key = q["question"].strip().lower()
    if key not in seen:
        seen.add(key)
        deduped.append(q)
ALL = deduped

# Assign IDs
for i, q in enumerate(ALL):
    q["id"] = hashlib.md5(f"{q['category']}-{q['difficulty']}-{q['question'][:50]}-{i}".encode()).hexdigest()[:12]

# Count per category
from collections import Counter
cat_counts = Counter(q["category"] for q in ALL)
diff_counts = Counter((q["category"], q["difficulty"]) for q in ALL)

print(f"\n{'='*60}")
print(f"TOTAL UNIQUE QUESTIONS: {len(ALL)}")
print(f"{'='*60}")
for cat in sorted(set(q["category"] for q in ALL)):
    l = diff_counts.get((cat,"Layperson"),0)
    d = diff_counts.get((cat,"Deacon"),0)
    p = diff_counts.get((cat,"Pastor"),0)
    print(f"  {cat}: {cat_counts[cat]} (L:{l} D:{d} P:{p})")

# Save
out_path = "/home/claude/manna/manna_questions.json"
with open(out_path, "w") as f:
    json.dump(ALL, f, indent=2)

print(f"\nSaved to {out_path}")
print(f"File size: {os.path.getsize(out_path)/1024:.0f} KB")
