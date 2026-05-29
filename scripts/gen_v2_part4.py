#!/usr/bin/env python3
"""
Manna Volume 2 — PART 4: +2400 more. Sources:
 (A) TSK OT cross-references  -> Prophecy & Fulfillment + OT book categories
 (B) Gospel->OT links (expanded, fresh verses/anchors)
 (C) Greek/Hebrew lexicon (fresh words)
 (D) "Which book is this verse from?" (distinctive verses)
Deduped vs V1 + current V2. Appends to manna_questions_v2.json.
"""
import re, json, hashlib, random, html, glob, os
from collections import defaultdict
import sys
sys.path.insert(0, "/home/claude/manna/scripts")
from kjv_parse import parse_kjv, BOOKID

random.seed(7777001)
MANNA = "/home/claude/manna"; LUMINA = "/home/claude/lumina-bible"

BOOKS = {  # ref abbrev -> full name (covers TSK + gospel-link style)
 "Gen":"Genesis","Exod":"Exodus","Lev":"Leviticus","Num":"Numbers","Deut":"Deuteronomy",
 "Josh":"Joshua","Judg":"Judges","Ruth":"Ruth","1Sam":"1 Samuel","2Sam":"2 Samuel","1Kgs":"1 Kings",
 "2Kgs":"2 Kings","1Chr":"1 Chronicles","2Chr":"2 Chronicles","Ezra":"Ezra","Neh":"Nehemiah",
 "Esth":"Esther","Job":"Job","Ps":"Psalms","Prov":"Proverbs","Eccl":"Ecclesiastes","Song":"Song of Solomon",
 "Isa":"Isaiah","Jer":"Jeremiah","Lam":"Lamentations","Ezek":"Ezekiel","Dan":"Daniel","Hos":"Hosea",
 "Joel":"Joel","Amos":"Amos","Obad":"Obadiah","Jonah":"Jonah","Mic":"Micah","Nah":"Nahum","Hab":"Habakkuk",
 "Zeph":"Zephaniah","Hag":"Haggai","Zech":"Zechariah","Mal":"Malachi","Matt":"Matthew","Mark":"Mark",
 "Luke":"Luke","John":"John","Acts":"Acts","Rom":"Romans","1Cor":"1 Corinthians","2Cor":"2 Corinthians",
 "Gal":"Galatians","Eph":"Ephesians","Phil":"Philippians","Col":"Colossians","1Thess":"1 Thessalonians",
 "2Thess":"2 Thessalonians","1Tim":"1 Timothy","2Tim":"2 Timothy","Titus":"Titus","Phlm":"Philemon",
 "Heb":"Hebrews","Jas":"James","1Pet":"1 Peter","2Pet":"2 Peter","1John":"1 John","2John":"2 John",
 "3John":"3 John","Jude":"Jude","Rev":"Revelation",
}
NT = {"Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians","Galatians",
 "Ephesians","Philippians","Colossians","1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy",
 "Titus","Philemon","Hebrews","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation"}
def nice(ref):
    p=ref.split("."); 
    return f"{BOOKS.get(p[0],p[0])} {p[1]}:{p[2]}" if len(p)>=3 else ref
def bookof(ref): return BOOKS.get(ref.split(".")[0], ref.split(".")[0])
def norm(s): return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]","",s.lower())).strip()
def clean(t): return re.sub(r"\s+"," ",re.sub(r"\s+([,.;:!?])",r"\1",t)).strip()

# book -> manna category
BCAT = {}
for b in ["Genesis"]: BCAT[b]="Genesis & Creation"
for b in ["Exodus","Numbers"]: BCAT[b]="Moses & the Exodus"
for b in ["Leviticus","Deuteronomy"]: BCAT[b]="Laws & Commandments"
for b in ["Joshua","Judges"]: BCAT[b]="Battles & Wars"
for b in ["Ruth","Esther"]: BCAT[b]="Women of the Bible"
for b in ["1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra","Nehemiah"]:
    BCAT[b]="Kings & Kingdoms"
for b in ["Job","Psalms","Proverbs","Ecclesiastes","Song of Solomon"]: BCAT[b]="Psalms & Proverbs"
for b in ["Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah",
          "Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi"]:
    BCAT[b]="Prophets"
for b in ["Matthew","Mark","Luke","John"]: BCAT[b]="Life of Jesus"
for b in ["Acts","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude"]: BCAT[b]="The Apostles"
for b in ["Romans","1 Corinthians","2 Corinthians","Galatians","Ephesians","Philippians","Colossians",
          "1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon","Hebrews"]:
    BCAT[b]="Paul & His Letters"
BCAT["Revelation"]="Revelation & End Times"

