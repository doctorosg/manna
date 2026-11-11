import CoreImage.CIFilterBuiltins
import SwiftUI

struct PartyRootView: View {
    @EnvironmentObject private var gameManager: GameManager
    @EnvironmentObject private var party: PartyManager
    @EnvironmentObject private var languageManager: LanguageManager
    @State private var showingTVGuide = false
    @State private var tvModeEnabled = false

    var body: some View {
        Group {
            if tvModeEnabled, let room = party.room, room.isHost {
                PartyTVDisplayView(room: room, exitTVMode: { tvModeEnabled = false })
            } else {
                VStack(spacing: 0) {
                    partyHeader
                    if let room = party.room {
                        switch room.phase {
                        case .lobby: PartyLobbyView(room: room, openTV: { showingTVGuide = true })
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
            }
        }
        .onAppear { party.startNearbyDiscovery() }
        .onDisappear {
            party.stopNearbyDiscovery()
            UIApplication.shared.isIdleTimerDisabled = false
        }
        .onChange(of: tvModeEnabled) { _, enabled in
            UIApplication.shared.isIdleTimerDisabled = enabled
        }
        .sheet(isPresented: $showingTVGuide) {
            PartyTVConnectionGuide {
                showingTVGuide = false
                tvModeEnabled = true
            }
            .presentationDetents([.large])
        }
        .background {
            MannaText("Party Mode").hidden()
            MannaText("OK").hidden()
        }
        .alert(languageManager.interfaceString("Party Mode"), isPresented: Binding(get: { party.errorMessage != nil }, set: { if !$0 { party.errorMessage = nil } })) {
            Button(role: .cancel, action: { party.errorMessage = nil }) { MannaText("OK") }
        } message: { MannaText(party.errorMessage ?? "") }
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
            MannaLabel("Party Mode", systemImage: "person.3.fill")
                .font(.system(size: 18, weight: .bold, design: .rounded)).foregroundColor(.white)
            Spacer()
            if party.room?.isHost == true {
                Button { showingTVGuide = true } label: {
                    Image(systemName: "tv.and.mediabox")
                        .font(.system(size: 18, weight: .semibold)).foregroundColor(.white)
                }
                .mannaAccessibilityLabel("Play on a TV")
            } else {
                Color.clear.frame(width: 22, height: 22)
            }
        }
        .padding(.horizontal, 20).padding(.vertical, 14)
    }
}

private struct PartyTVConnectionGuide: View {
    let start: () -> Void

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    Image(systemName: "tv.and.mediabox.fill")
                        .font(.system(size: 58)).foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                        .frame(maxWidth: .infinity)
                    MannaText("Set Up TV Display")
                        .font(.system(size: 29, weight: .black, design: .rounded)).foregroundColor(.white)
                        .frame(maxWidth: .infinity, alignment: .center)
                    MannaText("Mirror the host phone to the TV first. Players keep answering on their own phones.")
                        .foregroundColor(.white.opacity(0.72)).multilineTextAlignment(.center)
                    setupStep(1, "Use the same Wi-Fi", "Connect the host phone and smart TV to the same Wi-Fi network.", "wifi")
                    setupStep(2, "Connect the host phone", "Choose one connection method below. If the TV displays a code or asks permission, approve it on the phone or TV.", "iphone.gen3")
                    connectionRow("iPhone or iPad · AirPlay", "Open Control Center, tap Screen Mirroring, then select the TV. Enter the AirPlay code shown on the TV if asked.", "airplayvideo")
                    connectionRow("Samsung phone · Smart View", "Swipe down twice for Quick Settings, tap Smart View, select the TV, then tap Start now.", "dot.radiowaves.left.and.right")
                    connectionRow("Android · Chromecast or Google TV", "Open Quick Settings, tap Cast or Screen Cast, then select the TV. Some phones use Google Home → TV → Cast my screen.", "tv")
                    connectionRow("Any TV · HDMI", "Connect a compatible USB-C or Lightning HDMI adapter and cable, then change the TV input to that HDMI port. This is the universal fallback.", "cable.connector")
                    setupStep(3, "Open the game display", "After the TV shows this phone, tap the button below. Turn the host phone sideways for the full-screen question and scoreboard layout.", "rectangle.landscape.rotate")
                    Button(action: start) { MannaText("TV IS CONNECTED — OPEN DISPLAY") }.partyPrimary().padding(.top, 6)
                }
                .padding(24)
            }
            .background(Color(red: 0.06, green: 0.07, blue: 0.13).ignoresSafeArea())
            .toolbar { ToolbarItem(placement: .topBarTrailing) { Button(action: startGuideDismiss) { MannaText("Close") } } }
        }
    }

    @Environment(\.dismiss) private var dismiss
    private func startGuideDismiss() { dismiss() }

    private func connectionRow(_ title: String, _ detail: String, _ icon: String) -> some View {
        HStack(alignment: .top, spacing: 14) {
            Image(systemName: icon).font(.system(size: 24)).foregroundColor(Color(hex: "#D4A843") ?? .yellow).frame(width: 34)
            VStack(alignment: .leading, spacing: 4) {
                MannaText(title).font(.system(size: 16, weight: .bold)).foregroundColor(.white)
                MannaText(detail).font(.system(size: 14)).foregroundColor(.white.opacity(0.65))
            }
        }
        .padding(15).background(Color.white.opacity(0.06)).cornerRadius(13)
    }

    private func setupStep(_ number: Int, _ title: String, _ detail: String, _ icon: String) -> some View {
        HStack(alignment: .top, spacing: 13) {
            Text("\(number)")
                .font(.system(size: 16, weight: .black)).foregroundColor(.black)
                .frame(width: 30, height: 30).background(Color(hex: "#D4A843") ?? .yellow).clipShape(Circle())
            VStack(alignment: .leading, spacing: 4) {
                MannaLabel(title, systemImage: icon).font(.system(size: 16, weight: .bold)).foregroundColor(.white)
                MannaText(detail).font(.system(size: 14)).foregroundColor(.white.opacity(0.68))
            }
        }
    }
}

