package com.oddcurrent.manna

import com.google.mlkit.nl.translate.TranslateLanguage
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

class LocalizationCoverageTest {
    @Test
    fun everyListedLanguageHasAUniqueSupportedTranslationModel() {
        val expected = setOf(
            "en", "ar", "zh", "da", "nl", "fr", "de", "hi", "id", "it", "ja",
            "ko", "no", "pl", "pt", "ru", "es", "sv", "th", "tr", "uk", "vi"
        )
        assertEquals(expected, languages.map { it.code }.toSet())
        assertEquals(expected.size, languages.size)
        languages.forEach { language ->
            assertTrue(language.nativeName.isNotBlank())
            assertTrue(language.englishName.isNotBlank())
            if (language.code != "en") {
                assertNotNull(
                    "No ML Kit model for ${language.englishName} (${language.code})",
                    TranslateLanguage.fromLanguageTag(language.code)
                )
            }
        }
    }

    @Test
    fun firstLaunchUsesTheFirstSupportedDeviceLanguage() {
        assertEquals("zh", detectedLanguageFromCodes(listOf("zh", "en")).code)
        assertEquals("ar", detectedLanguageFromCodes(listOf("ar", "fr")).code)
        assertEquals("no", detectedLanguageFromCodes(listOf("nb", "en")).code)
        assertEquals("es", detectedLanguageFromCodes(listOf("xx", "es", "en")).code)
        assertEquals("en", detectedLanguageFromCodes(listOf("xx")).code)
    }
}
