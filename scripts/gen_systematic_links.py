#!/usr/bin/env python3
"""
Systematic mining of Lumina cross-references.
Target: 2,000-3,000 questions from Gospel→OT + OT cross-refs + Church Fathers.
"""
import json, random, hashlib, os, glob, re
random.seed(9999)

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
    "Acts":"Acts","Rom":"Romans","1Cor":"1 Corinthians","2Cor":"2 Corinthians",
    "Gal":"Galatians","Eph":"Ephesians","Phil":"Philippians","Col":"Colossians",
    "1Thess":"1 Thessalonians","2Thess":"2 Thessalonians",
    "1Tim":"1 Timothy","2Tim":"2 Timothy","Titus":"Titus","Phlm":"Philemon",
    "Heb":"Hebrews","Jas":"James","1Pet":"1 Peter","2Pet":"2 Peter",
    "1John":"1 John","2John":"2 John","3John":"3 John","Jude":"Jude","Rev":"Revelation",
}
NT_ABBRS = {"Matt","Mark","Luke","John","Acts","Rom","1Cor","2Cor","Gal","Eph",
    "Phil","Col","1Thess","2Thess","1Tim","2Tim","Titus","Phlm","Heb","Jas",
    "1Pet","2Pet","1John","2John","3John","Jude","Rev"}

def bname(ref): return BOOK_NAMES.get(ref.split('.')[0], ref.split('.')[0])
def rread(ref):
    p=ref.split('.');b=BOOK_NAMES.get(p[0],p[0])
    return f"{b} {p[1]}:{p[2]}" if len(p)>=3 else f"{b} {p[1]}" if len(p)>=2 else b
def is_ot(ref): return ref.split('.')[0] not in NT_ABBRS

EASY_BOOKS = {"Genesis","Exodus","Psalms","Isaiah","Proverbs","Daniel","Jonah"}
MED_BOOKS = {"Deuteronomy","1 Samuel","2 Samuel","1 Kings","2 Kings","Jeremiah","Ezekiel","Zechariah","Malachi","Job","Numbers","Leviticus","Joshua","Judges","Ruth","Nehemiah","Esther"}
all_ot_books = sorted(set(BOOK_NAMES[k] for k in BOOK_NAMES if k not in NT_ABBRS))

def diff_for_book(book):
    if book in EASY_BOOKS: return "Layperson"
    if book in MED_BOOKS: return "Deacon"
    return "Pastor"

def cat_for_ot_book(book):
    if book == "Genesis": return "Genesis & Creation"
    if book in ["Exodus","Leviticus","Numbers","Deuteronomy"]: return "Moses & the Exodus"
    if book in ["Joshua","Judges","Ruth"]: return "Battles & Wars"
    if book in ["1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles"]: return "Kings & Kingdoms"
    if book in ["Ezra","Nehemiah","Esther"]: return "Kings & Kingdoms"
    if book in ["Psalms","Proverbs","Job","Ecclesiastes","Song of Solomon"]: return "Psalms & Proverbs"
    if book in ["Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel"]: return "Prophets"
    return "Prophets"  # minor prophets

# ============================================================================
# PART 1: ALL GOSPEL→OT LINKS (22,429 connections)
# ============================================================================
print("Loading all Gospel→OT connections...")

all_gospel_conns = []
for gospel in ['matthew','mark','luke','john']:
    with open(f"{LUMINA}/backups/{gospel}-links-backup.json") as f:
        data = json.load(f)['entries']
    for ref, entry in data.items():
        kjv = entry.get('kjv_text','')
        for anchor in entry.get('anchors',[]):
            anchor_text = anchor.get('anchor','')
            for target in anchor.get('targets',[]):
                t_start = target.get('start','')
                reason = target.get('reason','')
                if t_start and is_ot(t_start) and anchor_text and len(anchor_text) >= 5:
                    all_gospel_conns.append({
                        'src': ref, 'kjv': kjv, 'anchor': anchor_text,
                        'ot_ref': t_start, 'ot_book': bname(t_start),
                        'reason': reason or '', 'gospel': gospel.title()
                    })

print(f"Total Gospel→OT connections: {len(all_gospel_conns)}")
random.shuffle(all_gospel_conns)

