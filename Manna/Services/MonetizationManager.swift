import Foundation
import GoogleMobileAds
import Network
import StoreKit
import SwiftUI
import UIKit
import UserMessagingPlatform

@MainActor
final class MonetizationManager: NSObject, ObservableObject, FullScreenContentDelegate {
    static let fullScreenAdsBeginAfter = 40
    static let interstitialQuestionInterval = 10

    fileprivate static func adUnitID(infoKey: String, debugSampleID: String) -> String {
        #if DEBUG
        return debugSampleID
        #else
        guard let value = Bundle.main.object(forInfoDictionaryKey: infoKey) as? String,
              !value.isEmpty else {
            preconditionFailure("Missing production AdMob unit ID for \(infoKey)")
        }
        return value
        #endif
    }

    @Published private(set) var hasPurchasedAdFree = false
    @Published private(set) var hasPurchasedQuestionPack = false
    @Published private(set) var removeAdsProduct: Product?
    @Published private(set) var questionPackProduct: Product?
    @Published private(set) var purchaseMessage: String?
    @Published private(set) var isPurchasing = false
    @Published private(set) var privacyOptionsRequired = false
    @Published private(set) var isOnline = true
    @Published private(set) var freeQuestionsUsed = 0
    @Published private(set) var isChildDirectedSession = false

    private let defaults = UserDefaults.standard
    private let freeQuestionsUsedKey = "manna.freeQuestionsUsed"
    private let lastFreeQuestionIDKey = "manna.lastFreeQuestionID"
    private let regularAnswerCountKey = "manna.regularAnswerCount"
    private let adSupportedAnswerCountKey = "manna.adSupportedAnswerCount"
    private let purchasedEntitlementKey = "manna.hasVerifiedAdFreePurchase"
    private let questionPackEntitlementKey = "manna.hasVerifiedQuestionPackPurchase"
    private let productID: String
    private let questionPackProductID: String
    private let questionPackURL: URL?
    private var rewardedAd: RewardedAd?
    private var interstitialAd: InterstitialAd?
    private var pendingFullScreenCompletion: ((Bool) -> Void)?
    private var rewardEarned = false
    private var lastFullScreenAdDate: Date?
    private var transactionListener: Task<Void, Never>?
    private let networkMonitor = NWPathMonitor()
    private let networkQueue = DispatchQueue(label: "com.oddcurrent.manna.network")
    private var networkStatusKnown = false

    var shouldShowAds: Bool {
        !hasPurchasedAdFree
    }

    var shouldExplainAdvertising: Bool { !hasPurchasedAdFree }
    var requiresInternetAccess: Bool { !hasPurchasedAdFree && !isOnline }
    var purchasePrice: String { removeAdsProduct?.displayPrice ?? "one-time purchase" }

    override init() {
        productID = Bundle.main.object(forInfoDictionaryKey: "MannaRemoveAdsProductID") as? String
            ?? "com.oddcurrent.manna.remove_ads"
        questionPackProductID = Bundle.main.object(forInfoDictionaryKey: "MannaQuestionPackProductID") as? String
            ?? "com.oddcurrent.manna.question_pack_10000"
        questionPackURL = (Bundle.main.object(forInfoDictionaryKey: "MannaQuestionPackURL") as? String).flatMap(URL.init(string:))
        super.init()
        hasPurchasedAdFree = defaults.bool(forKey: purchasedEntitlementKey)
        hasPurchasedQuestionPack = defaults.bool(forKey: questionPackEntitlementKey)
        if defaults.object(forKey: freeQuestionsUsedKey) != nil {
            freeQuestionsUsed = defaults.integer(forKey: freeQuestionsUsedKey)
        } else {
            freeQuestionsUsed = defaults.integer(forKey: regularAnswerCountKey)
            defaults.set(freeQuestionsUsed, forKey: freeQuestionsUsedKey)
        }

        networkMonitor.pathUpdateHandler = { [weak self] path in
            DispatchQueue.main.async {
                guard let self else { return }
                self.networkStatusKnown = true
                self.isOnline = path.status == .satisfied
                if self.isOnline { Task { await self.refreshEntitlement() } }
            }
        }
        networkMonitor.start(queue: networkQueue)

        transactionListener = listenForTransactions()
        Task {
            await refreshEntitlement()
            await loadProducts()
            if shouldShowAds { await gatherConsentAndStartAds() }
        }
    }

