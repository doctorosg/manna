#!/usr/bin/env python3
"""
Manna Bible Trivia — VOLUME 2 question generator.
Generates brand-new questions from Lumina data, guaranteed NOT to duplicate Volume 1.
Sources: bible_people, bible_places, timeline_events, parables, Gospel->OT links.
Output: manna_questions_v2.json (does NOT touch the V1 bank).
"""
import json, hashlib, random, re, os, html
from collections import defaultdict

random.seed(20262)  # reproducible

LUMINA = "/home/claude/lumina-bible"
MANNA  = "/home/claude/manna"

# ---------------------------------------------------------------- helpers
BOOKS = {
    "Gen":"Genesis","Exod":"Exodus","Lev":"Leviticus","Num":"Numbers","Deut":"Deuteronomy",
    "Josh":"Joshua","Judg":"Judges","Ruth":"Ruth","1Sam":"1 Samuel","2Sam":"2 Samuel",
    "1Kgs":"1 Kings","2Kgs":"2 Kings","1Chr":"1 Chronicles","2Chr":"2 Chronicles",
    "Ezra":"Ezra","Neh":"Nehemiah","Esth":"Esther","Job":"Job","Ps":"Psalms","Prov":"Proverbs",
    "Eccl":"Ecclesiastes","Song":"Song of Solomon","Isa":"Isaiah","Jer":"Jeremiah","Lam":"Lamentations",
    "Ezek":"Ezekiel","Dan":"Daniel","Hos":"Hosea","Joel":"Joel","Amos":"Amos","Obad":"Obadiah",
    "Jonah":"Jonah","Mic":"Micah","Nah":"Nahum","Hab":"Habakkuk","Zeph":"Zephaniah","Hag":"Haggai",
    "Zech":"Zechariah","Mal":"Malachi","Matt":"Matthew","Mark":"Mark","Luke":"Luke","John":"John",
    "Acts":"Acts","Rom":"Romans","1Cor":"1 Corinthians","2Cor":"2 Corinthians","Gal":"Galatians",
    "Eph":"Ephesians","Phil":"Philippians","Col":"Colossians","1Thess":"1 Thessalonians",
    "2Thess":"2 Thessalonians","1Tim":"1 Timothy","2Tim":"2 Timothy","Titus":"Titus","Phlm":"Philemon",
    "Heb":"Hebrews","Jas":"James","1Pet":"1 Peter","2Pet":"2 Peter","1John":"1 John","2John":"2 John",
    "3John":"3 John","Jude":"Jude","Rev":"Revelation",
}
def nice_ref(ref):
    """Matt.1.1 -> Matthew 1:1"""
    parts = ref.split(".")
    if len(parts) >= 3:
        book = BOOKS.get(parts[0], parts[0])
        return f"{book} {parts[1]}:{parts[2]}"
    if len(parts) == 2:
        return f"{BOOKS.get(parts[0], parts[0])} {parts[1]}"
    return ref
def book_of(ref):
    return BOOKS.get(ref.split(".")[0], ref.split(".")[0])

def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", s.lower())).strip()

def first_sentence(text, maxlen=180):
    text = re.sub(r"\s+", " ", text).strip()
    m = re.split(r"(?<=[.!?]) ", text)
    s = m[0] if m else text
    if len(s) > maxlen:
        s = s[:maxlen].rsplit(" ", 1)[0] + "..."
    return s

WOMEN = {"Eve","Sarah","Rebekah","Rachel","Leah","Miriam","Deborah","Ruth","Naomi","Hannah",
         "Esther","Mary","Martha","Elizabeth","Mary Magdalene","Bathsheba","Jezebel","Rahab",
         "Abigail","Delilah","Lydia","Priscilla","Dorcas","Tabitha","Hagar","Tamar","Anna"}

# person.category -> Manna category
PERSON_CAT = {
    "Patriarch":"Genesis & Creation","Prophet":"Prophets","King":"Kings & Kingdoms",
    "Apostle":"The Apostles","Priest":"Laws & Commandments","Judge":"Kings & Kingdoms",
    "Leader":"Moses & the Exodus","Other":"Numbers & Genealogies",
}
ERA_CAT = {
    "Patriarchs":"Genesis & Creation","Exodus":"Moses & the Exodus",
    "Judges & Early Monarchy":"Kings & Kingdoms","Divided Kingdom & Prophets":"Prophets",
    "Return & Intertestamental":"Prophecy & Fulfillment","Life of Christ":"Life of Jesus",
    "Early Church":"The Apostles",
}
PLACE_CAT_LABEL = {"City":"City","Mountain":"Mountain","River":"River","Region":"Region",
                   "Sea":"Sea","Country":"Country"}

