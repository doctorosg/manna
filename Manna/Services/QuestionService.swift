import Foundation

class QuestionService {

    // MARK: - Properties
    private var availableQuestions: [MannaQuestion] = []
    private let cache = QuestionCache.shared

    private var sessionCategories: [String] = []
    private var sessionDifficulty: String = ""

    // MARK: - Load from Bundle

    func loadQuestions() async {
        if cache.cachedQuestions.isEmpty {
            guard let url = Bundle.main.url(forResource: "manna_questions", withExtension: "json") else {
                print("⚠️ manna_questions.json not found in bundle")
                return
            }

            do {
                let data = try Data(contentsOf: url)
                let decoder = JSONDecoder()
                let questions = try decoder.decode([MannaQuestion].self, from: data)
                cache.addToCache(questions)
                print("✅ Loaded \(questions.count) questions from bundle")
            } catch {
                print("❌ Failed to load questions: \(error)")
            }
        } else {
            print("✅ Cache already has \(cache.cachedQuestions.count) questions")
        }
    }

    // MARK: - Session Setup

    func prepareSession(categories: [String], difficulty: String) {
        sessionCategories = categories
        sessionDifficulty = difficulty
        applySessionFilter()
    }

    private func applySessionFilter() {
        // Step 1: Exact match — unseen, right categories, right difficulty
        var filtered = cache.unseenQuestions(categories: sessionCategories, difficulty: sessionDifficulty)

        // Step 2: If not enough, use adjacent difficulties
        if filtered.count < 5 {
            let diffLevels: [String]
            switch sessionDifficulty {
            case "Layperson": diffLevels = ["Layperson", "Deacon"]
            case "Pastor": diffLevels = ["Pastor", "Deacon"]
            default: diffLevels = ["Deacon", "Layperson", "Pastor"]
            }
            let nearby = cache.cachedQuestions.filter { q in
                sessionCategories.contains(q.category) &&
                diffLevels.contains(q.difficulty) &&
                !cache.hasSeen(q.id)
            }
            if nearby.count > filtered.count { filtered = nearby }
        }

        // Step 3: Any unseen from selected categories
        if filtered.count < 5 {
            let allUnseen = cache.unseenQuestions(categories: sessionCategories)
            if allUnseen.count > filtered.count { filtered = allUnseen }
        }

        // Step 4: Reset seen and recycle
        if filtered.isEmpty {
            print("🔄 All questions seen — resetting for these categories")
            for cat in sessionCategories {
                cache.resetSeen(forCategory: cat)
            }
            filtered = cache.unseenQuestions(categories: sessionCategories, difficulty: sessionDifficulty)
            if filtered.isEmpty {
                filtered = cache.cachedQuestions.filter { sessionCategories.contains($0.category) }
            }
        }

        availableQuestions = filtered.shuffled()
        print("🎯 Session pool: \(availableQuestions.count) questions (\(cache.stats))")
    }

    // MARK: - Fetch Next

    func nextQuestion() -> MannaQuestion? {
        if availableQuestions.isEmpty && !sessionCategories.isEmpty {
            applySessionFilter()
        }

        guard !availableQuestions.isEmpty else { return nil }

        let index = Int.random(in: 0..<availableQuestions.count)
        let question = availableQuestions.remove(at: index)
        cache.markSeen(question.id)
        return question
    }

    // MARK: - Helpers

    var totalQuestionCount: Int { cache.cachedQuestions.count }
    var unseenCount: Int { cache.unseenCount }
}
