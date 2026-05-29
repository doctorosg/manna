# MANNA BIBLE TRIVIA — HANDOFF DOCUMENT
**Date:** May 29, 2026  
**Developer:** Silvano Guzzo  
**GitHub:** `doctorosg/manna` (private)  
**GitHub Token:** Ask Silvano for current PAT

---

## 1. PROJECT OVERVIEW

Manna is an iOS Bible trivia app built in SwiftUI. Solo game — no multiplayer, no rankings, no tokens. 5 questions per session across 21 categories and 3 difficulty levels. Tracks performance and provides personalized study suggestions.

**Business Model:** Free 7-day trial → $4.99 one-time purchase. Future versions (Vol 2, Vol 3) with different question sets at $4.99 each. No ads, no IAP token shop.

**Architecture:** Native Swift/SwiftUI iOS app. Adapted from the Bluff Trivia Game (`doctorosg/bluff`) but rebuilt without tokens, rankings, or multiplayer. Uses XcodeGen for project generation.

---

## 2. BUILD & RUN

```bash
cd ~/Desktop/manna
git pull
xcodegen generate      # requires: brew install xcodegen
open Manna.xcodeproj
# In Xcode: ⇧⌘K (clean) then ⌘R (run)
```

**Bundle ID:** `com.doctorosg.manna`  
**Team ID:** `28WGFPLAHZ`  
**Deployment Target:** iOS 17.0  
**XcodeGen spec:** `project.yml` at repo root

---

## 3. FILE STRUCTURE

```
manna/
├── project.yml                          # XcodeGen project spec
├── setup.sh                             # One-command build script
├── manna_questions.json                 # Master question bank (14,507 questions)
├── HANDOFF.md                           # This file
├── scripts/                             # Question generation scripts (Python)
│   ├── generate_all.py                  # Base questions with data tables
│   ├── expand.py → expand5.py           # Handwritten expansions
│   ├── gen_jesus_ot.py                  # 530 Jesus→OT questions
│   ├── gen_from_lumina.py               # Hebrew/Greek/people/places/timeline
│   ├── gen_deep_lumina.py               # Expanded lexicons, parables, theology
│   ├── gen_layperson.py                 # 355 Layperson questions
│   ├── gen_1000_more.py                 # Catena Aurea + more OT + lexicons
│   ├── gen_systematic_links.py          # 3,519 from 10 question patterns
│   └── gen_session2.py                  # 3,519 from all Gospel→OT + OT xrefs
│
├── Manna/
│   ├── App/
│   │   ├── MannaApp.swift               # @main entry point
│   │   └── ContentView.swift            # Root router (AppState switch)
│   │
│   ├── Models/
│   │   ├── Category.swift               # 21 categories with emoji, color, description
│   │   ├── DifficultyLevel.swift        # Layperson / Deacon / Pastor
│   │   ├── Player.swift                 # Player, AppState enum, GameMode enum
│   │   └── Question.swift               # MannaQuestion, PlayerAnswer, RoundResult, BotAnswer
│   │
│   ├── Services/
│   │   ├── AuthManager.swift            # Auto guest sign-in (Apple Sign In stubbed)
│   │   ├── BotService.swift             # Cosmetic bot opponents (names, flags)
│   │   ├── PerformanceTracker.swift     # Stats by category/difficulty, trends, study tips
│   │   ├── QuestionCache.swift          # Smart caching: tracks correct/wrong for refeeding
│   │   ├── QuestionService.swift        # Loads from bundle, smart selection, marks correct/wrong
│   │   └── SoundManager.swift           # Audio (correct/wrong/wager sounds)
│   │
│   ├── ViewModels/
│   │   └── GameManager.swift            # Core game logic, timer, state machine
│   │
│   ├── Views/
│   │   ├── HomeView.swift               # Falling manna animation, scripture quote, PLAY
│   │   ├── PreGameView.swift            # Wraps category → difficulty flow
│   │   ├── CategorySelectionView.swift  # Multi-select grid, Select All, instructions
│   │   ├── DifficultySelectionView.swift # Layperson/Deacon/Pastor cards
│   │   ├── GameView.swift               # Question display, timer, countdown, answers
│   │   ├── PerformanceView.swift        # 3 tabs: Categories, Difficulty, Improve
│   │   ├── DoubleOrNothingView.swift    # Bonus Challenge (offered at 3+/5 correct)
│   │   ├── SignInView.swift             # Apple Sign In + guest (auto-bypass for MVP)
│   │   └── SupportingViews.swift        # SplashView, ResultView, SettingsView
│   │
│   ├── Resources/
│   │   ├── manna_questions.json         # Bundled question bank (copy of root file)
│   │   └── Assets.xcassets/             # App icon, colors, challah image
│   │       ├── AppIcon.appiconset/      # 1024x1024 challah bread on navy
│   │       └── challah.imageset/        # Challah bread PNG (transparent bg)
│   │
│   └── Supporting/
│       └── Info.plist
```

