import re, json

USFX = "/home/claude/lumina-bible/data/kjv_strongs/eng-kjv2006_usfx.xml"
BOOKID = {
 "GEN":"Genesis","EXO":"Exodus","LEV":"Leviticus","NUM":"Numbers","DEU":"Deuteronomy",
 "JOS":"Joshua","JDG":"Judges","RUT":"Ruth","1SA":"1 Samuel","2SA":"2 Samuel","1KI":"1 Kings",
 "2KI":"2 Kings","1CH":"1 Chronicles","2CH":"2 Chronicles","EZR":"Ezra","NEH":"Nehemiah",
 "EST":"Esther","JOB":"Job","PSA":"Psalms","PRO":"Proverbs","ECC":"Ecclesiastes","SNG":"Song of Solomon",
 "ISA":"Isaiah","JER":"Jeremiah","LAM":"Lamentations","EZK":"Ezekiel","DAN":"Daniel","HOS":"Hosea",
 "JOL":"Joel","AMO":"Amos","OBA":"Obadiah","JON":"Jonah","MIC":"Micah","NAM":"Nahum","HAB":"Habakkuk",
 "ZEP":"Zephaniah","HAG":"Haggai","ZEC":"Zechariah","MAL":"Malachi","MAT":"Matthew","MRK":"Mark",
 "LUK":"Luke","JHN":"John","ACT":"Acts","ROM":"Romans","1CO":"1 Corinthians","2CO":"2 Corinthians",
 "GAL":"Galatians","EPH":"Ephesians","PHP":"Philippians","COL":"Colossians","1TH":"1 Thessalonians",
 "2TH":"2 Thessalonians","1TI":"1 Timothy","2TI":"2 Timothy","TIT":"Titus","PHM":"Philemon",
 "HEB":"Hebrews","JAS":"James","1PE":"1 Peter","2PE":"2 Peter","1JN":"1 John","2JN":"2 John",
 "3JN":"3 John","JUD":"Jude","REV":"Revelation",
}

def parse_kjv():
    raw = open(USFX, encoding="utf-8").read()
    raw = re.sub(r"<f\b.*?</f>", "", raw, flags=re.S)   # drop footnotes
    verses = {}  # bcv -> text
    # capture each verse marker and the text up to next <v or <ve
    for m in re.finditer(r'<v id="[^"]*" bcv="([^"]+)" />(.*?)(?=<v id=|<ve\s*/>|</p>)', raw, flags=re.S):
        bcv = m.group(1)
        chunk = m.group(2)
        txt = re.sub(r"<[^>]+>", " ", chunk)      # strip tags
        txt = txt.replace("¶", " ")
        txt = re.sub(r"\s+", " ", txt).strip()
        if txt:
            verses[bcv] = txt
    return verses

if __name__ == "__main__":
    v = parse_kjv()
    print("verses parsed:", len(v))
    for ref in ["GEN.1.1","PSA.23.1","PRO.15.1","JHN.3.16","REV.1.1","DAN.2.31","EXO.16.15"]:
        print(f"{ref}: {v.get(ref)}")
