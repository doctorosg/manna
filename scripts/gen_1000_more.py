#!/usr/bin/env python3
"""Generate 1000+ more questions from untapped Lumina data."""
import json, random, hashlib, os, glob, re
random.seed(5050)

LUMINA = "/home/claude/lumina-bible/data"

with open("/home/claude/manna/manna_questions.json") as f:
    ALL = json.load(f)
existing = set(q["question"].strip().lower() for q in ALL)
start = len(ALL)

def Q(cat,diff,q,opts,cor,exp=""):
    k=q.strip().lower()
    if k not in existing:
        existing.add(k)
        ALL.append({"category":cat,"difficulty":diff,"question":q,"options":opts,"correct":cor,"explanation":exp})

def S(c,ws):
    o=[c]+list(ws[:3]);random.shuffle(o);return o

# ============================================================================
# 1. CATENA AUREA — Church Father Commentary Questions
# ============================================================================
with open(f"{LUMINA}/commentaries/catena-aurea-project/catena_aurea_graph.json") as f:
    catena = json.load(f)

nodes_by_id = {n['id']: n for n in catena['nodes']}
narratives = [n for n in catena['nodes'] if n['type'] == 'Patristic_Narrative']
verses = [n for n in catena['nodes'] if n['type'] == 'Gospel_Verse']
sources = [n for n in catena['nodes'] if n['type'] == 'Patristic_Source']

# Build edge maps
verse_to_narratives = {}  # verse_id -> [narrative_ids]
narrative_to_source = {}  # narrative_id -> source_id
for edge in catena['edges']:
    src_node = nodes_by_id.get(edge['source'])
    tgt_node = nodes_by_id.get(edge['target'])
    if not src_node or not tgt_node:
        continue
    if src_node['type'] == 'Gospel_Verse' and tgt_node['type'] == 'Patristic_Narrative':
        verse_to_narratives.setdefault(src_node['id'], []).append(tgt_node['id'])
    if src_node['type'] == 'Patristic_Source' and tgt_node['type'] == 'Patristic_Narrative':
        narrative_to_source[tgt_node['id']] = src_node['id']

source_names = [n['name'] for n in sources]
print(f"Catena: {len(narratives)} commentaries, {len(source_names)} Church Fathers, {len(verses)} verses")

# Generate questions from narratives with good text
random.shuffle(narratives)
catena_count = 0

for narr in narratives:
    if catena_count >= 400:
        break
    
    text = narr.get('properties', {}).get('text', '')
    if not text or len(text) < 40 or len(text) > 300:
        continue
    
    # Find source (Church Father)
    source_id = narrative_to_source.get(narr['id'])
    if not source_id:
        continue
    source_node = nodes_by_id.get(source_id)
    if not source_node:
        continue
    father_name = source_node['name']
    
    # Find verse
    verse_id = None
    for vid, nids in verse_to_narratives.items():
        if narr['id'] in nids:
            verse_id = vid
            break
    
    verse_name = nodes_by_id.get(verse_id, {}).get('name', '') if verse_id else ''
    
    # Clean text
    text_clean = text.strip()
    if len(text_clean) > 150:
        text_clean = text_clean[:150].rsplit(' ', 1)[0] + '...'
    
    # Q1: Who said this about [verse]?
    wrong_fathers = [n for n in source_names if n != father_name]
    random.shuffle(wrong_fathers)
    if len(wrong_fathers) >= 3 and verse_name:
        Q("Life of Jesus", "Pastor",
          f"Which Church Father wrote about {verse_name}: '{text_clean}'?",
          S(father_name, wrong_fathers[:3]), father_name)
        catena_count += 1
    
    # Q2: What did [Father] say about [verse]? (every 3rd entry)
    if catena_count % 3 == 0 and verse_name:
        wrong_texts = []
        for other_narr in random.sample(narratives, min(20, len(narratives))):
            other_text = other_narr.get('properties', {}).get('text', '')
            if other_text and len(other_text) > 30 and other_text != text:
                ot = other_text[:150].rsplit(' ', 1)[0] + '...' if len(other_text) > 150 else other_text
                wrong_texts.append(ot)
                if len(wrong_texts) >= 4:
                    break
        if len(wrong_texts) >= 3:
            Q("Life of Jesus", "Pastor",
              f"What did {father_name} write about {verse_name}?",
              S(text_clean, wrong_texts[:3]), text_clean)
            catena_count += 1

