import SwiftUI

struct DifficultySelectionView: View {
    let categories: [MannaCategory]
    let onSelect: (DifficultyLevel) -> Void

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                // Category badge — compact at top
                VStack(spacing: 6) {
                    if categories.count == 1 {
                        Text(categories[0].emoji).font(.system(size: 36))
                        Text(categories[0].name)
                            .font(.system(size: 17, weight: .bold, design: .rounded))
                            .foregroundColor(.white)
                    } else {
                        let emojis = categories.prefix(8).map { $0.emoji }.joined(separator: " ")
                        Text(emojis).font(.system(size: 24))
                        Text("\(categories.count) categories selected")
                            .font(.system(size: 15, weight: .bold, design: .rounded))
                            .foregroundColor(.white)
                    }
                    Text("How well do you know your Bible?")
                        .font(.system(size: 13)).foregroundColor(.white.opacity(0.5))
                }
                .padding(.top, 8).padding(.bottom, 4)

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
                        .padding(18)
                        .background(level.color.opacity(0.1))
                        .overlay(RoundedRectangle(cornerRadius: 14).stroke(level.color.opacity(0.3), lineWidth: 1))
                        .cornerRadius(14)
                    }
                    .padding(.horizontal, 20)
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
    }
}
