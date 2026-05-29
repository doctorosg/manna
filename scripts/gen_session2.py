#!/usr/bin/env python3
"""
Session 2: Mine remaining Lumina data for 3000+ new questions.
New question patterns to avoid duplicating previous generation.
"""
import json, random, hashlib, os, glob, re, math
from collections import Counter, defaultdict
random.seed(20260529)

LUMINA = "/home/claude/lumina-bible/data"

with open("/home/claude/manna/manna_questions.json") as f:
    ALL = json.load(f)
existing = set(q["question"].strip().lower() for q in ALL)
start_count = len(ALL)

def Q(cat,diff,q,opts,cor,exp=""):
    k=q.strip().lower()
    if k not in existing:
        existing.add(k)
        ALL.append({"category":cat,"difficulty":diff,"question":q,"options":opts,"correct":cor,"explanation":exp})

def S(c,ws):
    o=[c]+list(ws[:3]);random.shuffle(o);return o

BOOK_NAMES = {
    "Gen":"Genesis","Exod":"Exodus","Lev":"Leviticus","Num":"Numbers",
    "Deut":"Deuteronomy","Josh":"Joshua","Judg":"Judges","Ruth":"Ruth",
    "1Sam":"1 Samuel","2Sam":"2 Samuel","1Kgs":"1 Kings","2Kgs":"2 Kings",
    "1Chr":"1 Chronicles","2Chr":"2 Chronicles","Ezra":"Ezra","Neh":"Nehemiah",
    "Esth":"Esther","Job":"Job","Ps":"Psalms","Prov":"Proverbs",
    "Eccl":"Ecclesiastes","Song":"Song of Solomon","Isa":"Isaiah",
    "Jer":"Jeremiah","Lam":"Lamentations","Ezek":"Ezekiel","Dan":"Daniel",
    "Hos":"Hosea","Joel":"Joel","Amos":"Amos","Obad":"Obadiah",
    "Jonah":"Jonah","Mic":"Micah","Nah":"Nahum","Hab":"Habakkuk",
    "Zeph":"Zephaniah","Hag":"Haggai","Zech":"Zechariah","Mal":"Malachi",
    "Matt":"Matthew","Mark":"Mark","Luke":"Luke","John":"John",
}
NT_ABBRS = {"Matt","Mark","Luke","John","Acts","Rom","1Cor","2Cor","Gal","Eph",
    "Phil","Col","1Thess","2Thess","1Tim","2Tim","Titus","Phlm","Heb","Jas",
    "1Pet","2Pet","1John","2John","3John","Jude","Rev"}

def bname(ref): return BOOK_NAMES.get(ref.split('.')[0], ref.split('.')[0])
def rread(ref):
    p=ref.split('.');b=BOOK_NAMES.get(p[0],p[0])
    return f"{b} {p[1]}:{p[2]}" if len(p)>=3 else f"{b} {p[1]}" if len(p)>=2 else b
def is_ot(ref): return ref.split('.')[0] not in NT_ABBRS
def chap(ref):
    p=ref.split('.')
    return f"{p[0]}.{p[1]}" if len(p)>=2 else ref

EASY={"Genesis","Exodus","Psalms","Isaiah","Proverbs","Daniel","Jonah"}
MED={"Deuteronomy","1 Samuel","2 Samuel","1 Kings","2 Kings","Jeremiah","Ezekiel","Zechariah","Malachi","Job","Numbers","Leviticus","Joshua","Judges","Ruth","Nehemiah","Esther"}

def diff_b(book):
    if book in EASY: return "Layperson"
    if book in MED: return "Deacon"
    return "Pastor"

def cat_ot(book):
    if book=="Genesis": return "Genesis & Creation"
    if book in ["Exodus","Leviticus","Numbers","Deuteronomy"]: return "Moses & the Exodus"
    if book in ["Joshua","Judges","Ruth"]: return "Battles & Wars"
    if book in ["1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra","Nehemiah","Esther"]: return "Kings & Kingdoms"
    if book in ["Psalms","Proverbs","Job","Ecclesiastes","Song of Solomon"]: return "Psalms & Proverbs"
    if book in ["Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel"]: return "Prophets"
    return "Prophets"

all_ot_books = sorted(set(v for k,v in BOOK_NAMES.items() if k not in NT_ABBRS))

