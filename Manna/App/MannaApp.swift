import SwiftUI

@main
struct MannaApp: App {
    @StateObject private var gameManager = GameManager()
    @StateObject private var performanceTracker = PerformanceTracker()
    @StateObject private var authManager = AuthManager()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(gameManager)
                .environmentObject(performanceTracker)
                .environmentObject(authManager)
                .preferredColorScheme(.dark)
        }
    }
}
