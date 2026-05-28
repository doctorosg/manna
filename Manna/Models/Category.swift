import SwiftUI

// MARK: - Manna Category

struct MannaCategory: Identifiable, Codable, Hashable {
    let id: String
    let name: String
    let emoji: String
    let description: String
    let colorHex: String

    var color: Color {
        Color(hex: colorHex) ?? .blue
    }

    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }

    static func == (lhs: MannaCategory, rhs: MannaCategory) -> Bool {
        lhs.id == rhs.id
    }
}

// MARK: - All 21 Categories

extension MannaCategory {
    static let all: [MannaCategory] = [
        MannaCategory(id: "genesis",        name: "Genesis & Creation",            emoji: "🌍", description: "Creation, the Fall, the patriarchs, and Israel's origins",       colorHex: "#1D9E75"),
        MannaCategory(id: "exodus",         name: "Moses & the Exodus",            emoji: "🔥", description: "Plagues, the Red Sea, Sinai, and the wilderness wanderings",     colorHex: "#BA7517"),
        MannaCategory(id: "kings",          name: "Kings & Kingdoms",              emoji: "👑", description: "Saul, David, Solomon, and the divided monarchy",                 colorHex: "#D85A30"),
        MannaCategory(id: "prophets",       name: "Prophets",                      emoji: "📜", description: "Isaiah, Jeremiah, Ezekiel, Daniel, and the twelve minor prophets",colorHex: "#534AB7"),
        MannaCategory(id: "psalms",         name: "Psalms & Proverbs",             emoji: "🎵", description: "Songs, wisdom sayings, and the poetry of Israel",                colorHex: "#378ADD"),
        MannaCategory(id: "jesus",          name: "Life of Jesus",                 emoji: "✝️", description: "Birth, ministry, teachings, death, and resurrection",             colorHex: "#E24B4A"),
        MannaCategory(id: "miracles",       name: "Miracles",                      emoji: "✨", description: "Supernatural acts of God from Genesis to Acts",                   colorHex: "#1D9E75"),
        MannaCategory(id: "parables",       name: "Parables",                      emoji: "🌱", description: "Jesus' stories and their deeper spiritual lessons",              colorHex: "#639922"),
        MannaCategory(id: "apostles",       name: "The Apostles",                  emoji: "⛵", description: "The twelve, Pentecost, and the early church in Acts",             colorHex: "#0F6E56"),
        MannaCategory(id: "paul",           name: "Paul & His Letters",            emoji: "✉️", description: "Conversion, missionary journeys, and the epistles",               colorHex: "#854F0B"),
        MannaCategory(id: "revelation",     name: "Revelation & End Times",        emoji: "🔮", description: "Apocalyptic visions, the seven churches, and God's final victory",colorHex: "#7F77DD"),
        MannaCategory(id: "women",          name: "Women of the Bible",            emoji: "👩", description: "Eve to Priscilla — the women who shaped Scripture",              colorHex: "#D4537E"),
        MannaCategory(id: "battles",        name: "Battles & Wars",                emoji: "⚔️", description: "Jericho, David and Goliath, the judges, and Israel's conflicts",  colorHex: "#993C1D"),
        MannaCategory(id: "angels",         name: "Angels & Demons",               emoji: "😇", description: "Heavenly beings, spiritual warfare, and the fallen",             colorHex: "#5F5E5A"),
        MannaCategory(id: "laws",           name: "Laws & Commandments",           emoji: "📋", description: "The Ten Commandments, Torah, and Jesus' teaching on the Law",     colorHex: "#791F1F"),
        MannaCategory(id: "prophecy",       name: "Prophecy & Fulfillment",        emoji: "🎯", description: "OT predictions and their NT fulfillment in Christ",              colorHex: "#A32D2D"),
        MannaCategory(id: "places",         name: "Places & Lands",                emoji: "🗺️", description: "Jerusalem, Babylon, Galilee, and the lands of the Bible",         colorHex: "#3B6D11"),
        MannaCategory(id: "numbers",        name: "Numbers & Genealogies",         emoji: "🔢", description: "Ages, tribes, counts, and the family lines of Scripture",         colorHex: "#888780"),
        MannaCategory(id: "food",           name: "Food, Feasts & Offerings",      emoji: "🍞", description: "Manna, Passover, sacrifices, and the meals of the Bible",         colorHex: "#BA7517"),
        MannaCategory(id: "dreams",         name: "Dreams & Visions",              emoji: "💭", description: "Joseph's dreams, Daniel's visions, and prophetic revelations",    colorHex: "#534AB7"),
        MannaCategory(id: "jesusot",        name: "Words of Jesus & OT Roots",     emoji: "📖", description: "How Jesus' words connect to Old Testament passages",             colorHex: "#D85A30"),
    ]

    // MARK: - Name-based lookup (for matching question JSON)

    static func byName(_ name: String) -> MannaCategory? {
        all.first { $0.name.localizedCaseInsensitiveCompare(name) == .orderedSame }
    }
}

// MARK: - Color from Hex

extension Color {
    init?(hex: String) {
        var hexSanitized = hex.trimmingCharacters(in: .whitespacesAndNewlines)
        hexSanitized = hexSanitized.replacingOccurrences(of: "#", with: "")

        var rgb: UInt64 = 0
        guard Scanner(string: hexSanitized).scanHexInt64(&rgb) else { return nil }

        let r = Double((rgb & 0xFF0000) >> 16) / 255.0
        let g = Double((rgb & 0x00FF00) >> 8) / 255.0
        let b = Double(rgb & 0x0000FF) / 255.0

        self.init(red: r, green: g, blue: b)
    }
}
