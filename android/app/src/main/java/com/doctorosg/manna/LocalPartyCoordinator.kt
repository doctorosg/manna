package com.oddcurrent.manna

import android.content.Context
import android.net.nsd.NsdManager
import android.net.nsd.NsdServiceInfo
import android.os.Handler
import android.os.Looper
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.BufferedWriter
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.InetSocketAddress
import java.net.ServerSocket
import java.net.Socket
import java.security.SecureRandom
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.Executors

/** Backend-free Party Mode. The host phone owns state and talks directly to up to 11 guests. */
internal class LocalPartyCoordinator(
    context: Context,
    private val questions: List<Question>,
    private val onSession: (PartySession) -> Unit,
    private val onNearby: (List<NearbyParty>) -> Unit,
    private val onWorking: (Boolean) -> Unit,
    private val onError: (String) -> Unit
) {
    private data class LocalQuestion(val id: String, val correctIndex: Int)
    private data class LocalPlayer(
        val id: String,
        val token: String,
        val name: String,
        var score: Int = 0,
        val answers: MutableMap<Int, Int> = mutableMapOf()
    )
    private data class LocalRoom(
        val code: String,
        val hostPlayerId: String,
        val settings: PartySettings,
        val questions: List<LocalQuestion>,
        var phase: String = "lobby",
        var currentIndex: Int = -1,
        val players: MutableList<LocalPlayer>,
        var version: Int = 1
    )

    private val main = Handler(Looper.getMainLooper())
    private val transport = LocalPartyTransport(context.applicationContext, ::handleTransportEvent)
    private var hostRoom: LocalRoom? = null
    private var sessionToken: String? = null

    fun startDiscovery() = transport.startDiscovery()

    fun create(hostName: String, settings: PartySettings, selected: List<Question>) {
        leave(keepDiscovery = true)
        onWorking(true)
        val host = LocalPlayer(UUID.randomUUID().toString(), UUID.randomUUID().toString(), cleanName(hostName, "Host"))
        val code = randomCode()
        hostRoom = LocalRoom(
            code = code,
            hostPlayerId = host.id,
            settings = settings,
            questions = selected.map { LocalQuestion(it.id, it.correctIndex) },
            players = mutableListOf(host)
        )
        sessionToken = host.token
        transport.startHost(code, host.name)
        publishHostAndGuests()
        onWorking(false)
    }

    fun join(name: String, code: String) {
        onWorking(true)
        transport.join(cleanName(name, "Player"), code.uppercase())
    }

    fun startGame() {
        mutateHost { room ->
            if (room.phase != "lobby" || room.players.size < 2) throw IllegalStateException("At least two players are required.")
            room.phase = "question"
            room.currentIndex = 0
        }
        if (hostRoom?.phase == "question") transport.stopAccepting()
    }

    fun answer(index: Int) {
        val room = hostRoom
        if (room != null) applyAnswer(sessionToken.orEmpty(), index, null)
        else transport.sendGuest(JSONObject().put("type", "action").put("token", sessionToken).put("action", "answer").put("answerIndex", index))
    }

    fun reveal() = mutateHost { room ->
        if (room.phase != "question") throw IllegalStateException("There is no question to reveal.")
        val correct = room.questions[room.currentIndex].correctIndex
        room.players.filter { it.answers[room.currentIndex] == correct }.forEach { it.score += 1 }
        room.phase = "reveal"
    }

    fun next() = mutateHost { room ->
        if (room.phase != "reveal") throw IllegalStateException("Reveal the answer first.")
        if (room.currentIndex + 1 >= room.questions.size) room.phase = "finished"
        else { room.currentIndex += 1; room.phase = "question" }
    }

    fun leave(keepDiscovery: Boolean = false) {
        transport.stopSession()
        hostRoom = null
        sessionToken = null
        if (!keepDiscovery) transport.startDiscovery()
    }

    fun shutdown() = transport.shutdown()

    private fun mutateHost(change: (LocalRoom) -> Unit) {
        val room = hostRoom ?: return
        onWorking(true)
        runCatching { change(room); room.version += 1; publishHostAndGuests() }
            .onFailure { onError(it.message ?: "Party action failed.") }
        onWorking(false)
    }

    private fun handleTransportEvent(event: JSONObject) {
        when (event.optString("type")) {
            "nearbyPeers" -> {
                val peers = event.optJSONArray("peers") ?: JSONArray()
                onNearby(List(peers.length()) { index ->
                    val item = peers.getJSONObject(index)
                    NearbyParty(item.getString("code"), item.optString("name", "Nearby Host"))
                }.distinctBy { it.code }.sortedBy { it.hostName.lowercase() })
            }
            "hostMessage" -> handleHostMessage(event.getString("peerId"), event.getJSONObject("payload"))
            "hostDisconnected" -> handleHostDisconnect(event.optString("playerId"))
            "guestMessage" -> handleGuestMessage(event.getJSONObject("payload"))
            "guestDisconnected" -> {
                onWorking(false)
                onError("The host ended the nearby party or left the Wi-Fi network.")
            }
            "error" -> { onWorking(false); onError(event.optString("message", "Nearby Party Mode failed.")) }
        }
    }

    private fun handleHostMessage(peerId: String, message: JSONObject) {
        val room = hostRoom ?: return
        if (transport.playerId(peerId) == null) {
            if (message.optString("type") != "join" || message.optString("code") != room.code) {
                transport.sendHost(peerId, JSONObject().put("type", "error").put("message", "Incorrect nearby game code."))
                transport.closePeer(peerId)
                return
            }
            if (room.phase != "lobby" || room.players.size >= 12) {
                val text = if (room.players.size >= 12) "This party is full." else "This game has already started."
                transport.sendHost(peerId, JSONObject().put("type", "error").put("message", text))
                transport.closePeer(peerId)
                return
            }
            val player = LocalPlayer(UUID.randomUUID().toString(), UUID.randomUUID().toString(), cleanName(message.optString("name"), "Player"))
            room.players += player
            room.version += 1
            transport.setPlayerId(peerId, player.id)
            transport.sendHost(peerId, JSONObject().put("type", "joined").put("token", player.token).put("room", snapshot(room, player.id)))
            publishHostAndGuests(excludePeer = peerId)
            return
        }
        if (message.optString("type") == "action" && message.optString("action") == "answer") {
            applyAnswer(message.optString("token"), message.optInt("answerIndex", -1), peerId)
        }
    }

    private fun applyAnswer(token: String, answerIndex: Int, peerId: String?) {
        val room = hostRoom ?: return
        val player = room.players.firstOrNull { it.token == token }
        if (player == null || room.phase != "question" || answerIndex !in 0..5 ||
            (peerId != null && transport.playerId(peerId) != player.id)) {
            if (peerId != null) transport.sendHost(peerId, JSONObject().put("type", "error").put("message", "Answers are not open right now."))
            return
        }
        player.answers[room.currentIndex] = answerIndex
        room.version += 1
        publishHostAndGuests()
    }

    private fun handleHostDisconnect(playerId: String) {
        val room = hostRoom ?: return
        if (room.phase != "lobby" || playerId.isBlank()) return
        room.players.removeAll { it.id == playerId }
        room.version += 1
        publishHostAndGuests()
    }

    private fun handleGuestMessage(message: JSONObject) {
        when (message.optString("type")) {
            "joined" -> {
                sessionToken = message.getString("token")
                onSession(PartySession(sessionToken!!, parsePartyRoom(message.getJSONObject("room"))))
                onWorking(false)
            }
            "snapshot" -> onSession(PartySession(sessionToken.orEmpty(), parsePartyRoom(message.getJSONObject("room"))))
            "error" -> { onWorking(false); onError(message.optString("message", "Party connection failed.")) }
        }
    }

    private fun publishHostAndGuests(excludePeer: String? = null) {
        val room = hostRoom ?: return
        val host = room.players.first { it.id == room.hostPlayerId }
        onSession(PartySession(host.token, parsePartyRoom(snapshot(room, host.id))))
        transport.authenticatedPeers().filter { it != excludePeer }.forEach { peerId ->
            val playerId = transport.playerId(peerId) ?: return@forEach
            transport.sendHost(peerId, JSONObject().put("type", "snapshot").put("room", snapshot(room, playerId)))
        }
    }

    private fun snapshot(room: LocalRoom, viewerId: String): JSONObject {
        val viewer = room.players.first { it.id == viewerId }
        val correctIndex = room.questions.getOrNull(room.currentIndex)?.correctIndex
        val reveal = room.phase == "reveal" || room.phase == "finished"
        val sorted = room.players.sortedWith(compareByDescending<LocalPlayer> { it.score }.thenBy { it.name.lowercase() })
        return JSONObject()
            .put("code", room.code).put("phase", room.phase)
            .put("settings", JSONObject().put("category", room.settings.category).put("difficulty", room.settings.difficulty).put("questionCount", room.settings.questionCount))
            .put("currentIndex", room.currentIndex)
            .put("questionId", room.questions.getOrNull(room.currentIndex)?.id ?: JSONObject.NULL)
            .put("questionNumber", room.currentIndex + 1)
            .put("players", JSONArray().apply { sorted.forEach { player ->
                put(JSONObject().put("id", player.id).put("name", player.name).put("score", player.score)
                    .put("hasAnswered", player.answers.containsKey(room.currentIndex)).put("isHost", player.id == room.hostPlayerId)
                    .put("wasCorrect", if (reveal && correctIndex != null) player.answers[room.currentIndex] == correctIndex else JSONObject.NULL))
            } })
            .put("answeredCount", room.players.count { it.answers.containsKey(room.currentIndex) })
            .put("myPlayerId", viewer.id).put("myAnswer", viewer.answers[room.currentIndex] ?: JSONObject.NULL)
            .put("isHost", viewer.id == room.hostPlayerId).put("version", room.version)
    }

    private fun randomCode(): String {
        val alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        val random = SecureRandom()
        return buildString { repeat(6) { append(alphabet[random.nextInt(alphabet.length)]) } }
    }

    private fun cleanName(value: String, fallback: String): String =
        value.trim().replace(Regex("\\s+"), " ").ifBlank { fallback }.take(24)
}

