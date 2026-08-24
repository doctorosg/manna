import CoreImage.CIFilterBuiltins
import SwiftUI

struct PartyRootView: View {
    @EnvironmentObject private var gameManager: GameManager
    @EnvironmentObject private var party: PartyManager

    var body: some View {
        VStack(spacing: 0) {
            partyHeader
            if let room = party.room {
                switch room.phase {
                case .lobby: PartyLobbyView(room: room)
                case .question, .reveal: PartyGameView(room: room)
                case .finished: PartyResultsView(room: room)
                }
            } else {
                switch party.screen {
                case .menu: PartyMenuView()
                case .setup: PartySetupView()
                case .join: PartyJoinView()
                }
            }
        }
        .onAppear { party.startNearbyDiscovery() }
        .onDisappear { party.stopNearbyDiscovery() }
        .alert("Party Mode", isPresented: Binding(get: { party.errorMessage != nil }, set: { if !$0 { party.errorMessage = nil } })) {
            Button("OK", role: .cancel) { party.errorMessage = nil }
        } message: { Text(party.errorMessage ?? "") }
    }

    private var partyHeader: some View {
        HStack {
            Button {
                if party.room != nil { party.leaveParty() }
                else if party.screen != .menu { party.showMenu() }
                else { gameManager.goHome() }
            } label: {
                Image(systemName: "chevron.left").font(.system(size: 18, weight: .semibold)).foregroundColor(.white)
            }
            Spacer()
            Label("Party Mode", systemImage: "person.3.fill")
                .font(.system(size: 18, weight: .bold, design: .rounded)).foregroundColor(.white)
            Spacer()
            Color.clear.frame(width: 22, height: 22)
        }
        .padding(.horizontal, 20).padding(.vertical, 14)
    }
}

private struct PartyMenuView: View {
    @EnvironmentObject private var party: PartyManager
    @State private var name = UserDefaults.standard.string(forKey: "manna_party_name") ?? ""

    var body: some View {
        VStack(spacing: 22) {
            Spacer()
            Image(systemName: "person.3.sequence.fill")
                .font(.system(size: 72)).foregroundColor(Color(hex: "#D4A843") ?? .yellow)
            Text("Play Together")
                .font(.system(size: 34, weight: .black, design: .rounded)).foregroundColor(.white)
            Text("Everyone sees the same questions and answers on their own phone.")
                .font(.system(size: 16, weight: .medium, design: .rounded)).foregroundColor(.white.opacity(0.65))
                .multilineTextAlignment(.center).padding(.horizontal, 36)
            TextField("Your name", text: $name)
                .textInputAutocapitalization(.words).autocorrectionDisabled()
                .padding(16).background(Color.white.opacity(0.09)).cornerRadius(12).foregroundColor(.white)
                .padding(.horizontal, 30)
            Button("Create Party Game") {
                saveName(); party.screen = .setup
            }.partyPrimary().disabled(name.trimmingCharacters(in: .whitespaces).isEmpty)
            if !party.nearbyParties.isEmpty {
                VStack(alignment: .leading, spacing: 10) {
                    Label("Nearby on this Wi-Fi", systemImage: "wifi")
                        .font(.system(size: 15, weight: .bold)).foregroundColor(.white.opacity(0.7))
                    ForEach(party.nearbyParties) { nearby in
                        Button {
                            saveName()
                            Task { await party.joinRoom(name: name.trimmingCharacters(in: .whitespaces), code: nearby.code) }
                        } label: {
                            HStack {
                                Image(systemName: "person.3.fill")
                                Text("Join \(nearby.hostName)’s Party").fontWeight(.bold)
                                Spacer()
                                Image(systemName: "chevron.right")
                            }.padding(14).background(Color.white.opacity(0.09)).cornerRadius(12)
                        }.foregroundColor(.white).disabled(name.trimmingCharacters(in: .whitespaces).isEmpty || party.isWorking)
                    }
                }.padding(.horizontal, 30)
            }
            Button("Join with a Code") {
                saveName(); party.screen = .join
            }.partySecondary().disabled(name.trimmingCharacters(in: .whitespaces).isEmpty)
            if party.hasSavedSession {
                Button("Rejoin Previous Party") { Task { await party.rejoinSavedRoom() } }
                    .font(.system(size: 15, weight: .semibold)).foregroundColor(.white.opacity(0.7))
            }
            if party.isWorking { ProgressView().tint(.white) }
            Spacer()
        }
    }

