import Foundation
import Combine

class GameManager: ObservableObject {
    @Published var appState: AppState = .home
    @Published var currentQuestion: MannaQuestion?
    @Published var currentRoundNumber: Int = 0
    @Published var roundResults: [RoundResult] = []
    @Published var botOpponents: [BotOpponent] = []
    @Published var timeRemaining: Double = 20.0
    @Published var isTimerRunning: Bool = false
    @Published var selectedAnswerIndex: Int? = nil
    @Published var showReveal: Bool = false
    @Published var timedOut: Bool = false
    @Published var gameMode: GameMode = .competitive
    @Published var sessionComplete: Bool = false
    @Published var currentStreak: Int = 0
    @Published var questionsLoaded: Bool = false

    // Bonus Challenge (was Double or Nothing)
    @Published var showDoubleOrNothing: Bool = false
    @Published var doubleOrNothingQuestion: MannaQuestion? = nil
    @Published var doubleOrNothingActive: Bool = false
    @Published var doubleOrNothingResult: Bool? = nil

    // Level Up Challenge
    @Published var showLevelUpOffer: Bool = false
    @Published var levelUpActive: Bool = false
    @Published var levelUpQuestion: MannaQuestion? = nil
    @Published var levelUpResult: Bool? = nil

    // Session Config
    @Published var selectedCategories: [MannaCategory] = []
    @Published var selectedDifficulty: DifficultyLevel = .deacon

    let questionService = QuestionService()
    private let botService = BotService()
    private var timerCancellable: AnyCancellable?

    let roundTimeLimit: Double = 20.0
    let questionsPerSession: Int = 5

    init() {
        Task { @MainActor in
            await questionService.loadQuestions()
            self.questionsLoaded = true
            print("🍞 Questions loaded: \(questionService.totalQuestionCount)")
        }
    }

    // MARK: - Navigation
    func goToPreGame(mode: GameMode = .competitive) { gameMode = mode; appState = .categorySelection }
    func cancelPreGame() { appState = .home }
    func goHome() { stopTimer(); appState = .home }
    func goToPerformance() { appState = .performance }
    func goToSettings() { appState = .settings }

    // MARK: - Start Session
    func startSession(categories: [MannaCategory], difficulty: DifficultyLevel) {
        selectedCategories = categories
        selectedDifficulty = difficulty
        currentRoundNumber = 0; roundResults = []; sessionComplete = false
        botOpponents = botService.generateOpponents(count: 4, mode: gameMode)
        questionService.prepareSession(categories: categories.map { $0.name }, difficulty: difficulty.name)
        appState = .playing
        loadNextQuestion()
    }

    func loadNextQuestion() {
        guard currentRoundNumber < questionsPerSession else { endSession(); return }
        selectedAnswerIndex = nil; showReveal = false; timedOut = false
        if let question = questionService.nextQuestion() {
            currentQuestion = question; currentRoundNumber += 1; startTimer()
        } else {
            print("⚠️ No questions available!")
            endSession()
        }
    }