private struct PartyTVDisplayView: View {
    @EnvironmentObject private var gameManager: GameManager
    @EnvironmentObject private var party: PartyManager
    let room: PartyRoomSnapshot
    let exitTVMode: () -> Void

    private var question: MannaQuestion? { room.questionId.flatMap(gameManager.questionService.question(withId:)) }

    var body: some View {
        ZStack {
            Color(red: 0.035, green: 0.045, blue: 0.10).ignoresSafeArea()
            VStack(spacing: 14) {
                HStack {
                    MannaText("MANNA PARTY").font(.system(size: 18, weight: .black, design: .rounded)).tracking(2).foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                    Spacer()
                    HStack(spacing: 5) {
                        MannaText("ROOM")
                        Text(room.code)
                    }.font(.system(size: 15, weight: .bold, design: .monospaced)).foregroundColor(.white.opacity(0.55))
                    Button(action: exitTVMode) { Image(systemName: "xmark.circle.fill").font(.system(size: 25)).foregroundColor(.white.opacity(0.7)) }
                        .padding(.leading, 12).mannaAccessibilityLabel("Close TV Display")
                }
                switch room.phase {
                case .lobby: lobby
                case .question, .reveal: game
                case .finished: results
                }
            }
            .padding(24)
        }
    }

    private var lobby: some View {
        VStack(spacing: 15) {
            Spacer()
            MannaText("Join the game on your phone").font(.system(size: 27, weight: .black, design: .rounded)).foregroundColor(.white)
            Text(room.code).font(.system(size: 68, weight: .black, design: .monospaced)).tracking(12).foregroundColor(Color(hex: "#D4A843") ?? .yellow)
            MannaText("\(room.players.count) of 12 players joined").font(.system(size: 19, weight: .bold)).foregroundColor(.white.opacity(0.7))
            Text(room.players.map(\.name).joined(separator: "  •  ")).font(.system(size: 18, weight: .semibold)).foregroundColor(.white).multilineTextAlignment(.center)
            if room.players.count >= 2 {
                Button(action: { Task { await party.startGame() } }) { MannaText("Start Game") }.partyPrimary().frame(maxWidth: 440)
            } else {
                MannaText("Waiting for another player…").foregroundColor(.white.opacity(0.55))
            }
            Spacer()
        }
    }

