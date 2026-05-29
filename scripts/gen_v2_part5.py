#!/usr/bin/env python3
"""
Manna Volume 2 — PART 5.
Step 1: drop the Layperson tier (V2 becomes two levels: Deacon + Pastor).
Step 2: add 2400 more Deacon/Pastor questions from fresh sources:
  - Catena Aurea Church Fathers ("which Father commented on...")
  - more TSK cross-references
  - more Gospel->OT links
  - more Greek/Hebrew lexicon
  - alternate-split verse completions
Deduped vs V1 + current V2. Writes manna_questions_v2.json.
"""
import re, json, hashlib, random, html, glob
from collections import defaultdict
import sys
sys.path.insert(0, "/home/claude/manna/scripts")
from kjv_parse import parse_kjv, BOOKID

random.seed(550055)
MANNA="/home/claude/manna"; LUMINA="/home/claude/lumina-bible"

BOOKS={"Gen":"Genesis","Exod":"Exodus","Lev":"Leviticus","Num":"Numbers","Deut":"Deuteronomy",
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
 "3John":"3 John","Jude":"Jude","Rev":"Revelation"}
NT={"Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians","Galatians",
 "Ephesians","Philippians","Colossians","1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy",
 "Titus","Philemon","Hebrews","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation"}
def nice(r):
    p=r.split("."); return f"{BOOKS.get(p[0],p[0])} {p[1]}:{p[2]}" if len(p)>=3 else r
def bookof(r): return BOOKS.get(r.split(".")[0], r.split(".")[0])
def norm(s): return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]","",s.lower())).strip()
def clean(t): return re.sub(r"\s+"," ",re.sub(r"\s+([,.;:!?])",r"\1",t)).strip()

BCAT={}
BCAT["Genesis"]="Genesis & Creation"
for b in ["Exodus","Numbers"]: BCAT[b]="Moses & the Exodus"
for b in ["Leviticus","Deuteronomy"]: BCAT[b]="Laws & Commandments"
for b in ["Joshua","Judges"]: BCAT[b]="Battles & Wars"
for b in ["Ruth","Esther"]: BCAT[b]="Women of the Bible"
for b in ["1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra","Nehemiah"]: BCAT[b]="Kings & Kingdoms"
for b in ["Job","Psalms","Proverbs","Ecclesiastes","Song of Solomon"]: BCAT[b]="Psalms & Proverbs"
for b in ["Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi"]: BCAT[b]="Prophets"
for b in ["Matthew","Mark","Luke","John"]: BCAT[b]="Life of Jesus"
for b in ["Acts","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude"]: BCAT[b]="The Apostles"
for b in ["Romans","1 Corinthians","2 Corinthians","Galatians","Ephesians","Philippians","Colossians","1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon","Hebrews"]: BCAT[b]="Paul & His Letters"
BCAT["Revelation"]="Revelation & End Times"

raw=parse_kjv(); verses={}; meta={}
for bcv,txt in raw.items():
    p=bcv.split(".")
    if len(p)!=3: continue
    bk=BOOKID.get(p[0])
    if not bk: continue
    r=f"{bk} {p[1]}:{p[2]}"; verses[r]=clean(txt); meta[r]=bk

# ---- Step 1: drop Layperson ----
v1=json.load(open(f"{MANNA}/manna_questions.json"))
v2_all=json.load(open(f"{MANNA}/manna_questions_v2.json"))
v2=[q for q in v2_all if q["difficulty"]!="Layperson"]
print(f"V2 before: {len(v2_all)} -> after dropping Layperson: {len(v2)} (removed {len(v2_all)-len(v2)})")
seen=set(norm(q["question"]) for q in v1)|set(norm(q["question"]) for q in v2)

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

# ===== (A) Catena Aurea — which Church Father =====
g=json.load(open(f"{LUMINA}/data/commentaries/catena-aurea-project/catena_aurea_graph.json"))
narrs=[n["properties"] for n in g["nodes"] if n["type"]=="Patristic_Narrative"]
fathers=sorted({n.get("source") for n in narrs if n.get("source")})
def ref_to_nice(vr):
    # verse_matthew_1_1 -> Matthew 1:1
    m=re.match(r"verse_([a-z0-9]+)_(\d+)_(\d+)", vr or "")
    if not m: return None
    bk={"matthew":"Matthew","mark":"Mark","luke":"Luke","john":"John"}.get(m.group(1))
    return f"{bk} {m.group(2)}:{m.group(3)}" if bk else None
