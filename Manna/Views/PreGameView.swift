import SwiftUI
import UIKit

final class DiagnosticRecorder {
    static let shared = DiagnosticRecorder()

    private struct Entry {
        let date: Date
        let event: String
    }

    private let lock = NSLock()
    private var entries: [Entry] = []
    private let window: TimeInterval = 20

    private init() {}

    func record(_ event: String) {
        let now = Date()
        lock.lock()
        entries.append(Entry(date: now, event: event.replacingOccurrences(of: "\n", with: " ")))
        entries.removeAll { now.timeIntervalSince($0.date) > window }
        if entries.count > 200 { entries.removeFirst(entries.count - 200) }
        lock.unlock()
    }

    func reportBody() -> String {
        let now = Date()
        lock.lock()
        entries.removeAll { now.timeIntervalSince($0.date) > window }
        let snapshot = entries
        lock.unlock()

        let info = Bundle.main.infoDictionary ?? [:]
        let version = info["CFBundleShortVersionString"] as? String ?? "unknown"
        let build = info["CFBundleVersion"] as? String ?? "unknown"
        let device = UIDevice.current
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        let events = snapshot.isEmpty
            ? "No diagnostic events were recorded during the previous 20 seconds."
            : snapshot.map { "\(formatter.string(from: $0.date))  \($0.event)" }.joined(separator: "\n")

        return """
        Please describe the problem above this line:


        ---------------- Manna diagnostics ----------------
        App: Manna \(version) (build \(build))
        Platform: \(device.systemName) \(device.systemVersion)
        Device class: \(device.model)
        Captured window: previous 20 seconds

        \(events)
        -----------------------------------------------------
        This report excludes question text, answer text, account data, and user-entered content.
        """
    }

    func composeSupportEmail(onUnavailable: @escaping () -> Void) {
        record("support_email_opened")
        let body = reportBody()
        var components = URLComponents(string: "mailto:support@oddcurrent.com")
        components?.queryItems = [
            URLQueryItem(name: "subject", value: "Manna Problem Report"),
            URLQueryItem(name: "body", value: body)
        ]
        guard let url = components?.url else { return }
        UIApplication.shared.open(url, options: [:]) { opened in
            guard !opened else { return }
            UIPasteboard.general.string = body
            DispatchQueue.main.async { onUnavailable() }
        }
    }
}

struct PreGameView: View {
    @EnvironmentObject var gameManager: GameManager
    @State private var selectedCategories: Set<String> = []
    @State private var showDifficulty = false
    @State private var showEmailUnavailable = false

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Button(action: {
                    if showDifficulty { showDifficulty = false }
                    else { gameManager.cancelPreGame() }
                }) {
                    Image(systemName: "chevron.left")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.white)
                }
                Spacer()
                Text(showDifficulty ? "Choose Difficulty" : "Choose Categories")
                    .font(.system(size: 18, weight: .bold, design: .rounded))
                    .foregroundColor(.white)
                Spacer()
                Color.clear.frame(width: 24, height: 24)
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 10)

            // Content
            if showDifficulty {
                DifficultySelectionView(
                    categories: Array(selectedCategories).compactMap { name in
                        MannaCategory.all.first { $0.name == name }
                    }
                ) { difficulty in
                    let cats = Array(selectedCategories).compactMap { name in
                        MannaCategory.all.first { $0.name == name }
                    }
                    DiagnosticRecorder.shared.record("setup_difficulty=\(difficulty.name) categories=\(cats.count)")
                    gameManager.startSession(categories: cats, difficulty: difficulty)
                }
            } else {
                CategorySelectionView(selectedCategories: $selectedCategories) {
                    DiagnosticRecorder.shared.record("setup_categories_confirmed count=\(selectedCategories.count)")
                    showDifficulty = true
                }
            }

            Button {
                DiagnosticRecorder.shared.composeSupportEmail {
                    showEmailUnavailable = true
                }
            } label: {
                VStack(spacing: 3) {
                    Label("Report a Problem", systemImage: "envelope.badge")
                        .font(.system(size: 14, weight: .bold, design: .rounded))
                    Text("Includes privacy-safe diagnostics from the last 20 seconds")
                        .font(.system(size: 10, weight: .medium, design: .rounded))
                }
                .foregroundColor(.white.opacity(0.78))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 9)
                .background(Color.white.opacity(0.07))
                .cornerRadius(12)
            }
            .padding(.horizontal, 20)
            .padding(.bottom, 8)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
        .onAppear { DiagnosticRecorder.shared.record("screen=session_setup") }
        .alert("No Email App Available", isPresented: $showEmailUnavailable) {
            Button("OK", role: .cancel) {}
        } message: {
            Text("The diagnostic report was copied. Paste it into an email to support@oddcurrent.com and add your description.")
        }
    }
}
