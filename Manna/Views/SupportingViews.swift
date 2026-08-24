import SwiftUI

// MARK: - Splash
struct SplashView: View {
    var body: some View {
        VStack(spacing: 16) {
            Spacer()
            Image("challah")
                .resizable()
                .scaledToFit()
                .frame(width: 140, height: 90)
            Text("MANNA").font(.system(size: 48, weight: .black, design: .serif))
                .foregroundColor(Color(hex: "#D4A843") ?? .yellow).tracking(6)
            Text("BIBLE TRIVIA").font(.system(size: 14, weight: .semibold)).foregroundColor(.white.opacity(0.5)).tracking(4)
            Spacer()
            ProgressView().tint(.white.opacity(0.5)).padding(.bottom, 40)
        }
    }
}

// MARK: - Result
struct ResultView: View {
    @EnvironmentObject var gameManager: GameManager
    @EnvironmentObject var performanceTracker: PerformanceTracker

    private var correct: Int { gameManager.roundResults.filter { $0.playerAnswer.isCorrect }.count }
    private var total: Int { gameManager.roundResults.count }
    private var pct: Int { total > 0 ? Int(Double(correct) / Double(total) * 100) : 0 }

    private var letterGrade: String {
        switch pct {
        case 90...100: return "A"
        case 80..<90: return "B"
        case 70..<80: return "C"
        case 60..<70: return "D"
        default: return "F"
        }
    }

    private var gradeColor: Color {
        switch letterGrade {
        case "A": return .green
        case "B": return Color(hex: "#D4A843") ?? .yellow
        case "C": return .orange
        case "D": return .orange
        default: return .red
        }
    }

    var body: some View {
        VStack(spacing: 0) {
            ScrollView {
                VStack(spacing: 16) {
                    Text("Session Complete")
                        .font(.system(size: 24, weight: .bold, design: .rounded))
                        .foregroundColor(.white).padding(.top, 24)

                    // Score circle
                    ZStack {
                        Circle().stroke(Color.white.opacity(0.1), lineWidth: 8).frame(width: 130, height: 130)
                        Circle().trim(from: 0, to: total > 0 ? CGFloat(correct) / CGFloat(total) : 0)
                            .stroke(gradeColor, style: StrokeStyle(lineWidth: 8, lineCap: .round))
                            .frame(width: 130, height: 130).rotationEffect(.degrees(-90))
                        VStack(spacing: 2) {
                            Text("\(correct)/\(total)")
                                .font(.system(size: 28, weight: .black, design: .rounded))
                                .foregroundColor(.white)
                            Text("Correct")
                                .font(.system(size: 12))
                                .foregroundColor(.white.opacity(0.5))
                        }
                    }

                    // BIG percentage + Letter Grade
                    VStack(spacing: 4) {
                        Text("\(pct)%")
                            .font(.system(size: 48, weight: .black, design: .rounded))
                            .foregroundColor(gradeColor)
                        HStack(spacing: 8) {
                            Text("Grade:")
                                .font(.system(size: 16, weight: .medium))
                                .foregroundColor(.white.opacity(0.5))
                            Text(letterGrade)
                                .font(.system(size: 32, weight: .black, design: .rounded))
                                .foregroundColor(gradeColor)
                        }
                    }

                    // Round breakdown
                    VStack(spacing: 8) {
                        ForEach(Array(gameManager.roundResults.enumerated()), id: \.offset) { i, result in
                            HStack {
                                Text("Q\(i+1)")
                                    .font(.system(size: 13, weight: .bold))
                                    .foregroundColor(.white.opacity(0.5)).frame(width: 30)
                                Text(result.playerAnswer.isCorrect ? "✅" : (result.playerAnswer.selectedIndex < 0 ? "⏰" : "❌")).frame(width: 24)
                                Text(result.question.category)
                                    .font(.system(size: 12))
                                    .foregroundColor(.white.opacity(0.5)).lineLimit(1)
                                Spacer()
                                Text(result.question.difficulty)
                                    .font(.system(size: 11, weight: .medium))
                                    .foregroundColor(result.question.difficultyLevel.color)
                            }
                            .padding(.horizontal, 16).padding(.vertical, 8)
                            .background(Color.white.opacity(0.04)).cornerRadius(8)
                        }
                    }.padding(.horizontal, 16)

                    if gameManager.currentStreak >= 3 {
                        Text("🔥 \(gameManager.currentStreak) streak!")
                            .font(.system(size: 16, weight: .bold)).foregroundColor(.orange)
                    }

                    encouragement
                }.padding(.bottom, 20)
            }

            VStack(spacing: 10) {
                Button(action: { gameManager.goToPreGame() }) {
                    Text("Play Again")
                        .font(.system(size: 16, weight: .bold, design: .rounded))
                        .foregroundColor(.black)
                        .frame(maxWidth: .infinity).padding(.vertical, 16)
                        .background(Color(hex: "#D4A843") ?? .yellow).cornerRadius(14)
                }
                Button(action: { gameManager.goHome() }) {
                    Text("Home")
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.white.opacity(0.6))
                }
            }
            .padding(.horizontal, 20).padding(.bottom, 20)
        }
        .onAppear { performanceTracker.recordGameComplete() }
        .overlay {
            if gameManager.showDoubleOrNothing || gameManager.doubleOrNothingActive { DoubleOrNothingView() }
        }
    }

    private var encouragement: some View {
        Group {
            if total > 0 {
                switch letterGrade {
                case "A":
                    Text("🏆 Outstanding! You really know your Bible!")
                        .font(.system(size: 14, weight: .semibold)).foregroundColor(.green)
                case "B":
                    Text("🌟 Great job! Strong Bible knowledge.")
                        .font(.system(size: 14, weight: .semibold)).foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                case "C":
                    Text("👍 Good effort! Keep studying to improve.")
                        .font(.system(size: 14, weight: .semibold)).foregroundColor(.white.opacity(0.6))
                case "D":
                    Text("📖 Room to grow! Check My Stats for study tips.")
                        .font(.system(size: 14, weight: .semibold)).foregroundColor(.white.opacity(0.6))
                default:
                    Text("📖 Check out My Stats for study suggestions to improve!")
                        .font(.system(size: 14, weight: .semibold)).foregroundColor(.white.opacity(0.6))
                }
            }
        }
        .multilineTextAlignment(.center)
        .padding(.horizontal, 20)
    }
}

