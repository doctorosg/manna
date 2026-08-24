import SwiftUI

struct HomeView: View {
    @EnvironmentObject var gameManager: GameManager
    @EnvironmentObject var languageManager: LanguageManager

    var body: some View {
        ZStack {
            VStack(spacing: 0) {
                Spacer()

                VStack(spacing: 12) {
                    Text("MANNA")
                        .font(.system(size: 48, weight: .black, design: .serif))
                        .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                        .tracking(6)
                    Text("\(gameManager.questionService.totalQuestionCount.formatted()) QUESTIONS")
                        .font(.system(size: 17, weight: .black, design: .rounded))
                        .foregroundColor(.white)
                        .tracking(1.4)
                    Text("Volume 1 of 3")
                        .font(.system(size: 16, weight: .semibold, design: .rounded))
                        .foregroundColor(.white.opacity(0.55))
                        .tracking(2)
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
                        Text(languageManager.ui("play"))
                            .font(.system(size: 20, weight: .bold, design: .rounded))
                    }
                    .foregroundColor(.black)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 18)
                    .background(Color(hex: "#D4A843") ?? .yellow)
                    .cornerRadius(16)
                }
                .padding(.horizontal, 40)
                .padding(.bottom, 10)

                Button(action: { gameManager.goToParty() }) {
                    HStack(spacing: 12) {
                        Image(systemName: "person.3.fill")
                        Text("Party Mode")
                            .font(.system(size: 18, weight: .bold, design: .rounded))
                    }
                    .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 15)
                    .background(Color.white.opacity(0.08))
                    .overlay(RoundedRectangle(cornerRadius: 16).stroke((Color(hex: "#D4A843") ?? .yellow).opacity(0.7), lineWidth: 1.5))
                    .cornerRadius(16)
                }
                .padding(.horizontal, 40)
                .padding(.bottom, 16)

                HStack(spacing: 64) {
                    navButton(icon: "chart.bar.fill", label: languageManager.ui("stats")) { gameManager.goToPerformance() }
                    navButton(icon: "gearshape.fill", label: languageManager.ui("settings")) { gameManager.goToSettings() }
                }
                .padding(.bottom, 30)
            }
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
