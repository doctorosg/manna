#!/usr/bin/env python3
"""
Generate hard Pastor-level questions from Lumina Bible data:
- Hebrew/Greek lexicons (Strong's numbers)
- Bible people profiles
- Bible places profiles  
- Timeline events
- Theological debates
"""
import json, random, hashlib, os, re
random.seed(2025)

LUMINA = "/home/claude/lumina-bible/data"

# Load existing questions
with open("/home/claude/manna/manna_questions.json") as f:
    ALL = json.load(f)
existing = set(q["question"].strip().lower() for q in ALL)

def Q(cat,diff,q,opts,cor,exp=""):
    k=q.strip().lower()
    if k not in existing:
        existing.add(k)
        ALL.append({"category":cat,"difficulty":diff,"question":q,"options":opts,"correct":cor,"explanation":exp})

def S(c,ws):
    o=[c]+list(ws[:3]);random.shuffle(o);return o

# ============================================================================
# LOAD LUMINA DATA
# ============================================================================

# Hebrew Lexicon
with open(f"{LUMINA}/lexicons/lexicon-hebrew.json") as f:
    heb_raw = json.load(f)

def parse_lexicon(raw_html):
    """Extract key info from HTML lexicon entry"""
    clean = re.sub('<[^>]+>', ' ', raw_html).strip()
    clean = re.sub(r'\s+', ' ', clean)
    
    info = {}
    # Original word
    m = re.search(r'Original:\s*(\S+)', clean)
    if m: info['original'] = m.group(1)
    # Transliteration
    m = re.search(r'Transliteration:\s*(\S+)', clean)
    if m: info['translit'] = m.group(1)
    # Definition (first item)
    m = re.search(r'Definition\s*:\s*(.+?)(?:Origin:|Part\(s\)|TWOT|$)', clean)
    if m: 
        defn = m.group(1).strip()
        # Get first meaningful definition
        parts = re.split(r'\d+\.', defn)
        if len(parts) > 1:
            info['definition'] = parts[1].strip()[:100]
        else:
            info['definition'] = defn[:100]
    return info

# Parse key Hebrew words
HEBREW_ENTRIES = {}
important_hebrew = {
    'H1':'father','H430':'God (Elohim)','H3068':'LORD (YHWH)','H7225':'beginning',
    'H8451':'Torah/law','H7307':'spirit/wind','H5315':'soul','H1285':'covenant',
    'H2617':'lovingkindness','H6664':'righteousness','H6918':'holy','H4899':'messiah/anointed',
    'H3444':'salvation','H539':'believe/faithful','H1984':'praise/hallelujah',
    'H7965':'peace/shalom','H2580':'grace','H571':'truth','H3519':'glory',
    'H776':'earth/land','H8064':'heaven','H120':'man/adam','H2421':'live',
    'H3045':'know','H157':'love','H3372':'fear/revere','H5647':'serve/worship',
    'H6213':'do/make','H1254':'create','H7121':'call/proclaim','H8085':'hear/obey',
    'H5975':'stand','H7200':'see','H1980':'walk/go','H5414':'give',
    'H3427':'dwell/sit','H3318':'go out','H935':'come/enter','H559':'say/speak',
    'H4428':'king','H3548':'priest','H5030':'prophet','H5650':'servant',
    'H1121':'son','H1323':'daughter','H802':'woman/wife','H376':'man/husband',
    'H5769':'everlasting/eternal','H2822':'darkness','H216':'light','H4325':'water',
    'H784':'fire','H68':'stone','H6086':'tree/wood','H1818':'blood',
    'H2403':'sin','H5771':'iniquity','H6588':'transgression','H3722':'atonement',
    'H4196':'altar','H2077':'sacrifice','H6999':'incense','H5930':'burnt offering',
    'H7676':'sabbath','H2320':'month/new moon','H4150':'appointed time/feast',
    'H168':'tent/tabernacle','H1004':'house/temple','H727':'ark',
}

for strongs, hint in important_hebrew.items():
    if strongs in heb_raw:
        info = parse_lexicon(heb_raw[strongs])
        info['strongs'] = strongs
        info['hint'] = hint
        if info.get('original') and info.get('definition'):
            HEBREW_ENTRIES[strongs] = info

print(f"Parsed {len(HEBREW_ENTRIES)} Hebrew entries")

# Parse key Greek words
with open(f"{LUMINA}/lexicons/lexicon-greek.json") as f:
    grk_raw = json.load(f)