# Track used source refs to avoid too many from same verse
used_src_type = {}  # (src, type) -> count

# TYPE A: "Which OT book does this Gospel phrase connect to?" 
type_a = 0
for conn in all_gospel_conns:
    if type_a >= 800: break
    key = (conn['src'], 'A')
    if used_src_type.get(key, 0) >= 1: continue
    
    anchor = conn['anchor']
    if len(anchor) < 8 or len(anchor) > 100: continue
    
    ot_book = conn['ot_book']
    wrongs = [b for b in all_ot_books if b != ot_book]
    random.shuffle(wrongs)
    
    diff = diff_for_book(ot_book)
    cat = "Prophecy & Fulfillment" if conn['gospel'] in ['Matthew','Luke'] and ot_book in ["Isaiah","Jeremiah","Zechariah","Micah","Malachi","Daniel"] else "Words of Jesus & OT Roots"
    
    anchor_short = anchor[:75] + '...' if len(anchor) > 75 else anchor
    Q(cat, diff,
      f"The phrase '{anchor_short}' in {rread(conn['src'])} echoes which OT book?",
      S(ot_book, wrongs[:3]), ot_book, conn['reason'][:100] if conn['reason'] else "")
    used_src_type[key] = used_src_type.get(key, 0) + 1
    type_a += 1

print(f"  Type A (which OT book): {type_a}")

# TYPE B: "Which Gospel references [OT passage]?"
type_b = 0
all_gospel_refs = list(set(rread(c['src']) for c in all_gospel_conns))
for conn in all_gospel_conns:
    if type_b >= 600: break
    key = (conn['ot_ref'], 'B')
    if used_src_type.get(key, 0) >= 1: continue
    if not conn['reason'] or len(conn['reason']) < 20: continue
    
    src_readable = rread(conn['src'])
    ot_readable = rread(conn['ot_ref'])
    wrongs = [r for r in all_gospel_refs if r != src_readable]
    random.shuffle(wrongs)
    
    diff = "Deacon" if conn['ot_book'] in EASY_BOOKS else "Pastor"
    Q("Words of Jesus & OT Roots", diff,
      f"Which Gospel verse draws on {ot_readable} ({conn['ot_book']})?",
      S(src_readable, wrongs[:3]), src_readable, conn['reason'][:100])
    used_src_type[key] = used_src_type.get(key, 0) + 1
    type_b += 1

print(f"  Type B (which Gospel): {type_b}")

# TYPE C: Connection type (QUOTE/ALLUSION/TYPE/THEME/FULFILLMENT)
conn_types = {
    "QUOTE": "A direct quotation from the Old Testament",
    "ALLUSION": "An allusion or echo of an OT passage",
    "TYPE": "A typological connection — the OT event foreshadows the NT",
    "FULFILLMENT": "A prophetic fulfillment — what was predicted came true",
    "THEMATIC": "A shared theological theme between the passages",
}
type_labels = list(conn_types.values())

type_c = 0
for conn in all_gospel_conns:
    if type_c >= 500: break
    reason = conn['reason'].upper()
    if not conn['reason'] or len(conn['reason']) < 30: continue
    
    key = (conn['src'] + conn['ot_ref'], 'C')
    if used_src_type.get(key, 0) >= 1: continue
    
    detected = None
    for keyword, label in conn_types.items():
        if keyword in reason:
            detected = label; break
    if not detected: detected = "A shared theological theme between the passages"
    
    wrongs = [l for l in type_labels if l != detected]
    random.shuffle(wrongs)
    
    anchor = conn['anchor'][:60] + '...' if len(conn['anchor']) > 60 else conn['anchor']
    if len(anchor) < 8: continue
    
    Q("Prophecy & Fulfillment", "Pastor",
      f"What type of link connects '{anchor}' ({rread(conn['src'])}) to {conn['ot_book']}?",
      S(detected, wrongs[:3]), detected, conn['reason'][:100])
    used_src_type[key] = used_src_type.get(key, 0) + 1
    type_c += 1

print(f"  Type C (connection type): {type_c}")

