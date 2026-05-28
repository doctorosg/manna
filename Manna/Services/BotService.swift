import Foundation

struct BotOpponent: Identifiable {
    let id = UUID()
    let name: String
    let countryFlag: String
    let scorePercentage: Double
    let personality: BotPersonality
    let league: League
}

enum BotPersonality: CaseIterable {
    case conservative, aggressive, erratic, strategic
}

class BotService {
    private let botNames = [
        "FaithWalker", "PsalmSinger", "ScrollSeeker", "GraceNote",
        "TruthFinder", "CrossRoad", "SpiritWind", "LightBearer",
        "HolyQuest", "BibleBuff", "VerseKing", "ProphetPro",
        "SaltLight", "DawnStar", "AmenMind", "PathFinder",
        "MustardSeed", "LivingWater", "BurningBush", "RockSolid"
    ]
    private let flags = ["🇺🇸","🇨🇦","🇬🇧","🇦🇺","🇧🇷","🇵🇭","🇳🇬","🇰🇷","🇲🇽","🇮🇹","🇩🇪","🇫🇷","🇮🇳","🇿🇦","🇰🇪","🇬🇭","🇯🇲","🇨🇴","🇪🇸","🇳🇱"]

    func generateOpponents(count: Int, mode: GameMode) -> [BotOpponent] {
        var opponents: [BotOpponent] = []
        var usedNames: Set<String> = []
        for _ in 0..<count {
            var name: String
            repeat { name = botNames.randomElement() ?? "Player" } while usedNames.contains(name)
            usedNames.insert(name)
            let skill: Double = switch mode {
            case .casual: Double.random(in: 40...75)
            case .competitive: Double.random(in: 45...80)
            case .elite: Double.random(in: 75...95)
            case .daily: Double.random(in: 50...85)
            }
            let league: League = skill >= 85 ? .elite : skill >= 70 ? .platinum : skill >= 55 ? .gold : skill >= 40 ? .silver : .bronze
            opponents.append(BotOpponent(name: name, countryFlag: flags.randomElement() ?? "🏳️", scorePercentage: skill, personality: BotPersonality.allCases.randomElement() ?? .strategic, league: league))
        }
        return opponents
    }

    func simulateAnswers(for question: MannaQuestion, bots: [BotOpponent], playerTimeUsed: Double) -> [BotAnswer] {
        bots.map { bot in
            let penalty = Double(question.difficultyInt - 1) * 8.0
            let adjusted = max(10, bot.scorePercentage - penalty)
            let correct = Double.random(in: 0...100) < adjusted
            let idx = correct ? question.correctIndex : (0..<question.options.count).filter { $0 != question.correctIndex }.randomElement() ?? 0
            let time = correct ? Double.random(in: 1.5...8.0) : Double.random(in: 4.0...13.0)
            let wager = Double.random(in: 0...1) < 0.4 ? [10,25,50,100].randomElement() ?? 0 : 0
            return BotAnswer(botName: bot.name, botScore: bot.scorePercentage, selectedIndex: idx, isCorrect: correct, wagerAmount: wager, wagerType: wager > 0 ? .standard : .none, responseTime: time)
        }
    }
}
