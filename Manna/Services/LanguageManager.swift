import Foundation
import Translation

struct LocalizedQuestionContent {
    let id: String
    let category: String
    let question: String
    let options: [String]
    let explanation: String
}

@MainActor
final class LanguageManager: ObservableObject {
    enum AppLanguage: String, CaseIterable, Identifiable {
        case english = "en", arabic = "ar-AE", chinese = "zh", danish = "da"
        case dutch = "nl", french = "fr", german = "de", hindi = "hi"
        case indonesian = "id", italian = "it", japanese = "ja", korean = "ko"
        case norwegian = "nb", polish = "pl", portuguese = "pt", russian = "ru"
        case spanish = "es", swedish = "sv", thai = "th", turkish = "tr"
        case ukrainian = "uk", vietnamese = "vi"

        var id: String { rawValue }
        var name: String {
            switch self {
            case .english: "English"
            case .danish: "Dansk"
            case .dutch: "Nederlands"
            case .spanish: "Español"
            case .french: "Français"
            case .german: "Deutsch"
            case .italian: "Italiano"
            case .portuguese: "Português"
            case .polish: "Polski"
            case .arabic: "العربية"
            case .turkish: "Türkçe"
            case .chinese: "简体中文"
            case .japanese: "日本語"
            case .korean: "한국어"
            case .hindi: "हिन्दी"
            case .indonesian: "Bahasa Indonesia"
            case .norwegian: "Norsk bokmål"
            case .russian: "Русский"
            case .swedish: "Svenska"
            case .thai: "ไทย"
            case .ukrainian: "Українська"
            case .vietnamese: "Tiếng Việt"
            }
        }
        var englishName: String {
            switch self {
            case .english: "English"
            case .danish: "Danish"
            case .dutch: "Dutch"
            case .spanish: "Spanish"
            case .french: "French"
            case .german: "German"
            case .italian: "Italian"
            case .portuguese: "Portuguese"
            case .polish: "Polish"
            case .arabic: "Arabic"
            case .turkish: "Turkish"
            case .chinese: "Simplified Chinese"
            case .japanese: "Japanese"
            case .korean: "Korean"
            case .hindi: "Hindi"
            case .indonesian: "Indonesian"
            case .norwegian: "Norwegian"
            case .russian: "Russian"
            case .swedish: "Swedish"
            case .thai: "Thai"
            case .ukrainian: "Ukrainian"
            case .vietnamese: "Vietnamese"
            }
        }
        var displayName: String { self == .english ? englishName : "\(englishName) · \(name)" }
    }

    @Published var selected: AppLanguage {
        didSet {
            UserDefaults.standard.set(selected.rawValue, forKey: "manna_language")
            localizedQuestion = nil
            translationError = nil
        }
    }
    @Published private(set) var localizedQuestion: LocalizedQuestionContent?
    @Published private(set) var isTranslating = false
    @Published private(set) var translationError: String?
    @Published var translationConfiguration: TranslationSession.Configuration?
    private var cache: [String: LocalizedQuestionContent] = [:]

    init() {
        let stored = UserDefaults.standard.string(forKey: "manna_language") ?? "en"
        let migrated = ["ar": "ar-AE", "zh-Hans": "zh"][stored] ?? stored
        selected = AppLanguage(rawValue: migrated) ?? .english
    }

    func prepare(_ question: MannaQuestion?) {
        localizedQuestion = nil
        translationError = nil
        guard selected != .english, let question else {
            translationConfiguration = nil
            isTranslating = false
            return
        }
        if let cached = cache["\(selected.rawValue):\(question.id)"] {
            localizedQuestion = cached
            translationConfiguration = nil
            isTranslating = false
            return
        }
        var configuration = TranslationSession.Configuration(
            source: Locale.Language(identifier: "en"),
            target: Locale.Language(identifier: selected.rawValue)
        )
        configuration.invalidate()
        translationConfiguration = configuration
        isTranslating = true
    }

    func translate(_ question: MannaQuestion, using session: TranslationSession) async {
        guard selected != .english else { return }
        var requests = [
            TranslationSession.Request(sourceText: question.category, clientIdentifier: "category"),
            TranslationSession.Request(sourceText: question.question, clientIdentifier: "question")
        ]
        requests += question.options.enumerated().map {
            TranslationSession.Request(sourceText: $0.element, clientIdentifier: "option_\($0.offset)")
        }
        if !question.explanation.isEmpty {
            requests.append(.init(sourceText: question.explanation, clientIdentifier: "explanation"))
        }
        do {
            let responses = try await session.translations(from: requests)
            let values = Dictionary(uniqueKeysWithValues: responses.compactMap { response in
                response.clientIdentifier.map { ($0, response.targetText) }
            })
            let content = LocalizedQuestionContent(
                id: question.id,
                category: values["category"] ?? question.category,
                question: values["question"] ?? question.question,
                options: question.options.indices.map { values["option_\($0)"] ?? question.options[$0] },
                explanation: values["explanation"] ?? question.explanation
            )
            cache["\(selected.rawValue):\(question.id)"] = content
            localizedQuestion = content
            isTranslating = false
        } catch {
            translationError = error.localizedDescription
            isTranslating = false
        }
    }