# ---------------------------------------------------------------- load V1 dedup set
v1 = json.load(open(f"{MANNA}/manna_questions.json"))
seen = set(norm(q["question"]) for q in v1)
print(f"V1 questions loaded for dedup: {len(v1)}")

out = []
def add(category, difficulty, question, options, correct, explanation=""):
    """Validate + dedup + append."""
    q = question.strip()
    if norm(q) in seen:
        return False
    opts = [o for o in options if o and str(o).strip()]
    # unique options
    uniq = []
    for o in opts:
        if o not in uniq:
            uniq.append(o)
    if correct not in uniq or len(uniq) < 4:
        return False
    uniq = uniq[:4]
    if correct not in uniq:
        uniq[-1] = correct
    random.shuffle(uniq)
    seen.add(norm(q))
    out.append({
        "category": category, "difficulty": difficulty, "question": q,
        "options": uniq, "correct": correct, "explanation": explanation,
        "id": hashlib.md5((q+correct).encode()).hexdigest()[:12],
    })
    return True

def distractors(pool, exclude, n=3):
    cand = [x for x in pool if x and x != exclude]
    random.shuffle(cand)
    res = []
    for c in cand:
        if c not in res:
            res.append(c)
        if len(res) == n:
            break
    return res

# ================================================================ PEOPLE
people = json.load(open(f"{LUMINA}/data/people_places/bible_people.json"))
all_names = [p["name"] for p in people]
names_by_cat = defaultdict(list)
for p in people:
    names_by_cat[p.get("category")].append(p["name"])
all_passages = [p["key_passage"] for p in people if p.get("key_passage")]

ROLE_LABEL = {"Patriarch":"A patriarch","Prophet":"A prophet","King":"A king",
              "Apostle":"An apostle","Priest":"A priest","Judge":"A judge",
              "Leader":"A leader of Israel","Other":"A notable figure"}
ALL_ROLES = list(set(ROLE_LABEL.values()))

for p in people:
    name = p["name"]; cat = p.get("category","Other")
    testament = p.get("testament")
    manna_cat = "Women of the Bible" if name in WOMEN else PERSON_CAT.get(cat, "Numbers & Genealogies")

    # 1. identify by description
    if p.get("description"):
        clue = first_sentence(p["description"])
        d = distractors([n for n in names_by_cat[cat] if n != name] or all_names, name)
        add(manna_cat, "Deacon",
            f"Which biblical figure is described here: \"{clue}\"",
            [name] + d, name, p.get("key_passage",""))

    # 2. also_known_as
    if p.get("also_known_as"):
        d = distractors(all_names, name)
        add(manna_cat, "Layperson",
            f"Which person in the Bible is also known as \"{p['also_known_as']}\"?",
            [name] + d, name, p.get("key_passage",""))

    # 3. role
    if cat in ROLE_LABEL:
        ans = ROLE_LABEL[cat]
        d = distractors(ALL_ROLES, ans)
        add(manna_cat, "Deacon",
            f"What role did {name} hold in the biblical narrative?",
            [ans] + d, ans, p.get("key_passage",""))

    # 4. testament
    if testament in ("OT","NT"):
        ans = "Old Testament" if testament=="OT" else "New Testament"
        add(manna_cat, "Layperson",
            f"In which part of the Bible do we mainly read about {name}?",
            [ans, "Old Testament", "New Testament", "Both Old and New Testaments", "Neither Testament"],
            ans, p.get("key_passage",""))

    # 5. key passage
    if p.get("key_passage"):
        d = distractors([x for x in all_passages if x != p["key_passage"]], p["key_passage"])
        add(manna_cat, "Pastor",
            f"Which passage is central to the account of {name}?",
            [p["key_passage"]] + d, p["key_passage"], "")

print(f"after PEOPLE: {len(out)}")

# ================================================================ PLACES
places = json.load(open(f"{LUMINA}/data/people_places/bible_places.json"))
place_names = [p["name"] for p in places]
modern_locs = [p.get("modern_location") for p in places if p.get("modern_location")]
place_cats  = list(set(p.get("category") for p in places if p.get("category")))

