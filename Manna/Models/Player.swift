import Foundation

// MARK: - League

enum League: String, Codable, CaseIterable {
    case bronze    = "Bronze"
    case silver    = "Silver"
    case gold      = "Gold"
    case platinum  = "Platinum"
    case elite     = "Elite"

    var minimumScore: Double {
        switch self {
        case .bronze:   return 0
        case .silver:   return 40
        case .gold:     return 55
        case .platinum: return 70
        case .elite:    return 85
        }
    }

    var icon: String {
        switch self {
        case .bronze:   return "🥉"
        case .silver:   return "🥈"
        case .gold:     return "🥇"
        case .platinum: return "💎"
        case .elite:    return "👑"
        }
    }
}

// MARK: - Player

struct Player: Codable, Identifiable {
    var id: String = UUID().uuidString
    var name: String
    var totalQuestionsAnswered: Int = 0
    var totalCorrect: Int = 0
    var overallScore: Double {
        guard totalQuestionsAnswered > 0 else { return 0 }
        return (Double(totalCorrect) / Double(totalQuestionsAnswered)) * 100
    }
    var tokens: Int = 1000
    var league: League = .bronze
    var currentStreak: Int = 0
    var bestStreak: Int = 0
    var seenQuestionIds: [String] = []
}

// MARK: - Leaderboard Entry

struct LeaderboardEntry: Identifiable {
    let id: String
    let rank: Int
    let playerName: String
    let totalTokens: Int
    let weeklyDelta: Int
    let overallScore: Double
    let league: League
}

// MARK: - App State

enum AppState {
    case splash
    case home
    case categorySelection
    case playing
    case result
    case leaderboard
    case settings
    case tokenShop
}

// MARK: - Game Mode

enum GameMode {
    case casual
    case competitive
    case elite
    case daily
}
