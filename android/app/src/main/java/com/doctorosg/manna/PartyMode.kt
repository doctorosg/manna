package com.oddcurrent.manna

import android.content.Context
import android.graphics.Bitmap
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardCapitalization
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.google.zxing.BarcodeFormat
import com.google.zxing.qrcode.QRCodeWriter

private val PartyNavy = Color(0xFF0F1223)
private val PartyGold = Color(0xFFD4A843)

private enum class PartyPage { MENU, SETUP, JOIN }

internal data class PartySettings(
    val category: String,
    val difficulty: String,
    val questionCount: Int,
    val ageGroup: String? = null
)

@Composable
private fun PartySettings.selectionSummary(): String = if (ageGroup != null) {
    "${LocalizedOrLoadingText("Children")} · ${LocalizedOrLoadingText("Ages")} ${ageGroup.replace("-", "–")} · $questionCount ${LocalizedOrLoadingText("questions")}"
} else {
    "${LocalizedOrLoadingText(category)} · ${LocalizedOrLoadingText(difficulty)} · $questionCount ${LocalizedOrLoadingText("questions")}"
}
internal data class PartyPlayer(val id: String, val name: String, val score: Int, val hasAnswered: Boolean, val isHost: Boolean, val wasCorrect: Boolean?)
internal data class PartyRoom(
    val code: String,
    val phase: String,
    val settings: PartySettings,
    val currentIndex: Int,
    val questionId: String?,
    val questionNumber: Int,
    val players: List<PartyPlayer>,
    val answeredCount: Int,
    val myPlayerId: String,
    val myAnswer: Int?,
    val isHost: Boolean,
    val version: Int
)
internal data class PartySession(val token: String, val room: PartyRoom)
internal data class NearbyParty(val code: String, val hostName: String)

@Composable
fun PartyModeScreen(questions: List<Question>, initialCode: String? = null, onBack: () -> Unit) {
    val context = LocalContext.current
    val language = LocalAppLanguage.current
    val preferences = remember { context.getSharedPreferences("manna_party", Context.MODE_PRIVATE) }
    var page by remember(initialCode) { mutableStateOf(if (initialCode.isNullOrBlank()) PartyPage.MENU else PartyPage.JOIN) }
    var session by remember { mutableStateOf<PartySession?>(null) }
    var working by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    var showTVGuide by remember { mutableStateOf(false) }
    var tvMode by remember { mutableStateOf(false) }
    val nearbyParties = remember { mutableStateListOf<NearbyParty>() }
    val coordinator = remember(context, questions) {
        LocalPartyCoordinator(
            context = context,
            questions = questions,
            onSession = { session = it },
            onNearby = { parties -> nearbyParties.clear(); nearbyParties.addAll(parties) },
            onWorking = { working = it },
            onError = { error = it }
        )
    }

    DisposableEffect(coordinator) {
        coordinator.startDiscovery()
        onDispose { coordinator.shutdown() }
    }

    val hostView = LocalView.current
    DisposableEffect(tvMode) {
        val previous = hostView.keepScreenOn
        hostView.keepScreenOn = tvMode
        onDispose { hostView.keepScreenOn = previous }
    }

    fun leave() {
        coordinator.leave()
        session = null
        page = PartyPage.MENU
    }

    if (error != null) {
        AlertDialog(onDismissRequest = { error = null }, confirmButton = { TextButton(onClick = { error = null }) { Text(LocalizedOrLoadingText("OK")) } }, title = { Text(coreUi("party_mode", language) ?: "Party Mode") }, text = { Text(LocalizedOrLoadingText(error.orEmpty())) })
    }

    if (showTVGuide) {
        TVConnectionGuide(
            onDismiss = { showTVGuide = false },
            onStart = { showTVGuide = false; tvMode = true }
        )
    }

    val current = session
    if (tvMode && current?.room?.isHost == true) {
        PartyTVDisplay(
            session = current,
            questions = questions,
            onClose = { tvMode = false },
            onAnswer = coordinator::answer,
            onStart = coordinator::startGame,
            onReveal = coordinator::reveal,
            onNext = coordinator::next
        )
        return
    }

    Column(Modifier.fillMaxSize().background(PartyNavy)) {
        Row(Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
            TextButton(onClick = {
                if (session != null) leave()
                else if (page != PartyPage.MENU) page = PartyPage.MENU
                else onBack()
            }) { Text("‹ ${LocalizedOrLoadingText("Back")}", color = Color.White) }
            Spacer(Modifier.weight(1f)); Text("👥  ${coreUi("party_mode", language) ?: "Party Mode"}", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 19.sp); Spacer(Modifier.weight(1f))
            if (current?.room?.isHost == true) {
                TextButton(onClick = { showTVGuide = true }) { Text("▣ ${LocalizedOrLoadingText("TV")}", color = Color.White, fontWeight = FontWeight.Bold) }
            } else Spacer(Modifier.width(62.dp))
        }
        if (current == null) {
            when (page) {
                PartyPage.MENU -> PartyMenu(
                    hasSaved = false, working = working,
                    nearbyParties = nearbyParties,
                    onCreate = { page = PartyPage.SETUP }, onJoin = { page = PartyPage.JOIN },
                    onJoinNearby = { code, name ->
                        preferences.edit().putString("name", name).apply()
                        coordinator.join(name, code)
                    },
                    onRejoin = {}
                )
                PartyPage.SETUP -> PartySetup(questions, working, preferences.getString("name", "Host") ?: "Host", onCreate = coordinator::create, onError = { error = it })
                PartyPage.JOIN -> PartyJoin(working, preferences.getString("name", "Player") ?: "Player", initialCode, onJoin = coordinator::join)
            }
        } else {
            when (current.room.phase) {
                "lobby" -> PartyLobby(current, working, onStart = coordinator::startGame, onTV = { showTVGuide = true })
                "question", "reveal" -> PartyGame(current, questions, working, onAnswer = coordinator::answer, onReveal = coordinator::reveal, onNext = coordinator::next)
                else -> PartyResults(current.room, onDone = ::leave)
            }
        }
    }
}

