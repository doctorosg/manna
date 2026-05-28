import SwiftUI

struct DifficultySelectionView: View {
    let category: MannaCategory
    let onSelect: (DifficultyLevel) -> Void

    var body: some View {
        VStack(spacing: 16) {
            // Category badge
            VStack(spacing: 6) {
                Text(category.emoji).font(.system(size: 40))
                Text(category.name)
                    .font(.system(size: 18, weight: .bold, design: .rounded))
                    .foregroundColor(.white)
                Text(category.description)
                    .font(.system(size: 13)).foregroundColor(.white.opacity(0.5))
                    .multilineTextAlignment(.center).padding(.horizontal, 20)
            }
            .padding(.vertical, 16)

            Spacer()

            ForEach(DifficultyLevel.allCases) { level in
                Button(action: { onSelect(level) }) {
                    HStack(spacing: 16) {
                        Image(systemName: level.iconName)
                            .font(.system(size: 24))
                            .foregroundColor(level.color)
                            .frame(width: 40)
                        VStack(alignment: .leading, spacing: 4) {
                            HStack {
                                Text(level.name)
                                    .font(.system(size: 18, weight: .bold, design: .rounded))
                                    .foregroundColor(.white)
                                Spacer()
                                Text("+\(level.tokenReward)")
                                    .font(.system(size: 15, weight: .bold, design: .rounded))
                                    .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                            }
                            Text(level.description)
                                .font(.system(size: 12))
                                .foregroundColor(.white.opacity(0.5))
                                .lineLimit(2)
                        }
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