# ---- verses + dedup base ----
raw=parse_kjv(); verses={}; meta={}
for bcv,txt in raw.items():
    p=bcv.split("."); 
    if len(p)!=3: continue
    bk=BOOKID.get(p[0]); 
    if not bk: continue
    r=f"{bk} {p[1]}:{p[2]}"; verses[r]=clean(txt); meta[r]=bk
v1=json.load(open(f"{MANNA}/manna_questions.json")); v2=json.load(open(f"{MANNA}/manna_questions_v2.json"))
seen=set(norm(q["question"]) for q in v1)|set(norm(q["question"]) for q in v2)
print(f"dedup base: V1={len(v1)} + V2={len(v2)}")

new=[]
def add(cat,diff,q,options,correct,exp=""):
    q=q.strip()
    if norm(q) in seen: return False
    opts=[]
    for o in options:
        o=str(o).strip()
        if o and o not in opts: opts.append(o)
    if correct not in opts or len(opts)<4: return False
    opts=opts[:4]
    if correct not in opts: opts[-1]=correct
    random.shuffle(opts); seen.add(norm(q))
    new.append({"category":cat,"difficulty":diff,"question":q,"options":opts,"correct":correct,
                "explanation":exp,"id":hashlib.md5((q+correct).encode()).hexdigest()[:12]})
    return True
def pick(pool,exclude,n=3):
    c=[x for x in pool if x and x!=exclude]; random.shuffle(c); out=[]
    for x in c:
        if x not in out: out.append(x)
        if len(out)==n: break
    return out

# ================= (A) TSK cross-references =================
tsk_files=glob.glob(f"{LUMINA}/ot_links_output/*.json"); random.shuffle(tsk_files)
all_targets=[]; tsk_rows=[]
for f in tsk_files:
    try: rows=json.load(open(f))
    except: continue
    for e in rows:
        ts=e.get("target_start"); src=e.get("source_ref"); anc=e.get("anchor"); rsn=e.get("reason","")
        if not (ts and src and anc): continue
        tsk_rows.append((src,anc,ts,rsn)); all_targets.append(nice(ts))
random.shuffle(tsk_rows)
made_tsk=0
for src,anc,ts,rsn in tsk_rows:
    if made_tsk>=720: break
    src_ref=nice(src); tgt_ref=nice(ts); tgt_book=bookof(ts); src_book=bookof(src)
    rtype=rsn.split(":")[0].strip().upper()
    reason_txt=clean(rsn.split(":",1)[1]) if ":" in rsn else clean(rsn)
    reason_txt=reason_txt[:160]
    if tgt_book in NT and rtype in ("QUOTE","FULFILLMENT"):
        verb="quoted in" if rtype=="QUOTE" else "fulfilled in"
        q=f"The Old Testament words \"{anc}\" ({src_ref}) are {verb} which New Testament passage?"
        cat="Prophecy & Fulfillment"
    else:
        q=f"In {src_ref}, the phrase \"{anc}\" is cross-referenced with which passage?"
        cat=BCAT.get(src_book,"Prophecy & Fulfillment")
    if add(cat,"Pastor",q,[tgt_ref]+pick(all_targets,tgt_ref),tgt_ref,reason_txt):
        made_tsk+=1
print(f"(A) TSK cross-refs: {made_tsk}")

# ================= (B) Gospel->OT links expanded =================
OT_BOOKS=[b for b in BCAT if b not in NT and b!="Revelation"]
OT_SET=set(OT_BOOKS)
gcat={"matthew":"Life of Jesus","mark":"Words of Jesus & OT Roots","luke":"Words of Jesus & OT Roots",
      "john":"Life of Jesus","acts":"The Apostles"}
made_links=0
for g,mcat in gcat.items():
    try: entries=json.load(open(f"{LUMINA}/data/backups/{g}-links-backup.json"))["entries"]
    except: continue
    refs=list(entries.keys()); random.shuffle(refs)
    ot_pool=list({nice(t["start"]) for r in refs for a in entries[r].get("anchors",[])
                  for t in a.get("targets",[]) if bookof(t["start"]) in OT_SET})
    for r in refs:
        if made_links>=620: break
        for a in entries[r].get("anchors",[]):   # use ALL anchors now (part 1 used only first)
            ot_t=next((t for t in a.get("targets",[]) if bookof(t["start"]) in OT_SET),None)
            if not ot_t: continue
            anc=a.get("anchor","")
            if not anc: continue
            tref=nice(ot_t["start"]); tbook=bookof(ot_t["start"])
            exp=clean(ot_t.get("reason",""))[:160]
            if add(mcat,"Pastor",
                   f"In {nice(r)}, the phrase \"{anc}\" echoes which Old Testament passage?",
                   [tref]+pick(ot_pool,tref),tref,exp):
                made_links+=1
    if made_links>=620: break
print(f"(B) Gospel->OT expanded: {made_links}")