@Composable
private fun TVConnectionGuide(onDismiss: () -> Unit, onStart: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        icon = { Text("📺", fontSize = 42.sp) },
        title = { Text(LocalizedOrLoadingText("Set Up TV Display"), fontWeight = FontWeight.Black) },
        text = {
            Column(
                Modifier.heightIn(max = 610.dp).verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(13.dp)
            ) {
                Text(LocalizedOrLoadingText("Mirror the host phone to the TV first. Players keep answering on their own phones."))
                TVGuideStep("1", "Use the same Wi-Fi", "Connect the host phone and smart TV to the same Wi-Fi network.")
                TVGuideStep("2", "Connect the host phone", "Choose one method below. Approve the connection or enter the code shown on the TV if asked.")
                TVGuideRow("Samsung phone · Smart View", "Swipe down twice for Quick Settings, tap Smart View, select the TV, then tap Start now.")
                TVGuideRow("Android · Chromecast or Google TV", "Open Quick Settings, tap Cast or Screen Cast, then select the TV. Some phones use Google Home → TV → Cast my screen.")
                TVGuideRow("iPhone or iPad · AirPlay", "Open Control Center, tap Screen Mirroring, select the TV, and enter its AirPlay code if asked.")
                TVGuideRow("Any TV · HDMI", "Connect a compatible USB-C or Lightning HDMI adapter and cable, then change the TV input to that HDMI port. This is the universal fallback.")
                TVGuideStep("3", "Open the game display", "After the TV shows this phone, tap the button below. Turn the host phone sideways for the full-screen question and scoreboard layout.")
            }
        },
        confirmButton = { Button(onClick = onStart) { Text(LocalizedOrLoadingText("TV Is Connected — Open Display")) } },
        dismissButton = { TextButton(onClick = onDismiss) { Text(LocalizedOrLoadingText("Cancel")) } }
    )
}

@Composable
private fun TVGuideStep(number: String, title: String, detail: String) {
    Row(verticalAlignment = Alignment.Top, horizontalArrangement = Arrangement.spacedBy(11.dp)) {
        Surface(color = PartyGold, shape = RoundedCornerShape(50), modifier = Modifier.size(30.dp)) {
            Box(contentAlignment = Alignment.Center) { Text(number, color = Color.Black, fontWeight = FontWeight.Black) }
        }
        Column {
            Text(LocalizedOrLoadingText(title), fontWeight = FontWeight.Black)
            Text(LocalizedOrLoadingText(detail), color = MaterialTheme.colorScheme.onSurface.copy(alpha = .72f), fontSize = 13.sp)
        }
    }
}

@Composable
private fun TVGuideRow(title: String, detail: String) {
    Column {
        Text(LocalizedOrLoadingText(title), fontWeight = FontWeight.Bold)
        Text(LocalizedOrLoadingText(detail), color = MaterialTheme.colorScheme.onSurface.copy(alpha = .7f), fontSize = 13.sp)
    }
}

