import SwiftUI

struct GameView: View {
    @EnvironmentObject var gameManager: GameManager
    @EnvironmentObject var tokenManager: TokenManager
    @State private var showPause = false

    var body: some View {
        ZStack {
            VStack(spacing: 0) {
                // Top bar: round counter + timer + pause
                HStack {
                    Text("Q\(gameManager.currentRoundNumber)/\(gameManager.questionsPerSession)")
                        .font(.system(size: 14, weight: .bold, design: .rounded))
                        .foregroundColor(.white.opacity(0.7))
                    Spacer()
                    // Timer
                    HStack(spacing: 4) {
                        Image(systemName: "clock.fill").font(.system(size: 12))
                        Text(String(format: "%.0f", max(0, gameManager.timeRemaining)))
                            .font(.system(size: 16, weight: .bold, design: .monospaced))
                    }
                    .foregroundColor(gameManager.timeRemaining <= 5 ? .red : .white)
                    Spacer()
                    Button(action: { showPause = true; gameManager.pauseGame() }) {
                        Image(systemName: "pause.fill").font(.system(size: 16)).foregroundColor(.white.opacity(0.7))
                    }
                }
                .padding(.horizontal, 20).padding(.vertical, 12)

                // Timer bar
                GeometryReader { geo in
                    ZStack(alignment: .leading) {
                        Rectangle().fill(Color.white.opacity(0.1)).frame(height: 3)
                        Rectangle().fill(gameManager.timeRemaining <= 5 ? Color.red : Color(hex: "#D4A843") ?? .yellow)
                            .frame(width: geo.size.width * max(0, gameManager.timeRemaining / gameManager.roundTimeLimit), height: 3)
                            .animation(.linear(duration: 0.1), value: gameManager.timeRemaining)
                    }
                }.frame(height: 3)

                if let question = gameManager.currentQuestion {
                    ScrollView {
                        VStack(spacing: 20) {
                            // Category + difficulty badge
                            HStack(spacing: 8) {
                                Text(question.category).font(.system(size: 12, weight: .medium)).foregroundColor(.white.opacity(0.5))
                                Text("•").foregroundColor(.white.opacity(0.3))
                                Text(question.difficulty).font(.system(size: 12, weight: .bold))
                                    .foregroundColor(question.difficultyLevel.color)
                            }.padding(.top, 16)

                            // Question text
                            Text(question.question)
                                .font(.system(size: 20, weight: .semibold, design: .rounded))
                                .foregroundColor(.white)
                                .multilineTextAlignment(.center)
                                .padding(.horizontal, 20)

                            // Answer options
                            VStack(spacing: 10) {
                                ForEach(Array(question.options.enumerated()), id: \.offset) { index, option in
                                    answerButton(index: index, text: option, question: question)
                                }
                            }
                            .padding(.horizontal, 16)
                            .padding(.bottom, 12)

                            // Reveal section
                            if gameManager.showReveal {
                                revealSection(question: question)
                            }
                        }
                    }

                    // Next button
                    if gameManager.showReveal {
                        Button(action: { gameManager.advanceToNextRound(); tokenManager.awardRoundTokens(earned: gameManager.roundResults.last?.tokensEarned ?? 0, lost: gameManager.roundResults.last?.tokensLost ?? 0) }) {
                            Text(gameManager.currentRoundNumber >= gameManager.questionsPerSession ? "See Results" : "Next Question")
                                .font(.system(size: 16, weight: .bold, design: .rounded))
                                .foregroundColor(.black)
                                .frame(maxWidth: .infinity).padding(.vertical, 16)
                                .background(Color(hex: "#D4A843") ?? .yellow)
                                .cornerRadius(14)
                        }
                        .padding(.horizontal, 20).padding(.bottom, 20)
                    }
                }
            }

            // Pause overlay
            if showPause {
                pauseOverlay
            }

            // Level Up offer
            if gameManager.showLevelUpOffer {
                levelUpOverlay
            }

            // Countdown popup for last 5 seconds
            if gameManager.isTimerRunning && gameManager.timeRemaining <= 5 && gameManager.timeRemaining > 0 && gameManager.selectedAnswerIndex == nil {
                Text(String(format: "%.0f", gameManager.timeRemaining))
                    .font(.system(size: 80, weight: .black, design: .rounded))
                    .foregroundColor(.red.opacity(0.3))
                    .allowsHitTesting(false)
            }
        }
    }

