#!/usr/bin/env python3
"""
Manna Volume 2 — PART 2: broaden the thin categories with 1200 more questions.
Sources: public-domain KJV text (complete-the-verse) + curated well-known facts.
Categories targeted: Psalms & Proverbs, Revelation & End Times, Battles & Wars,
Angels & Demons, Dreams & Visions, Food/Feasts & Offerings, Miracles.
Deduped against V1 (manna_questions.json) AND V2 part 1 (manna_questions_v2.json).
Appends to manna_questions_v2.json.
"""
import re, json, hashlib, random
from collections import defaultdict
import sys
sys.path.insert(0, "/home/claude/manna/scripts")
from kjv_parse import parse_kjv, BOOKID

random.seed(98765)
MANNA = "/home/claude/manna"

def clean(t):
    t = re.sub(r"\s+([,.;:!?])", r"\1", t)      # no space before punctuation
    t = re.sub(r"\s+", " ", t).strip()
    return t

def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", s.lower())).strip()

# ---- load KJV verses, keyed by readable ref ----
raw = parse_kjv()
verses = {}     # "Genesis 1:1" -> text ; also keep book + numeric
meta = {}       # ref -> (book, chap, verse)
for bcv, txt in raw.items():
    parts = bcv.split(".")
    if len(parts) != 3:
        continue
    bk = BOOKID.get(parts[0])
    if not bk:
        continue
    ref = f"{bk} {parts[1]}:{parts[2]}"
    verses[ref] = clean(txt)
    meta[ref] = (bk, parts[1], parts[2])
print("KJV verses indexed:", len(verses))

# ---- dedup set from V1 + existing V2 ----
v1 = json.load(open(f"{MANNA}/manna_questions.json"))
v2 = json.load(open(f"{MANNA}/manna_questions_v2.json"))
seen = set(norm(q["question"]) for q in v1) | set(norm(q["question"]) for q in v2)
print(f"dedup base: V1={len(v1)} + V2pt1={len(v2)}")

new = []
def add(category, difficulty, question, options, correct, explanation=""):
    q = question.strip()
    if norm(q) in seen:
        return False
    opts = []
    for o in options:
        o = str(o).strip()
        if o and o not in opts:
            opts.append(o)
    if correct not in opts or len(opts) < 4:
        return False
    opts = opts[:4]
    if correct not in opts:
        opts[-1] = correct
    random.shuffle(opts)
    seen.add(norm(q))
    new.append({"category":category,"difficulty":difficulty,"question":q,
                "options":opts,"correct":correct,"explanation":explanation,
                "id":hashlib.md5((q+correct).encode()).hexdigest()[:12]})
    return True

# ---------------- complete-the-verse engine ----------------
def split_verse(text):
    """Return (stem, answer) splitting at a clause boundary; both halves >=4 words."""
    for sep in [": ", "; "]:
        if sep in text:
            i = text.index(sep)
            a, b = text[:i].strip(), text[i+len(sep):].strip().rstrip(".")
            if 4 <= len(a.split()) and 4 <= len(b.split()) <= 14:
                return a, b
    # fallback: comma near the middle
    if ", " in text:
        idxs = [m.start() for m in re.finditer(", ", text)]
        mid = len(text)//2
        i = min(idxs, key=lambda x: abs(x-mid))
        a, b = text[:i].strip(), text[i+2:].strip().rstrip(".")
        if 4 <= len(a.split()) and 4 <= len(b.split()) <= 14:
            return a, b
    return None

def build_completions(refs, category, diff_weights, cap):
    """refs: list of readable refs in this category. Generates complete-the-verse."""
    pieces = []   # (ref, stem, answer)
    for ref in refs:
        sp = split_verse(verses[ref])
        if sp:
            pieces.append((ref, sp[0], sp[1]))
    answers_pool = [p[2] for p in pieces]
    random.shuffle(pieces)
    diffs = list(diff_weights.keys()); weights = list(diff_weights.values())
    made = 0
    for ref, stem, ans in pieces:
        if made >= cap:
            break
        n = len(ans.split())
        pool = [a for a in answers_pool if a != ans and abs(len(a.split())-n) <= 4]
        random.shuffle(pool)
        distr = []
        for a in pool:
            if a not in distr:
                distr.append(a)
            if len(distr) == 3:
                break
        if len(distr) < 3:
            continue
        bk = meta[ref][0]
        diff = random.choices(diffs, weights=weights, k=1)[0]
        if add(category, diff,
               f"Complete this verse from {bk}: \"{stem} ...\"",
               [ans] + distr, ans, ref):
            made += 1
    return made

