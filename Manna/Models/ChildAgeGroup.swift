import SwiftUI

enum PlayAudience: String, CaseIterable, Identifiable {
    case adults = "Adults"
    case children = "Children"

    var id: String { rawValue }
}

enum ChildAgeGroup: String, Codable, CaseIterable, Identifiable {
    case ages4to10 = "4-10"
    case ages11to17 = "11-17"

    var id: String { rawValue }

    var shortLabel: String {
        switch self {
        case .ages4to10: "4–10"
        case .ages11to17: "11–17"
        }
    }

    var title: String { "Ages \(shortLabel)" }

    var emoji: String {
        switch self {
        case .ages4to10: "🌱"
        case .ages11to17: "🧭"
        }
    }

    var description: String {
        switch self {
        case .ages4to10: "Familiar Bible stories with three answer choices"
        case .ages11to17: "Bible stories, passages, and deeper knowledge with four answer choices"
        }
    }

    var answerChoiceCount: Int {
        switch self {
        case .ages4to10: 3
        case .ages11to17: 4
        }
    }

    var questionCount: Int {
        switch self {
        case .ages4to10: 3_333
        case .ages11to17: 6_667
        }
    }

    var difficulty: DifficultyLevel {
        switch self {
        case .ages4to10: .layperson
        case .ages11to17: .pastor
        }
    }
}
