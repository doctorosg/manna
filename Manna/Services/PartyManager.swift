import Combine
import Foundation
import Network

enum PartyPhase: String, Codable { case lobby, question, reveal, finished }

struct PartySettings: Codable {
    let category: String
    let difficulty: String
    let ageGroup: String?
    let questionCount: Int

    var selectionSummary: String {
        if let ageGroup, let group = ChildAgeGroup(rawValue: ageGroup) {
            return "Children · \(group.title) · \(questionCount) questions"
        }
        return "\(category) · \(difficulty) · \(questionCount) questions"
    }
}

struct PartyPlayer: Codable, Identifiable {
    let id: String
    let name: String
    let score: Int
    let hasAnswered: Bool
    let isHost: Bool
    let wasCorrect: Bool?
}

struct PartyRoomSnapshot: Codable {
    let code: String
    let phase: PartyPhase
    let settings: PartySettings
    let currentIndex: Int
    let questionId: String?
    let questionNumber: Int
    let players: [PartyPlayer]
    let answeredCount: Int
    let myPlayerId: String
    let myAnswer: Int?
    let isHost: Bool
    let version: Int
}

private struct PartyQuestionPayload: Codable {
    let id: String
    let correctIndex: Int
}

private struct PartyWireMessage: Codable {
    let type: String
    var code: String? = nil
    var name: String? = nil
    var token: String? = nil
    var action: String? = nil
    var answerIndex: Int? = nil
    var room: PartyRoomSnapshot? = nil
    var message: String? = nil
}

private struct LocalPartyPlayer {
    let id: String
    let token: String
    let name: String
    var score: Int
    var answers: [Int: Int]
}

private struct LocalPartyRoom {
    let code: String
    let hostPlayerId: String
    let settings: PartySettings
    let questions: [PartyQuestionPayload]
    var phase: PartyPhase
    var currentIndex: Int
    var players: [LocalPartyPlayer]
    var version: Int
}

private final class PartyPeer: @unchecked Sendable {
    let id = UUID()
    let connection: NWConnection
    var receiveBuffer = Data()
    var playerId: String?

    init(connection: NWConnection) { self.connection = connection }
}

enum PartyScreen: Equatable { case menu, setup, join }

struct NearbyParty: Identifiable, Equatable {
    let code: String
    let hostName: String
    var id: String { code }
}

@MainActor
final class PartyManager: ObservableObject {
    @Published var screen: PartyScreen = .menu
    @Published var room: PartyRoomSnapshot?
    @Published var isWorking = false
    @Published var errorMessage: String?
    @Published var joinCode = ""
    @Published private(set) var nearbyParties: [NearbyParty] = []

    private static let serviceType = "_manna-party._tcp"
    private static let maxPlayers = 12

    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()
    private let networkQueue = DispatchQueue(label: "com.oddcurrent.manna.party-local")
    private var localRoom: LocalPartyRoom?
    private var token: String?
    private var nearbyBrowser: NWBrowser?
    private var nearbyEndpoints: [String: NWEndpoint] = [:]
    private var hostListener: NWListener?
    private var hostPeers: [UUID: PartyPeer] = [:]
    private var guestPeer: PartyPeer?
    private var pendingJoinName = ""
    private var pendingJoinCode = ""
    private var shuttingDown = false

    var hasSavedSession: Bool { false }

    func showMenu() {
        stopSession()
        room = nil
        screen = .menu
        errorMessage = nil
    }

    func openJoin(code: String) {
        joinCode = String(code.uppercased().filter { $0.isLetter || $0.isNumber }.prefix(6))
        room = nil
        screen = .join
    }

    func createRoom(hostName: String, category: String?, difficulty: String, ageGroup: ChildAgeGroup? = nil, questionCount: Int, questionService: QuestionService) async {
        let questions = if let ageGroup {
            questionService.partyQuestions(ageGroup: ageGroup, count: questionCount)
        } else {
            questionService.partyQuestions(category: category, difficulty: difficulty, count: questionCount)
        }
        guard questions.count == questionCount else {
            errorMessage = "There are not enough matching questions. Try All Categories or another difficulty."
            return
        }
        stopSession()
        isWorking = true
        errorMessage = nil
        let host = LocalPartyPlayer(id: UUID().uuidString, token: UUID().uuidString,
                                    name: Self.cleanName(hostName, fallback: "Host"), score: 0, answers: [:])
        let code = Self.randomCode()
        localRoom = LocalPartyRoom(
            code: code, hostPlayerId: host.id,
            settings: PartySettings(
                category: ageGroup == nil ? (category ?? "All Categories") : "Children",
                difficulty: ageGroup?.title ?? difficulty,
                ageGroup: ageGroup?.rawValue,
                questionCount: questionCount
            ),
            questions: questions.map { PartyQuestionPayload(id: $0.id, correctIndex: $0.correctIndex) },
            phase: .lobby, currentIndex: -1, players: [host], version: 1
        )
        token = host.token
        publishHostSnapshot()
        startHostListener(code: code, hostName: host.name)
        isWorking = false
    }

