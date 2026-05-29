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
    @State private var soundOn = !SoundManager.shared.isMuted
    @State private var showResetAlert = false

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Button(action: { gameManager.goHome() }) {
                    Image(systemName: "chevron.left").foregroundColor(.white)
                }
                Spacer()
                Text("Settings").font(.system(size: 18, weight: .bold, design: .rounded)).foregroundColor(.white)
                Spacer()
                Color.clear.frame(width: 24)
            }.padding(.horizontal, 20).padding(.vertical, 16)

            VStack(spacing: 16) {
                // Sound
                HStack {
                    Image(systemName: soundOn ? "speaker.wave.2.fill" : "speaker.slash.fill")
                        .foregroundColor(.white.opacity(0.7))
                    Text("Sound Effects").foregroundColor(.white)
                    Spacer()
                    Toggle("", isOn: $soundOn)
                        .onChange(of: soundOn) { _ in SoundManager.shared.toggleMute() }
                        .tint(Color(hex: "#D4A843") ?? .yellow)
                }
                .padding(16).background(Color.white.opacity(0.05)).cornerRadius(12)

                // Questions count
                HStack {
                    Image(systemName: "book.fill").foregroundColor(.white.opacity(0.7))
                    Text("Questions loaded").foregroundColor(.white)
                    Spacer()
                    Text("\(gameManager.questionService.totalQuestionCount)")
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

                // App info
                HStack {
                    Image(systemName: "info.circle.fill").foregroundColor(.white.opacity(0.7))
                    Text("Manna Bible Trivia").foregroundColor(.white)
                    Spacer()
                    Text("v1.0").foregroundColor(.white.opacity(0.5))
                }
                .padding(16).background(Color.white.opacity(0.05)).cornerRadius(12)

                Spacer()
            }
            .padding(.horizontal, 16)
        }
    }
}