# ============================================================================
# LOAD ALL GOSPEL→OT CONNECTIONS
# ============================================================================
print("Loading Gospel→OT connections...")
gospel_conns = []
gospel_stats = defaultdict(lambda: defaultdict(int))  # gospel -> ot_book -> count

for gospel in ['matthew','mark','luke','john']:
    with open(f"{LUMINA}/backups/{gospel}-links-backup.json") as f:
        data = json.load(f)['entries']
    for ref, entry in data.items():
        kjv = entry.get('kjv_text','')
        for anchor in entry.get('anchors',[]):
            at = anchor.get('anchor','')
            for target in anchor.get('targets',[]):
                ts = target.get('start','')
                reason = target.get('reason','')
                if ts and is_ot(ts) and at and len(at)>=5:
                    ob = bname(ts)
                    gospel_conns.append({
                        'src':ref,'kjv':kjv,'anchor':at,'ot_ref':ts,
                        'ot_book':ob,'reason':reason or '','gospel':gospel.title()
                    })
                    gospel_stats[gospel.title()][ob] += 1

print(f"Total: {len(gospel_conns)} connections")
random.shuffle(gospel_conns)

# Track already-used question keys
used_keys = set()

# ============================================================================
# PATTERN 1: "In [Gospel], which OT book is referenced through '[anchor]'?"
# Different phrasing from previous "echoes which OT book"
# ============================================================================
p1 = 0
for conn in gospel_conns:
    if p1 >= 700: break
    key = f"p1-{conn['src']}-{conn['ot_ref']}"
    if key in used_keys: continue
    a = conn['anchor']
    if len(a) < 8 or len(a) > 90: continue
    
    wrongs = [b for b in all_ot_books if b != conn['ot_book']]
    random.shuffle(wrongs)
    used_keys.add(key)
    
    a_short = a[:75]+'...' if len(a)>75 else a
    Q("Words of Jesus & OT Roots", diff_b(conn['ot_book']),
      f"In {conn['gospel']}'s Gospel, '{a_short}' references which OT book?",
      S(conn['ot_book'], wrongs[:3]), conn['ot_book'],
      conn['reason'][:100] if conn['reason'] else "")
    p1 += 1
print(f"  Pattern 1 (Gospel→OT book, new phrasing): {p1}")

# ============================================================================
# PATTERN 2: "Which Gospel contains a reference to [OT passage]?"
# ============================================================================
p2 = 0
ot_to_gospels = defaultdict(set)
for c in gospel_conns:
    ot_to_gospels[c['ot_ref']].add(c['gospel'])

gospels_list = ["Matthew","Mark","Luke","John"]
for conn in gospel_conns:
    if p2 >= 500: break
    key = f"p2-{conn['ot_ref']}-{conn['gospel']}"
    if key in used_keys: continue
    if not conn['reason'] or len(conn['reason']) < 25: continue
    
    correct = conn['gospel']
    # Only use if this OT ref is NOT in all 4 gospels (otherwise too easy)
    if len(ot_to_gospels[conn['ot_ref']]) >= 4: continue
    
    wrongs = [g for g in gospels_list if g != correct and g not in ot_to_gospels[conn['ot_ref']]]
    if len(wrongs) < 1:
        wrongs = [g for g in gospels_list if g != correct]
    random.shuffle(wrongs)
    
    used_keys.add(key)
    ot_r = rread(conn['ot_ref'])
    Q("Words of Jesus & OT Roots", "Deacon" if conn['ot_book'] in EASY else "Pastor",
      f"Which Gospel contains a reference to {ot_r}?",
      S(correct, wrongs[:3]), correct, conn['reason'][:100])
    p2 += 1
print(f"  Pattern 2 (which Gospel references OT): {p2}")

# ============================================================================
# PATTERN 3: "What OT chapter is most connected to [Gospel chapter]?"
# Build chapter-level connection counts
# ============================================================================
chap_connections = defaultdict(lambda: defaultdict(int))
for conn in gospel_conns:
    src_ch = chap(conn['src'])
    ot_ch = chap(conn['ot_ref'])
    chap_connections[src_ch][ot_ch] += 1

