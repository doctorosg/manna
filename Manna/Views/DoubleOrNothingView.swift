import SwiftUI

struct DoubleOrNothingView: View {
    @EnvironmentObject var gameManager: GameManager
    @EnvironmentObject var performanceTracker: PerformanceTracker

    var body: some View {
        ZStack {
            Color.black.opacity(0.85).ignoresSafeArea()

            if gameManager.doubleOrNothingActive, let question = gameManager.doubleOrNothingQuestion {
                questionPhase(question: question)
            } else if gameManager.showDoubleOrNothing {
                offerPhase
            }
        }
    }

    private var offerPhase: some View {
        VStack(spacing: 20) {
            Text("⚡ BONUS CHALLENGE")
                .font(.system(size: 22, weight: .black, design: .rounded))
                .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
            Text("Great session! Want to test yourself with one more question?")
                .font(.system(size: 15)).foregroundColor(.white.opacity(0.7)).multilineTextAlignment(.center)
            HStack(spacing: 16) {
                Button(action: { gameManager.declineDoubleOrNothing() }) {
                    Text("I'm Good").foregroundColor(.white.opacity(0.6))
                        .frame(maxWidth: .infinity).padding(.vertical, 14)
                        .background(Color.white.opacity(0.1)).cornerRadius(12)
                }
                Button(action: { gameManager.acceptDoubleOrNothing() }) {
                    Text("Bring It!").font(.system(size: 16, weight: .bold)).foregroundColor(.black)
                        .frame(maxWidth: .infinity).padding(.vertical, 14)
                        .background(Color(hex: "#D4A843") ?? .yellow).cornerRadius(12)
                }
            }.padding(.horizontal, 20)
        }.padding(24)
    }

    private func questionPhase(question: MannaQuestion) -> some View {
        VStack(spacing: 16) {
            Text("⚡ BONUS CHALLENGE")
                .font(.system(size: 18, weight: .black, design: .rounded))
                .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
            HStack(spacing: 6) {
                Image(systemName: "clock.fill").font(.system(size: 12))
                Text(String(format: "%.0f", max(0, gameManager.timeRemaining)))
                    .font(.system(size: 18, weight: .bold, design: .monospaced))
            }
            .foregroundColor(gameManager.timeRemaining <= 5 ? .red : .white)

            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 2).fill(Color.white.opacity(0.1)).frame(height: 4)
                    RoundedRectangle(cornerRadius: 2)
                        .fill(gameManager.timeRemaining <= 5 ? Color.red : Color(hex: "#D4A843") ?? .yellow)
                        .frame(width: geo.size.width * max(0, gameManager.timeRemaining / gameManager.roundTimeLimit), height: 4)
                        .animation(.linear(duration: 0.1), value: gameManager.timeRemaining)
                }
            }.frame(height: 4).padding(.horizontal, 24)

            Text(question.question)
                .font(.system(size: 17, weight: .semibold, design: .rounded))
                .foregroundColor(.white).multilineTextAlignment(.center).padding(.horizontal, 20)

            VStack(spacing: 10) {
                ForEach(Array(question.options.enumerated()), id: \.offset) { index, option in
                    bonusButton(index: index, text: option, question: question)
                }
            }.padding(.horizontal, 20)

            if let result = gameManager.doubleOrNothingResult {
                VStack(spacing: 8) {
                    Text(result ? "🎉 NAILED IT!" : "❌ Not quite!")
                        .font(.system(size: 28, weight: .black, design: .rounded))
                        .foregroundColor(result ? .green : .red)
                    Text("✅ Answer: \(question.correct)")
                        .font(.system(size: 13, weight: .semibold)).foregroundColor(.green.opacity(0.8))
                }.padding(.top, 8)
                .onAppear {
                    performanceTracker.recordAnswer(category: question.category, difficulty: question.difficulty, correct: result)
                }
            }
        }.padding(.vertical, 24)
    }

    private func bonusButton(index: Int, text: String, question: MannaQuestion) -> some View {
        let selected = gameManager.selectedAnswerIndex == index
        let hasResult = gameManager.doubleOrNothingResult != nil
        let isCorrect = index == question.correctIndex
        let bgColor: Color = !hasResult ? (selected ? Color.white.opacity(0.2) : Color.white.opacity(0.08)) : isCorrect ? Color.green.opacity(0.25) : (selected && !isCorrect ? Color.red.opacity(0.25) : Color.white.opacity(0.05))
        let borderColor: Color = !hasResult ? (selected ? Color.white.opacity(0.4) : Color.white.opacity(0.12)) : isCorrect ? Color.green.opacity(0.6) : (selected && !isCorrect ? Color.red.opacity(0.6) : Color.clear)

        return Button(action: {
            if gameManager.selectedAnswerIndex == nil && gameManager.doubleOrNothingResult == nil {
                gameManager.submitDoubleOrNothingAnswer(index: index)
            }
        }) {
            HStack {
                Text(["A","B","C","D"][index]).font(.system(size: 14, weight: .bold)).foregroundColor(.white.opacity(0.4)).frame(width: 28)
                Text(text).font(.system(size: 14, weight: .medium)).foregroundColor(.white).multilineTextAlignment(.leading)
                Spacer()
                if hasResult && isCorrect { Image(systemName: "checkmark.circle.fill").foregroundColor(.green) }
                if hasResult && selected && !isCorrect { Image(systemName: "xmark.circle.fill").foregroundColor(.red) }
            }
            .padding(14).background(bgColor)
            .overlay(RoundedRectangle(cornerRadius: 12).stroke(borderColor, lineWidth: 1.5)).cornerRadius(12)
        }.disabled(gameManager.selectedAnswerIndex != nil)
    }
}
