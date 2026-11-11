#!/usr/bin/env python3
"""Deterministic, label-independent adult difficulty assessment for Manna.

The allocator combines explicit task-family rules with a 0-100 content score.
It is an editorial cold-start model, not a substitute for response-rate
calibration.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from statistics import mean


TIER_ORDER = {"Layperson": 0, "Deacon": 1, "Pastor": 2}
TIER_THRESHOLDS = ((43, "Layperson"), (68, "Deacon"), (101, "Pastor"))

OBSCURE_BOOKS = {
    "Leviticus", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah",
    "Ecclesiastes", "Song of Solomon", "Lamentations", "Hosea", "Joel",
    "Amos", "Obadiah", "Nahum", "Habakkuk", "Zephaniah", "Haggai",
    "Zechariah", "Malachi", "Micah", "2 Corinthians", "Colossians",
    "2 Thessalonians", "Titus", "Philemon", "2 Peter", "2 John",
    "3 John", "Jude", "Revelation",
}
INTERMEDIATE_BOOKS = {
    "Numbers", "Deuteronomy", "Judges", "1 Kings", "2 Kings", "Job",
    "Isaiah", "Jeremiah", "Ezekiel", "Romans", "1 Corinthians",
    "Galatians", "Ephesians", "Philippians", "1 Thessalonians",
    "1 Timothy", "2 Timothy", "Hebrews", "James", "1 Peter", "1 John",
}
FAMILIAR_BOOKS = {
    "Genesis", "Exodus", "Joshua", "Ruth", "1 Samuel", "2 Samuel",
    "Psalms", "Proverbs", "Esther", "Daniel", "Jonah", "Matthew", "Mark", "Luke",
    "John", "Acts",
}
ALL_BOOKS = OBSCURE_BOOKS | INTERMEDIATE_BOOKS | FAMILIAR_BOOKS

SPECIALIST_RE = re.compile(
    r"\b(?:church father|catena|strong['’]?s|lexicon|"
    r"septuagint|vulgate|masoretic|manuscript|textual|typology|eschatolog|"
    r"dispensation|covenant theology|hypostatic|kenosis|paraclete|theophany|"
    r"apocalyptic|intertestamental|synoptic|chiastic|hapax|exegesis)\b|\b[HG]\d{2,5}\b",
    re.I,
)
CROSS_REFERENCE_RE = re.compile(
    r"cross-reference|draws (?:from|on)|echoes|fulfilled|fulfillment|"
    r"old testament (?:root|passage)|quoted in|cited in|parallel account|"
    r"which passage|which prophecy",
    re.I,
)
SEQUENCE_RE = re.compile(
    r"chronolog|in order|first.*then|before.*after|how many generations|"
    r"which came first|sequence|during whose reign|successor|predecessor",
    re.I,
)
EXACT_TEXT_RE = re.compile(
    r"^(?:complete|where is this verse found|in which book .*verse found)|"
    r"accurately completes|exact (?:word|phrase)|according to .+ \d+:\d+",
    re.I,
)
SPECIFIC_DETAIL_RE = re.compile(
    r"\bhow many\b|\bwhat number\b|\bwhat color\b|\bwhat material\b|"
    r"\bwhich tribe\b|\bwhich king\b|\bwhich ruler\b|\bwhich relative\b|"
    r"\bwhich (?:chapter|verse|book|city|mountain|river|priest|prophet)\b|"
    r"\bname the\b|\bson of\b|\bdaughter of\b",
    re.I,
)
FAMILIAR_STORY_RE = re.compile(
    r"noah.{0,30}ark|david.{0,30}goliath|jonah.{0,30}(?:fish|whale)|"
    r"daniel.{0,30}lion|(?:born|birth).{0,30}bethlehem|red sea|"
    r"ten commandments|feeding.{0,20}(?:five thousand|5,?000)|"
    r"water into wine|garden of eden|adam and eve|walls? of jericho",
    re.I,
)
SCRIPTURE_REFERENCE_RE = re.compile(
    r"^(?:[1-3] )?[A-Za-z]+(?: [A-Za-z]+)* \d+:\d+(?:[-–]\d+)?$"
)
ORIGINAL_LANGUAGE_RE = re.compile(
    r"\b[HG]\d{2,5}\b|\b(?:hebrew|greek|aramaic) (?:word|term|lexicon)\b|"
    r"\bstrong['’]?s\b|\bseptuagint\b|\bvulgate\b|\bmasoretic\b",
    re.I,
)
CHURCH_FATHER_RE = re.compile(
    r"church father|catena aurea|\b(?:chrysostom|augustine|jerome|bede|origen|"
    r"ambrose|gregory|hilary|remigius|rabanus|basil|cyril|theophylact)\b",
    re.I,
)
INTERPRETATION_RE = re.compile(
    r"\b(?:symboli[sz]e[sd]?|represents?|interpretation|significance)\b|"
    r"^what is the meaning of (?:the|this)\b",
    re.I,
)
ADVANCED_CROSS_REFERENCE_RE = re.compile(
    r"stands behind|draws (?:from|on)|fulfilled in which|"
    r"old testament words .+ new testament passage|"
    r"which (?:old testament|new testament) (?:verse|passage|scripture)",
    re.I,
)
CONNECTION_CLASSIFICATION_RE = re.compile(
    r"what type of (?:link|connection)|shared theological theme|"
    r"^why is .+ linked|^what connects\b|what (?:ot|old testament) concept underlies",
    re.I,
)
SIMPLE_CROSS_REFERENCE_RE = re.compile(
    r"what (?:ot|old testament) book|which (?:book|gospel|prophet) "
    r"(?:shares|contains|is echoed|provides)|which prophet is echoed|"
    r"shares a connection with|contains a reference to",
    re.I,
)
BROAD_CROSS_REFERENCE_RE = re.compile(
    r"cross-reference|cross referenced|\bcross-references\b|\bconnected (?:to|by)\b|"
    r"\bconnection (?:to|with|links?)\b|\bconnects? to\b|\blinked to\b|\blinks? .+ (?:to|with)\b|"
    r"\bechoe?s?\b|\bhas roots in\b|\bprovides background\b|\bstands behind\b|"
    r"\bdraws (?:from|on)\b|\bfulfilled in\b|\breferences which\b|"
    r"\breferences a theme\b|\bshares a connection\b|\bpoints? back to\b",
    re.I,
)
TRADITIONAL_AUTHOR_RE = re.compile(
    r"traditional author|^who wrote\b|who is .* author", re.I
)
RARE_DETAIL_RE = re.compile(
    r"\bhow many\b|\bhow (?:old|long)\b|\bat what age\b|"
    r"\bwhat (?:color|material|wood|number|total|value|motive)\b|"
    r"\bwhich (?:relative|macedonian|earlier prophet|tribe|king|ruler)\b|"
    r"\bfrom which level\b|\bname of the\b|\bwhose (?:staff|rod|bed|garment)\b",
    re.I,
)
GENEALOGY_RE = re.compile(
    r"\bson of\b|\bdaughter of\b|\bfather of\b|\bmother of\b|\bgenealog",
    re.I,
)
VERSE_LOCATION_RE = re.compile(
    r"^where (?:in the bible |in scripture )?is .+ (?:found|recorded)|"
    r"^where is this verse found|^in which book of the bible is this verse found|"
    r"^in which of paul['’]?s letters is this verse found|"
    r"where in the bible is .+ (?:found|recorded)|"
    r"^in which book\(s\) does .+ (?:appear|occur)|"
    r"^which passage (?:records|is central)|^which parable contains the verse|"
    r"^what is the key verse of",
    re.I,
)
THEOLOGY_RE = re.compile(
    r"\b(?:noahide|firstfruits|atonement|justification|sanctification|"
    r"predestination|trinity|incarnation|eschatology|soteriology|ecclesiology|"
    r"covenant theology|dispensation|millennium|transubstantiation|typology)\b",
    re.I,
)
STUDY_TERM_RE = re.compile(
    r"\bkey (?:passage|verse)\b|\btribal name .+ mean\b|\bname ['’\"]?.+['’\"]? mean\b|"
    r"\bwhat language was .+ written\b|\bbook of the covenant\b|"
    r"\bmodern name or location\b|\b(?:heave offering|lex talionis)\b|"
    r"when is (?:pentecost|shavuot|passover|firstfruits)|"
    r"what did paul teach about the law",
    re.I,
)
ACADEMIC_STUDY_RE = re.compile(
    r"\b(?:pseudepigrapha|documentary hypothesis|prolepsis|hapax legomenon|"
    r"synoptic problem|textual criticism|source criticism)\b|^in the debate\b",
    re.I,
)
EXACT_DATE_RE = re.compile(
    r"\bwhen did\b|\bwhat (?:year|century|date|period|era)\b|"
    r"\b(?:b\.?c\.?e?|a\.?d\.?)\b",
    re.I,
)
FAMILIAR_ANSWERS = {
    "aaron", "abraham", "adam", "adam and eve", "bethlehem", "daniel",
    "david", "egypt", "elijah", "elisha", "eve", "gabriel", "genesis",
    "god", "holy spirit", "isaac", "israel", "jacob", "jericho", "jesus",
    "job", "john", "john the baptist", "jonah", "joseph", "joshua", "judas",
    "lazarus", "light", "mary", "mary magdalene", "michael", "moses",
    "noah", "paul", "peter", "pharaoh", "samson", "sarah", "saul",
    "solomon", "the red sea", "twelve", "twelve disciples",
}


@dataclass(frozen=True)
class DifficultyAssessment:
    score: int
    recommended: str
    confidence: str
    recall_obscurity: int
    task_complexity: int
    specificity: int
    distractor_competitiveness: int
    language_burden: int
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class AllocationDecision:
    tier: str
    confidence: str
    score: int
    family: str
    basis: tuple[str, ...]


def _mentioned_books(text: str) -> set[str]:
    return {
        book for book in ALL_BOOKS
        if re.search(rf"(?<![A-Za-z]){re.escape(book)}(?![A-Za-z])", text, re.I)
    }


def _option_shape(value: str) -> str:
    value = value.strip()
    if re.fullmatch(r"[\d,]+(?:\s+(?:years?|days?|men|people|souls?))?", value, re.I):
        return "number"
    if re.fullmatch(r"(?:[1-3] )?[A-Za-z ]+ \d+:\d+(?:-\d+)?", value):
        return "reference"
    words = re.findall(r"[A-Za-z]+", value)
    if 1 <= len(words) <= 4 and all(word[:1].isupper() for word in words):
        return "name"
    return "phrase"


def question_family(question: dict) -> str:
    prompt = str(question.get("question", ""))
    lowered = prompt.casefold()
    correct = str(question.get("correct", "")).strip()
    if CHURCH_FATHER_RE.search(prompt):
        return "Church Father attribution"
    if ORIGINAL_LANGUAGE_RE.search(prompt):
        return "Original-language lexicon"
    if CONNECTION_CLASSIFICATION_RE.search(prompt):
        return "Connection classification"
    if VERSE_LOCATION_RE.search(prompt):
        return "Verse location/book"
    if ADVANCED_CROSS_REFERENCE_RE.search(prompt) or (
        CROSS_REFERENCE_RE.search(prompt) and SCRIPTURE_REFERENCE_RE.fullmatch(correct)
    ):
        return "Exact cross-reference"
    if SIMPLE_CROSS_REFERENCE_RE.search(prompt) or "shares a connection" in lowered:
        return "Book-level cross-reference"
    if INTERPRETATION_RE.search(prompt):
        return "Symbolism or interpretation"
    if lowered.startswith("complete") or "accurately completes" in lowered:
        return "Exact completion"
    if BROAD_CROSS_REFERENCE_RE.search(prompt):
        if SCRIPTURE_REFERENCE_RE.fullmatch(correct):
            return "Exact cross-reference"
        return "Book-level cross-reference"
    if EXACT_DATE_RE.search(prompt) or SEQUENCE_RE.search(prompt):
        return "Chronology"
    if GENEALOGY_RE.search(prompt):
        return "Genealogy"
    if THEOLOGY_RE.search(prompt):
        return "Doctrine or theological term"
    if ACADEMIC_STUDY_RE.search(prompt):
        return "Academic biblical studies"
    if STUDY_TERM_RE.search(prompt):
        return "Study terminology"
    if RARE_DETAIL_RE.search(prompt):
        return "Specific-detail recall"
    if re.match(
        r"^(?:who|what|where|when|which|how|is|true or false|to which|at what)\b",
        prompt,
        re.I,
    ):
        return "Direct recall"
    return "Other"


def _distractor_score(options: list[str]) -> int:
    if len(options) < 3:
        return 0
    normalized_options = [re.sub(r"\W+", " ", option.casefold()).strip() for option in options]
    lengths = [max(1, len(option.split())) for option in normalized_options]
    score = 4 if len(options) == 4 else 2
    if len({_option_shape(option) for option in options}) == 1:
        score += 6
    if (max(lengths) - min(lengths)) / max(lengths) <= 0.45:
        score += 3
    similarities = [
        SequenceMatcher(None, left, right).ratio()
        for index, left in enumerate(normalized_options)
        for right in normalized_options[index + 1:]
    ]
    if similarities and mean(similarities) >= 0.28:
        score += 2
    return min(15, score)


def assess(question: dict) -> DifficultyAssessment:
    prompt = str(question.get("question", ""))
    answer = str(question.get("correct", ""))
    explanation = str(question.get("explanation", ""))
    options = [str(value) for value in question.get("options", [])]
    combined = f"{prompt} {answer} {explanation}"
    combined_choices = f"{prompt} {answer} {' '.join(options)}"
    reasons: list[str] = []

    books = _mentioned_books(combined)
    if books & OBSCURE_BOOKS:
        recall = 24
        reasons.append("obscure-book knowledge")
    elif books & INTERMEDIATE_BOOKS:
        recall = 15
        reasons.append("intermediate-canon knowledge")
    elif books & FAMILIAR_BOOKS:
        recall = 7
        reasons.append("familiar-book knowledge")
    else:
        recall = 11

    # Specialist burden is driven by what the player must interpret, not by a
    # Hebrew/Greek nationality word that happens to appear in an answer or
    # source quotation.
    specialist = bool(
        SPECIALIST_RE.search(prompt)
        or ORIGINAL_LANGUAGE_RE.search(prompt)
        or CHURCH_FATHER_RE.search(prompt)
    )
    advanced_cross_reference = bool(
        ADVANCED_CROSS_REFERENCE_RE.search(prompt)
        or CONNECTION_CLASSIFICATION_RE.search(prompt)
        or (BROAD_CROSS_REFERENCE_RE.search(prompt) and SCRIPTURE_REFERENCE_RE.fullmatch(answer.strip()))
    )
    simple_cross_reference = bool(
        SIMPLE_CROSS_REFERENCE_RE.search(prompt)
        or "shares a connection" in prompt.casefold()
    )
    interpretation = bool(INTERPRETATION_RE.search(prompt))
    cross_reference = advanced_cross_reference or simple_cross_reference or bool(
        CROSS_REFERENCE_RE.search(prompt) or BROAD_CROSS_REFERENCE_RE.search(prompt)
    )
    exact_text = bool(EXACT_TEXT_RE.search(prompt))
    sequence = bool(SEQUENCE_RE.search(prompt) or EXACT_DATE_RE.search(combined_choices))
    if specialist:
        recall = max(recall, 30)
        task = 25
        reasons.append("specialist language or source")
    elif interpretation:
        recall = max(recall, 24)
        task = 25
        reasons.append("symbolic or interpretive reasoning")
    elif advanced_cross_reference:
        recall = max(recall, 20)
        task = 25
        reasons.append("exact cross-reference reasoning")
    elif simple_cross_reference or cross_reference:
        task = 18
        reasons.append("book-level cross-reference reasoning")
    elif sequence:
        task = 22
        reasons.append("sequence or chronology")
    elif exact_text:
        task = 15
        reasons.append("exact-text retrieval")
    elif re.match(r"^(?:who|what|where|when|which|how many)\b", prompt, re.I):
        task = 6
        reasons.append("direct factual recall")
    else:
        task = 11

    specificity = 5
    if SPECIFIC_DETAIL_RE.search(prompt):
        specificity = 15
        reasons.append("specific detail required")
    if RARE_DETAIL_RE.search(prompt):
        specificity = 20
        task = max(task, 10)
        reasons.append("rare or exact detail required")
    if re.search(r"\b(?:chapter|verse)\s+\d+|\d+:\d+", prompt):
        specificity = max(specificity, 17)
        reasons.append("chapter-and-verse precision")
    if exact_text:
        specificity = max(specificity, 15)
    if sequence:
        specificity = max(specificity, 20 if EXACT_DATE_RE.search(combined_choices) else 16)
    if len(re.findall(r"\b[A-Z][a-z]+\b", answer)) >= 3 or len(answer.split()) >= 9:
        specificity = min(20, specificity + 3)

    distractors = _distractor_score(options)
    if distractors >= 10:
        reasons.append("closely shaped answer choices")

    prompt_words = re.findall(r"[A-Za-z]+", prompt)
    average_word_length = mean(map(len, prompt_words)) if prompt_words else 0
    language = 1
    if len(prompt_words) >= 18:
        language += 2
    if len(prompt_words) >= 28:
        language += 2
    if average_word_length >= 5.2:
        language += 2
    if average_word_length >= 6.0:
        language += 1
    if specialist:
        language += 2
    language = min(10, language)

    if FAMILIAR_STORY_RE.search(prompt) and task <= 11 and specificity <= 15:
        recall = max(0, recall - 7)
        task = max(0, task - 2)
        reasons.append("widely familiar story cue")

    score = min(100, recall + task + specificity + distractors + language)
    recommended = next(tier for upper, tier in TIER_THRESHOLDS if score < upper)
    distance = min(abs(score - 43), abs(score - 68))
    confidence = "high" if distance >= 9 else "medium" if distance >= 4 else "low"
    return DifficultyAssessment(
        score=score,
        recommended=recommended,
        confidence=confidence,
        recall_obscurity=recall,
        task_complexity=task,
        specificity=specificity,
        distractor_competitiveness=distractors,
        language_burden=language,
        reasons=tuple(reasons),
    )


def allocate_difficulty(question: dict, answer_frequency: int = 1) -> AllocationDecision:
    """Allocate one adult question using task rules plus the content score.

    `answer_frequency` is computed over the adult bank and acts only as a
    familiarity signal for direct, specific-detail questions.
    """
    prompt = str(question.get("question", ""))
    answer = str(question.get("correct", "")).strip()
    answer_key = re.sub(r"[^a-z0-9]+", " ", answer.casefold()).strip()
    assigned = str(question.get("difficulty", "Deacon"))
    family = question_family(question)
    assessment = assess(question)
    basis: list[str] = []

    if family in {
        "Academic biblical studies",
        "Church Father attribution",
        "Original-language lexicon",
        "Connection classification",
        "Exact cross-reference",
    }:
        basis.append(f"{family} requires specialist interpretation or source knowledge")
        return AllocationDecision("Pastor", "high", assessment.score, family, tuple(basis))

    if family == "Symbolism or interpretation":
        books = _mentioned_books(f"{prompt} {question.get('explanation', '')}")
        tier = "Pastor" if books & (OBSCURE_BOOKS | INTERMEDIATE_BOOKS) or assessment.score >= 68 else "Deacon"
        basis.append("symbolic interpretation is tiered by canonical context and content burden")
        return AllocationDecision(tier, "medium", assessment.score, family, tuple(basis))

    combined_choices = f"{prompt} {answer} {' '.join(str(v) for v in question.get('options', []))}"
    if (family == "Chronology" or prompt.casefold().startswith("when ")) and EXACT_DATE_RE.search(combined_choices):
        basis.append("exact historical dating is specialist knowledge")
        return AllocationDecision("Pastor", "high", assessment.score, family, tuple(basis))

    if family == "Chronology":
        if assigned == "Layperson":
            basis.append("introductory source label retained for non-date event ordering")
            return AllocationDecision("Layperson", "high", assessment.score, family, tuple(basis))
        basis.append("canonical sequence knowledge beyond one-step introductory recall")
        return AllocationDecision("Deacon", "high", assessment.score, family, tuple(basis))

    if family == "Book-level cross-reference":
        basis.append("identifying a linked book or prophet is an intermediate canonical task")
        tier = "Pastor" if assessment.score >= 74 else "Deacon"
        confidence = "medium" if tier == "Pastor" else "high"
        return AllocationDecision(tier, confidence, assessment.score, family, tuple(basis))

    if family == "Exact completion":
        basis.append("verbatim verse completion is above introductory recall")
        tier = "Pastor" if assessment.score >= 72 else "Deacon"
        return AllocationDecision(tier, "medium", assessment.score, family, tuple(basis))

    if family == "Verse location/book":
        basis.append("locating an unattributed verse is above introductory recall")
        unattributed_text = bool(re.search(r"this verse|following verse|^where is ['\"]", prompt, re.I))
        tier = "Pastor" if assessment.score >= 72 or (
            SCRIPTURE_REFERENCE_RE.fullmatch(answer) and unattributed_text
        ) else "Deacon"
        return AllocationDecision(tier, "high", assessment.score, family, tuple(basis))

    if TRADITIONAL_AUTHOR_RE.search(prompt):
        if answer_key in FAMILIAR_ANSWERS and not (_mentioned_books(prompt) & OBSCURE_BOOKS):
            basis.append("familiar authorship question")
            return AllocationDecision("Layperson", "high", assessment.score, family, tuple(basis))
        basis.append("less-familiar canonical authorship question")
        return AllocationDecision("Deacon", "high", assessment.score, family, tuple(basis))

    if family in {"Doctrine or theological term", "Study terminology"}:
        basis.append("doctrinal vocabulary requires more than introductory story recall")
        tier = "Pastor" if assessment.score >= 68 else "Deacon"
        return AllocationDecision(tier, "medium", assessment.score, family, tuple(basis))

    familiar = bool(FAMILIAR_STORY_RE.search(prompt))
    rare_detail = bool(RARE_DETAIL_RE.search(prompt))
    books = _mentioned_books(combined := f"{prompt} {question.get('explanation', '')}")

    if family == "Genealogy":
        if familiar and answer_frequency >= 5:
            basis.append("familiar family relationship")
            return AllocationDecision("Layperson", "medium", assessment.score, family, tuple(basis))
        basis.append("canonical genealogy beyond introductory story recall")
        return AllocationDecision("Deacon", "high", assessment.score, family, tuple(basis))

    if family in {"Direct recall", "Specific-detail recall", "Other", "Chronology"}:
        if family == "Direct recall" and familiar and not rare_detail and not sequence_requires_precision(prompt):
            basis.append("one-step recall of a widely familiar person, place, or story")
            return AllocationDecision("Layperson", "high", assessment.score, family, tuple(basis))
        if rare_detail:
            if answer_frequency <= 2 and not FAMILIAR_STORY_RE.search(prompt):
                basis.append("rare answer plus an exact canonical detail")
                return AllocationDecision("Pastor", "medium", assessment.score, family, tuple(basis))
            basis.append("specific canonical detail beyond basic story recall")
            return AllocationDecision("Deacon", "high", assessment.score, family, tuple(basis))
        if family == "Direct recall":
            if assigned == "Layperson" and assessment.score < 50:
                basis.append("introductory source label corroborated by a low content score")
                return AllocationDecision("Layperson", "medium", assessment.score, family, tuple(basis))
            if assigned == "Deacon" and assessment.score < 43:
                basis.append("low-burden one-step recall from an intermediate source label")
                return AllocationDecision("Layperson", "medium", assessment.score, family, tuple(basis))
            basis.append("canonical recall without a strong introductory familiarity cue")
            tier = "Pastor" if assessment.score >= 74 else "Deacon"
            return AllocationDecision(tier, "medium", assessment.score, family, tuple(basis))
        if family in {"Other", "Chronology"}:
            if assigned == "Layperson" and assessment.score < 50:
                basis.append("introductory source label corroborated by a low content score")
                return AllocationDecision("Layperson", "low", assessment.score, family, tuple(basis))
            if assessment.score < 43:
                basis.append("low content score without enough evidence for introductory placement")
                return AllocationDecision("Deacon", "low", assessment.score, family, tuple(basis))

    basis.append("content score resolves an unanchored task")
    return AllocationDecision(
        assessment.recommended,
        assessment.confidence,
        assessment.score,
        family,
        tuple(basis),
    )


def sequence_requires_precision(prompt: str) -> bool:
    return bool(SEQUENCE_RE.search(prompt) or EXACT_DATE_RE.search(prompt))