    private func saveName() { UserDefaults.standard.set(name.trimmingCharacters(in: .whitespaces), forKey: "manna_party_name") }
}

private struct PartySetupView: View {
    @EnvironmentObject private var gameManager: GameManager
    @EnvironmentObject private var party: PartyManager
    @State private var category = "All Categories"
    @State private var difficulty = DifficultyLevel.deacon
    @State private var questionCount = 10

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                Text("Create Your Game").font(.system(size: 28, weight: .black, design: .rounded)).foregroundColor(.white)
                settingCard("Category", icon: "square.grid.2x2.fill") {
                    Picker("Category", selection: $category) {
                        Text("All Categories").tag("All Categories")
                        ForEach(MannaCategory.all) { Text("\($0.emoji) \($0.name)").tag($0.name) }
                    }.tint(Color(hex: "#D4A843") ?? .yellow)
                }
                settingCard("Difficulty", icon: "graduationcap.fill") {
                    Picker("Difficulty", selection: $difficulty) {
                        ForEach(DifficultyLevel.allCases) { Text($0.name).tag($0) }
                    }.pickerStyle(.segmented)
                }
                settingCard("Questions", icon: "number.circle.fill") {
                    Picker("Questions", selection: $questionCount) {
                        Text("5").tag(5); Text("10").tag(10); Text("20").tag(20)
                    }.pickerStyle(.segmented)
                }
                Button {
                    let name = UserDefaults.standard.string(forKey: "manna_party_name") ?? "Host"
                    Task { await party.createRoom(hostName: name, category: category == "All Categories" ? nil : category, difficulty: difficulty.name, questionCount: questionCount, questionService: gameManager.questionService) }
                } label: {
                    HStack { if party.isWorking { ProgressView().tint(.black) }; Text(party.isWorking ? "Creating…" : "Create Room") }
                }.partyPrimary().disabled(party.isWorking)
            }.padding(24)
        }
    }

    private func settingCard<Content: View>(_ title: String, icon: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(title, systemImage: icon).font(.system(size: 16, weight: .bold)).foregroundColor(.white.opacity(0.75))
            content()
        }.padding(16).background(Color.white.opacity(0.06)).cornerRadius(14)
    }
}

private struct PartyJoinView: View {
    @EnvironmentObject private var party: PartyManager

    var body: some View {
        VStack(spacing: 24) {
            Spacer()
            Text("Enter Party Code").font(.system(size: 30, weight: .black, design: .rounded)).foregroundColor(.white)
            TextField("ABC123", text: $party.joinCode)
                .textInputAutocapitalization(.characters).autocorrectionDisabled()
                .font(.system(size: 34, weight: .black, design: .monospaced)).tracking(7).multilineTextAlignment(.center)
                .padding(18).background(Color.white.opacity(0.09)).cornerRadius(14).foregroundColor(.white)
                .padding(.horizontal, 34).onChange(of: party.joinCode) { _, value in party.joinCode = String(value.uppercased().filter { $0.isLetter || $0.isNumber }.prefix(6)) }
            Button {
                let name = UserDefaults.standard.string(forKey: "manna_party_name") ?? "Player"
                Task { await party.joinRoom(name: name, code: party.joinCode) }
            } label: {
                HStack { if party.isWorking { ProgressView().tint(.black) }; Text(party.isWorking ? "Joining…" : "Join Party") }
            }.partyPrimary().disabled(party.joinCode.count != 6 || party.isWorking)
            Spacer()
        }
    }
}

private struct PartyLobbyView: View {
    @EnvironmentObject private var party: PartyManager
    let room: PartyRoomSnapshot