p3 = 0
for src_ch, ot_chs in chap_connections.items():
    if p3 >= 300: break
    if not ot_chs: continue
    
    top_ot = max(ot_chs, key=ot_chs.get)
    top_count = ot_chs[top_ot]
    if top_count < 3: continue  # only strong connections
    
    key = f"p3-{src_ch}"
    if key in used_keys: continue
    used_keys.add(key)
    
    top_book = bname(top_ot)
    src_readable = rread(src_ch)
    
    wrongs = [bname(ch) for ch in list(ot_chs.keys()) if ch != top_ot and bname(ch) != top_book]
    if len(wrongs) < 3:
        wrongs += [b for b in all_ot_books if b != top_book]
    random.shuffle(wrongs)
    wrongs = list(dict.fromkeys(wrongs))[:3]  # unique
    
    Q("Prophecy & Fulfillment", "Deacon" if top_book in EASY else "Pastor",
      f"Which OT book has the strongest connection to {src_readable}?",
      S(top_book, wrongs[:3]), top_book,
      f"{top_count} cross-references to {bname(top_ot)}")
    p3 += 1
print(f"  Pattern 3 (strongest OT connection): {p3}")

# ============================================================================
# PATTERN 4: "What is the OT background behind [KJV text snippet]?"
# Use the actual KJV text as the question
# ============================================================================
p4 = 0
for conn in gospel_conns:
    if p4 >= 500: break
    kjv = conn['kjv']
    if not kjv or len(kjv) < 30: continue
    if not conn['reason'] or len(conn['reason']) < 30: continue
    
    key = f"p4-{conn['src']}"
    if key in used_keys: continue
    used_keys.add(key)
    
    kjv_short = kjv[:100]+'...' if len(kjv)>100 else kjv
    wrongs = [b for b in all_ot_books if b != conn['ot_book']]
    random.shuffle(wrongs)
    
    Q("Words of Jesus & OT Roots", diff_b(conn['ot_book']),
      f"What OT book provides background for: '{kjv_short}' ({rread(conn['src'])})?",
      S(conn['ot_book'], wrongs[:3]), conn['ot_book'],
      conn['reason'][:100])
    p4 += 1
print(f"  Pattern 4 (KJV text→OT background): {p4}")

# ============================================================================
# PATTERN 5: TSK OT-to-OT connections with new question types
# "Which book shares a thematic connection with [source]?"
# ============================================================================
print("\nMining OT cross-references...")
tsk_files = sorted(glob.glob("/home/claude/lumina-bible/ot_links_output/*.json"))
random.shuffle(tsk_files)

p5 = 0
for fpath in tsk_files:
    if p5 >= 800: break
    try:
        with open(fpath) as f:
            data = json.load(f)
        if not isinstance(data, list): continue
        
        good = [e for e in data if isinstance(e,dict) and e.get('reason') and len(e['reason'])>30 and e.get('anchor') and len(e['anchor'])>=6]
        random.shuffle(good)
        
        for entry in good[:3]:
            src = entry.get('source_ref','')
            anchor = entry.get('anchor','')
            target = entry.get('target_start','')
            reason = entry.get('reason','')
            
            if not src or not target: continue
            sb = bname(src); tb = bname(target)
            if sb == tb: continue
            
            key = f"p5-{src}-{target}"
            if key in used_keys: continue
            used_keys.add(key)
            
            wrongs = [b for b in all_ot_books if b != tb]
            random.shuffle(wrongs)
            
            anchor_s = anchor[:65]+'...' if len(anchor)>65 else anchor
            
            # Alternate question phrasings
            templates = [
                f"The concept '{anchor_s}' in {rread(src)} connects to which OT book?",
                f"Which book shares a connection with {rread(src)} regarding '{anchor_s}'?",
                f"{rread(src)} references a theme also found in which book?",
            ]
            template = templates[p5 % len(templates)]
            
            Q(cat_ot(sb), diff_b(tb), template,
              S(tb, wrongs[:3]), tb, reason[:100])
            p5 += 1
    except: pass
print(f"  Pattern 5 (OT-to-OT themed): {p5}")

# ============================================================================
# PATTERN 6: "What reason connects [source] to [target]?"
# Focus on rich reasons we haven't used
# ============================================================================
p6 = 0
reason_pool = []
for fpath in tsk_files[:500]:
    try:
        with open(fpath) as f: data = json.load(f)
        for e in data:
            if isinstance(e,dict) and e.get('reason') and len(e['reason'])>50:
                reason_pool.append(e)
    except: pass

