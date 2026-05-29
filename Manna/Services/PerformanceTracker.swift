import Foundation

// MARK: - Performance Record

struct CategoryPerformance: Codable, Identifiable {
    var id: String { category }
    let category: String
    var totalAnswered: Int = 0
    var totalCorrect: Int = 0
    var recentAnswered: Int = 0     // last 20 questions
    var recentCorrect: Int = 0
    var previousScore: Double = 0   // for trend
    
    var score: Double {
        guard totalAnswered > 0 else { return 0 }
        return (Double(totalCorrect) / Double(totalAnswered)) * 100
    }
    
    var recentScore: Double {
        guard recentAnswered > 0 else { return score }
        return (Double(recentCorrect) / Double(recentAnswered)) * 100
    }
    
    var trend: Trend {
        guard totalAnswered >= 5 else { return .neutral }
        let diff = recentScore - previousScore
        if diff > 5 { return .improving }
        if diff < -5 { return .declining }
        return .neutral
    }
}

struct DifficultyPerformance: Codable, Identifiable {
    var id: String { difficulty }
    let difficulty: String
    var totalAnswered: Int = 0
    var totalCorrect: Int = 0
    
    var score: Double {
        guard totalAnswered > 0 else { return 0 }
        return (Double(totalCorrect) / Double(totalAnswered)) * 100
    }
}

enum Trend: String, Codable {
    case improving = "Improving"
    case declining = "Declining"
    case neutral = "Steady"
    
    var icon: String {
        switch self {
        case .improving: return "arrow.up.right"
        case .declining: return "arrow.down.right"
        case .neutral: return "arrow.right"
        }
    }
    
    var color: String {
        switch self {
        case .improving: return "green"
        case .declining: return "red"
        case .neutral: return "gray"
        }
    }
}

// MARK: - Study Suggestion

struct StudySuggestion: Identifiable {
    let id = UUID()
    let category: String
    let emoji: String
    let title: String
    let detail: String
    let priority: Int   // 1=high, 3=low
}

// MARK: - Performance Tracker

class PerformanceTracker: ObservableObject {
    @Published var categoryStats: [String: CategoryPerformance] = [:]
    @Published var difficultyStats: [String: DifficultyPerformance] = [:]
    @Published var totalGames: Int = 0
    @Published var totalQuestions: Int = 0
    @Published var totalCorrect: Int = 0
    @Published var bestStreak: Int = 0
    @Published var currentStreak: Int = 0
    
    private let storageKey = "manna_performance"
    
    init() {
        load()
    }
    
    // MARK: - Record a Round
    
    func recordAnswer(category: String, difficulty: String, correct: Bool) {
        // Category stats
        var cat = categoryStats[category] ?? CategoryPerformance(category: category)
        cat.previousScore = cat.recentScore
        cat.totalAnswered += 1
        cat.recentAnswered = min(cat.recentAnswered + 1, 20)
        if correct {
            cat.totalCorrect += 1
            cat.recentCorrect = min(cat.recentCorrect + 1, 20)
        }
        // Keep recent window at 20
        if cat.recentAnswered >= 20 {
            cat.recentAnswered = 20
            cat.recentCorrect = Int(cat.recentScore / 100.0 * 20)
        }
        categoryStats[category] = cat
        
        // Difficulty stats
        var diff = difficultyStats[difficulty] ?? DifficultyPerformance(difficulty: difficulty)
        diff.totalAnswered += 1
        if correct { diff.totalCorrect += 1 }
        difficultyStats[difficulty] = diff
        
        // Overall
        totalQuestions += 1
        if correct {
            totalCorrect += 1
            currentStreak += 1
            if currentStreak > bestStreak { bestStreak = currentStreak }
        } else {
            currentStreak = 0
        }
        
        save()
    }
    
    func recordGameComplete() {
        totalGames += 1
        save()
    }
    
    // MARK: - Computed Properties
    
    var overallScore: Double {
        guard totalQuestions > 0 else { return 0 }
        return (Double(totalCorrect) / Double(totalQuestions)) * 100
    }
    
    var sortedCategories: [CategoryPerformance] {
        categoryStats.values.sorted { $0.score < $1.score }
    }
    
    var weakestCategories: [CategoryPerformance] {
        categoryStats.values
            .filter { $0.totalAnswered >= 3 }
            .sorted { $0.score < $1.score }
    }
    
    var strongestCategories: [CategoryPerformance] {
        categoryStats.values
            .filter { $0.totalAnswered >= 3 }
            .sorted { $0.score > $1.score }
    }
    
    // MARK: - Study Suggestions
    
