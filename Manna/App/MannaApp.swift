import SwiftUI

@main
struct MannaApp: App {
    @StateObject private var gameManager = GameManager()
    @StateObject private var performanceTracker = PerformanceTracker()
    @StateObject private var authManager = AuthManager()
    @StateObject private var languageManager = LanguageManager()
    @StateObject private var monetizationManager = MonetizationManager()
    @StateObject private var partyManager = PartyManager()

    var body: some Scene {
        WindowGroup {
            Group {
                if languageManager.hasCompletedLanguageSetup {
                    ContentView()
                } else {
                    LanguageSetupView()
                }
            }
                .environmentObject(gameManager)
                .environmentObject(performanceTracker)
                .environmentObject(authManager)
                .environmentObject(languageManager)
                .environmentObject(monetizationManager)
                .environmentObject(partyManager)
                .environment(\.layoutDirection, languageManager.selected == .arabic ? .rightToLeft : .leftToRight)
                .preferredColorScheme(.dark)
                .onOpenURL { url in
                    guard url.scheme == "manna", url.host == "party",
                          let code = url.pathComponents.last, code.count == 6 else { return }
                    partyManager.openJoin(code: code)
                    gameManager.goToParty()
                }
        }
    }
}