    func joinRoom(name: String, code: String) async {
        let normalized = String(code.uppercased().filter { $0.isLetter || $0.isNumber }.prefix(6))
        guard normalized.count == 6 else {
            errorMessage = "Enter the six-character party code."
            return
        }
        guard let endpoint = nearbyEndpoints[normalized] else {
            errorMessage = "Party not found on this Wi-Fi network. Make sure the host is waiting in the lobby and both phones are on the same Wi-Fi."
            return
        }
        stopSession(keepDiscovery: true)
        isWorking = true
        errorMessage = nil
        pendingJoinName = Self.cleanName(name, fallback: "Player")
        pendingJoinCode = normalized
        let connection = NWConnection(to: endpoint, using: .tcp)
        let peer = PartyPeer(connection: connection)
        guestPeer = peer
        connection.stateUpdateHandler = { [weak self, weak peer] state in
            guard let self, let peer else { return }
            switch state {
            case .ready:
                Task { @MainActor [weak self] in self?.sendGuestJoin() }
                self.receiveGuest(peer)
            case .failed(let error):
                Task { @MainActor [weak self] in self?.guestFailed("Unable to join the nearby party: \(error.localizedDescription)") }
            case .cancelled:
                Task { @MainActor [weak self] in self?.guestDisconnected() }
            default: break
            }
        }
        connection.start(queue: networkQueue)
    }

    func rejoinSavedRoom() async {
        errorMessage = "Nearby parties are temporary. Ask the host to create a new room."
    }

    func startGame() async {
        mutateHostRoom { room in
            guard room.phase == .lobby, room.players.count >= 2 else {
                throw PartyClientError(message: "At least two players are required.")
            }
            room.phase = .question
            room.currentIndex = 0
        }
        if localRoom?.phase == .question { stopAcceptingPlayers() }
    }

    func revealAnswer() async {
        mutateHostRoom { room in
            guard room.phase == .question else { throw PartyClientError(message: "There is no question to reveal.") }
            let correctIndex = room.questions[room.currentIndex].correctIndex
            for index in room.players.indices where room.players[index].answers[room.currentIndex] == correctIndex {
                room.players[index].score += 1
            }
            room.phase = .reveal
        }
    }

    func nextQuestion() async {
        mutateHostRoom { room in
            guard room.phase == .reveal else { throw PartyClientError(message: "Reveal the answer first.") }
            if room.currentIndex + 1 >= room.questions.count { room.phase = .finished }
            else { room.currentIndex += 1; room.phase = .question }
        }
    }

    func submitAnswer(_ index: Int) async {
        guard (0...5).contains(index) else { return }
        if localRoom != nil {
            guard let hostToken = token else { return }
            applyHostAction(token: hostToken, action: "answer", answerIndex: index, peer: nil)
        } else {
            sendGuest(PartyWireMessage(type: "action", token: token, action: "answer", answerIndex: index))
        }
    }

    func leaveParty() { showMenu() }

