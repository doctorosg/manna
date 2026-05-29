import SwiftUI

struct DifficultySelectionView: View {
    let categories: [MannaCategory]
    let onSelect: (DifficultyLevel) -> Void

    var body: some View {
        VStack(spacing: 16) {
            // Category badges
            VStack(spacing: 8) {
                if categories.count == 1 {
                    Text(categories[0].emoji).font(.system(size: 40))
                    Text(categories[0].name)
                        .font(.system(size: 18, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                } else {
                    // Show selected category emojis
                    let emojis = categories.prefix(8).map { $0.emoji }.joined(separator: " ")
                    Text(emojis).font(.system(size: 28))
                    Text("\(categories.count) categories selected")
                        .font(.system(size: 16, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                }
                Text("How well do you know your Bible?")
                    .font(.system(size: 13)).foregroundColor(.white.opacity(0.5))
            }
            .padding(.top, 16).padding(.bottom, 8)

            ForEach(DifficultyLevel.allCases) { level in
                Button(action: { onSelect(level) }) {
                    HStack(spacing: 16) {
                        Image(systemName: level.iconName)
                            .font(.system(size: 24))
                            .foregroundColor(level.color)
                            .frame(width: 40)
                        VStack(alignment: .leading, spacing: 4) {
                            Text(level.name)
                                .font(.system(size: 18, weight: .bold, design: .rounded))
                                .foregroundColor(.white)
                            Text(level.description)
                                .font(.system(size: 12))
                                .foregroundColor(.white.opacity(0.5))
                                .lineLimit(2)
                        }
                        Spacer()
                    }
                    .padding(20)
                    .background(level.color.opacity(0.1))
                    .overlay(RoundedRectangle(cornerRadius: 14).stroke(level.color.opacity(0.3), lineWidth: 1))
                    .cornerRadius(14)
                }
                .padding(.horizontal, 20)
            }

            Spacer()
        }
    }
}