internal fun parsePartyRoom(json: JSONObject): PartyRoom {
    val settings = json.getJSONObject("settings")
    val playersArray = json.getJSONArray("players")
    val players = List(playersArray.length()) { index -> playersArray.getJSONObject(index).let {
        PartyPlayer(it.getString("id"), it.getString("name"), it.getInt("score"), it.getBoolean("hasAnswered"),
            it.getBoolean("isHost"), if (it.isNull("wasCorrect")) null else it.getBoolean("wasCorrect"))
    } }
    return PartyRoom(
        json.getString("code"), json.getString("phase"),
        PartySettings(settings.getString("category"), settings.getString("difficulty"), settings.getInt("questionCount")),
        json.getInt("currentIndex"), if (json.isNull("questionId")) null else json.getString("questionId"),
        json.getInt("questionNumber"), players, json.getInt("answeredCount"), json.getString("myPlayerId"),
        if (json.isNull("myAnswer")) null else json.getInt("myAnswer"), json.getBoolean("isHost"), json.getInt("version")
    )
}

private class LocalPartyTransport(context: Context, private val emit: (JSONObject) -> Unit) {
    private data class Endpoint(val id: String, val name: String, val code: String, val host: String, val port: Int)
    private data class Peer(val id: String, val socket: Socket, val writer: BufferedWriter, @Volatile var playerId: String? = null)

