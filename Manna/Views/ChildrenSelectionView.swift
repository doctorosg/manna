import SwiftUI

struct ChildrenSelectionView: View {
    @EnvironmentObject private var languageManager: LanguageManager
    @Binding var selectedAgeGroup: ChildAgeGroup
    let onStart: () -> Void

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                Picker(languageManager.interfaceString("Age group"), selection: $selectedAgeGroup) {
                    ForEach(ChildAgeGroup.allCases) { group in
                        MannaText(group.shortLabel).tag(group)
                    }
                }
                .pickerStyle(.segmented)
                .padding(.horizontal, 20)
                .mannaAccessibilityLabel("Children's age group")
                .background { MannaText("Age group").hidden() }

                VStack(spacing: 12) {
                    Text(selectedAgeGroup.emoji).font(.system(size: 56))
                    MannaText(selectedAgeGroup.title)
                        .font(.system(size: 26, weight: .black, design: .rounded))
                        .foregroundColor(.white)
                    MannaText(selectedAgeGroup.description)
                        .font(.system(size: 15, weight: .medium, design: .rounded))
                        .foregroundColor(.white.opacity(0.68))
                        .multilineTextAlignment(.center)
                    HStack(spacing: 18) {
                        fact(selectedAgeGroup.questionCount.formatted(), "questions")
                        Divider().frame(height: 36).overlay(Color.white.opacity(0.2))
                        fact("\(selectedAgeGroup.answerChoiceCount)", "choices each")
                    }
                    .padding(.top, 5)
                }
                .frame(maxWidth: .infinity)
                .padding(28)
                .background(Color.white.opacity(0.07))
                .overlay(
                    RoundedRectangle(cornerRadius: 18)
                        .stroke(Color(hex: "#D4A843")?.opacity(0.35) ?? .yellow.opacity(0.35))
                )
                .cornerRadius(18)
                .padding(.horizontal, 20)

                MannaText(selectedAgeGroup == .ages4to10
                     ? "A grown-up can read the questions aloud while the child chooses an answer."
                     : "Questions are selected only from this age group and work offline.")
                    .font(.system(size: 13, weight: .medium, design: .rounded))
                    .foregroundColor(.white.opacity(0.52))
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 30)

                Button(action: onStart) {
                    MannaText("Start \(selectedAgeGroup.title) Game")
                        .font(.system(size: 17, weight: .bold, design: .rounded))
                        .foregroundColor(.black)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                        .background(Color(hex: "#D4A843") ?? .yellow)
                        .cornerRadius(14)
                }
                .padding(.horizontal, 20)
            }
            .padding(.top, 12)
            .padding(.bottom, 24)
        }
    }

    private func fact(_ value: String, _ label: String) -> some View {
        VStack(spacing: 2) {
            Text(value).font(.system(size: 17, weight: .black, design: .rounded)).foregroundColor(.white)
            MannaText(label).font(.system(size: 11, weight: .semibold, design: .rounded)).foregroundColor(.white.opacity(0.5))
        }
    }
}