// MARK: - Settings
struct SettingsView: View {
    @EnvironmentObject var gameManager: GameManager
    @EnvironmentObject var performanceTracker: PerformanceTracker
    @EnvironmentObject var languageManager: LanguageManager
    @EnvironmentObject var monetization: MonetizationManager
    @Environment(\.openURL) private var openURL
    @StateObject private var updateChecker = UpdateChecker()
    @State private var soundOn = !SoundManager.shared.isMuted
    @State private var showResetAlert = false
    @State private var selectedSettingsTab = 0

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Button(action: { gameManager.goHome() }) {
                    Image(systemName: "chevron.left").foregroundColor(.white)
                }
                Spacer()
                Text(languageManager.ui("settings")).font(.system(size: 18, weight: .bold, design: .rounded)).foregroundColor(.white)
                Spacer()
                Color.clear.frame(width: 24, height: 24)
            }.padding(.horizontal, 20).padding(.vertical, 16)

            Picker("Settings section", selection: $selectedSettingsTab) {
                Text("Settings").tag(0)
                Text("Info & How It Works").tag(1)
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 16)
            .padding(.bottom, 12)

            if selectedSettingsTab == 0 {
            ScrollView {
            VStack(spacing: 16) {
                // Sound
                HStack {
                    Image(systemName: soundOn ? "speaker.wave.2.fill" : "speaker.slash.fill")
                        .foregroundColor(.white.opacity(0.7))
                    Text("Sound Effects").foregroundColor(.white)
                    Spacer()
                    Toggle("", isOn: $soundOn)
                        .onChange(of: soundOn) { _, enabled in
                            SoundManager.shared.setMuted(!enabled)
                            if enabled { SoundManager.shared.playCorrect() }
                        }
                        .tint(Color(hex: "#D4A843") ?? .yellow)
                }
                .padding(16).background(Color.white.opacity(0.05)).cornerRadius(12)

                // Language and on-device question translation
                HStack {
                    Image(systemName: "globe").foregroundColor(.white.opacity(0.7))
                    Text(languageManager.ui("language")).foregroundColor(.white)
                    Spacer()
                    Picker(languageManager.ui("language"), selection: $languageManager.selected) {
                        ForEach(LanguageManager.AppLanguage.allCases) { language in
                            Text(language.displayName).tag(language)
                        }
                    }
                    .pickerStyle(.menu).tint(Color(hex: "#D4A843") ?? .yellow)
                }
                .padding(16).background(Color.white.opacity(0.05)).cornerRadius(12)

                Button(action: {
                    if case let .available(_, url) = updateChecker.status { openURL(url) }
                    else { Task { await updateChecker.check() } }
                }) {
                    HStack {
                        Image(systemName: "arrow.triangle.2.circlepath").foregroundColor(.white.opacity(0.7))
                        Text(updateButtonTitle).foregroundColor(.white)
                        Spacer()
                        if updateChecker.status == .checking { ProgressView().tint(.white) }
                    }
                    .padding(16).background(Color.white.opacity(0.05)).cornerRadius(12)
                }
                if let message = updateMessage {
                    Text(message).font(.system(size: 12)).foregroundColor(.white.opacity(0.55))
                        .frame(maxWidth: .infinity, alignment: .leading).padding(.horizontal, 4)
                }

                if !monetization.hasPurchasedAdFree {
                    VStack(alignment: .leading, spacing: 12) {
                        Label("Remove Advertising", systemImage: "rectangle.slash.fill")
                            .font(.system(size: 17, weight: .bold, design: .rounded))
                            .foregroundColor(.white)
                        Text("A single one-time purchase permanently removes every banner, bonus ad and scheduled full-screen ad, and enables offline play.")
                            .font(.system(size: 13)).foregroundColor(.white.opacity(0.62))
                        Button {
                            Task { await monetization.purchaseAdFree() }
                        } label: {
                            Text(monetization.isPurchasing ? "Please wait…" : "Remove Ads · \(monetization.purchasePrice)")
                                .font(.system(size: 14, weight: .bold))
                                .foregroundColor(.black).frame(maxWidth: .infinity).padding(.vertical, 12)
                                .background(Color(hex: "#D4A843") ?? .yellow).cornerRadius(10)
                        }
                        .disabled(monetization.isPurchasing)
                        Button("Restore Purchase") { Task { await monetization.restorePurchases() } }
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundColor(.white.opacity(0.7)).frame(maxWidth: .infinity)
                        if let message = monetization.purchaseMessage {
                            Text(message).font(.system(size: 12)).foregroundColor(.white.opacity(0.6))
                        }
                        if monetization.privacyOptionsRequired {
                            Button("Advertising Privacy Choices") { Task { await monetization.showPrivacyOptions() } }
                                .font(.system(size: 13, weight: .semibold))
                                .foregroundColor(.white.opacity(0.7)).frame(maxWidth: .infinity)
                        }
                    }
                    .padding(16).background(Color.white.opacity(0.05)).cornerRadius(12)
                }

                // Questions count
                HStack {
                    Image(systemName: "book.fill").foregroundColor(.white.opacity(0.7))
                    Text("Questions loaded").foregroundColor(.white)
                    Spacer()
                    Text(gameManager.questionService.totalQuestionCount.formatted())
                        .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                        .font(.system(size: 15, weight: .bold, design: .rounded))
                }
                .padding(16).background(Color.white.opacity(0.05)).cornerRadius(12)

                // Reset performance
                Button(action: { showResetAlert = true }) {
                    HStack {
                        Image(systemName: "arrow.counterclockwise").foregroundColor(.red.opacity(0.7))
                        Text("Reset Performance Data").foregroundColor(.red.opacity(0.7))
                        Spacer()
                    }
                    .padding(16).background(Color.white.opacity(0.05)).cornerRadius(12)
                }
                .alert("Reset Performance?", isPresented: $showResetAlert) {
                    Button("Cancel", role: .cancel) {}
                    Button("Reset", role: .destructive) { performanceTracker.resetAll() }
                } message: {
                    Text("This will erase all your performance history. This cannot be undone.")
                }

                // App information
                VStack(alignment: .leading, spacing: 12) {
                    Label("About Manna", systemImage: "info.circle.fill")
                        .font(.system(size: 17, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                    Divider().overlay(Color.white.opacity(0.12))
                    appInfoRow("Publisher", "Odd Current Software")
                    appInfoRow("Questions", gameManager.questionService.totalQuestionCount.formatted())
                    appInfoRow("Categories", "21")
                    appInfoRow("Difficulty levels", "3")
                    Text("Layperson · Deacon · Pastor")
                        .font(.system(size: 12)).foregroundColor(.white.opacity(0.5))
                    appInfoRow("Languages", LanguageManager.AppLanguage.allCases.count.formatted())
                    appInfoRow("Questions per session", "5")
                    if !monetization.hasPurchasedAdFree {
                        appInfoRow("Questions presented", monetization.freeQuestionsUsed.formatted())
                    }
                    appInfoRow("Version", Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "1.0.1")
                    Divider().overlay(Color.white.opacity(0.12))
                    Text(monetization.hasPurchasedAdFree ? "All questions ad-free · No subscriptions" : "Answer banners · One-time Remove Ads purchase · No subscriptions")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                }
                .padding(16).background(Color.white.opacity(0.05)).cornerRadius(12)
            }
            .padding(.horizontal, 16)
            .padding(.bottom, 20)
            }
            } else {
                MannaInfoView(questionCount: gameManager.questionService.totalQuestionCount, showsHeader: false)
            }
        }
    }

    private func appInfoRow(_ label: String, _ value: String) -> some View {
        HStack(alignment: .firstTextBaseline) {
            Text(label).font(.system(size: 13)).foregroundColor(.white.opacity(0.62))
            Spacer()
            Text(value).font(.system(size: 13, weight: .semibold)).foregroundColor(.white)
                .multilineTextAlignment(.trailing)
        }
    }

    private var updateButtonTitle: String {
        if case let .available(version, _) = updateChecker.status { return "Update to v\(version)" }
        return languageManager.ui("check_updates")
    }

    private var updateMessage: String? {
        switch updateChecker.status {
        case .idle, .checking: nil
        case .current: "You have the latest version."
        case .available: "A newer App Store version is available."
        case let .unavailable(message): message
        }
    }
}