    func submitAnswer(index: Int) {
        guard let question = currentQuestion, selectedAnswerIndex == nil else { return }
        stopTimer(); selectedAnswerIndex = index
        let timeUsed = roundTimeLimit - timeRemaining
        let isCorrect = index >= 0 && index == question.correctIndex

        // Track for refeeding
        if isCorrect { questionService.markCorrect(question.id) }
        else { questionService.markWrong(question.id) }

        let playerAnswer = PlayerAnswer(questionId: question.id, selectedIndex: index, isCorrect: isCorrect, timeUsed: timeUsed)
        let botAnswers = botService.simulateAnswers(for: question, bots: botOpponents)
        let result = RoundResult(question: question, playerAnswer: playerAnswer, botAnswers: botAnswers)
        roundResults.append(result)

        if isCorrect { currentStreak += 1; SoundManager.shared.playCorrect() }
        else { currentStreak = 0; SoundManager.shared.playWrong() }

        // If timed out, don't show reveal — auto advance
        if index < 0 {
            timedOut = true
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [weak self] in
                self?.advanceToNextRound()
            }
        } else {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) { [weak self] in self?.showReveal = true }
        }
    }

    func advanceToNextRound() {
        if shouldOfferLevelUp() { offerLevelUp(); return }
        if currentRoundNumber >= questionsPerSession { endSession() } else { loadNextQuestion() }
    }

    // MARK: - Level Up
    private func shouldOfferLevelUp() -> Bool {
        guard !levelUpActive, selectedDifficulty.nextLevel != nil else { return false }
        // Only offer if player is getting 80%+ correct in this session
        let answered = roundResults.count
        let correct = roundResults.filter { $0.playerAnswer.isCorrect }.count
        guard answered >= 3, let last = roundResults.last, last.playerAnswer.isCorrect else { return false }
        let accuracy = Double(correct) / Double(answered)
        return accuracy >= 0.80 && Double.random(in: 0...1) < 0.5
    }
    private func offerLevelUp() {
        guard selectedDifficulty.nextLevel != nil else { return }
        showLevelUpOffer = true
    }
    func acceptLevelUp() {
        guard let next = selectedDifficulty.nextLevel else { return }
        showLevelUpOffer = false; levelUpActive = true; levelUpResult = nil
        questionService.prepareSession(categories: selectedCategories.map { $0.name }, difficulty: next.name)
        if let q = questionService.nextQuestion() { levelUpQuestion = q; timeRemaining = roundTimeLimit; selectedAnswerIndex = nil; startTimer() }
        else { levelUpActive = false; continueAfterLevelUp() }
        questionService.prepareSession(categories: selectedCategories.map { $0.name }, difficulty: selectedDifficulty.name)
    }
    func declineLevelUp() { showLevelUpOffer = false; if currentRoundNumber >= questionsPerSession { endSession() } else { loadNextQuestion() } }
    func submitLevelUpAnswer(index: Int) {
        guard let q = levelUpQuestion, levelUpActive else { return }
        stopTimer(); selectedAnswerIndex = index; levelUpResult = (index >= 0 && index == q.correctIndex)
        if levelUpResult == true { SoundManager.shared.playCorrect() } else { SoundManager.shared.playWrong() }
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) { [weak self] in self?.finalizeLevelUp() }
    }
    private func finalizeLevelUp() { levelUpActive = false; levelUpQuestion = nil; continueAfterLevelUp() }
    private func continueAfterLevelUp() { if currentRoundNumber >= questionsPerSession { endSession() } else { loadNextQuestion() } }

    // MARK: - End Session
    private func endSession() {
        sessionComplete = true; stopTimer(); appState = .result
        let correctCount = roundResults.filter { $0.playerAnswer.isCorrect }.count
        // Offer bonus challenge if player did well (3+ correct)
        if correctCount >= 3 {
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [weak self] in self?.showDoubleOrNothing = true }
        }
    }

    // MARK: - Bonus Challenge
    func acceptDoubleOrNothing() {
        showDoubleOrNothing = false; doubleOrNothingActive = true; doubleOrNothingResult = nil
        if let q = questionService.nextQuestion() { doubleOrNothingQuestion = q; timeRemaining = roundTimeLimit; selectedAnswerIndex = nil; startTimer() }
    }
    func declineDoubleOrNothing() { showDoubleOrNothing = false }
    func submitDoubleOrNothingAnswer(index: Int) {
        guard let q = doubleOrNothingQuestion, doubleOrNothingActive else { return }
        stopTimer(); selectedAnswerIndex = index; doubleOrNothingResult = (index >= 0 && index == q.correctIndex)
        if doubleOrNothingResult == true { SoundManager.shared.playCorrect() } else { SoundManager.shared.playWrong() }
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) { [weak self] in self?.finalizeDoubleOrNothing() }
    }
    private func finalizeDoubleOrNothing() { doubleOrNothingActive = false; doubleOrNothingQuestion = nil }

    // MARK: - Timer
    private func startTimer() {
        timeRemaining = roundTimeLimit; isTimerRunning = true
        timerCancellable = Timer.publish(every: 0.1, on: .main, in: .common).autoconnect()
            .sink { [weak self] _ in guard let self = self else { return }; self.timeRemaining -= 0.1
                if self.timeRemaining <= 0 { self.timeRemaining = 0; self.handleTimeOut() }
            }
    }
    private func stopTimer() { isTimerRunning = false; timerCancellable?.cancel(); timerCancellable = nil }
    private func handleTimeOut() { stopTimer(); if doubleOrNothingActive { submitDoubleOrNothingAnswer(index: -1) } else if levelUpActive { submitLevelUpAnswer(index: -1) } else if selectedAnswerIndex == nil { submitAnswer(index: -1) } }

    private var pausedTime: Double = 0
    func pauseGame() { guard isTimerRunning else { return }; pausedTime = timeRemaining; stopTimer() }
    func resumeGame() {
        guard !isTimerRunning, pausedTime > 0, selectedAnswerIndex == nil else { return }
        timeRemaining = pausedTime; isTimerRunning = true
        timerCancellable = Timer.publish(every: 0.1, on: .main, in: .common).autoconnect()
            .sink { [weak self] _ in guard let self = self else { return }; self.timeRemaining -= 0.1
                if self.timeRemaining <= 0 { self.timeRemaining = 0; self.handleTimeOut() }
            }
    }
    func quitGame() { stopTimer(); appState = .home }
}