    func startNearbyDiscovery() {
        guard nearbyBrowser == nil else { return }
        let browser = NWBrowser(for: .bonjour(type: Self.serviceType, domain: nil), using: .tcp)
        browser.browseResultsChangedHandler = { [weak self] results, _ in
            guard let self else { return }
            var endpoints: [String: NWEndpoint] = [:]
            var parties: [NearbyParty] = []
            for result in results {
                guard case let .service(name, _, _, _) = result.endpoint,
                      let party = Self.parseNearbyServiceName(name) else { continue }
                endpoints[party.code] = result.endpoint
                parties.append(party)
            }
            let unique = Dictionary(grouping: parties, by: \.code).compactMap { $0.value.first }
                .sorted { $0.hostName.localizedCaseInsensitiveCompare($1.hostName) == .orderedAscending }
            Task { @MainActor [weak self] in
                self?.nearbyEndpoints = endpoints
                self?.nearbyParties = unique.filter { $0.code != self?.localRoom?.code }
            }
        }
        browser.stateUpdateHandler = { [weak self] state in
            if case .failed = state {
                Task { @MainActor [weak self] in
                    self?.nearbyBrowser?.cancel(); self?.nearbyBrowser = nil
                    self?.nearbyEndpoints = [:]; self?.nearbyParties = []
                }
            }
        }
        nearbyBrowser = browser
        browser.start(queue: networkQueue)
    }

    func stopNearbyDiscovery() {
        nearbyBrowser?.cancel(); nearbyBrowser = nil
        nearbyEndpoints = [:]; nearbyParties = []
    }

    private func mutateHostRoom(_ mutation: (inout LocalPartyRoom) throws -> Void) {
        guard var state = localRoom else { return }
        isWorking = true
        defer { isWorking = false }
        do {
            try mutation(&state)
            state.version += 1
            localRoom = state
            broadcastSnapshots()
        } catch { errorMessage = error.localizedDescription }
    }

    private func applyHostAction(token: String, action: String, answerIndex: Int?, peer: PartyPeer?) {
        guard var state = localRoom,
              let playerIndex = state.players.firstIndex(where: { $0.token == token }),
              peer == nil || peer?.playerId == state.players[playerIndex].id else {
            if let peer { sendHost(PartyWireMessage(type: "error", message: "Your party session has expired."), to: peer) }
            return
        }
        guard action == "answer", state.phase == .question, let answerIndex, (0...5).contains(answerIndex) else {
            if let peer { sendHost(PartyWireMessage(type: "error", message: "Answers are not open right now."), to: peer) }
            return
        }
        state.players[playerIndex].answers[state.currentIndex] = answerIndex
        state.version += 1
        localRoom = state
        broadcastSnapshots()
    }

    private func startHostListener(code: String, hostName: String) {
        do {
            let listener = try NWListener(using: .tcp, on: .any)
            listener.service = NWListener.Service(name: Self.nearbyServiceName(code: code, hostName: hostName), type: Self.serviceType)
            listener.newConnectionHandler = { [weak self] connection in
                Task { @MainActor [weak self] in self?.acceptHostConnection(connection) }
            }
            listener.stateUpdateHandler = { [weak self] state in
                if case let .failed(error) = state {
                    Task { @MainActor [weak self] in
                        self?.errorMessage = "Unable to host on this Wi-Fi: \(error.localizedDescription)"
                        self?.hostListener = nil
                    }
                }
            }
            hostListener = listener
            listener.start(queue: networkQueue)
        } catch { errorMessage = "Unable to host on this Wi-Fi: \(error.localizedDescription)" }
    }

    private func acceptHostConnection(_ connection: NWConnection) {
        guard localRoom?.phase == .lobby else { connection.cancel(); return }
        let peer = PartyPeer(connection: connection)
        hostPeers[peer.id] = peer
        connection.stateUpdateHandler = { [weak self, weak peer] state in
            guard let self, let peer else { return }
            switch state {
            case .ready: self.receiveHost(peer)
            case .failed, .cancelled: Task { @MainActor [weak self] in self?.hostPeerDisconnected(peer) }
            default: break
            }
        }
        connection.start(queue: networkQueue)
    }

    private nonisolated func receiveHost(_ peer: PartyPeer) {
        peer.connection.receive(minimumIncompleteLength: 1, maximumLength: 64 * 1024) { [weak self, weak peer] data, _, complete, error in
            guard let self, let peer else { return }
            if let data, !data.isEmpty {
                peer.receiveBuffer.append(data)
                for message in self.consumeMessages(from: &peer.receiveBuffer) {
                    Task { @MainActor [weak self] in self?.handleHostMessage(message, from: peer) }
                }
            }
            if error != nil || complete { Task { @MainActor [weak self] in self?.hostPeerDisconnected(peer) } }
            else { self.receiveHost(peer) }
        }
    }