def first_sent(t,maxlen=170):
    t=clean(html.unescape(str(t)).replace("’","'").replace("‘","'").replace("“",'"').replace("”",'"'))
    s=re.split(r"(?<=[.!?]) ", t)[0]
    return (s[:maxlen].rsplit(" ",1)[0]+"...") if len(s)>maxlen else s
random.shuffle(narrs); made_cat=0
for n in narrs:
    if made_cat>=520: break
    src=n.get("source"); ref=ref_to_nice(n.get("verse_reference")); txt=n.get("text")
    if not (src and ref and txt): continue
    snip=first_sent(txt)
    if len(snip.split())<6 or src in snip: continue
    if add("Life of Jesus","Pastor",
           f"Which Church Father wrote this commentary on {ref}: \"{snip}\"",
           [src]+pick(fathers,src), src, ref):
        made_cat+=1
print(f"(A) Catena Church Fathers: {made_cat}")

# ===== (B) more TSK cross-refs =====
tsk_rows=[]; all_t=[]
for f in glob.glob(f"{LUMINA}/ot_links_output/*.json"):
    try: rows=json.load(open(f))
    except: continue
    for e in rows:
        ts=e.get("target_start"); src=e.get("source_ref"); anc=e.get("anchor"); rsn=e.get("reason","")
        if ts and src and anc:
            tsk_rows.append((src,anc,ts,rsn)); all_t.append(nice(ts))
random.shuffle(tsk_rows); made_tsk=0
for src,anc,ts,rsn in tsk_rows:
    if made_tsk>=620: break
    sref=nice(src); tref=nice(ts); tb=bookof(ts); sb=bookof(src)
    rtype=rsn.split(":")[0].strip().upper(); rtxt=clean(rsn.split(":",1)[1])[:160] if ":" in rsn else clean(rsn)[:160]
    if tb in NT and rtype in ("QUOTE","FULFILLMENT"):
        verb="quoted in" if rtype=="QUOTE" else "fulfilled in"
        q=f"The Old Testament words \"{anc}\" ({sref}) are {verb} which New Testament passage?"
        cat="Prophecy & Fulfillment"; diff="Pastor"
    else:
        q=f"To which passage is {sref} (\"{anc}\") cross-referenced?"
        cat=BCAT.get(sb,"Prophecy & Fulfillment"); diff="Deacon"
    if add(cat,diff,q,[tref]+pick(all_t,tref),tref,rtxt): made_tsk+=1
print(f"(B) TSK cross-refs: {made_tsk}")

# ===== (C) more Gospel->OT links =====
OT_SET={b for b in BCAT if b not in NT and b!="Revelation"}
gcat={"matthew":"Life of Jesus","mark":"Words of Jesus & OT Roots","luke":"Words of Jesus & OT Roots",
      "john":"Life of Jesus","acts":"The Apostles"}
made_links=0
for gg,mcat in gcat.items():
    try: entries=json.load(open(f"{LUMINA}/data/backups/{gg}-links-backup.json"))["entries"]
    except: continue
    refs=list(entries.keys()); random.shuffle(refs)
    pool=list({nice(t["start"]) for r in refs for a in entries[r].get("anchors",[]) for t in a.get("targets",[]) if bookof(t["start"]) in OT_SET})
    for r in refs:
        if made_links>=420: break
        for a in entries[r].get("anchors",[]):
            tt=[t for t in a.get("targets",[]) if bookof(t["start"]) in OT_SET]
            for ot_t in tt[:2]:   # use up to 2 targets per anchor (fresh)
                tref=nice(ot_t["start"]); anc=a.get("anchor","")
                if not anc: continue
                if add(mcat,"Pastor",
                       f"The phrase \"{anc}\" in {nice(r)} draws on which Old Testament text?",
                       [tref]+pick(pool,tref),tref,clean(ot_t.get("reason",""))[:160]):
                    made_links+=1
    if made_links>=420: break
print(f"(C) Gospel->OT: {made_links}")