# ---------------- category verse pools ----------------
def book_refs(books):
    return [r for r in verses if meta[r][0] in books]

def keyword_refs(books, patterns, minwords=9, maxwords=32):
    rx = re.compile("|".join(patterns), re.I)
    out = []
    for r in verses:
        if meta[r][0] in books:
            wc = len(verses[r].split())
            if minwords <= wc <= maxwords and rx.search(verses[r]):
                out.append(r)
    return out

OT_HIST = {"Joshua","Judges","1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles"}
PENT    = {"Exodus","Leviticus","Numbers","Deuteronomy"}
GOSPELS = {"Matthew","Mark","Luke","John","Acts"}

pools = {
 "Psalms & Proverbs":     (book_refs({"Psalms","Proverbs"}), {"Layperson":4,"Deacon":4,"Pastor":2}, 310),
 "Revelation & End Times":(book_refs({"Revelation"}) + keyword_refs({"Daniel","Matthew","Mark","Luke",
                            "1 Thessalonians","2 Thessalonians","2 Peter"},
                            [r"\bend\b",r"last day",r"come quickly",r"throne",r"beast",r"trumpet",
                             r"new heaven",r"resurrection",r"judg",r"kingdom of"]),
                            {"Deacon":5,"Pastor":5}, 175),
 "Battles & Wars":        (keyword_refs(OT_HIST, [r"\bwar\b",r"battle",r"\bsword",r"\bslew\b",
                            r"smote",r"\barmy\b",r"\bfought\b",r"\bspear",r"chariot",r"\bhost\b",
                            r"prevail",r"\bsiege"]),
                            {"Layperson":2,"Deacon":6,"Pastor":2}, 170),
 "Angels & Demons":       (keyword_refs(set(verses and {meta[r][0] for r in verses}),
                            [r"\bangel",r"archangel",r"\bMichael\b",r"\bGabriel\b",r"\bSatan\b",
                             r"\bdevil",r"unclean spirit",r"\bLucifer\b",r"cherub"]),
                            {"Layperson":2,"Deacon":6,"Pastor":2}, 170),
 "Dreams & Visions":      (keyword_refs(set(verses and {meta[r][0] for r in verses}),
                            [r"\bdream",r"\bvision",r"\binterpret",r"saw in the night"]),
                            {"Layperson":2,"Deacon":6,"Pastor":2}, 160),
 "Food, Feasts & Offerings":(keyword_refs(PENT | {"Joshua","2 Chronicles","Nehemiah"},
                            [r"offering",r"sacrifice",r"\bfeast",r"passover",r"\bmanna\b",
                             r"unleavened",r"firstfruits",r"\btithe",r"\baltar",r"\bbread\b"]),
                            {"Deacon":6,"Pastor":4}, 150),
 "Miracles":              (keyword_refs(GOSPELS, [r"\bheal",r"miracle",r"\bsign",r"\bwonder",
                            r"raised",r"made whole",r"\bleper",r"\bcast out",r"loaves"]),
                            {"Layperson":3,"Deacon":5,"Pastor":2}, 145),
}

for cat,(refs,weights,cap) in pools.items():
    refs = list(dict.fromkeys(refs))  # unique, keep order
    made = build_completions(refs, cat, weights, cap)
    print(f"{cat}: pool={len(refs)} made={made}")

