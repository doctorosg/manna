#!/usr/bin/env python3
"""
Manna Volume 2 — PART 3: +1200 more, filling Paul & His Letters and other thin
categories. Sources: KJV (complete-the-verse on untapped books) + Greek/Hebrew
lexicon word-meaning questions. Deduped vs V1 + current V2. Appends to V2.
"""
import re, json, hashlib, random, html
from collections import defaultdict
import sys
sys.path.insert(0, "/home/claude/manna/scripts")
from kjv_parse import parse_kjv, BOOKID

random.seed(424242)
MANNA = "/home/claude/manna"
LUMINA = "/home/claude/lumina-bible"

def clean(t):
    return re.sub(r"\s+", " ", re.sub(r"\s+([,.;:!?])", r"\1", t)).strip()
def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", s.lower())).strip()

raw = parse_kjv()
verses, meta = {}, {}
for bcv, txt in raw.items():
    p = bcv.split(".")
    if len(p) != 3: continue
    bk = BOOKID.get(p[0])
    if not bk: continue
    ref = f"{bk} {p[1]}:{p[2]}"
    verses[ref] = clean(txt); meta[ref] = (bk, p[1], p[2])

v1 = json.load(open(f"{MANNA}/manna_questions.json"))
v2 = json.load(open(f"{MANNA}/manna_questions_v2.json"))
seen = set(norm(q["question"]) for q in v1) | set(norm(q["question"]) for q in v2)
print(f"dedup base: V1={len(v1)} + V2={len(v2)}")

new = []
def add(category, difficulty, question, options, correct, explanation=""):
    q = question.strip()
    if norm(q) in seen: return False
    opts = []
    for o in options:
        o = str(o).strip()
        if o and o not in opts: opts.append(o)
    if correct not in opts or len(opts) < 4: return False
    opts = opts[:4]
    if correct not in opts: opts[-1] = correct
    random.shuffle(opts); seen.add(norm(q))
    new.append({"category":category,"difficulty":difficulty,"question":q,"options":opts,
                "correct":correct,"explanation":explanation,
                "id":hashlib.md5((q+correct).encode()).hexdigest()[:12]})
    return True

# ---------------- complete-the-verse ----------------
def split_verse(text):
    for sep in [": ", "; "]:
        if sep in text:
            i = text.index(sep)
            a, b = text[:i].strip(), text[i+len(sep):].strip().rstrip(".")
            if len(a.split()) >= 4 and 4 <= len(b.split()) <= 14: return a, b
    if ", " in text:
        idxs = [m.start() for m in re.finditer(", ", text)]; mid = len(text)//2
        i = min(idxs, key=lambda x: abs(x-mid))
        a, b = text[:i].strip(), text[i+2:].strip().rstrip(".")
        if len(a.split()) >= 4 and 4 <= len(b.split()) <= 14: return a, b
    return None

def completions(refs, category, weights, cap):
    pieces = []
    for r in refs:
        sp = split_verse(verses[r])
        if sp: pieces.append((r, sp[0], sp[1]))
    pool = [p[2] for p in pieces]; random.shuffle(pieces)
    ds = list(weights.keys()); ws = list(weights.values()); made = 0
    for r, stem, ans in pieces:
        if made >= cap: break
        n = len(ans.split())
        cand = [a for a in pool if a != ans and abs(len(a.split())-n) <= 4]
        random.shuffle(cand); distr = []
        for a in cand:
            if a not in distr: distr.append(a)
            if len(distr) == 3: break
        if len(distr) < 3: continue
        if add(category, random.choices(ds, weights=ws, k=1)[0],
               f"Complete this verse from {meta[r][0]}: \"{stem} ...\"",
               [ans]+distr, ans, r): made += 1
    return made

def brefs(books): return [r for r in verses if meta[r][0] in books]

PAUL = {"Romans","1 Corinthians","2 Corinthians","Galatians","Ephesians","Philippians",
        "Colossians","1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy","Titus",
        "Philemon","Hebrews"}
GENERAL = {"James","1 Peter","2 Peter","1 John","2 John","3 John","Jude"}

plan = {
 "Paul & His Letters":      (brefs(PAUL), {"Deacon":5,"Pastor":5}, 200),
 "Genesis & Creation":      (brefs({"Genesis"}), {"Layperson":3,"Deacon":5,"Pastor":2}, 130),
 "Moses & the Exodus":      (brefs({"Exodus","Numbers"}), {"Layperson":3,"Deacon":5,"Pastor":2}, 130),
 "Laws & Commandments":     (brefs({"Leviticus","Deuteronomy"}), {"Deacon":6,"Pastor":4}, 120),
 "Kings & Kingdoms":        (brefs({"1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles",
                              "2 Chronicles","Ezra","Nehemiah"}), {"Layperson":2,"Deacon":6,"Pastor":2}, 130),
 "Prophets":                (brefs({"Isaiah","Jeremiah","Lamentations","Ezekiel","Hosea","Joel",
                              "Amos","Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah",
                              "Haggai","Zechariah","Malachi"}), {"Deacon":5,"Pastor":5}, 130),
 "Life of Jesus":           (brefs({"Matthew","Mark","Luke","John"}), {"Layperson":3,"Deacon":5,"Pastor":2}, 110),
 "The Apostles":            (brefs({"Acts"} | GENERAL), {"Deacon":6,"Pastor":4}, 110),
}
for cat,(refs,w,cap) in plan.items():
    refs = list(dict.fromkeys(refs))
    print(f"{cat}: pool={len(refs)} made={completions(refs, cat, w, cap)}")

