import Foundation

class QuestionCache {
    static let shared = QuestionCache()

    // MARK: - Storage
    private(set) var cachedQuestions: [MannaQuestion] = []
    private var seenIds: Set<String> = []
    private let seenKey = "manna_seen_question_ids"

    private init() {
        loadSeenIds()
    }

    // MARK: - Add to Cache

    func addToCache(_ questions: [MannaQuestion]) {
        let existingIds = Set(cachedQuestions.map { $0.id })
        let newQuestions = questions.filter { !existingIds.contains($0.id) }
        cachedQuestions.append(contentsOf: newQuestions)
    }

    // MARK: - Seen Tracking

    func hasSeen(_ id: String) -> Bool {
        seenIds.contains(id)
    }

    func markSeen(_ id: String) {
        seenIds.insert(id)
        saveSeenIds()
    }

    func resetSeen(forCategory category: String) {
        let categoryIds = Set(cachedQuestions.filter { $0.category == category }.map { $0.id })
        seenIds.subtract(categoryIds)
        saveSeenIds()
    }

    func resetAllSeen() {
        seenIds.removeAll()
        saveSeenIds()
    }

    // MARK: - Filtered Queries

    func unseenQuestions(categories: [String], difficulty: String? = nil) -> [MannaQuestion] {
        cachedQuestions.filter { q in
            categories.contains(q.category) &&
            !seenIds.contains(q.id) &&
            (difficulty == nil || q.difficulty == difficulty)
        }
    }

    func unseenQuestions(categories: [String]) -> [MannaQuestion] {
        cachedQuestions.filter { q in
            categories.contains(q.category) && !seenIds.contains(q.id)
        }
    }

    var unseenCount: Int {
        cachedQuestions.filter { !seenIds.contains($0.id) }.count
    }

    var stats: String {
        "Total: \(cachedQuestions.count), Seen: \(seenIds.count), Unseen: \(unseenCount)"
    }

    // MARK: - Persistence

    private func loadSeenIds() {
        if let saved = UserDefaults.standard.array(forKey: seenKey) as? [String] {
            seenIds = Set(saved)
        }
    }

    private func saveSeenIds() {
        UserDefaults.standard.set(Array(seenIds), forKey: seenKey)
    }

    func checkAndReplenish() {
        // For now, all questions are bundled. Future: fetch from server.
        print("📦 Cache: \(stats)")
    }
}