@Composable
private fun rememberLocalizedQuestion(question: Question?): List<String>? {
    val language = LocalAppLanguage.current
    val repository = LocalTranslationRepository.current
    val source = question?.let { listOf(it.category, it.question) + it.options + it.explanation }
    var localized by remember(question?.id, language.code) {
        mutableStateOf(if (language.code == "en") source else null)
    }
    LaunchedEffect(question?.id, language.code) {
        localized = when {
            source == null -> null
            language.code == "en" -> source
            else -> runCatching { repository.translate(source, language.code) }.getOrNull()
        }
    }
    return localized
}

@Composable
private fun PartyTVDisplay(
    session: PartySession,
    questions: List<Question>,
    onClose: () -> Unit,
    onAnswer: (Int) -> Unit,
    onStart: () -> Unit,
    onReveal: () -> Unit,
    onNext: () -> Unit
) {
    val room = session.room
    val question = questions.firstOrNull { it.id == room.questionId }
    val localizedQuestion = rememberLocalizedQuestion(question)
    Column(
        Modifier.fillMaxSize().background(Color(0xFF090C1B)).padding(22.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            Text("MANNA ${LocalizedOrLoadingText("PARTY")}", color = PartyGold, fontSize = 18.sp, fontWeight = FontWeight.Black, letterSpacing = 2.sp)
            Spacer(Modifier.weight(1f))
            Text("${LocalizedOrLoadingText("ROOM")} ${room.code}", color = Color.White.copy(alpha = .55f), fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold)
            TextButton(onClick = onClose) { Text("✕", color = Color.White, fontSize = 22.sp) }
        }
        when (room.phase) {
            "lobby" -> {
                Spacer(Modifier.weight(1f))
                Text(LocalizedOrLoadingText("Join the game on your phone"), color = Color.White, fontSize = 29.sp, fontWeight = FontWeight.Black, textAlign = TextAlign.Center)
                Text(room.code, color = PartyGold, fontSize = 62.sp, fontWeight = FontWeight.Black, fontFamily = FontFamily.Monospace, letterSpacing = 9.sp)
                Text("${room.players.size} ${LocalizedOrLoadingText("of 12 players joined")}", color = Color.White.copy(alpha = .7f), fontSize = 18.sp, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(12.dp))
                Text(room.players.joinToString("  •  ") { it.name }, color = Color.White, fontSize = 17.sp, textAlign = TextAlign.Center)
                Spacer(Modifier.height(20.dp))
                if (room.players.size >= 2) Button(onClick = onStart, colors = ButtonDefaults.buttonColors(containerColor = PartyGold)) { Text(LocalizedOrLoadingText("Start Game"), color = Color.Black, fontWeight = FontWeight.Bold) }
                else Text(LocalizedOrLoadingText("Waiting for another player…"), color = Color.White.copy(alpha = .55f))
                Spacer(Modifier.weight(1f))
            }
            "question", "reveal" -> {
                Row(Modifier.fillMaxWidth()) {
                    Text("${LocalizedOrLoadingText("QUESTION")} ${room.questionNumber} ${LocalizedOrLoadingText("OF")} ${room.settings.questionCount}", color = Color.White.copy(alpha = .6f), fontWeight = FontWeight.Black)
                    Spacer(Modifier.weight(1f))
                    Text("${room.answeredCount} / ${room.players.size} ${LocalizedOrLoadingText("ANSWERED")}", color = Color.White.copy(alpha = .6f), fontWeight = FontWeight.Black)
                }
                if (question == null) {
                    Spacer(Modifier.weight(1f)); Text(LocalizedOrLoadingText("Question unavailable on this version of Manna."), color = Color.Red); Spacer(Modifier.weight(1f))
                } else if (localizedQuestion == null) {
                    Spacer(Modifier.weight(1f)); CircularProgressIndicator(color = PartyGold); Spacer(Modifier.weight(1f))
                } else {
                    Spacer(Modifier.height(8.dp))
                    Text(localizedQuestion[0].uppercase(), color = PartyGold, fontWeight = FontWeight.Black, fontSize = 13.sp)
                    Spacer(Modifier.height(8.dp))
                    Text(localizedQuestion[1], color = Color.White, fontSize = 27.sp, fontWeight = FontWeight.Black, textAlign = TextAlign.Center, maxLines = 3)
                    Spacer(Modifier.height(12.dp))
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                            localizedQuestion.drop(2).take(question.options.size).filterIndexed { index, _ -> index % 2 == 0 }.forEachIndexed { row, option ->
                                val index = row * 2
                                TVAnswer(option, index, room.phase == "reveal" && index == question.correctIndex) { if (room.phase == "question") onAnswer(index) }
                            }
                        }
                        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                            localizedQuestion.drop(2).take(question.options.size).filterIndexed { index, _ -> index % 2 == 1 }.forEachIndexed { row, option ->
                                val index = row * 2 + 1
                                TVAnswer(option, index, room.phase == "reveal" && index == question.correctIndex) { if (room.phase == "question") onAnswer(index) }
                            }
                        }
                    }
                    Spacer(Modifier.height(10.dp))
                    if (room.phase == "reveal") {
                        Text("${LocalizedOrLoadingText("Correct answer")}: ${localizedQuestion[2 + question.correctIndex]}", color = Color.Green, fontSize = 21.sp, fontWeight = FontWeight.Black)
                        val names = room.players.filter { it.wasCorrect == true }.joinToString(", ") { it.name }
                        Text(if (names.isEmpty()) LocalizedOrLoadingText("Nobody answered correctly") else "${LocalizedOrLoadingText("Correct")}: $names", color = Color.White.copy(alpha = .75f), fontWeight = FontWeight.SemiBold)
                    } else if (room.myAnswer != null) Text(LocalizedOrLoadingText("Host answer locked in • waiting for the room"), color = Color.Green, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.weight(1f))
                    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                        Text(room.players.take(4).mapIndexed { index, p -> "${index + 1}. ${p.name}  ${p.score}" }.joinToString("    "), color = Color.White.copy(alpha = .72f), fontWeight = FontWeight.Bold, modifier = Modifier.weight(1f))
                        Button(onClick = { if (room.phase == "question") onReveal() else onNext() }, colors = ButtonDefaults.buttonColors(containerColor = PartyGold)) {
                            Text(LocalizedOrLoadingText(if (room.phase == "question") "Reveal Answer" else if (room.questionNumber == room.settings.questionCount) "Finish Game" else "Next Question"), color = Color.Black, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
            else -> {
                Spacer(Modifier.weight(1f)); Text("🏆", fontSize = 58.sp); Text(LocalizedOrLoadingText("Party Complete"), color = Color.White, fontSize = 36.sp, fontWeight = FontWeight.Black)
                Spacer(Modifier.height(14.dp))
                room.players.take(8).forEachIndexed { index, player ->
                    Row(Modifier.fillMaxWidth(.75f).padding(vertical = 5.dp)) { Text(if (index == 0) "👑" else "${index + 1}", modifier = Modifier.width(42.dp)); Text(player.name, color = if (index == 0) PartyGold else Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold); Spacer(Modifier.weight(1f)); Text("${player.score} / ${room.settings.questionCount}", color = if (index == 0) PartyGold else Color.White, fontSize = 20.sp, fontWeight = FontWeight.Black) }
                }
                Spacer(Modifier.weight(1f))
            }
        }
    }
}

@Composable
private fun TVAnswer(text: String, index: Int, correct: Boolean, onClick: () -> Unit) {
    Surface(
        color = if (correct) Color(0xFF245B45) else Color.White.copy(alpha = .08f),
        shape = RoundedCornerShape(14.dp),
        modifier = Modifier.fillMaxWidth().heightIn(min = 66.dp).clickable(onClick = onClick)
    ) {
        Row(Modifier.padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
            Text("${('A'.code + index).toChar()}.", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Black)
            Spacer(Modifier.width(12.dp)); Text(text, color = Color.White, fontSize = 19.sp, fontWeight = FontWeight.Bold, maxLines = 2)
        }
    }
}

@Composable
private fun PartyMenu(hasSaved: Boolean, working: Boolean, nearbyParties: List<NearbyParty>, onCreate: () -> Unit, onJoin: () -> Unit, onJoinNearby: (String, String) -> Unit, onRejoin: () -> Unit) {
    val context = LocalContext.current
    val prefs = remember { context.getSharedPreferences("manna_party", Context.MODE_PRIVATE) }
    var name by remember { mutableStateOf(prefs.getString("name", "") ?: "") }
    Column(Modifier.fillMaxSize().padding(28.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
        Text("👥", fontSize = 68.sp); Text(LocalizedOrLoadingText("Play Together"), color = Color.White, fontSize = 32.sp, fontWeight = FontWeight.Black)
        Spacer(Modifier.height(10.dp)); Text(LocalizedOrLoadingText("Everyone sees the same questions and answers on their own phone."), color = Color.White.copy(alpha = .65f), textAlign = TextAlign.Center)
        Spacer(Modifier.height(24.dp)); OutlinedTextField(value = name, onValueChange = { name = it.take(24) }, label = { Text(LocalizedOrLoadingText("Your name")) }, singleLine = true, modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(18.dp)); PartyPrimaryButton("Create Party Game", enabled = name.isNotBlank()) { prefs.edit().putString("name", name.trim()).apply(); onCreate() }
        if (nearbyParties.isNotEmpty()) {
            Spacer(Modifier.height(14.dp)); Text("◉  ${LocalizedOrLoadingText("Nearby on this Wi-Fi")}", color = Color.White.copy(alpha = .7f), fontWeight = FontWeight.Bold, modifier = Modifier.fillMaxWidth())
            nearbyParties.forEach { nearby ->
                Spacer(Modifier.height(8.dp))
                Surface(color = Color.White.copy(alpha = .09f), shape = RoundedCornerShape(12.dp), modifier = Modifier.fillMaxWidth().clickable(enabled = name.isNotBlank() && !working) { onJoinNearby(nearby.code, name.trim()) }) {
                    Row(Modifier.padding(15.dp), verticalAlignment = Alignment.CenterVertically) {
                        Text("👥  ${LocalizedOrLoadingText("Join")} ${nearby.hostName} · ${LocalizedOrLoadingText("Party")}", color = Color.White, fontWeight = FontWeight.Bold)
                        Spacer(Modifier.weight(1f)); Text("›", color = Color.White, fontSize = 22.sp)
                    }
                }
            }
        }
        Spacer(Modifier.height(10.dp)); OutlinedButton(onClick = { prefs.edit().putString("name", name.trim()).apply(); onJoin() }, enabled = name.isNotBlank(), modifier = Modifier.fillMaxWidth().height(54.dp)) { Text(LocalizedOrLoadingText("Join with a Code"), color = PartyGold, fontWeight = FontWeight.Bold) }
        if (hasSaved) TextButton(onClick = onRejoin) { Text(LocalizedOrLoadingText("Rejoin Previous Party"), color = Color.White.copy(alpha = .7f)) }
        if (working) ProgressIndicator()
    }
}

@Composable
private fun PartySetup(questions: List<Question>, working: Boolean, hostName: String, onCreate: (String, PartySettings, List<Question>) -> Unit, onError: (String) -> Unit) {
    var category by remember { mutableStateOf("All Categories") }
    var difficulty by remember { mutableStateOf("Deacon") }
    var childrenMode by remember { mutableStateOf(false) }
    var ageGroup by remember { mutableStateOf("4-10") }
    var count by remember { mutableIntStateOf(10) }
    var categoryMenu by remember { mutableStateOf(false) }
    val categories = remember(questions) { listOf("All Categories") + questions.filter { it.ageGroup == null }.map { it.category }.distinct().sorted() }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp)) {
        Text(LocalizedOrLoadingText("Create Your Game"), color = Color.White, fontSize = 28.sp, fontWeight = FontWeight.Black); Spacer(Modifier.height(20.dp))
        Text(LocalizedOrLoadingText("Players"), color = Color.White.copy(alpha = .65f))
        SingleChoiceSegmentedButtonRow(Modifier.fillMaxWidth()) {
            listOf(false to "Adults", true to "Children").forEachIndexed { index, value ->
                SegmentedButton(selected = childrenMode == value.first, onClick = { childrenMode = value.first }, shape = SegmentedButtonDefaults.itemShape(index, 2)) { Text(LocalizedOrLoadingText(value.second)) }
            }
        }
        Spacer(Modifier.height(18.dp))
        if (childrenMode) {
            Text(LocalizedOrLoadingText("Children's Age"), color = Color.White.copy(alpha = .65f))
            SingleChoiceSegmentedButtonRow(Modifier.fillMaxWidth()) {
                childAgeGroups.forEachIndexed { index, group ->
                    SegmentedButton(selected = ageGroup == group.id, onClick = { ageGroup = group.id }, shape = SegmentedButtonDefaults.itemShape(index, childAgeGroups.size)) { Text(group.label, fontSize = 12.sp) }
                }
            }
            val group = childAgeGroups.first { it.id == ageGroup }
            Text("${"%,d".format(group.questionCount)} ${LocalizedOrLoadingText("questions")} · ${group.answerChoices} ${LocalizedOrLoadingText("choices each")}", color = PartyGold, fontSize = 13.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(top = 10.dp))
        } else {
            Text(LocalizedOrLoadingText("Category"), color = Color.White.copy(alpha = .65f)); Box { OutlinedButton(onClick = { categoryMenu = true }, modifier = Modifier.fillMaxWidth()) { Text(LocalizedOrLoadingText(category)) }; DropdownMenu(categoryMenu, { categoryMenu = false }) { categories.forEach { item -> DropdownMenuItem(text = { Text(LocalizedOrLoadingText(item)) }, onClick = { category = item; categoryMenu = false }) } } }
            Spacer(Modifier.height(18.dp)); Text(LocalizedOrLoadingText("Difficulty"), color = Color.White.copy(alpha = .65f)); SingleChoiceSegmentedButtonRow(Modifier.fillMaxWidth()) { listOf("Layperson", "Deacon", "Pastor").forEachIndexed { index, value -> SegmentedButton(selected = difficulty == value, onClick = { difficulty = value }, shape = SegmentedButtonDefaults.itemShape(index, 3)) { Text(LocalizedOrLoadingText(value), fontSize = 12.sp) } } }
        }
        Spacer(Modifier.height(18.dp)); Text(LocalizedOrLoadingText("Questions"), color = Color.White.copy(alpha = .65f)); SingleChoiceSegmentedButtonRow(Modifier.fillMaxWidth()) { listOf(5, 10, 20).forEachIndexed { index, value -> SegmentedButton(selected = count == value, onClick = { count = value }, shape = SegmentedButtonDefaults.itemShape(index, 3)) { Text(value.toString()) } } }
        Spacer(Modifier.height(28.dp)); PartyPrimaryButton(if (working) "Creating…" else "Create Room", !working) {
            val eligible = questions.filter {
                if (childrenMode) it.ageGroup == ageGroup
                else it.ageGroup == null && it.difficulty == difficulty && (category == "All Categories" || it.category == category)
            }
            val selected = if (!childrenMode && difficulty == "Pastor") {
                balancedPastorQuestions(eligible).take(count)
            } else eligible.shuffled().take(count)
            if (selected.size < count) { onError("There are not enough matching questions. Try All Categories or another difficulty."); return@PartyPrimaryButton }
            onCreate(
                hostName,
                PartySettings(if (childrenMode) "Children" else category, if (childrenMode) "Ages ${ageGroup.replace("-", "–")}" else difficulty, count, if (childrenMode) ageGroup else null),
                selected
            )
        }
    }
}

