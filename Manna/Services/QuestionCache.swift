import Foundation

class QuestionCache {
    static let shared = QuestionCache()

    private(set) var cachedQuestions: [MannaQuestion] = []
    private var seenIds: Set<String> = []
    private var correctIds: Set<String> = []    // Questions answered correctly — remove from pool
    private var wrongIds: Set<String> = []      // Questions answered wrong — refeed into pool
    private let seenKey = "manna_seen_question_ids"
    private let correctKey = "manna_correct_question_ids"
    private let wrongKey = "manna_wrong_question_ids"

    private init() {
        loadData()
    }

    func addToCache(_ questions: [MannaQuestion]) {
        let existingIds = Set(cachedQuestions.map { $0.id })
        let newQuestions = questions.filter { !existingIds.contains($0.id) }
        cachedQuestions.append(contentsOf: newQuestions)
    }

    // MARK: - Tracking

    func markCorrect(_ id: String) {
        correctIds.insert(id)
        wrongIds.remove(id)
        seenIds.insert(id)
        saveData()
    }

    func markPresented(_ id: String) {
        seenIds.insert(id)
        saveData()
    }

    func markWrong(_ id: String) {
        wrongIds.insert(id)
        seenIds.insert(id)
        // Do NOT add to correctIds — keep it in the pool
        saveData()
    }

    func hasSeen(_ id: String) -> Bool { seenIds.contains(id) }
    func isCorrect(_ id: String) -> Bool { correctIds.contains(id) }

    // MARK: - Smart Question Selection
    // Strict deck: present every eligible question once before any repeat.

    func smartQuestions(categories: [String], difficulty: String? = nil) -> [MannaQuestion] {
        let categoryFiltered = cachedQuestions.filter { q in
            q.ageGroup == nil &&
            categories.contains(q.category) &&
            (difficulty == nil || q.difficulty == difficulty)
        }

        let unseen = categoryFiltered.filter { !seenIds.contains($0.id) }
        if !unseen.isEmpty { return ordered(unseen, difficulty: difficulty) }

        // Every currently eligible question has been presented. Start a new cycle
        // without erasing correctness history.
        let eligibleIds = Set(categoryFiltered.map(\.id))
        seenIds.subtract(eligibleIds)
        saveData()
        return ordered(categoryFiltered, difficulty: difficulty)
    }

    func childrenQuestions(ageGroup: String) -> [MannaQuestion] {
        let eligible = cachedQuestions.filter { $0.ageGroup == ageGroup }
        let unseen = eligible.filter { !seenIds.contains($0.id) }
        if !unseen.isEmpty { return unseen.shuffled() }
        seenIds.subtract(Set(eligible.map(\.id)))
        saveData()
        return eligible.shuffled()
    }

    func resetSeen(forCategories categories: [String]) {
        let catIds = Set(cachedQuestions.filter { categories.contains($0.category) }.map { $0.id })
        seenIds.subtract(catIds)
        correctIds.subtract(catIds)
        wrongIds.subtract(catIds)
        saveData()
    }

    func resetSeen(forCategory category: String) {
        resetSeen(forCategories: [category])
    }

    func resetAllSeen() {
        seenIds.removeAll(); correctIds.removeAll(); wrongIds.removeAll()
        saveData()
    }

    var unseenCount: Int { cachedQuestions.filter { !seenIds.contains($0.id) }.count }
    var wrongCount: Int { wrongIds.count }
    var stats: String { "Total: \(cachedQuestions.count), Seen: \(seenIds.count), Wrong: \(wrongIds.count), Correct: \(correctIds.count)" }

    func question(withId id: String) -> MannaQuestion? {
        cachedQuestions.first { $0.id == id }
    }

    func partyQuestions(category: String?, difficulty: String, count: Int) -> [MannaQuestion] {
        let eligible = cachedQuestions.filter { question in
            question.ageGroup == nil &&
            (category == nil || question.category == category) && question.difficulty == difficulty
        }
        return ordered(eligible, difficulty: difficulty).prefix(count).map { $0 }
    }

    func partyQuestions(ageGroup: String, count: Int) -> [MannaQuestion] {
        cachedQuestions.filter { $0.ageGroup == ageGroup }.shuffled().prefix(count).map { $0 }
    }

    // MARK: - Persistence
    private func loadData() {
        seenIds = Set(UserDefaults.standard.array(forKey: seenKey) as? [String] ?? [])
        correctIds = Set(UserDefaults.standard.array(forKey: correctKey) as? [String] ?? [])
        wrongIds = Set(UserDefaults.standard.array(forKey: wrongKey) as? [String] ?? [])
    }
    private func saveData() {
        UserDefaults.standard.set(Array(seenIds), forKey: seenKey)
        UserDefaults.standard.set(Array(correctIds), forKey: correctKey)
        UserDefaults.standard.set(Array(wrongIds), forKey: wrongKey)
    }

    func checkAndReplenish() { print("📦 Cache: \(stats)") }

    private func ordered(_ questions: [MannaQuestion], difficulty: String?) -> [MannaQuestion] {
        if difficulty == DifficultyLevel.pastor.name {
            return PastorSessionBalancer.balanced(questions)
        }
        return questions.shuffled()
    }
}