# ---------------- curated well-known anchors ----------------
curated = [
 # Dreams & Visions
 ("Dreams & Visions","Layperson","Who dreamed of a ladder reaching from earth to heaven?",
   ["Jacob","Joseph","Daniel","Samuel"],"Jacob","Genesis 28:12"),
 ("Dreams & Visions","Layperson","Who interpreted Pharaoh's dreams of the fat and lean cows?",
   ["Joseph","Moses","Aaron","Daniel"],"Joseph","Genesis 41"),
 ("Dreams & Visions","Deacon","Who interpreted Nebuchadnezzar's dream of the great image?",
   ["Daniel","Ezekiel","Isaiah","Jeremiah"],"Daniel","Daniel 2"),
 ("Dreams & Visions","Deacon","Which prophet saw a vision of a valley of dry bones?",
   ["Ezekiel","Isaiah","Daniel","Jeremiah"],"Ezekiel","Ezekiel 37"),
 ("Dreams & Visions","Deacon","Who saw a vision of a sheet let down from heaven full of animals?",
   ["Peter","Paul","John","Stephen"],"Peter","Acts 10"),
 ("Dreams & Visions","Deacon","Which prophet saw the Lord 'high and lifted up' in the temple?",
   ["Isaiah","Ezekiel","Amos","Hosea"],"Isaiah","Isaiah 6"),
 ("Dreams & Visions","Layperson","Joseph dreamed that what bowed down to him?",
   ["The sun, moon, and stars","The trees of the field","The rivers of Egypt","The beasts of the earth"],
   "The sun, moon, and stars","Genesis 37:9"),
 # Angels & Demons
 ("Angels & Demons","Layperson","Which angel announced to Mary that she would bear Jesus?",
   ["Gabriel","Michael","Raphael","Uriel"],"Gabriel","Luke 1:26-38"),
 ("Angels & Demons","Deacon","Which archangel is described disputing with the devil over the body of Moses?",
   ["Michael","Gabriel","Raphael","Lucifer"],"Michael","Jude 1:9"),
 ("Angels & Demons","Deacon","What did the demons Jesus cast out in the Gadarene region call themselves?",
   ["Legion","Beelzebub","Apollyon","Belial"],"Legion","Mark 5:9"),
 ("Angels & Demons","Layperson","What was placed at the east of Eden to guard the tree of life?",
   ["Cherubim with a flaming sword","A great wall","A pillar of fire","An angel with a trumpet"],
   "Cherubim with a flaming sword","Genesis 3:24"),
 ("Angels & Demons","Deacon","Which angel announced the birth of John the Baptist to Zacharias?",
   ["Gabriel","Michael","Raphael","An unnamed seraph"],"Gabriel","Luke 1:11-19"),
 # Revelation & End Times
 ("Revelation & End Times","Layperson","How many churches are addressed in the book of Revelation?",
   ["Seven","Three","Twelve","Ten"],"Seven","Revelation 1:11"),
 ("Revelation & End Times","Deacon","How many seals are on the scroll the Lamb opens in Revelation?",
   ["Seven","Four","Twelve","Three"],"Seven","Revelation 5-8"),
 ("Revelation & End Times","Deacon","What is the number of the beast in Revelation?",
   ["666","777","144","888"],"666","Revelation 13:18"),
 ("Revelation & End Times","Deacon","What new city does John see coming down out of heaven?",
   ["New Jerusalem","New Babylon","New Eden","New Zion"],"New Jerusalem","Revelation 21:2"),
 ("Revelation & End Times","Pastor","'I am Alpha and Omega' identifies Christ as what?",
   ["The beginning and the end","The first and last prophet","The light of the world",
    "The lion and the lamb"],"The beginning and the end","Revelation 22:13"),
 # Food, Feasts & Offerings
 ("Food, Feasts & Offerings","Layperson","What food did God rain from heaven to feed Israel in the wilderness?",
   ["Manna","Quail only","Barley loaves","Honey"],"Manna","Exodus 16"),
 ("Food, Feasts & Offerings","Layperson","Which feast commemorates Israel's deliverance from Egypt?",
   ["Passover","Pentecost","Tabernacles","Purim"],"Passover","Exodus 12"),
 ("Food, Feasts & Offerings","Deacon","What was put on the doorposts at the first Passover?",
   ["The blood of a lamb","Olive oil","Ashes","Salt"],"The blood of a lamb","Exodus 12:7"),
 ("Food, Feasts & Offerings","Deacon","During Passover week, what kind of bread were the Israelites to eat?",
   ["Unleavened bread","Barley cakes","Honeyed bread","Wheat loaves"],"Unleavened bread","Exodus 12:15"),
 ("Food, Feasts & Offerings","Pastor","The feast of weeks (firstfruits of wheat harvest) is also known as what?",
   ["Pentecost","Passover","Atonement","Trumpets"],"Pentecost","Leviticus 23:15-16"),
 # Battles & Wars
 ("Battles & Wars","Layperson","Around which city did Israel march until its walls fell down?",
   ["Jericho","Ai","Gibeon","Hebron"],"Jericho","Joshua 6"),
 ("Battles & Wars","Layperson","Who killed the giant Goliath with a sling and a stone?",
   ["David","Saul","Jonathan","Samson"],"David","1 Samuel 17"),
 ("Battles & Wars","Deacon","During whose battle did the sun stand still over Gibeon?",
   ["Joshua","Gideon","Barak","Deborah"],"Joshua","Joshua 10:12-13"),
 ("Battles & Wars","Deacon","With how many men did Gideon defeat the Midianites?",
   ["300","600","3,000","30"],"300","Judges 7"),
 ("Battles & Wars","Deacon","With what did Samson slay a thousand Philistines?",
   ["The jawbone of a donkey","A wooden club","A bronze spear","A sling"],
   "The jawbone of a donkey","Judges 15:15"),
 # Miracles
 ("Miracles","Layperson","What did Jesus turn water into at the wedding in Cana?",
   ["Wine","Oil","Honey","Milk"],"Wine","John 2:1-11"),
 ("Miracles","Layperson","How many loaves did Jesus use to feed the five thousand?",
   ["Five","Two","Seven","Twelve"],"Five","Matthew 14:17-21"),
 ("Miracles","Deacon","Whom did Jesus raise from the dead after four days in the tomb?",
   ["Lazarus","Jairus' daughter","The widow's son","Tabitha"],"Lazarus","John 11"),
 ("Miracles","Deacon","Which disciple walked on the water toward Jesus before he began to sink?",
   ["Peter","John","James","Andrew"],"Peter","Matthew 14:29-30"),
 ("Miracles","Layperson","What did Jesus do to the storm on the Sea of Galilee?",
   ["Calmed it with a word","Sailed around it","Prayed all night","Walked away from it"],
   "Calmed it with a word","Mark 4:39"),
]
cur_made = 0
for cat,diff,q,opts,correct,exp in curated:
    if add(cat,diff,q,opts,correct,exp):
        cur_made += 1