for p in places:
    name = p["name"]
    # type of place
    if p.get("category"):
        d = distractors(place_cats, p["category"])
        add("Places & Lands", "Layperson",
            f"What type of place is {name} in the Bible?",
            [p["category"]] + d, p["category"], p.get("key_passage",""))
    # modern location
    if p.get("modern_location"):
        d = distractors(modern_locs, p["modern_location"])
        add("Places & Lands", "Deacon",
            f"Where is the biblical site of {name} located today?",
            [p["modern_location"]] + d, p["modern_location"], p.get("key_passage",""))
    # testament
    if p.get("testament") in ("OT","NT"):
        ans = "Old Testament" if p["testament"]=="OT" else "New Testament"
        add("Places & Lands", "Layperson",
            f"The biblical place {name} is associated chiefly with which Testament?",
            [ans, "Old Testament","New Testament","Both Old and New Testaments","Neither Testament"],
            ans, p.get("key_passage",""))
    # describe -> name
    if p.get("description"):
        clue = first_sentence(p["description"])
        d = distractors(place_names, name)
        add("Places & Lands", "Deacon",
            f"Which biblical place is this: \"{clue}\"",
            [name] + d, name, p.get("key_passage",""))

print(f"after PLACES: {len(out)}")

# ================================================================ TIMELINE
tl = json.load(open(f"{LUMINA}/data/timeline/timeline_events.json"))
eras = sorted(set(t["era"] for t in tl))
titles = [t["title"] for t in tl]
tl_pass = [t.get("key_passage") for t in tl if t.get("key_passage")]

for t in tl:
    title = t["title"]; era = t["era"]
    mcat = ERA_CAT.get(era, "Prophecy & Fulfillment")
    # era
    add(mcat, "Deacon",
        f"In which era of biblical history did \"{title}\" take place?",
        [era] + distractors(eras, era), era, t.get("key_passage",""))
    # describe -> title
    if t.get("description"):
        clue = first_sentence(t["description"])
        add(mcat, "Deacon",
            f"Which biblical event does this describe: \"{clue}\"",
            [title] + distractors(titles, title), title, t.get("key_passage",""))
    # key passage
    if t.get("key_passage"):
        add(mcat, "Pastor",
            f"Which passage records the event known as \"{title}\"?",
            [t["key_passage"]] + distractors(tl_pass, t["key_passage"]),
            t["key_passage"], "")

print(f"after TIMELINE: {len(out)}")

# ================================================================ PARABLES
pa = json.load(open(f"{LUMINA}/data/parables/parables.json"))
ptitles = [p["title"] for p in pa]
pcats = sorted(set(p.get("category") for p in pa if p.get("category")))
ppass = [p.get("passage","").split(" \u00b7 ")[0] for p in pa if p.get("passage")]

for p in pa:
    title = p["title"]
    first_ref = p.get("passage","").split(" \u00b7 ")[0]
    # location
    if first_ref:
        add("Parables", "Layperson",
            f"Where is the Parable of {title} primarily found?",
            [first_ref] + distractors(ppass, first_ref), first_ref, "")
    # theme/category
    if p.get("category"):
        add("Parables", "Deacon",
            f"What is the central theme of the Parable of {title}?",
            [p["category"]] + distractors(pcats, p["category"]), p["category"], first_ref)
    # key verse text -> title
    if p.get("key_verse_text"):
        clue = first_sentence(p["key_verse_text"], 150)
        add("Parables", "Pastor",
            f"Which parable contains the words: \"{clue}\"",
            [title] + distractors(ptitles, title), title, p.get("key_verse",""))

print(f"after PARABLES: {len(out)}")

# ================================================================ GOSPEL -> OT LINKS
OT_BOOKS = ["Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth",
    "1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra","Nehemiah",
    "Esther","Job","Psalms","Proverbs","Ecclesiastes","Song of Solomon","Isaiah","Jeremiah",
    "Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah","Jonah","Micah","Nahum",
    "Habakkuk","Zephaniah","Haggai","Zechariah","Malachi"]
OT_SET = set(OT_BOOKS)

def load_links(fn):
    try:
        return json.load(open(f"{LUMINA}/data/backups/{fn}"))["entries"]
    except Exception:
        return {}

gospels = {"matthew":"Life of Jesus","mark":"Words of Jesus & OT Roots",
           "luke":"Words of Jesus & OT Roots","john":"Life of Jesus","acts":"The Apostles"}

