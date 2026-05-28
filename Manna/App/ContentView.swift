import SwiftUI

struct ContentView: View {
    @EnvironmentObject var gameManager: GameManager
    @EnvironmentObject var tokenManager: TokenManager

    var body: some View {
        ZStack {
            Color(red: 0.06, green: 0.07, blue: 0.13)
                .ignoresSafeArea()

            switch gameManager.appState {
            case .splash:
                SplashView()
            case .home:
                HomeView()
            case .categorySelection:
                PreGameView()
            case .playing:
                GameView()
            case .result:
                ResultView()
            case .leaderboard:
                LeaderboardView()
            case .settings:
                SettingsView()
            case .tokenShop:
                TokenShopView()
            }
        }
        .animation(.easeInOut(duration: 0.3), value: gameManager.appState)
    }
}
