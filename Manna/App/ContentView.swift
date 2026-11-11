import SwiftUI

struct ContentView: View {
    @EnvironmentObject var gameManager: GameManager
    @EnvironmentObject var performanceTracker: PerformanceTracker
    @EnvironmentObject var monetization: MonetizationManager

    var body: some View {
        ZStack(alignment: .top) {
            Color(red: 0.06, green: 0.07, blue: 0.13)
                .ignoresSafeArea()

            if monetization.requiresInternetAccess {
                InternetRequiredView()
            } else {
                switch gameManager.appState {
                case .splash:            SplashView()
                case .home:              HomeView()
                case .categorySelection: PreGameView()
                case .playing:           GameView()
                case .result:            ResultView()
                case .performance:       PerformanceView()
                case .settings:          SettingsView()
                case .party:             PartyRootView()
                }
            }
        }
        .onAppear { DiagnosticRecorder.shared.record("app_visible screen=\(screenName(gameManager.appState))") }
        .onChange(of: gameManager.appState) { state in
            DiagnosticRecorder.shared.record("screen=\(screenName(state))")
            if state == .home { monetization.setChildDirectedSession(false) }
        }
    }

    private func screenName(_ state: AppState) -> String {
        switch state {
        case .splash: "splash"
        case .home: "home"
        case .categorySelection: "session_setup"
        case .playing: "game"
        case .result: "result"
        case .performance: "performance"
        case .settings: "settings"
        case .party: "party"
        }
    }
}

private struct InternetRequiredView: View {
    var body: some View {
        VStack(spacing: 18) {
            Image(systemName: "wifi.exclamationmark")
                .font(.system(size: 52, weight: .semibold))
                .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
            MannaText("Internet Required")
                .font(.system(size: 28, weight: .bold, design: .rounded))
                .foregroundColor(.white)
            MannaText("The free version of Manna needs an active Wi-Fi or cellular internet connection so advertising can be delivered. Reconnect to continue, or purchase Remove Ads while online for permanent offline access.")
                .font(.system(size: 16, weight: .medium, design: .rounded))
                .foregroundColor(.white.opacity(0.72))
                .multilineTextAlignment(.center)
                .lineSpacing(4)
        }
        .padding(34)
        .frame(maxWidth: 520)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