    @ViewBuilder private var game: some View {
        if let question {
            HStack {
                MannaText("QUESTION \(room.questionNumber) OF \(room.settings.questionCount)")
                Spacer()
                MannaText("\(room.answeredCount) / \(room.players.count) ANSWERED")
            }
            .font(.system(size: 15, weight: .black)).foregroundColor(.white.opacity(0.6))
            MannaText(question.category.uppercased()).font(.system(size: 14, weight: .black)).tracking(1).foregroundColor(Color(hex: "#D4A843") ?? .yellow)
            MannaText(question.question).font(.system(size: 30, weight: .black, design: .rounded)).foregroundColor(.white).multilineTextAlignment(.center).minimumScaleFactor(0.68)
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                ForEach(Array(question.options.enumerated()), id: \.offset) { index, option in
                    Button { if room.phase == .question { Task { await party.submitAnswer(index) } } } label: {
                        HStack(spacing: 12) {
                            Text(String(UnicodeScalar(65 + index)!)).font(.system(size: 19, weight: .black)).frame(width: 38, height: 38).background(Color.white.opacity(0.11)).clipShape(Circle())
                            MannaText(option).font(.system(size: 20, weight: .bold)).multilineTextAlignment(.leading).minimumScaleFactor(0.75)
                            Spacer()
                        }
                        .foregroundColor(.white).padding(15).frame(maxWidth: .infinity, minHeight: 72)
                        .background(tvAnswerColor(index)).cornerRadius(14)
                    }
                    .disabled(room.phase == .reveal)
                }
            }
            if room.phase == .reveal {
                MannaText("Correct answer: \(question.correct)").font(.system(size: 22, weight: .black)).foregroundColor(.green)
                MannaText(correctPlayerNames).font(.system(size: 16, weight: .semibold)).foregroundColor(.white.opacity(0.75)).multilineTextAlignment(.center)
            } else if room.myAnswer != nil {
                MannaText("Host answer locked in • waiting for the room").font(.system(size: 15, weight: .bold)).foregroundColor(.green)
            }
            HStack(spacing: 16) {
                tvLeaderboard
                Button {
                    Task { if room.phase == .question { await party.revealAnswer() } else { await party.nextQuestion() } }
                } label: {
                    MannaText(room.phase == .question ? "Reveal Answer" : (room.questionNumber == room.settings.questionCount ? "Finish Game" : "Next Question"))
                }
                .partyPrimary().frame(maxWidth: 360)
            }
        } else {
            MannaText("Question unavailable on this version of Manna.").foregroundColor(.red)
        }
    }

    private var results: some View {
        VStack(spacing: 14) {
            Text("🏆").font(.system(size: 62))
            MannaText("Party Complete").font(.system(size: 38, weight: .black, design: .rounded)).foregroundColor(.white)
            ForEach(Array(room.players.prefix(8).enumerated()), id: \.element.id) { index, player in
                HStack { Text(index == 0 ? "👑" : "\(index + 1)").frame(width: 42); Text(player.name); Spacer(); Text("\(player.score) / \(room.settings.questionCount)") }
                    .font(.system(size: 21, weight: .bold)).foregroundColor(index == 0 ? (Color(hex: "#D4A843") ?? .yellow) : .white)
                    .padding(.vertical, 8).padding(.horizontal, 16).background(Color.white.opacity(0.06)).cornerRadius(11)
            }
        }
    }

    private var correctPlayerNames: String {
        let names = room.players.filter { $0.wasCorrect == true }.map(\.name)
        return names.isEmpty ? "Nobody answered correctly" : "Correct: " + names.joined(separator: ", ")
    }

    private func tvAnswerColor(_ index: Int) -> Color {
        guard let question, room.phase == .reveal else { return Color.white.opacity(0.07) }
        return index == question.correctIndex ? Color.green.opacity(0.38) : Color.white.opacity(0.06)
    }

    private var tvLeaderboard: some View {
        HStack(spacing: 14) {
            ForEach(Array(room.players.prefix(4).enumerated()), id: \.element.id) { index, player in
                Text("\(index + 1). \(player.name)  \(player.score)").font(.system(size: 14, weight: .bold)).foregroundColor(.white.opacity(0.75))
            }
        }
        .padding(12).background(Color.white.opacity(0.05)).cornerRadius(12)
    }
}

