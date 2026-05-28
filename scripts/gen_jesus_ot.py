#!/usr/bin/env python3
"""
Generate 500 'Words of Jesus → OT Connection' trivia questions
from Lumina Bible's cross-reference data.
"""
import json, random, hashlib, os, re

random.seed(42)

# ============================================================================
# LOAD ALL GOSPEL DATA
# ============================================================================
all_entries = {}
for gospel in ['matthew','mark','luke','john']:
    path = f'/home/claude/lumina-bible/data/backups/{gospel}-links-backup.json'
    with open(path) as f:
        data = json.load(f)['entries']
    all_entries.update(data)

print(f"Loaded {len(all_entries)} Gospel verses")

# OT book abbreviations → full names
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
    "Zeph":"Zephaniah","Hag":"Haggai","Zech":"Zechariah","Mal":"Malachi"
}
NT_BOOKS = {"Matt","Mark","Luke","John","Acts","Rom","1Cor","2Cor","Gal","Eph",
    "Phil","Col","1Thess","2Thess","1Tim","2Tim","Titus","Phlm","Heb","Jas",
    "1Pet","2Pet","1John","2John","3John","Jude","Rev"}

def ref_to_readable(ref):
    """Convert 'Isa.53.5' to 'Isaiah 53:5'"""
    parts = ref.split('.')
    if len(parts) >= 2:
        book = BOOK_NAMES.get(parts[0], parts[0])
        ch = parts[1]
        vs = parts[2] if len(parts) > 2 else ""
        return f"{book} {ch}:{vs}" if vs else f"{book} {ch}"
    return ref

def source_to_readable(ref):
    """Convert 'Matt.5.3' to 'Matthew 5:3'"""
    NT_NAMES = {"Matt":"Matthew","Mark":"Mark","Luke":"Luke","John":"John"}
    parts = ref.split('.')
    if len(parts) >= 3:
        book = NT_NAMES.get(parts[0], parts[0])
        return f"{book} {parts[1]}:{parts[2]}"
    return ref

def is_ot_ref(ref):
    book = ref.split('.')[0]
    return book not in NT_BOOKS

def get_ot_book(ref):
    return ref.split('.')[0]

def get_ot_book_full(ref):
    abbr = ref.split('.')[0]
    return BOOK_NAMES.get(abbr, abbr)

# ============================================================================
# EXTRACT RICH OT CONNECTIONS
# ============================================================================
connections = []

for source_ref, entry in all_entries.items():
    kjv = entry.get('kjv_text', '')
    if not kjv or len(kjv) < 20:
        continue
    
    anchors = entry.get('anchors', [])
    for anchor in anchors:
        anchor_text = anchor.get('anchor', '')
        targets = anchor.get('targets', [])
        
        for target in targets:
            start = target.get('start', '')
            reason = target.get('reason', '')
            
            if not is_ot_ref(start) or not reason or len(reason) < 20:
                continue
            
            ot_book = get_ot_book_full(start)
            ot_ref_readable = ref_to_readable(start)
            source_readable = source_to_readable(source_ref)
            
            connections.append({
                'source_ref': source_ref,
                'source_readable': source_readable,
                'kjv_text': kjv,
                'anchor_text': anchor_text,
                'ot_ref': start,
                'ot_ref_readable': ot_ref_readable,
                'ot_book': ot_book,
                'ot_abbr': get_ot_book(start),
                'reason': reason
            })

print(f"Extracted {len(connections)} OT connections")

# Sort by reason quality (longer = richer explanation)
connections.sort(key=lambda x: len(x['reason']), reverse=True)

# ============================================================================
# BUILD QUESTIONS
# ============================================================================
ALL_Q = []
used_sources = set()
used_questions = set()

def Q(q, opts, cor, exp=""):
    k = q.strip().lower()
    if k not in used_questions:
        used_questions.add(k)
        ALL_Q.append({
            "category": "Words of Jesus & OT Roots",
            "difficulty": "",  # set below
            "question": q,
            "options": opts,
            "correct": cor,
            "explanation": exp
        })

def shuf(correct, wrongs):
    w = [x for x in wrongs if x != correct][:3]
    while len(w) < 3: w.append("None of these")
    opts = [correct] + w[:3]
    random.shuffle(opts)
    return opts

# Get unique OT books for wrong answers
all_ot_books = sorted(set(c['ot_book'] for c in connections))

