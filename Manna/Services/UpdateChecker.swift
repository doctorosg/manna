import Foundation

@MainActor
final class UpdateChecker: ObservableObject {
    enum Status: Equatable {
        case idle, checking, current, available(version: String, url: URL), unavailable(String)
    }

    @Published private(set) var status: Status = .idle

    func check() async {
        status = .checking
        guard let bundleID = Bundle.main.bundleIdentifier,
              let url = URL(string: "https://itunes.apple.com/lookup?bundleId=\(bundleID)&country=ca") else {
            status = .unavailable("The app identifier is unavailable.")
            return
        }
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            let response = try JSONDecoder().decode(LookupResponse.self, from: data)
            guard let listing = response.results.first else {
                status = .unavailable("Manna is not yet listed in the App Store.")
                return
            }
            let installed = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "0"
            if listing.version.compare(installed, options: .numeric) == .orderedDescending,
               let storeURL = URL(string: listing.trackViewUrl) {
                status = .available(version: listing.version, url: storeURL)
            } else {
                status = .current
            }
        } catch {
            status = .unavailable("Could not check for updates. Try again later.")
        }
    }

    private struct LookupResponse: Decodable { let results: [Listing] }
    private struct Listing: Decodable { let version: String; let trackViewUrl: String }
}
