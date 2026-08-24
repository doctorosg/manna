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

internal data class PartySettings(val category: String, val difficulty: String, val questionCount: Int)
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
    val preferences = remember { context.getSharedPreferences("manna_party", Context.MODE_PRIVATE) }
    var page by remember(initialCode) { mutableStateOf(if (initialCode.isNullOrBlank()) PartyPage.MENU else PartyPage.JOIN) }
    var session by remember { mutableStateOf<PartySession?>(null) }
    var working by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
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

    fun leave() {
        coordinator.leave()
        session = null
        page = PartyPage.MENU
    }

    if (error != null) {
        AlertDialog(onDismissRequest = { error = null }, confirmButton = { TextButton(onClick = { error = null }) { Text("OK") } }, title = { Text("Party Mode") }, text = { Text(error.orEmpty()) })
    }

    Column(Modifier.fillMaxSize().background(PartyNavy)) {
        Row(Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
            TextButton(onClick = {
                if (session != null) leave()
                else if (page != PartyPage.MENU) page = PartyPage.MENU
                else onBack()
            }) { Text("‹ Back", color = Color.White) }
            Spacer(Modifier.weight(1f)); Text("👥  Party Mode", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 19.sp); Spacer(Modifier.weight(1f)); Spacer(Modifier.width(62.dp))
        }
        val current = session
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
                "lobby" -> PartyLobby(current, working, onStart = coordinator::startGame)
                "question", "reveal" -> PartyGame(current, questions, working, onAnswer = coordinator::answer, onReveal = coordinator::reveal, onNext = coordinator::next)
                else -> PartyResults(current.room, onDone = ::leave)
            }
        }
    }
}

@Composable
private fun PartyMenu(hasSaved: Boolean, working: Boolean, nearbyParties: List<NearbyParty>, onCreate: () -> Unit, onJoin: () -> Unit, onJoinNearby: (String, String) -> Unit, onRejoin: () -> Unit) {
    val context = LocalContext.current
    val prefs = remember { context.getSharedPreferences("manna_party", Context.MODE_PRIVATE) }
    var name by remember { mutableStateOf(prefs.getString("name", "") ?: "") }
    Column(Modifier.fillMaxSize().padding(28.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
        Text("👥", fontSize = 68.sp); Text("Play Together", color = Color.White, fontSize = 32.sp, fontWeight = FontWeight.Black)
        Spacer(Modifier.height(10.dp)); Text("Everyone sees the same questions and answers on their own phone.", color = Color.White.copy(alpha = .65f), textAlign = TextAlign.Center)
        Spacer(Modifier.height(24.dp)); OutlinedTextField(value = name, onValueChange = { name = it.take(24) }, label = { Text("Your name") }, singleLine = true, modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(18.dp)); PartyPrimaryButton("Create Party Game", enabled = name.isNotBlank()) { prefs.edit().putString("name", name.trim()).apply(); onCreate() }
        if (nearbyParties.isNotEmpty()) {
            Spacer(Modifier.height(14.dp)); Text("◉  Nearby on this Wi-Fi", color = Color.White.copy(alpha = .7f), fontWeight = FontWeight.Bold, modifier = Modifier.fillMaxWidth())
            nearbyParties.forEach { nearby ->
                Spacer(Modifier.height(8.dp))
                Surface(color = Color.White.copy(alpha = .09f), shape = RoundedCornerShape(12.dp), modifier = Modifier.fillMaxWidth().clickable(enabled = name.isNotBlank() && !working) { onJoinNearby(nearby.code, name.trim()) }) {
                    Row(Modifier.padding(15.dp), verticalAlignment = Alignment.CenterVertically) {
                        Text("👥  Join ${nearby.hostName}’s Party", color = Color.White, fontWeight = FontWeight.Bold)
                        Spacer(Modifier.weight(1f)); Text("›", color = Color.White, fontSize = 22.sp)
                    }
                }
            }
        }
        Spacer(Modifier.height(10.dp)); OutlinedButton(onClick = { prefs.edit().putString("name", name.trim()).apply(); onJoin() }, enabled = name.isNotBlank(), modifier = Modifier.fillMaxWidth().height(54.dp)) { Text("Join with a Code", color = PartyGold, fontWeight = FontWeight.Bold) }
        if (hasSaved) TextButton(onClick = onRejoin) { Text("Rejoin Previous Party", color = Color.White.copy(alpha = .7f)) }
        if (working) ProgressIndicator()
    }
}

@Composable
private fun PartySetup(questions: List<Question>, working: Boolean, hostName: String, onCreate: (String, PartySettings, List<Question>) -> Unit, onError: (String) -> Unit) {
    var category by remember { mutableStateOf("All Categories") }
    var difficulty by remember { mutableStateOf("Deacon") }
    var count by remember { mutableIntStateOf(10) }
    var categoryMenu by remember { mutableStateOf(false) }
    val categories = remember(questions) { listOf("All Categories") + questions.map { it.category }.distinct().sorted() }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp)) {
        Text("Create Your Game", color = Color.White, fontSize = 28.sp, fontWeight = FontWeight.Black); Spacer(Modifier.height(20.dp))
        Text("Category", color = Color.White.copy(alpha = .65f)); Box { OutlinedButton(onClick = { categoryMenu = true }, modifier = Modifier.fillMaxWidth()) { Text(category) }; DropdownMenu(categoryMenu, { categoryMenu = false }) { categories.forEach { item -> DropdownMenuItem(text = { Text(item) }, onClick = { category = item; categoryMenu = false }) } } }
        Spacer(Modifier.height(18.dp)); Text("Difficulty", color = Color.White.copy(alpha = .65f)); SingleChoiceSegmentedButtonRow(Modifier.fillMaxWidth()) { listOf("Layperson", "Deacon", "Pastor").forEachIndexed { index, value -> SegmentedButton(selected = difficulty == value, onClick = { difficulty = value }, shape = SegmentedButtonDefaults.itemShape(index, 3)) { Text(value, fontSize = 12.sp) } } }
        Spacer(Modifier.height(18.dp)); Text("Questions", color = Color.White.copy(alpha = .65f)); SingleChoiceSegmentedButtonRow(Modifier.fillMaxWidth()) { listOf(5, 10, 20).forEachIndexed { index, value -> SegmentedButton(selected = count == value, onClick = { count = value }, shape = SegmentedButtonDefaults.itemShape(index, 3)) { Text(value.toString()) } } }
        Spacer(Modifier.height(28.dp)); PartyPrimaryButton(if (working) "Creating…" else "Create Room", !working) {
            val selected = questions.filter { it.difficulty == difficulty && (category == "All Categories" || it.category == category) }.shuffled().take(count)
            if (selected.size < count) { onError("There are not enough matching questions. Try All Categories or another difficulty."); return@PartyPrimaryButton }
            onCreate(hostName, PartySettings(category, difficulty, count), selected)
        }
    }
}