# ============================================================================
# QUESTION TYPE 1: "Which OT book does [Gospel verse] draw from?"
# ============================================================================
random.shuffle(connections)
type1_count = 0
for conn in connections:
    if type1_count >= 150:
        break
    src = conn['source_readable']
    anchor = conn['anchor_text']
    ot_book = conn['ot_book']
    reason = conn['reason']
    kjv = conn['kjv_text']
    
    # Skip very short anchors
    if len(anchor) < 5 or len(kjv) < 30:
        continue
    
    # Unique per source verse
    key = f"type1-{conn['source_ref']}"
    if key in used_sources:
        continue
    used_sources.add(key)
    
    # Truncate KJV if too long
    kjv_short = kjv[:120] + "..." if len(kjv) > 120 else kjv
    
    wrongs = [b for b in all_ot_books if b != ot_book]
    random.shuffle(wrongs)
    
    Q(f"The verse '{kjv_short}' ({src}) has roots in which OT book?",
      shuf(ot_book, wrongs[:3]), ot_book,
      f"{conn['ot_ref_readable']}: {reason[:150]}")
    type1_count += 1

print(f"  Type 1 (which OT book): {type1_count}")

# ============================================================================
# QUESTION TYPE 2: "Which OT reference is the phrase '[anchor]' linked to?"
# ============================================================================
random.shuffle(connections)
type2_count = 0
all_ot_refs = list(set(c['ot_ref_readable'] for c in connections))
for conn in connections:
    if type2_count >= 120:
        break
    anchor = conn['anchor_text']
    ot_ref = conn['ot_ref_readable']
    src = conn['source_readable']
    reason = conn['reason']
    
    if len(anchor) < 8:
        continue
    
    key = f"type2-{anchor[:30]}"
    if key in used_sources:
        continue
    used_sources.add(key)
    
    wrongs = [r for r in all_ot_refs if r != ot_ref and r.split()[0] != ot_ref.split()[0]]
    random.shuffle(wrongs)
    if len(wrongs) < 3:
        continue
    
    anchor_short = anchor[:80] + "..." if len(anchor) > 80 else anchor
    
    Q(f"In {src}, the phrase '{anchor_short}' echoes which OT passage?",
      shuf(ot_ref, wrongs[:3]), ot_ref,
      reason[:150])
    type2_count += 1

print(f"  Type 2 (which OT ref): {type2_count}")

# ============================================================================
# QUESTION TYPE 3: "Why is [Gospel verse] connected to [OT verse]?"
# ============================================================================
random.shuffle(connections)
type3_count = 0
for conn in connections:
    if type3_count >= 100:
        break
    src = conn['source_readable']
    ot_ref = conn['ot_ref_readable']
    reason = conn['reason']
    
    if len(reason) < 50:
        continue
    
    key = f"type3-{conn['source_ref']}-{conn['ot_ref']}"
    if key in used_sources:
        continue
    used_sources.add(key)
    
    # Create the correct answer (truncated reason)
    correct_reason = reason[:120]
    if len(reason) > 120:
        correct_reason = reason[:120].rsplit(' ', 1)[0] + "..."
    
    # Generate plausible wrong reasons from other connections
    wrong_reasons = []
    for other in random.sample(connections, min(50, len(connections))):
        if other['source_ref'] != conn['source_ref'] and len(other['reason']) >= 40:
            wr = other['reason'][:120]
            if len(other['reason']) > 120:
                wr = other['reason'][:120].rsplit(' ', 1)[0] + "..."
            wrong_reasons.append(wr)
            if len(wrong_reasons) >= 5:
                break
    
    if len(wrong_reasons) < 3:
        continue
    
    Q(f"Why is {src} connected to {ot_ref}?",
      shuf(correct_reason, wrong_reasons[:3]), correct_reason)
    type3_count += 1

print(f"  Type 3 (why connected): {type3_count}")

# ============================================================================
# QUESTION TYPE 4: "Which Gospel passage references [OT passage]?"
# ============================================================================
random.shuffle(connections)
type4_count = 0
all_sources = list(set(c['source_readable'] for c in connections))
for conn in connections:
    if type4_count >= 80:
        break
    src = conn['source_readable']
    ot_ref = conn['ot_ref_readable']
    ot_book = conn['ot_book']
    
    key = f"type4-{conn['ot_ref']}"
    if key in used_sources:
        continue
    used_sources.add(key)
    
    wrongs = [s for s in all_sources if s != src]
    random.shuffle(wrongs)
    
    Q(f"Which Gospel verse draws from {ot_ref} ({ot_book})?",
      shuf(src, wrongs[:3]), src,
      conn['reason'][:150])
    type4_count += 1