print(f"  Catena Aurea questions: {catena_count}")

# ============================================================================
# 2. MORE OT CROSS-REFERENCES (200+ more files)
# ============================================================================
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
    "Acts":"Acts","Rom":"Romans","1Cor":"1 Corinthians","Rev":"Revelation",
    "Heb":"Hebrews",
}

def book_name(ref):
    return BOOK_NAMES.get(ref.split('.')[0], ref.split('.')[0])

def ref_read(ref):
    p = ref.split('.')
    b = BOOK_NAMES.get(p[0], p[0])
    return f"{b} {p[1]}:{p[2]}" if len(p)>=3 else f"{b} {p[1]}" if len(p)>=2 else b

all_books = list(BOOK_NAMES.values())

# Load from files NOT already used (skip the 51 key chapters from before)
used_files = {
    "Isa_053","Isa_007","Isa_009","Isa_011","Isa_040","Isa_061",
    "Ps_022","Ps_023","Ps_051","Ps_110","Ps_119","Ps_002","Ps_045","Ps_069",
    "Gen_001","Gen_003","Gen_012","Gen_022","Gen_049",
    "Exod_012","Exod_020","Deut_006","Deut_018","Deut_028",
    "Jer_031","Ezek_037","Dan_002","Dan_007","Dan_009",
    "Zech_009","Zech_012","Zech_013","Mic_005","Mal_003","Mal_004",
    "Job_001","Job_038","Job_042","Prov_008","Prov_031",
    "1Sam_016","2Sam_007","1Kgs_018","2Kgs_002",
    "Hos_011","Joel_002","Amos_005","Jonah_002",
    "Ruth_004","Esth_004","Neh_001",
}

tsk_files = sorted(glob.glob("/home/claude/lumina-bible/ot_links_output/*.json"))
new_files = [f for f in tsk_files if os.path.basename(f).replace('.json','') not in used_files]
random.shuffle(new_files)

ot_count = 0
for fpath in new_files[:250]:
    if ot_count >= 350:
        break
    try:
        with open(fpath) as f:
            data = json.load(f)
        if not isinstance(data, list):
            continue
        # Pick best entries (longest reasons)
        good = [e for e in data if isinstance(e, dict) and e.get('reason') and len(e.get('reason','')) > 30 and e.get('anchor') and len(e.get('anchor','')) > 5]
        good.sort(key=lambda x: len(x['reason']), reverse=True)
        
        for entry in good[:3]:
            src = entry.get('source_ref','')
            anchor = entry.get('anchor','')
            target = entry.get('target_start','')
            reason = entry.get('reason','')
            
            if not src or not target:
                continue
            
            src_book = book_name(src)
            tgt_book = book_name(target)
            
            if src_book == tgt_book:
                continue
            
            wrongs = [b for b in all_books if b != tgt_book]
            random.shuffle(wrongs)
            
            cat = ("Prophecy & Fulfillment" if src_book in ["Isaiah","Jeremiah","Ezekiel","Daniel","Zechariah","Micah","Malachi"] else
                   "Psalms & Proverbs" if src_book in ["Psalms","Proverbs","Job","Ecclesiastes"] else
                   "Genesis & Creation" if src_book == "Genesis" else
                   "Moses & the Exodus" if src_book in ["Exodus","Leviticus","Numbers","Deuteronomy"] else
                   "Kings & Kingdoms" if any(k in src_book for k in ["Kings","Samuel","Chronicles"]) else
                   "Prophets")
            
            diff = "Deacon" if tgt_book in ["Genesis","Exodus","Psalms","Isaiah","Matthew","John"] else "Pastor"
            anchor_short = anchor[:70] + '...' if len(anchor) > 70 else anchor
            
            Q(cat, diff,
              f"'{anchor_short}' in {ref_read(src)} cross-references which book?",
              S(tgt_book, wrongs[:3]), tgt_book, reason[:100])
            ot_count += 1
    except:
        pass

