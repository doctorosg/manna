import Foundation

// MARK: - Question Model

struct MannaQuestion: Codable, Identifiable {
    let id: String
    let category: String
    let difficulty: String
    let question: String
    let options: [String]
    let correct: String
    let explanation: String

    var correctIndex: Int { options.firstIndex(of: correct) ?? 0 }
    var difficultyLevel: DifficultyLevel { DifficultyLevel.fromString(difficulty) ?? .layperson }
}

// MARK: - Player Answer

struct PlayerAnswer {
    let questionId: String
    let selectedIndex: Int
    let isCorrect: Bool
    let timeUsed: Double
}

// MARK: - Round Result

struct RoundResult {
    let question: MannaQuestion
    let playerAnswer: PlayerAnswer
    let botAnswers: [BotAnswer]
    
    var correctPlayerCount: Int {
        let botCorrect = botAnswers.filter { $0.isCorrect }.count
        return botCorrect + (playerAnswer.isCorrect ? 1 : 0)
    }
}

// MARK: - Bot Answer

struct BotAnswer: Identifiable {
    let id = UUID()
    let botName: String
    let botScore: Double
    let selectedIndex: Int
    let isCorrect: Bool
    let responseTime: Double
}