@Composable
private fun PartyJoin(working: Boolean, name: String, initialCode: String?, onJoin: (String, String) -> Unit) {
    var code by remember(initialCode) { mutableStateOf(initialCode?.uppercase()?.filter(Char::isLetterOrDigit)?.take(6).orEmpty()) }
    Column(Modifier.fillMaxSize().padding(28.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
        Text(LocalizedOrLoadingText("Enter Party Code"), color = Color.White, fontSize = 29.sp, fontWeight = FontWeight.Black); Spacer(Modifier.height(24.dp))
        OutlinedTextField(value = code, onValueChange = { code = it.uppercase().filter(Char::isLetterOrDigit).take(6) }, textStyle = LocalTextStyle.current.copy(fontSize = 30.sp, fontWeight = FontWeight.Black, fontFamily = FontFamily.Monospace, textAlign = TextAlign.Center), keyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.Characters), singleLine = true, modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(22.dp)); PartyPrimaryButton(if (working) "Joining…" else "Join Party", code.length == 6 && !working) { onJoin(name, code) }
    }
}

@Composable
private fun PartyLobby(session: PartySession, working: Boolean, onStart: () -> Unit, onTV: () -> Unit) {
    val room = session.room
    val qr = remember(room.code) { qrBitmap("manna://party/${room.code}") }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text(LocalizedOrLoadingText(if (room.isHost) "Your Party Code" else "Waiting for the Host"), color = Color.White.copy(alpha = .7f), fontWeight = FontWeight.Bold)
        Text(room.code, color = PartyGold, fontSize = 42.sp, fontWeight = FontWeight.Black, fontFamily = FontFamily.Monospace, letterSpacing = 6.sp)
        qr?.let { Image(it.asImageBitmap(), LocalizedOrLoadingText("Party QR code"), Modifier.size(150.dp).background(Color.White).padding(8.dp)) }
        Spacer(Modifier.height(10.dp)); Text(room.settings.selectionSummary(), color = Color.White.copy(alpha = .55f), fontSize = 13.sp, textAlign = TextAlign.Center)
        if (room.isHost) {
            Spacer(Modifier.height(10.dp))
            Button(
                onClick = onTV,
                modifier = Modifier.fillMaxWidth().height(68.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(containerColor = PartyGold)
            ) {
                Text("📺  ${LocalizedOrLoadingText("OPEN TV DISPLAY")}", color = Color.Black, fontSize = 19.sp, fontWeight = FontWeight.Black)
            }
        }
        Spacer(Modifier.height(18.dp)); room.players.forEach { player -> Surface(color = Color.White.copy(alpha = .06f), shape = RoundedCornerShape(11.dp), modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) { Row(Modifier.padding(14.dp)) { Text(if (player.isHost) "👑  ${player.name}" else "👤  ${player.name}", color = if (player.isHost) PartyGold else Color.White, fontWeight = FontWeight.Bold); Spacer(Modifier.weight(1f)); if (player.id == room.myPlayerId) Text(LocalizedOrLoadingText("YOU"), color = PartyGold) } } }
        Spacer(Modifier.height(10.dp)); Text("${room.players.size} ${LocalizedOrLoadingText("of 12 players joined")}", color = Color.White.copy(alpha = .5f))
        Spacer(Modifier.height(18.dp)); if (room.isHost) {
            PartyPrimaryButton("Start Game", !working && room.players.size >= 2, onStart)
            if (room.players.size < 2) Text(LocalizedOrLoadingText("Waiting for another player to join"), color = Color.White.copy(alpha = .55f), fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
        } else ProgressIndicator("The host will start the game")
    }
}

@Composable
private fun PartyGame(session: PartySession, questions: List<Question>, working: Boolean, onAnswer: (Int) -> Unit, onReveal: () -> Unit, onNext: () -> Unit) {
    val room = session.room
    val question = questions.firstOrNull { it.id == room.questionId }
    val localizedQuestion = rememberLocalizedQuestion(question)
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(18.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Row(Modifier.fillMaxWidth()) { Text("${LocalizedOrLoadingText("Question")} ${room.questionNumber}/${room.settings.questionCount}", color = Color.White.copy(alpha = .6f), fontWeight = FontWeight.Bold); Spacer(Modifier.weight(1f)); Text("${room.answeredCount}/${room.players.size} ${LocalizedOrLoadingText("answered")}", color = Color.White.copy(alpha = .6f)) }
        Text("${LocalizedOrLoadingText("ROOM")} ${room.code}", color = Color.White.copy(alpha = .38f), fontSize = 11.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace, letterSpacing = 2.sp)
        if (question == null) Text(LocalizedOrLoadingText("This question is not available on this version of Manna."), color = Color.Red)
        else if (localizedQuestion == null) CircularProgressIndicator(color = PartyGold)
        else {
            Spacer(Modifier.height(12.dp)); Text(localizedQuestion[0].uppercase(), color = PartyGold, fontSize = 12.sp, fontWeight = FontWeight.Black)
            Spacer(Modifier.height(12.dp)); Text(localizedQuestion[1], color = Color.White, fontSize = 21.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center)
            Spacer(Modifier.height(16.dp)); localizedQuestion.drop(2).take(question.options.size).forEachIndexed { index, option ->
                val correct = room.phase == "reveal" && index == question.correctIndex
                val wrong = room.phase == "reveal" && room.myAnswer == index && !correct
                val selected = room.myAnswer == index
                Surface(color = if (correct) Color(0xFF245B45) else if (wrong) Color(0xFF642F37) else Color.White.copy(alpha = if (selected) .18f else .07f), shape = RoundedCornerShape(12.dp), modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp).clickable(enabled = room.phase == "question") { onAnswer(index) }) { Text("${('A'.code + index).toChar()}.  $option", color = Color.White, modifier = Modifier.padding(15.dp), fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal) }
            }
            if (room.phase == "reveal") { Spacer(Modifier.height(12.dp)); Surface(color = Color.White.copy(alpha = .06f), shape = RoundedCornerShape(12.dp), modifier = Modifier.fillMaxWidth()) { Column(Modifier.padding(14.dp)) { Text(if (room.myAnswer == question.correctIndex) LocalizedOrLoadingText("Correct!") else "${LocalizedOrLoadingText("Correct answer")}: ${localizedQuestion[2 + question.correctIndex]}", color = if (room.myAnswer == question.correctIndex) Color.Green else Color(0xFFFF7777), fontWeight = FontWeight.Bold); if (question.explanation.isNotBlank()) Text(localizedQuestion.last(), color = Color.White.copy(alpha = .65f), fontSize = 13.sp) } }; Spacer(Modifier.height(10.dp)); PartyRoundResults(room.players) }
            else if (room.myAnswer != null) { Spacer(Modifier.height(10.dp)); Text("✓ ${LocalizedOrLoadingText("Answer locked in")}", color = Color.Green, fontWeight = FontWeight.Bold) }
        }
        Spacer(Modifier.height(14.dp)); PartyLeaderboard(room)
        Spacer(Modifier.height(18.dp)); if (room.isHost) PartyPrimaryButton(if (room.phase == "question") "Reveal Answer" else if (room.questionNumber == room.settings.questionCount) "Finish Game" else "Next Question", !working) { if (room.phase == "question") onReveal() else onNext() } else Text(LocalizedOrLoadingText(if (room.phase == "question") "Waiting for the host to reveal the answer" else "Waiting for the next question"), color = Color.White.copy(alpha = .5f), fontSize = 13.sp)
    }
}