# ---------------- which Pauline epistle ----------------
paul_refs = [r for r in verses if meta[r][0] in PAUL and 9 <= len(verses[r].split()) <= 26]
random.shuffle(paul_refs); pmade = 0
for r in paul_refs:
    if pmade >= 60: break
    bk = meta[r][0]
    others = [b for b in PAUL if b != bk]
    snippet = verses[r].rstrip(".")
    if add("Paul & His Letters", "Pastor",
           f"In which of Paul's letters is this verse found: \"{snippet}\"",
           [bk] + random.sample(others, 3), bk, r):
        pmade += 1
print(f"which-epistle: {pmade}")

# ---------------- lexicon word meanings ----------------
def lex_questions(path, lang, cap):
    d = json.load(open(path))
    def cleandef(x):
        x = re.sub("<[^>]+>", " ", html.unescape(x))
        x = re.sub(r"^\s*\([A-Za-z]+\)\s*", "", x)   # drop leading source codes like (CLBL)
        x = re.sub(r"\s+", " ", x).strip(" .;:")
        return x
    items = []
    ETY = re.compile(r"^(of |from |a primary|a prim|akin to|comparative|superlative|"
                     r"the same as|an unused root|by extension|probably|perhaps|apparently|"
                     r"contracted|reduplicat|intensive|feminine of|masculine of|plural of)", re.I)
    for k, v in d.items():
        tr = re.search(r"Transliteration:\s*<strong>([^<]+)</strong>", v)
        og = re.search(r"Original:\s*<strong>([^<]+)</strong>", v)
        if not (tr and og): continue
        gloss = None
        # primary: first BDB/Thayer list item (the actual definition), cut before any nested list
        m = re.search(r"<li>(.*?)(?=<ol|<li|</li>|</ol>)", v, re.S)
        if m:
            g = cleandef(m.group(1))
            if 4 <= len(g) <= 60 and len(g.split()) >= 2 and not ETY.search(g):
                gloss = g
        if not gloss:   # fallback: Strong's gloss = clause before the ':—' KJV-usage marker
            sd = re.search(r"Strong's Definition</strong>:?\s*(.*?)(?:<|Origin:|$)", v, re.S)
            if sd:
                g = cleandef(sd.group(1))
                g = re.split(r":[—\-]", g)[0]          # drop KJV usage list
                g = re.split(r";", g)[-1].strip()       # take meaning clause after etymology
                if 4 <= len(g) <= 60 and len(g.split()) >= 2 and not ETY.search(g):
                    gloss = g
        if gloss:
            items.append((tr.group(1), og.group(1), gloss))
    defpool = [it[2] for it in items]
    random.shuffle(items); made = 0
    for tr, og, dfn in items:
        if made >= cap: break
        n = len(dfn.split())
        cand = [d2 for d2 in defpool if d2 != dfn and abs(len(d2.split())-n) <= 4]
        random.shuffle(cand); distr = []
        for d2 in cand:
            if d2 not in distr and norm(d2) != norm(dfn): distr.append(d2)
            if len(distr) == 3: break
        if len(distr) < 3: continue
        if add("Words of Jesus & OT Roots", "Pastor",
               f"What is the meaning of the {lang} word \"{tr}\" ({og})?",
               [dfn]+distr, dfn, ""): made += 1
    return made

print(f"greek lexicon: {lex_questions(f'{LUMINA}/data/lexicons/lexicon-greek.json','Greek',90)}")
print(f"hebrew lexicon: {lex_questions(f'{LUMINA}/data/lexicons/lexicon-hebrew.json','Hebrew',90)}")

# ---------------- trim to 1200 ----------------
random.shuffle(new)
TARGET = 1200
by = defaultdict(list)
for q in new: by[q["difficulty"]].append(q)
print("available by difficulty:", {k:len(v) for k,v in by.items()})
final = []
per = TARGET//3
for d in ("Layperson","Deacon","Pastor"): final.extend(by[d][:per])
left = [q for q in new if q not in final]; random.shuffle(left)
for q in left:
    if len(final) >= TARGET: break
    final.append(q)
final = final[:TARGET]

from collections import Counter
print("\n=== PART 3 ===")
print("total:", len(final), "| by difficulty:", dict(Counter(q["difficulty"] for q in final)))
print("by category:", dict(Counter(q["category"] for q in final)))

combined = v2 + final
ns=set(); dd=[]
for q in combined:
    n=norm(q["question"])
    if n in ns: continue
    ns.add(n); dd.append(q)
json.dump(dd, open(f"{MANNA}/manna_questions_v2.json","w"), indent=2, ensure_ascii=False)
print(f"\nV2 file now: {len(dd)} (was {len(v2)})")
print("by difficulty:", dict(Counter(q["difficulty"] for q in dd)))
print("by category:", dict(Counter(q["category"] for q in dd)))
