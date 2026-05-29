import SwiftUI

struct PreGameView: View {
    @EnvironmentObject var gameManager: GameManager
    @State private var selectedCategories: Set<String> = []
    @State private var showDifficulty = false

    var body: some View {
        GeometryReader { geo in
            VStack(spacing: 0) {
                // Header
                HStack {
                    Button(action: {
                        if showDifficulty { showDifficulty = false }
                        else { gameManager.cancelPreGame() }
                    }) {
                        Image(systemName: "chevron.left")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.white)
                    }
                    Spacer()
                    Text(showDifficulty ? "Choose Difficulty" : "Choose Categories")
                        .font(.system(size: 18, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                    Spacer()
                    Color.clear.frame(width: 24)
                }
                .padding(.horizontal, 20)
                .padding(.vertical, 10)

                // Content
                if showDifficulty {
                    DifficultySelectionView(
                        categories: Array(selectedCategories).compactMap { name in
                            MannaCategory.all.first { $0.name == name }
                        }
                    ) { difficulty in
                        let cats = Array(selectedCategories).compactMap { name in
                            MannaCategory.all.first { $0.name == name }
                        }
                        gameManager.startSession(categories: cats, difficulty: difficulty)
                    }
                } else {
                    CategorySelectionView(selectedCategories: $selectedCategories) {
                        showDifficulty = true
                    }
                }

                Spacer(minLength: 0)
            }
            .frame(width: geo.size.width, height: geo.size.height, alignment: .top)
            .border(Color.red, width: 4)   // TEMPORARY DIAGNOSTIC — remove later
        }
    }
}