    var questionPackPrice: String { questionPackProduct?.displayPrice ?? "one-time purchase" }
    var isQuestionPackOfferAvailable: Bool { questionPackProduct != nil && questionPackURL != nil }
    var isQuestionPackInstalled: Bool { QuestionPackStore.isInstalled }

    func setChildDirectedSession(_ enabled: Bool) {
        guard isChildDirectedSession != enabled else { return }
        isChildDirectedSession = enabled
        let configuration = MobileAds.shared.requestConfiguration
        configuration.tagForChildDirectedTreatment = enabled ? true : nil
        configuration.tagForUnderAgeOfConsent = enabled ? true : nil
        configuration.maxAdContentRating = enabled ? .general : nil
        configuration.publisherPrivacyPersonalizationState = enabled ? .disabled : .default

        // Never carry an ad loaded for one audience into the other audience.
        rewardedAd = nil
        interstitialAd = nil
        if shouldShowAds {
            Task {
                await loadRewarded()
                await loadInterstitial()
            }
        }
    }

    func purchaseQuestionPack() async {
        guard let product = questionPackProduct, questionPackURL != nil else {
            purchaseMessage = "The extra question pack is not available yet."
            return
        }
        isPurchasing = true
        defer { isPurchasing = false }
        do {
            switch try await product.purchase() {
            case let .success(result):
                guard case let .verified(transaction) = result else {
                    purchaseMessage = "The App Store could not verify this purchase."
                    return
                }
                await transaction.finish()
                await refreshEntitlement()
                if hasPurchasedQuestionPack { await downloadQuestionPack(showMessage: true) }
            case .pending: purchaseMessage = "The purchase is awaiting approval."
            case .userCancelled: purchaseMessage = nil
            @unknown default: purchaseMessage = "The purchase could not be completed."
            }
        } catch {
            purchaseMessage = error.localizedDescription
        }
    }

    func retryQuestionPackDownload() async {
        await downloadQuestionPack(showMessage: true)
    }

    deinit {
        transactionListener?.cancel()
        networkMonitor.cancel()
    }

    func purchaseAdFree() async {
        guard let product = removeAdsProduct else {
            purchaseMessage = "The ad-free purchase is not available yet. Please try again later."
            return
        }
        isPurchasing = true
        defer { isPurchasing = false }
        do {
            switch try await product.purchase() {
            case let .success(result):
                guard case let .verified(transaction) = result else {
                    purchaseMessage = "The App Store could not verify this purchase."
                    return
                }
                await transaction.finish()
                await refreshEntitlement()
                purchaseMessage = hasPurchasedAdFree ? "Advertising has been removed permanently." : nil
            case .pending:
                purchaseMessage = "The purchase is awaiting approval."
            case .userCancelled:
                purchaseMessage = nil
            @unknown default:
                purchaseMessage = "The purchase could not be completed."
            }
        } catch {
            purchaseMessage = error.localizedDescription
        }
    }

    func restorePurchases() async {
        isPurchasing = true
        defer { isPurchasing = false }
        do {
            try await AppStore.sync()
            await refreshEntitlement()
            if hasPurchasedQuestionPack && !QuestionPackStore.isInstalled {
                await downloadQuestionPack(showMessage: false)
            }
            purchaseMessage = (hasPurchasedAdFree || hasPurchasedQuestionPack)
                ? "Your purchases have been restored."
                : "No previous purchases were found."
        } catch {
            purchaseMessage = error.localizedDescription
        }
    }

