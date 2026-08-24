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
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.google.mlkit.common.model.DownloadConditions
import com.google.mlkit.nl.translate.Translation
import com.google.mlkit.nl.translate.TranslatorOptions
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.tasks.await
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

private fun openProblemReport(context: Context) {
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
        clipboard.setPrimaryClip(ClipData.newPlainText("Manna diagnostics", body))
        Toast.makeText(
            context,
            "No email app is available. The report was copied; email it to support@oddcurrent.com.",
            Toast.LENGTH_LONG
        ).show()
    }
}

data class Question(
    val id: String, val number: Int, val category: String, val difficulty: String, val question: String,
    val options: List<String>, val correct: String, val explanation: String
) { val correctIndex: Int get() = options.indexOf(correct) }

data class AppLanguage(val code: String, val nativeName: String, val englishName: String) {
    val displayName: String get() = if (code == "en") englishName else "$englishName · $nativeName"
}
private val languages = listOf(
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

private enum class Screen { HOME, SETUP, GAME, SETTINGS, RESULT, BONUS, PARTY }

@Composable
private fun MannaApp(partyLinkCode: String? = null) {
    val context = LocalContext.current
    var questions by remember { mutableStateOf<List<Question>>(emptyList()) }
    var loadError by remember { mutableStateOf<String?>(null) }
    var screen by remember { mutableStateOf(Screen.HOME) }
    var selectedCategory by remember { mutableStateOf("All Categories") }
    var selectedDifficulty by remember { mutableStateOf("Deacon") }
    var session by remember { mutableStateOf<List<Question>>(emptyList()) }
    var index by remember { mutableIntStateOf(0) }
    var correctCount by remember { mutableIntStateOf(0) }
    val preferences = remember { context.getSharedPreferences("manna_settings", Context.MODE_PRIVATE) }
    var language by remember { mutableStateOf(languages.firstOrNull { it.code == preferences.getString("language", "en") } ?: languages.first()) }
    var soundOn by remember { mutableStateOf(preferences.getBoolean("sound_effects", true)) }
    val monetization = remember { MonetizationManager(context as Activity, preferences) }
    var bonusQuestion by remember { mutableStateOf<Question?>(null) }
    var bonusOffered by remember { mutableStateOf(false) }

    fun eligibleQuestions(): List<Question> = questions.filter {
        it.difficulty == selectedDifficulty && (selectedCategory == "All Categories" || it.category == selectedCategory)
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
        val question = candidates.randomOrNull() ?: return null
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
    LaunchedEffect(screen) { DiagnosticRecorder.record("screen=${screen.name.lowercase()}") }
    LaunchedEffect(partyLinkCode) { if (!partyLinkCode.isNullOrBlank()) screen = Screen.PARTY }

    if (monetization.requiresInternetAccess) {
        InternetRequiredScreen()
    } else when (screen) {
        Screen.HOME -> HomeScreen(
            ready = questions.isNotEmpty(), error = loadError, language = language,
            questionCount = questions.size,
            onPlay = { screen = Screen.SETUP }, onParty = { screen = Screen.PARTY }, onSettings = { screen = Screen.SETTINGS }
        )
        Screen.SETUP -> SetupScreen(
            categories = listOf("All Categories") + questions.map { it.category }.distinct().sorted(),
            category = selectedCategory, difficulty = selectedDifficulty,
            onCategory = {
                selectedCategory = it
                DiagnosticRecorder.record("setup_category_changed")
            }, onDifficulty = {
                selectedDifficulty = it
                DiagnosticRecorder.record("setup_difficulty=$it")
            },
            onBack = { screen = Screen.HOME }, onStart = {
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
            onLanguage = { language = it; preferences.edit().putString("language", it.code).apply() },
            onSound = { soundOn = it; preferences.edit().putBoolean("sound_effects", it).apply() }
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

@Composable
private fun InternetRequiredScreen() {
    Column(
        Modifier.fillMaxSize().padding(34.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("📶", fontSize = 52.sp)
        Spacer(Modifier.height(16.dp))
        Text("Internet Required", color = Color.White, fontSize = 28.sp, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(14.dp))
        Text(
            "The free version of Manna needs an active Wi-Fi or cellular internet connection so advertising can be delivered. Reconnect to continue, or purchase Remove Ads while online for permanent offline access.",
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
        Text("${"%,d".format(questionCount)} QUESTIONS", color = Color.White, fontSize = 17.sp, fontWeight = FontWeight.Black, letterSpacing = 1.4.sp)
        Text("BIBLE TRIVIA", color = Color.White.copy(alpha = .55f), letterSpacing = 3.sp)
        Spacer(Modifier.height(28.dp))
        Text("“All Scripture is given by inspiration of God and is profitable for doctrine, for reproof, for correction, for instruction in righteousness.”",
            color = Color.White.copy(alpha = .65f), fontSize = 20.sp, fontFamily = FontFamily.Serif, fontStyle = FontStyle.Italic, textAlign = TextAlign.Center)
        Spacer(Modifier.weight(1f))
        if (error != null) Text(error, color = MaterialTheme.colorScheme.error)
        Button(onClick = onPlay, enabled = ready, modifier = Modifier.fillMaxWidth().height(58.dp), colors = ButtonDefaults.buttonColors(containerColor = Gold)) {
            Text(if (ready) ui("play", language) else "Loading questions…", color = Color.Black, fontWeight = FontWeight.Bold, fontSize = 18.sp)
        }
        Spacer(Modifier.height(10.dp))
        OutlinedButton(onClick = onParty, enabled = ready, modifier = Modifier.fillMaxWidth().height(54.dp)) {
            Text("👥  Party Mode", color = Gold, fontWeight = FontWeight.Bold, fontSize = 17.sp)
        }
        TextButton(onClick = onSettings) { Text("⚙  ${ui("settings", language)}", color = Color.White.copy(alpha = .7f)) }
    }
}

@Composable
private fun SetupScreen(categories: List<String>, category: String, difficulty: String, onCategory: (String) -> Unit, onDifficulty: (String) -> Unit, onBack: () -> Unit, onStart: () -> Unit) {
    val context = LocalContext.current
    var categoryMenu by remember { mutableStateOf(false) }
    Column(Modifier.fillMaxSize().padding(20.dp)) {
        Column(Modifier.weight(1f).verticalScroll(rememberScrollState())) {
            TextButton(onClick = onBack) { Text("‹ Back") }
            Text("Set Up Your Session", color = Color.White, fontSize = 27.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(24.dp))
            Text("Category", color = Color.White.copy(alpha = .65f))
            Box {
                OutlinedButton(onClick = { categoryMenu = true }, modifier = Modifier.fillMaxWidth()) {
                    Text(category, textAlign = TextAlign.Center, maxLines = 2)
                }
                DropdownMenu(expanded = categoryMenu, onDismissRequest = { categoryMenu = false }, modifier = Modifier.heightIn(max = 420.dp)) {
                    categories.forEach { DropdownMenuItem(text = { Text(it) }, onClick = { onCategory(it); categoryMenu = false }) }
                }
            }
            Spacer(Modifier.height(20.dp)); Text("Difficulty", color = Color.White.copy(alpha = .65f))
            listOf("Layperson", "Deacon", "Pastor").forEach { value ->
                Row(Modifier.fillMaxWidth().clickable { onDifficulty(value) }.padding(vertical = 12.dp), verticalAlignment = Alignment.CenterVertically) {
                    RadioButton(selected = difficulty == value, onClick = { onDifficulty(value) }); Text(value, color = Color.White)
                }
            }
            Spacer(Modifier.height(12.dp))
        }
        Spacer(Modifier.height(12.dp))
        OutlinedButton(
            onClick = { openProblemReport(context) },
            modifier = Modifier.fillMaxWidth().heightIn(min = 62.dp)
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text("✉  Report a Problem", fontWeight = FontWeight.Bold)
                Text(
                    "Includes privacy-safe diagnostics from the last 20 seconds",
                    fontSize = 10.sp,
                    color = Color.White.copy(alpha = .62f),
                    textAlign = TextAlign.Center
                )
            }
        }
        Spacer(Modifier.height(10.dp))
        Button(onClick = onStart, modifier = Modifier.fillMaxWidth().height(56.dp), colors = ButtonDefaults.buttonColors(containerColor = Gold)) {
            Text("Start", color = Color.Black, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
private fun QuestionScreen(question: Question, number: Int, total: Int, language: AppLanguage, soundOn: Boolean, monetization: MonetizationManager, allowAnswerBanner: Boolean, onQuit: () -> Unit, onNext: (Boolean) -> Unit) {
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
        else runCatching { translate(source, language.code) }.onSuccess { localized = it }.onFailure { translationError = it.localizedMessage }
    }
    val text = localized ?: source
    val optionOffset = 2
    Column(Modifier.fillMaxSize().padding(16.dp)) {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text("$number/$total  •  Question #${question.number}", color = Color.White.copy(alpha = .7f), fontWeight = FontWeight.Bold)
            TextButton(onClick = onQuit) { Text("✕", color = Color.White.copy(alpha = .7f)) }
        }
        if (reveal && allowAnswerBanner && monetization.shouldShowAds) {
            MannaBannerAd(Modifier.fillMaxWidth().background(Color.Black.copy(alpha = .16f)))
        }
        Column(Modifier.weight(1f).verticalScroll(rememberScrollState()), horizontalAlignment = Alignment.CenterHorizontally) {
            Text("${text[0]}  •  ${question.difficulty}", color = Gold, fontSize = 12.sp)
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
                Spacer(Modifier.height(16.dp)); Text("Question #${question.number}", color = Color.White.copy(alpha = .55f), fontWeight = FontWeight.Bold)
                Text("✓ ${text[optionOffset + question.correctIndex]}", color = Color(0xFF68D391), fontWeight = FontWeight.Bold)
                if (question.explanation.isNotBlank()) Text(text.last(), color = Color.White.copy(alpha = .6f), modifier = Modifier.padding(top = 10.dp))
            } else if (selected != null) {
                Spacer(Modifier.height(14.dp))
                Text(
                    "Answer selected. You can change it until you reveal the answer or continue.",
                    color = Color.White.copy(alpha = .55f),
                    fontSize = 13.sp,
                    textAlign = TextAlign.Center
                )
            }
            if (localized == null && translationError == null) { Spacer(Modifier.height(16.dp)); CircularProgressIndicator(color = Gold) }
            translationError?.let { Text("Translation unavailable: $it", color = Color(0xFFFFB74D), fontSize = 12.sp) }
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
private fun SettingsScreen(language: AppLanguage, questionCount: Int, soundOn: Boolean, monetization: MonetizationManager, onBack: () -> Unit, onLanguage: (AppLanguage) -> Unit, onSound: (Boolean) -> Unit) {
    val context = LocalContext.current
    var menu by remember { mutableStateOf(false) }
    var selectedTab by remember { mutableIntStateOf(0) }
    val tone = remember { ToneGenerator(AudioManager.STREAM_MUSIC, 80) }
    DisposableEffect(Unit) { onDispose { tone.release() } }
    Column(Modifier.fillMaxSize()) {
        Row(Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
            TextButton(onClick = onBack) { Text("‹ Back") }
            Spacer(Modifier.weight(1f))
            Text(ui("settings", language), color = Color.White, fontSize = 22.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.weight(1f))
            Spacer(Modifier.width(64.dp))
        }
        TabRow(selectedTabIndex = selectedTab, containerColor = Navy, contentColor = Gold) {
            Tab(selected = selectedTab == 0, onClick = { selectedTab = 0 }, text = { Text("Settings") })
            Tab(selected = selectedTab == 1, onClick = { selectedTab = 1 }, text = { Text("Info & How It Works", textAlign = TextAlign.Center) })
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
                Text("Sound Effects", color = Color.White, modifier = Modifier.weight(1f))
                Switch(checked = soundOn, onCheckedChange = {
                    onSound(it)
                    if (it) tone.startTone(ToneGenerator.TONE_PROP_ACK, 180)
                })
            }
        }
        Spacer(Modifier.height(14.dp))
        Box {
            OutlinedButton(onClick = { menu = true }, modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp)) {
                Text("🌐  ${language.displayName}", textAlign = TextAlign.Center, maxLines = 2)
            }
            DropdownMenu(expanded = menu, onDismissRequest = { menu = false }) {
                languages.forEach { item -> DropdownMenuItem(text = { Text(item.displayName) }, onClick = { onLanguage(item); menu = false }) }
            }
        }
        Spacer(Modifier.height(14.dp))
        OutlinedButton(onClick = { openStoreListing(context) }, modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp)) {
            Text("↻  ${ui("check_updates", language)}", textAlign = TextAlign.Center, maxLines = 2)
        }
        if (!monetization.hasPurchasedAdFree) {
            Spacer(Modifier.height(14.dp))
            Surface(color = Color.White.copy(alpha = .06f), shape = RoundedCornerShape(14.dp), modifier = Modifier.fillMaxWidth()) {
                Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("Remove Advertising", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                    Text("A single one-time purchase permanently removes every banner, bonus ad and scheduled full-screen ad, and enables offline play.", color = Color.White.copy(alpha = .65f), fontSize = 13.sp)
                    Button(
                        onClick = monetization::purchaseAdFree,
                        enabled = !monetization.isPurchasing,
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(containerColor = Gold)
                    ) {
                        Text(if (monetization.isPurchasing) "Please wait…" else "Remove Ads · ${monetization.removeAdsPrice}", color = Color.Black, fontWeight = FontWeight.Bold)
                    }
                    TextButton(onClick = monetization::restorePurchases, modifier = Modifier.fillMaxWidth()) { Text("Restore Purchase") }
                    monetization.purchaseMessage?.let { Text(it, color = Color.White.copy(alpha = .6f), fontSize = 12.sp) }
                    if (monetization.privacyOptionsRequired) {
                        TextButton(onClick = monetization::showPrivacyOptions, modifier = Modifier.fillMaxWidth()) { Text("Advertising Privacy Choices") }
                    }
                }
            }
        }
        Spacer(Modifier.height(18.dp))
        Surface(color = Color.White.copy(alpha = .06f), shape = RoundedCornerShape(14.dp), modifier = Modifier.fillMaxWidth()) {
            Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text("About Manna", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                HorizontalDivider(color = Color.White.copy(alpha = .12f))
                AppInfoRow("Publisher", "Odd Current Software")
                AppInfoRow("Questions", "%,d".format(questionCount))
                AppInfoRow("Categories", "21")
                AppInfoRow("Difficulty levels", "3")
                Text("Layperson · Deacon · Pastor", color = Color.White.copy(alpha = .5f), fontSize = 12.sp)
                AppInfoRow("Languages", languages.size.toString())
                AppInfoRow("Questions per session", "5")
                if (!monetization.hasPurchasedAdFree) {
                    AppInfoRow("Questions presented", "%,d".format(monetization.freeQuestionsUsed))
                }
                AppInfoRow("Version", context.packageManager.getPackageInfo(context.packageName, 0).versionName ?: "1.0.1")
                HorizontalDivider(color = Color.White.copy(alpha = .12f))
                Text(
                    if (monetization.hasPurchasedAdFree) "All questions ad-free · No subscriptions"
                    else "Answer banners · One-time Remove Ads purchase · No subscriptions",
                    color = Gold, fontSize = 12.sp, fontWeight = FontWeight.SemiBold
                )
            }
        }
        Spacer(Modifier.height(12.dp))
        Text("Translations are downloaded on device when first needed.", color = Color.White.copy(alpha = .45f), fontSize = 12.sp)
        Spacer(Modifier.height(20.dp))
        }
    }
}

@Composable
private fun InfoContent(questionCount: Int, monetization: MonetizationManager) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp)) {
        Text("About Manna", color = Color.White, fontSize = 27.sp, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(18.dp))
        InfoSection("How Manna works") {
            Text("Choose a category and difficulty. Each session has five questions. Select an answer and change it as often as needed before using Show Answer or Next Question to lock it in. There is no timer. Players who answer at least three of five correctly may accept one optional bonus challenge. Performance history records accuracy, difficulty and category results.", color = Color.White.copy(alpha = .76f))
            Text("Manna shows every eligible question once before beginning a new cycle, and this history is saved between launches. Every record has a permanent Question # shared by Apple and Android; include it when contacting support about a disputed answer.", color = Color.White.copy(alpha = .76f))
        }
        InfoSection("Difficulty levels") {
            InfoItem("Layperson", "Foundation level emphasizing widely known stories, major people and events, familiar passages and direct identification. It requires the least background knowledge.")
            InfoItem("Deacon", "Intermediate level for regular Bible readers, covering context, relationships, chronology, less familiar events and cross-references. Distractors are closer to the answer.")
            InfoItem("Pastor", "Advanced material including minor prophets, genealogies, detailed chronology, Hebrew and Greek terms, Church Fathers and deeper textual connections.")
            Text("Difficulty describes the knowledge and reasoning required—not a countdown. All three levels remain untimed.", color = Color.White.copy(alpha = .76f))
        }
        if (monetization.shouldExplainAdvertising) {
            InfoSection("Advertising and the ad-free purchase") {
                Text("The first 50 questions are completely free of advertising. Beginning with question 51, the unpaid version shows a small banner in its own reserved area whenever a regular answer is revealed. It never covers the question, answer or controls and does not pause the game. Once advertising begins, the unpaid version requires an active Wi-Fi or cellular internet connection.", color = Color.White.copy(alpha = .76f))
                Text("After the 50-question ad-free allowance, a full-screen ad appears after each additional 20 regular questions, only at the end of a five-question session. An optional bonus button clearly identifies the voluntary rewarded ad shown before that bonus. If an ad cannot load, Manna continues and never withholds an answer or promised bonus.", color = Color.White.copy(alpha = .76f))
                Text("The one-time Remove Ads purchase permanently removes all banners, bonus advertisements and scheduled full-screen ads, and enables offline play. Manna has no advertising subscriptions.", color = Color.White.copy(alpha = .76f))
            }
        }
        InfoSection("Where the questions come from") {
            Text("Manna contains ${"%,d".format(questionCount)} permanently numbered question records in 21 categories. Question numbers are identical on Apple and Android and are never reassigned to a different record. The bundled, offline bank is assembled from the King James Bible, Treasury of Scripture Knowledge cross-references, Gospel-to-Old-Testament links, Strong’s Hebrew and Greek lexicons, Catena Aurea and other public-domain Bible-study data also used by Lumina. Release checks remove duplicate question text, reject invalid choices and enforce the difficulty rules.", color = Color.White.copy(alpha = .76f))
        }
        InfoSection("Where the answers come from") {
            Text("Each correct answer is stored with its question. Source-backed audits recheck supported question patterns against the KJV, Strong’s/BDB/Thayer lexicons and Catena Aurea records; the remaining patterns require editorial review rather than being declared correct by a format check. Explanations include references or context when available. Users should consult Scripture and trusted study resources for disputed interpretations.", color = Color.White.copy(alpha = .76f))
        }
        InfoSection("Odd Current Software") {
            Text(
                if (monetization.hasPurchasedAdFree) "Odd Current Software creates focused, respectful apps for study and everyday life. This copy of Manna is permanently ad-free and has no subscriptions."
                else "Odd Current Software creates focused, respectful apps for study and everyday life. Manna provides an optional one-time purchase that permanently removes advertising; it has no advertising subscriptions.",
                color = Color.White.copy(alpha = .76f)
            )
        }
        InfoSection("More from Odd Current") {
            InfoItem("Lumina Bible Study", "Places Scripture beside cross-references, Strong’s concordance material, commentaries, Church Fathers, Mishnah, Talmud, Septuagint resources, maps and notes.")
            InfoItem("Sabbath Watch", "Uses location-aware sunset calculations for weekly Sabbath countdowns, start/end times, reminders, saved cities, Apple Watch faces and a bedside clock.")
            InfoItem("Clean Table", "Checks foods, ingredient lists and packaged products against biblical food-law categories, with product lookup, ingredient analysis and UPC scanning.")
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
        Spacer(Modifier.height(28.dp)); Button(onClick = onHome, colors = ButtonDefaults.buttonColors(containerColor = Gold)) { Text("Home", color = Color.Black) }
    }
    if (showBonusOffer) {
        AlertDialog(
            onDismissRequest = onDeclineBonus,
            title = { Text("⚡ Bonus Challenge") },
            text = {
                Text(
                    if (adsRequiredForBonus) "You earned an optional extra question. A voluntary full-screen rewarded ad plays first."
                    else "You earned an optional extra question."
                )
            },
            dismissButton = { TextButton(onClick = onDeclineBonus) { Text("I'm Good") } },
            confirmButton = {
                Button(onClick = onAcceptBonus, colors = ButtonDefaults.buttonColors(containerColor = Gold)) {
                    Text(if (adsRequiredForBonus) "Watch Ad & Play" else "Bring It!", color = Color.Black, fontWeight = FontWeight.Bold)
                }
            }
        )
    }
}

private suspend fun loadQuestions(context: Context): List<Question> = withContext(Dispatchers.IO) {
    val array = JSONArray(context.assets.open("manna_questions.json").bufferedReader().use { it.readText() })
    List(array.length()) { i ->
        val item = array.getJSONObject(i); val options = item.getJSONArray("options")
        Question(item.getString("id"), item.getInt("number"), item.getString("category"), item.getString("difficulty"), item.getString("question"),
            List(options.length()) { options.getString(it) }, item.getString("correct"), item.optString("explanation"))
    }
}

private suspend fun translate(values: List<String>, target: String): List<String> {
    val translator = Translation.getClient(TranslatorOptions.Builder().setSourceLanguage("en").setTargetLanguage(target).build())
    return try {
        translator.downloadModelIfNeeded(DownloadConditions.Builder().requireWifi().build()).await()
        values.map { if (it.isBlank()) it else translator.translate(it).await() }
    } finally { translator.close() }
}

private fun openStoreListing(context: Context) {
    val packageName = context.packageName
    val market = Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=$packageName"))
    runCatching { context.startActivity(market) }.onFailure {
        context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://play.google.com/store/apps/details?id=$packageName")))
    }
}

private fun ui(key: String, language: AppLanguage): String {
    val values = mapOf(
        "play" to mapOf("ar" to "العب", "zh" to "开始", "da" to "SPIL", "nl" to "SPELEN", "fr" to "JOUER", "de" to "SPIELEN", "hi" to "खेलें", "id" to "MAIN", "it" to "GIOCA", "ja" to "プレイ", "ko" to "플레이", "no" to "SPILL", "pl" to "GRAJ", "pt" to "JOGAR", "ru" to "ИГРАТЬ", "es" to "JUGAR", "sv" to "SPELA", "th" to "เล่น", "tr" to "OYNA", "uk" to "ГРАТИ", "vi" to "CHƠI"),
        "settings" to mapOf("ar" to "الإعدادات", "zh" to "设置", "da" to "Indstillinger", "nl" to "Instellingen", "fr" to "Réglages", "de" to "Einstellungen", "hi" to "सेटिंग्स", "id" to "Pengaturan", "it" to "Impostazioni", "ja" to "設定", "ko" to "설정", "no" to "Innstillinger", "pl" to "Ustawienia", "pt" to "Definições", "ru" to "Настройки", "es" to "Ajustes", "sv" to "Inställningar", "th" to "การตั้งค่า", "tr" to "Ayarlar", "uk" to "Налаштування", "vi" to "Cài đặt"),
        "show_answer" to mapOf("ar" to "أظهر الإجابة", "zh" to "显示答案", "da" to "Vis svar", "nl" to "Toon antwoord", "fr" to "Afficher la réponse", "de" to "Antwort anzeigen", "hi" to "उत्तर दिखाएँ", "id" to "Tampilkan jawaban", "it" to "Mostra risposta", "ja" to "答えを見る", "ko" to "정답 보기", "no" to "Vis svar", "pl" to "Pokaż odpowiedź", "pt" to "Mostrar resposta", "ru" to "Показать ответ", "es" to "Mostrar respuesta", "sv" to "Visa svar", "th" to "แสดงคำตอบ", "tr" to "Cevabı göster", "uk" to "Показати відповідь", "vi" to "Hiển thị đáp án"),
        "next" to mapOf("ar" to "التالي", "zh" to "下一题", "da" to "Næste spørgsmål", "nl" to "Volgende vraag", "fr" to "Suivante", "de" to "Weiter", "hi" to "अगला", "id" to "Pertanyaan berikutnya", "it" to "Avanti", "ja" to "次へ", "ko" to "다음", "no" to "Neste spørsmål", "pl" to "Dalej", "pt" to "Seguinte", "ru" to "Следующий вопрос", "es" to "Siguiente", "sv" to "Nästa fråga", "th" to "คำถามถัดไป", "tr" to "Sonraki", "uk" to "Наступне запитання", "vi" to "Câu hỏi tiếp theo"),
        "results" to mapOf("ar" to "النتائج", "zh" to "结果", "da" to "Resultater", "nl" to "Resultaten", "fr" to "Résultats", "de" to "Ergebnisse", "hi" to "परिणाम", "id" to "Hasil", "it" to "Risultati", "ja" to "結果", "ko" to "결과", "no" to "Resultater", "pl" to "Wyniki", "pt" to "Resultados", "ru" to "Результаты", "es" to "Resultados", "sv" to "Resultat", "th" to "ผลลัพธ์", "tr" to "Sonuçlar", "uk" to "Результати", "vi" to "Kết quả"),
        "check_updates" to mapOf("ar" to "التحقق من التحديثات", "zh" to "检查更新", "da" to "Søg efter opdateringer", "nl" to "Controleren op updates", "fr" to "Rechercher des mises à jour", "de" to "Nach Updates suchen", "hi" to "अपडेट जाँचें", "id" to "Periksa pembaruan", "it" to "Controlla aggiornamenti", "ja" to "アップデートを確認", "ko" to "업데이트 확인", "no" to "Se etter oppdateringer", "pl" to "Sprawdź aktualizacje", "pt" to "Procurar atualizações", "ru" to "Проверить обновления", "es" to "Buscar actualizaciones", "sv" to "Sök efter uppdateringar", "th" to "ตรวจสอบการอัปเดต", "tr" to "Güncellemeleri denetle", "uk" to "Перевірити оновлення", "vi" to "Kiểm tra cập nhật")
    )
    val english = mapOf("play" to "PLAY", "settings" to "Settings", "show_answer" to "Show Answer", "next" to "Next Question", "results" to "Results", "check_updates" to "Check for Updates")
    return values[key]?.get(language.code) ?: english[key] ?: key
}