---

## 4. QUESTION BANK

**Total: 14,507 questions**

| Difficulty | Count | Description |
|---|---|---|
| Layperson | 2,645 | Sunday School — well-known stories, famous verses |
| Deacon | 5,250 | Regular Bible reader — details, context, connections |
| Pastor | 6,612 | Seminary-level — Hebrew/Greek, Church Fathers, textual criticism |

### Question JSON Format
```json
{
  "id": "a1b2c3d4e5f6",
  "category": "Genesis & Creation",
  "difficulty": "Layperson",
  "question": "What did God do on the seventh day?",
  "options": ["He created humans", "He rested", "He created the sea", "He created the sun"],
  "correct": "He rested",
  "explanation": "Genesis 2:2-3"
}
```

### 21 Categories
Genesis & Creation, Moses & the Exodus, Kings & Kingdoms, Prophets, Psalms & Proverbs, Life of Jesus, Miracles, Parables, The Apostles, Paul & His Letters, Revelation & End Times, Women of the Bible, Battles & Wars, Angels & Demons, Laws & Commandments, Prophecy & Fulfillment, Places & Lands, Numbers & Genealogies, Food/Feasts/Offerings, Dreams & Visions, Words of Jesus & OT Roots

### Question Sources (from Lumina Bible data)
All scripts read from `doctorosg/lumina-bible` (private repo) at `/home/claude/lumina-bible/data/`:

| Source | Entries | Location |
|---|---|---|
| Gospel→OT links | 22,429 | `backups/{matthew,mark,luke,john}-links-backup.json` |
| OT cross-references (TSK) | ~50K+ | `ot_links_output/*.json` (928 files) |
| Catena Aurea (Church Fathers) | 11,145 | `commentaries/catena-aurea-project/catena_aurea_graph.json` |
| Hebrew lexicon | 8,853 | `lexicons/lexicon-hebrew.json` |
| Greek lexicon | 5,843 | `lexicons/lexicon-greek.json` |
| Bible people | 82 | `people_places/bible_people.json` |
| Bible places | 48 | `people_places/bible_places.json` |
| Timeline events | 68 | `timeline/timeline_events.json` |
| Parables | 40 | `parables_new.json` |
| Theological debates | 14 | `debates/debates.json` |

**Remaining capacity:** ~17,000+ Gospel→OT connections untapped, ~600+ OT cross-ref files unused, ~10,700 Church Father commentaries unused. Estimated 30,000+ more questions possible.

---

## 5. KEY FEATURES

### Game Flow
1. Home screen → falling manna animation + scripture quote (2 Timothy 3:16)
2. Multi-select categories (with Select All) → choose difficulty
3. 5 questions with 20-second timer per question
4. Last 5 seconds: big red countdown overlay
5. Timeout: "Time's Up!" → auto-advances, does NOT show answer
6. Results: percentage (48pt), letter grade (A/B/C/D/F), round breakdown
7. Bonus Challenge offered at 3+/5 correct
8. Level Up Challenge offered only at 80%+ accuracy AND 3+ questions answered

### Smart Question Refeeding
- Wrong answers tracked and prioritized back into pool
- Correct answers removed from future pool
- Priority order: wrong (refeed) → unseen → remaining
- Persisted in UserDefaults across sessions

### Performance Tracking (My Stats)
- **Categories tab:** % correct per category with progress bars and trend arrows (improving ↗ / declining ↘ / steady →)
- **Difficulty tab:** Layperson/Deacon/Pastor comparison with recommendations
- **Improve tab:** Personalized study suggestions per category (e.g., "Reread the story of the golden calf and focus on who the important characters are")
- Each category has 3 specific study tips in `PerformanceTracker.swift`

### Bot Opponents (cosmetic)
- 4 bots per session with Bible-themed names (FaithWalker, ScrollSeeker, etc.)
- Simulate answers based on difficulty — no competitive element
- Present for visual interest only

---

## 6. WHAT'S REMOVED (from Bluff)

- ❌ Token economy (TokenManager, tokens, wagering, win/place/show)
- ❌ Token shop (IAP for tokens)
- ❌ Rankings / Leaderboard
- ❌ StoreManager (StoreKit IAP)
- ❌ CloudflareService (no backend)
- ❌ LeaderboardManager
- ❌ Multiplayer / competitive features

---

## 7. APP ICON & BRANDING