important_greek = {
    'G26':'love (agape)','G3056':'word (logos)','G4151':'spirit (pneuma)',
    'G5547':'Christ (Christos)','G2316':'God (theos)','G2962':'Lord (kyrios)',
    'G4102':'faith (pistis)','G5485':'grace (charis)','G1680':'hope (elpis)',
    'G1343':'righteousness','G266':'sin (hamartia)','G3341':'repentance (metanoia)',
    'G908':'baptism (baptisma)','G1577':'church (ekklesia)','G2098':'gospel (euangelion)',
    'G3875':'helper/comforter (parakletos)','G2842':'fellowship (koinonia)',
    'G1411':'power (dynamis)','G1849':'authority (exousia)','G932':'kingdom (basileia)',
    'G4991':'salvation (soteria)','G1515':'peace (eirene)','G5479':'joy (chara)',
    'G3551':'law (nomos)','G1242':'covenant (diatheke)','G129':'blood (haima)',
    'G4716':'cross (stauros)','G386':'resurrection (anastasis)',
    'G3952':'coming/presence (parousia)','G165':'age/eternity (aion)',
    'G1401':'servant/slave (doulos)','G652':'apostle (apostolos)',
    'G4396':'prophet (prophetes)','G1320':'teacher (didaskalos)',
    'G4561':'flesh (sarx)','G2889':'world (kosmos)','G2222':'life (zoe)',
    'G2288':'death (thanatos)','G5457':'light (phos)','G4655':'darkness (skotos)',
    'G225':'truth (aletheia)','G3498':'dead (nekros)',
}

GREEK_ENTRIES = {}
for strongs, hint in important_greek.items():
    if strongs in grk_raw:
        info = parse_lexicon(grk_raw[strongs])
        info['strongs'] = strongs
        info['hint'] = hint
        if info.get('original') and info.get('definition'):
            GREEK_ENTRIES[strongs] = info

print(f"Parsed {len(GREEK_ENTRIES)} Greek entries")

# Bible People
with open(f"{LUMINA}/people_places/bible_people.json") as f:
    PEOPLE = json.load(f)
print(f"Loaded {len(PEOPLE)} people")

# Bible Places
with open(f"{LUMINA}/people_places/bible_places.json") as f:
    PLACES = json.load(f)
print(f"Loaded {len(PLACES)} places")

# Timeline
with open(f"{LUMINA}/timeline/timeline_events.json") as f:
    TIMELINE = json.load(f)
print(f"Loaded {len(TIMELINE)} timeline events")

# Debates
with open(f"{LUMINA}/debates/debates.json") as f:
    DEBATES = json.load(f)
print(f"Loaded {len(DEBATES)} debates")

# ============================================================================
# GENERATE QUESTIONS
# ============================================================================

# --- HEBREW LEXICON QUESTIONS ---
all_heb_defs = [e['definition'] for e in HEBREW_ENTRIES.values()]
all_heb_words = [e['original'] for e in HEBREW_ENTRIES.values()]
all_heb_translits = [e.get('translit','') for e in HEBREW_ENTRIES.values() if e.get('translit')]

for strongs, entry in HEBREW_ENTRIES.items():
    word = entry['original']
    translit = entry.get('translit', '')
    defn = entry['definition']
    hint = entry['hint']
    
    # Q: What does Hebrew word X mean?
    wrongs = [d for d in all_heb_defs if d != defn]
    random.shuffle(wrongs)
    if translit and len(wrongs) >= 3:
        Q("Psalms & Proverbs" if 'praise' in hint or 'psalm' in hint.lower() else
          "Laws & Commandments" if 'law' in hint or 'sabbath' in hint or 'sacrifice' in hint or 'altar' in hint else
          "Genesis & Creation" if 'create' in hint or 'beginning' in hint or 'earth' in hint or 'heaven' in hint else
          "Moses & the Exodus" if 'tabernacle' in hint or 'ark' in hint or 'incense' in hint else
          "Prophecy & Fulfillment" if 'messiah' in hint or 'prophet' in hint else
          "Life of Jesus" if 'salvation' in hint else
          "Numbers & Genealogies",
          "Pastor",
          f"What does the Hebrew word '{translit}' ({word}) mean?",
          S(defn, wrongs[:3]), defn, f"Strong's {strongs}")
    
    # Q: What is the Strong's number for [concept]?
    all_strongs = list(HEBREW_ENTRIES.keys())
    wrong_strongs = [s for s in all_strongs if s != strongs]
    random.shuffle(wrong_strongs)
    if len(wrong_strongs) >= 3:
        Q("Numbers & Genealogies", "Pastor",
          f"What is the Strong's number for the Hebrew word meaning '{hint}'?",
          S(strongs, wrong_strongs[:3]), strongs)