@Composable
private fun PartyJoin(working: Boolean, name: String, initialCode: String?, onJoin: (String, String) -> Unit) {
    var code by remember(initialCode) { mutableStateOf(initialCode?.uppercase()?.filter(Char::isLetterOrDigit)?.take(6).orEmpty()) }
    Column(Modifier.fillMaxSize().padding(28.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
        Text("Enter Party Code", color = Color.White, fontSize = 29.sp, fontWeight = FontWeight.Black); Spacer(Modifier.height(24.dp))
        OutlinedTextField(value = code, onValueChange = { code = it.uppercase().filter(Char::isLetterOrDigit).take(6) }, textStyle = LocalTextStyle.current.copy(fontSize = 30.sp, fontWeight = FontWeight.Black, fontFamily = FontFamily.Monospace, textAlign = TextAlign.Center), keyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.Characters), singleLine = true, modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(22.dp)); PartyPrimaryButton(if (working) "Joining…" else "Join Party", code.length == 6 && !working) { onJoin(name, code) }
    }
}

@Composable
private fun PartyLobby(session: PartySession, working: Boolean, onStart: () -> Unit) {
    val room = session.room
    val qr = remember(room.code) { qrBitmap("manna://party/${room.code}") }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text(if (room.isHost) "Your Party Code" else "Waiting for the Host", color = Color.White.copy(alpha = .7f), fontWeight = FontWeight.Bold)
        Text(room.code, color = PartyGold, fontSize = 42.sp, fontWeight = FontWeight.Black, fontFamily = FontFamily.Monospace, letterSpacing = 6.sp)
        qr?.let { Image(it.asImageBitmap(), "Party QR code", Modifier.size(150.dp).background(Color.White).padding(8.dp)) }
        Spacer(Modifier.height(10.dp)); Text("${room.settings.category} · ${room.settings.difficulty} · ${room.settings.questionCount} questions", color = Color.White.copy(alpha = .55f), fontSize = 13.sp, textAlign = TextAlign.Center)
        Spacer(Modifier.height(18.dp)); room.players.forEach { player -> Surface(color = Color.White.copy(alpha = .06f), shape = RoundedCornerShape(11.dp), modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) { Row(Modifier.padding(14.dp)) { Text(if (player.isHost) "👑  ${player.name}" else "👤  ${player.name}", color = if (player.isHost) PartyGold else Color.White, fontWeight = FontWeight.Bold); Spacer(Modifier.weight(1f)); if (player.id == room.myPlayerId) Text("YOU", color = PartyGold) } } }
        Spacer(Modifier.height(10.dp)); Text("${room.players.size} of 12 players joined", color = Color.White.copy(alpha = .5f))
        Spacer(Modifier.height(18.dp)); if (room.isHost) {
            PartyPrimaryButton("Start Game", !working && room.players.size >= 2, onStart)
            if (room.players.size < 2) Text("Waiting for another player to join", color = Color.White.copy(alpha = .55f), fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
        } else ProgressIndicator("The host will start the game")
    }
}

