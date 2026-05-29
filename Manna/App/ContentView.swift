import SwiftUI

struct ContentView: View {
    @EnvironmentObject var gameManager: GameManager
    @EnvironmentObject var performanceTracker: PerformanceTracker

    var body: some View {
        currentScreen
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
            .background(
                Color(red: 0.06, green: 0.07, blue: 0.13)
                    .ignoresSafeArea()
            )
            .animation(.easeInOut(duration: 0.3), value: gameManager.appState)
    }

    @ViewBuilder
    private var currentScreen: some View {
        switch gameManager.appState {
        case .splash:           SplashView()
        case .home:             HomeView()
        case .categorySelection: PreGameView()
        case .playing:          GameView()
        case .result:           ResultView()
        case .performance:      PerformanceView()
        case .settings:         SettingsView()
        }
    }
}
