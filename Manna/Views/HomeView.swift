import SwiftUI

struct HomeView: View {
    @EnvironmentObject var gameManager: GameManager
    @State private var animateFlakes = false

    var body: some View {
        ZStack {
            // Falling manna particles
            ForEach(0..<20, id: \.self) { i in
                MannaFlake(index: i, animate: animateFlakes)
            }

            VStack(spacing: 0) {
                Spacer()

                VStack(spacing: 12) {
                    Text("MANNA")
                        .font(.system(size: 48, weight: .black, design: .serif))
                        .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                        .tracking(6)
                    Text("\"All Scripture is given by inspiration of God and is profitable for doctrine, for reproof, for correction, for instruction in righteousness.\"")
                        .font(.system(size: 36, weight: .regular, design: .serif))
                        .foregroundColor(.white.opacity(0.6))
                        .multilineTextAlignment(.center)
                        .italic()
                        .lineSpacing(6)
                        .padding(.horizontal, 24)
                        .padding(.top, 12)
                    Text("— 2 Timothy 3:16")
                        .font(.system(size: 18, weight: .semibold, design: .serif))
                        .foregroundColor(.white.opacity(0.45))
                        .padding(.top, 4)
                }

                Spacer()

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

                HStack(spacing: 50) {
                    navButton(icon: "chart.bar.fill", label: "My Stats") { gameManager.goToPerformance() }
                    navButton(icon: "gearshape.fill", label: "Settings") { gameManager.goToSettings() }
                }
                .padding(.bottom, 30)
            }
        }
        .onAppear { animateFlakes = true }
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

// MARK: - Falling Manna Flake
struct MannaFlake: View {
    let index: Int
    let animate: Bool

    private var size: CGFloat { CGFloat.random(in: 8...22) }
    private var startX: CGFloat { CGFloat.random(in: 20...360) }
    private var duration: Double { Double.random(in: 4...9) }
    private var delay: Double { Double.random(in: 0...5) }
    private var opacity: Double { Double.random(in: 0.15...0.5) }
    private var drift: CGFloat { CGFloat.random(in: -30...30) }

    @State private var yPos: CGFloat = -50
    @State private var xOffset: CGFloat = 0
    @State private var rotation: Double = 0

    var body: some View {
        Ellipse()
            .fill(Color(hex: "#D4A843")?.opacity(opacity) ?? .yellow.opacity(opacity))
            .frame(width: size * 1.4, height: size * 0.8)
            .offset(x: startX - 200 + xOffset, y: yPos)
            .rotationEffect(.degrees(rotation))
            .onAppear {
                guard animate else { return }
                withAnimation(
                    .linear(duration: duration)
                    .delay(delay)
                    .repeatForever(autoreverses: false)
                ) {
                    yPos = 900
                    xOffset = drift
                    rotation = Double.random(in: -180...180)
                }
            }
    }
}
