import SwiftUI
import AuthenticationServices

struct SignInView: View {
    @EnvironmentObject var authManager: AuthManager

    var body: some View {
        VStack(spacing: 24) {
            Spacer()
            Image("challah")
                .resizable()
                .scaledToFit()
                .frame(width: 130, height: 85)
            Text("MANNA").font(.system(size: 44, weight: .black, design: .serif))
                .foregroundColor(Color(hex: "#D4A843") ?? .yellow).tracking(6)
            Text("BIBLE TRIVIA").font(.system(size: 14, weight: .semibold)).foregroundColor(.white.opacity(0.5)).tracking(4)
            Spacer()

            SignInWithAppleButton(.signIn) { request in
                request.requestedScopes = [.fullName, .email]
            } onCompletion: { result in
                authManager.handleAppleSignIn(result: result)
            }
            .signInWithAppleButtonStyle(.white)
            .frame(height: 52)
            .cornerRadius(14)
            .padding(.horizontal, 40)

            Button(action: {
                // Skip sign in for now
                authManager.userId = UUID().uuidString
                authManager.userName = "Player"
                UserDefaults.standard.set(authManager.userId, forKey: "manna_user_id")
                UserDefaults.standard.set(authManager.userName, forKey: "manna_user_name")
                authManager.authState = .signedIn
            }) {
                Text("Continue as Guest")
                    .font(.system(size: 15, weight: .medium)).foregroundColor(.white.opacity(0.5))
            }
            .padding(.bottom, 40)
        }
    }
}