print(f"  Type 4 (which Gospel): {type4_count}")

# ============================================================================
# QUESTION TYPE 5: "What OT theme/concept underlies [Gospel teaching]?"
# ============================================================================
random.shuffle(connections)
type5_count = 0
for conn in connections:
    if type5_count >= 80:
        break
    anchor = conn['anchor_text']
    reason = conn['reason']
    src = conn['source_readable']
    ot_book = conn['ot_book']
    
    if len(reason) < 60 or len(anchor) < 10:
        continue
    
    key = f"type5-{conn['source_ref']}-{conn['anchor_text'][:20]}"
    if key in used_sources:
        continue
    used_sources.add(key)
    
    # Extract the core OT concept from the reason
    concept = reason[:100]
    if len(reason) > 100:
        concept = reason[:100].rsplit(' ', 1)[0] + "..."
    
    wrong_concepts = []
    for other in random.sample(connections, min(50, len(connections))):
        if other['ot_ref'] != conn['ot_ref'] and len(other['reason']) >= 40:
            wc = other['reason'][:100]
            if len(other['reason']) > 100:
                wc = other['reason'][:100].rsplit(' ', 1)[0] + "..."
            wrong_concepts.append(wc)
            if len(wrong_concepts) >= 5:
                break
    
    if len(wrong_concepts) < 3:
        continue
    
    anchor_short = anchor[:60] + "..." if len(anchor) > 60 else anchor
    Q(f"What OT concept underlies the phrase '{anchor_short}' in {src}?",
      shuf(concept, wrong_concepts[:3]), concept)
    type5_count += 1

print(f"  Type 5 (OT concept): {type5_count}")

# ============================================================================
# ASSIGN DIFFICULTY + IDS
# ============================================================================
# Difficulty based on OT book familiarity
EASY_BOOKS = {"Genesis","Exodus","Psalms","Isaiah","Daniel","Jonah","Proverbs"}
MEDIUM_BOOKS = {"Deuteronomy","1 Samuel","2 Samuel","1 Kings","2 Kings","Jeremiah","Ezekiel","Zechariah","Malachi","Job","Numbers","Leviticus","Joshua","Judges"}
# Everything else = Pastor

for q in ALL_Q:
    # Try to identify the OT book from the question or answer
    ot_book = ""
    for book in BOOK_NAMES.values():
        if book in q['correct'] or book in q['question']:
            ot_book = book
            break
    
    if ot_book in EASY_BOOKS:
        q['difficulty'] = 'Layperson'
    elif ot_book in MEDIUM_BOOKS:
        q['difficulty'] = 'Deacon'
    else:
        q['difficulty'] = random.choice(['Deacon', 'Pastor'])

for i, q in enumerate(ALL_Q):
    q['id'] = hashlib.md5(f"jesus-ot-{q['question'][:50]}-{i}".encode()).hexdigest()[:12]

# ============================================================================
# STATS & SAVE
# ============================================================================
from collections import Counter
dc = Counter(q['difficulty'] for q in ALL_Q)

print(f"\n{'='*60}")
print(f"TOTAL JESUS-OT QUESTIONS: {len(ALL_Q)}")
print(f"  Layperson: {dc['Layperson']}")
print(f"  Deacon: {dc['Deacon']}")
print(f"  Pastor: {dc['Pastor']}")
print(f"{'='*60}")

# Save standalone
out1 = "/home/claude/manna/jesus_ot_questions.json"
with open(out1, "w") as f:
    json.dump(ALL_Q, f, indent=2)
print(f"Saved standalone: {out1} ({os.path.getsize(out1)/1024:.0f} KB)")

# Also merge into main question bank
main_path = "/home/claude/manna/manna_questions.json"
with open(main_path) as f:
    main = json.load(f)

existing_main = set(q['question'].strip().lower() for q in main)
added = 0
for q in ALL_Q:
    if q['question'].strip().lower() not in existing_main:
        main.append(q)
        existing_main.add(q['question'].strip().lower())
        added += 1

# Re-ID everything
for i, q in enumerate(main):
    q['id'] = hashlib.md5(f"{q['category']}-{q['difficulty']}-{q['question'][:50]}-{i}".encode()).hexdigest()[:12]

with open(main_path, "w") as f:
    json.dump(main, f, indent=2)

cc = Counter(q['category'] for q in main)
print(f"\nMerged {added} new questions into main bank")
print(f"GRAND TOTAL: {len(main)} questions across {len(cc)} categories")
print(f"Saved: {main_path} ({os.path.getsize(main_path)/1024:.0f} KB)")