@Composable
private fun PartyRoundResults(players: List<PartyPlayer>) {
    val correct = players.filter { it.wasCorrect == true }
    val incorrect = players.filter { it.hasAnswered && it.wasCorrect == false }
    val unanswered = players.filter { !it.hasAnswered }
    Surface(color = Color.White.copy(alpha = .06f), shape = RoundedCornerShape(12.dp), modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(9.dp)) {
            Text(LocalizedOrLoadingText("This Round"), color = Color.White, fontSize = 17.sp, fontWeight = FontWeight.Black)
            RoundResultGroup("✓ Correct", Color.Green, correct)
            if (incorrect.isNotEmpty()) RoundResultGroup("✕ Incorrect", Color(0xFFFF7777), incorrect)
            if (unanswered.isNotEmpty()) RoundResultGroup("– No Answer", Color(0xFFFFB74D), unanswered)
        }
    }
}

@Composable
private fun RoundResultGroup(label: String, color: Color, players: List<PartyPlayer>) {
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Text("${LocalizedOrLoadingText(label)} · ${players.size}", color = color, fontWeight = FontWeight.Bold, fontSize = 14.sp)
        Text(if (players.isEmpty()) LocalizedOrLoadingText("Nobody") else players.joinToString(", ") { it.name }, color = Color.White.copy(alpha = .78f), fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
    }
}

