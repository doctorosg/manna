# Manna — Bible Trivia Game

A native iOS and Android Bible trivia game. Players wager tokens on their Bible knowledge across 21 categories and 3 difficulty levels.

## Game Concept

**Manna** (the bread God provided from heaven) — players earn tokens by answering Bible trivia correctly. Same wagering/bot mechanics as Bluff.

## Categories (21)

1. Genesis & Creation
2. Moses & the Exodus
3. Kings & Kingdoms
4. Prophets
5. Psalms & Proverbs
6. Life of Jesus
7. Miracles
8. Parables
9. The Apostles
10. Paul & His Letters
11. Revelation & End Times
12. Women of the Bible
13. Battles & Wars
14. Angels & Demons
15. Laws & Commandments
16. Prophecy & Fulfillment
17. Places & Lands
18. Numbers & Genealogies
19. Food, Feasts & Offerings
20. Dreams & Visions
21. Words of Jesus & OT Roots

## Difficulty Levels

| Level | Description | Tokens |
|-------|-------------|--------|
| **Layperson** | Sunday School stories, well-known passages | +10 |
| **Deacon** | Real Bible reading knowledge, tricky details | +25 |
| **Pastor** | Seminary-level — minor prophets, genealogies, original language | +50 |

## Question Bank

- **50,020 unique, permanently numbered questions** in the shipping bank: 40,020 adult questions plus 3,333 for ages 4–10 and 6,667 for ages 11–17
- Spread across all 21 categories and 3 difficulty levels
- Each question has: category, difficulty, question text, 2–4 options, correct answer, and an explanation/reference. Children's records also have an `ageGroup` field.

### Question Format

```json
{
  "id": "a1b2c3d4e5f6",
  "category": "Life of Jesus",
  "difficulty": "Layperson",
  "question": "Where was Jesus born?",
  "options": ["Bethlehem", "Nazareth", "Jerusalem", "Capernaum"],
  "correct": "Bethlehem",
  "explanation": ""
}
```

## Tech Stack

- **iOS:** Native SwiftUI
- **Android:** Native Kotlin + Jetpack Compose
- **IAP:** StoreKit 2 and Google Play Billing
- **Questions:** Bundled JSON

## Project Status

- [x] Game design & categories
- [x] Question bank (50,000 questions, including three children's age groups)
- [x] Native iOS and Android apps
- [x] Logo/icon design
- [x] One-time Remove Ads purchase integration
- [x] Advertising integration

## Generation Scripts

The `scripts/` folder contains the generators, source audit, deterministic bank builder,
number lookup, and invariant validator. See `BUILDING.md` for the current workflow.

The children's bank is reproducible from Lumina's local public-domain World
English Bible source. Ages 4–10 receive direct, three-choice questions about
familiar stories; ages 11–17 receive four-choice questions using short
modern-English excerpts plus curated direct trivia. Both groups pass safety and
readability checks:

```bash
python3 scripts/generate_children_questions.py
python3 scripts/build_question_bank.py
python3 scripts/validate_question_bank.py
```

The adult bank also includes newly worded, KJV-verified Deacon and Pastor
questions selected with A. Dana Adams's *4000 Questions and Answers on the
Bible* as a study guide. Rebuild that curated source with:

```bash
python3 scripts/generate_adams_adult_questions.py
```
# TV Display for Party Mode

The Party Mode host can tap the TV button after creating a room and open a large-format shared display. Connect the host phone before opening TV Display:

- iPhone: AirPlay Screen Mirroring, or a compatible Lightning/USB-C HDMI adapter.
- Android: Cast/Screen Cast, Samsung Smart View, Miracast/Screen Share, or a compatible USB-C HDMI adapter.
- Any television or projector with HDMI works through a compatible phone-to-HDMI adapter, including sets without smart-TV features.

Turn the host phone sideways for the TV layout. The display stays awake and shows the room code, questions, answer choices, response count, correct answer, round winners, and leaderboard. Other players answer on their own phones over the existing local Wi-Fi Party Mode connection; no TV backend is required.

## Optional 10,000-question expansion

Build 16 includes the purchase and download plumbing for a future permanent question expansion on both Apple and Google Play:

- Product ID: `com.oddcurrent.manna.question_pack_10000`
- Delivery URL: `https://downloads.oddcurrent.com/manna/question-pack-10000-v1.json`
- The offer stays hidden until the non-consumable product exists in the relevant store.
- After purchase or restore, Manna downloads the JSON once, requires exactly 10,000 unique valid questions, saves it atomically, and merges it into solo and Party Mode.
- The installed pack works offline. Failed downloads can be retried without purchasing again.

Before activating the product, publish the validated JSON at the delivery URL and create the same non-consumable product ID in App Store Connect and Google Play Console. Store pricing is controlled by each store and is intentionally not hard-coded in the app.
