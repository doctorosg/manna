import Foundation

class LeaderboardManager: ObservableObject {
    @Published var entries: [LeaderboardEntry] = []
    init() {
        let names = ["FaithWalker","PsalmSinger","ScrollSeeker","GraceNote","TruthFinder","CrossRoad","SpiritWind","LightBearer","HolyQuest","BibleBuff"]
        entries = names.enumerated().map { i, name in
            LeaderboardEntry(id: UUID().uuidString, rank: i+1, playerName: name, totalTokens: Int.random(in: 500...10000), weeklyDelta: Int.random(in: -200...500), overallScore: Double.random(in: 40...95), league: [League.bronze,.silver,.gold,.platinum,.elite].randomElement() ?? .bronze)
        }.sorted { $0.totalTokens > $1.totalTokens }
    }
}
