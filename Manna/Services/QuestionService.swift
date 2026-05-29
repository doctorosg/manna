import Foundation

class QuestionService {
    private var availableQuestions: [MannaQuestion] = []
    private let cache = QuestionCache.shared
    private var sessionCategories: [String] = []
    private var sessionDifficulty: String = ""

    func loadQuestions() async {
        if cache.cachedQuestions.isEmpty {
            guard let url = Bundle.main.url(forResource: "manna_questions", withExtension: "json") else {
                print("⚠️ manna_questions.json not found in bundle"); return
            }
            do {
                let data = try Data(contentsOf: url)
                let questions = try JSONDecoder().decode([MannaQuestion].self, from: data)
                cache.addToCache(questions)
                print("✅ Loaded \(questions.count) questions from bundle")
            } catch { print("❌ Failed to load questions: \(error)") }
        }
    }

    func prepareSession(categories: [String], difficulty: String) {
        sessionCategories = categories
        sessionDifficulty = difficulty
        availableQuestions = cache.smartQuestions(categories: categories, difficulty: difficulty)
        if availableQuestions.count < 5 {
            // Broaden: try all difficulties for selected categories
            availableQuestions = cache.smartQuestions(categories: categories)
        }
        print("🎯 Session pool: \(availableQuestions.count) questions (\(cache.stats))")
    }

    func nextQuestion() -> MannaQuestion? {
        guard !availableQuestions.isEmpty else {
            if !sessionCategories.isEmpty {
                availableQuestions = cache.smartQuestions(categories: sessionCategories, difficulty: sessionDifficulty)
            }
            guard !availableQuestions.isEmpty else { return nil }
        }
        return availableQuestions.removeFirst()
    }

    func markCorrect(_ id: String) { cache.markCorrect(id) }
    func markWrong(_ id: String) { cache.markWrong(id) }

    var totalQuestionCount: Int { cache.cachedQuestions.count }
    var unseenCount: Int { cache.unseenCount }
}
