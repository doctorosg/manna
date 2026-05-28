import SwiftUI

struct PreGameView: View {
    @EnvironmentObject var gameManager: GameManager
    @State private var selectedCategory: MannaCategory? = nil
    @State private var showDifficulty = false

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Button(action: { if showDifficulty { showDifficulty = false; selectedCategory = nil } else { gameManager.cancelPreGame() } }) {
                    Image(systemName: "chevron.left").font(.system(size: 18, weight: .semibold)).foregroundColor(.white)
                }
                Spacer()
                Text(showDifficulty ? "Choose Difficulty" : "Choose Category")
                    .font(.system(size: 18, weight: .bold, design: .rounded)).foregroundColor(.white)
                Spacer()
                Color.clear.frame(width: 24)
            }
            .padding(.horizontal, 20).padding(.vertical, 16)

            if showDifficulty {
                DifficultySelectionView(category: selectedCategory!) { difficulty in
                    gameManager.startSession(categories: [selectedCategory!], difficulty: difficulty)
                }
            } else {
                CategorySelectionView { category in
                    selectedCategory = category
                    showDifficulty = true
                }
            }
        }
        .animation(.easeInOut(duration: 0.2), value: showDifficulty)
    }
}
