import Foundation

enum QuestionPackStore {
    static let expectedQuestionCount = 10_000
    static let installedNotification = Notification.Name("manna.questionPackInstalled")

    private static var fileURL: URL? {
        guard let support = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first else { return nil }
        return support.appendingPathComponent("Manna", isDirectory: true)
            .appendingPathComponent("question-pack-10000-v1.json")
    }

    static var isInstalled: Bool {
        guard let fileURL else { return false }
        return FileManager.default.fileExists(atPath: fileURL.path)
    }

    static func loadInstalledQuestions() -> [MannaQuestion] {
        guard let fileURL, let data = try? Data(contentsOf: fileURL) else { return [] }
        return (try? validatedQuestions(from: data)) ?? []
    }

    static func downloadAndInstall(from remoteURL: URL) async throws -> [MannaQuestion] {
        let (data, response) = try await URLSession.shared.data(from: remoteURL)
        guard let http = response as? HTTPURLResponse, (200...299).contains(http.statusCode) else {
            throw PackError.downloadFailed
        }
        let questions = try validatedQuestions(from: data)
        guard let fileURL else { throw PackError.storageUnavailable }
        try FileManager.default.createDirectory(at: fileURL.deletingLastPathComponent(), withIntermediateDirectories: true)
        try data.write(to: fileURL, options: .atomic)
        NotificationCenter.default.post(name: installedNotification, object: questions)
        return questions
    }

    private static func validatedQuestions(from data: Data) throws -> [MannaQuestion] {
        let questions = try JSONDecoder().decode([MannaQuestion].self, from: data)
        guard questions.count == expectedQuestionCount,
              Set(questions.map(\.id)).count == questions.count,
              questions.allSatisfy({ !$0.id.isEmpty && !$0.question.isEmpty && $0.options.count >= 2 && $0.options.contains($0.correct) }) else {
            throw PackError.invalidContents
        }
        return questions
    }

    enum PackError: LocalizedError {
        case downloadFailed, invalidContents, storageUnavailable

        var errorDescription: String? {
            switch self {
            case .downloadFailed: "The extra question pack could not be downloaded. Please try again."
            case .invalidContents: "The downloaded question pack did not pass validation."
            case .storageUnavailable: "Manna could not save the extra question pack on this device."
            }
        }
    }
}
