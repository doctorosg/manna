import SwiftUI
import AuthenticationServices

enum AuthState {
    case unknown, signedOut, signedIn
}

class AuthManager: ObservableObject {
    @Published var authState: AuthState = .unknown
    @Published var userName: String = ""
    @Published var userId: String = ""

    init() {
        // Check for existing session
        if let saved = UserDefaults.standard.string(forKey: "manna_user_id"), !saved.isEmpty {
            userId = saved
            userName = UserDefaults.standard.string(forKey: "manna_user_name") ?? "Player"
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                self.authState = .signedIn
            }
        } else {
            // Auto sign-in as guest for MVP
            let newId = UUID().uuidString
            UserDefaults.standard.set(newId, forKey: "manna_user_id")
            UserDefaults.standard.set("Player", forKey: "manna_user_name")
            userId = newId
            userName = "Player"
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                self.authState = .signedIn
            }
        }
    }

    func handleAppleSignIn(result: Result<ASAuthorization, Error>) {
        switch result {
        case .success(let auth):
            if let credential = auth.credential as? ASAuthorizationAppleIDCredential {
                userId = credential.user
                userName = [credential.fullName?.givenName, credential.fullName?.familyName]
                    .compactMap { $0 }.joined(separator: " ")
                if userName.isEmpty { userName = "Player" }
                UserDefaults.standard.set(userId, forKey: "manna_user_id")
                UserDefaults.standard.set(userName, forKey: "manna_user_name")
                authState = .signedIn
            }
        case .failure(let error):
            print("Apple Sign In failed: \(error)")
        }
    }

    func signOut() {
        UserDefaults.standard.removeObject(forKey: "manna_user_id")
        UserDefaults.standard.removeObject(forKey: "manna_user_name")
        userId = ""
        userName = ""
        authState = .signedOut
    }
}
