package com.oddcurrent.manna

import android.content.Context
import android.content.Intent
import android.content.ActivityNotFoundException
import android.content.ClipData
import android.content.ClipboardManager
import android.app.Activity
import android.media.AudioManager
import android.media.ToneGenerator
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.LocaleList
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONArray
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

private val Navy = Color(0xFF0F1223)
private val Gold = Color(0xFFD4A843)

private object DiagnosticRecorder {
    private data class Entry(val timestamp: Long, val event: String)
    private const val WINDOW_MILLIS = 20_000L
    private val entries = mutableListOf<Entry>()

    @Synchronized
    fun record(event: String) {
        val now = System.currentTimeMillis()
        entries += Entry(now, event.replace('\n', ' '))
        entries.removeAll { now - it.timestamp > WINDOW_MILLIS }
        if (entries.size > 200) entries.subList(0, entries.size - 200).clear()
    }

    @Synchronized
    fun reportBody(): String {
        val now = System.currentTimeMillis()
        entries.removeAll { now - it.timestamp > WINDOW_MILLIS }
        val formatter = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSZ", Locale.US)
        val events = if (entries.isEmpty()) {
            "No diagnostic events were recorded during the previous 20 seconds."
        } else {
            entries.joinToString("\n") { "${formatter.format(Date(it.timestamp))}  ${it.event}" }
        }
        return """
            Please describe the problem above this line:


            ---------------- Manna diagnostics ----------------
            App: Manna ${BuildConfig.VERSION_NAME} (build ${BuildConfig.VERSION_CODE})
            Platform: Android ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT})
            Device: ${Build.MANUFACTURER} ${Build.MODEL}
            Captured window: previous 20 seconds

            $events
            -----------------------------------------------------
            This report excludes question text, answer text, account data, and user-entered content.
        """.trimIndent()
    }
}

private fun openProblemReport(context: Context, clipboardLabel: String, noEmailMessage: String) {
    DiagnosticRecorder.record("support_email_opened")
    val subject = "Manna Problem Report"
    val body = DiagnosticRecorder.reportBody()
    val uri = Uri.parse("mailto:support@oddcurrent.com").buildUpon()
        .appendQueryParameter("subject", subject)
        .appendQueryParameter("body", body)
        .build()
    val intent = Intent(Intent.ACTION_SENDTO, uri).apply {
        putExtra(Intent.EXTRA_EMAIL, arrayOf("support@oddcurrent.com"))
        putExtra(Intent.EXTRA_SUBJECT, subject)
        putExtra(Intent.EXTRA_TEXT, body)
    }
    try {
        context.startActivity(intent)
    } catch (_: ActivityNotFoundException) {
        val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        clipboard.setPrimaryClip(ClipData.newPlainText(clipboardLabel, body))
        Toast.makeText(
            context,
            noEmailMessage,
            Toast.LENGTH_LONG
        ).show()
    }
}

data class Question(
    val id: String, val number: Int, val category: String, val difficulty: String, val question: String,
    val options: List<String>, val correct: String, val explanation: String, val ageGroup: String? = null,
    val pastorFormat: String? = null
) { val correctIndex: Int get() = options.indexOf(correct) }

internal enum class PastorQuestionFormat(val wireValue: String) {
    SCRIPTURE_MEMORY("scriptureMemory"),
    ORIGINAL_LANGUAGE("originalLanguage"),
    CHURCH_FATHER("churchFather"),
    INTERPRETATION("interpretation"),
    OTHER("other")
}

private val pastorBlockTemplates = listOf(
    listOf(PastorQuestionFormat.SCRIPTURE_MEMORY, PastorQuestionFormat.INTERPRETATION, PastorQuestionFormat.ORIGINAL_LANGUAGE, PastorQuestionFormat.INTERPRETATION, PastorQuestionFormat.OTHER),
    listOf(PastorQuestionFormat.SCRIPTURE_MEMORY, PastorQuestionFormat.INTERPRETATION, PastorQuestionFormat.ORIGINAL_LANGUAGE, PastorQuestionFormat.INTERPRETATION, PastorQuestionFormat.CHURCH_FATHER),
    listOf(PastorQuestionFormat.SCRIPTURE_MEMORY, PastorQuestionFormat.INTERPRETATION, PastorQuestionFormat.OTHER, PastorQuestionFormat.INTERPRETATION, PastorQuestionFormat.CHURCH_FATHER),
    listOf(PastorQuestionFormat.SCRIPTURE_MEMORY, PastorQuestionFormat.INTERPRETATION, PastorQuestionFormat.ORIGINAL_LANGUAGE, PastorQuestionFormat.INTERPRETATION, PastorQuestionFormat.OTHER)
)

internal fun Question.resolvedPastorFormat(): PastorQuestionFormat {
    PastorQuestionFormat.entries.firstOrNull { it.wireValue == pastorFormat }?.let { return it }
    val prompt = question.lowercase()
    return when {
        "church father" in prompt || "catena aurea" in prompt -> PastorQuestionFormat.CHURCH_FATHER
        "hebrew word" in prompt || "greek word" in prompt || "aramaic word" in prompt ||
            "strong's" in prompt || "strong’s" in prompt -> PastorQuestionFormat.ORIGINAL_LANGUAGE
        prompt.startsWith("complete") || "which passage" in prompt ||
            "which gospel verse" in prompt || "where is this verse" in prompt ||
            "where in the bible" in prompt || "cross-reference" in prompt -> PastorQuestionFormat.SCRIPTURE_MEMORY
        "what ot concept" in prompt || "what connects" in prompt ||
            "what type of connection" in prompt || "symbolize" in prompt ||
            "symbolise" in prompt || "interpretation" in prompt ||
            "significance" in prompt -> PastorQuestionFormat.INTERPRETATION
        else -> PastorQuestionFormat.OTHER
    }
}

internal fun balancedPastorQuestions(questions: List<Question>): List<Question> {
    if (questions.isEmpty()) return emptyList()
    val buckets = questions.shuffled().groupBy { it.resolvedPastorFormat() }
        .mapValues { (_, values) -> values.toMutableList() }.toMutableMap()
    val result = mutableListOf<Question>()
    var blockIndex = 0
    while (result.size < questions.size) {
        val block = mutableListOf<Question>()
        for (preferred in pastorBlockTemplates[blockIndex % pastorBlockTemplates.size]) {
            if (result.size + block.size >= questions.size) break
            val preferredBucket = buckets[preferred]
            val selected = if (!preferredBucket.isNullOrEmpty()) {
                preferredBucket.removeAt(preferredBucket.lastIndex)
            } else {
                val fallback = buckets.maxByOrNull { it.value.size }?.value
                if (fallback.isNullOrEmpty()) null else fallback.removeAt(fallback.lastIndex)
            }
            if (selected != null) block += selected
        }
        if (block.isEmpty()) break
        result += block.shuffled()
        blockIndex++
    }
    return result
}

internal data class ChildAgeGroupOption(
    val id: String,
    val label: String,
    val description: String,
    val answerChoices: Int,
    val questionCount: Int
)

