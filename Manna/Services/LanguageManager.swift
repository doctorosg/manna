import Foundation
import SwiftUI
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

        var continueTitle: String {
            switch self {
            case .english: "Continue"
            case .arabic: "متابعة"
            case .chinese: "继续"
            case .danish: "Fortsæt"
            case .dutch: "Doorgaan"
            case .french: "Continuer"
            case .german: "Weiter"
            case .hindi: "जारी रखें"
            case .indonesian: "Lanjutkan"
            case .italian: "Continua"
            case .japanese: "続ける"
            case .korean: "계속"
            case .norwegian: "Fortsett"
            case .polish: "Kontynuuj"
            case .portuguese: "Continuar"
            case .russian: "Продолжить"
            case .spanish: "Continuar"
            case .swedish: "Fortsätt"
            case .thai: "ดำเนินการต่อ"
            case .turkish: "Devam et"
            case .ukrainian: "Продовжити"
            case .vietnamese: "Tiếp tục"
            }
        }

        var downloadTitle: String {
            switch self {
            case .english: "Download language"
            case .arabic: "تنزيل اللغة"
            case .chinese: "下载语言"
            case .danish: "Download sprog"
            case .dutch: "Taal downloaden"
            case .french: "Télécharger la langue"
            case .german: "Sprache laden"
            case .hindi: "भाषा डाउनलोड करें"
            case .indonesian: "Unduh bahasa"
            case .italian: "Scarica lingua"
            case .japanese: "言語をダウンロード"
            case .korean: "언어 다운로드"
            case .norwegian: "Last ned språk"
            case .polish: "Pobierz język"
            case .portuguese: "Transferir idioma"
            case .russian: "Скачать язык"
            case .spanish: "Descargar idioma"
            case .swedish: "Ladda ned språk"
            case .thai: "ดาวน์โหลดภาษา"
            case .turkish: "Dili indir"
            case .ukrainian: "Завантажити мову"
            case .vietnamese: "Tải ngôn ngữ"
            }
        }

        var downloadingTitle: String {
            switch self {
            case .english: "Downloading…"
            case .arabic: "جارٍ التنزيل…"
            case .chinese: "正在下载…"
            case .danish: "Downloader…"
            case .dutch: "Downloaden…"
            case .french: "Téléchargement…"
            case .german: "Wird geladen…"
            case .hindi: "डाउनलोड हो रहा है…"
            case .indonesian: "Mengunduh…"
            case .italian: "Download…"
            case .japanese: "ダウンロード中…"
            case .korean: "다운로드 중…"
            case .norwegian: "Laster ned…"
            case .polish: "Pobieranie…"
            case .portuguese: "A transferir…"
            case .russian: "Загрузка…"
            case .spanish: "Descargando…"
            case .swedish: "Laddar ned…"
            case .thai: "กำลังดาวน์โหลด…"
            case .turkish: "İndiriliyor…"
            case .ukrainian: "Завантаження…"
            case .vietnamese: "Đang tải…"
            }
        }
    }

    @Published var selected: AppLanguage {
        didSet {
            UserDefaults.standard.set(selected.rawValue, forKey: "manna_language")
            localizedQuestion = nil
            translationError = nil
        }
    }
    @Published private(set) var hasCompletedLanguageSetup: Bool
    @Published private(set) var localizedQuestion: LocalizedQuestionContent?
    @Published private(set) var isTranslating = false
    @Published private(set) var translationError: String?
    @Published var translationConfiguration: TranslationSession.Configuration?
    private var cache: [String: LocalizedQuestionContent] = [:]
    private var interfaceCache: [String: String]
    private static let interfaceCacheKey = "manna_interface_translation_cache_v1"

    init() {
        let stored = UserDefaults.standard.string(forKey: "manna_language")
        selected = stored.flatMap(Self.language(for:)) ?? Self.detectedDeviceLanguage()
        hasCompletedLanguageSetup = UserDefaults.standard.bool(forKey: "manna_language_setup_complete")
        interfaceCache = UserDefaults.standard.dictionary(forKey: Self.interfaceCacheKey) as? [String: String] ?? [:]
    }

    func completeLanguageSetup() {
        hasCompletedLanguageSetup = true
        UserDefaults.standard.set(true, forKey: "manna_language_setup_complete")
    }

    private static func detectedDeviceLanguage() -> AppLanguage {
        for identifier in Locale.preferredLanguages {
            if let language = language(for: identifier) { return language }
        }
        return .english
    }

    private static func language(for identifier: String) -> AppLanguage? {
        let normalized = identifier.replacingOccurrences(of: "_", with: "-").lowercased()
        let code = normalized.split(separator: "-").first.map(String.init) ?? normalized
        switch code {
        case "ar": return .arabic
        case "zh": return .chinese
        case "da": return .danish
        case "nl": return .dutch
        case "fr": return .french
        case "de": return .german
        case "hi": return .hindi
        case "id": return .indonesian
        case "it": return .italian
        case "ja": return .japanese
        case "ko": return .korean
        case "nb", "nn", "no": return .norwegian
        case "pl": return .polish
        case "pt": return .portuguese
        case "ru": return .russian
        case "es": return .spanish
        case "sv": return .swedish
        case "th": return .thai
        case "tr": return .turkish
        case "uk": return .ukrainian
        case "vi": return .vietnamese
        case "en": return .english
        default: return nil
        }
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
            "party": [.arabic:"وضع المجموعة",.chinese:"聚会模式",.danish:"Gruppespil",.dutch:"Groepsmodus",.french:"Mode groupe",.german:"Gruppenmodus",.hindi:"समूह मोड",.indonesian:"Mode Grup",.italian:"Modalità gruppo",.japanese:"グループモード",.korean:"그룹 모드",.norwegian:"Gruppemodus",.polish:"Tryb grupowy",.portuguese:"Modo de grupo",.russian:"Групповой режим",.spanish:"Modo de grupo",.swedish:"Gruppläge",.thai:"โหมดกลุ่ม",.turkish:"Grup Modu",.ukrainian:"Груповий режим",.vietnamese:"Chế độ nhóm"],
            "show_answer": [.arabic:"أظهر الإجابة",.chinese:"显示答案",.danish:"Vis svar",.dutch:"Toon antwoord",.french:"Afficher la réponse",.german:"Antwort anzeigen",.hindi:"उत्तर दिखाएँ",.indonesian:"Tampilkan jawaban",.italian:"Mostra risposta",.japanese:"答えを見る",.korean:"정답 보기",.norwegian:"Vis svar",.polish:"Pokaż odpowiedź",.portuguese:"Mostrar resposta",.russian:"Показать ответ",.spanish:"Mostrar respuesta",.swedish:"Visa svar",.thai:"แสดงคำตอบ",.turkish:"Cevabı göster",.ukrainian:"Показати відповідь",.vietnamese:"Hiển thị đáp án"],
            "next": [.arabic:"التالي",.chinese:"下一题",.danish:"Næste spørgsmål",.dutch:"Volgende vraag",.french:"Suivante",.german:"Weiter",.hindi:"अगला",.indonesian:"Pertanyaan berikutnya",.italian:"Avanti",.japanese:"次へ",.korean:"다음",.norwegian:"Neste spørsmål",.polish:"Dalej",.portuguese:"Seguinte",.russian:"Следующий вопрос",.spanish:"Siguiente",.swedish:"Nästa fråga",.thai:"คำถามถัดไป",.turkish:"Sonraki",.ukrainian:"Наступне запитання",.vietnamese:"Câu hỏi tiếp theo"],
            "results": [.arabic:"عرض النتائج",.chinese:"查看结果",.danish:"Se resultater",.dutch:"Bekijk resultaten",.french:"Voir les résultats",.german:"Ergebnisse",.hindi:"परिणाम देखें",.indonesian:"Lihat hasil",.italian:"Vedi risultati",.japanese:"結果を見る",.korean:"결과 보기",.norwegian:"Se resultater",.polish:"Wyniki",.portuguese:"Ver resultados",.russian:"Посмотреть результаты",.spanish:"Ver resultados",.swedish:"Visa resultat",.thai:"ดูผลลัพธ์",.turkish:"Sonuçlar",.ukrainian:"Переглянути результати",.vietnamese:"Xem kết quả"],
            "check_updates": [.arabic:"التحقق من التحديثات",.chinese:"检查更新",.danish:"Søg efter opdateringer",.dutch:"Controleren op updates",.french:"Rechercher des mises à jour",.german:"Nach Updates suchen",.hindi:"अपडेट जाँचें",.indonesian:"Periksa pembaruan",.italian:"Controlla aggiornamenti",.japanese:"アップデートを確認",.korean:"업데이트 확인",.norwegian:"Se etter oppdateringer",.polish:"Sprawdź aktualizacje",.portuguese:"Procurar atualizações",.russian:"Проверить обновления",.spanish:"Buscar actualizaciones",.swedish:"Sök efter uppdateringar",.thai:"ตรวจสอบการอัปเดต",.turkish:"Güncellemeleri denetle",.ukrainian:"Перевірити оновлення",.vietnamese:"Kiểm tra cập nhật"]
        ]
        return table[key]?[selected] ?? ["play":"PLAY", "stats":"My Stats", "settings":"Settings", "language":"Language", "party":"Party Mode", "show_answer":"Show Answer", "next":"Next Question", "results":"See Results", "check_updates":"Check for Updates"][key] ?? key
    }

    func cachedInterfaceTranslation(for source: String, language: AppLanguage) -> String? {
        guard language != .english else { return source }
        return interfaceCache[interfaceCacheKey(for: source, language: language)]
    }

    func interfaceString(_ source: String) -> String {
        cachedInterfaceTranslation(for: source, language: selected) ?? source
    }

    func storeInterfaceTranslation(_ translation: String, for source: String, language: AppLanguage) {
        guard language != .english, !translation.isEmpty else { return }
        interfaceCache[interfaceCacheKey(for: source, language: language)] = translation
        UserDefaults.standard.set(interfaceCache, forKey: Self.interfaceCacheKey)
    }

    private func interfaceCacheKey(for source: String, language: AppLanguage) -> String {
        "\(language.rawValue)|\(source)"
    }
}

