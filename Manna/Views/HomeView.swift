import SwiftUI

struct HomeView: View {
    @EnvironmentObject var gameManager: GameManager

    var body: some View {
        VStack(spacing: 0) {
            Spacer()

            // Logo
            VStack(spacing: 8) {
                Image("challah")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 120, height: 80)
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
            HStack(spacing: 50) {
                navButton(icon: "chart.bar.fill", label: "My Stats") { gameManager.goToPerformance() }
                navButton(icon: "gearshape.fill", label: "Settings") { gameManager.goToSettings() }
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