    private val main = Handler(Looper.getMainLooper())
    private val executor = Executors.newCachedThreadPool()
    private val nsd = context.getSystemService(Context.NSD_SERVICE) as NsdManager
    private val endpoints = ConcurrentHashMap<String, Endpoint>()
    private val peers = ConcurrentHashMap<String, Peer>()
    @Volatile private var server: ServerSocket? = null
    @Volatile private var guestSocket: Socket? = null
    @Volatile private var guestWriter: BufferedWriter? = null
    private var registration: NsdManager.RegistrationListener? = null
    private var discovery: NsdManager.DiscoveryListener? = null

    fun startDiscovery() {
        if (discovery != null) return
        val listener = object : NsdManager.DiscoveryListener {
            override fun onDiscoveryStarted(type: String) { publishPeers() }
            override fun onServiceFound(info: NsdServiceInfo) {
                if (!info.serviceType.contains("_manna-party._tcp")) return
                @Suppress("DEPRECATION")
                nsd.resolveService(info, object : NsdManager.ResolveListener {
                    override fun onResolveFailed(serviceInfo: NsdServiceInfo, errorCode: Int) = Unit
                    override fun onServiceResolved(resolved: NsdServiceInfo) {
                        val parsed = parseServiceName(resolved.serviceName) ?: return
                        val address = resolved.host?.hostAddress ?: return
                        endpoints[parsed.first] = Endpoint(resolved.serviceName, parsed.second, parsed.first, address, resolved.port)
                        publishPeers()
                    }
                })
            }
            override fun onServiceLost(info: NsdServiceInfo) { endpoints.entries.removeAll { it.value.id == info.serviceName }; publishPeers() }
            override fun onDiscoveryStopped(type: String) = Unit
            override fun onStartDiscoveryFailed(type: String, code: Int) { discovery = null }
            override fun onStopDiscoveryFailed(type: String, code: Int) = Unit
        }
        discovery = listener
        runCatching { nsd.discoverServices(SERVICE_TYPE, NsdManager.PROTOCOL_DNS_SD, listener) }
    }