@Composable
private fun PartyGame(session: PartySession, questions: List<Question>, working: Boolean, onAnswer: (Int) -> Unit, onReveal: () -> Unit, onNext: () -> Unit) {
    val room = session.room
    val question = questions.firstOrNull { it.id == room.questionId }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(18.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Row(Modifier.fillMaxWidth()) { Text("Question ${room.questionNumber}/${room.settings.questionCount}", color = Color.White.copy(alpha = .6f), fontWeight = FontWeight.Bold); Spacer(Modifier.weight(1f)); Text("${room.answeredCount}/${room.players.size} answered", color = Color.White.copy(alpha = .6f)) }
        Text("ROOM ${room.code}", color = Color.White.copy(alpha = .38f), fontSize = 11.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace, letterSpacing = 2.sp)
        if (question == null) Text("This question is not available on this version of Manna.", color = Color.Red) else {
            Spacer(Modifier.height(12.dp)); Text(question.category.uppercase(), color = PartyGold, fontSize = 12.sp, fontWeight = FontWeight.Black)
            Spacer(Modifier.height(12.dp)); Text(question.question, color = Color.White, fontSize = 21.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center)
            Spacer(Modifier.height(16.dp)); question.options.forEachIndexed { index, option ->
                val correct = room.phase == "reveal" && index == question.correctIndex
                val wrong = room.phase == "reveal" && room.myAnswer == index && !correct
                val selected = room.myAnswer == index
                Surface(color = if (correct) Color(0xFF245B45) else if (wrong) Color(0xFF642F37) else Color.White.copy(alpha = if (selected) .18f else .07f), shape = RoundedCornerShape(12.dp), modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp).clickable(enabled = room.phase == "question") { onAnswer(index) }) { Text("${('A'.code + index).toChar()}.  $option", color = Color.White, modifier = Modifier.padding(15.dp), fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal) }
            }
            if (room.phase == "reveal") { Spacer(Modifier.height(12.dp)); Surface(color = Color.White.copy(alpha = .06f), shape = RoundedCornerShape(12.dp), modifier = Modifier.fillMaxWidth()) { Column(Modifier.padding(14.dp)) { Text(if (room.myAnswer == question.correctIndex) "Correct!" else "Correct answer: ${question.correct}", color = if (room.myAnswer == question.correctIndex) Color.Green else Color(0xFFFF7777), fontWeight = FontWeight.Bold); if (question.explanation.isNotBlank()) Text(question.explanation, color = Color.White.copy(alpha = .65f), fontSize = 13.sp) } }; Spacer(Modifier.height(10.dp)); PartyRoundResults(room.players) }
            else if (room.myAnswer != null) { Spacer(Modifier.height(10.dp)); Text("✓ Answer locked in", color = Color.Green, fontWeight = FontWeight.Bold) }
        }
        Spacer(Modifier.height(14.dp)); PartyLeaderboard(room)
        Spacer(Modifier.height(18.dp)); if (room.isHost) PartyPrimaryButton(if (room.phase == "question") "Reveal Answer" else if (room.questionNumber == room.settings.questionCount) "Finish Game" else "Next Question", !working) { if (room.phase == "question") onReveal() else onNext() } else Text(if (room.phase == "question") "Waiting for the host to reveal the answer" else "Waiting for the next question", color = Color.White.copy(alpha = .5f), fontSize = 13.sp)
    }
}

