#!/usr/bin/env python3
"""Static localization contract shared by Apple and Android builds."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_LANGUAGES = {
    "en", "ar", "zh", "da", "nl", "fr", "de", "hi", "id", "it", "ja",
    "ko", "nb", "pl", "pt", "ru", "es", "sv", "th", "tr", "uk", "vi",
}


class LocalizationCoverageTests(unittest.TestCase):
    def test_apple_and_android_offer_the_same_22_languages(self) -> None:
        swift = (ROOT / "Manna/Services/LanguageManager.swift").read_text()
        android = (ROOT / "android/app/src/main/java/com/doctorosg/manna/Localization.kt").read_text()
        swift_codes = set(re.findall(r'\b\w+\s*=\s*"([^"]+)"', swift.split("var id:", 1)[0]))
        swift_codes = {"ar" if code == "ar-AE" else code for code in swift_codes}
        android_codes = set(re.findall(r'AppLanguage\("([^"]+)"', android.split(")\n\ninternal val LocalAppLanguage", 1)[0]))
        android_codes = {"nb" if code == "no" else code for code in android_codes}
        self.assertEqual(EXPECTED_LANGUAGES, swift_codes)
        self.assertEqual(EXPECTED_LANGUAGES, android_codes)
        self.assertEqual(22, len(swift_codes))

    def test_every_visible_apple_literal_routes_through_localization(self) -> None:
        offenders: list[str] = []
        call = re.compile(r'\b(Text|Label|Button|Picker|ProgressView)\(\s*"([^"]*)"')
        accessibility = re.compile(r'\.accessibilityLabel\(\s*"([^"]+)"')
        for path in sorted((ROOT / "Manna").rglob("*.swift")):
            if path.name == "LanguageManager.swift":
                continue
            for number, line in enumerate(path.read_text().splitlines(), 1):
                for match in call.finditer(line):
                    value = match.group(2)
                    visible = self._without_swift_interpolation(value)
                    if re.search(r"[A-Za-z]", visible) and value not in {"MANNA", "ABC123"}:
                        offenders.append(f"{path.relative_to(ROOT)}:{number}: {value}")
                if accessibility.search(line):
                    offenders.append(f"{path.relative_to(ROOT)}:{number}: raw accessibility label")
        self.assertEqual([], offenders, "Unlocalized Apple UI copy:\n" + "\n".join(offenders))

    def test_every_visible_android_literal_routes_through_localization(self) -> None:
        offenders: list[str] = []
        call = re.compile(r'\bText\(\s*"([^"]*)"')
        routed_markers = (
            "LocalizedOrLoadingText(",
            "coreUi(",
            "ui(",
            "language.displayName",
            "localizedQuestion",
        )
        source_root = ROOT / "android/app/src/main/java/com/doctorosg/manna"
        for path in sorted(source_root.rglob("*.kt")):
            if path.name == "Localization.kt":
                continue
            for number, line in enumerate(path.read_text().splitlines(), 1):
                if any(marker in line for marker in routed_markers):
                    continue
                for match in call.finditer(line):
                    value = match.group(1)
                    visible = re.sub(r'\$\{[^}]+\}|\$\w+', '', value)
                    if re.search(r"[A-Za-z]", visible) and value != "MANNA":
                        offenders.append(f"{path.relative_to(ROOT)}:{number}: {value}")
        self.assertEqual([], offenders, "Unlocalized Android UI copy:\n" + "\n".join(offenders))

    @staticmethod
    def _without_swift_interpolation(value: str) -> str:
        output: list[str] = []
        index = 0
        while index < len(value):
            if value.startswith("\\(", index):
                index += 2
                depth = 1
                while index < len(value) and depth:
                    if value[index] == "(":
                        depth += 1
                    elif value[index] == ")":
                        depth -= 1
                    index += 1
            else:
                output.append(value[index])
                index += 1
        return "".join(output)

    def test_every_question_field_uses_the_translation_pipeline(self) -> None:
        swift = (ROOT / "Manna/Services/LanguageManager.swift").read_text()
        for field in ("question.category", "question.question", "question.options", "question.explanation"):
            self.assertIn(field, swift)

        android = (ROOT / "android/app/src/main/java/com/doctorosg/manna/MainActivity.kt").read_text()
        self.assertIn(
            "listOf(question.category, question.question) + question.options + question.explanation",
            android,
        )

        party = (ROOT / "Manna/Views/PartyViews.swift").read_text()
        bonus = (ROOT / "Manna/Views/DoubleOrNothingView.swift").read_text()
        for expression in ("MannaText(question.question)", "MannaText(option)", "MannaText(question.explanation)"):
            self.assertIn(expression, party)
        self.assertIn("MannaText(question.question)", bonus)
        self.assertIn("MannaText(text)", bonus)

    def test_all_bundled_questions_have_translatable_questions_and_answers(self) -> None:
        apple_path = ROOT / "Manna/Resources/manna_questions.json"
        android_path = ROOT / "android/app/src/main/assets/manna_questions.json"
        apple = json.loads(apple_path.read_text())
        android = json.loads(android_path.read_text())
        self.assertEqual(apple, android)
        self.assertEqual(50020, len(apple))
        for index, item in enumerate(apple):
            self.assertTrue(item.get("category"), index)
            self.assertTrue(item.get("question"), index)
            self.assertGreaterEqual(len(item.get("options", [])), 2, index)
            self.assertTrue(all(isinstance(value, str) and value.strip() for value in item["options"]), index)
            self.assertIn(item.get("correct"), item["options"], index)
            self.assertIsInstance(item.get("explanation", ""), str, index)

    def test_arabic_uses_right_to_left_layout_on_both_platforms(self) -> None:
        apple = (ROOT / "Manna/App/MannaApp.swift").read_text()
        android = (ROOT / "android/app/src/main/java/com/doctorosg/manna/MainActivity.kt").read_text()
        self.assertIn(".rightToLeft", apple)
        self.assertIn('language.code == "ar"', android)
        self.assertIn("LayoutDirection.Rtl", android)

    def test_first_launch_detects_language_and_requires_its_model(self) -> None:
        apple_manager = (ROOT / "Manna/Services/LanguageManager.swift").read_text()
        apple_app = (ROOT / "Manna/App/MannaApp.swift").read_text()
        self.assertIn("Locale.preferredLanguages", apple_manager)
        self.assertIn("prepareTranslation()", apple_manager)
        self.assertIn("hasCompletedLanguageSetup", apple_app)
        self.assertIn("LanguagePackManagerView", apple_manager)

        android = (ROOT / "android/app/src/main/java/com/doctorosg/manna/MainActivity.kt").read_text()
        repository = (ROOT / "android/app/src/main/java/com/doctorosg/manna/Localization.kt").read_text()
        self.assertIn("LocaleList.getDefault()", android)
        self.assertIn("language_setup_complete", android)
        self.assertIn("LanguageManagerScreen", android)
        self.assertIn("downloadModelIfNeeded", repository)
        self.assertIn("isModelDownloaded", repository)


if __name__ == "__main__":
    unittest.main(verbosity=2)