private struct PartyMenuView: View {
    @EnvironmentObject private var party: PartyManager
    @EnvironmentObject private var languageManager: LanguageManager
    @State private var name = UserDefaults.standard.string(forKey: "manna_party_name") ?? ""

    var body: some View {
        VStack(spacing: 22) {
            Spacer()
            Image(systemName: "person.3.sequence.fill")
                .font(.system(size: 72)).foregroundColor(Color(hex: "#D4A843") ?? .yellow)
            MannaText("Play Together")
                .font(.system(size: 34, weight: .black, design: .rounded)).foregroundColor(.white)
            MannaText("Everyone sees the same questions and answers on their own phone.")
                .font(.system(size: 16, weight: .medium, design: .rounded)).foregroundColor(.white.opacity(0.65))
                .multilineTextAlignment(.center).padding(.horizontal, 36)
            TextField(languageManager.interfaceString("Your name"), text: $name)
                .textInputAutocapitalization(.words).autocorrectionDisabled()
                .padding(16).background(Color.white.opacity(0.09)).cornerRadius(12).foregroundColor(.white)
                .padding(.horizontal, 30)
            Button(action: { saveName(); party.screen = .setup }) {
                MannaText("Create Party Game")
            }.partyPrimary().disabled(name.trimmingCharacters(in: .whitespaces).isEmpty)
            if !party.nearbyParties.isEmpty {
                VStack(alignment: .leading, spacing: 10) {
                    MannaLabel("Nearby on this Wi-Fi", systemImage: "wifi")
                        .font(.system(size: 15, weight: .bold)).foregroundColor(.white.opacity(0.7))
                    ForEach(party.nearbyParties) { nearby in
                        Button {
                            saveName()
                            Task { await party.joinRoom(name: name.trimmingCharacters(in: .whitespaces), code: nearby.code) }
                        } label: {
                            HStack {
                                Image(systemName: "person.3.fill")
                                MannaText("Join \(nearby.hostName)’s Party").fontWeight(.bold)
                                Spacer()
                                Image(systemName: "chevron.right")
                            }.padding(14).background(Color.white.opacity(0.09)).cornerRadius(12)
                        }.foregroundColor(.white).disabled(name.trimmingCharacters(in: .whitespaces).isEmpty || party.isWorking)
                    }
                }.padding(.horizontal, 30)
            }
            Button(action: { saveName(); party.screen = .join }) {
                MannaText("Join with a Code")
            }.partySecondary().disabled(name.trimmingCharacters(in: .whitespaces).isEmpty)
            if party.hasSavedSession {
                Button(action: { Task { await party.rejoinSavedRoom() } }) { MannaText("Rejoin Previous Party") }
                    .font(.system(size: 15, weight: .semibold)).foregroundColor(.white.opacity(0.7))
            }
            if party.isWorking { ProgressView().tint(.white) }
            Spacer()
        }
        .background { MannaText("Your name").hidden() }
    }

    private func saveName() { UserDefaults.standard.set(name.trimmingCharacters(in: .whitespaces), forKey: "manna_party_name") }
}