random.shuffle(reason_pool)
all_reasons_text = [r['reason'][:120] for r in reason_pool[:2000]]

for entry in reason_pool:
    if p6 >= 400: break
    reason = entry['reason'][:120]
    if len(reason) < 50: continue
    
    key = f"p6-{entry.get('source_ref','')}-{entry.get('target_start','')}"
    if key in used_keys: continue
    used_keys.add(key)
    
    src_r = rread(entry.get('source_ref',''))
    tgt_r = rread(entry.get('target_start',''))
    
    wrong_reasons = random.sample([r for r in all_reasons_text if r != reason], min(10, len(all_reasons_text)-1))
    if len(wrong_reasons) < 3: continue
    
    if len(reason) > 120:
        reason = reason[:120].rsplit(' ',1)[0] + '...'
    
    sb = bname(entry.get('source_ref',''))
    Q(cat_ot(sb), "Pastor",
      f"What connects {src_r} to {tgt_r}?",
      S(reason, wrong_reasons[:3]), reason)
    p6 += 1
print(f"  Pattern 6 (reason-based): {p6}")

# ============================================================================
# PATTERN 7: Gospel stats questions
# "Which OT book does Matthew reference most?"
# ============================================================================
p7 = 0
for gospel, book_counts in gospel_stats.items():
    if not book_counts: continue
    top_book = max(book_counts, key=book_counts.get)
    top_count = book_counts[top_book]
    
    # Top 3
    sorted_books = sorted(book_counts.items(), key=lambda x: -x[1])
    
    wrongs = [b for b,c in sorted_books[3:8] if b != top_book]
    random.shuffle(wrongs)
    if len(wrongs) < 3:
        wrongs += [b for b in all_ot_books if b != top_book and b not in [x[0] for x in sorted_books[:3]]]
    
    Q("Words of Jesus & OT Roots", "Pastor",
      f"Which OT book does {gospel}'s Gospel reference most often?",
      S(top_book, wrongs[:3]), top_book,
      f"{top_count} connections")
    p7 += 1
    
    # Second most
    if len(sorted_books) >= 2:
        second = sorted_books[1][0]
        wrongs2 = [b for b,c in sorted_books[3:8] if b != second]
        random.shuffle(wrongs2)
        if len(wrongs2) >= 3:
            Q("Words of Jesus & OT Roots", "Pastor",
              f"After {top_book}, which OT book does {gospel} reference most?",
              S(second, wrongs2[:3]), second)
            p7 += 1

print(f"  Pattern 7 (Gospel stats): {p7}")