print(f"  OT cross-ref questions: {ot_count}")

# ============================================================================
# 3. MORE HEBREW/GREEK — mine obscure entries
# ============================================================================
with open(f"{LUMINA}/lexicons/lexicon-hebrew.json") as f:
    heb = json.load(f)
with open(f"{LUMINA}/lexicons/lexicon-greek.json") as f:
    grk = json.load(f)

def parse_lex(raw):
    c = re.sub('<[^>]+>',' ',raw).strip()
    c = re.sub(r'\s+',' ',c)
    info = {}
    m = re.search(r'Original:\s*(\S+)', c)
    if m: info['word'] = m.group(1)
    m = re.search(r'Transliteration:\s*(\S+)', c)
    if m: info['translit'] = m.group(1)
    m = re.search(r'Definition\s*:\s*(.+?)(?:Origin:|Part\(s\)|TWOT|TDNT|$)', c)
    if m:
        parts = re.split(r'\d+\.', m.group(1).strip())
        defs = [p.strip() for p in parts if len(p.strip()) > 3]
        if defs: info['def1'] = defs[0][:80]
    return info

# Sample random Hebrew entries not yet used
already_used_heb = set()
for q in ALL:
    m = re.search(r'H\d+', q.get('question',''))
    if m: already_used_heb.add(m.group())

new_heb_entries = []
for sid, raw in heb.items():
    if sid in already_used_heb:
        continue
    info = parse_lex(raw)
    if info.get('word') and info.get('def1') and info.get('translit') and len(info['def1']) > 5:
        info['id'] = sid
        new_heb_entries.append(info)

random.shuffle(new_heb_entries)
all_heb_defs = [e['def1'] for e in new_heb_entries[:500]]

heb_count = 0
for entry in new_heb_entries[:200]:
    wrongs = [d for d in all_heb_defs if d != entry['def1']]
    random.shuffle(wrongs)
    if len(wrongs) >= 3:
        Q("Numbers & Genealogies", "Pastor",
          f"What does the Hebrew word '{entry['translit']}' ({entry['word']}, {entry['id']}) mean?",
          S(entry['def1'], wrongs[:3]), entry['def1'])
        heb_count += 1

# Same for Greek
already_used_grk = set()
for q in ALL:
    m = re.search(r'G\d+', q.get('question',''))
    if m: already_used_grk.add(m.group())

new_grk_entries = []
for sid, raw in grk.items():
    if sid in already_used_grk:
        continue
    info = parse_lex(raw)
    if info.get('word') and info.get('def1') and info.get('translit') and len(info['def1']) > 5:
        info['id'] = sid
        new_grk_entries.append(info)

random.shuffle(new_grk_entries)
all_grk_defs = [e['def1'] for e in new_grk_entries[:500]]

grk_count = 0
for entry in new_grk_entries[:150]:
    wrongs = [d for d in all_grk_defs if d != entry['def1']]
    random.shuffle(wrongs)
    if len(wrongs) >= 3:
        Q("Paul & His Letters", "Pastor",
          f"What does the Greek word '{entry['translit']}' ({entry['word']}, {entry['id']}) mean?",
          S(entry['def1'], wrongs[:3]), entry['def1'])
        grk_count += 1

print(f"  New Hebrew questions: {heb_count}")
print(f"  New Greek questions: {grk_count}")

