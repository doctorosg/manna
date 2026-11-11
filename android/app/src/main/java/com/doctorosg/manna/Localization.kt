package com.oddcurrent.manna

import android.content.Context
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.staticCompositionLocalOf
import com.google.mlkit.common.model.DownloadConditions
import com.google.mlkit.common.model.RemoteModelManager
import com.google.mlkit.nl.translate.TranslateLanguage
import com.google.mlkit.nl.translate.Translation
import com.google.mlkit.nl.translate.Translator
import com.google.mlkit.nl.translate.TranslatorOptions
import com.google.mlkit.nl.translate.TranslateRemoteModel
import kotlinx.coroutines.tasks.await
import java.security.MessageDigest

internal data class AppLanguage(val code: String, val nativeName: String, val englishName: String) {
    val displayName: String get() = nativeName
}

internal val languages = listOf(
    AppLanguage("en", "English", "English"), AppLanguage("ar", "العربية", "Arabic"),
    AppLanguage("zh", "简体中文", "Simplified Chinese"), AppLanguage("da", "Dansk", "Danish"),
    AppLanguage("nl", "Nederlands", "Dutch"), AppLanguage("fr", "Français", "French"),
    AppLanguage("de", "Deutsch", "German"), AppLanguage("hi", "हिन्दी", "Hindi"),
    AppLanguage("id", "Bahasa Indonesia", "Indonesian"), AppLanguage("it", "Italiano", "Italian"),
    AppLanguage("ja", "日本語", "Japanese"), AppLanguage("ko", "한국어", "Korean"),
    AppLanguage("no", "Norsk bokmål", "Norwegian"), AppLanguage("pl", "Polski", "Polish"),
    AppLanguage("pt", "Português", "Portuguese"), AppLanguage("ru", "Русский", "Russian"),
    AppLanguage("es", "Español", "Spanish"), AppLanguage("sv", "Svenska", "Swedish"),
    AppLanguage("th", "ไทย", "Thai"), AppLanguage("tr", "Türkçe", "Turkish"),
    AppLanguage("uk", "Українська", "Ukrainian"), AppLanguage("vi", "Tiếng Việt", "Vietnamese")
)

internal val LocalAppLanguage = staticCompositionLocalOf { languages.first() }
internal val LocalTranslationRepository = staticCompositionLocalOf<TranslationRepository> {
    error("TranslationRepository was not provided")
}

private val coreUiText = mapOf(
    "play" to mapOf(
        "en" to "PLAY", "ar" to "العب", "zh" to "开始", "da" to "SPIL", "nl" to "SPELEN",
        "fr" to "JOUER", "de" to "SPIELEN", "hi" to "खेलें", "id" to "MAIN", "it" to "GIOCA",
        "ja" to "プレイ", "ko" to "플레이", "no" to "SPILL", "pl" to "GRAJ", "pt" to "JOGAR",
        "ru" to "ИГРАТЬ", "es" to "JUGAR", "sv" to "SPELA", "th" to "เล่น", "tr" to "OYNA",
        "uk" to "ГРАТИ", "vi" to "CHƠI"
    ),
    "settings" to mapOf(
        "en" to "Settings", "ar" to "الإعدادات", "zh" to "设置", "da" to "Indstillinger", "nl" to "Instellingen",
        "fr" to "Réglages", "de" to "Einstellungen", "hi" to "सेटिंग्स", "id" to "Pengaturan", "it" to "Impostazioni",
        "ja" to "設定", "ko" to "설정", "no" to "Innstillinger", "pl" to "Ustawienia", "pt" to "Definições",
        "ru" to "Настройки", "es" to "Ajustes", "sv" to "Inställningar", "th" to "การตั้งค่า", "tr" to "Ayarlar",
        "uk" to "Налаштування", "vi" to "Cài đặt"
    ),
    "party_mode" to mapOf(
        "en" to "Party Mode", "ar" to "وضع المجموعة", "zh" to "聚会模式", "da" to "Gruppespil", "nl" to "Groepsmodus",
        "fr" to "Mode groupe", "de" to "Gruppenmodus", "hi" to "समूह मोड", "id" to "Mode Grup", "it" to "Modalità gruppo",
        "ja" to "グループモード", "ko" to "그룹 모드", "no" to "Gruppemodus", "pl" to "Tryb grupowy", "pt" to "Modo de grupo",
        "ru" to "Групповой режим", "es" to "Modo de grupo", "sv" to "Gruppläge", "th" to "โหมดกลุ่ม", "tr" to "Grup Modu",
        "uk" to "Груповий режим", "vi" to "Chế độ nhóm"
    )
)

internal fun coreUi(key: String, language: AppLanguage): String? = coreUiText[key]?.get(language.code)

/**
 * One shared on-device translator and persistent cache per language. Both interface copy and
 * question content use this path, so selecting a language applies to every screen in Manna.
 */
internal class TranslationRepository(context: Context) {
    private val preferences = context.getSharedPreferences("manna_translation_cache_v2", Context.MODE_PRIVATE)
    private val translators = mutableMapOf<String, Translator>()
    private val memory = mutableMapOf<String, String>()

    init {
        languages.drop(1).forEach { language ->
            require(TranslateLanguage.fromLanguageTag(language.code) != null) {
                "ML Kit does not support Manna language ${language.code}"
            }
        }
    }

    suspend fun translate(text: String, target: String): String {
        if (target == "en" || text.isBlank()) return text
        val digest = MessageDigest.getInstance("SHA-256").digest(text.toByteArray())
            .joinToString("") { "%02x".format(it) }
        val key = "${target}_$digest"
        memory[key]?.let { return it }
        preferences.getString(key, null)?.let { cached ->
            memory[key] = cached
            return cached
        }
        val translator = translatorFor(target)
        translator.downloadModelIfNeeded(DownloadConditions.Builder().build()).await()
        val translated = translator.translate(text).await()
        memory[key] = translated
        preferences.edit().putString(key, translated).apply()
        return translated
    }

    suspend fun translate(values: List<String>, target: String): List<String> =
        values.map { translate(it, target) }

    suspend fun downloadLanguage(target: String) {
        if (target == "en") return
        translatorFor(target).downloadModelIfNeeded(DownloadConditions.Builder().build()).await()
    }

    suspend fun isLanguageDownloaded(target: String): Boolean {
        if (target == "en") return true
        val model = TranslateRemoteModel.Builder(requireNotNull(TranslateLanguage.fromLanguageTag(target))).build()
        return RemoteModelManager.getInstance().isModelDownloaded(model).await()
    }

    private fun translatorFor(target: String): Translator {
        val targetLanguage = requireNotNull(TranslateLanguage.fromLanguageTag(target))
        return translators.getOrPut(target) {
            Translation.getClient(
                TranslatorOptions.Builder()
                    .setSourceLanguage(TranslateLanguage.ENGLISH)
                    .setTargetLanguage(targetLanguage)
                    .build()
            )
        }
    }

    fun close() {
        translators.values.forEach(Translator::close)
        translators.clear()
    }
}

@Composable
internal fun tr(english: String): String {
    val language = LocalAppLanguage.current
    val repository = LocalTranslationRepository.current
    var localized by remember(english, language.code) { mutableStateOf(if (language.code == "en") english else "") }
    LaunchedEffect(english, language.code) {
        localized = runCatching { repository.translate(english, language.code) }.getOrElse { english }
    }
    return localized
}

@Composable
internal fun LocalizedOrLoadingText(english: String): String {
    val value = tr(english)
    return if (value.isBlank()) "…" else value
}