# ===== (D) more lexicon =====
ETY=re.compile(r"^(of |from |a primary|a prim|akin to|comparative|superlative|the same as|an unused root|by extension|probably|perhaps|apparently|contracted|reduplicat|intensive|feminine of|masculine of|plural of)",re.I)
def cleandef(x):
    x=re.sub("<[^>]+>"," ",html.unescape(x)); x=re.sub(r"^\s*\([A-Za-z]+\)\s*","",x)
    return re.sub(r"\s+"," ",x).strip(" .;:")
def lex(path,lang,cap):
    d=json.load(open(path)); items=[]
    for k,v in d.items():
        tr=re.search(r"Transliteration:\s*<strong>([^<]+)</strong>",v); og=re.search(r"Original:\s*<strong>([^<]+)</strong>",v)
        if not(tr and og): continue
        m=re.search(r"<li>(.*?)(?=<ol|<li|</li>|</ol>)",v,re.S)
        if not m: continue
        gl=cleandef(m.group(1))
        if 4<=len(gl)<=60 and len(gl.split())>=2 and not ETY.search(gl): items.append((tr.group(1),og.group(1),gl))
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
               f"What is the meaning of the {lang} word \"{tr}\" ({og})?",[dfn]+distr,dfn,""): made+=1
    return made
ml=lex(f"{LUMINA}/data/lexicons/lexicon-greek.json","Greek",220)+lex(f"{LUMINA}/data/lexicons/lexicon-hebrew.json","Hebrew",220)
print(f"(D) lexicon: {ml}")

# ===== (E) alternate-split verse completions (Deacon volume) =====
def split_alt(text):
    bounds=[m.start() for m in re.finditer(r"[;:] ", text)]+[m.start() for m in re.finditer(r", ", text)]
    bounds=sorted(set(bounds))
    if not bounds: return None
    # take the LAST boundary (different stem than first-split used in parts 2/3)
    for i in reversed(bounds):
        sep_len=2
        a=text[:i].strip(); b=text[i+sep_len:].strip().rstrip(".")
        if len(a.split())>=6 and 4<=len(b.split())<=12:
            return a,b
    return None
all_refs=list(verses.keys()); random.shuffle(all_refs)
allbits=[]
for r in all_refs:
    sp=split_alt(verses[r])
    if sp: allbits.append((r,sp[0],sp[1]))
poolE=[b for _,_,b in allbits]; made_e=0
for r,stem,ans in allbits:
    if made_e>=520: break
    n=len(ans.split()); cand=[a for a in poolE if a!=ans and abs(len(a.split())-n)<=4]
    random.shuffle(cand); distr=[]
    for a in cand:
        if a not in distr: distr.append(a)
        if len(distr)==3: break
    if len(distr)<3: continue
    if add(BCAT.get(meta[r],"Numbers & Genealogies"),"Deacon",
           f"Complete this verse from {meta[r]}: \"{stem} ...\"",[ans]+distr,ans,r):
        made_e+=1
print(f"(E) alt-split completions: {made_e}")

# ===== trim to 2400 (Deacon+Pastor only) =====
random.shuffle(new); TARGET=2400
# prefer a healthier Deacon share: take up to 1100 Deacon then fill with Pastor
by=defaultdict(list)
for q in new: by[q["difficulty"]].append(q)
print("available:", {k:len(v) for k,v in by.items()})
final=by["Deacon"][:1100]
need=TARGET-len(final)
final+=by["Pastor"][:need]
if len(final)<TARGET:  # top up from any leftover
    extra=[q for q in new if q not in final]; random.shuffle(extra)
    final+=extra[:TARGET-len(final)]
final=final[:TARGET]
from collections import Counter
print("\n=== PART 5 NEW ===","total:",len(final),"| by difficulty:",dict(Counter(q["difficulty"] for q in final)))
print("by category:",dict(Counter(q["category"] for q in final)))

combined=v2+final; ns=set(); dd=[]
for q in combined:
    n=norm(q["question"])
    if n in ns: continue
    ns.add(n); dd.append(q)
json.dump(dd,open(f"{MANNA}/manna_questions_v2.json","w"),indent=2,ensure_ascii=False)
print(f"\nV2 FILE NOW: {len(dd)}")
print("by difficulty:",dict(Counter(q["difficulty"] for q in dd)))
print("by category:",dict(Counter(q["category"] for q in dd)))