internal val childAgeGroups = listOf(
    ChildAgeGroupOption("4-10", "4–10", "Familiar Bible stories", 3, 3_333),
    ChildAgeGroupOption("11-17", "11–17", "Bible stories, passages, and deeper knowledge", 4, 6_667)
)

class MainActivity : ComponentActivity() {
    private val partyLinkCode = mutableStateOf<String?>(null)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        partyLinkCode.value = intent?.data?.takeIf { it.scheme == "manna" && it.host == "party" }?.lastPathSegment
        setContent {
            MaterialTheme(colorScheme = darkColorScheme(primary = Gold, background = Navy, surface = Navy)) {
                Surface(
                    Modifier.fillMaxSize().windowInsetsPadding(WindowInsets.safeDrawing),
                    color = Navy
                ) { MannaApp(partyLinkCode.value) }
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        partyLinkCode.value = intent.data?.takeIf { it.scheme == "manna" && it.host == "party" }?.lastPathSegment
    }
}

private enum class Screen { HOME, SETUP, GAME, SETTINGS, LANGUAGES, RESULT, BONUS, PARTY }

private fun detectedDeviceLanguage(): AppLanguage {
    val preferred = LocaleList.getDefault()
    return detectedLanguageFromCodes(List(preferred.size()) { index -> preferred[index].language })
}

internal fun detectedLanguageFromCodes(preferredCodes: List<String>): AppLanguage {
    for (preferredCode in preferredCodes) {
        val code = preferredCode.lowercase()
        val normalized = when (code) {
            "nb", "nn" -> "no"
            else -> code
        }
        languages.firstOrNull { it.code == normalized }?.let { return it }
    }
    return languages.first()
}

@Composable
private fun MannaApp(partyLinkCode: String? = null) {
    val context = LocalContext.current
    val translationRepository = remember { TranslationRepository(context.applicationContext) }
    DisposableEffect(translationRepository) { onDispose(translationRepository::close) }
    var questions by remember { mutableStateOf<List<Question>>(emptyList()) }
    var loadError by remember { mutableStateOf<String?>(null) }
    var screen by remember { mutableStateOf(Screen.HOME) }
    var selectedCategory by remember { mutableStateOf("All Categories") }
    var selectedDifficulty by remember { mutableStateOf("Deacon") }
    var childrenMode by remember { mutableStateOf(false) }
    var selectedAgeGroup by remember { mutableStateOf("4-10") }
    var session by remember { mutableStateOf<List<Question>>(emptyList()) }
    var index by remember { mutableIntStateOf(0) }
    var correctCount by remember { mutableIntStateOf(0) }
    val preferences = remember { context.getSharedPreferences("manna_settings", Context.MODE_PRIVATE) }
    var language by remember {
        val stored = preferences.getString("language", null)
        mutableStateOf(languages.firstOrNull { it.code == stored } ?: detectedDeviceLanguage())
    }
    var languageSetupComplete by remember { mutableStateOf(preferences.getBoolean("language_setup_complete", false)) }
    var soundOn by remember { mutableStateOf(preferences.getBoolean("sound_effects", true)) }
    val monetization = remember {
        MonetizationManager(context as Activity, preferences) { installed ->
            questions = (questions + installed).distinctBy { it.id }
        }
    }
    var bonusQuestion by remember { mutableStateOf<Question?>(null) }
    var bonusOffered by remember { mutableStateOf(false) }

    fun eligibleQuestions(): List<Question> = questions.filter {
        if (childrenMode) it.ageGroup == selectedAgeGroup
        else it.ageGroup == null && it.difficulty == selectedDifficulty &&
            (selectedCategory == "All Categories" || it.category == selectedCategory)
    }

    fun nextStrictQuestion(excluding: Set<String> = emptySet()): Question? {
        val eligible = eligibleQuestions()
        if (eligible.isEmpty()) return null
        val seen = preferences.getStringSet("presented_question_ids", emptySet()).orEmpty().toMutableSet()
        var candidates = eligible.filter { it.id !in seen && it.id !in excluding }
        if (candidates.isEmpty() && eligible.all { it.id in seen }) {
            seen.removeAll(eligible.map { it.id }.toSet())
            candidates = eligible.filter { it.id !in excluding }
            if (candidates.isEmpty()) candidates = eligible
        }
        val balancedCandidates = if (selectedDifficulty == "Pastor" && !childrenMode) {
            val position = excluding.size
            val template = pastorBlockTemplates[(position / 5) % pastorBlockTemplates.size]
            val preferred = template[position % 5]
            candidates.filter { it.resolvedPastorFormat() == preferred }.ifEmpty { candidates }
        } else candidates
        val question = balancedCandidates.randomOrNull() ?: return null
        // Selection happens immediately before this question becomes the current screen.
        seen.add(question.id)
        preferences.edit().putStringSet("presented_question_ids", seen).apply()
        return question
    }

    LaunchedEffect(Unit) {
        DiagnosticRecorder.record("app_visible")
        runCatching { loadQuestions(context) }
            .onSuccess {
                questions = it
                DiagnosticRecorder.record("question_bank_loaded count=${it.size}")
            }
            .onFailure {
                loadError = it.message
                DiagnosticRecorder.record("question_bank_load_failed type=${it::class.java.simpleName}")
            }
    }
    LaunchedEffect(screen) {
        DiagnosticRecorder.record("screen=${screen.name.lowercase()}")
        if (screen == Screen.HOME) monetization.configureChildDirectedSession(false)
    }
    LaunchedEffect(partyLinkCode) { if (!partyLinkCode.isNullOrBlank()) screen = Screen.PARTY }

    CompositionLocalProvider(
        LocalAppLanguage provides language,
        LocalTranslationRepository provides translationRepository,
        LocalLayoutDirection provides if (language.code == "ar") LayoutDirection.Rtl else LayoutDirection.Ltr
    ) {
    if (!languageSetupComplete) {
        LanguageSetupScreen(
            selected = language,
            repository = translationRepository,
            onSelected = {
                language = it
                preferences.edit().putString("language", it.code).apply()
            },
            onComplete = {
                languageSetupComplete = true
                preferences.edit().putBoolean("language_setup_complete", true).apply()
            }
        )
    } else if (monetization.requiresInternetAccess) {
        InternetRequiredScreen()
    } else when (screen) {
        Screen.HOME -> HomeScreen(
            ready = questions.isNotEmpty(), error = loadError, language = language,
            questionCount = questions.size,
            onPlay = { screen = Screen.SETUP }, onParty = { screen = Screen.PARTY }, onSettings = { screen = Screen.SETTINGS }
        )
        Screen.SETUP -> SetupScreen(
            categories = listOf("All Categories") + questions.filter { it.ageGroup == null }.map { it.category }.distinct().sorted(),
            category = selectedCategory, difficulty = selectedDifficulty, language = language,
            childrenMode = childrenMode, ageGroup = selectedAgeGroup,
            onAudience = {
                childrenMode = it
                DiagnosticRecorder.record("setup_audience=${if (it) "children" else "adults"}")
            },
            onAgeGroup = {
                selectedAgeGroup = it
                DiagnosticRecorder.record("setup_children_age=$it")
            },
            onCategory = {
                selectedCategory = it
                DiagnosticRecorder.record("setup_category_changed")
            }, onDifficulty = {
                selectedDifficulty = it
                DiagnosticRecorder.record("setup_difficulty=$it")
            },
            onBack = { screen = Screen.HOME }, onStart = {
                monetization.configureChildDirectedSession(childrenMode)
                val first = nextStrictQuestion()
                session = first?.let(::listOf).orEmpty(); index = 0; correctCount = 0
                bonusOffered = false; bonusQuestion = null
                if (first != null) screen = Screen.GAME
            }
        )
        Screen.GAME -> if (session.isNotEmpty()) QuestionScreen(
            question = session[index], number = index + 1, total = 5, language = language, soundOn = soundOn,
            monetization = monetization, allowAnswerBanner = true,
            onQuit = { screen = Screen.HOME }, onNext = { correct ->
                val finalCorrect = correctCount + if (correct) 1 else 0
                correctCount = finalCorrect
                val sessionComplete = index == 4
                monetization.recordRegularAnswer(sessionComplete) {
                    if (sessionComplete) {
                        bonusOffered = finalCorrect >= 3
                        screen = Screen.RESULT
                    } else {
                        val next = nextStrictQuestion(session.map { it.id }.toSet())
                        if (next == null) screen = Screen.RESULT
                        else { session = session + next; index++ }
                    }
                }
            }
        )
        Screen.SETTINGS -> SettingsScreen(
            language = language, questionCount = questions.size, onBack = { screen = Screen.HOME },
            monetization = monetization,
            soundOn = soundOn,
            onManageLanguages = { screen = Screen.LANGUAGES },
            onSound = { soundOn = it; preferences.edit().putBoolean("sound_effects", it).apply() }
        )
        Screen.LANGUAGES -> LanguageManagerScreen(
            selected = language,
            repository = translationRepository,
            onSelected = {
                language = it
                preferences.edit().putString("language", it.code).apply()
            },
            onBack = { screen = Screen.SETTINGS }
        )
        Screen.RESULT -> ResultScreen(
            correct = correctCount, total = session.size, language = language,
            showBonusOffer = bonusOffered,
            adsRequiredForBonus = monetization.shouldShowAds,
            onDeclineBonus = { bonusOffered = false },
            onAcceptBonus = {
                monetization.showBonusAdIfNeeded { earned ->
                    if (earned) {
                        bonusOffered = false
                        bonusQuestion = nextStrictQuestion(session.map { it.id }.toSet())
                        if (bonusQuestion != null) screen = Screen.BONUS
                    }
                }
            },
            onHome = { screen = Screen.HOME }
        )
        Screen.BONUS -> bonusQuestion?.let { question ->
            QuestionScreen(
                question = question, number = 1, total = 1, language = language, soundOn = soundOn,
                monetization = monetization, allowAnswerBanner = false,
                onQuit = { screen = Screen.RESULT },
                onNext = { screen = Screen.RESULT }
            )
        } ?: run { screen = Screen.RESULT }
        Screen.PARTY -> PartyModeScreen(questions = questions, initialCode = partyLinkCode, onBack = { screen = Screen.HOME })
    }
    }
}

private enum class LanguageModelState { CHECKING, DOWNLOADABLE, DOWNLOADING, READY, FAILED }

@Composable
private fun LanguageSetupScreen(
    selected: AppLanguage,
    repository: TranslationRepository,
    onSelected: (AppLanguage) -> Unit,
    onComplete: () -> Unit
) {
    val scope = rememberCoroutineScope()
    var state by remember(selected.code) { mutableStateOf(LanguageModelState.CHECKING) }
    LaunchedEffect(selected.code) {
        state = runCatching {
            if (repository.isLanguageDownloaded(selected.code)) LanguageModelState.READY else LanguageModelState.DOWNLOADABLE
        }.getOrElse { LanguageModelState.FAILED }
    }

    Column(
        Modifier.fillMaxSize().background(Navy).padding(horizontal = 24.dp, vertical = 20.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(Modifier.height(18.dp))
        Text("🌐", fontSize = 52.sp)
        Text("MANNA", color = Gold, fontSize = 30.sp, fontWeight = FontWeight.Black, letterSpacing = 4.sp)
        Spacer(Modifier.height(16.dp))
        Column(
            Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            languages.forEach { language ->
                val active = language == selected
                OutlinedButton(
                    onClick = { onSelected(language) },
                    modifier = Modifier.fillMaxWidth().heightIn(min = 50.dp),
                    colors = ButtonDefaults.outlinedButtonColors(
                        containerColor = if (active) Gold else Color.Transparent,
                        contentColor = if (active) Color.Black else Color.White
                    ),
                    border = ButtonDefaults.outlinedButtonBorder(enabled = true).copy(
                        brush = androidx.compose.ui.graphics.SolidColor(if (active) Gold else Color.White.copy(alpha = .25f))
                    )
                ) {
                    Text(if (active) "✓  ${language.nativeName}" else language.nativeName, fontWeight = if (active) FontWeight.Bold else FontWeight.Medium)
                }
            }
        }
        Spacer(Modifier.height(14.dp))
        Button(
            onClick = {
                if (state == LanguageModelState.READY) onComplete()
                else scope.launch {
                    state = LanguageModelState.DOWNLOADING
                    state = runCatching {
                        repository.downloadLanguage(selected.code)
                        LanguageModelState.READY
                    }.getOrElse { LanguageModelState.FAILED }
                    if (state == LanguageModelState.READY) onComplete()
                }
            },
            enabled = state != LanguageModelState.CHECKING && state != LanguageModelState.DOWNLOADING,
            modifier = Modifier.fillMaxWidth().height(58.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Gold)
        ) {
            if (state == LanguageModelState.CHECKING || state == LanguageModelState.DOWNLOADING) {
                CircularProgressIndicator(modifier = Modifier.size(24.dp), color = Color.Black, strokeWidth = 3.dp)
            } else {
                val symbol = when (state) {
                    LanguageModelState.READY -> "✓"
                    LanguageModelState.FAILED -> "↻"
                    else -> "↓"
                }
                Text("$symbol  ${selected.nativeName}", color = Color.Black, fontSize = 18.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
private fun LanguageManagerScreen(
    selected: AppLanguage,
    repository: TranslationRepository,
    onSelected: (AppLanguage) -> Unit,
    onBack: () -> Unit
) {
    Column(Modifier.fillMaxSize().background(Navy)) {
        Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
            TextButton(onClick = onBack) { Text("‹", fontSize = 30.sp) }
            Spacer(Modifier.weight(1f))
            Text("🌐  ${LocalizedOrLoadingText("Languages")}", color = Color.White, fontSize = 21.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.weight(1f))
            Spacer(Modifier.width(46.dp))
        }
        Column(
            Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            languages.forEach { language ->
                LanguageDownloadRow(language, language == selected, repository, onSelected)
            }
            Spacer(Modifier.height(20.dp))
        }
    }
}

@Composable
private fun LanguageDownloadRow(
    language: AppLanguage,
    selected: Boolean,
    repository: TranslationRepository,
    onSelected: (AppLanguage) -> Unit
) {
    val scope = rememberCoroutineScope()
    var state by remember(language.code) { mutableStateOf(LanguageModelState.CHECKING) }
    LaunchedEffect(language.code) {
        state = runCatching {
            if (repository.isLanguageDownloaded(language.code)) LanguageModelState.READY else LanguageModelState.DOWNLOADABLE
        }.getOrElse { LanguageModelState.FAILED }
    }
    OutlinedButton(
        onClick = {
            if (state == LanguageModelState.READY) onSelected(language)
            else scope.launch {
                state = LanguageModelState.DOWNLOADING
                state = runCatching {
                    repository.downloadLanguage(language.code)
                    LanguageModelState.READY
                }.getOrElse { LanguageModelState.FAILED }
                if (state == LanguageModelState.READY) onSelected(language)
            }
        },
        enabled = state != LanguageModelState.CHECKING && state != LanguageModelState.DOWNLOADING,
        modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp)
    ) {
        Text(language.nativeName, modifier = Modifier.weight(1f), textAlign = TextAlign.Start, color = Color.White, fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium)
        when (state) {
            LanguageModelState.CHECKING, LanguageModelState.DOWNLOADING -> CircularProgressIndicator(modifier = Modifier.size(21.dp), color = Gold, strokeWidth = 2.dp)
            LanguageModelState.READY -> Text(if (selected) "✓" else "☁✓", color = if (selected) Gold else Color.Green, fontWeight = FontWeight.Bold)
            LanguageModelState.DOWNLOADABLE -> Text("↓", color = Gold, fontSize = 24.sp, fontWeight = FontWeight.Bold)
            LanguageModelState.FAILED -> Text("↻", color = Color(0xFFFFA000), fontSize = 22.sp, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
private fun InternetRequiredScreen() {
    Column(
        Modifier.fillMaxSize().padding(34.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("📶", fontSize = 52.sp)
        Spacer(Modifier.height(16.dp))
        Text(LocalizedOrLoadingText("Internet Required"), color = Color.White, fontSize = 28.sp, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(14.dp))
        Text(
            LocalizedOrLoadingText("The free version of Manna needs an active Wi-Fi or cellular internet connection so advertising can be delivered. Reconnect to continue, or purchase Remove Ads while online for permanent offline access."),
            color = Color.White.copy(alpha = .72f),
            fontSize = 16.sp,
            lineHeight = 23.sp,
            textAlign = TextAlign.Center
        )
    }
}

@Composable
private fun HomeScreen(ready: Boolean, error: String?, language: AppLanguage, questionCount: Int, onPlay: () -> Unit, onParty: () -> Unit, onSettings: () -> Unit) {
    Column(Modifier.fillMaxSize().padding(28.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Spacer(Modifier.weight(1f))
        Text("MANNA", color = Gold, fontSize = 52.sp, fontWeight = FontWeight.Black, fontFamily = FontFamily.Serif, letterSpacing = 6.sp)
        Text(LocalizedOrLoadingText("OVER 50,000 QUESTIONS"), color = Color.White, fontSize = 17.sp, fontWeight = FontWeight.Black, letterSpacing = 1.4.sp)
        Text(LocalizedOrLoadingText("BIBLE TRIVIA"), color = Color.White.copy(alpha = .55f), letterSpacing = 3.sp)
        Spacer(Modifier.height(28.dp))
        Text(LocalizedOrLoadingText("“All Scripture is given by inspiration of God and is profitable for doctrine, for reproof, for correction, for instruction in righteousness.”"),
            color = Color.White.copy(alpha = .65f), fontSize = 20.sp, fontFamily = FontFamily.Serif, fontStyle = FontStyle.Italic, textAlign = TextAlign.Center)
        Spacer(Modifier.weight(1f))
        if (error != null) Text(LocalizedOrLoadingText("Questions could not be loaded. Please restart Manna."), color = MaterialTheme.colorScheme.error)
        Button(onClick = onPlay, enabled = ready, modifier = Modifier.fillMaxWidth().height(58.dp), colors = ButtonDefaults.buttonColors(containerColor = Gold)) {
            Text(if (ready) ui("play", language) else LocalizedOrLoadingText("Loading questions…"), color = Color.Black, fontWeight = FontWeight.Bold, fontSize = 18.sp)
        }
        Spacer(Modifier.height(10.dp))
        OutlinedButton(onClick = onParty, enabled = ready, modifier = Modifier.fillMaxWidth().height(54.dp)) {
            Text("👥  ${coreUi("party_mode", language) ?: "Party Mode"}", color = Gold, fontWeight = FontWeight.Bold, fontSize = 17.sp)
        }
        TextButton(onClick = onSettings) { Text("⚙  ${ui("settings", language)}", color = Color.White.copy(alpha = .7f)) }
    }
}

@Composable
private fun SetupScreen(
    categories: List<String>,
    category: String,
    difficulty: String,
    language: AppLanguage,
    childrenMode: Boolean,
    ageGroup: String,
    onAudience: (Boolean) -> Unit,
    onAgeGroup: (String) -> Unit,
    onCategory: (String) -> Unit,
    onDifficulty: (String) -> Unit,
    onBack: () -> Unit,
    onStart: () -> Unit
) {
    val context = LocalContext.current
    val diagnosticsLabel = LocalizedOrLoadingText("Manna diagnostics")
    val noEmailMessage = LocalizedOrLoadingText("No email app is available. The report was copied; email it to support@oddcurrent.com.")
    var categoryMenu by remember { mutableStateOf(false) }
    Column(Modifier.fillMaxSize().padding(20.dp)) {
        Column(Modifier.weight(1f).verticalScroll(rememberScrollState())) {
            TextButton(onClick = onBack) { Text("‹ ${LocalizedOrLoadingText("Back")}") }
            Text(LocalizedOrLoadingText("Set Up Your Session"), color = Color.White, fontSize = 27.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(24.dp))
            Text(LocalizedOrLoadingText("Players"), color = Color.White.copy(alpha = .65f))
            SingleChoiceSegmentedButtonRow(Modifier.fillMaxWidth()) {
                listOf(false to "Adults", true to "Children").forEachIndexed { index, value ->
                    SegmentedButton(
                        selected = childrenMode == value.first,
                        onClick = { onAudience(value.first) },
                        shape = SegmentedButtonDefaults.itemShape(index, 2)
                    ) { Text(LocalizedOrLoadingText(value.second)) }
                }
            }
            Spacer(Modifier.height(24.dp))
            if (childrenMode) {
                Text(LocalizedOrLoadingText("Children's Age"), color = Color.White.copy(alpha = .65f))
                SingleChoiceSegmentedButtonRow(Modifier.fillMaxWidth()) {
                    childAgeGroups.forEachIndexed { index, group ->
                        SegmentedButton(
                            selected = ageGroup == group.id,
                            onClick = { onAgeGroup(group.id) },
                            shape = SegmentedButtonDefaults.itemShape(index, childAgeGroups.size)
                        ) { Text(group.label, fontSize = 12.sp) }
                    }
                }
                val selected = childAgeGroups.first { it.id == ageGroup }
                Spacer(Modifier.height(18.dp))
                Surface(color = Color.White.copy(alpha = .07f), shape = RoundedCornerShape(16.dp)) {
                    Column(Modifier.fillMaxWidth().padding(22.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(if (ageGroup == "4-10") "🌱" else "🧭", fontSize = 46.sp)
                        Text("${LocalizedOrLoadingText("Ages")} ${selected.label}", color = Color.White, fontSize = 24.sp, fontWeight = FontWeight.Black)
                        Text(LocalizedOrLoadingText(selected.description), color = Color.White.copy(alpha = .68f), textAlign = TextAlign.Center)
                        Spacer(Modifier.height(9.dp))
                        Text("${"%,d".format(selected.questionCount)} ${LocalizedOrLoadingText("questions")} · ${selected.answerChoices} ${LocalizedOrLoadingText("choices each")}", color = Gold, fontWeight = FontWeight.Bold)
                    }
                }
                if (ageGroup == "4-10") {
                    Spacer(Modifier.height(12.dp))
                    Text(LocalizedOrLoadingText("A grown-up can read the questions aloud while the child chooses an answer."), color = Color.White.copy(alpha = .55f), fontSize = 13.sp, textAlign = TextAlign.Center)
                }
            } else {
                Text(LocalizedOrLoadingText("Category"), color = Color.White.copy(alpha = .65f))
                Box {
                    OutlinedButton(onClick = { categoryMenu = true }, modifier = Modifier.fillMaxWidth()) {
                        Text(LocalizedOrLoadingText(category), textAlign = TextAlign.Center, maxLines = 2)
                    }
                    DropdownMenu(expanded = categoryMenu, onDismissRequest = { categoryMenu = false }, modifier = Modifier.heightIn(max = 420.dp)) {
                        categories.forEach { DropdownMenuItem(text = { Text(LocalizedOrLoadingText(it)) }, onClick = { onCategory(it); categoryMenu = false }) }
                    }
                }
                Spacer(Modifier.height(20.dp)); Text(LocalizedOrLoadingText("Difficulty"), color = Color.White.copy(alpha = .65f))
                listOf("Layperson", "Deacon", "Pastor").forEach { value ->
                    Row(Modifier.fillMaxWidth().clickable { onDifficulty(value) }.padding(vertical = 12.dp), verticalAlignment = Alignment.CenterVertically) {
                        RadioButton(selected = difficulty == value, onClick = { onDifficulty(value) }); Text(LocalizedOrLoadingText(value), color = Color.White)
                    }
                }
            }
            Spacer(Modifier.height(12.dp))
        }
        Spacer(Modifier.height(12.dp))
        OutlinedButton(
            onClick = { openProblemReport(context, diagnosticsLabel, noEmailMessage) },
            modifier = Modifier.fillMaxWidth().heightIn(min = 62.dp)
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text("✉  ${LocalizedOrLoadingText("Report a Problem")}", fontWeight = FontWeight.Bold)
                Text(
                    LocalizedOrLoadingText("Includes privacy-safe diagnostics from the last 20 seconds"),
                    fontSize = 10.sp,
                    color = Color.White.copy(alpha = .62f),
                    textAlign = TextAlign.Center
                )
            }
        }
        Spacer(Modifier.height(10.dp))
        Button(onClick = onStart, modifier = Modifier.fillMaxWidth().height(56.dp), colors = ButtonDefaults.buttonColors(containerColor = Gold)) {
            Text(LocalizedOrLoadingText("Start"), color = Color.Black, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
private fun QuestionScreen(question: Question, number: Int, total: Int, language: AppLanguage, soundOn: Boolean, monetization: MonetizationManager, allowAnswerBanner: Boolean, onQuit: () -> Unit, onNext: (Boolean) -> Unit) {
    val translationRepository = LocalTranslationRepository.current
    var selected by remember(question.id) { mutableStateOf<Int?>(null) }
    var reveal by remember(question.id) { mutableStateOf(false) }
    var graded by remember(question.id) { mutableStateOf(false) }
    var localized by remember(question.id, language.code) { mutableStateOf<List<String>?>(null) }
    var translationError by remember(question.id, language.code) { mutableStateOf<String?>(null) }
    val source = listOf(question.category, question.question) + question.options + question.explanation
    val tone = remember { ToneGenerator(AudioManager.STREAM_MUSIC, 80) }
    DisposableEffect(Unit) { onDispose { tone.release() } }

    LaunchedEffect(question.id) {
        DiagnosticRecorder.record("question_presented number=${question.number} difficulty=${question.difficulty}")
        monetization.recordQuestionPresented(question.id)
    }

    fun gradeOnce() {
        if (!graded) {
            if (soundOn) {
                tone.startTone(
                    if (selected == question.correctIndex) ToneGenerator.TONE_PROP_ACK else ToneGenerator.TONE_PROP_NACK,
                    180
                )
            }
            graded = true
        }
    }

    LaunchedEffect(question.id, language.code) {
        if (language.code == "en") localized = source
        else runCatching { translationRepository.translate(source, language.code) }.onSuccess { localized = it }.onFailure { translationError = it.localizedMessage }
    }
    val text = localized ?: source
    val optionOffset = 2
    Column(Modifier.fillMaxSize().padding(16.dp)) {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text("$number/$total  •  ${LocalizedOrLoadingText("Question")} #${question.number}", color = Color.White.copy(alpha = .7f), fontWeight = FontWeight.Bold)
            TextButton(onClick = onQuit) { Text("✕", color = Color.White.copy(alpha = .7f)) }
        }
        if (reveal && allowAnswerBanner && monetization.shouldShowAds) {
            MannaBannerAd(Modifier.fillMaxWidth().background(Color.Black.copy(alpha = .16f)))
        }
        Column(Modifier.weight(1f).verticalScroll(rememberScrollState()), horizontalAlignment = Alignment.CenterHorizontally) {
            Text("${text[0]}  •  ${question.ageGroup?.let { "${LocalizedOrLoadingText("Ages")} ${it.replace("-", "–")}" } ?: LocalizedOrLoadingText(question.difficulty)}", color = Gold, fontSize = 12.sp)
            Spacer(Modifier.height(18.dp)); Text(text[1], color = Color.White, fontSize = 21.sp, fontWeight = FontWeight.SemiBold, textAlign = TextAlign.Center)
            Spacer(Modifier.height(20.dp))
            question.options.indices.forEach { answerIndex ->
                val correct = answerIndex == question.correctIndex
                val chosen = selected == answerIndex
                val color = if (reveal && correct) Color(0xFF245B45) else if (reveal && chosen) Color(0xFF642F37) else Color.White.copy(alpha = if (chosen) .16f else .07f)
                Surface(
                    Modifier.fillMaxWidth().padding(vertical = 5.dp).selectable(
                        selected = chosen,
                        enabled = !reveal,
                        role = Role.RadioButton,
                        onClick = {
                            selected = answerIndex
                            DiagnosticRecorder.record("answer_selected question=${question.number} option=${answerIndex + 1}")
                        }
                    ),
                    color = color,
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text("${('A'.code + answerIndex).toChar()}.  ${text[optionOffset + answerIndex]}", color = Color.White, modifier = Modifier.padding(16.dp))
                }
            }
            if (reveal) {
                Spacer(Modifier.height(16.dp)); Text("${LocalizedOrLoadingText("Question")} #${question.number}", color = Color.White.copy(alpha = .55f), fontWeight = FontWeight.Bold)
                Text("✓ ${text[optionOffset + question.correctIndex]}", color = Color(0xFF68D391), fontWeight = FontWeight.Bold)
                if (question.explanation.isNotBlank()) Text(text.last(), color = Color.White.copy(alpha = .6f), modifier = Modifier.padding(top = 10.dp))
            } else if (selected != null) {
                Spacer(Modifier.height(14.dp))
                Text(
                    LocalizedOrLoadingText("Answer selected. You can change it until you reveal the answer or continue."),
                    color = Color.White.copy(alpha = .55f),
                    fontSize = 13.sp,
                    textAlign = TextAlign.Center
                )
            }
            if (localized == null && translationError == null) { Spacer(Modifier.height(16.dp)); CircularProgressIndicator(color = Gold) }
            translationError?.let { Text("${LocalizedOrLoadingText("Translation unavailable")}: $it", color = Color(0xFFFFB74D), fontSize = 12.sp) }
        }
        BoxWithConstraints(Modifier.fillMaxWidth()) {
            val compact = maxWidth < 420.dp
            val showAnswerButton: @Composable (Modifier) -> Unit = { modifier ->
                OutlinedButton(
                    onClick = {
                        DiagnosticRecorder.record("answer_revealed question=${question.number} banner_eligible=${allowAnswerBanner && monetization.shouldShowAds}")
                        gradeOnce()
                        reveal = true
                    },
                    enabled = !reveal,
                    modifier = modifier.heightIn(min = 54.dp)
                ) {
                    Text(ui("show_answer", language), textAlign = TextAlign.Center, maxLines = 2)
                }
            }
            val nextButton: @Composable (Modifier) -> Unit = { modifier ->
                Button(
                    onClick = {
                        DiagnosticRecorder.record("next_pressed question=${question.number} revealed=$reveal")
                        gradeOnce()
                        onNext(selected == question.correctIndex)
                    },
                    modifier = modifier.heightIn(min = 54.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Gold)
                ) {
                    Text(
                        if (number == total) ui("results", language) else ui("next", language),
                        color = Color.Black,
                        fontWeight = FontWeight.Bold,
                        textAlign = TextAlign.Center,
                        maxLines = 2
                    )
                }
            }
            if (compact) {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    showAnswerButton(Modifier.fillMaxWidth())
                    nextButton(Modifier.fillMaxWidth())
                }
            } else {
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    showAnswerButton(Modifier.weight(1f))
                    nextButton(Modifier.weight(1f))
                }
            }
        }
    }
}

@Composable
private fun SettingsScreen(language: AppLanguage, questionCount: Int, soundOn: Boolean, monetization: MonetizationManager, onBack: () -> Unit, onManageLanguages: () -> Unit, onSound: (Boolean) -> Unit) {
    val context = LocalContext.current
    var selectedTab by remember { mutableIntStateOf(0) }
    val tone = remember { ToneGenerator(AudioManager.STREAM_MUSIC, 80) }
    DisposableEffect(Unit) { onDispose { tone.release() } }
    Column(Modifier.fillMaxSize()) {
        Row(Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
            TextButton(onClick = onBack) { Text("‹ ${LocalizedOrLoadingText("Back")}") }
            Spacer(Modifier.weight(1f))
            Text(ui("settings", language), color = Color.White, fontSize = 22.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.weight(1f))
            Spacer(Modifier.width(64.dp))
        }
        TabRow(selectedTabIndex = selectedTab, containerColor = Navy, contentColor = Gold) {
            Tab(selected = selectedTab == 0, onClick = { selectedTab = 0 }, text = { Text(LocalizedOrLoadingText("Settings")) })
            Tab(selected = selectedTab == 1, onClick = { selectedTab = 1 }, text = { Text(LocalizedOrLoadingText("Info & How It Works"), textAlign = TextAlign.Center) })
        }
        if (selectedTab == 1) {
            InfoContent(questionCount, monetization)
            return@Column
        }
        Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp)) {
        Surface(color = Color.White.copy(alpha = .06f), shape = RoundedCornerShape(14.dp), modifier = Modifier.fillMaxWidth()) {
            Row(Modifier.padding(horizontal = 18.dp, vertical = 12.dp), verticalAlignment = Alignment.CenterVertically) {
                Text(if (soundOn) "🔊" else "🔇", fontSize = 20.sp)
                Spacer(Modifier.width(12.dp))
                Text(LocalizedOrLoadingText("Sound Effects"), color = Color.White, modifier = Modifier.weight(1f))
                Switch(checked = soundOn, onCheckedChange = {
                    onSound(it)
                    if (it) tone.startTone(ToneGenerator.TONE_PROP_ACK, 180)
                })
            }
        }
        Spacer(Modifier.height(14.dp))
        OutlinedButton(onClick = onManageLanguages, modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp)) {
            Text("🌐  ${language.displayName}  ›", textAlign = TextAlign.Center, maxLines = 2)
        }
        Spacer(Modifier.height(14.dp))
        OutlinedButton(onClick = { openStoreListing(context) }, modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp)) {
            Text("↻  ${ui("check_updates", language)}", textAlign = TextAlign.Center, maxLines = 2)
        }
        if (!monetization.hasPurchasedAdFree) {
            Spacer(Modifier.height(14.dp))
            Surface(color = Color.White.copy(alpha = .06f), shape = RoundedCornerShape(14.dp), modifier = Modifier.fillMaxWidth()) {
                Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(LocalizedOrLoadingText("Remove Advertising"), color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                    Text(LocalizedOrLoadingText("A single one-time purchase permanently removes every banner, bonus ad and scheduled full-screen ad, and enables offline play."), color = Color.White.copy(alpha = .65f), fontSize = 13.sp)
                    Button(
                        onClick = monetization::purchaseAdFree,
                        enabled = !monetization.isPurchasing,
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(containerColor = Gold)
                    ) {
                        Text(if (monetization.isPurchasing) LocalizedOrLoadingText("Please wait…") else "${LocalizedOrLoadingText("Remove Ads")} · ${if (monetization.removeAdsPrice == "one-time purchase") LocalizedOrLoadingText("one-time purchase") else monetization.removeAdsPrice}", color = Color.Black, fontWeight = FontWeight.Bold)
                    }
                    TextButton(onClick = monetization::restorePurchases, modifier = Modifier.fillMaxWidth()) { Text(LocalizedOrLoadingText("Restore Purchase")) }
                    monetization.purchaseMessage?.let { Text(LocalizedOrLoadingText(it), color = Color.White.copy(alpha = .6f), fontSize = 12.sp) }
                    if (monetization.privacyOptionsRequired) {
                        TextButton(onClick = monetization::showPrivacyOptions, modifier = Modifier.fillMaxWidth()) { Text(LocalizedOrLoadingText("Advertising Privacy Choices")) }
                    }
                }
            }
        }
        if (monetization.isQuestionPackOfferAvailable || monetization.hasPurchasedQuestionPack) {
            Spacer(Modifier.height(14.dp))
            Surface(color = Color.White.copy(alpha = .06f), shape = RoundedCornerShape(14.dp), modifier = Modifier.fillMaxWidth()) {
                Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(LocalizedOrLoadingText("10,000 Extra Questions"), color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                    Text(LocalizedOrLoadingText("A permanent expansion pack for every game mode. Download once and play offline. No subscription."), color = Color.White.copy(alpha = .65f), fontSize = 13.sp)
                    when {
                        monetization.isQuestionPackInstalled -> Text("✓  ${LocalizedOrLoadingText("Installed")}", color = Gold, fontWeight = FontWeight.SemiBold)
                        monetization.hasPurchasedQuestionPack -> Button(
                            onClick = monetization::retryQuestionPackDownload,
                            modifier = Modifier.fillMaxWidth(), colors = ButtonDefaults.buttonColors(containerColor = Gold)
                        ) { Text(LocalizedOrLoadingText("Download Question Pack"), color = Color.Black, fontWeight = FontWeight.Bold) }
                        else -> Button(
                            onClick = monetization::purchaseQuestionPack, enabled = !monetization.isPurchasing,
                            modifier = Modifier.fillMaxWidth(), colors = ButtonDefaults.buttonColors(containerColor = Gold)
                        ) { Text(if (monetization.isPurchasing) LocalizedOrLoadingText("Please wait…") else "${LocalizedOrLoadingText("Get 10,000 Questions")} · ${if (monetization.questionPackPrice == "one-time purchase") LocalizedOrLoadingText("one-time purchase") else monetization.questionPackPrice}", color = Color.Black, fontWeight = FontWeight.Bold) }
                    }
                    TextButton(onClick = monetization::restorePurchases, modifier = Modifier.fillMaxWidth()) { Text(LocalizedOrLoadingText("Restore Purchases")) }
                    monetization.purchaseMessage?.let { Text(LocalizedOrLoadingText(it), color = Color.White.copy(alpha = .6f), fontSize = 12.sp) }
                }
            }
        }
        Spacer(Modifier.height(18.dp))
        Surface(color = Color.White.copy(alpha = .06f), shape = RoundedCornerShape(14.dp), modifier = Modifier.fillMaxWidth()) {
            Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text(LocalizedOrLoadingText("About Manna"), color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                HorizontalDivider(color = Color.White.copy(alpha = .12f))
                AppInfoRow(LocalizedOrLoadingText("Publisher"), "Odd Current Software")
                AppInfoRow(LocalizedOrLoadingText("Questions"), "%,d".format(questionCount))
                AppInfoRow(LocalizedOrLoadingText("Categories"), "21")
                AppInfoRow(LocalizedOrLoadingText("Difficulty levels"), "3")
                Text("${LocalizedOrLoadingText("Layperson")} · ${LocalizedOrLoadingText("Deacon")} · ${LocalizedOrLoadingText("Pastor")}", color = Color.White.copy(alpha = .5f), fontSize = 12.sp)
                AppInfoRow(LocalizedOrLoadingText("Languages"), languages.size.toString())
                AppInfoRow(LocalizedOrLoadingText("Questions per session"), "5")
                if (!monetization.hasPurchasedAdFree) {
                    AppInfoRow(LocalizedOrLoadingText("Questions presented"), "%,d".format(monetization.freeQuestionsUsed))
                }
                AppInfoRow(LocalizedOrLoadingText("Version"), context.packageManager.getPackageInfo(context.packageName, 0).versionName ?: "1.0.1")
                HorizontalDivider(color = Color.White.copy(alpha = .12f))
                Text(
                    if (monetization.hasPurchasedAdFree) LocalizedOrLoadingText("All questions ad-free · No subscriptions")
                    else LocalizedOrLoadingText("Answer banners · One-time Remove Ads purchase · No subscriptions"),
                    color = Gold, fontSize = 12.sp, fontWeight = FontWeight.SemiBold
                )
            }
        }
        Spacer(Modifier.height(12.dp))
        Text(LocalizedOrLoadingText("Translations are downloaded on device when first needed."), color = Color.White.copy(alpha = .45f), fontSize = 12.sp)
        Spacer(Modifier.height(20.dp))
        }
    }
}

@Composable
private fun InfoContent(questionCount: Int, monetization: MonetizationManager) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp)) {
        Text(LocalizedOrLoadingText("About Manna"), color = Color.White, fontSize = 27.sp, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(18.dp))
        InfoSection(LocalizedOrLoadingText("How Manna works")) {
            Text(LocalizedOrLoadingText("Choose a category and difficulty. Each session has five questions. Select an answer and change it as often as needed before using Show Answer or Next Question to lock it in. There is no timer. Players who answer at least three of five correctly may accept one optional bonus challenge. Performance history records accuracy, difficulty and category results."), color = Color.White.copy(alpha = .76f))
            Text(LocalizedOrLoadingText("Manna shows every eligible question once before beginning a new cycle, and this history is saved between launches. Every record has a permanent Question # shared by Apple and Android; include it when contacting support about a disputed answer."), color = Color.White.copy(alpha = .76f))
        }
        InfoSection(LocalizedOrLoadingText("Difficulty levels")) {
            InfoItem(LocalizedOrLoadingText("Layperson"), LocalizedOrLoadingText("Foundation level emphasizing widely known stories, major people and events, familiar passages and direct identification. It requires the least background knowledge."))
            InfoItem(LocalizedOrLoadingText("Deacon"), LocalizedOrLoadingText("Intermediate level for regular Bible readers, covering context, relationships, chronology, less familiar events and cross-references. Distractors are closer to the answer."))
            InfoItem(LocalizedOrLoadingText("Pastor"), LocalizedOrLoadingText("Advanced material including minor prophets, genealogies, detailed chronology, Hebrew and Greek terms, Church Fathers and deeper textual connections."))
            Text(LocalizedOrLoadingText("Difficulty describes the knowledge and reasoning required—not a countdown. All three levels remain untimed."), color = Color.White.copy(alpha = .76f))
        }
        if (monetization.shouldExplainAdvertising) {
            InfoSection(LocalizedOrLoadingText("Advertising and the ad-free purchase")) {
                Text(LocalizedOrLoadingText("The first 50 questions are completely free of advertising. Beginning with question 51, the unpaid version shows a small banner in its own reserved area whenever a regular answer is revealed. It never covers the question, answer or controls and does not pause the game. Once advertising begins, the unpaid version requires an active Wi-Fi or cellular internet connection."), color = Color.White.copy(alpha = .76f))
                Text(LocalizedOrLoadingText("After the 50-question ad-free allowance, a full-screen ad appears after each additional 20 regular questions, only at the end of a five-question session. An optional bonus button clearly identifies the voluntary rewarded ad shown before that bonus. If an ad cannot load, Manna continues and never withholds an answer or promised bonus."), color = Color.White.copy(alpha = .76f))
                Text(LocalizedOrLoadingText("The one-time Remove Ads purchase permanently removes all banners, bonus advertisements and scheduled full-screen ads, and enables offline play. Manna has no advertising subscriptions."), color = Color.White.copy(alpha = .76f))
            }
        }
        InfoSection(LocalizedOrLoadingText("Where the questions come from")) {
            Text("${LocalizedOrLoadingText("Over 50,000 questions")} · ${"%,d".format(questionCount)} ${LocalizedOrLoadingText("permanently numbered question records: 40,020 adult questions in 21 categories, plus 3,333 questions for ages 4–10 and 6,667 for ages 11–17. Question numbers are identical on Apple and Android and are never reassigned to a different record. The bundled, offline bank is assembled from the King James Bible, the public-domain World English Bible for source-cited story questions and modern, age-screened children's excerpts, Treasury of Scripture Knowledge cross-references, Gospel-to-Old-Testament links, Strong’s Hebrew and Greek lexicons, Catena Aurea and other public-domain Bible-study data also used by Lumina. Release checks remove duplicate question text, reject invalid choices and enforce the difficulty and age-group rules.")}", color = Color.White.copy(alpha = .76f))
        }
        InfoSection(LocalizedOrLoadingText("Where the answers come from")) {
            Text(LocalizedOrLoadingText("Each correct answer is stored with its question. Source-backed audits recheck supported question patterns against the KJV, Strong’s/BDB/Thayer lexicons and Catena Aurea records; the remaining patterns require editorial review rather than being declared correct by a format check. Explanations include references or context when available. Users should consult Scripture and trusted study resources for disputed interpretations."), color = Color.White.copy(alpha = .76f))
        }
        InfoSection("Odd Current Software") {
            Text(
                if (monetization.hasPurchasedAdFree) LocalizedOrLoadingText("Odd Current Software creates focused, respectful apps for study and everyday life. This copy of Manna is permanently ad-free and has no subscriptions.")
                else LocalizedOrLoadingText("Odd Current Software creates focused, respectful apps for study and everyday life. Manna provides an optional one-time purchase that permanently removes advertising; it has no advertising subscriptions."),
                color = Color.White.copy(alpha = .76f)
            )
        }
        InfoSection(LocalizedOrLoadingText("More from Odd Current")) {
            InfoItem("Lumina Bible Study", LocalizedOrLoadingText("Places Scripture beside cross-references, Strong’s concordance material, commentaries, Church Fathers, Mishnah, Talmud, Septuagint resources, maps and notes."))
            InfoItem("Sabbath Watch", LocalizedOrLoadingText("Uses location-aware sunset calculations for weekly Sabbath countdowns, start/end times, reminders, saved cities, Apple Watch faces and a bedside clock."))
            InfoItem("Clean Table", LocalizedOrLoadingText("Checks foods, ingredient lists and packaged products against biblical food-law categories, with product lookup, ingredient analysis and UPC scanning."))
        }
        Spacer(Modifier.height(20.dp))
    }
}

@Composable
private fun InfoSection(title: String, content: @Composable ColumnScope.() -> Unit) {
    Surface(color = Color.White.copy(alpha = .06f), shape = RoundedCornerShape(14.dp), modifier = Modifier.fillMaxWidth().padding(bottom = 14.dp)) {
        Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text(title, color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.Bold)
            content()
        }
    }
}

@Composable
private fun InfoItem(name: String, detail: String) {
    Column(verticalArrangement = Arrangement.spacedBy(3.dp)) {
        Text(name, color = Gold, fontWeight = FontWeight.Bold)
        Text(detail, color = Color.White.copy(alpha = .72f))
    }
}

@Composable
private fun AppInfoRow(label: String, value: String) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(label, color = Color.White.copy(alpha = .62f), fontSize = 13.sp, modifier = Modifier.weight(1f))
        Text(value, color = Color.White, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, textAlign = TextAlign.End, modifier = Modifier.weight(1f), maxLines = 2)
    }
}

@Composable
private fun ResultScreen(correct: Int, total: Int, language: AppLanguage, showBonusOffer: Boolean, adsRequiredForBonus: Boolean, onDeclineBonus: () -> Unit, onAcceptBonus: () -> Unit, onHome: () -> Unit) {
    Column(Modifier.fillMaxSize().padding(28.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
        Text(ui("results", language), color = Color.White, fontSize = 28.sp, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(20.dp)); Text("$correct / $total", color = Gold, fontSize = 56.sp, fontWeight = FontWeight.Black)
        Spacer(Modifier.height(28.dp)); Button(onClick = onHome, colors = ButtonDefaults.buttonColors(containerColor = Gold)) { Text(LocalizedOrLoadingText("Home"), color = Color.Black) }
    }
    if (showBonusOffer) {
        AlertDialog(
            onDismissRequest = onDeclineBonus,
            title = { Text("⚡ ${LocalizedOrLoadingText("Bonus Challenge")}") },
            text = {
                Text(
                    if (adsRequiredForBonus) LocalizedOrLoadingText("You earned an optional extra question. A voluntary full-screen rewarded ad plays first.")
                    else LocalizedOrLoadingText("You earned an optional extra question.")
                )
            },
            dismissButton = { TextButton(onClick = onDeclineBonus) { Text(LocalizedOrLoadingText("I'm Good")) } },
            confirmButton = {
                Button(onClick = onAcceptBonus, colors = ButtonDefaults.buttonColors(containerColor = Gold)) {
                    Text(if (adsRequiredForBonus) LocalizedOrLoadingText("Watch Ad & Play") else LocalizedOrLoadingText("Bring It!"), color = Color.Black, fontWeight = FontWeight.Bold)
                }
            }
        )
    }
}

private suspend fun loadQuestions(context: Context): List<Question> = withContext(Dispatchers.IO) {
    val array = JSONArray(context.assets.open("manna_questions.json").bufferedReader().use { it.readText() })
    val bundled = List(array.length()) { i ->
        val item = array.getJSONObject(i); val options = item.getJSONArray("options")
        Question(item.getString("id"), item.getInt("number"), item.getString("category"), item.getString("difficulty"), item.getString("question"),
            List(options.length()) { options.getString(it) }, item.getString("correct"), item.optString("explanation"),
            item.optString("ageGroup").takeIf { it.isNotBlank() && it != "null" },
            item.optString("pastorFormat").takeIf { it.isNotBlank() && it != "null" })
    }
    (bundled + QuestionPackStore.loadInstalled(context)).distinctBy { it.id }
}

private fun openStoreListing(context: Context) {
    val packageName = context.packageName
    val market = Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=$packageName"))
    runCatching { context.startActivity(market) }.onFailure {
        context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://play.google.com/store/apps/details?id=$packageName")))
    }
}

@Composable
private fun ui(key: String, language: AppLanguage): String {
    coreUi(key, language)?.let { return it }
    val english = mapOf(
        "play" to "PLAY", "settings" to "Settings", "show_answer" to "Show Answer",
        "next" to "Next Question", "results" to "Results", "check_updates" to "Check for Updates"
    )
    return LocalizedOrLoadingText(english[key] ?: key)
}