print(f"curated added: {cur_made}")

# ---------------- trim to 1200, balance difficulty ----------------
random.shuffle(new)
TARGET = 1200
by_diff = defaultdict(list)
for q in new: by_diff[q["difficulty"]].append(q)
print("available by difficulty:", {k:len(v) for k,v in by_diff.items()})

final = []
per = TARGET//3
for d in ("Layperson","Deacon","Pastor"):
    final.extend(by_diff[d][:per])
leftovers = [q for q in new if q not in final]
random.shuffle(leftovers)
for q in leftovers:
    if len(final) >= TARGET: break
    final.append(q)
final = final[:TARGET]

from collections import Counter
print("\n=== PART 2 BANK ===")
print("total:", len(final))
print("by difficulty:", dict(Counter(q["difficulty"] for q in final)))
print("by category:", dict(Counter(q["category"] for q in final)))

# ---------------- append to V2 file ----------------
combined = v2 + final
# final safety dedup
nseen=set(); dedup=[]
for q in combined:
    n=norm(q["question"])
    if n in nseen: continue
    nseen.add(n); dedup.append(q)
json.dump(dedup, open(f"{MANNA}/manna_questions_v2.json","w"), indent=2, ensure_ascii=False)
print(f"\nV2 file now has {len(dedup)} total questions (was {len(v2)})")
print("by difficulty:", dict(Counter(q["difficulty"] for q in dedup)))
print("by category:", dict(Counter(q["category"] for q in dedup)))