/// Translates any visible app copy through Apple's on-device Translation framework.
/// Question content uses the same English-to-selected-language route in `LanguageManager.translate`.
struct MannaText: View {
    @EnvironmentObject private var languageManager: LanguageManager
    private let source: String
    @State private var displayed: String
    @State private var configuration: TranslationSession.Configuration?

    init(_ source: String) {
        self.source = source
        _displayed = State(initialValue: source)
    }

    var body: some View {
        Text(displayed)
            .task(id: "\(languageManager.selected.rawValue)|\(source)") {
                prepareTranslation()
            }
            .translationTask(configuration) { session in
                await translate(using: session)
            }
    }

    private func prepareTranslation() {
        let language = languageManager.selected
        guard language != .english, source.rangeOfCharacter(from: .letters) != nil else {
            displayed = source
            configuration = nil
            return
        }
        if let cached = languageManager.cachedInterfaceTranslation(for: source, language: language) {
            displayed = cached
            configuration = nil
            return
        }
        displayed = "…"
        var next = TranslationSession.Configuration(
            source: Locale.Language(identifier: "en"),
            target: Locale.Language(identifier: language.rawValue)
        )
        next.invalidate()
        configuration = next
    }

    private func translate(using session: TranslationSession) async {
        let language = languageManager.selected
        guard language != .english else { return }
        do {
            let responses = try await session.translations(from: [
                .init(sourceText: source, clientIdentifier: "interface")
            ])
            guard language == languageManager.selected,
                  let translated = responses.first?.targetText,
                  !translated.isEmpty else { return }
            languageManager.storeInterfaceTranslation(translated, for: source, language: language)
            displayed = translated
        } catch {
            guard language == languageManager.selected else { return }
            displayed = source
        }
    }
}