    // MARK: - Answer Button
    @ViewBuilder
    private func answerButton(index: Int, text: String, question: MannaQuestion) -> some View {
        let selected = gameManager.selectedAnswerIndex == index
        let revealed = gameManager.showReveal
        let isCorrect = index == question.correctIndex
        let bgColor: Color = {
            if !revealed { return selected ? Color.white.opacity(0.15) : Color.white.opacity(0.06) }
            if isCorrect { return Color.green.opacity(0.25) }
            if selected && !isCorrect { return Color.red.opacity(0.25) }
            return Color.white.opacity(0.04)
        }()
        let borderColor: Color = {
            if !revealed { return selected ? Color.white.opacity(0.4) : Color.white.opacity(0.1) }
            if isCorrect { return Color.green.opacity(0.6) }
            if selected && !isCorrect { return Color.red.opacity(0.6) }
            return Color.clear
        }()

        Button(action: { if gameManager.selectedAnswerIndex == nil { gameManager.submitAnswer(index: index) } }) {
            HStack {
                Text(["A","B","C","D"][index])
                    .font(.system(size: 14, weight: .bold, design: .rounded))
                    .foregroundColor(.white.opacity(0.4))
                    .frame(width: 28)
                Text(text)
                    .font(.system(size: 15, weight: .medium, design: .rounded))
                    .foregroundColor(.white)
                    .multilineTextAlignment(.leading)
                Spacer()
                if revealed && isCorrect { Image(systemName: "checkmark.circle.fill").foregroundColor(.green) }
                if revealed && selected && !isCorrect { Image(systemName: "xmark.circle.fill").foregroundColor(.red) }
            }
            .padding(16)
            .background(bgColor)
            .overlay(RoundedRectangle(cornerRadius: 12).stroke(borderColor, lineWidth: 1.5))
            .cornerRadius(12)
        }
        .disabled(gameManager.selectedAnswerIndex != nil)
    }

    // MARK: - Reveal
    @ViewBuilder
    private func revealSection(question: MannaQuestion) -> some View {
        if let last = gameManager.roundResults.last {
            VStack(spacing: 12) {
                HStack {
                    Text(last.playerAnswer.isCorrect ? "✅ Correct!" : "❌ Wrong")
                        .font(.system(size: 16, weight: .bold)).foregroundColor(last.playerAnswer.isCorrect ? .green : .red)
                    Spacer()
                    if last.netTokenChange != 0 {
                        Text("\(last.netTokenChange > 0 ? "+" : "")\(last.netTokenChange)")
                            .font(.system(size: 14, weight: .bold, design: .rounded))
                            .foregroundColor(last.netTokenChange > 0 ? Color(hex: "#D4A843") ?? .yellow : .red)
                    }
                }
                if !question.explanation.isEmpty {
                    Text(question.explanation)
                        .font(.system(size: 13)).foregroundColor(.white.opacity(0.5))
                        .multilineTextAlignment(.leading)
                }
                Text("✅ Answer: \(question.correct)")
                    .font(.system(size: 13, weight: .semibold)).foregroundColor(.green.opacity(0.8))
            }
            .padding(16)
            .background(Color.white.opacity(0.05))
            .cornerRadius(12)
            .padding(.horizontal, 16)
        }
    }

    // MARK: - Pause Overlay
    private var pauseOverlay: some View {
        ZStack {
            Color.black.opacity(0.7).ignoresSafeArea()
            VStack(spacing: 20) {
                Text("⏸ Paused").font(.system(size: 28, weight: .bold, design: .rounded)).foregroundColor(.white)
                Button(action: { showPause = false; gameManager.resumeGame() }) {
                    Text("Resume").font(.system(size: 18, weight: .bold)).foregroundColor(.black)
                        .frame(maxWidth: .infinity).padding(.vertical, 16)
                        .background(Color(hex: "#D4A843") ?? .yellow).cornerRadius(14)
                }.padding(.horizontal, 40)
                Button(action: { showPause = false; gameManager.quitGame() }) {
                    Text("Quit").font(.system(size: 16, weight: .medium)).foregroundColor(.red)
                }
            }
        }
    }

    // MARK: - Level Up Overlay
    private var levelUpOverlay: some View {
        ZStack {
            Color.black.opacity(0.7).ignoresSafeArea()
            VStack(spacing: 16) {
                Text("⚡️ LEVEL UP CHALLENGE").font(.system(size: 22, weight: .black, design: .rounded)).foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                Text("Answer a harder question for \(gameManager.levelUpBonusTokens) bonus tokens!")
                    .font(.system(size: 14)).foregroundColor(.white.opacity(0.7)).multilineTextAlignment(.center)
                Text("Risk: -\(gameManager.levelUpPenaltyTokens) if wrong")
                    .font(.system(size: 13)).foregroundColor(.red.opacity(0.7))
                HStack(spacing: 16) {
                    Button(action: { gameManager.declineLevelUp() }) {
                        Text("Skip").foregroundColor(.white.opacity(0.6)).frame(maxWidth: .infinity).padding(.vertical, 14)
                            .background(Color.white.opacity(0.1)).cornerRadius(12)
                    }
                    Button(action: { gameManager.acceptLevelUp() }) {
                        Text("Accept!").font(.system(size: 16, weight: .bold)).foregroundColor(.black)
                            .frame(maxWidth: .infinity).padding(.vertical, 14)
                            .background(Color(hex: "#D4A843") ?? .yellow).cornerRadius(12)
                    }
                }.padding(.horizontal, 20)
            }.padding(24)
        }
    }
}