# ============================================================================
# PATTERN 8: Layperson-friendly cross-ref questions
# Focus on famous passages everyone knows
# ============================================================================
famous_connections = [
    # (Gospel ref pattern, OT book, easy description, difficulty)
    ("Matt.1","Genesis","Jesus' genealogy traces back to Abraham in Genesis","Layperson"),
    ("Matt.2","Micah","The wise men searched for Jesus born in Bethlehem — prophesied in Micah","Layperson"),
    ("Matt.3","Isaiah","John the Baptist fulfilled Isaiah's prophecy of 'a voice in the wilderness'","Layperson"),
    ("Matt.4","Deuteronomy","Jesus quoted Deuteronomy three times when Satan tempted Him","Layperson"),
    ("Matt.5","Exodus","The Sermon on the Mount echoes the giving of the Law on Mount Sinai","Deacon"),
    ("Matt.12","Jonah","Jesus compared His death and resurrection to Jonah's three days in the fish","Layperson"),
    ("Matt.21","Zechariah","Jesus rode a donkey into Jerusalem — fulfilling Zechariah's prophecy","Layperson"),
    ("Matt.26","Exodus","The Last Supper was a Passover meal — connecting to Exodus 12","Layperson"),
    ("Matt.27","Psalms","Jesus' words on the cross — 'My God, why have you forsaken me' — are from Psalm 22","Deacon"),
    ("Mark.1","Isaiah","Mark begins by quoting Isaiah about preparing the Lord's way","Deacon"),
    ("Mark.12","Deuteronomy","Jesus quotes the Shema from Deuteronomy 6 as the greatest commandment","Deacon"),
    ("Mark.14","Zechariah","Jesus predicted the disciples would scatter — from Zechariah 13","Deacon"),
    ("Luke.1","1 Samuel","Mary's song (Magnificat) echoes Hannah's prayer in 1 Samuel","Deacon"),
    ("Luke.2","Leviticus","Jesus was presented at the Temple following Leviticus purification laws","Deacon"),
    ("Luke.4","Isaiah","Jesus read from Isaiah 61 in the Nazareth synagogue — 'The Spirit of the Lord is upon me'","Layperson"),
    ("Luke.10","Leviticus","The Good Samaritan illustrates 'love your neighbor' from Leviticus 19","Deacon"),
    ("Luke.22","Jeremiah","The 'new covenant' Jesus announced at the Last Supper was prophesied in Jeremiah 31","Deacon"),
    ("Luke.24","Psalms","The risen Jesus explained how the Psalms pointed to Him","Deacon"),
    ("John.1","Genesis","'In the beginning was the Word' echoes 'In the beginning God created' from Genesis 1","Layperson"),
    ("John.3","Numbers","Jesus compared being 'lifted up' to Moses lifting the bronze serpent in Numbers 21","Deacon"),
    ("John.6","Exodus","'I am the bread of life' connects to God providing manna in Exodus 16","Layperson"),
    ("John.10","Psalms","'I am the good shepherd' echoes Psalm 23 — 'The Lord is my shepherd'","Layperson"),
    ("John.12","Isaiah","John quotes Isaiah 53 about why Israel didn't believe Jesus' signs","Deacon"),
    ("John.15","Isaiah","'I am the true vine' echoes Isaiah 5 where Israel is God's vineyard","Deacon"),
    ("John.19","Psalms","Soldiers casting lots for Jesus' clothes fulfilled Psalm 22","Deacon"),
    ("John.19","Exodus","'Not a bone of Him shall be broken' — the Passover lamb rule from Exodus 12","Deacon"),
]

p8 = 0
for src_pattern, ot_book, description, diff in famous_connections:
    wrongs = [b for b in all_ot_books if b != ot_book]
    random.shuffle(wrongs)
    
    # Question from description
    Q("Prophecy & Fulfillment" if diff == "Layperson" else "Words of Jesus & OT Roots", diff,
      f"{description}. Which OT book is this connection from?",
      S(ot_book, wrongs[:3]), ot_book)
    
    # Reverse: given the OT book, which Gospel passage?
    gospel_name = {"Matt":"Matthew","Mark":"Mark","Luke":"Luke","John":"John"}[src_pattern.split('.')[0]]
    ch = src_pattern.split('.')[1]
    wrongs_g = [f"{g} {ch}" for g in ["Matthew","Mark","Luke","John"] if g != gospel_name]
    random.shuffle(wrongs_g)
    Q("Prophecy & Fulfillment", diff,
      f"Which Gospel chapter contains the connection to {ot_book}: '{description[:80]}'?",
      S(f"{gospel_name} {ch}", wrongs_g[:3]), f"{gospel_name} {ch}")
    p8 += 2
print(f"  Pattern 8 (famous connections): {p8}")

# ============================================================================
# PATTERN 9: Church Fathers — new batch (500 Deacon/Pastor)
# ============================================================================
print("\nMining Church Fathers...")
with open(f"{LUMINA}/commentaries/catena-aurea-project/catena_aurea_graph.json") as f:
    catena = json.load(f)

nodes_by_id = {n['id']:n for n in catena['nodes']}
narratives = [n for n in catena['nodes'] if n['type']=='Patristic_Narrative']
sources = [n for n in catena['nodes'] if n['type']=='Patristic_Source']
source_names = [s['name'] for s in sources]

narrative_to_source = {}
verse_to_narratives = {}
for edge in catena['edges']:
    sn = nodes_by_id.get(edge['source'])
    tn = nodes_by_id.get(edge['target'])
    if not sn or not tn: continue
    if sn['type']=='Patristic_Source' and tn['type']=='Patristic_Narrative':
        narrative_to_source[tn['id']] = sn['id']
    if sn['type']=='Gospel_Verse' and tn['type']=='Patristic_Narrative':
        verse_to_narratives.setdefault(sn['id'],[]).append(tn['id'])

