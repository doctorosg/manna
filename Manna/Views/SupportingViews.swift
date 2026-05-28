import SwiftUI

// MARK: - Splash
struct SplashView: View {
    var body: some View {
        VStack(spacing: 16) {
            Spacer()
            Text("🍞").font(.system(size: 80))
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
    @EnvironmentObject var tokenManager: TokenManager

    private var correct: Int { gameManager.roundResults.filter { $0.playerAnswer.isCorrect }.count }
    private var total: Int { gameManager.roundResults.count }
    private var netTokens: Int { gameManager.roundResults.reduce(0) { $0 + $1.netTokenChange } }

    var body: some View {
        VStack(spacing: 0) {
            ScrollView {
                VStack(spacing: 20) {
                    Text("Session Complete").font(.system(size: 24, weight: .bold, design: .rounded)).foregroundColor(.white).padding(.top, 24)

                    ZStack {
                        Circle().stroke(Color.white.opacity(0.1), lineWidth: 8).frame(width: 120, height: 120)
                        Circle().trim(from: 0, to: total > 0 ? CGFloat(correct) / CGFloat(total) : 0)
                            .stroke(Color(hex: "#D4A843") ?? .yellow, style: StrokeStyle(lineWidth: 8, lineCap: .round))
                            .frame(width: 120, height: 120).rotationEffect(.degrees(-90))
                        VStack(spacing: 2) {
                            Text("\(correct)/\(total)").font(.system(size: 28, weight: .black, design: .rounded)).foregroundColor(.white)
                            Text("Correct").font(.system(size: 12)).foregroundColor(.white.opacity(0.5))
                        }
                    }

                    HStack(spacing: 8) {
                        Image(systemName: "circle.fill").foregroundColor(.yellow).font(.system(size: 12))
                        Text("\(netTokens > 0 ? "+" : "")\(netTokens) tokens")
                            .font(.system(size: 18, weight: .bold, design: .rounded))
                            .foregroundColor(netTokens >= 0 ? Color(hex: "#D4A843") ?? .yellow : .red)
                    }.padding(.vertical, 8)

                    VStack(spacing: 8) {
                        ForEach(Array(gameManager.roundResults.enumerated()), id: \.offset) { i, result in
                            HStack {
                                Text("Q\(i+1)").font(.system(size: 13, weight: .bold)).foregroundColor(.white.opacity(0.5)).frame(width: 30)
                                Text(result.playerAnswer.isCorrect ? "✅" : "❌").frame(width: 24)
                                Text(result.question.category).font(.system(size: 12)).foregroundColor(.white.opacity(0.5)).lineLimit(1)
                                Spacer()
                                Text("\(result.netTokenChange > 0 ? "+" : "")\(result.netTokenChange)")
                                    .font(.system(size: 13, weight: .semibold, design: .rounded))
                                    .foregroundColor(result.netTokenChange >= 0 ? .green : .red)
                            }
                            .padding(.horizontal, 16).padding(.vertical, 8)
                            .background(Color.white.opacity(0.04)).cornerRadius(8)
                        }
                    }.padding(.horizontal, 16)

                    if gameManager.currentStreak >= 3 {
                        Text("🔥 \(gameManager.currentStreak) streak!")
                            .font(.system(size: 16, weight: .bold)).foregroundColor(.orange)
                    }
                }.padding(.bottom, 20)
            }

            Button(action: { gameManager.goHome() }) {
                Text("Back to Home").font(.system(size: 16, weight: .bold, design: .rounded)).foregroundColor(.black)
                    .frame(maxWidth: .infinity).padding(.vertical, 16)
                    .background(Color(hex: "#D4A843") ?? .yellow).cornerRadius(14)
            }.padding(.horizontal, 20).padding(.bottom, 20)
        }
        .overlay {
            if gameManager.showDoubleOrNothing { DoubleOrNothingView() }
        }
    }
}

// MARK: - Leaderboard
struct LeaderboardView: View {
    @EnvironmentObject var gameManager: GameManager
    @EnvironmentObject var leaderboardManager: LeaderboardManager

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Button(action: { gameManager.goHome() }) {
                    Image(systemName: "chevron.left").foregroundColor(.white)
                }
                Spacer()
                Text("Leaderboard").font(.system(size: 18, weight: .bold, design: .rounded)).foregroundColor(.white)
                Spacer()
                Color.clear.frame(width: 24)
            }.padding(.horizontal, 20).padding(.vertical, 16)

            ScrollView {
                VStack(spacing: 8) {
                    ForEach(leaderboardManager.entries) { entry in
                        HStack {
                            Text("#\(entry.rank)").font(.system(size: 14, weight: .bold)).foregroundColor(.white.opacity(0.5)).frame(width: 36)
                            Text(entry.league.icon).frame(width: 24)
                            Text(entry.playerName).font(.system(size: 15, weight: .semibold)).foregroundColor(.white)
                            Spacer()
                            VStack(alignment: .trailing) {
                                Text("\(entry.totalTokens.formatted())").font(.system(size: 14, weight: .bold, design: .rounded)).foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                            }
                        }
                        .padding(.horizontal, 16).padding(.vertical, 12)
                        .background(Color.white.opacity(0.05)).cornerRadius(10)
                    }
                }.padding(.horizontal, 16)
            }
        }
    }
}

// MARK: - Settings
struct SettingsView: View {
    @EnvironmentObject var gameManager: GameManager
    @State private var soundOn = !SoundManager.shared.isMuted

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
                // Sound toggle
                HStack {
                    Image(systemName: soundOn ? "speaker.wave.2.fill" : "speaker.slash.fill")
                        .foregroundColor(.white.opacity(0.7))
                    Text("Sound Effects").foregroundColor(.white)
                    Spacer()
                    Toggle("", isOn: $soundOn)
                        .onChange(of: soundOn) { _ in SoundManager.shared.toggleMute() }
                        .tint(Color(hex: "#D4A843") ?? .yellow)
                }
                .padding(16)
                .background(Color.white.opacity(0.05))
                .cornerRadius(12)

                // Questions loaded
                HStack {
                    Image(systemName: "book.fill").foregroundColor(.white.opacity(0.7))
                    Text("Questions loaded").foregroundColor(.white)
                    Spacer()
                    Text("\(gameManager.questionService.totalQuestionCount)")
                        .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                        .font(.system(size: 15, weight: .bold, design: .rounded))
                }
                .padding(16)
                .background(Color.white.opacity(0.05))
                .cornerRadius(12)

                // App info
                HStack {
                    Image(systemName: "info.circle.fill").foregroundColor(.white.opacity(0.7))
                    Text("Manna Bible Trivia").foregroundColor(.white)
                    Spacer()
                    Text("v1.0").foregroundColor(.white.opacity(0.5))
                }
                .padding(16)
                .background(Color.white.opacity(0.05))
                .cornerRadius(12)

                Spacer()
            }
            .padding(.horizontal, 16)
        }
    }
}
