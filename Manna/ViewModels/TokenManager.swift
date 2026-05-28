import Foundation
import Combine

class TokenManager: ObservableObject {
    @Published var currentTokens: Int = 1000
    @Published var weeklyTokenDelta: Int = 0
    @Published var showStreakBonus: Bool = false
    @Published var lastBonusAmount: Int = 0

    private let dailyLoginBonus: Int = 10
    private let streakBonusMultiplier: Int = 5
    private let tokenKey = "manna_tokens"
    private let lastLoginKey = "manna_last_login"

    init() {
        loadTokens()
        checkDailyBonus()
        Task { @MainActor in
            StoreManager.shared.onTokensPurchased = { [weak self] amount in
                self?.earnTokens(amount, reason: "In-app purchase")
            }
        }
    }

    func earnTokens(_ amount: Int, reason: String = "") { currentTokens += amount; weeklyTokenDelta += amount; saveTokens() }
    func awardRoundTokens(earned: Int, lost: Int) { let net = earned - lost; currentTokens = max(0, currentTokens + net); weeklyTokenDelta += net; saveTokens() }

    @discardableResult func spendTokens(_ amount: Int) -> Bool {
        guard currentTokens >= amount else { return false }
        currentTokens -= amount; weeklyTokenDelta -= amount; saveTokens(); return true
    }

    func canAfford(_ amount: Int) -> Bool { currentTokens >= amount }

    func applyStreakBonus(streak: Int) {
        guard streak >= 3 else { return }
        let bonus = streak * streakBonusMultiplier
        earnTokens(bonus, reason: "Streak bonus x\(streak)")
        lastBonusAmount = bonus; showStreakBonus = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) { self.showStreakBonus = false }
    }

    func checkDailyBonus() {
        let lastLogin = UserDefaults.standard.object(forKey: lastLoginKey) as? Date
        let now = Date()
        if let last = lastLogin, (Calendar.current.dateComponents([.day], from: last, to: now).day ?? 0) >= 1 {
            earnTokens(dailyLoginBonus)
        } else if lastLogin == nil { earnTokens(dailyLoginBonus) }
        UserDefaults.standard.set(now, forKey: lastLoginKey)
    }

    var formattedTokens: String { currentTokens.formatted() }
    var formattedDelta: String { weeklyTokenDelta >= 0 ? "+\(weeklyTokenDelta.formatted())" : "\(weeklyTokenDelta.formatted())" }
    var deltaIsPositive: Bool { weeklyTokenDelta >= 0 }

    private func loadTokens() { let s = UserDefaults.standard.integer(forKey: tokenKey); currentTokens = s > 0 ? s : 1000 }
    private func saveTokens() { UserDefaults.standard.set(currentTokens, forKey: tokenKey) }
}
