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

- **40,000 unique, permanently numbered questions** in the shipping bank
- Spread across all 21 categories and 3 difficulty levels
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

## Tech Stack

- **iOS:** Native SwiftUI
- **Android:** Native Kotlin + Jetpack Compose
- **IAP:** StoreKit 2 and Google Play Billing
- **Questions:** Bundled JSON

## Project Status

- [x] Game design & categories
- [x] Question bank (40,000 questions)
- [x] Native iOS and Android apps
- [x] Logo/icon design
- [x] One-time Remove Ads purchase integration
- [x] Advertising integration

## Generation Scripts

The `scripts/` folder contains the generators, source audit, deterministic bank builder,
number lookup, and invariant validator. See `BUILDING.md` for the current workflow.