    func generateSuggestions() -> [StudySuggestion] {
        var suggestions: [StudySuggestion] = []
        
        let weak = weakestCategories.prefix(5)
        
        let categoryTips: [String: (emoji: String, tips: [String])] = [
            "Genesis & Creation": ("🌍", [
                "Reread Genesis 1-3 and focus on the order of creation and the Fall.",
                "Study the patriarchs: Abraham, Isaac, Jacob, and Joseph — know their family tree.",
                "Focus on the covenant promises God made to Abraham in Genesis 12, 15, and 17."
            ]),
            "Moses & the Exodus": ("🔥", [
                "Review the 10 plagues in order (Exodus 7-12) — know which ones the magicians could copy.",
                "Reread the story of the golden calf and focus on who the important characters are and what they do during this event.",
                "Study the Tabernacle layout and the items inside the Ark of the Covenant."
            ]),
            "Kings & Kingdoms": ("👑", [
                "Make a timeline of Saul → David → Solomon → the split. Know why each transition happened.",
                "Study the 'good kings' of Judah: Asa, Jehoshaphat, Hezekiah, Josiah — and what reforms they made.",
                "Know the difference between the northern kingdom (Israel) and southern kingdom (Judah)."
            ]),
            "Prophets": ("📜", [
                "Learn the major vs. minor prophets — it's about book length, not importance.",
                "Study Jonah, Daniel, Isaiah, and Jeremiah first — they're the most commonly tested.",
                "Know which prophet spoke to which kingdom and when."
            ]),
            "Psalms & Proverbs": ("🎵", [
                "Memorize key psalms: 1, 22, 23, 51, 91, 100, 119, 139 — know their themes.",
                "Study Proverbs themes: wisdom vs. folly, the tongue, money, friendship.",
                "Know who wrote which psalms — David wrote most, but Moses wrote Psalm 90."
            ]),
            "Life of Jesus": ("✝️", [
                "Study the birth narrative in Matthew 1-2 and Luke 1-2 — they tell different details.",
                "Know the 7 'I AM' statements in John's Gospel.",
                "Review the Passion narrative: Last Supper → Gethsemane → trials → crucifixion → resurrection."
            ]),
            "Miracles": ("✨", [
                "List Jesus' miracles by category: nature, healing, raising the dead, exorcism.",
                "Know which miracles appear in all four Gospels (only feeding the 5,000 and the resurrection).",
                "Study Elijah and Elisha's miracles — Elisha performed about twice as many."
            ]),
            "Parables": ("🌱", [
                "Know the three 'lost' parables in Luke 15: sheep, coin, and son — same theme.",
                "Study parables unique to Matthew (talents, sheep/goats) vs. Luke (Good Samaritan, Prodigal Son).",
                "For each parable, know: who is the audience, what's the main point, where is it found."
            ]),
            "The Apostles": ("⛵", [
                "Learn each apostle's background: fishermen, tax collector, zealot, etc.",
                "Study Acts 1-8 closely: Pentecost, early church, Stephen's martyrdom, Philip.",
                "Know the difference between James (son of Zebedee) and James (brother of Jesus)."
            ]),
            "Paul & His Letters": ("✉️", [
                "Make a timeline of Paul's life: Pharisee → conversion → 3 journeys → prison → Rome.",
                "Know which letters Paul wrote from prison (Ephesians, Philippians, Colossians, Philemon).",
                "Study the key themes: Romans (justification), Galatians (freedom), 1 Cor 13 (love)."
            ]),
            "Revelation & End Times": ("🔮", [
                "Learn the structure: 7 churches, 7 seals, 7 trumpets, 7 bowls.",
                "Know the main symbols: Lamb, Dragon, Beast, New Jerusalem, 144,000.",
                "Focus on the messages to the 7 churches — each has praise, criticism, and a promise."
            ]),
            "Women of the Bible": ("👩", [
                "Study the women in Jesus' genealogy: Tamar, Rahab, Ruth, Bathsheba, Mary.",
                "Know the judges: Deborah judged Israel; Jael killed Sisera.",
                "Compare Mary and Martha — and know Mary Magdalene is a different person."
            ]),
            "Battles & Wars": ("⚔️", [
                "Know the judges in order and their unique victories: Othniel, Ehud, Deborah, Gideon, Samson.",
                "Study David's military career: Goliath, fleeing Saul, conquering Jerusalem.",
                "Understand the conquest of Canaan: Jericho first, then Ai, then the southern and northern campaigns."
            ]),
            "Angels & Demons": ("😇", [
                "Know the named angels: Michael (archangel), Gabriel (messenger). Others are tradition, not Bible.",
                "Study the difference between seraphim (Isaiah 6) and cherubim (Ezekiel 1).",
                "Review Satan's appearances: Eden, Job, temptation of Jesus, Revelation."
            ]),
            "Laws & Commandments": ("📋", [
                "Memorize the Ten Commandments in order — group them: God (1-4) and people (5-10).",
                "Understand clean vs. unclean laws and why Jesus said they no longer bind Christians.",
                "Study the feasts of Leviticus 23 — each one points forward to Christ."
            ]),
            "Prophecy & Fulfillment": ("🎯", [
                "Study Isaiah 53 and Psalm 22 — they describe the crucifixion in detail centuries before.",
                "Know the key Messianic prophecies: born in Bethlehem (Micah 5), virgin birth (Isaiah 7), riding a donkey (Zechariah 9).",
                "Learn how Jesus quoted the OT during His ministry — He cited Deuteronomy, Psalms, and Isaiah most."
            ]),
            "Places & Lands": ("🗺️", [
                "Learn the geography: Galilee (north), Samaria (middle), Judea (south), Jordan River, Dead Sea.",
                "Know key cities: Jerusalem (Temple), Bethlehem (birth), Nazareth (childhood), Capernaum (ministry base).",
                "Study Paul's missionary journey cities: Antioch, Ephesus, Corinth, Philippi, Thessalonica, Rome."
            ]),
            "Numbers & Genealogies": ("🔢", [
                "Memorize key numbers: 3 (Trinity), 7 (perfection), 12 (tribes/apostles), 40 (testing).",
                "Study Jesus' genealogy in Matthew 1 — note the women included and the structure of 3 × 14 generations.",
                "Know the 12 tribes and their mothers: Leah (6), Rachel (2), Bilhah (2), Zilpah (2)."
            ]),
            "Food, Feasts & Offerings": ("🍞", [
                "Learn the 5 offerings of Leviticus: burnt, grain, peace, sin, guilt — and what each represents.",
                "Study the 7 feasts of Israel and how each connects to Jesus.",
                "Know the kosher rules basics: split hoof + cud = clean; fins + scales = clean."
            ]),
            "Dreams & Visions": ("💭", [
                "Study Joseph's dreams (Genesis 37, 40, 41) — each one came true literally.",
                "Know Daniel's visions: the statue (ch. 2), four beasts (ch. 7), 70 weeks (ch. 9).",
                "Compare Ezekiel's visions (dry bones, wheel, temple) with John's in Revelation."
            ]),
            "Words of Jesus & OT Roots": ("📖", [
                "Study how Jesus quoted the OT during His temptation — all three quotes are from Deuteronomy.",
                "Learn the connections between the Sermon on the Mount and the Law of Moses.",
                "Know which psalms Jesus quoted on the cross: Psalm 22:1 and Psalm 31:5."
            ]),
        ]
        
        for cat in weak {
            let tips = categoryTips[cat.category]
            let emoji = tips?.emoji ?? "📚"
            let tipList = tips?.tips ?? ["Review the key stories and characters in this category."]
            let tip = tipList[min(cat.totalAnswered % tipList.count, tipList.count - 1)]
            
            suggestions.append(StudySuggestion(
                category: cat.category,
                emoji: emoji,
                title: "Improve: \(cat.category)",
                detail: tip,
                priority: cat.score < 40 ? 1 : cat.score < 60 ? 2 : 3
            ))
        }
        
        // Add general suggestions
        if totalQuestions < 50 {
            suggestions.append(StudySuggestion(
                category: "General", emoji: "🎯",
                title: "Keep Playing!",
                detail: "Play at least 50 questions to get accurate performance data and personalized tips.",
                priority: 1))
        }
        
        if let diffStat = difficultyStats["Pastor"], diffStat.score < 40, diffStat.totalAnswered >= 10 {
            suggestions.append(StudySuggestion(
                category: "Difficulty", emoji: "📖",
                title: "Pastor Level is Tough",
                detail: "Try mastering Deacon level first. Strong foundations make harder questions easier.",
                priority: 2))
        }
        
        return suggestions.sorted { $0.priority < $1.priority }
    }
    
