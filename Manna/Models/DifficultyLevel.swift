import SwiftUI

// MARK: - Difficulty Level

enum DifficultyLevel: Int, CaseIterable, Identifiable, Codable {
    case layperson = 1
    case deacon = 2
    case pastor = 3

    var id: Int { rawValue }

    var name: String {
        switch self {
        case .layperson: return "Layperson"
        case .deacon: return "Deacon"
        case .pastor: return "Pastor"
        }
    }

    var description: String {
        switch self {
        case .layperson: return "Sunday School stories and well-known passages. Anyone can play."
        case .deacon: return "You've read the Bible — but the details trip you up."
        case .pastor: return "Seminary-level. Minor prophets, genealogies, original languages."
        }
    }

    var tokenReward: Int {
        switch self {
        case .layperson: return 10
        case .deacon: return 25
        case .pastor: return 50
        }
    }

    var colorHex: String {
        switch self {
        case .layperson: return "#1D9E75"
        case .deacon: return "#BA7517"
        case .pastor: return "#E24B4A"
        }
    }

    var color: Color {
        Color(hex: colorHex) ?? .blue
    }

    var iconName: String {
        switch self {
        case .layperson: return "book.fill"
        case .deacon: return "text.book.closed.fill"
        case .pastor: return "graduationcap.fill"
        }
    }

    var starCount: Int { rawValue }

    /// Match difficulty string from JSON
    static func fromString(_ s: String) -> DifficultyLevel? {
        switch s.lowercased() {
        case "layperson": return .layperson
        case "deacon": return .deacon
        case "pastor": return .pastor
        default: return nil
        }
    }

    /// The next difficulty level up (for Level Up Challenge)
    var nextLevel: DifficultyLevel? {
        switch self {
        case .layperson: return .deacon
        case .deacon: return .pastor
        case .pastor: return nil
        }
    }
}
