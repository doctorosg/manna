package com.oddcurrent.manna

import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class OnDeviceTranslationTest {
    @Test
    fun everyLanguageProducesRealTranslatedText() = runBlocking {
        val repository = TranslationRepository(ApplicationProvider.getApplicationContext())
        val source = "Start the Bible trivia game"
        try {
            languages.forEach { language ->
                val translated = withTimeout(180_000) {
                    repository.translate(source, language.code)
                }
                assertTrue("Blank translation for ${language.englishName}", translated.isNotBlank())
                if (language.code == "en") {
                    assertEquals(source, translated)
                } else {
                    assertFalse(
                        "Unchanged translation for ${language.englishName}",
                        source.equals(translated, ignoreCase = true)
                    )
                }
            }
        } finally {
            repository.close()
        }
    }

    @Test
    fun everyLanguageTranslatesACompleteQuestionAndAllAnswers() = runBlocking {
        val repository = TranslationRepository(ApplicationProvider.getApplicationContext())
        val source = listOf(
            "Life of Jesus",
            "Who was the mother of Jesus?",
            "Mary",
            "Martha",
            "Elizabeth",
            "Ruth",
            "Mary was the mother of Jesus according to the Gospel accounts."
        )
        try {
            languages.forEach { language ->
                val translated = withTimeout(180_000) {
                    repository.translate(source, language.code)
                }
                assertEquals("Incomplete question translation for ${language.englishName}", source.size, translated.size)
                translated.forEachIndexed { index, value ->
                    assertTrue("Blank field $index for ${language.englishName}", value.isNotBlank())
                }
                if (language.code == "en") {
                    assertEquals(source, translated)
                } else {
                    assertFalse(
                        "Question stayed entirely English for ${language.englishName}",
                        source == translated
                    )
                }
            }
        } finally {
            repository.close()
        }
    }
}
