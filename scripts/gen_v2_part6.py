#!/usr/bin/env python3
"""Manna V2 PART 6: round up to exactly 10,000 (two levels). Fresh items from
Catena Fathers, TSK cross-refs, Gospel->OT links, lexicon, mid-split completions.
Deduped vs V1 + current V2. Appends to manna_questions_v2.json."""
import re, json, hashlib, random, html, glob
from collections import defaultdict
import sys; sys.path.insert(0,"/home/claude/manna/scripts")
from kjv_parse import parse_kjv, BOOKID
random.seed(31415926)
M="/home/claude/manna"; L="/home/claude/lumina-bible"
BOOKS={"Gen":"Genesis","Exod":"Exodus","Lev":"Leviticus","Num":"Numbers","Deut":"Deuteronomy","Josh":"Joshua","Judg":"Judges","Ruth":"Ruth","1Sam":"1 Samuel","2Sam":"2 Samuel","1Kgs":"1 Kings","2Kgs":"2 Kings","1Chr":"1 Chronicles","2Chr":"2 Chronicles","Ezra":"Ezra","Neh":"Nehemiah","Esth":"Esther","Job":"Job","Ps":"Psalms","Prov":"Proverbs","Eccl":"Ecclesiastes","Song":"Song of Solomon","Isa":"Isaiah","Jer":"Jeremiah","Lam":"Lamentations","Ezek":"Ezekiel","Dan":"Daniel","Hos":"Hosea","Joel":"Joel","Amos":"Amos","Obad":"Obadiah","Jonah":"Jonah","Mic":"Micah","Nah":"Nahum","Hab":"Habakkuk","Zeph":"Zephaniah","Hag":"Haggai","Zech":"Zechariah","Mal":"Malachi","Matt":"Matthew","Mark":"Mark","Luke":"Luke","John":"John","Acts":"Acts","Rom":"Romans","1Cor":"1 Corinthians","2Cor":"2 Corinthians","Gal":"Galatians","Eph":"Ephesians","Phil":"Philippians","Col":"Colossians","1Thess":"1 Thessalonians","2Thess":"2 Thessalonians","1Tim":"1 Timothy","2Tim":"2 Timothy","Titus":"Titus","Phlm":"Philemon","Heb":"Hebrews","Jas":"James","1Pet":"1 Peter","2Pet":"2 Peter","1John":"1 John","2John":"2 John","3John":"3 John","Jude":"Jude","Rev":"Revelation"}
NT={"Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians","Galatians","Ephesians","Philippians","Colossians","1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon","Hebrews","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation"}
def nice(r): p=r.split("."); return f"{BOOKS.get(p[0],p[0])} {p[1]}:{p[2]}" if len(p)>=3 else r
def bookof(r): return BOOKS.get(r.split(".")[0], r.split(".")[0])
def norm(s): return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]","",s.lower())).strip()
def clean(t): return re.sub(r"\s+"," ",re.sub(r"\s+([,.;:!?])",r"\1",t)).strip()
BCAT={"Genesis":"Genesis & Creation"}
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
    if len(p)==3 and BOOKID.get(p[0]):
        r=f"{BOOKID[p[0]]} {p[1]}:{p[2]}"; verses[r]=clean(txt); meta[r]=BOOKID[p[0]]

v1=json.load(open(f"{M}/manna_questions.json")); v2=json.load(open(f"{M}/manna_questions_v2.json"))
seen=set(norm(q["question"]) for q in v1)|set(norm(q["question"]) for q in v2)
NEED=10000-len(v2)
print(f"current V2={len(v2)} -> need {NEED} more")
new=[]
def add(cat,diff,q,opts,correct,exp=""):
    q=q.strip()
    if norm(q) in seen: return False
    o=[]
    for x in opts:
        x=str(x).strip()
        if x and x not in o: o.append(x)
    if correct not in o or len(o)<4: return False
    o=o[:4]
    if correct not in o: o[-1]=correct
    random.shuffle(o); seen.add(norm(q))
    new.append({"category":cat,"difficulty":diff,"question":q,"options":o,"correct":correct,"explanation":exp,"id":hashlib.md5((q+correct).encode()).hexdigest()[:12]})
    return True
