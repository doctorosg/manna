import SwiftUI

struct CategorySelectionView: View {
    @Binding var selectedCategories: Set<String>
    let onContinue: () -> Void
    let columns = [GridItem(.flexible(), spacing: 12), GridItem(.flexible(), spacing: 12)]

    var body: some View {
        VStack(spacing: 0) {
            // Select All — compact strip directly under the page header
            Button(action: {
                if selectedCategories.count == MannaCategory.all.count { selectedCategories.removeAll() }
                else { selectedCategories = Set(MannaCategory.all.map { $0.name }) }
            }) {
                HStack(spacing: 8) {
                    Image(systemName: selectedCategories.count == MannaCategory.all.count ? "checkmark.square.fill" : "square")
                        .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                    Text(selectedCategories.count == MannaCategory.all.count ? "Deselect All" : "Select All")
                        .font(.system(size: 14, weight: .semibold, design: .rounded))
                        .foregroundColor(.white.opacity(0.7))
                    Spacer()
                    if !selectedCategories.isEmpty {
                        Text("\(selectedCategories.count) selected")
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                    }
                }
                .padding(.horizontal, 20).padding(.top, 4).padding(.bottom, 8)
            }

            // Categories grid — starts immediately under the heading
            ScrollView {
                LazyVGrid(columns: columns, spacing: 10) {
                    ForEach(MannaCategory.all) { category in
                        let isSelected = selectedCategories.contains(category.name)
                        Button(action: {
                            if isSelected { selectedCategories.remove(category.name) }
                            else { selectedCategories.insert(category.name) }
                        }) {
                            VStack(spacing: 6) {
                                Text(category.emoji).font(.system(size: 28))
                                Text(category.name)
                                    .font(.system(size: 12, weight: .semibold, design: .rounded))
                                    .foregroundColor(.white)
                                    .multilineTextAlignment(.center)
                                    .lineLimit(2)
                                    .minimumScaleFactor(0.8)
                            }
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                            .background(isSelected ? category.color.opacity(0.35) : category.color.opacity(0.12))
                            .overlay(
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(isSelected ? category.color : category.color.opacity(0.2), lineWidth: isSelected ? 2 : 1)
                            )
                            .cornerRadius(12)
                            .overlay(alignment: .topTrailing) {
                                if isSelected {
                                    Image(systemName: "checkmark.circle.fill")
                                        .foregroundColor(.green).font(.system(size: 16)).padding(5)
                                }
                            }
                        }
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 2)
                .padding(.bottom, 90)
            }

            // Continue button — fixed at bottom
            if !selectedCategories.isEmpty {
                Button(action: onContinue) {
                    Text("Continue (\(selectedCategories.count) \(selectedCategories.count == 1 ? "category" : "categories"))")
                        .font(.system(size: 16, weight: .bold, design: .rounded))
                        .foregroundColor(.black)
                        .frame(maxWidth: .infinity).padding(.vertical, 16)
                        .background(Color(hex: "#D4A843") ?? .yellow)
                        .cornerRadius(14)
                }
                .padding(.horizontal, 20).padding(.bottom, 16)
            }
        }
    }
}