private struct MannaInfoView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var monetization: MonetizationManager
    let questionCount: Int
    var showsHeader = true

    var body: some View {
        ZStack {
            Color(hex: "#0F1223")?.ignoresSafeArea()
            VStack(spacing: 0) {
                if showsHeader {
                HStack {
                    Button("Done") { dismiss() }
                        .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                    Spacer()
                    Text("About Manna").font(.system(size: 18, weight: .bold, design: .rounded)).foregroundColor(.white)
                    Spacer()
                    Color.clear.frame(width: 44, height: 1)
                }.padding()
                }

                ScrollView {
                    VStack(alignment: .leading, spacing: 16) {
                        infoSection("How Manna works", icon: "questionmark.circle.fill") {
                            Text("Choose one or more categories and a difficulty level. Each session presents five questions. Select an answer and change it as often as needed before using Show Answer or Next Question to lock it in. There is no answer timer. Players who answer at least three of five correctly may accept one optional bonus challenge. Performance history records accuracy, difficulty and category results.")
                            Text("Manna shows every eligible question once before beginning a new cycle, and this history is saved between launches. Every record has a permanent Question # shared by Apple and Android; include that number when contacting support about a disputed answer.")
                        }

                        infoSection("Difficulty levels", icon: "chart.bar.fill") {
                            level("Layperson", "Foundation level. It emphasizes widely known Bible stories, major people and events, familiar passages and direct identification. The wording and required background knowledge are the most approachable.")
                            level("Deacon", "Intermediate level. It expects regular Bible reading and asks about context, relationships, chronology, less familiar events and Scripture cross-references. Distractors are closer to the correct answer.")
                            level("Pastor", "Advanced level. It includes minor prophets, genealogies, detailed chronology, Hebrew and Greek terms, Church Fathers and deeper textual connections. Questions require more specialized recall and comparison of sources.")
                            Text("Difficulty describes the knowledge and reasoning required—not a countdown. All three levels remain untimed.")
                        }

                        if monetization.shouldExplainAdvertising {
                            infoSection("Advertising and the ad-free purchase", icon: "rectangle.on.rectangle") {
                                Text("In the unpaid Apple version, a small banner appears in its own reserved, labelled area beneath the multiple-choice answers on every regular question. It is separated from the answer choices and controls, never covers game content and does not pause the game. The unpaid version requires an active Wi-Fi or cellular internet connection.")
                                Text("After the first 40 regular questions, a full-screen ad may appear after each additional 10 regular questions, only at the end of a five-question session. If a bonus challenge is offered, its button clearly identifies the voluntary rewarded ad shown before that bonus. A cooldown separates full-screen ads to prevent back-to-back interruptions. If an ad cannot load, Manna continues and never withholds an answer or promised bonus.")
                                Text("The one-time Remove Ads purchase permanently removes all banners, bonus advertisements and scheduled full-screen ads, and enables offline play. Manna has no advertising subscriptions.")
                            }
                        }

                        infoSection("Where the questions come from", icon: "books.vertical.fill") {
                            Text("Manna contains \(questionCount.formatted()) permanently numbered question records in 21 categories. Question numbers are identical on Apple and Android and are never reassigned to a different record. Its bundled, offline bank is assembled from the King James Bible, Treasury of Scripture Knowledge cross-references, Gospel-to-Old-Testament links, Strong’s Hebrew and Greek lexicons, Catena Aurea and other public-domain Bible-study data also used by Lumina. Release checks remove duplicate question text, reject invalid choices and enforce the difficulty rules.")
                        }

                        infoSection("Where the answers come from", icon: "checkmark.seal.fill") {
                            Text("Each correct answer is stored with its question. Source-backed audits recheck supported question patterns against the KJV, Strong’s/BDB/Thayer lexicons and Catena Aurea records; the remaining patterns require editorial review rather than being declared correct by a format check. Explanations include a reference or context when the source provides one. Manna is a study game, so users should consult Scripture and trusted study resources when examining disputed interpretations.")
                        }

                        infoSection("Odd Current Software", icon: "bolt.horizontal.circle.fill") {
                            Text(monetization.hasPurchasedAdFree
                                 ? "Odd Current Software creates focused, respectful apps for study and everyday life. This copy of Manna is permanently ad-free and has no subscriptions."
                                 : "Odd Current Software creates focused, respectful apps for study and everyday life. Manna provides an optional one-time purchase that permanently removes advertising; it has no advertising subscriptions.")
                        }

                        infoSection("More from Odd Current", icon: "square.grid.2x2.fill") {
                            product("Lumina Bible Study", "A deep Bible-reading and study app that places Scripture beside cross-references, Strong’s concordance material, commentaries, Church Fathers, Mishnah, Talmud, Septuagint resources, maps and personal notes.")
                            product("Sabbath Watch", "Uses location-aware sunset calculations to show the weekly Sabbath countdown and start/end times. It supports reminders, saved cities, Apple Watch faces and complications, and a bedside clock view.")
                            product("Clean Table", "Helps users check foods, ingredient lists and packaged products against biblical food-law categories. It supports product lookup, ingredient analysis and UPC barcode scanning.")
                        }
                    }
                    .font(.system(size: 14, design: .rounded))
                    .foregroundColor(.white.opacity(0.76))
                    .padding(16)
                    .padding(.bottom, 20)
                }
            }
        }
        .preferredColorScheme(.dark)
    }

    private func infoSection<Content: View>(_ title: String, icon: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Label(title, systemImage: icon)
                .font(.system(size: 17, weight: .bold, design: .rounded))
                .foregroundColor(.white)
            content().fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(Color.white.opacity(0.05))
        .cornerRadius(14)
    }

    private func level(_ name: String, _ detail: String) -> some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(name).fontWeight(.bold).foregroundColor(Color(hex: "#D4A843") ?? .yellow)
            Text(detail)
        }
    }

    private func product(_ name: String, _ detail: String) -> some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(name).fontWeight(.bold).foregroundColor(.white)
            Text(detail)
        }
    }
}