    private func handleHostMessage(_ message: PartyWireMessage, from peer: PartyPeer) {
        if peer.playerId == nil {
            guard message.type == "join", message.code == localRoom?.code, let requestedName = message.name else {
                sendHost(PartyWireMessage(type: "error", message: "Incorrect nearby game code."), to: peer)
                peer.connection.cancel(); return
            }
            guard var state = localRoom, state.phase == .lobby else {
                sendHost(PartyWireMessage(type: "error", message: "This game has already started."), to: peer)
                peer.connection.cancel(); return
            }
            guard state.players.count < Self.maxPlayers else {
                sendHost(PartyWireMessage(type: "error", message: "This party is full."), to: peer)
                peer.connection.cancel(); return
            }
            let player = LocalPartyPlayer(id: UUID().uuidString, token: UUID().uuidString,
                                          name: Self.cleanName(requestedName, fallback: "Player"), score: 0, answers: [:])
            state.players.append(player); state.version += 1; localRoom = state; peer.playerId = player.id
            sendHost(PartyWireMessage(type: "joined", token: player.token, room: snapshot(for: player.id)), to: peer)
            broadcastSnapshots(excluding: peer.id)
            return
        }
        if message.type == "action", let token = message.token, let action = message.action {
            applyHostAction(token: token, action: action, answerIndex: message.answerIndex, peer: peer)
        }
    }

    private func hostPeerDisconnected(_ peer: PartyPeer) {
        guard hostPeers.removeValue(forKey: peer.id) != nil else { return }
        peer.connection.cancel()
        guard var state = localRoom, state.phase == .lobby, let playerId = peer.playerId else { return }
        state.players.removeAll { $0.id == playerId }; state.version += 1; localRoom = state
        broadcastSnapshots()
    }

    private func sendHost(_ message: PartyWireMessage, to peer: PartyPeer) { send(message, on: peer.connection) }

    private func sendGuestJoin() {
        sendGuest(PartyWireMessage(type: "join", code: pendingJoinCode, name: pendingJoinName))
    }

    private func sendGuest(_ message: PartyWireMessage) {
        guard let guestPeer else { errorMessage = "The host is no longer connected."; return }
        send(message, on: guestPeer.connection)
    }

    private nonisolated func receiveGuest(_ peer: PartyPeer) {
        peer.connection.receive(minimumIncompleteLength: 1, maximumLength: 64 * 1024) { [weak self, weak peer] data, _, complete, error in
            guard let self, let peer else { return }
            if let data, !data.isEmpty {
                peer.receiveBuffer.append(data)
                for message in self.consumeMessages(from: &peer.receiveBuffer) {
                    Task { @MainActor [weak self] in self?.handleGuestMessage(message) }
                }
            }
            if error != nil || complete { Task { @MainActor [weak self] in self?.guestDisconnected() } }
            else { self.receiveGuest(peer) }
        }
    }

    private func handleGuestMessage(_ message: PartyWireMessage) {
        switch message.type {
        case "joined":
            guard let joinedRoom = message.room, let joinedToken = message.token else { return }
            token = joinedToken; room = joinedRoom; isWorking = false
        case "snapshot":
            guard let latest = message.room else { return }
            if latest.version >= (room?.version ?? -1) { room = latest }
        case "error":
            isWorking = false; errorMessage = message.message ?? "Party connection failed."
        default: break
        }
    }

    private func guestFailed(_ message: String) {
        guard !shuttingDown else { return }
        isWorking = false; errorMessage = message
        guestPeer?.connection.cancel(); guestPeer = nil
    }

    private func guestDisconnected() {
        guard !shuttingDown, guestPeer != nil else { return }
        guestPeer = nil; isWorking = false
        if room != nil {
            room = nil; screen = .menu
            errorMessage = "The host ended the nearby party or left the Wi-Fi network."
        }
    }

    private func publishHostSnapshot() {
        guard let hostId = localRoom?.hostPlayerId else { return }
        room = snapshot(for: hostId)
    }

    private func broadcastSnapshots(excluding excludedPeerID: UUID? = nil) {
        publishHostSnapshot()
        for peer in hostPeers.values where peer.id != excludedPeerID {
            guard let playerId = peer.playerId, let snapshot = snapshot(for: playerId) else { continue }
            sendHost(PartyWireMessage(type: "snapshot", room: snapshot), to: peer)
        }
    }