private struct PartySetupView: View {
    @EnvironmentObject private var gameManager: GameManager
    @EnvironmentObject private var party: PartyManager
    @EnvironmentObject private var languageManager: LanguageManager
    @State private var category = "All Categories"
    @State private var difficulty = DifficultyLevel.deacon
    @State private var audience = PlayAudience.adults
    @State private var ageGroup = ChildAgeGroup.ages4to10
    @State private var questionCount = 10

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                MannaText("Create Your Game").font(.system(size: 28, weight: .black, design: .rounded)).foregroundColor(.white)
                settingCard("Players", icon: "person.2.fill") {
                    Picker(languageManager.interfaceString("Players"), selection: $audience) {
                        ForEach(PlayAudience.allCases) { MannaText($0.rawValue).tag($0) }
                    }.pickerStyle(.segmented)
                }
                if audience == .adults {
                    settingCard("Category", icon: "square.grid.2x2.fill") {
                        Picker(languageManager.interfaceString("Category"), selection: $category) {
                            MannaText("All Categories").tag("All Categories")
                            ForEach(MannaCategory.all) { MannaText("\($0.emoji) \($0.name)").tag($0.name) }
                        }.tint(Color(hex: "#D4A843") ?? .yellow)
                    }
                    settingCard("Difficulty", icon: "graduationcap.fill") {
                        Picker(languageManager.interfaceString("Difficulty"), selection: $difficulty) {
                            ForEach(DifficultyLevel.allCases) { MannaText($0.name).tag($0) }
                        }.pickerStyle(.segmented)
                    }
                } else {
                    settingCard("Children's Age", icon: "figure.2.and.child.holdinghands") {
                        Picker(languageManager.interfaceString("Children's Age"), selection: $ageGroup) {
                            ForEach(ChildAgeGroup.allCases) { MannaText($0.shortLabel).tag($0) }
                        }.pickerStyle(.segmented)
                        MannaText("\(ageGroup.questionCount.formatted()) questions · \(ageGroup.answerChoiceCount) choices each")
                            .font(.system(size: 12, weight: .semibold)).foregroundColor(.white.opacity(0.5))
                    }
                }
                settingCard("Questions", icon: "number.circle.fill") {
                    Picker(languageManager.interfaceString("Questions"), selection: $questionCount) {
                        Text("5").tag(5); Text("10").tag(10); Text("20").tag(20)
                    }.pickerStyle(.segmented)
                }
                Button {
                    let name = UserDefaults.standard.string(forKey: "manna_party_name") ?? "Host"
                    Task {
                        await party.createRoom(
                            hostName: name,
                            category: audience == .adults && category != "All Categories" ? category : nil,
                            difficulty: difficulty.name,
                            ageGroup: audience == .children ? ageGroup : nil,
                            questionCount: questionCount,
                            questionService: gameManager.questionService
                        )
                    }
                } label: {
                    HStack { if party.isWorking { ProgressView().tint(.black) }; MannaText(party.isWorking ? "Creating…" : "Create Room") }
                }.partyPrimary().disabled(party.isWorking)
            }.padding(24)
        }
    }

    private func settingCard<Content: View>(_ title: String, icon: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            MannaLabel(title, systemImage: icon).font(.system(size: 16, weight: .bold)).foregroundColor(.white.opacity(0.75))
            content()
        }.padding(16).background(Color.white.opacity(0.06)).cornerRadius(14)
    }
}

private struct PartyJoinView: View {
    @EnvironmentObject private var party: PartyManager

