# Manna — Bible Trivia Game

A Bible trivia iOS app modeled on the Bluff Trivia Game. Players wager tokens on their Bible knowledge across 20 categories and 3 difficulty levels.

## Game Concept

**Manna** (the bread God provided from heaven) — players earn tokens by answering Bible trivia correctly. Same wagering/bot mechanics as Bluff.

## Categories (20)

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

## Difficulty Levels

| Level | Description | Tokens |
|-------|-------------|--------|
| **Layperson** | Sunday School stories, well-known passages | +10 |
| **Deacon** | Real Bible reading knowledge, tricky details | +25 |
| **Pastor** | Seminary-level — minor prophets, genealogies, original language | +50 |

## Question Bank

- **2,640 unique questions** in `manna_questions.json`
- Spread across all 20 categories and 3 difficulty levels
- Each question has: category, difficulty, question text, 4 options, correct answer, optional explanation

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

## Tech Stack (planned)

- **iOS:** Swift + WKWebView (HTML/JS game engine) — same architecture as Bluff
- **Backend:** Cloudflare Workers + D1 (same as Bluff)
- **IAP:** StoreKit 2
- **Questions:** Bundled JSON

## Project Status

- [x] Game design & categories
- [x] Question bank (2,640 questions)
- [ ] iOS app (adapt from Bluff codebase)
- [ ] Logo/icon design
- [ ] StoreKit integration
- [ ] iCloud sync
- [ ] Ads
- [ ] Multiplayer

## Generation Scripts

The `scripts/` folder contains the Python scripts used to generate the question bank:
- `generate_all.py` — Base generation with data tables + templates
- `expand.py` through `expand5.py` — Expansion scripts adding more questions
