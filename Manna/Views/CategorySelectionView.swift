import SwiftUI

struct CategorySelectionView: View {
    let onSelect: (MannaCategory) -> Void
    let columns = [GridItem(.flexible(), spacing: 12), GridItem(.flexible(), spacing: 12)]

    var body: some View {
        ScrollView {
            LazyVGrid(columns: columns, spacing: 12) {
                ForEach(MannaCategory.all) { category in
                    Button(action: { onSelect(category) }) {
                        VStack(spacing: 8) {
                            Text(category.emoji).font(.system(size: 32))
                            Text(category.name)
                                .font(.system(size: 13, weight: .semibold, design: .rounded))
                                .foregroundColor(.white)
                                .multilineTextAlignment(.center)
                                .lineLimit(2)
                                .minimumScaleFactor(0.8)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 20)
                        .background(category.color.opacity(0.2))
                        .overlay(RoundedRectangle(cornerRadius: 12).stroke(category.color.opacity(0.4), lineWidth: 1))
                        .cornerRadius(12)
                    }
                }
            }
            .padding(.horizontal, 16)
            .padding(.bottom, 40)
        }
    }
}
