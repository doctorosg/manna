import SwiftUI
import Translation

struct GameView: View {
    @EnvironmentObject var gameManager: GameManager
    @EnvironmentObject var performanceTracker: PerformanceTracker
    @EnvironmentObject var languageManager: LanguageManager
    @EnvironmentObject var monetization: MonetizationManager

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                MannaText("\(gameManager.currentRoundNumber)/\(gameManager.questionsPerSession)  •  Question #\(gameManager.currentQuestion?.number ?? 0)")
                    .font(.system(size: 14, weight: .bold, design: .rounded))
                    .foregroundColor(.white.opacity(0.7))
                Spacer()
                Button(action: { gameManager.quitGame() }) {
                    Image(systemName: "xmark").foregroundColor(.white.opacity(0.7))
                }
                .mannaAccessibilityLabel("Quit")
            }
            .padding(.horizontal, 20).padding(.vertical, 14)

            if let question = gameManager.currentQuestion {
                let localized = languageManager.localizedQuestion?.id == question.id ? languageManager.localizedQuestion : nil
                ScrollView {
                    VStack(spacing: 20) {
                        HStack(spacing: 8) {
                            Text(localized?.category ?? question.category)
                                .font(.system(size: 12, weight: .medium)).foregroundColor(.white.opacity(0.5))
                            Text("•").foregroundColor(.white.opacity(0.3))
                            MannaText(question.audienceLevelLabel).font(.system(size: 12, weight: .bold))
                                .foregroundColor(question.difficultyLevel.color)
                        }.padding(.top, 8)

                        if languageManager.isTranslating { ProgressView().tint(.white.opacity(0.6)) }

                        Text(localized?.question ?? question.question)
                            .font(.system(size: 20, weight: .semibold, design: .rounded))
                            .foregroundColor(.white).multilineTextAlignment(.center).padding(.horizontal, 20)

                        VStack(spacing: 10) {
                            ForEach(question.options.indices, id: \.self) { index in
                                answerButton(
                                    index: index,
                                    text: localized?.options[safe: index] ?? question.options[index],
                                    question: question
                                )
                            }
                        }.padding(.horizontal, 16)

                        if gameManager.showReveal {
                            revealSection(question: question, localized: localized)
                        } else if gameManager.selectedAnswerIndex != nil {
                            MannaText("Answer selected. You can change it until you reveal the answer or continue.")
                                .font(.system(size: 13)).foregroundColor(.white.opacity(0.5))
                                .multilineTextAlignment(.center).padding(.horizontal, 20)
                        }

                        if let error = languageManager.translationError {
                            MannaText("Translation unavailable: \(error)")
                                .font(.system(size: 12)).foregroundColor(.orange.opacity(0.8))
                                .multilineTextAlignment(.center).padding(.horizontal, 20)
                        }

                        if monetization.shouldShowAds {
                            VStack(spacing: 7) {
                                Divider().overlay(Color.white.opacity(0.10))
                                MannaText("Advertisement")
                                    .font(.system(size: 9, weight: .medium, design: .rounded))
                                    .foregroundColor(.white.opacity(0.42))
                                    .textCase(.uppercase)
                                    .accessibilityHidden(true)
                                MannaBannerAd()
                            }
                            .padding(.top, 10)
                            .padding(.horizontal, 16)
                            .background(Color.black.opacity(0.12))
                        }
                    }.padding(.bottom, 16)
                }

                HStack(spacing: 12) {
                    Button(action: {
                        DiagnosticRecorder.shared.record("answer_revealed question=\(question.number) banner_eligible=\(monetization.shouldShowAds)")
                        gameManager.showCorrectAnswer()
                    }) {
                        Label(languageManager.ui("show_answer"), systemImage: "eye.fill")
                            .font(.system(size: 14, weight: .bold, design: .rounded)).foregroundColor(.white)
                            .frame(maxWidth: .infinity).padding(.vertical, 15)
                            .background(Color.white.opacity(0.1)).cornerRadius(14)
                    }.disabled(gameManager.showReveal)

                    Button(action: { advance(from: question) }) {
                        Text(gameManager.currentRoundNumber >= gameManager.questionsPerSession ? languageManager.ui("results") : languageManager.ui("next"))
                            .font(.system(size: 14, weight: .bold, design: .rounded)).foregroundColor(.black)
                            .frame(maxWidth: .infinity).padding(.vertical, 15)
                            .background(Color(hex: "#D4A843") ?? .yellow).cornerRadius(14)
                    }
                }.padding(.horizontal, 16).padding(.bottom, 16)
            }
        }
        .onAppear {
            languageManager.prepare(gameManager.currentQuestion)
            if let question = gameManager.currentQuestion {
                DiagnosticRecorder.shared.record("question_presented number=\(question.number) difficulty=\(question.difficulty)")
                monetization.recordQuestionPresented(questionID: question.id)
            }
        }
        .onChange(of: gameManager.currentQuestion?.id) { _ in
            languageManager.prepare(gameManager.currentQuestion)
            if let question = gameManager.currentQuestion {
                DiagnosticRecorder.shared.record("question_presented number=\(question.number) difficulty=\(question.difficulty)")
                monetization.recordQuestionPresented(questionID: question.id)
            }
        }
        .onChange(of: languageManager.selected) { languageManager.prepare(gameManager.currentQuestion) }
        .translationTask(languageManager.translationConfiguration) { session in
            if let question = gameManager.currentQuestion { await languageManager.translate(question, using: session) }
        }
    }

    private func answerButton(index: Int, text: String, question: MannaQuestion) -> some View {
        let selected = gameManager.selectedAnswerIndex == index
        let revealed = gameManager.showReveal
        let isCorrect = index == question.correctIndex
        let background: Color = revealed && isCorrect ? .green.opacity(0.25) :
            (revealed && selected ? .red.opacity(0.25) : (selected ? .white.opacity(0.16) : .white.opacity(0.06)))
        let border: Color = revealed && isCorrect ? .green.opacity(0.7) :
            (revealed && selected ? .red.opacity(0.7) : (selected ? .white.opacity(0.45) : .white.opacity(0.1)))

        return Button(action: {
            DiagnosticRecorder.shared.record("answer_selected question=\(question.number) option=\(index + 1)")
            gameManager.selectAnswer(index: index)
        }) {
            HStack {
                Text(String(UnicodeScalar(65 + index)!))
                    .font(.system(size: 14, weight: .bold, design: .rounded))
                    .foregroundColor(.white.opacity(0.45)).frame(width: 28)
                Text(text).font(.system(size: 15, weight: .medium, design: .rounded))
                    .foregroundColor(.white).multilineTextAlignment(.leading)
                Spacer()
                if revealed && isCorrect { Image(systemName: "checkmark.circle.fill").foregroundColor(.green) }
                if revealed && selected && !isCorrect { Image(systemName: "xmark.circle.fill").foregroundColor(.red) }
            }
            .padding(16).background(background)
            .overlay(RoundedRectangle(cornerRadius: 12).stroke(border, lineWidth: 1.5)).cornerRadius(12)
        }.disabled(gameManager.showReveal)
    }

    private func revealSection(question: MannaQuestion, localized: LocalizedQuestionContent?) -> some View {
        let selected = gameManager.selectedAnswerIndex ?? -1
        let correctText = localized?.options[safe: question.correctIndex] ?? question.correct
        return VStack(spacing: 12) {
            MannaText("Question #\(question.number)")
                .font(.system(size: 12, weight: .bold)).foregroundColor(.white.opacity(0.5))
            MannaText(selected == question.correctIndex ? "✅ Correct!" : "❌ Not correct")
                .font(.system(size: 16, weight: .bold))
                .foregroundColor(selected == question.correctIndex ? .green : .red)
            Text("✅ \(correctText)").font(.system(size: 14, weight: .semibold)).foregroundColor(.green.opacity(0.9))
            let explanation = localized?.explanation ?? question.explanation
            if !explanation.isEmpty {
                Text(explanation).font(.system(size: 13)).foregroundColor(.white.opacity(0.55))
                    .multilineTextAlignment(.leading)
            }
        }.padding(16).background(Color.white.opacity(0.05)).cornerRadius(12).padding(.horizontal, 16)
    }

    private func advance(from question: MannaQuestion) {
        DiagnosticRecorder.shared.record("next_pressed question=\(question.number) revealed=\(gameManager.showReveal)")
        gameManager.finalizeCurrentAnswer()
        if let result = gameManager.roundResults.last, result.question.id == question.id {
            performanceTracker.recordAnswer(category: question.category, difficulty: question.difficulty, correct: result.playerAnswer.isCorrect)
        }
        let sessionIsComplete = gameManager.currentRoundNumber >= gameManager.questionsPerSession
        monetization.recordRegularAnswer(sessionIsComplete: sessionIsComplete) {
            gameManager.advanceToNextRound()
        }
    }
}

private extension Array {
    subscript(safe index: Index) -> Element? { indices.contains(index) ? self[index] : nil }
}
