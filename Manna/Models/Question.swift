import Foundation

// MARK: - Question Model (matches manna_questions.json format)

struct MannaQuestion: Codable, Identifiable {
    let id: String
    let category: String
    let difficulty: String        // "Layperson", "Deacon", "Pastor"
    let question: String
    let options: [String]         // 4 answer choices
    let correct: String           // correct answer text
    let explanation: String

    // Computed: index of correct answer
    var correctIndex: Int {
        options.firstIndex(of: correct) ?? 0
    }

    var difficultyLevel: DifficultyLevel {
        DifficultyLevel.fromString(difficulty) ?? .layperson
    }

    var baseTokenReward: Int {
        difficultyLevel.tokenReward
    }

    var difficultyInt: Int {
        difficultyLevel.rawValue
    }
}

// MARK: - Player Answer

struct PlayerAnswer {
    let questionId: String
    let selectedIndex: Int
    let isCorrect: Bool
    let timeUsed: Double        // seconds taken
    let wagerAmount: Int
    let wagerType: WagerType
}

// MARK: - Wager Types

enum WagerType: String, Codable, CaseIterable, Hashable {
    case none       = "None"
    case standard   = "Standard"
    case win        = "Win"        // Only correct player
    case place      = "Place"      // One of two correct
    case show       = "Show"       // One of three correct

    var multiplier: Double {
        switch self {
        case .none:     return 0
        case .standard: return 1.0
        case .win:      return 4.0
        case .place:    return 2.5
        case .show:     return 1.5
        }
    }

    var label: String {
        switch self {
        case .none:     return "No Wager"
        case .standard: return "Standard"
        case .win:      return "WIN — Only me"
        case .place:    return "PLACE — One of two"
        case .show:     return "SHOW — One of three"
        }
    }
}

// MARK: - Round Result

struct RoundResult {
    let question: MannaQuestion
    let playerAnswer: PlayerAnswer
    let botAnswers: [BotAnswer]
    let tokensEarned: Int
    let tokensLost: Int

    var netTokenChange: Int { tokensEarned - tokensLost }

    var correctPlayerCount: Int {
        let botCorrect = botAnswers.filter { $0.isCorrect }.count
        let playerCorrect = playerAnswer.isCorrect ? 1 : 0
        return botCorrect + playerCorrect
    }
}

// MARK: - Bot Answer

struct BotAnswer: Identifiable {
    let id = UUID()
    let botName: String
    let botScore: Double
    let selectedIndex: Int
    let isCorrect: Bool
    let wagerAmount: Int
    let wagerType: WagerType
    let responseTime: Double
}