    private func snapshot(for viewerId: String) -> PartyRoomSnapshot? {
        guard let state = localRoom, let viewer = state.players.first(where: { $0.id == viewerId }) else { return nil }
        let answerKey = state.currentIndex
        let revealResults = state.phase == .reveal || state.phase == .finished
        let correctIndex = state.questions.indices.contains(state.currentIndex) ? state.questions[state.currentIndex].correctIndex : nil
        let players = state.players.map { player in
            PartyPlayer(id: player.id, name: player.name, score: player.score,
                        hasAnswered: player.answers[answerKey] != nil, isHost: player.id == state.hostPlayerId,
                        wasCorrect: revealResults && correctIndex != nil ? player.answers[answerKey] == correctIndex : nil)
        }.sorted { $0.score != $1.score ? $0.score > $1.score : $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
        return PartyRoomSnapshot(
            code: state.code, phase: state.phase, settings: state.settings, currentIndex: state.currentIndex,
            questionId: state.questions.indices.contains(state.currentIndex) ? state.questions[state.currentIndex].id : nil,
            questionNumber: state.currentIndex + 1, players: players,
            answeredCount: state.players.filter { $0.answers[answerKey] != nil }.count,
            myPlayerId: viewer.id, myAnswer: viewer.answers[answerKey], isHost: viewer.id == state.hostPlayerId,
            version: state.version
        )
    }

    private func stopAcceptingPlayers() { hostListener?.cancel(); hostListener = nil }

    private func stopSession(keepDiscovery: Bool = false) {
        shuttingDown = true
        hostListener?.cancel(); hostListener = nil
        for peer in hostPeers.values { peer.connection.cancel() }
        hostPeers.removeAll()
        guestPeer?.connection.cancel(); guestPeer = nil
        localRoom = nil; token = nil
        pendingJoinName = ""; pendingJoinCode = ""
        if !keepDiscovery { startNearbyDiscovery() }
        shuttingDown = false
    }

    private nonisolated func send(_ message: PartyWireMessage, on connection: NWConnection) {
        guard var data = try? encoder.encode(message) else { return }
        data.append(0x0A)
        connection.send(content: data, completion: .contentProcessed { _ in })
    }

    private nonisolated func consumeMessages(from buffer: inout Data) -> [PartyWireMessage] {
        var messages: [PartyWireMessage] = []
        let newline = Data([0x0A])
        while let range = buffer.range(of: newline) {
            let line = buffer.subdata(in: buffer.startIndex..<range.lowerBound)
            buffer.removeSubrange(buffer.startIndex...range.lowerBound)
            if let message = try? decoder.decode(PartyWireMessage.self, from: line) { messages.append(message) }
        }
        return messages
    }

    nonisolated private static func randomCode() -> String {
        let alphabet = Array("ABCDEFGHJKLMNPQRSTUVWXYZ23456789")
        return String((0..<6).compactMap { _ in alphabet.randomElement() })
    }

    nonisolated private static func cleanName(_ value: String, fallback: String) -> String {
        let collapsed = value.trimmingCharacters(in: .whitespacesAndNewlines).split(whereSeparator: \.isWhitespace).joined(separator: " ")
        return String((collapsed.isEmpty ? fallback : collapsed).prefix(24))
    }

    nonisolated private static func nearbyServiceName(code: String, hostName: String) -> String {
        let safeHost = hostName.replacingOccurrences(of: "-", with: " ").trimmingCharacters(in: .whitespacesAndNewlines)
        return "Manna-\(code)-\(String(safeHost.prefix(36)))"
    }

    nonisolated private static func parseNearbyServiceName(_ name: String) -> NearbyParty? {
        guard name.hasPrefix("Manna-"), name.count >= 13 else { return nil }
        let codeStart = name.index(name.startIndex, offsetBy: 6)
        let codeEnd = name.index(codeStart, offsetBy: 6)
        let code = String(name[codeStart..<codeEnd]).uppercased()
        guard code.allSatisfy({ $0.isLetter || $0.isNumber }) else { return nil }
        var hostName = "Nearby Host"
        if codeEnd < name.endIndex, name[codeEnd] == "-" {
            let value = String(name[name.index(after: codeEnd)...]).trimmingCharacters(in: .whitespacesAndNewlines)
            if !value.isEmpty { hostName = value }
        }
        return NearbyParty(code: code, hostName: hostName)
    }
}

private struct PartyClientError: LocalizedError {
    let message: String
    var errorDescription: String? { message }
}