    var body: some View {
        ScrollView {
            VStack(spacing: 18) {
                Text(room.isHost ? "Your Party Code" : "Waiting for the Host")
                    .font(.system(size: 20, weight: .bold, design: .rounded)).foregroundColor(.white.opacity(0.7))
                Text(room.code).font(.system(size: 44, weight: .black, design: .monospaced)).tracking(8).foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                if let qr = qrImage(room.code) { Image(uiImage: qr).interpolation(.none).resizable().scaledToFit().frame(width: 150, height: 150).background(.white).cornerRadius(12) }
                Text("\(room.settings.category) · \(room.settings.difficulty) · \(room.settings.questionCount) questions")
                    .font(.system(size: 13, weight: .semibold)).foregroundColor(.white.opacity(0.55)).multilineTextAlignment(.center)
                VStack(spacing: 8) {
                    ForEach(room.players) { player in
                        HStack { Image(systemName: player.isHost ? "crown.fill" : "person.fill"); Text(player.name); Spacer(); if player.id == room.myPlayerId { Text("YOU") } }
                            .font(.system(size: 15, weight: .bold)).foregroundColor(player.isHost ? (Color(hex: "#D4A843") ?? .yellow) : .white)
                            .padding(14).background(Color.white.opacity(0.06)).cornerRadius(11)
                    }
                }
                Text("\(room.players.count) of 12 players joined").font(.system(size: 13)).foregroundColor(.white.opacity(0.5))
                if room.isHost {
                    Button("Start Game") { Task { await party.startGame() } }.partyPrimary().disabled(party.isWorking || room.players.count < 2)
                    if room.players.count < 2 {
                        Text("Waiting for another player to join")
                            .font(.system(size: 13, weight: .semibold)).foregroundColor(.white.opacity(0.55))
                    }
                } else {
                    ProgressView("The host will start the game").tint(.white).foregroundColor(.white.opacity(0.65)).padding(.top, 10)
                }
            }.padding(24)
        }
    }

    private func qrImage(_ code: String) -> UIImage? {
        let filter = CIFilter.qrCodeGenerator(); filter.message = Data("manna://party/\(code)".utf8); filter.correctionLevel = "M"
        guard let output = filter.outputImage else { return nil }
        return UIImage(ciImage: output.transformed(by: CGAffineTransform(scaleX: 10, y: 10)))
    }
}

private struct PartyGameView: View {
    @EnvironmentObject private var gameManager: GameManager
    @EnvironmentObject private var party: PartyManager
    let room: PartyRoomSnapshot

    private var question: MannaQuestion? { room.questionId.flatMap(gameManager.questionService.question(withId:)) }

    var body: some View {
        ScrollView {
            VStack(spacing: 14) {
                HStack {
                    Text("Question \(room.questionNumber)/\(room.settings.questionCount)")
                    Spacer(); Text("\(room.answeredCount)/\(room.players.count) answered")
                }.font(.system(size: 13, weight: .bold)).foregroundColor(.white.opacity(0.55))
                Text("ROOM \(room.code)").font(.system(size: 11, weight: .bold, design: .monospaced)).tracking(2).foregroundColor(.white.opacity(0.38))
                if let question {
                    Text(question.category.uppercased()).font(.system(size: 12, weight: .black)).tracking(1).foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                    Text(question.question).font(.system(size: 22, weight: .bold, design: .rounded)).foregroundColor(.white).multilineTextAlignment(.center).padding(.vertical, 8)
                    ForEach(Array(question.options.enumerated()), id: \.offset) { index, option in
                        Button { if room.phase == .question { Task { await party.submitAnswer(index) } } } label: {
                            HStack {
                                Text(String(UnicodeScalar(65 + index)!)).font(.system(size: 14, weight: .black)).frame(width: 30, height: 30).background(answerColor(index).opacity(0.22)).clipShape(Circle())
                                Text(option).font(.system(size: 16, weight: .semibold)).multilineTextAlignment(.leading)
                                Spacer()
                                if room.myAnswer == index { Image(systemName: "checkmark.circle.fill") }
                            }.foregroundColor(.white).padding(14).background(answerColor(index).opacity(room.phase == .reveal || room.myAnswer == index ? 0.22 : 0.07)).cornerRadius(12)
                        }.disabled(room.phase == .reveal)
                    }
                    if room.phase == .reveal {
                        VStack(alignment: .leading, spacing: 8) {
                            Text(room.myAnswer == question.correctIndex ? "Correct!" : "Correct answer: \(question.correct)")
                                .font(.system(size: 18, weight: .bold)).foregroundColor(room.myAnswer == question.correctIndex ? .green : .red)
                            if !question.explanation.isEmpty { Text(question.explanation).font(.system(size: 14)).foregroundColor(.white.opacity(0.65)) }
                        }.frame(maxWidth: .infinity, alignment: .leading).padding(14).background(Color.white.opacity(0.06)).cornerRadius(12)
                        PartyRoundResultsView(players: room.players)
                    } else if room.myAnswer != nil {
                        Label("Answer locked in", systemImage: "checkmark.seal.fill").font(.system(size: 15, weight: .bold)).foregroundColor(.green).padding(.top, 6)
                    }
                } else {
                    Text("This question is not available on this version of Manna.").foregroundColor(.red)
                }
                leaderboard
                if room.isHost {
                    if room.phase == .question { Button("Reveal Answer") { Task { await party.revealAnswer() } }.partyPrimary() }
                    else { Button(room.questionNumber == room.settings.questionCount ? "Finish Game" : "Next Question") { Task { await party.nextQuestion() } }.partyPrimary() }
                } else {
                    Text(room.phase == .question ? "Waiting for the host to reveal the answer" : "Waiting for the next question")
                        .font(.system(size: 13, weight: .medium)).foregroundColor(.white.opacity(0.5)).padding(.top, 8)
                }
            }.padding(20)
        }
    }

