import Foundation

enum PastorSessionFormat: String, Codable, CaseIterable {
    case scriptureMemory
    case originalLanguage
    case churchFather
    case interpretation
    case other
}

extension MannaQuestion {
    var resolvedPastorSessionFormat: PastorSessionFormat {
        if let pastorFormat, let format = PastorSessionFormat(rawValue: pastorFormat) {
            return format
        }

        // Installed legacy packs may predate the explicit metadata. Keep their
        // sessions balanced with a conservative text fallback.
        let prompt = question.lowercased()
        if prompt.contains("church father") || prompt.contains("catena aurea") {
            return .churchFather
        }
        if prompt.contains("hebrew word") || prompt.contains("greek word") ||
            prompt.contains("aramaic word") || prompt.contains("strong's") ||
            prompt.contains("strong’s") {
            return .originalLanguage
        }
        if prompt.hasPrefix("complete") || prompt.contains("which passage") ||
            prompt.contains("which gospel verse") || prompt.contains("where is this verse") ||
            prompt.contains("where in the bible") || prompt.contains("cross-reference") {
            return .scriptureMemory
        }
        if prompt.contains("what ot concept") || prompt.contains("what connects") ||
            prompt.contains("what type of connection") || prompt.contains("symbolize") ||
            prompt.contains("symbolise") || prompt.contains("interpretation") ||
            prompt.contains("significance") {
            return .interpretation
        }
        return .other
    }
}

enum PastorSessionBalancer {
    // Every five-question block limits exact-text/reference recall to one item
    // and reserves two places for interpretation or synthesis. The remaining
    // specialist slots rotate so ten- and twenty-question Party games retain
    // language, patristic, and other advanced material without letting one
    // template dominate.
    private static let blockTemplates: [[PastorSessionFormat]] = [
        [.scriptureMemory, .interpretation, .originalLanguage, .interpretation, .other],
        [.scriptureMemory, .interpretation, .originalLanguage, .interpretation, .churchFather],
        [.scriptureMemory, .interpretation, .other, .interpretation, .churchFather],
        [.scriptureMemory, .interpretation, .originalLanguage, .interpretation, .other]
    ]

    static func balanced(_ questions: [MannaQuestion]) -> [MannaQuestion] {
        guard !questions.isEmpty else { return [] }
        var buckets = Dictionary(
            grouping: questions.shuffled(),
            by: \.resolvedPastorSessionFormat
        )
        var result: [MannaQuestion] = []
        result.reserveCapacity(questions.count)
        var blockIndex = 0

        while result.count < questions.count {
            let template = blockTemplates[blockIndex % blockTemplates.count]
            var block: [MannaQuestion] = []
            for preferred in template where result.count + block.count < questions.count {
                if let question = pop(preferred, from: &buckets) ?? popLargest(from: &buckets) {
                    block.append(question)
                }
            }
            guard !block.isEmpty else { break }
            result.append(contentsOf: block.shuffled())
            blockIndex += 1
        }
        return result
    }

    private static func pop(
        _ format: PastorSessionFormat,
        from buckets: inout [PastorSessionFormat: [MannaQuestion]]
    ) -> MannaQuestion? {
        guard var bucket = buckets[format], let question = bucket.popLast() else {
            return nil
        }
        buckets[format] = bucket
        return question
    }

    private static func popLargest(
        from buckets: inout [PastorSessionFormat: [MannaQuestion]]
    ) -> MannaQuestion? {
        let fallback = PastorSessionFormat.allCases.max { left, right in
            let leftCount = buckets[left]?.count ?? 0
            let rightCount = buckets[right]?.count ?? 0
            if leftCount == rightCount {
                return left.rawValue < right.rawValue
            }
            return leftCount < rightCount
        }
        guard let fallback else { return nil }
        return pop(fallback, from: &buckets)
    }
}