    fun startHost(code: String, name: String) {
        stopSession()
        executor.execute {
            try {
                val listening = ServerSocket().apply { reuseAddress = true; bind(InetSocketAddress(0)) }
                server = listening
                register(code, name, listening.localPort)
                while (!listening.isClosed) attachHost(listening.accept())
            } catch (error: Exception) {
                if (server != null) emitError("Unable to host on this Wi-Fi: ${error.message ?: "network error"}")
            }
        }
    }

    fun join(name: String, code: String) {
        val endpoint = endpoints[code]
        if (endpoint == null) { emitError("Party not found on this Wi-Fi network. Make sure the host is waiting in the lobby."); return }
        executor.execute {
            try {
                val socket = Socket().apply { connect(InetSocketAddress(endpoint.host, endpoint.port), 8_000) }
                guestSocket = socket
                guestWriter = BufferedWriter(OutputStreamWriter(socket.getOutputStream(), Charsets.UTF_8))
                sendGuest(JSONObject().put("type", "join").put("code", code).put("name", name))
                readGuest(socket)
            } catch (error: Exception) { emitError("Unable to join the nearby party: ${error.message ?: "network error"}") }
        }
    }

    fun sendGuest(message: JSONObject) = executor.execute { write(guestWriter, message) }
    fun sendHost(peerId: String, message: JSONObject) = executor.execute { write(peers[peerId]?.writer, message) }
    fun playerId(peerId: String): String? = peers[peerId]?.playerId
    fun setPlayerId(peerId: String, playerId: String) { peers[peerId]?.playerId = playerId }
    fun authenticatedPeers(): List<String> = peers.values.filter { it.playerId != null }.map { it.id }
    fun closePeer(peerId: String) { peers.remove(peerId)?.let { runCatching { it.socket.close() } } }

    fun stopAccepting() {
        unregister()
        runCatching { server?.close() }
        server = null
    }