print(f"  After Hebrew Qs: {len(ALL)}")

# --- GREEK LEXICON QUESTIONS ---
all_grk_defs = [e['definition'] for e in GREEK_ENTRIES.values()]

for strongs, entry in GREEK_ENTRIES.items():
    word = entry['original']
    translit = entry.get('translit', '')
    defn = entry['definition']
    hint = entry['hint']
    
    wrongs = [d for d in all_grk_defs if d != defn]
    random.shuffle(wrongs)
    if translit and len(wrongs) >= 3:
        cat = ("Paul & His Letters" if any(w in hint for w in ['faith','grace','gospel','church','apostle','covenant','flesh','law']) else
               "Life of Jesus" if any(w in hint for w in ['Christ','Lord','kingdom','cross','resurrection']) else
               "The Apostles" if any(w in hint for w in ['baptism','fellowship','teacher']) else
               "Revelation & End Times" if any(w in hint for w in ['coming','eternity','dead']) else
               "Angels & Demons" if 'spirit' in hint else
               "Numbers & Genealogies")
        Q(cat, "Pastor",
          f"What does the Greek word '{translit}' ({word}) mean?",
          S(defn, wrongs[:3]), defn, f"Strong's {strongs}")

print(f"  After Greek Qs: {len(ALL)}")

# --- PEOPLE QUESTIONS ---
all_names = [p['name'] for p in PEOPLE]
all_categories = list(set(p['category'] for p in PEOPLE))
all_passages = [p['key_passage'] for p in PEOPLE if p.get('key_passage')]

for person in PEOPLE:
    name = person['name']
    desc = person['description'][:150]
    cat_p = person['category']
    passage = person.get('key_passage', '')
    also = person.get('also_known_as', '')
    
    # Map person category to Manna category
    manna_cat = ("Genesis & Creation" if cat_p in ['Patriarch','Matriarch'] and name in ['Adam','Eve','Noah','Abraham','Sarah','Isaac','Rebekah','Jacob','Rachel','Leah','Joseph','Esau'] else
                 "Moses & the Exodus" if name in ['Moses','Aaron','Miriam','Joshua'] else
                 "Kings & Kingdoms" if cat_p in ['King','Queen'] or name in ['David','Solomon','Saul'] else
                 "Prophets" if cat_p == 'Prophet' else
                 "The Apostles" if cat_p == 'Apostle' or name in ['Peter','Paul','John','James','Stephen'] else
                 "Women of the Bible" if cat_p in ['Matriarch','Queen'] or name in ['Ruth','Esther','Deborah','Mary','Martha','Mary Magdalene','Hannah','Rahab'] else
                 "Life of Jesus" if name in ['Jesus','John the Baptist','Nicodemus','Zacchaeus'] else
                 "Numbers & Genealogies")
    
    # Who is this person?
    wrong_descs = [p['description'][:150] for p in PEOPLE if p['name'] != name]
    random.shuffle(wrong_descs)
    if len(wrong_descs) >= 3:
        Q(manna_cat, "Deacon",
          f"Who was {name} in the Bible?",
          S(desc, wrong_descs[:3]), desc, passage)
    
    # Key passage question
    if passage:
        wrong_passages = [p for p in all_passages if p != passage]
        random.shuffle(wrong_passages)
        if len(wrong_passages) >= 3:
            Q(manna_cat, "Pastor",
              f"What is the key passage for {name}?",
              S(passage, wrong_passages[:3]), passage)
    
    # Also known as
    if also:
        wrong_names = [p.get('also_known_as','') for p in PEOPLE if p.get('also_known_as') and p['name'] != name]
        random.shuffle(wrong_names)
        if len(wrong_names) >= 3:
            Q(manna_cat, "Deacon",
              f"What is {name} also known as?",
              S(also, wrong_names[:3]), also)

print(f"  After People Qs: {len(ALL)}")

# --- PLACES QUESTIONS ---
for place in PLACES:
    name = place['name']
    desc = place.get('description', '')[:150]
    significance = place.get('significance', '')[:150]
    
    if not desc and not significance:
        continue
    
    text = significance if significance else desc
    wrong_texts = [p.get('significance', p.get('description', ''))[:150] for p in PLACES if p['name'] != name]
    random.shuffle(wrong_texts)
    wrong_texts = [w for w in wrong_texts if w]
    
    if len(wrong_texts) >= 3:
        Q("Places & Lands", "Deacon" if name in ['Jerusalem','Bethlehem','Egypt','Babylon','Nazareth'] else "Pastor",
          f"What is the biblical significance of {name}?",
          S(text, wrong_texts[:3]), text)