struct MannaLabel: View {
    let source: String
    let systemImage: String

    init(_ source: String, systemImage: String) {
        self.source = source
        self.systemImage = systemImage
    }

    var body: some View {
        Label {
            MannaText(source)
        } icon: {
            Image(systemName: systemImage)
        }
    }
}

private struct MannaAccessibilityLabelModifier: ViewModifier {
    @EnvironmentObject private var languageManager: LanguageManager
    let source: String

    func body(content: Content) -> some View {
        content
            .accessibilityLabel(Text(languageManager.interfaceString(source)))
            .background { MannaText(source).hidden() }
    }
}

extension View {
    func mannaAccessibilityLabel(_ source: String) -> some View {
        modifier(MannaAccessibilityLabelModifier(source: source))
    }
}

private enum LanguagePackState: Equatable {
    case checking
    case supported
    case downloading
    case installed
    case unsupported
    case failed
}

/// A first-launch gate whose essential copy is bundled rather than dynamically translated.
/// This lets a person select and download a language before the rest of the app appears.
struct LanguageSetupView: View {
    @EnvironmentObject private var languageManager: LanguageManager
    @State private var state: LanguagePackState = .checking
    @State private var configuration: TranslationSession.Configuration?

    var body: some View {
        ZStack {
            Color(red: 0.06, green: 0.07, blue: 0.13).ignoresSafeArea()
            VStack(spacing: 24) {
                Spacer()
                Image(systemName: "globe")
                    .font(.system(size: 56, weight: .semibold))
                    .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                Text(languageManager.ui("language"))
                    .font(.system(size: 30, weight: .bold, design: .rounded))
                    .foregroundColor(.white)

                Picker(languageManager.ui("language"), selection: $languageManager.selected) {
                    ForEach(LanguageManager.AppLanguage.allCases) { language in
                        Text(language.name).tag(language)
                    }
                }
                .pickerStyle(.menu)
                .tint(.white)
                .padding(.horizontal, 20)
                .frame(maxWidth: 420, minHeight: 58)
                .background(Color.white.opacity(0.08))
                .clipShape(RoundedRectangle(cornerRadius: 14))

                if state == .unsupported || state == .failed {
                    Text("⚠︎  \(languageManager.selected.name)")
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.orange)
                }

                Spacer()

                Button(action: primaryAction) {
                    HStack(spacing: 10) {
                        if state == .checking || state == .downloading {
                            ProgressView().tint(.black)
                        } else {
                            Image(systemName: state == .installed || languageManager.selected == .english ? "checkmark.circle.fill" : "arrow.down.circle.fill")
                        }
                        Text(primaryTitle)
                            .font(.system(size: 18, weight: .bold, design: .rounded))
                    }
                    .foregroundColor(.black)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 17)
                    .background(Color(hex: "#D4A843") ?? .yellow)
                    .clipShape(RoundedRectangle(cornerRadius: 15))
                }
                .disabled(state == .checking || state == .downloading || state == .unsupported)
                .padding(.horizontal, 28)
                .padding(.bottom, 28)
            }
        }
        .task(id: languageManager.selected) { await refreshStatus() }
        .translationTask(configuration) { session in
            state = .downloading
            do {
                try await session.prepareTranslation()
                state = .installed
                languageManager.completeLanguageSetup()
            } catch {
                state = .failed
            }
            configuration = nil
        }
    }

    private var primaryTitle: String {
        switch state {
        case .checking, .downloading: languageManager.selected.downloadingTitle
        case .installed: languageManager.selected.continueTitle
        case .supported, .failed: languageManager.selected.downloadTitle
        case .unsupported: languageManager.selected.name
        }
    }

    private func primaryAction() {
        if languageManager.selected == .english || state == .installed {
            languageManager.completeLanguageSetup()
        } else {
            configuration = TranslationSession.Configuration(
                source: Locale.Language(identifier: "en"),
                target: Locale.Language(identifier: languageManager.selected.rawValue)
            )
        }
    }

    private func refreshStatus() async {
        configuration = nil
        guard languageManager.selected != .english else {
            state = .installed
            return
        }
        state = .checking
        let status = await LanguageAvailability().status(
            from: Locale.Language(identifier: "en"),
            to: Locale.Language(identifier: languageManager.selected.rawValue)
        )
        guard !Task.isCancelled else { return }
        switch status {
        case .installed: state = .installed
        case .supported: state = .supported
        case .unsupported: state = .unsupported
        @unknown default: state = .unsupported
        }
    }
}