link_qs = []
for g, mcat in gospels.items():
    entries = load_links(f"{g}-links-backup.json")
    refs = list(entries.keys())
    random.shuffle(refs)
    # build a pool of genuine OT target refs for distractors
    ot_target_pool = []
    for ref in refs:
        for a in entries[ref].get("anchors", []):
            for t in a.get("targets", []):
                if book_of(t["start"]) in OT_SET:
                    ot_target_pool.append(nice_ref(t["start"]))
    ot_target_pool = list(set(ot_target_pool))
    for ref in refs:
        e = entries[ref]
        for a in e.get("anchors", []):
            # pick the FIRST genuinely-OT target
            ot_t = next((t for t in a.get("targets", []) if book_of(t["start"]) in OT_SET), None)
            if not ot_t:
                continue
            target_ref  = nice_ref(ot_t["start"])
            target_book = book_of(ot_t["start"])
            src = nice_ref(ref)
            anchor = a.get("anchor","")
            if not anchor:
                continue
            # which OT passage is echoed
            link_qs.append((mcat, "Pastor",
                f"In {src}, the phrase \"{anchor}\" echoes which Old Testament passage?",
                target_ref, [x for x in ot_target_pool if x != target_ref], ot_t.get("reason","")))
            # which OT book
            link_qs.append((mcat, "Deacon",
                f"In {src}, the words \"{anchor}\" point back to which Old Testament book?",
                target_book, [b for b in OT_BOOKS if b != target_book], ot_t.get("reason","")))
            break  # one anchor per verse keeps variety high

random.shuffle(link_qs)
added_links = 0
for mcat, diff, q, correct, pool, reason in link_qs:
    if added_links >= 650:  # cap link questions so other types stay represented
        break
    exp = first_sentence(reason, 160) if reason else ""
    if add(mcat, diff, q, [correct] + distractors(pool, correct), correct, exp):
        added_links += 1

print(f"after GOSPEL LINKS: {len(out)} (links added: {added_links})")

# ================================================================ LAYPERSON recognition
recog = {"Apostle":("an apostle","The Apostles"),"King":("a king of Israel or Judah","Kings & Kingdoms"),
         "Prophet":("a prophet","Prophets"),"Patriarch":("a patriarch","Genesis & Creation"),
         "Judge":("a judge of Israel","Kings & Kingdoms"),"Priest":("a priest","Laws & Commandments")}
for cat,(label,mcat) in recog.items():
    members = names_by_cat.get(cat,[])
    others = [n for n in all_names if n not in members]
    random.shuffle(members)
    for correct in members:
        add(mcat, "Layperson",
            f"Which of the following people was {label}?",
            [correct] + distractors(others, correct), correct, "")

pcat_members = defaultdict(list)
for p in places: pcat_members[p.get("category")].append(p["name"])
for pcat, members in pcat_members.items():
    if not pcat: continue
    others = [n for n in place_names if n not in members]
    if len(others) < 3: continue
    random.shuffle(members)
    for correct in members:
        add("Places & Lands", "Layperson",
            f"Which of these biblical places was a {pcat.lower()}?",
            [correct] + distractors(others, correct), correct, "")

print(f"after RECOGNITION: {len(out)}")

# ================================================================ balance to 1200
random.shuffle(out)
TARGET = 1200
by_diff = defaultdict(list)
for q in out:
    by_diff[q["difficulty"]].append(q)
print("available by difficulty:", {k: len(v) for k, v in by_diff.items()})

# aim ~400 each, fall back to whatever is available
final = []
per = TARGET // 3
for diff in ("Layperson","Deacon","Pastor"):
    take = by_diff[diff][:per]
    final.extend(take)
# top up to 1200 from leftovers
leftovers = [q for q in out if q not in final]
random.shuffle(leftovers)
for q in leftovers:
    if len(final) >= TARGET:
        break
    final.append(q)
final = final[:TARGET]

from collections import Counter
print("\n=== FINAL V2 BANK ===")
print("total:", len(final))
print("by difficulty:", dict(Counter(q["difficulty"] for q in final)))
print("by category:", dict(Counter(q["category"] for q in final)))

json.dump(final, open(f"{MANNA}/manna_questions_v2.json","w"), indent=2, ensure_ascii=False)
print("\nwrote manna_questions_v2.json")