print(f"  After Places Qs: {len(ALL)}")

# --- TIMELINE QUESTIONS ---
all_dates = [t['date_label'] for t in TIMELINE]
all_titles = [t['title'] for t in TIMELINE]
all_eras = list(set(t['era'] for t in TIMELINE))

for event in TIMELINE:
    title = event['title']
    date = event['date_label']
    era = event['era']
    desc = event['description'][:150]
    passage = event.get('key_passage', '')
    
    # When did X happen?
    wrong_dates = [d for d in all_dates if d != date]
    random.shuffle(wrong_dates)
    if len(wrong_dates) >= 3:
        diff = "Layperson" if title in ['Creation','The Flood','The Exodus','Birth of Jesus','Crucifixion','Resurrection'] else "Deacon" if era in ['Patriarchs','United Kingdom','Divided Kingdom'] else "Pastor"
        Q("Numbers & Genealogies", diff,
          f"When did '{title}' occur in biblical history?",
          S(date, wrong_dates[:3]), date, passage)
    
    # What era was X in?
    wrong_eras = [e for e in all_eras if e != era]
    random.shuffle(wrong_eras)
    if len(wrong_eras) >= 3:
        Q("Numbers & Genealogies", "Deacon",
          f"Which era of biblical history does '{title}' belong to?",
          S(era, wrong_eras[:3]), era)

# Timeline ordering
sorted_timeline = sorted(TIMELINE, key=lambda x: x['date_sort'])
for i in range(len(sorted_timeline) - 1):
    ev1 = sorted_timeline[i]
    ev2 = sorted_timeline[i+1]
    if ev1['title'] != ev2['title']:
        Q("Numbers & Genealogies", "Deacon",
          f"Which came first: '{ev1['title']}' or '{ev2['title']}'?",
          S(ev1['title'], [ev2['title'], "They happened at the same time", "Neither is in the Bible"]),
          ev1['title'])

print(f"  After Timeline Qs: {len(ALL)}")

# --- DEBATE QUESTIONS ---
for debate in DEBATES:
    topic = debate['topic']
    category = debate['category']
    
    manna_cat = ("Laws & Commandments" if 'Law' in category or 'Sabbath' in topic else
                 "Life of Jesus" if 'Christ' in topic or 'Jesus' in topic else
                 "Paul & His Letters" if 'Grace' in topic or 'Faith' in topic else
                 "Revelation & End Times" if 'End' in topic or 'Rapture' in topic or 'Millennium' in topic else
                 "The Apostles" if 'Church' in topic or 'Baptism' in topic else
                 "Prophecy & Fulfillment")
    
    for point in debate.get('points', [])[:5]:
        against = point.get('against_heading') or ''
        for_head = point.get('for_heading') or ''
        against_arg = (point.get('against_argument') or '')[:120]
        for_arg = (point.get('for_argument') or '')[:120]
        
        if against and for_head:
            # Q: What is the argument AGAINST [position]?
            Q(manna_cat, "Pastor",
              f"In the debate '{topic}', what argues against the position that '{against[:80]}'?",
              S(for_head[:100] if for_head else "There is no counter-argument",
                [against[:100], "The Bible is silent on this", "Both sides agree"]),
              for_head[:100] if for_head else "There is no counter-argument")

print(f"  After Debate Qs: {len(ALL)}")

# ============================================================================
# FINALIZE
# ============================================================================
for i, q in enumerate(ALL):
    q["id"] = hashlib.md5(f"{q['category']}-{q['difficulty']}-{q['question'][:50]}-{i}".encode()).hexdigest()[:12]

from collections import Counter
cc = Counter(q["category"] for q in ALL)
dc = Counter(q["difficulty"] for q in ALL)

print(f"\n{'='*60}")
print(f"GRAND TOTAL: {len(ALL)} questions")
print(f"  Layperson: {dc['Layperson']}  Deacon: {dc['Deacon']}  Pastor: {dc['Pastor']}")
print(f"{'='*60}")
for cat in sorted(cc.keys()):
    dd = Counter(q["difficulty"] for q in ALL if q["category"] == cat)
    print(f"  {cat}: {cc[cat]:4d} (L:{dd.get('Layperson',0):3d} D:{dd.get('Deacon',0):3d} P:{dd.get('Pastor',0):3d})")

with open("/home/claude/manna/manna_questions.json", "w") as f:
    json.dump(ALL, f, indent=2)
print(f"\nSaved: {os.path.getsize('/home/claude/manna/manna_questions.json')/1024:.0f} KB")