    private func answerColor(_ index: Int) -> Color {
        guard let question else { return .white }
        if room.phase == .reveal { return index == question.correctIndex ? .green : (room.myAnswer == index ? .red : .white) }
        return room.myAnswer == index ? (Color(hex: "#D4A843") ?? .yellow) : .white
    }

    private var leaderboard: some View {
        VStack(spacing: 6) {
            ForEach(Array(room.players.prefix(5).enumerated()), id: \.element.id) { position, player in
                HStack { Text("\(position + 1)").frame(width: 22); Text(player.name); Spacer(); Text("\(player.score)") }
                    .font(.system(size: 14, weight: .bold)).foregroundColor(player.id == room.myPlayerId ? (Color(hex: "#D4A843") ?? .yellow) : .white.opacity(0.75))
            }
        }.padding(12).background(Color.white.opacity(0.05)).cornerRadius(12).padding(.top, 6)
    }
}

private struct PartyRoundResultsView: View {
    let players: [PartyPlayer]

    private var correct: [PartyPlayer] { players.filter { $0.wasCorrect == true } }
    private var incorrect: [PartyPlayer] { players.filter { $0.hasAnswered && $0.wasCorrect == false } }
    private var unanswered: [PartyPlayer] { players.filter { !$0.hasAnswered } }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("This Round")
                .font(.system(size: 17, weight: .black, design: .rounded))
                .foregroundColor(.white)
            resultGroup(title: "Correct", icon: "checkmark.circle.fill", color: .green, players: correct)
            if !incorrect.isEmpty { resultGroup(title: "Incorrect", icon: "xmark.circle.fill", color: .red, players: incorrect) }
            if !unanswered.isEmpty { resultGroup(title: "No Answer", icon: "minus.circle.fill", color: .orange, players: unanswered) }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(14)
        .background(Color.white.opacity(0.06))
        .cornerRadius(12)
    }

    private func resultGroup(title: String, icon: String, color: Color, players: [PartyPlayer]) -> some View {
        VStack(alignment: .leading, spacing: 5) {
            Label("\(title) · \(players.count)", systemImage: icon)
                .font(.system(size: 14, weight: .bold)).foregroundColor(color)
            Text(players.isEmpty ? "Nobody" : players.map(\.name).joined(separator: ", "))
                .font(.system(size: 14, weight: .semibold)).foregroundColor(.white.opacity(0.78))
        }
    }
}

private struct PartyResultsView: View {
    @EnvironmentObject private var party: PartyManager
    let room: PartyRoomSnapshot

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                Text("🏆").font(.system(size: 72))
                Text("Party Complete").font(.system(size: 32, weight: .black, design: .rounded)).foregroundColor(.white)
                ForEach(Array(room.players.enumerated()), id: \.element.id) { index, player in
                    HStack {
                        Text(index == 0 ? "👑" : "\(index + 1)").frame(width: 40)
                        Text(player.name).font(.system(size: 18, weight: .bold)); Spacer()
                        Text("\(player.score)/\(room.settings.questionCount)").font(.system(size: 18, weight: .black))
                    }.foregroundColor(index == 0 ? (Color(hex: "#D4A843") ?? .yellow) : .white).padding(16).background(Color.white.opacity(0.07)).cornerRadius(13)
                }
                Button("Done") { party.leaveParty() }.partyPrimary().padding(.top, 12)
            }.padding(24)
        }
    }
}

private extension View {
    func partyPrimary() -> some View {
        self.font(.system(size: 17, weight: .bold, design: .rounded)).foregroundColor(.black)
            .frame(maxWidth: .infinity).padding(.vertical, 16).background(Color(hex: "#D4A843") ?? .yellow).cornerRadius(14).padding(.horizontal, 30)
    }
    func partySecondary() -> some View {
        self.font(.system(size: 17, weight: .bold, design: .rounded)).foregroundColor(Color(hex: "#D4A843") ?? .yellow)
            .frame(maxWidth: .infinity).padding(.vertical, 15).background(Color.white.opacity(0.08)).cornerRadius(14).padding(.horizontal, 30)
    }
}
