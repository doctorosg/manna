import SwiftUI

struct PerformanceView: View {
    @EnvironmentObject var gameManager: GameManager
    @EnvironmentObject var performanceTracker: PerformanceTracker
    @State private var selectedTab = 0

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Button(action: { gameManager.goHome() }) {
                    Image(systemName: "chevron.left").foregroundColor(.white)
                }
                Spacer()
                Text("My Performance").font(.system(size: 18, weight: .bold, design: .rounded)).foregroundColor(.white)
                Spacer()
                Color.clear.frame(width: 24, height: 24)
            }.padding(.horizontal, 20).padding(.vertical, 16)

            // Overall stats bar
            overallStats

            // Tab picker
            Picker("", selection: $selectedTab) {
                Text("Categories").tag(0)
                Text("Difficulty").tag(1)
                Text("Improve").tag(2)
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 16)
            .padding(.vertical, 8)

            // Tab content
            ScrollView {
                switch selectedTab {
                case 0: categoryBreakdown
                case 1: difficultyBreakdown
                case 2: studySuggestions
                default: EmptyView()
                }
            }
        }
    }

    // MARK: - Overall Stats
    private var overallStats: some View {
        HStack(spacing: 20) {
            statBox(value: "\(Int(performanceTracker.overallScore))%", label: "Overall", color: scoreColor(performanceTracker.overallScore))
            statBox(value: "\(performanceTracker.totalQuestions)", label: "Answered", color: .white)
            statBox(value: "\(performanceTracker.totalGames)", label: "Games", color: .white)
            statBox(value: "\(performanceTracker.bestStreak)", label: "Best Streak", color: .orange)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(Color.white.opacity(0.05))
        .cornerRadius(12)
        .padding(.horizontal, 16)
    }

    private func statBox(value: String, label: String, color: Color) -> some View {
        VStack(spacing: 4) {
            Text(value).font(.system(size: 20, weight: .black, design: .rounded)).foregroundColor(color)
            Text(label).font(.system(size: 10, weight: .medium)).foregroundColor(.white.opacity(0.5))
        }.frame(maxWidth: .infinity)
    }

    // MARK: - Category Breakdown
    private var categoryBreakdown: some View {
        VStack(spacing: 8) {
            if performanceTracker.categoryStats.isEmpty {
                emptyState("Play some games to see your category breakdown!")
            } else {
                ForEach(performanceTracker.sortedCategories) { cat in
                    categoryRow(cat)
                }
            }
        }
        .padding(.horizontal, 16)
        .padding(.bottom, 30)
    }

    private func categoryRow(_ cat: CategoryPerformance) -> some View {
        let mannaCategory = MannaCategory.byName(cat.category)
        return HStack(spacing: 12) {
            Text(mannaCategory?.emoji ?? "📚").font(.system(size: 20)).frame(width: 30)
            
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(cat.category)
                        .font(.system(size: 13, weight: .semibold, design: .rounded))
                        .foregroundColor(.white)
                        .lineLimit(1)
                    Spacer()
                    Image(systemName: cat.trend.icon)
                        .font(.system(size: 11))
                        .foregroundColor(trendColor(cat.trend))
                    Text("\(Int(cat.score))%")
                        .font(.system(size: 14, weight: .bold, design: .rounded))
                        .foregroundColor(scoreColor(cat.score))
                }
                
                // Progress bar
                GeometryReader { geo in
                    ZStack(alignment: .leading) {
                        RoundedRectangle(cornerRadius: 3)
                            .fill(Color.white.opacity(0.1))
                            .frame(height: 6)
                        RoundedRectangle(cornerRadius: 3)
                            .fill(scoreColor(cat.score))
                            .frame(width: geo.size.width * min(1, cat.score / 100), height: 6)
                    }
                }.frame(height: 6)
                
                Text("\(cat.totalCorrect)/\(cat.totalAnswered) correct")
                    .font(.system(size: 11))
                    .foregroundColor(.white.opacity(0.4))
            }
        }
        .padding(12)
        .background(Color.white.opacity(0.04))
        .cornerRadius(10)
    }

    // MARK: - Difficulty Breakdown
    private var difficultyBreakdown: some View {
        VStack(spacing: 12) {
            if performanceTracker.difficultyStats.isEmpty {
                emptyState("Play some games to see your difficulty breakdown!")
            } else {
                ForEach(["Layperson", "Deacon", "Pastor"], id: \.self) { diff in
                    if let stat = performanceTracker.difficultyStats[diff] {
                        difficultyRow(stat)
                    }
                }
            }
            
            // Recommendation
            if let pastor = performanceTracker.difficultyStats["Pastor"],
               let deacon = performanceTracker.difficultyStats["Deacon"],
               pastor.totalAnswered >= 5 && deacon.totalAnswered >= 5 {
                VStack(spacing: 8) {
                    Text("💡 Recommendation")
                        .font(.system(size: 15, weight: .bold)).foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                    if pastor.score < 40 {
                        Text("Focus on Deacon level to build a strong foundation before tackling Pastor questions.")
                            .font(.system(size: 13)).foregroundColor(.white.opacity(0.6)).multilineTextAlignment(.center)
                    } else if deacon.score > 80 {
                        Text("You're crushing Deacon level! You're ready for more Pastor questions.")
                            .font(.system(size: 13)).foregroundColor(.white.opacity(0.6)).multilineTextAlignment(.center)
                    } else {
                        Text("Keep practicing across all levels. Variety builds the deepest knowledge.")
                            .font(.system(size: 13)).foregroundColor(.white.opacity(0.6)).multilineTextAlignment(.center)
                    }
                }
                .padding(16)
                .background(Color.white.opacity(0.05))
                .cornerRadius(12)
            }
        }
        .padding(.horizontal, 16)
        .padding(.bottom, 30)
    }

    private func difficultyRow(_ stat: DifficultyPerformance) -> some View {
        let level = DifficultyLevel.fromString(stat.difficulty)
        return VStack(spacing: 10) {
            HStack {
                Image(systemName: level?.iconName ?? "book.fill")
                    .foregroundColor(level?.color ?? .white)
                    .font(.system(size: 22))
                VStack(alignment: .leading, spacing: 2) {
                    Text(stat.difficulty)
                        .font(.system(size: 17, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                    Text("\(stat.totalCorrect)/\(stat.totalAnswered) correct")
                        .font(.system(size: 12))
                        .foregroundColor(.white.opacity(0.5))
                }
                Spacer()
                Text("\(Int(stat.score))%")
                    .font(.system(size: 24, weight: .black, design: .rounded))
                    .foregroundColor(scoreColor(stat.score))
            }
            
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 4).fill(Color.white.opacity(0.1)).frame(height: 8)
                    RoundedRectangle(cornerRadius: 4).fill(level?.color ?? .blue)
                        .frame(width: geo.size.width * min(1, stat.score / 100), height: 8)
                }
            }.frame(height: 8)
        }
        .padding(16)
        .background(Color.white.opacity(0.05))
        .cornerRadius(12)
    }

    // MARK: - Study Suggestions
    private var studySuggestions: some View {
        VStack(spacing: 12) {
            let suggestions = performanceTracker.generateSuggestions()
            
            if suggestions.isEmpty {
                emptyState("Play more games to get personalized study suggestions!")
            } else {
                Text("Based on your results, here's where to focus:")
                    .font(.system(size: 13))
                    .foregroundColor(.white.opacity(0.5))
                    .multilineTextAlignment(.center)
                    .padding(.top, 8)
                
                ForEach(suggestions) { suggestion in
                    HStack(alignment: .top, spacing: 12) {
                        Text(suggestion.emoji)
                            .font(.system(size: 28))
                            .frame(width: 40)
                        
                        VStack(alignment: .leading, spacing: 6) {
                            HStack {
                                Text(suggestion.title)
                                    .font(.system(size: 14, weight: .bold, design: .rounded))
                                    .foregroundColor(.white)
                                Spacer()
                                if suggestion.priority == 1 {
                                    Text("Priority")
                                        .font(.system(size: 10, weight: .bold))
                                        .foregroundColor(.black)
                                        .padding(.horizontal, 8)
                                        .padding(.vertical, 3)
                                        .background(Color.red)
                                        .cornerRadius(6)
                                }
                            }
                            Text(suggestion.detail)
                                .font(.system(size: 13))
                                .foregroundColor(.white.opacity(0.6))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    .padding(14)
                    .background(suggestion.priority == 1 ? Color.red.opacity(0.08) : Color.white.opacity(0.04))
                    .overlay(RoundedRectangle(cornerRadius: 12).stroke(suggestion.priority == 1 ? Color.red.opacity(0.2) : Color.clear, lineWidth: 1))
                    .cornerRadius(12)
                }
            }
        }
        .padding(.horizontal, 16)
        .padding(.bottom, 30)
    }

    // MARK: - Helpers
    private func scoreColor(_ score: Double) -> Color {
        if score >= 80 { return .green }
        if score >= 60 { return Color(hex: "#D4A843") ?? .yellow }
        if score >= 40 { return .orange }
        return .red
    }

    private func trendColor(_ trend: Trend) -> Color {
        switch trend {
        case .improving: return .green
        case .declining: return .red
        case .neutral: return .gray
        }
    }

    private func emptyState(_ message: String) -> some View {
        VStack(spacing: 12) {
            Text("📊").font(.system(size: 48)).padding(.top, 40)
            Text(message)
                .font(.system(size: 15))
                .foregroundColor(.white.opacity(0.5))
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
        }
    }
}
