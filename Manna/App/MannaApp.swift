import SwiftUI

@main
struct MannaApp: App {
    @StateObject private var gameManager = GameManager()
    @StateObject private var tokenManager = TokenManager()
    @StateObject private var leaderboardManager = LeaderboardManager()
    @StateObject private var authManager = AuthManager()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(gameManager)
                .environmentObject(tokenManager)
                .environmentObject(leaderboardManager)
                .environmentObject(authManager)
        }
    }
}

struct RootView: View {
    @EnvironmentObject var authManager: AuthManager
    var body: some View {
        switch authManager.authState {
        case .unknown: SplashView()
        case .signedOut: SignInView()
        case .signedIn: ContentView()
        }
    }
}