# ================= (C) lexicon expanded =================
ETY=re.compile(r"^(of |from |a primary|a prim|akin to|comparative|superlative|the same as|"
               r"an unused root|by extension|probably|perhaps|apparently|contracted|reduplicat|"
               r"intensive|feminine of|masculine of|plural of)",re.I)
def cleandef(x):
    x=re.sub("<[^>]+>"," ",html.unescape(x)); x=re.sub(r"^\s*\([A-Za-z]+\)\s*","",x)
    return re.sub(r"\s+"," ",x).strip(" .;:")
def lex(path,lang,cap):
    d=json.load(open(path)); items=[]
    for k,v in d.items():
        tr=re.search(r"Transliteration:\s*<strong>([^<]+)</strong>",v)
        og=re.search(r"Original:\s*<strong>([^<]+)</strong>",v)
        if not(tr and og): continue
        gloss=None
        m=re.search(r"<li>(.*?)(?=<ol|<li|</li>|</ol>)",v,re.S)
        if m:
            g=cleandef(m.group(1))
            if 4<=len(g)<=60 and len(g.split())>=2 and not ETY.search(g): gloss=g
        if gloss: items.append((tr.group(1),og.group(1),gloss))
    pool=[i[2] for i in items]; random.shuffle(items); made=0
    for tr,og,dfn in items:
        if made>=cap: break
        n=len(dfn.split()); cand=[d2 for d2 in pool if d2!=dfn and abs(len(d2.split())-n)<=4]
        random.shuffle(cand); distr=[]
        for d2 in cand:
            if d2 not in distr and norm(d2)!=norm(dfn): distr.append(d2)
            if len(distr)==3: break
        if len(distr)<3: continue
        if add("Words of Jesus & OT Roots","Pastor",
               f"What is the meaning of the {lang} word \"{tr}\" ({og})?",
               [dfn]+distr,dfn,""): made+=1
    return made
ml=lex(f"{LUMINA}/data/lexicons/lexicon-greek.json","Greek",260)+lex(f"{LUMINA}/data/lexicons/lexicon-hebrew.json","Hebrew",260)
print(f"(C) lexicon expanded: {ml}")

# ================= (D) which book is this verse from =================
TESTA={b:("NT" if b in NT else "OT") for b in BCAT}
books_by_t={"OT":[b for b in BCAT if TESTA[b]=="OT"],"NT":[b for b in BCAT if TESTA[b]=="NT"]}
# distinctive verses: contain a proper noun (capitalized word not at start) and decent length
distinct=[]
for r,txt in verses.items():
    wc=len(txt.split())
    if 10<=wc<=24:
        words=txt.split()
        if any(w[0].isupper() and w.lower() not in ("and","but","the","for","lord","god","jesus","christ")
               for w in words[2:]):
            distinct.append(r)
random.shuffle(distinct); made_wb=0
weights={"Layperson":2,"Deacon":5,"Pastor":3}; ds=list(weights); ws=list(weights.values())
for r in distinct:
    if made_wb>=700: break
    bk=meta[r]; t=TESTA.get(bk)
    if not t: continue
    others=[b for b in books_by_t[t] if b!=bk]
    if len(others)<3: continue
    snippet=verses[r].rstrip(".")
    if add(BCAT.get(bk,"Numbers & Genealogies"), random.choices(ds,weights=ws,k=1)[0],
           f"In which book of the Bible is this verse found: \"{snippet}\"",
           [bk]+random.sample(others,3),bk,r):
        made_wb+=1
print(f"(D) which-book: {made_wb}")

# ================= trim to 2400 =================
random.shuffle(new); TARGET=2400
by=defaultdict(list)
for q in new: by[q["difficulty"]].append(q)
print("available by difficulty:", {k:len(v) for k,v in by.items()})
final=[]; per=TARGET//3
for d in ("Layperson","Deacon","Pastor"): final.extend(by[d][:per])
left=[q for q in new if q not in final]; random.shuffle(left)
for q in left:
    if len(final)>=TARGET: break
    final.append(q)
final=final[:TARGET]
from collections import Counter
print("\n=== PART 4 ===","total:",len(final))
print("by difficulty:",dict(Counter(q["difficulty"] for q in final)))
print("by category:",dict(Counter(q["category"] for q in final)))

combined=v2+final; ns=set(); dd=[]
for q in combined:
    n=norm(q["question"])
    if n in ns: continue
    ns.add(n); dd.append(q)
json.dump(dd,open(f"{MANNA}/manna_questions_v2.json","w"),indent=2,ensure_ascii=False)
print(f"\nV2 file now: {len(dd)} (was {len(v2)})")
print("by difficulty:",dict(Counter(q["difficulty"] for q in dd)))
print("by category:",dict(Counter(q["category"] for q in dd)))
