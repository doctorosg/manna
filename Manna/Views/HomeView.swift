import SwiftUI

struct HomeView: View {
    @EnvironmentObject var gameManager: GameManager
    @EnvironmentObject var tokenManager: TokenManager

    var body: some View {
        VStack(spacing: 0) {
            // Token Bar
            HStack {
                Image(systemName: "circle.fill")
                    .foregroundColor(.yellow)
                    .font(.system(size: 14))
                Text(tokenManager.formattedTokens)
                    .font(.system(size: 16, weight: .bold, design: .rounded))
                    .foregroundColor(.white)
                Spacer()
                Text(tokenManager.formattedDelta)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(tokenManager.deltaIsPositive ? .green : .red)
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 12)
            .background(Color.white.opacity(0.08))
            .cornerRadius(12)
            .padding(.horizontal, 20)
            .padding(.top, 16)
            .onTapGesture { gameManager.goToTokenShop() }

            Spacer()

            // Logo Area
            VStack(spacing: 8) {
                Text("🍞")
                    .font(.system(size: 72))
                Text("MANNA")
                    .font(.system(size: 44, weight: .black, design: .serif))
                    .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                    .tracking(6)
                Text("BIBLE TRIVIA")
                    .font(.system(size: 14, weight: .semibold, design: .rounded))
                    .foregroundColor(.white.opacity(0.6))
                    .tracking(4)
            }

            Spacer()

            // Play Button
            Button(action: { gameManager.goToPreGame() }) {
                HStack(spacing: 12) {
                    Image(systemName: "play.fill")
                    Text("PLAY")
                        .font(.system(size: 20, weight: .bold, design: .rounded))
                }
                .foregroundColor(.black)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 18)
                .background(Color(hex: "#D4A843") ?? .yellow)
                .cornerRadius(16)
            }
            .padding(.horizontal, 40)
            .padding(.bottom, 16)

            // Bottom Nav
            HStack(spacing: 40) {
                navButton(icon: "trophy.fill", label: "Ranks") { gameManager.goToLeaderboard() }
                navButton(icon: "gearshape.fill", label: "Settings") { gameManager.goToSettings() }
                navButton(icon: "cart.fill", label: "Shop") { gameManager.goToTokenShop() }
            }
            .padding(.bottom, 30)
        }
    }

    private func navButton(icon: String, label: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Image(systemName: icon).font(.system(size: 22))
                Text(label).font(.system(size: 11, weight: .medium))
            }
            .foregroundColor(.white.opacity(0.6))
        }
    }
}