def pick(pool,ex,n=3):
    c=[x for x in pool if x and x!=ex]; random.shuffle(c); out=[]
    for x in c:
        if x not in out: out.append(x)
        if len(out)==n: break
    return out

# (A) Catena
g=json.load(open(f"{L}/data/commentaries/catena-aurea-project/catena_aurea_graph.json"))
narrs=[n["properties"] for n in g["nodes"] if n["type"]=="Patristic_Narrative"]
fathers=sorted({n.get("source") for n in narrs if n.get("source")})
def r2n(vr):
    m=re.match(r"verse_([a-z0-9]+)_(\d+)_(\d+)",vr or "")
    bk={"matthew":"Matthew","mark":"Mark","luke":"Luke","john":"John"}.get(m.group(1)) if m else None
    return f"{bk} {m.group(2)}:{m.group(3)}" if bk else None
def fs(t,mx=170):
    t=clean(html.unescape(str(t)).replace("\u2019","'").replace("\u2018","'").replace("\u201c",'"').replace("\u201d",'"'))
    s=re.split(r"(?<=[.!?]) ",t)[0]; return (s[:mx].rsplit(" ",1)[0]+"...") if len(s)>mx else s
random.shuffle(narrs); a=0
for n in narrs:
    if a>=760: break
    src=n.get("source"); ref=r2n(n.get("verse_reference")); txt=n.get("text")
    if not(src and ref and txt): continue
    snip=fs(txt)
    if len(snip.split())<6 or src in snip: continue
    if add("Life of Jesus","Pastor",f"Which Church Father wrote this commentary on {ref}: \"{snip}\"",[src]+pick(fathers,src),src,ref): a+=1
print("(A) catena:",a)

# (B) TSK
rows=[]; allt=[]
for f in glob.glob(f"{L}/ot_links_output/*.json"):
    try: rr=json.load(open(f))
    except: continue
    for e in rr:
        ts=e.get("target_start"); s=e.get("source_ref"); an=e.get("anchor"); rs=e.get("reason","")
        if ts and s and an: rows.append((s,an,ts,rs)); allt.append(nice(ts))
random.shuffle(rows); b=0
for s,an,ts,rs in rows:
    if b>=900: break
    sr=nice(s); tr=nice(ts); tb=bookof(ts); sb=bookof(s)
    rt=rs.split(":")[0].strip().upper(); rx=clean(rs.split(":",1)[1])[:160] if ":" in rs else clean(rs)[:160]
    if tb in NT and rt in ("QUOTE","FULFILLMENT"):
        vb="quoted in" if rt=="QUOTE" else "fulfilled in"
        if add("Prophecy & Fulfillment","Pastor",f"The Old Testament words \"{an}\" ({sr}) are {vb} which New Testament passage?",[tr]+pick(allt,tr),tr,rx): b+=1
    else:
        if add(BCAT.get(sb,"Prophecy & Fulfillment"),"Deacon",f"With which passage is {sr} (\"{an}\") connected by cross-reference?",[tr]+pick(allt,tr),tr,rx): b+=1
print("(B) tsk:",b)

# (C) Gospel->OT
OT={x for x in BCAT if x not in NT and x!="Revelation"}
gc={"matthew":"Life of Jesus","mark":"Words of Jesus & OT Roots","luke":"Words of Jesus & OT Roots","john":"Life of Jesus","acts":"The Apostles"}
c=0
for gg,mc in gc.items():
    try: en=json.load(open(f"{L}/data/backups/{gg}-links-backup.json"))["entries"]
    except: continue
    rf=list(en.keys()); random.shuffle(rf)
    pool=list({nice(t["start"]) for r in rf for an in en[r].get("anchors",[]) for t in an.get("targets",[]) if bookof(t["start"]) in OT})
    for r in rf:
        if c>=600: break
        for an in en[r].get("anchors",[]):
            for t in [x for x in an.get("targets",[]) if bookof(x["start"]) in OT][:3]:
                tr=nice(t["start"]); a2=an.get("anchor","")
                if not a2: continue
                if add(mc,"Pastor",f"Which Old Testament scripture stands behind \"{a2}\" in {nice(r)}?",[tr]+pick(pool,tr),tr,clean(t.get("reason",""))[:160]): c+=1
    if c>=600: break
print("(C) gospel:",c)