@Composable
private fun PartyLeaderboard(room: PartyRoom) {
    Surface(color = Color.White.copy(alpha = .05f), shape = RoundedCornerShape(12.dp), modifier = Modifier.fillMaxWidth()) { Column(Modifier.padding(12.dp)) { room.players.take(5).forEachIndexed { index, player -> Row(Modifier.fillMaxWidth().padding(vertical = 3.dp)) { Text("${index + 1}", color = Color.White.copy(alpha = .5f), modifier = Modifier.width(24.dp)); Text(player.name, color = if (player.id == room.myPlayerId) PartyGold else Color.White, fontWeight = FontWeight.Bold); Spacer(Modifier.weight(1f)); Text(player.score.toString(), color = if (player.id == room.myPlayerId) PartyGold else Color.White, fontWeight = FontWeight.Black) } } } }
}

@Composable
private fun PartyResults(room: PartyRoom, onDone: () -> Unit) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) { Text("🏆", fontSize = 68.sp); Text(LocalizedOrLoadingText("Party Complete"), color = Color.White, fontSize = 31.sp, fontWeight = FontWeight.Black); Spacer(Modifier.height(18.dp)); room.players.forEachIndexed { index, player -> Surface(color = Color.White.copy(alpha = .07f), shape = RoundedCornerShape(13.dp), modifier = Modifier.fillMaxWidth().padding(vertical = 5.dp)) { Row(Modifier.padding(16.dp)) { Text(if (index == 0) "👑" else "${index + 1}", modifier = Modifier.width(40.dp)); Text(player.name, color = if (index == 0) PartyGold else Color.White, fontWeight = FontWeight.Bold); Spacer(Modifier.weight(1f)); Text("${player.score}/${room.settings.questionCount}", color = if (index == 0) PartyGold else Color.White, fontWeight = FontWeight.Black) } } }; Spacer(Modifier.height(18.dp)); PartyPrimaryButton("Done", true, onDone) }
}

