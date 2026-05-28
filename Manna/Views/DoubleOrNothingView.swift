import SwiftUI

struct DoubleOrNothingView: View {
    @EnvironmentObject var gameManager: GameManager

    var body: some View {
        ZStack {
            Color.black.opacity(0.8).ignoresSafeArea()
            VStack(spacing: 20) {
                Text("🎲 DOUBLE OR NOTHING").font(.system(size: 22, weight: .black, design: .rounded))
                    .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                Text("You earned \(gameManager.doubleOrNothingStake) tokens this session.")
                    .font(.system(size: 15)).foregroundColor(.white.opacity(0.7))
                Text("Risk it all on one question?")
                    .font(.system(size: 14)).foregroundColor(.white.opacity(0.5))
                VStack(spacing: 8) {
                    Text("Win: +\(gameManager.doubleOrNothingStake) more").font(.system(size: 14, weight: .bold)).foregroundColor(.green)
                    Text("Lose: -\(gameManager.doubleOrNothingStake) tokens").font(.system(size: 14, weight: .bold)).foregroundColor(.red)
                }
                HStack(spacing: 16) {
                    Button(action: { gameManager.declineDoubleOrNothing() }) {
                        Text("Keep Tokens").foregroundColor(.white.opacity(0.6))
                            .frame(maxWidth: .infinity).padding(.vertical, 14)
                            .background(Color.white.opacity(0.1)).cornerRadius(12)
                    }
                    Button(action: { gameManager.acceptDoubleOrNothing() }) {
                        Text("Double It!").font(.system(size: 16, weight: .bold)).foregroundColor(.black)
                            .frame(maxWidth: .infinity).padding(.vertical, 14)
                            .background(Color(hex: "#D4A843") ?? .yellow).cornerRadius(12)
                    }
                }.padding(.horizontal, 20)
            }.padding(24)
        }
    }
}