# TYPE D: "Why are these passages connected?" (reason-based)
type_d = 0
all_reasons = [c['reason'][:120] for c in all_gospel_conns if c['reason'] and len(c['reason']) > 40]
for conn in all_gospel_conns:
    if type_d >= 400: break
    if not conn['reason'] or len(conn['reason']) < 50: continue
    
    key = (conn['src'] + conn['ot_ref'], 'D')
    if used_src_type.get(key, 0) >= 1: continue
    
    correct_reason = conn['reason'][:120]
    if len(conn['reason']) > 120:
        correct_reason = conn['reason'][:120].rsplit(' ', 1)[0] + '...'
    
    wrong_reasons = random.sample([r for r in all_reasons if r != correct_reason], min(10, len(all_reasons)-1))
    if len(wrong_reasons) < 3: continue
    
    Q("Words of Jesus & OT Roots", "Deacon" if conn['ot_book'] in EASY_BOOKS else "Pastor",
      f"Why is {rread(conn['src'])} linked to {rread(conn['ot_ref'])}?",
      S(correct_reason, wrong_reasons[:3]), correct_reason)
    used_src_type[key] = used_src_type.get(key, 0) + 1
    type_d += 1

print(f"  Type D (why connected): {type_d}")

# TYPE E: "Which prophet is referenced in this Gospel passage?"
prophets = ["Isaiah","Jeremiah","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah",
            "Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi"]
type_e = 0
prophet_conns = [c for c in all_gospel_conns if c['ot_book'] in prophets]
random.shuffle(prophet_conns)
for conn in prophet_conns:
    if type_e >= 300: break
    key = (conn['src'], 'E')
    if used_src_type.get(key, 0) >= 1: continue
    
    anchor = conn['anchor']
    if len(anchor) < 10: continue
    anchor_short = anchor[:70] + '...' if len(anchor) > 70 else anchor
    
    wrongs = [p for p in prophets if p != conn['ot_book']]
    random.shuffle(wrongs)
    
    diff = "Deacon" if conn['ot_book'] in ["Isaiah","Jeremiah","Daniel","Jonah","Zechariah","Malachi"] else "Pastor"
    Q("Prophets", diff,
      f"Which prophet is echoed by '{anchor_short}' in {rread(conn['src'])}?",
      S(conn['ot_book'], wrongs[:3]), conn['ot_book'])
    used_src_type[key] = used_src_type.get(key, 0) + 1
    type_e += 1

print(f"  Type E (which prophet): {type_e}")

gospel_total = type_a + type_b + type_c + type_d + type_e
print(f"  GOSPEL SUBTOTAL: {gospel_total}")

# ============================================================================
# PART 2: OT CROSS-REFERENCES (remaining ~600 files)
# ============================================================================
print("\nLoading OT cross-references...")

tsk_files = sorted(glob.glob("/home/claude/lumina-bible/ot_links_output/*.json"))
random.shuffle(tsk_files)

ot_xref_count = 0
for fpath in tsk_files:
    if ot_xref_count >= 600: break
    try:
        with open(fpath) as f:
            data = json.load(f)
        if not isinstance(data, list): continue
        
        good = [e for e in data if isinstance(e, dict) and e.get('reason') and len(e['reason']) > 25 and e.get('anchor') and len(e['anchor']) >= 6]
        good.sort(key=lambda x: len(x['reason']), reverse=True)
        
        for entry in good[:2]:
            src = entry.get('source_ref','')
            anchor = entry.get('anchor','')
            target = entry.get('target_start','')
            reason = entry.get('reason','')
            
            if not src or not target: continue
            
            src_book = bname(src)
            tgt_book = bname(target)
            if src_book == tgt_book: continue
            
            wrongs = [b for b in all_ot_books if b != tgt_book]
            random.shuffle(wrongs)
            
            cat = cat_for_ot_book(src_book)
            diff = diff_for_book(tgt_book)
            anchor_short = anchor[:70] + '...' if len(anchor) > 70 else anchor
            
            Q(cat, diff,
              f"'{anchor_short}' ({rread(src)}) cross-references which book?",
              S(tgt_book, wrongs[:3]), tgt_book, reason[:100])
            ot_xref_count += 1
    except: pass

print(f"  OT cross-ref questions: {ot_xref_count}")

