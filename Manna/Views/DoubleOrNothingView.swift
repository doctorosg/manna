import SwiftUI

struct DoubleOrNothingView: View {
    @EnvironmentObject var gameManager: GameManager
    @EnvironmentObject var tokenManager: TokenManager

    var body: some View {
        ZStack {
            Color.black.opacity(0.85).ignoresSafeArea()

            if gameManager.doubleOrNothingActive, let question = gameManager.doubleOrNothingQuestion {
                // PHASE 2: Answer the question
                questionPhase(question: question)
            } else if gameManager.showDoubleOrNothing {
                // PHASE 1: Accept or decline
                offerPhase
            }
        }
    }

    // MARK: - Offer Phase
    private var offerPhase: some View {
        VStack(spacing: 20) {
            Text("🎲 DOUBLE OR NOTHING")
                .font(.system(size: 22, weight: .black, design: .rounded))
                .foregroundColor(Color(hex: "#D4A843") ?? .yellow)

            Text("You earned \(gameManager.doubleOrNothingStake) tokens this session.")
                .font(.system(size: 15)).foregroundColor(.white.opacity(0.7))

            Text("Risk it all on one question?")
                .font(.system(size: 14)).foregroundColor(.white.opacity(0.5))

            VStack(spacing: 8) {
                Text("Win: +\(gameManager.doubleOrNothingStake) more")
                    .font(.system(size: 14, weight: .bold)).foregroundColor(.green)
                Text("Lose: -\(gameManager.doubleOrNothingStake) tokens")
                    .font(.system(size: 14, weight: .bold)).foregroundColor(.red)
            }

            HStack(spacing: 16) {
                Button(action: { gameManager.declineDoubleOrNothing() }) {
                    Text("Keep Tokens").foregroundColor(.white.opacity(0.6))
                        .frame(maxWidth: .infinity).padding(.vertical, 14)
                        .background(Color.white.opacity(0.1)).cornerRadius(12)
                }
                Button(action: { gameManager.acceptDoubleOrNothing() }) {
                    Text("Double It!").font(.system(size: 16, weight: .bold)).foregroundColor(.black)
                        .frame(maxWidth: .infinity).padding(.vertical, 14)
                        .background(Color(hex: "#D4A843") ?? .yellow).cornerRadius(12)
                }
            }.padding(.horizontal, 20)
        }.padding(24)
    }

    // MARK: - Question Phase
    private func questionPhase(question: MannaQuestion) -> some View {
        VStack(spacing: 16) {
            // Header
            Text("🎲 DOUBLE OR NOTHING")
                .font(.system(size: 18, weight: .black, design: .rounded))
                .foregroundColor(Color(hex: "#D4A843") ?? .yellow)

            // Stakes reminder
            Text("\(gameManager.doubleOrNothingStake) tokens on the line!")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.orange)

            // Timer
            HStack(spacing: 6) {
                Image(systemName: "clock.fill").font(.system(size: 12))
                Text(String(format: "%.0f", max(0, gameManager.timeRemaining)))
                    .font(.system(size: 18, weight: .bold, design: .monospaced))
            }
            .foregroundColor(gameManager.timeRemaining <= 5 ? .red : .white)

            // Timer bar
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 2).fill(Color.white.opacity(0.1)).frame(height: 4)
                    RoundedRectangle(cornerRadius: 2)
                        .fill(gameManager.timeRemaining <= 5 ? Color.red : Color(hex: "#D4A843") ?? .yellow)
                        .frame(width: geo.size.width * max(0, gameManager.timeRemaining / gameManager.roundTimeLimit), height: 4)
                        .animation(.linear(duration: 0.1), value: gameManager.timeRemaining)
                }
            }.frame(height: 4).padding(.horizontal, 24)

            // Question
            Text(question.question)
                .font(.system(size: 17, weight: .semibold, design: .rounded))
                .foregroundColor(.white)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 20)

            // Answer options
            VStack(spacing: 10) {
                ForEach(Array(question.options.enumerated()), id: \.offset) { index, option in
                    donAnswerButton(index: index, text: option, question: question)
                }
            }
            .padding(.horizontal, 20)

            // Result display
            if let result = gameManager.doubleOrNothingResult {
                VStack(spacing: 8) {
                    Text(result ? "🎉 DOUBLED!" : "💔 LOST!")
                        .font(.system(size: 28, weight: .black, design: .rounded))
                        .foregroundColor(result ? .green : .red)
                    Text(result ? "+\(gameManager.doubleOrNothingStake) tokens!" : "-\(gameManager.doubleOrNothingStake) tokens")
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(result ? .green : .red)
                    Text("✅ Answer: \(question.correct)")
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(.green.opacity(0.8))
                        .padding(.top, 4)
                }
                .padding(.top, 8)
                .onAppear {
                    // Award/deduct tokens
                    let delta = result ? gameManager.doubleOrNothingStake : -gameManager.doubleOrNothingStake
                    tokenManager.earnTokens(delta, reason: "Double or Nothing")
                }
            }
        }
        .padding(.vertical, 24)
    }

    // MARK: - Answer Button
    private func donAnswerButton(index: Int, text: String, question: MannaQuestion) -> some View {
        let selected = gameManager.selectedAnswerIndex == index
        let hasResult = gameManager.doubleOrNothingResult != nil
        let isCorrect = index == question.correctIndex

        let bgColor: Color = {
            if !hasResult { return selected ? Color.white.opacity(0.2) : Color.white.opacity(0.08) }
            if isCorrect { return Color.green.opacity(0.25) }
            if selected && !isCorrect { return Color.red.opacity(0.25) }
            return Color.white.opacity(0.05)
        }()

        let borderColor: Color = {
            if !hasResult { return selected ? Color.white.opacity(0.4) : Color.white.opacity(0.12) }
            if isCorrect { return Color.green.opacity(0.6) }
            if selected && !isCorrect { return Color.red.opacity(0.6) }
            return Color.clear
        }()

        return Button(action: {
            if gameManager.selectedAnswerIndex == nil && gameManager.doubleOrNothingResult == nil {
                gameManager.submitDoubleOrNothingAnswer(index: index)
            }
        }) {
            HStack {
                Text(["A","B","C","D"][index])
                    .font(.system(size: 14, weight: .bold, design: .rounded))
                    .foregroundColor(.white.opacity(0.4))
                    .frame(width: 28)
                Text(text)
                    .font(.system(size: 14, weight: .medium, design: .rounded))
                    .foregroundColor(.white)
                    .multilineTextAlignment(.leading)
                Spacer()
                if hasResult && isCorrect {
                    Image(systemName: "checkmark.circle.fill").foregroundColor(.green)
                }
                if hasResult && selected && !isCorrect {
                    Image(systemName: "xmark.circle.fill").foregroundColor(.red)
                }
            }
            .padding(14)
            .background(bgColor)
            .overlay(RoundedRectangle(cornerRadius: 12).stroke(borderColor, lineWidth: 1.5))
            .cornerRadius(12)
        }
        .disabled(gameManager.selectedAnswerIndex != nil)
    }
}
