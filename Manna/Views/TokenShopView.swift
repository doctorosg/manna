import SwiftUI

struct TokenShopView: View {
    @EnvironmentObject var gameManager: GameManager
    @EnvironmentObject var tokenManager: TokenManager

    let packs: [(name: String, tokens: Int, price: String, badge: String?)] = [
        ("Starter Pack", 1000, "$0.99", nil),
        ("Value Pack", 2500, "$1.99", nil),
        ("Pro Pack", 7500, "$4.99", "Best Value"),
        ("Elite Pack", 20000, "$9.99", nil),
    ]

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Button(action: { gameManager.goHome() }) {
                    Image(systemName: "chevron.left").foregroundColor(.white)
                }
                Spacer()
                Text("Token Shop").font(.system(size: 18, weight: .bold, design: .rounded)).foregroundColor(.white)
                Spacer()
                Color.clear.frame(width: 24)
            }.padding(.horizontal, 20).padding(.vertical, 16)

            // Current balance
            HStack(spacing: 8) {
                Image(systemName: "circle.fill").foregroundColor(.yellow).font(.system(size: 16))
                Text(tokenManager.formattedTokens).font(.system(size: 24, weight: .black, design: .rounded)).foregroundColor(.white)
                Text("tokens").font(.system(size: 14)).foregroundColor(.white.opacity(0.5))
            }.padding(.vertical, 16)

            ScrollView {
                VStack(spacing: 12) {
                    ForEach(Array(packs.enumerated()), id: \.offset) { _, pack in
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                HStack(spacing: 8) {
                                    Text(pack.name).font(.system(size: 16, weight: .bold)).foregroundColor(.white)
                                    if let badge = pack.badge {
                                        Text(badge).font(.system(size: 10, weight: .bold))
                                            .foregroundColor(.black).padding(.horizontal, 8).padding(.vertical, 3)
                                            .background(Color(hex: "#D4A843") ?? .yellow).cornerRadius(6)
                                    }
                                }
                                Text("\(pack.tokens.formatted()) tokens").font(.system(size: 13)).foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                            }
                            Spacer()
                            Button(action: {
                                // StoreKit purchase would go here
                                tokenManager.earnTokens(pack.tokens, reason: "Purchase: \(pack.name)")
                            }) {
                                Text(pack.price).font(.system(size: 15, weight: .bold)).foregroundColor(.black)
                                    .padding(.horizontal, 20).padding(.vertical, 10)
                                    .background(Color(hex: "#D4A843") ?? .yellow).cornerRadius(10)
                            }
                        }
                        .padding(16)
                        .background(Color.white.opacity(0.05))
                        .overlay(RoundedRectangle(cornerRadius: 12).stroke(Color.white.opacity(0.1), lineWidth: 1))
                        .cornerRadius(12)
                    }
                }.padding(.horizontal, 16)
            }
        }
    }
}