    func recordRegularAnswer(sessionIsComplete: Bool, completion: @escaping () -> Void) {
        guard shouldShowAds else {
            completion()
            return
        }
        let legacyCount = defaults.integer(forKey: regularAnswerCountKey)
        let count = max(defaults.integer(forKey: adSupportedAnswerCountKey), legacyCount) + 1
        defaults.set(count, forKey: adSupportedAnswerCountKey)
        defaults.set(count, forKey: regularAnswerCountKey)
        guard sessionIsComplete,
              count > Self.fullScreenAdsBeginAfter,
              count.isMultiple(of: Self.interstitialQuestionInterval),
              canShowFullScreenNow else {
            completion()
            return
        }
        presentInterstitial { _ in completion() }
    }

    func recordQuestionPresented(questionID: String) {
        guard !hasPurchasedAdFree,
              defaults.string(forKey: lastFreeQuestionIDKey) != questionID else { return }
        freeQuestionsUsed += 1
        defaults.set(freeQuestionsUsed, forKey: freeQuestionsUsedKey)
        defaults.set(questionID, forKey: lastFreeQuestionIDKey)
    }

    func presentBonusAdIfNeeded(completion: @escaping (Bool) -> Void) {
        guard shouldShowAds, canShowFullScreenNow else {
            completion(true)
            return
        }
        Task {
            if rewardedAd == nil { await loadRewarded() }
            guard let rewardedAd, let presenter = Self.presentingViewController else {
                completion(true) // Ads never block the promised bonus.
                return
            }
            self.rewardedAd = nil
            rewardEarned = false
            pendingFullScreenCompletion = completion
            rewardedAd.fullScreenContentDelegate = self
            rewardedAd.present(from: presenter) { [weak self] in self?.rewardEarned = true }
        }
    }

    func initializeAndPreloadAds() {
        guard shouldShowAds else { return }
        MobileAds.shared.start()
        Task {
            await loadRewarded()
            await loadInterstitial()
        }
    }

    func showPrivacyOptions() async {
        guard let presenter = Self.presentingViewController else { return }
        try? await ConsentForm.presentPrivacyOptionsForm(from: presenter)
    }

    func adDidDismissFullScreenContent(_ ad: FullScreenPresentingAd) {
        lastFullScreenAdDate = Date()
        let granted = ad is RewardedAd ? rewardEarned : true
        pendingFullScreenCompletion?(granted)
        pendingFullScreenCompletion = nil
        Task {
            await loadRewarded()
            await loadInterstitial()
        }
    }

    func ad(_ ad: FullScreenPresentingAd, didFailToPresentFullScreenContentWithError error: Error) {
        pendingFullScreenCompletion?(true) // Fail open rather than interrupting the game.
        pendingFullScreenCompletion = nil
    }

    private var canShowFullScreenNow: Bool {
        guard let lastFullScreenAdDate else { return true }
        return Date().timeIntervalSince(lastFullScreenAdDate) >= 10 * 60
    }

    private func presentInterstitial(completion: @escaping (Bool) -> Void) {
        Task {
            if interstitialAd == nil { await loadInterstitial() }
            guard let interstitialAd, let presenter = Self.presentingViewController else {
                completion(true)
                return
            }
            self.interstitialAd = nil
            pendingFullScreenCompletion = completion
            interstitialAd.fullScreenContentDelegate = self
            interstitialAd.present(from: presenter)
        }
    }

    private func loadRewarded() async {
        guard shouldShowAds, rewardedAd == nil else { return }
        let id = Self.adUnitID(
            infoKey: "MannaRewardedAdUnitID",
            debugSampleID: "ca-app-pub-3940256099942544/1712485313"
        )
        rewardedAd = try? await RewardedAd.load(with: id, request: Request())
    }

    private func loadInterstitial() async {
        guard shouldShowAds, interstitialAd == nil else { return }
        let id = Self.adUnitID(
            infoKey: "MannaInterstitialAdUnitID",
            debugSampleID: "ca-app-pub-3940256099942544/4411468910"
        )
        interstitialAd = try? await InterstitialAd.load(with: id, request: Request())
    }

