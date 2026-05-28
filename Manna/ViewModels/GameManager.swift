import Foundation
import Combine

class GameManager: ObservableObject {
    @Published var appState: AppState = .home
    @Published var currentQuestion: MannaQuestion?
    @Published var currentRoundNumber: Int = 0
    @Published var totalRoundsInSession: Int = 5
    @Published var roundResults: [RoundResult] = []
    @Published var botOpponents: [BotOpponent] = []
    @Published var timeRemaining: Double = 15.0
    @Published var isTimerRunning: Bool = false
    @Published var selectedAnswerIndex: Int? = nil
    @Published var selectedWager: Int = 0
    @Published var selectedWagerType: WagerType = .none
    @Published var showReveal: Bool = false
    @Published var gameMode: GameMode = .competitive
    @Published var sessionComplete: Bool = false
    @Published var currentStreak: Int = 0

    @Published var showDoubleOrNothing: Bool = false
    @Published var doubleOrNothingQuestion: MannaQuestion? = nil
    @Published var doubleOrNothingActive: Bool = false
    @Published var doubleOrNothingResult: Bool? = nil
    var doubleOrNothingStake: Int = 0

    @Published var showLevelUpOffer: Bool = false
    @Published var levelUpActive: Bool = false
    @Published var levelUpQuestion: MannaQuestion? = nil
    @Published var levelUpResult: Bool? = nil
    var levelUpBonusTokens: Int = 0
    var levelUpPenaltyTokens: Int = 0

    @Published var selectedCategories: [MannaCategory] = []
    @Published var selectedDifficulty: DifficultyLevel = .deacon
    @Published var questionsLoaded: Bool = false

    let questionService = QuestionService()
    private let botService = BotService()
    private var timerCancellable: AnyCancellable?

    let roundTimeLimit: Double = 15.0
    let questionsPerSession: Int = 5

    init() {
        print("🍞 GameManager init — loading questions...")
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
    func goToLeaderboard() { appState = .leaderboard }
    func goToSettings() { appState = .settings }
    func goToTokenShop() { appState = .tokenShop }

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
        selectedAnswerIndex = nil; selectedWager = 0; selectedWagerType = .none; showReveal = false
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

        let playerAnswer = PlayerAnswer(questionId: question.id, selectedIndex: index, isCorrect: isCorrect, timeUsed: timeUsed, wagerAmount: selectedWager, wagerType: selectedWagerType)
        let botAnswers = botService.simulateAnswers(for: question, bots: botOpponents, playerTimeUsed: timeUsed)
        let (earned, lost) = calculateTokens(playerAnswer: playerAnswer, botAnswers: botAnswers, question: question)
        let result = RoundResult(question: question, playerAnswer: playerAnswer, botAnswers: botAnswers, tokensEarned: earned, tokensLost: lost)
        roundResults.append(result)
        if isCorrect { currentStreak += 1; SoundManager.shared.playCorrect() } else { currentStreak = 0; SoundManager.shared.playWrong() }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) { [weak self] in self?.showReveal = true }
    }

    func advanceToNextRound() {
        if shouldOfferLevelUp() { offerLevelUp(); return }
        if currentRoundNumber >= questionsPerSession { endSession() } else { loadNextQuestion() }
    }

    private func shouldOfferLevelUp() -> Bool {
        guard !levelUpActive, let last = roundResults.last, last.playerAnswer.isCorrect, selectedDifficulty.nextLevel != nil else { return false }
        return Double.random(in: 0...1) < 0.30
    }
    private func offerLevelUp() {
        guard let next = selectedDifficulty.nextLevel else { return }
        levelUpBonusTokens = next.tokenReward * 3; levelUpPenaltyTokens = next.tokenReward; showLevelUpOffer = true
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
        if levelUpResult == true { SoundManager.shared.playWagerWin() } else { SoundManager.shared.playWrong() }
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) { [weak self] in self?.finalizeLevelUp() }
    }
    private func finalizeLevelUp() { levelUpActive = false; levelUpQuestion = nil; continueAfterLevelUp() }
    private func continueAfterLevelUp() { if currentRoundNumber >= questionsPerSession { endSession() } else { loadNextQuestion() } }

    private func endSession() {
        sessionComplete = true; stopTimer(); appState = .result
        let net = roundResults.reduce(0) { $0 + $1.tokensEarned - $1.tokensLost }
        if net > 0 { doubleOrNothingStake = net
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [weak self] in self?.showDoubleOrNothing = true }
        }
    }

    func acceptDoubleOrNothing() {
        showDoubleOrNothing = false; doubleOrNothingActive = true; doubleOrNothingResult = nil
        if let q = questionService.nextQuestion() { doubleOrNothingQuestion = q; timeRemaining = roundTimeLimit; selectedAnswerIndex = nil; startTimer() }
    }
    func declineDoubleOrNothing() { showDoubleOrNothing = false; doubleOrNothingStake = 0 }
    func submitDoubleOrNothingAnswer(index: Int) {
        guard let q = doubleOrNothingQuestion, doubleOrNothingActive else { return }
        stopTimer(); selectedAnswerIndex = index; doubleOrNothingResult = (index >= 0 && index == q.correctIndex)
        if doubleOrNothingResult == true { SoundManager.shared.playWagerWin() } else { SoundManager.shared.playWrong() }
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) { [weak self] in self?.finalizeDoubleOrNothing() }
    }
    private func finalizeDoubleOrNothing() { doubleOrNothingActive = false; doubleOrNothingQuestion = nil; doubleOrNothingStake = 0 }

    // Timer
    private func startTimer() {
        timeRemaining = roundTimeLimit; isTimerRunning = true
        timerCancellable = Timer.publish(every: 0.1, on: .main, in: .common).autoconnect()
            .sink { [weak self] _ in guard let self = self else { return }; self.timeRemaining -= 0.1
                if self.timeRemaining <= 0 { self.timeRemaining = 0; self.handleTimeOut() }
            }
    }
    private func stopTimer() { isTimerRunning = false; timerCancellable?.cancel(); timerCancellable = nil }
    private func handleTimeOut() { stopTimer(); if doubleOrNothingActive { submitDoubleOrNothingAnswer(index: -1) } else if selectedAnswerIndex == nil { submitAnswer(index: -1) } }

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

    private func calculateTokens(playerAnswer: PlayerAnswer, botAnswers: [BotAnswer], question: MannaQuestion) -> (earned: Int, lost: Int) {
        var earned = 0; var lost = 0; let base = question.baseTokenReward
        if playerAnswer.isCorrect {
            earned += base
            if playerAnswer.wagerType == .standard && playerAnswer.wagerAmount > 0 { earned += playerAnswer.wagerAmount }
            else if playerAnswer.wagerType != .none && playerAnswer.wagerAmount > 0 {
                let cc = botAnswers.filter { $0.isCorrect }.count + 1
                let won = evaluateWager(type: playerAnswer.wagerType, correctCount: cc)
                if won { earned += Int(Double(playerAnswer.wagerAmount) * playerAnswer.wagerType.multiplier) } else { lost += playerAnswer.wagerAmount }
            }
        } else { if playerAnswer.wagerAmount > 0 { lost += playerAnswer.wagerAmount } }
        return (earned, lost)
    }

    private func evaluateWager(type: WagerType, correctCount: Int) -> Bool {
        switch type { case .win: return correctCount == 1; case .place: return correctCount <= 2; case .show: return correctCount <= 3; default: return false }
    }
}
