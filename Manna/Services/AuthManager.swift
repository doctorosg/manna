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
        if let saved = UserDefaults.standard.string(forKey: "manna_user_id"), !saved.isEmpty {
            userId = saved
            userName = UserDefaults.standard.string(forKey: "manna_user_name") ?? "Player"
            authState = .signedIn
        } else {
            // Auto sign-in for MVP — skip auth gate
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                self.authState = .signedIn
                self.userName = "Player"
                self.userId = UUID().uuidString
                UserDefaults.standard.set(self.userId, forKey: "manna_user_id")
                UserDefaults.standard.set(self.userName, forKey: "manna_user_name")
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
        authState = .signedOut
    }
}