# (D) lexicon
ETY=re.compile(r"^(of |from |a primary|a prim|akin to|comparative|superlative|the same as|an unused root|by extension|probably|perhaps|apparently|contracted|reduplicat|intensive|feminine of|masculine of|plural of)",re.I)
def cd(x):
    x=re.sub("<[^>]+>"," ",html.unescape(x)); x=re.sub(r"^\s*\([A-Za-z]+\)\s*","",x); return re.sub(r"\s+"," ",x).strip(" .;:")
def lex(path,lang,cap):
    d=json.load(open(path)); it=[]
    for k,v in d.items():
        tr=re.search(r"Transliteration:\s*<strong>([^<]+)</strong>",v); og=re.search(r"Original:\s*<strong>([^<]+)</strong>",v)
        if not(tr and og): continue
        m=re.search(r"<li>(.*?)(?=<ol|<li|</li>|</ol>)",v,re.S)
        if not m: continue
        gl=cd(m.group(1))
        if 4<=len(gl)<=60 and len(gl.split())>=2 and not ETY.search(gl): it.append((tr.group(1),og.group(1),gl))
    pool=[i[2] for i in it]; random.shuffle(it); md=0
    for tr,og,df in it:
        if md>=cap: break
        n=len(df.split()); cand=[d2 for d2 in pool if d2!=df and abs(len(d2.split())-n)<=4]; random.shuffle(cand); ds=[]
        for d2 in cand:
            if d2 not in ds and norm(d2)!=norm(df): ds.append(d2)
            if len(ds)==3: break
        if len(ds)<3: continue
        if add("Words of Jesus & OT Roots","Pastor",f"What is the meaning of the {lang} word \"{tr}\" ({og})?",[df]+ds,df,""): md+=1
    return md
dd=lex(f"{L}/data/lexicons/lexicon-greek.json","Greek",350)+lex(f"{L}/data/lexicons/lexicon-hebrew.json","Hebrew",350)
print("(D) lexicon:",dd)

# (E) mid-split completions (Deacon)
def midsplit(t):
    bs=sorted(set([m.start() for m in re.finditer(r"[;:] ",t)]+[m.start() for m in re.finditer(r", ",t)]))
    if len(bs)<2: return None
    i=bs[len(bs)//2]; aa=t[:i].strip(); bb=t[i+2:].strip().rstrip(".")
    if len(aa.split())>=6 and 4<=len(bb.split())<=12: return aa,bb
    return None
ar=list(verses.keys()); random.shuffle(ar); bits=[]
for r in ar:
    sp=midsplit(verses[r])
    if sp: bits.append((r,sp[0],sp[1]))
poolE=[b for _,_,b in bits]; e=0
for r,st,an in bits:
    if e>=450: break
    n=len(an.split()); cand=[x for x in poolE if x!=an and abs(len(x.split())-n)<=4]; random.shuffle(cand); ds=[]
    for x in cand:
        if x not in ds: ds.append(x)
        if len(ds)==3: break
    if len(ds)<3: continue
    if add(BCAT.get(meta[r],"Numbers & Genealogies"),"Deacon",f"Complete this verse from {meta[r]}: \"{st} ...\"",[an]+ds,an,r): e+=1
print("(E) mid-split:",e)

# trim to NEED, prefer Deacon balance
random.shuffle(new); by=defaultdict(list)
for q in new: by[q["difficulty"]].append(q)
print("available:",{k:len(v) for k,v in by.items()})
dea=min(len(by["Deacon"]), NEED//2 + 100)
final=by["Deacon"][:dea]; final+=by["Pastor"][:NEED-len(final)]
if len(final)<NEED:
    ex=[q for q in new if q not in final]; random.shuffle(ex); final+=ex[:NEED-len(final)]
final=final[:NEED]
from collections import Counter
print("NEW:",len(final),dict(Counter(q["difficulty"] for q in final)))
comb=v2+final; ns=set(); out=[]
for q in comb:
    n=norm(q["question"])
    if n in ns: continue
    ns.add(n); out.append(q)
json.dump(out,open(f"{M}/manna_questions_v2.json","w"),indent=2,ensure_ascii=False)
print("V2 FILE NOW:",len(out))
print("by difficulty:",dict(Counter(q["difficulty"] for q in out)))
print("by category:",dict(Counter(q["category"] for q in out)))
