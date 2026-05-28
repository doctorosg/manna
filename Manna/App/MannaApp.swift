import SwiftUI

@main
struct MannaApp: App {
    @StateObject private var gameManager = GameManager()
    @StateObject private var tokenManager = TokenManager()
    @StateObject private var leaderboardManager = LeaderboardManager()
    @StateObject private var authManager = AuthManager()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(gameManager)
                .environmentObject(tokenManager)
                .environmentObject(leaderboardManager)
                .environmentObject(authManager)
                .preferredColorScheme(.dark)
        }
    }
}