# Find narratives NOT yet used (check by text uniqueness)
existing_father_texts = set()
for q in ALL:
    if "Church Father" in q['question']:
        # Extract the quoted text
        m = re.search(r"'([^']{20,})'", q['question'])
        if m: existing_father_texts.add(m.group(1)[:50])

random.shuffle(narratives)
p9 = 0
for narr in narratives:
    if p9 >= 500: break
    text = narr.get('properties',{}).get('text','')
    if not text or len(text)<35 or len(text)>220: continue
    
    text_key = text[:50]
    if text_key in existing_father_texts: continue
    existing_father_texts.add(text_key)
    
    sid = narrative_to_source.get(narr['id'])
    if not sid: continue
    snode = nodes_by_id.get(sid)
    if not snode: continue
    father = snode['name']
    
    vid = None
    for v, nids in verse_to_narratives.items():
        if narr['id'] in nids: vid = v; break
    vname = nodes_by_id.get(vid,{}).get('name','') if vid else ''
    if not vname: continue
    
    tc = text.strip()
    if len(tc)>120: tc = tc[:120].rsplit(' ',1)[0]+'...'
    
    diff = "Deacon" if p9 % 2 == 0 else "Pastor"
    wrongs = [n for n in source_names if n != father]
    random.shuffle(wrongs)
    
    if len(wrongs) >= 3:
        Q("Life of Jesus", diff,
          f"On {vname}, which Church Father wrote: '{tc}'?",
          S(father, wrongs[:3]), father)
        p9 += 1
print(f"  Pattern 9 (Church Fathers new): {p9}")

# ============================================================================
# PATTERN 10: "True or false" about cross-references
# ============================================================================
p10 = 0
tf_questions = []

# Build some true/false from gospel stats
for gospel, counts in gospel_stats.items():
    top = max(counts, key=counts.get)
    bottom_books = [b for b,c in sorted(counts.items(), key=lambda x: x[1])[:5]]
    
    # True: "[Gospel] references [top book] more than any other OT book"
    tf_questions.append(("Words of Jesus & OT Roots", "Deacon",
        f"True or false: {gospel}'s Gospel references {top} more than any other OT book.",
        f"True — {top} has {counts[top]} references in {gospel}",
        f"False — {gospel} references Psalms most",
        f"False — {gospel} references Genesis most",
        f"False — {gospel} references Exodus most"))
    
    # False: "[Gospel] never references [bottom book]"  
    if bottom_books:
        bb = random.choice(bottom_books)
        tf_questions.append(("Words of Jesus & OT Roots", "Pastor",
            f"True or false: {gospel}'s Gospel never references the book of {bb}.",
            f"False — it references {bb} at least {counts[bb]} times",
            "True — there are no connections",
            "True — only indirectly",
            "False — but only once"))

for cat,diff,q,c1,c2,c3,c4 in tf_questions:
    Q(cat,diff,q,S(c1,[c2,c3,c4]),c1)
    p10 += 1
print(f"  Pattern 10 (T/F cross-refs): {p10}")

# ============================================================================
# FINALIZE
# ============================================================================
for i, q in enumerate(ALL):
    q["id"] = hashlib.md5(f"{q['category']}-{q['difficulty']}-{q['question'][:50]}-{i}".encode()).hexdigest()[:12]

dc = Counter(q["difficulty"] for q in ALL)
cc = Counter(q["category"] for q in ALL)
new_count = len(ALL) - start_count

print(f"\n{'='*60}")
print(f"NEW QUESTIONS: {new_count}")
print(f"GRAND TOTAL: {len(ALL)} questions")
print(f"  Layperson: {dc['Layperson']}  Deacon: {dc['Deacon']}  Pastor: {dc['Pastor']}")
print(f"{'='*60}")
for cat in sorted(cc.keys()):
    dd = Counter(q["difficulty"] for q in ALL if q["category"]==cat)
    print(f"  {cat}: {cc[cat]:4d} (L:{dd.get('Layperson',0):3d} D:{dd.get('Deacon',0):3d} P:{dd.get('Pastor',0):3d})")

with open("/home/claude/manna/manna_questions.json","w") as f:
    json.dump(ALL, f, indent=2)
import shutil
shutil.copy("/home/claude/manna/manna_questions.json","/home/claude/manna/Manna/Resources/manna_questions.json")
print(f"\nSaved: {os.path.getsize('/home/claude/manna/manna_questions.json')/1024:.0f} KB")