    // MARK: - Persistence
    
    private func save() {
        let data: [String: Any] = [
            "categories": (try? JSONEncoder().encode(Array(categoryStats.values))).flatMap { String(data: $0, encoding: .utf8) } ?? "[]",
            "difficulties": (try? JSONEncoder().encode(Array(difficultyStats.values))).flatMap { String(data: $0, encoding: .utf8) } ?? "[]",
            "totalGames": totalGames,
            "totalQuestions": totalQuestions,
            "totalCorrect": totalCorrect,
            "bestStreak": bestStreak,
        ]
        UserDefaults.standard.set(data, forKey: storageKey)
    }
    
    private func load() {
        guard let data = UserDefaults.standard.dictionary(forKey: storageKey) else { return }
        
        if let catJson = data["categories"] as? String, let catData = catJson.data(using: .utf8) {
            if let cats = try? JSONDecoder().decode([CategoryPerformance].self, from: catData) {
                categoryStats = Dictionary(uniqueKeysWithValues: cats.map { ($0.category, $0) })
            }
        }
        if let diffJson = data["difficulties"] as? String, let diffData = diffJson.data(using: .utf8) {
            if let diffs = try? JSONDecoder().decode([DifficultyPerformance].self, from: diffData) {
                difficultyStats = Dictionary(uniqueKeysWithValues: diffs.map { ($0.difficulty, $0) })
            }
        }
        totalGames = data["totalGames"] as? Int ?? 0
        totalQuestions = data["totalQuestions"] as? Int ?? 0
        totalCorrect = data["totalCorrect"] as? Int ?? 0
        bestStreak = data["bestStreak"] as? Int ?? 0
    }
    
    func resetAll() {
        categoryStats = [:]
        difficultyStats = [:]
        totalGames = 0
        totalQuestions = 0
        totalCorrect = 0
        bestStreak = 0
        currentStreak = 0
        UserDefaults.standard.removeObject(forKey: storageKey)
    }
}