    var body: some View {
        VStack(spacing: 24) {
            Spacer()
            MannaText("Enter Party Code").font(.system(size: 30, weight: .black, design: .rounded)).foregroundColor(.white)
            TextField("ABC123", text: $party.joinCode)
                .textInputAutocapitalization(.characters).autocorrectionDisabled()
                .font(.system(size: 34, weight: .black, design: .monospaced)).tracking(7).multilineTextAlignment(.center)
                .padding(18).background(Color.white.opacity(0.09)).cornerRadius(14).foregroundColor(.white)
                .padding(.horizontal, 34).onChange(of: party.joinCode) { _, value in party.joinCode = String(value.uppercased().filter { $0.isLetter || $0.isNumber }.prefix(6)) }
            Button {
                let name = UserDefaults.standard.string(forKey: "manna_party_name") ?? "Player"
                Task { await party.joinRoom(name: name, code: party.joinCode) }
            } label: {
                HStack { if party.isWorking { ProgressView().tint(.black) }; MannaText(party.isWorking ? "Joining…" : "Join Party") }
            }.partyPrimary().disabled(party.joinCode.count != 6 || party.isWorking)
            Spacer()
        }
    }
}

private struct PartyLobbyView: View {
    @EnvironmentObject private var party: PartyManager
    let room: PartyRoomSnapshot
    let openTV: () -> Void