    func ui(_ key: String) -> String {
        let table: [String: [AppLanguage: String]] = [
            "play": [.arabic:"العب",.chinese:"开始",.danish:"SPIL",.dutch:"SPELEN",.french:"JOUER",.german:"SPIELEN",.hindi:"खेलें",.indonesian:"MAIN",.italian:"GIOCA",.japanese:"プレイ",.korean:"플레이",.norwegian:"SPILL",.polish:"GRAJ",.portuguese:"JOGAR",.russian:"ИГРАТЬ",.spanish:"JUGAR",.swedish:"SPELA",.thai:"เล่น",.turkish:"OYNA",.ukrainian:"ГРАТИ",.vietnamese:"CHƠI"],
            "stats": [.arabic:"إحصاءاتي",.chinese:"我的统计",.danish:"Min statistik",.dutch:"Mijn statistieken",.french:"Mes statistiques",.german:"Meine Statistik",.hindi:"मेरे आँकड़े",.indonesian:"Statistik saya",.italian:"Statistiche",.japanese:"成績",.korean:"내 통계",.norwegian:"Min statistikk",.polish:"Statystyki",.portuguese:"Estatísticas",.russian:"Моя статистика",.spanish:"Mis estadísticas",.swedish:"Min statistik",.thai:"สถิติของฉัน",.turkish:"İstatistiklerim",.ukrainian:"Моя статистика",.vietnamese:"Thống kê của tôi"],
            "settings": [.arabic:"الإعدادات",.chinese:"设置",.danish:"Indstillinger",.dutch:"Instellingen",.french:"Réglages",.german:"Einstellungen",.hindi:"सेटिंग्स",.indonesian:"Pengaturan",.italian:"Impostazioni",.japanese:"設定",.korean:"설정",.norwegian:"Innstillinger",.polish:"Ustawienia",.portuguese:"Definições",.russian:"Настройки",.spanish:"Ajustes",.swedish:"Inställningar",.thai:"การตั้งค่า",.turkish:"Ayarlar",.ukrainian:"Налаштування",.vietnamese:"Cài đặt"],
            "language": [.arabic:"اللغة",.chinese:"语言",.danish:"Sprog",.dutch:"Taal",.french:"Langue",.german:"Sprache",.hindi:"भाषा",.indonesian:"Bahasa",.italian:"Lingua",.japanese:"言語",.korean:"언어",.norwegian:"Språk",.polish:"Język",.portuguese:"Idioma",.russian:"Язык",.spanish:"Idioma",.swedish:"Språk",.thai:"ภาษา",.turkish:"Dil",.ukrainian:"Мова",.vietnamese:"Ngôn ngữ"],
            "show_answer": [.arabic:"أظهر الإجابة",.chinese:"显示答案",.danish:"Vis svar",.dutch:"Toon antwoord",.french:"Afficher la réponse",.german:"Antwort anzeigen",.hindi:"उत्तर दिखाएँ",.indonesian:"Tampilkan jawaban",.italian:"Mostra risposta",.japanese:"答えを見る",.korean:"정답 보기",.norwegian:"Vis svar",.polish:"Pokaż odpowiedź",.portuguese:"Mostrar resposta",.russian:"Показать ответ",.spanish:"Mostrar respuesta",.swedish:"Visa svar",.thai:"แสดงคำตอบ",.turkish:"Cevabı göster",.ukrainian:"Показати відповідь",.vietnamese:"Hiển thị đáp án"],
            "next": [.arabic:"التالي",.chinese:"下一题",.danish:"Næste spørgsmål",.dutch:"Volgende vraag",.french:"Suivante",.german:"Weiter",.hindi:"अगला",.indonesian:"Pertanyaan berikutnya",.italian:"Avanti",.japanese:"次へ",.korean:"다음",.norwegian:"Neste spørsmål",.polish:"Dalej",.portuguese:"Seguinte",.russian:"Следующий вопрос",.spanish:"Siguiente",.swedish:"Nästa fråga",.thai:"คำถามถัดไป",.turkish:"Sonraki",.ukrainian:"Наступне запитання",.vietnamese:"Câu hỏi tiếp theo"],
            "results": [.arabic:"عرض النتائج",.chinese:"查看结果",.danish:"Se resultater",.dutch:"Bekijk resultaten",.french:"Voir les résultats",.german:"Ergebnisse",.hindi:"परिणाम देखें",.indonesian:"Lihat hasil",.italian:"Vedi risultati",.japanese:"結果を見る",.korean:"결과 보기",.norwegian:"Se resultater",.polish:"Wyniki",.portuguese:"Ver resultados",.russian:"Посмотреть результаты",.spanish:"Ver resultados",.swedish:"Visa resultat",.thai:"ดูผลลัพธ์",.turkish:"Sonuçlar",.ukrainian:"Переглянути результати",.vietnamese:"Xem kết quả"],
            "check_updates": [.arabic:"التحقق من التحديثات",.chinese:"检查更新",.danish:"Søg efter opdateringer",.dutch:"Controleren op updates",.french:"Rechercher des mises à jour",.german:"Nach Updates suchen",.hindi:"अपडेट जाँचें",.indonesian:"Periksa pembaruan",.italian:"Controlla aggiornamenti",.japanese:"アップデートを確認",.korean:"업데이트 확인",.norwegian:"Se etter oppdateringer",.polish:"Sprawdź aktualizacje",.portuguese:"Procurar atualizações",.russian:"Проверить обновления",.spanish:"Buscar actualizaciones",.swedish:"Sök efter uppdateringar",.thai:"ตรวจสอบการอัปเดต",.turkish:"Güncellemeleri denetle",.ukrainian:"Перевірити оновлення",.vietnamese:"Kiểm tra cập nhật"]
        ]
        return table[key]?[selected] ?? ["play":"PLAY", "stats":"My Stats", "settings":"Settings", "language":"Language", "show_answer":"Show Answer", "next":"Next Question", "results":"See Results", "check_updates":"Check for Updates"][key] ?? key
    }
}