# ============================================================================
# 4. MORE GOSPEL→OT CONNECTIONS (different question patterns)
# ============================================================================
gospel_connections = []
for gospel in ['matthew','mark','luke','john']:
    with open(f"{LUMINA}/backups/{gospel}-links-backup.json") as f:
        data = json.load(f)['entries']
    for ref, entry in data.items():
        kjv = entry.get('kjv_text','')
        for anchor in entry.get('anchors',[]):
            for target in anchor.get('targets',[]):
                start = target.get('start','')
                reason = target.get('reason','')
                if reason and len(reason) > 40 and start.split('.')[0] in BOOK_NAMES:
                    ot_book_name = book_name(start)
                    if ot_book_name not in ["Matthew","Mark","Luke","John","Acts","Romans","Revelation","Hebrews"]:
                        gospel_connections.append({
                            'src': ref, 'kjv': kjv[:120], 'anchor': anchor.get('anchor',''),
                            'ot_ref': start, 'ot_book': ot_book_name, 'reason': reason
                        })

random.shuffle(gospel_connections)
print(f"Gospel→OT connections available: {len(gospel_connections)}")

# New pattern: "What type of connection is this?"
connection_types = {
    "QUOTE": "Direct quotation from the Old Testament",
    "ALLUSION": "An allusion or echo of an OT passage",
    "TYPE": "A typological connection (OT event foreshadows NT)",
    "THEME": "A shared theological theme",
    "FULFILLMENT": "Prophetic fulfillment",
}
type_list = list(connection_types.values())

gospel_q_count = 0
for conn in gospel_connections[:400]:
    if gospel_q_count >= 200:
        break
    
    reason = conn['reason']
    anchor = conn['anchor']
    
    if len(anchor) < 8:
        continue
    
    # Determine connection type from reason
    conn_type = None
    for key, label in connection_types.items():
        if key in reason.upper():
            conn_type = label
            break
    if not conn_type:
        conn_type = "A shared theological theme"
    
    wrong_types = [t for t in type_list if t != conn_type]
    random.shuffle(wrong_types)
    
    anchor_short = anchor[:60] + '...' if len(anchor) > 60 else anchor
    
    Q("Prophecy & Fulfillment", "Pastor",
      f"What type of connection links '{anchor_short}' ({ref_read(conn['src'])}) to {conn['ot_book']}?",
      S(conn_type, wrong_types[:3]), conn_type, reason[:100])
    gospel_q_count += 1

print(f"  Gospel→OT type questions: {gospel_q_count}")

# ============================================================================
# 5. VERSE-TO-BOOK QUESTIONS FROM GOSPELS
# ============================================================================
# "Which OT prophet is echoed in this Gospel teaching?"
prophet_books = ["Isaiah","Jeremiah","Ezekiel","Daniel","Hosea","Joel","Amos",
                 "Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah",
                 "Haggai","Zechariah","Malachi"]

prophet_conns = [c for c in gospel_connections if c['ot_book'] in prophet_books]
random.shuffle(prophet_conns)

prophet_q_count = 0
for conn in prophet_conns[:150]:
    if prophet_q_count >= 100:
        break
    
    anchor = conn['anchor']
    if len(anchor) < 10:
        continue
    
    wrongs = [p for p in prophet_books if p != conn['ot_book']]
    random.shuffle(wrongs)
    
    anchor_short = anchor[:70] + '...' if len(anchor) > 70 else anchor
    Q("Prophets", "Deacon" if conn['ot_book'] in ["Isaiah","Jeremiah","Daniel","Zechariah"] else "Pastor",
      f"Which prophet is echoed in '{anchor_short}' ({ref_read(conn['src'])})?",
      S(conn['ot_book'], wrongs[:3]), conn['ot_book'])
    prophet_q_count += 1

print(f"  Prophet echo questions: {prophet_q_count}")

# ============================================================================
# FINALIZE
# ============================================================================
for i, q in enumerate(ALL):
    q["id"] = hashlib.md5(f"{q['category']}-{q['difficulty']}-{q['question'][:50]}-{i}".encode()).hexdigest()[:12]

from collections import Counter
dc = Counter(q["difficulty"] for q in ALL)
cc = Counter(q["category"] for q in ALL)
new_count = len(ALL) - 5605  # previous total

print(f"\n{'='*60}")
print(f"NEW QUESTIONS ADDED: {new_count}")
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
