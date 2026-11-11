import Foundation

class QuestionService {
    private var availableQuestions: [MannaQuestion] = []
    private let cache = QuestionCache.shared
    private var sessionCategories: [String] = []
    private var sessionDifficulty: String = ""
    private var sessionAgeGroup: String?

    func loadQuestions() async {
        if cache.cachedQuestions.isEmpty {
            guard let url = Bundle.main.url(forResource: "manna_questions", withExtension: "json") else {
                print("⚠️ manna_questions.json not found in bundle"); return
            }
            do {
                let data = try Data(contentsOf: url)
                let questions = try JSONDecoder().decode([MannaQuestion].self, from: data)
                cache.addToCache(questions)
                cache.addToCache(QuestionPackStore.loadInstalledQuestions())
                print("✅ Loaded \(questions.count) questions from bundle")
            } catch { print("❌ Failed to load questions: \(error)") }
        }
    }

    func prepareSession(categories: [String], difficulty: String) {
        sessionCategories = categories
        sessionDifficulty = difficulty
        sessionAgeGroup = nil
        availableQuestions = cache.smartQuestions(categories: categories, difficulty: difficulty)
        print("🎯 Session pool: \(availableQuestions.count) questions (\(cache.stats))")
    }

    func prepareChildrenSession(ageGroup: ChildAgeGroup) {
        sessionCategories = []
        sessionDifficulty = ageGroup.difficulty.name
        sessionAgeGroup = ageGroup.rawValue
        availableQuestions = cache.childrenQuestions(ageGroup: ageGroup.rawValue)
        print("🧒 Children session pool: \(availableQuestions.count) questions (\(ageGroup.title))")
    }

    func nextQuestion() -> MannaQuestion? {
        if availableQuestions.isEmpty {
            if let sessionAgeGroup {
                availableQuestions = cache.childrenQuestions(ageGroup: sessionAgeGroup)
            } else if !sessionCategories.isEmpty {
                availableQuestions = cache.smartQuestions(categories: sessionCategories, difficulty: sessionDifficulty)
            }
        }
        guard !availableQuestions.isEmpty else { return nil }
        let question = availableQuestions.removeFirst()
        cache.markPresented(question.id)
        return question
    }

    func markCorrect(_ id: String) { cache.markCorrect(id) }
    func markWrong(_ id: String) { cache.markWrong(id) }

    var totalQuestionCount: Int { cache.cachedQuestions.count }
    var unseenCount: Int { cache.unseenCount }

    func question(withId id: String) -> MannaQuestion? { cache.question(withId: id) }

    func partyQuestions(category: String?, difficulty: String, count: Int) -> [MannaQuestion] {
        cache.partyQuestions(category: category, difficulty: difficulty, count: count)
    }

    func partyQuestions(ageGroup: ChildAgeGroup, count: Int) -> [MannaQuestion] {
        cache.partyQuestions(ageGroup: ageGroup.rawValue, count: count)
    }
}