    private func loadProducts() async {
        let products = (try? await Product.products(for: [productID, questionPackProductID])) ?? []
        removeAdsProduct = products.first { $0.id == productID }
        questionPackProduct = products.first { $0.id == questionPackProductID }
    }

    private func gatherConsentAndStartAds() async {
        do {
            try await ConsentInformation.shared.requestConsentInfoUpdate(with: nil)
            try await ConsentForm.loadAndPresentIfRequired(from: Self.presentingViewController)
        } catch {
            print("Ad consent update unavailable: \(error.localizedDescription)")
        }
        privacyOptionsRequired = ConsentInformation.shared.privacyOptionsRequirementStatus == .required
        if ConsentInformation.shared.canRequestAds { initializeAndPreloadAds() }
    }

    private func refreshEntitlement() async {
        var purchased = false
        var purchasedPack = false
        for await result in Transaction.currentEntitlements {
            if case let .verified(transaction) = result,
               transaction.revocationDate == nil {
                if transaction.productID == productID { purchased = true }
                if transaction.productID == questionPackProductID { purchasedPack = true }
            }
        }
        if purchased || (networkStatusKnown && isOnline) {
            hasPurchasedAdFree = purchased
            defaults.set(purchased, forKey: purchasedEntitlementKey)
        }
        if purchasedPack || (networkStatusKnown && isOnline) {
            hasPurchasedQuestionPack = purchasedPack
            defaults.set(purchasedPack, forKey: questionPackEntitlementKey)
        }
        if purchasedPack && !QuestionPackStore.isInstalled {
            await downloadQuestionPack(showMessage: false)
        }
    }

    private func downloadQuestionPack(showMessage: Bool) async {
        guard hasPurchasedQuestionPack, let questionPackURL else { return }
        if QuestionPackStore.isInstalled {
            if showMessage { purchaseMessage = "10,000 extra questions are installed and ready to play." }
            return
        }
        do {
            let questions = try await QuestionPackStore.downloadAndInstall(from: questionPackURL)
            QuestionCache.shared.addToCache(questions)
            if showMessage { purchaseMessage = "10,000 extra questions are installed and ready to play." }
        } catch {
            if showMessage { purchaseMessage = error.localizedDescription }
        }
    }

    private func listenForTransactions() -> Task<Void, Never> {
        Task { [weak self] in
            for await result in Transaction.updates {
                guard let self else { return }
                if case let .verified(transaction) = result {
                    await transaction.finish()
                    await refreshEntitlement()
                }
            }
        }
    }

    fileprivate static var presentingViewController: UIViewController? {
        let scenes = UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }
        var controller = scenes.flatMap(\.windows).first(where: \.isKeyWindow)?.rootViewController
        while let presented = controller?.presentedViewController { controller = presented }
        return controller
    }
}

struct MannaBannerAd: View {
    @EnvironmentObject private var monetization: MonetizationManager

    var body: some View {
        BannerContainer(adSize: AdSizeLargeBanner)
            .frame(width: 320, height: 100)
            .frame(maxWidth: .infinity)
            .frame(height: 100)
            .clipped()
        .mannaAccessibilityLabel("Advertisement")
        .opacity(monetization.shouldShowAds ? 1 : 0)
    }
}

private struct BannerContainer: UIViewRepresentable {
    let adSize: AdSize

    func makeUIView(context: Context) -> BannerView {
        let banner = BannerView(adSize: adSize)
        banner.adUnitID = MonetizationManager.adUnitID(
            infoKey: "MannaBannerAdUnitID",
            debugSampleID: "ca-app-pub-3940256099942544/2934735716"
        )
        banner.rootViewController = MonetizationManager.presentingViewController
        banner.load(Request())
        return banner
    }

    func updateUIView(_ banner: BannerView, context: Context) {
        banner.adSize = adSize
        banner.rootViewController = MonetizationManager.presentingViewController
    }
}