@Composable
private fun PartyRoundResults(players: List<PartyPlayer>) {
    val correct = players.filter { it.wasCorrect == true }
    val incorrect = players.filter { it.hasAnswered && it.wasCorrect == false }
    val unanswered = players.filter { !it.hasAnswered }
    Surface(color = Color.White.copy(alpha = .06f), shape = RoundedCornerShape(12.dp), modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(9.dp)) {
            Text("This Round", color = Color.White, fontSize = 17.sp, fontWeight = FontWeight.Black)
            RoundResultGroup("✓ Correct", Color.Green, correct)
            if (incorrect.isNotEmpty()) RoundResultGroup("✕ Incorrect", Color(0xFFFF7777), incorrect)
            if (unanswered.isNotEmpty()) RoundResultGroup("– No Answer", Color(0xFFFFB74D), unanswered)
        }
    }
}

@Composable
private fun RoundResultGroup(label: String, color: Color, players: List<PartyPlayer>) {
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Text("$label · ${players.size}", color = color, fontWeight = FontWeight.Bold, fontSize = 14.sp)
        Text(if (players.isEmpty()) "Nobody" else players.joinToString(", ") { it.name }, color = Color.White.copy(alpha = .78f), fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
    }
}

@Composable
private fun PartyLeaderboard(room: PartyRoom) {
    Surface(color = Color.White.copy(alpha = .05f), shape = RoundedCornerShape(12.dp), modifier = Modifier.fillMaxWidth()) { Column(Modifier.padding(12.dp)) { room.players.take(5).forEachIndexed { index, player -> Row(Modifier.fillMaxWidth().padding(vertical = 3.dp)) { Text("${index + 1}", color = Color.White.copy(alpha = .5f), modifier = Modifier.width(24.dp)); Text(player.name, color = if (player.id == room.myPlayerId) PartyGold else Color.White, fontWeight = FontWeight.Bold); Spacer(Modifier.weight(1f)); Text(player.score.toString(), color = if (player.id == room.myPlayerId) PartyGold else Color.White, fontWeight = FontWeight.Black) } } } }
}

@Composable
private fun PartyResults(room: PartyRoom, onDone: () -> Unit) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) { Text("🏆", fontSize = 68.sp); Text("Party Complete", color = Color.White, fontSize = 31.sp, fontWeight = FontWeight.Black); Spacer(Modifier.height(18.dp)); room.players.forEachIndexed { index, player -> Surface(color = Color.White.copy(alpha = .07f), shape = RoundedCornerShape(13.dp), modifier = Modifier.fillMaxWidth().padding(vertical = 5.dp)) { Row(Modifier.padding(16.dp)) { Text(if (index == 0) "👑" else "${index + 1}", modifier = Modifier.width(40.dp)); Text(player.name, color = if (index == 0) PartyGold else Color.White, fontWeight = FontWeight.Bold); Spacer(Modifier.weight(1f)); Text("${player.score}/${room.settings.questionCount}", color = if (index == 0) PartyGold else Color.White, fontWeight = FontWeight.Black) } } }; Spacer(Modifier.height(18.dp)); PartyPrimaryButton("Done", true, onDone) }
}

@Composable
private fun PartyPrimaryButton(text: String, enabled: Boolean = true, onClick: () -> Unit) { Button(onClick = onClick, enabled = enabled, modifier = Modifier.fillMaxWidth().height(56.dp), colors = ButtonDefaults.buttonColors(containerColor = PartyGold)) { Text(text, color = Color.Black, fontWeight = FontWeight.Bold, fontSize = 17.sp) } }

@Composable
private fun ProgressIndicator(label: String? = null) { Row(verticalAlignment = Alignment.CenterVertically) { CircularProgressIndicator(Modifier.size(22.dp), color = PartyGold, strokeWidth = 2.dp); if (label != null) { Spacer(Modifier.width(10.dp)); Text(label, color = Color.White.copy(alpha = .65f)) } } }

private fun qrBitmap(value: String): Bitmap? = runCatching {
    val matrix = QRCodeWriter().encode(value, BarcodeFormat.QR_CODE, 400, 400)
    Bitmap.createBitmap(matrix.width, matrix.height, Bitmap.Config.ARGB_8888).apply {
        for (x in 0 until matrix.width) for (y in 0 until matrix.height) setPixel(x, y, if (matrix[x, y]) android.graphics.Color.BLACK else android.graphics.Color.WHITE)
    }
}.getOrNull()