    var body: some View {
        ScrollView {
            VStack(spacing: 18) {
                MannaText(room.isHost ? "Your Party Code" : "Waiting for the Host")
                    .font(.system(size: 20, weight: .bold, design: .rounded)).foregroundColor(.white.opacity(0.7))
                Text(room.code).font(.system(size: 44, weight: .black, design: .monospaced)).tracking(8).foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                if let qr = qrImage(room.code) { Image(uiImage: qr).interpolation(.none).resizable().scaledToFit().frame(width: 150, height: 150).background(.white).cornerRadius(12) }
                MannaText(room.settings.selectionSummary)
                    .font(.system(size: 13, weight: .semibold)).foregroundColor(.white.opacity(0.55)).multilineTextAlignment(.center)
                if room.isHost {
                    Button(action: openTV) {
                        HStack(spacing: 13) {
                            Image(systemName: "tv.and.mediabox.fill").font(.system(size: 25, weight: .bold))
                            MannaText("OPEN TV DISPLAY").font(.system(size: 19, weight: .black, design: .rounded))
                        }
                        .foregroundColor(.black)
                        .frame(maxWidth: .infinity, minHeight: 62)
                        .background(Color(hex: "#D4A843") ?? .yellow)
                        .cornerRadius(16)
                    }
                    .mannaAccessibilityLabel("Open TV Display")
                }
                VStack(spacing: 8) {
                    ForEach(room.players) { player in
                        HStack { Image(systemName: player.isHost ? "crown.fill" : "person.fill"); Text(player.name); Spacer(); if player.id == room.myPlayerId { MannaText("YOU") } }
                            .font(.system(size: 15, weight: .bold)).foregroundColor(player.isHost ? (Color(hex: "#D4A843") ?? .yellow) : .white)
                            .padding(14).background(Color.white.opacity(0.06)).cornerRadius(11)
                    }
                }
                MannaText("\(room.players.count) of 12 players joined").font(.system(size: 13)).foregroundColor(.white.opacity(0.5))
                if room.isHost {
                    Button(action: { Task { await party.startGame() } }) { MannaText("Start Game") }.partyPrimary().disabled(party.isWorking || room.players.count < 2)
                    if room.players.count < 2 {
                        MannaText("Waiting for another player to join")
                            .font(.system(size: 13, weight: .semibold)).foregroundColor(.white.opacity(0.55))
                    }
                } else {
                    HStack { ProgressView().tint(.white); MannaText("The host will start the game") }
                        .foregroundColor(.white.opacity(0.65)).padding(.top, 10)
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
                    MannaText("Question \(room.questionNumber)/\(room.settings.questionCount)")
                    Spacer(); MannaText("\(room.answeredCount)/\(room.players.count) answered")
                }.font(.system(size: 13, weight: .bold)).foregroundColor(.white.opacity(0.55))
                HStack(spacing: 4) {
                    MannaText("ROOM")
                    Text(room.code)
                }.font(.system(size: 11, weight: .bold, design: .monospaced)).tracking(2).foregroundColor(.white.opacity(0.38))
                if let question {
                    MannaText(question.category.uppercased()).font(.system(size: 12, weight: .black)).tracking(1).foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                    MannaText(question.question).font(.system(size: 22, weight: .bold, design: .rounded)).foregroundColor(.white).multilineTextAlignment(.center).padding(.vertical, 8)
                    ForEach(Array(question.options.enumerated()), id: \.offset) { index, option in
                        Button { if room.phase == .question { Task { await party.submitAnswer(index) } } } label: {
                            HStack {
                                Text(String(UnicodeScalar(65 + index)!)).font(.system(size: 14, weight: .black)).frame(width: 30, height: 30).background(answerColor(index).opacity(0.22)).clipShape(Circle())
                                MannaText(option).font(.system(size: 16, weight: .semibold)).multilineTextAlignment(.leading)
                                Spacer()
                                if room.myAnswer == index { Image(systemName: "checkmark.circle.fill") }
                            }.foregroundColor(.white).padding(14).background(answerColor(index).opacity(room.phase == .reveal || room.myAnswer == index ? 0.22 : 0.07)).cornerRadius(12)
                        }.disabled(room.phase == .reveal)
                    }
                    if room.phase == .reveal {
                        VStack(alignment: .leading, spacing: 8) {
                            MannaText(room.myAnswer == question.correctIndex ? "Correct!" : "Correct answer: \(question.correct)")
                                .font(.system(size: 18, weight: .bold)).foregroundColor(room.myAnswer == question.correctIndex ? .green : .red)
                            if !question.explanation.isEmpty { MannaText(question.explanation).font(.system(size: 14)).foregroundColor(.white.opacity(0.65)) }
                        }.frame(maxWidth: .infinity, alignment: .leading).padding(14).background(Color.white.opacity(0.06)).cornerRadius(12)
                        PartyRoundResultsView(players: room.players)
                    } else if room.myAnswer != nil {
                        MannaLabel("Answer locked in", systemImage: "checkmark.seal.fill").font(.system(size: 15, weight: .bold)).foregroundColor(.green).padding(.top, 6)
                    }
                } else {
                    MannaText("This question is not available on this version of Manna.").foregroundColor(.red)
                }
                leaderboard
                if room.isHost {
                    if room.phase == .question {
                        Button(action: { Task { await party.revealAnswer() } }) { MannaText("Reveal Answer") }.partyPrimary()
                    } else {
                        Button(action: { Task { await party.nextQuestion() } }) {
                            MannaText(room.questionNumber == room.settings.questionCount ? "Finish Game" : "Next Question")
                        }.partyPrimary()
                    }
                } else {
                    MannaText(room.phase == .question ? "Waiting for the host to reveal the answer" : "Waiting for the next question")
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
            MannaText("This Round")
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
            MannaLabel("\(title) · \(players.count)", systemImage: icon)
                .font(.system(size: 14, weight: .bold)).foregroundColor(color)
            if players.isEmpty {
                MannaText("Nobody")
                    .font(.system(size: 14, weight: .semibold)).foregroundColor(.white.opacity(0.78))
            } else {
                Text(players.map(\.name).joined(separator: ", "))
                .font(.system(size: 14, weight: .semibold)).foregroundColor(.white.opacity(0.78))
            }
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
                MannaText("Party Complete").font(.system(size: 32, weight: .black, design: .rounded)).foregroundColor(.white)
                ForEach(Array(room.players.enumerated()), id: \.element.id) { index, player in
                    HStack {
                        Text(index == 0 ? "👑" : "\(index + 1)").frame(width: 40)
                        Text(player.name).font(.system(size: 18, weight: .bold)); Spacer()
                        Text("\(player.score)/\(room.settings.questionCount)").font(.system(size: 18, weight: .black))
                    }.foregroundColor(index == 0 ? (Color(hex: "#D4A843") ?? .yellow) : .white).padding(16).background(Color.white.opacity(0.07)).cornerRadius(13)
                }
                Button(action: { party.leaveParty() }) { MannaText("Done") }.partyPrimary().padding(.top, 12)
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