@Composable
private fun PartyPrimaryButton(text: String, enabled: Boolean = true, onClick: () -> Unit) { Button(onClick = onClick, enabled = enabled, modifier = Modifier.fillMaxWidth().height(56.dp), colors = ButtonDefaults.buttonColors(containerColor = PartyGold)) { Text(LocalizedOrLoadingText(text), color = Color.Black, fontWeight = FontWeight.Bold, fontSize = 17.sp) } }

@Composable
private fun ProgressIndicator(label: String? = null) { Row(verticalAlignment = Alignment.CenterVertically) { CircularProgressIndicator(Modifier.size(22.dp), color = PartyGold, strokeWidth = 2.dp); if (label != null) { Spacer(Modifier.width(10.dp)); Text(LocalizedOrLoadingText(label), color = Color.White.copy(alpha = .65f)) } } }

private fun qrBitmap(value: String): Bitmap? = runCatching {
    val matrix = QRCodeWriter().encode(value, BarcodeFormat.QR_CODE, 400, 400)
    Bitmap.createBitmap(matrix.width, matrix.height, Bitmap.Config.ARGB_8888).apply {
        for (x in 0 until matrix.width) for (y in 0 until matrix.height) setPixel(x, y, if (matrix[x, y]) android.graphics.Color.BLACK else android.graphics.Color.WHITE)
    }
}.getOrNull()
