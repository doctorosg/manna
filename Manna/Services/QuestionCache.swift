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

    func markWrong(_ id: String) {
        wrongIds.insert(id)
        seenIds.insert(id)
        // Do NOT add to correctIds — keep it in the pool
        saveData()
    }

    func hasSeen(_ id: String) -> Bool { seenIds.contains(id) }
    func isCorrect(_ id: String) -> Bool { correctIds.contains(id) }

    // MARK: - Smart Question Selection
    // Priority: 1) Previously wrong questions, 2) Unseen questions, 3) All remaining

    func smartQuestions(categories: [String], difficulty: String? = nil) -> [MannaQuestion] {
        let categoryFiltered = cachedQuestions.filter { q in
            categories.contains(q.category) &&
            (difficulty == nil || q.difficulty == difficulty)
        }

        // First priority: questions they got wrong before (refeed)
        let wrongOnes = categoryFiltered.filter { wrongIds.contains($0.id) }

        // Second priority: never seen
        let unseenOnes = categoryFiltered.filter { !seenIds.contains($0.id) }

        // Third: seen but not correctly answered
        let remaining = categoryFiltered.filter { !correctIds.contains($0.id) && !wrongIds.contains($0.id) }

        // Mix: 40% wrong (refeed), 40% unseen, 20% remaining
        var pool: [MannaQuestion] = []
        pool.append(contentsOf: wrongOnes.shuffled())
        pool.append(contentsOf: unseenOnes.shuffled())
        pool.append(contentsOf: remaining.shuffled())

        // If pool is empty, reset and use everything
        if pool.isEmpty {
            resetSeen(forCategories: categories)
            return categoryFiltered.shuffled()
        }

        return pool
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
}