# ============================================================================
# PART 3: CHURCH FATHERS (500 at Deacon/Pastor)
# ============================================================================
print("\nLoading Church Father commentaries...")

with open(f"{LUMINA}/commentaries/catena-aurea-project/catena_aurea_graph.json") as f:
    catena = json.load(f)

nodes_by_id = {n['id']: n for n in catena['nodes']}
narratives = [n for n in catena['nodes'] if n['type'] == 'Patristic_Narrative']
sources = [n for n in catena['nodes'] if n['type'] == 'Patristic_Source']
source_names = [s['name'] for s in sources]

# Build maps
verse_to_narratives = {}
narrative_to_source = {}
for edge in catena['edges']:
    src_n = nodes_by_id.get(edge['source'])
    tgt_n = nodes_by_id.get(edge['target'])
    if not src_n or not tgt_n: continue
    if src_n['type'] == 'Gospel_Verse' and tgt_n['type'] == 'Patristic_Narrative':
        verse_to_narratives.setdefault(src_n['id'], []).append(tgt_n['id'])
    if src_n['type'] == 'Patristic_Source' and tgt_n['type'] == 'Patristic_Narrative':
        narrative_to_source[tgt_n['id']] = src_n['id']

# Filter narratives we haven't used yet
used_narr_ids = set()
for q in ALL:
    if "Church Father" in q.get('question','') or "wrote about" in q.get('question',''):
        # Mark as used (approximate)
        pass

random.shuffle(narratives)
father_count = 0

for narr in narratives:
    if father_count >= 500: break
    
    text = narr.get('properties', {}).get('text', '')
    if not text or len(text) < 30 or len(text) > 250: continue
    
    source_id = narrative_to_source.get(narr['id'])
    if not source_id: continue
    source_node = nodes_by_id.get(source_id)
    if not source_node: continue
    father = source_node['name']
    
    # Find verse
    verse_id = None
    for vid, nids in verse_to_narratives.items():
        if narr['id'] in nids:
            verse_id = vid; break
    verse_name = nodes_by_id.get(verse_id, {}).get('name', '') if verse_id else ''
    if not verse_name: continue
    
    text_clean = text.strip()
    if len(text_clean) > 130:
        text_clean = text_clean[:130].rsplit(' ', 1)[0] + '...'
    
    # Alternate between Deacon and Pastor
    diff = "Deacon" if father_count % 3 == 0 else "Pastor"
    
    wrongs = [n for n in source_names if n != father]
    random.shuffle(wrongs)
    
    if len(wrongs) >= 3:
        Q("Life of Jesus", diff,
          f"Which Church Father commented on {verse_name}: '{text_clean}'?",
          S(father, wrongs[:3]), father)
        father_count += 1

print(f"  Church Father questions: {father_count}")

# ============================================================================
# FINALIZE
# ============================================================================
for i, q in enumerate(ALL):
    q["id"] = hashlib.md5(f"{q['category']}-{q['difficulty']}-{q['question'][:50]}-{i}".encode()).hexdigest()[:12]

from collections import Counter
dc = Counter(q["difficulty"] for q in ALL)
cc = Counter(q["category"] for q in ALL)
new_count = len(ALL) - start_count

print(f"\n{'='*60}")
print(f"NEW QUESTIONS: {new_count}")
print(f"GRAND TOTAL: {len(ALL)} questions")
print(f"  Layperson: {dc['Layperson']}  Deacon: {dc['Deacon']}  Pastor: {dc['Pastor']}")
print(f"{'='*60}")
for cat in sorted(cc.keys()):
    dd = Counter(q["difficulty"] for q in ALL if q["category"] == cat)
    print(f"  {cat}: {cc[cat]:4d} (L:{dd.get('Layperson',0):3d} D:{dd.get('Deacon',0):3d} P:{dd.get('Pastor',0):3d})")

with open("/home/claude/manna/manna_questions.json","w") as f:
    json.dump(ALL, f, indent=2)
import shutil
shutil.copy("/home/claude/manna/manna_questions.json","/home/claude/manna/Manna/Resources/manna_questions.json")
print(f"\nSaved: {os.path.getsize('/home/claude/manna/manna_questions.json')/1024:.0f} KB")