- **App icon:** 1024×1024 PNG — navy background, gold "MANNA" text, cross, falling challah shapes
- **In-app logo:** Falling golden manna flakes animation on home screen (not static image)
- **Challah image:** `Assets.xcassets/challah.imageset/challah.png` — braided bread, transparent bg (used in splash/sign-in)
- **Color scheme:** Deep navy (#0F1223) background, gold (#D4A843) accents
- **Font:** System serif for "MANNA", rounded for UI

---

## 8. PENDING / KNOWN ISSUES

### Layout Bug (Active)
Category selection page has too much empty space at top. The "Choose Categories" header appears ~1/3 down the screen despite code fixes. Root cause likely: safe area insets on Dynamic Island iPhones combined with VStack centering. Last fix attempt: `frame(maxHeight: .infinity, alignment: .top)` on ContentView and PreGameView. May need `.ignoresSafeArea(edges: .top)` with manual status bar padding.

### Pending Features
- [ ] **Fix layout positioning** — content must start at top of screen on category/difficulty pages
- [ ] **Generate ~7,000 more questions** from remaining Lumina data (~17K+ Gospel→OT connections untapped, ~600 OT cross-ref files remaining)
- [ ] **1,000 Church Father questions** distributed at Deacon/Pastor levels
- [ ] **7-day free trial + $4.99 paywall** implementation (StoreKit)
- [ ] **iCloud sync** for performance data
- [ ] **App Store listing** preparation
- [ ] **TestFlight** beta distribution (same process as Bluff, same team ID)
- [ ] **Professional logo** refinement (current is Pillow-generated)
- [ ] **Onboarding flow** for first-time users

### Version Planning
- **Vol 1:** ~10,000 questions (first App Store release)
- **Vol 2:** Different 10,000 questions, same app architecture, $4.99
- **Vol 3:** etc.
- Current bank (14,507) covers Vol 1 with leftovers for Vol 2 seed

---

## 9. GIT HISTORY (recent)

```
27d867c Fix layout — force content to top with frame alignment
8aca93a Fix all UX issues from testing
3ca8366 Fix guard fallthrough in QuestionService
32e8a1c Major UX overhaul based on testing feedback
ea65143 Major refactor: Remove tokens/rankings, add Performance page
d8e2aa2 Replace bread emoji with challah image on all screens
dba5c73 Session 2: +3,519 questions — total 14,507
8ab3945 Update logo: challah bread instead of generic bread shapes
173c15a Break 10K — systematic mining adds 3,659 questions
5030e61 Add 355 new Layperson questions — total now 7,329
d7501ac Add 1,369 more questions — Catena Aurea + deep OT cross-refs
28c1dc3 Add 1,771 new questions from deep Lumina mining
35b7a6e Add 664 new questions from Lumina data — Pastor level boosted
2d819ba Fix Double or Nothing — add question phase UI
887a9ed Add app icon + increase timer to 20 seconds
24eaa35 Fix startup: remove auth gate, start directly at home
3aece24 Complete iOS app — Manna Bible Trivia
```

---

## 10. ENVIRONMENT

- **Xcode:** 15+ required
- **Swift:** 5.9
- **iOS target:** 17.0
- **XcodeGen:** Required (`brew install xcodegen`)
- **Mac path:** `~/Desktop/manna`
- **Xcode project:** `~/Desktop/manna/Manna.xcodeproj` (generated, not committed)

---

## 11. QUESTION GENERATION WORKFLOW

To generate more questions from Lumina data:

```python
# 1. Clone lumina-bible repo
git clone https://github.com/doctorosg/lumina-bible.git

# 2. Write a generation script in manna/scripts/
# 3. Script reads from lumina-bible/data/
# 4. Appends to manna_questions.json
# 5. Copy to bundle: cp manna_questions.json Manna/Resources/manna_questions.json
# 6. Rebuild in Xcode

# Key data paths:
# Gospel→OT:  lumina-bible/data/backups/{gospel}-links-backup.json
# TSK:        lumina-bible/ot_links_output/*.json
# Catena:     lumina-bible/data/commentaries/catena-aurea-project/catena_aurea_graph.json
# Lexicons:   lumina-bible/data/lexicons/lexicon-{hebrew,greek}.json
```

### Question Patterns Used (can generate more of each)
1. "Which OT book does [Gospel phrase] echo?" — used ~2,500, capacity ~20K+
2. "Which Gospel references [OT passage]?" — used ~600, capacity ~10K+
3. "What type of connection? (quote/allusion/type)" — used ~500, capacity ~5K+
4. "Why are [source] and [target] connected?" — used ~400, capacity ~10K+
5. "Which prophet is echoed in [Gospel verse]?" — used ~400, capacity ~3K+
6. "What does Hebrew/Greek word X mean?" — used ~600, capacity ~10K+
7. "Which Church Father wrote about [verse]?" — used ~900, capacity ~10K+
8. "What is the significance of [place]?" — used ~50, capacity ~200+
9. "When did [event] occur?" — used ~100, capacity ~200+
10. "What connects [OT passage A] to [OT passage B]?" — used ~800, capacity ~20K+

---

## 12. RELATED REPOS

| Repo | Description |
|---|---|
| `doctorosg/manna` | This app |
| `doctorosg/lumina-bible` | Bible data (cross-refs, lexicons, commentaries) |
| `doctorosg/bluff` | Original trivia game this was adapted from |
| `doctorosg/vector` | Board game (separate project) |
| `doctorosg/Schengen` | Travel tracker (separate project) |