    fun stopSession() {
        stopAccepting()
        peers.values.forEach { runCatching { it.socket.close() } }
        peers.clear()
        runCatching { guestSocket?.close() }
        guestSocket = null; guestWriter = null
    }

    fun shutdown() {
        stopSession()
        discovery?.let { runCatching { nsd.stopServiceDiscovery(it) } }
        discovery = null
        executor.shutdownNow()
    }

    private fun attachHost(socket: Socket) {
        val peer = Peer(UUID.randomUUID().toString(), socket, BufferedWriter(OutputStreamWriter(socket.getOutputStream(), Charsets.UTF_8)))
        peers[peer.id] = peer
        executor.execute {
            try {
                BufferedReader(InputStreamReader(socket.getInputStream(), Charsets.UTF_8)).useLines { lines ->
                    lines.forEach { line -> runCatching { JSONObject(line) }.getOrNull()?.let { payload ->
                        post(JSONObject().put("type", "hostMessage").put("peerId", peer.id).put("payload", payload))
                    } }
                }
            } finally {
                val removed = peers.remove(peer.id)
                if (removed != null) post(JSONObject().put("type", "hostDisconnected").put("peerId", peer.id).put("playerId", removed.playerId ?: ""))
                runCatching { socket.close() }
            }
        }
    }

    private fun readGuest(socket: Socket) {
        try {
            BufferedReader(InputStreamReader(socket.getInputStream(), Charsets.UTF_8)).useLines { lines ->
                lines.forEach { line -> runCatching { JSONObject(line) }.getOrNull()?.let { payload ->
                    post(JSONObject().put("type", "guestMessage").put("payload", payload))
                } }
            }
        } finally {
            if (guestSocket === socket) { guestSocket = null; guestWriter = null; post(JSONObject().put("type", "guestDisconnected")) }
            runCatching { socket.close() }
        }
    }

    private fun write(writer: BufferedWriter?, message: JSONObject) {
        try { requireNotNull(writer); synchronized(writer) { writer.write(message.toString()); writer.newLine(); writer.flush() } }
        catch (_: Exception) { emitError("Nearby connection ended.") }
    }

    private fun register(code: String, name: String, port: Int) {
        val listener = object : NsdManager.RegistrationListener {
            override fun onServiceRegistered(info: NsdServiceInfo) = Unit
            override fun onRegistrationFailed(info: NsdServiceInfo, code: Int) { emitError("The game started, but automatic discovery is unavailable.") }
            override fun onServiceUnregistered(info: NsdServiceInfo) = Unit
            override fun onUnregistrationFailed(info: NsdServiceInfo, code: Int) = Unit
        }
        registration = listener
        val info = NsdServiceInfo().apply {
            serviceName = "Manna-$code-${safeName(name)}"; serviceType = SERVICE_TYPE; this.port = port
        }
        runCatching { nsd.registerService(info, NsdManager.PROTOCOL_DNS_SD, listener) }
    }

    private fun unregister() { registration?.let { runCatching { nsd.unregisterService(it) } }; registration = null }

    private fun publishPeers() = post(JSONObject().put("type", "nearbyPeers").put("peers", JSONArray().apply {
        endpoints.values.sortedBy { it.name.lowercase() }.forEach { put(JSONObject().put("code", it.code).put("name", it.name)) }
    }))

    private fun post(event: JSONObject) = main.post { emit(event) }
    private fun emitError(message: String) = post(JSONObject().put("type", "error").put("message", message))
    private fun safeName(name: String) = name.replace(Regex("[^A-Za-z0-9]+"), "-").trim('-').ifBlank { "Host" }.take(24)
    private fun parseServiceName(name: String): Pair<String, String>? {
        val parts = name.split('-', limit = 3)
        if (parts.size != 3 || parts[0] != "Manna" || parts[1].length != 6) return null
        return parts[1].uppercase() to parts[2].replace('-', ' ')
    }
    companion object { private const val SERVICE_TYPE = "_manna-party._tcp." }
}