struct LanguagePackManagerView: View {
    @EnvironmentObject private var languageManager: LanguageManager
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            List(LanguageManager.AppLanguage.allCases) { language in
                LanguagePackRow(language: language)
            }
            .scrollContentBackground(.hidden)
            .background(Color(red: 0.06, green: 0.07, blue: 0.13))
            .navigationTitle(languageManager.ui("language"))
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button(action: { dismiss() }) {
                        Image(systemName: "xmark.circle.fill")
                    }
                }
            }
        }
        .preferredColorScheme(.dark)
    }
}

private struct LanguagePackRow: View {
    @EnvironmentObject private var languageManager: LanguageManager
    let language: LanguageManager.AppLanguage
    @State private var state: LanguagePackState = .checking
    @State private var configuration: TranslationSession.Configuration?

    var body: some View {
        HStack(spacing: 14) {
            VStack(alignment: .leading, spacing: 3) {
                Text(language.name).font(.system(size: 17, weight: .semibold))
                if language == languageManager.selected {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                        .accessibilityHidden(true)
                }
            }
            Spacer()
            switch state {
            case .checking, .downloading:
                ProgressView()
            case .installed:
                Button(action: { languageManager.selected = language }) {
                    Image(systemName: "checkmark.icloud.fill").foregroundColor(.green)
                }
            case .supported, .failed:
                Button(action: startDownload) {
                    Image(systemName: "arrow.down.circle.fill")
                        .font(.system(size: 24))
                        .foregroundColor(Color(hex: "#D4A843") ?? .yellow)
                }
            case .unsupported:
                Image(systemName: "exclamationmark.triangle.fill").foregroundColor(.orange)
            }
        }
        .padding(.vertical, 5)
        .task(id: language) { await refreshStatus() }
        .translationTask(configuration) { session in
            state = .downloading
            do {
                try await session.prepareTranslation()
                state = .installed
                languageManager.selected = language
            } catch {
                state = .failed
            }
            configuration = nil
        }
    }

    private func startDownload() {
        configuration = TranslationSession.Configuration(
            source: Locale.Language(identifier: "en"),
            target: Locale.Language(identifier: language.rawValue)
        )
    }

    private func refreshStatus() async {
        guard language != .english else {
            state = .installed
            return
        }
        state = .checking
        let status = await LanguageAvailability().status(
            from: Locale.Language(identifier: "en"),
            to: Locale.Language(identifier: language.rawValue)
        )
        guard !Task.isCancelled else { return }
        switch status {
        case .installed: state = .installed
        case .supported: state = .supported
        case .unsupported: state = .unsupported
        @unknown default: state = .unsupported
        }
    }
}
