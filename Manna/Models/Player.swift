import Foundation

enum League: String, Codable, CaseIterable {
    case bronze = "Bronze", silver = "Silver", gold = "Gold", platinum = "Platinum", elite = "Elite"
    var minimumScore: Double { switch self { case .bronze:0;case .silver:40;case .gold:55;case .platinum:70;case .elite:85 } }
    var icon: String { switch self { case .bronze:"🥉";case .silver:"🥈";case .gold:"🥇";case .platinum:"💎";case .elite:"👑" } }
}

struct Player: Codable, Identifiable {
    var id: String = UUID().uuidString
    var name: String
    var totalQuestionsAnswered: Int = 0
    var totalCorrect: Int = 0
    var overallScore: Double { guard totalQuestionsAnswered > 0 else { return 0 }; return (Double(totalCorrect)/Double(totalQuestionsAnswered))*100 }
    var currentStreak: Int = 0
    var bestStreak: Int = 0
}

enum AppState {
    case splash, home, categorySelection, playing, result, performance, settings, lumina
}

enum GameMode { case casual, competitive, elite, daily }
