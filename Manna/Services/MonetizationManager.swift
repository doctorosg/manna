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
    @Published private(set) var removeAdsProduct: Product?
    @Published private(set) var purchaseMessage: String?
    @Published private(set) var isPurchasing = false
    @Published private(set) var privacyOptionsRequired = false
    @Published private(set) var isOnline = true
    @Published private(set) var freeQuestionsUsed = 0

    private let defaults = UserDefaults.standard
    private let freeQuestionsUsedKey = "manna.freeQuestionsUsed"
    private let lastFreeQuestionIDKey = "manna.lastFreeQuestionID"
    private let regularAnswerCountKey = "manna.regularAnswerCount"
    private let adSupportedAnswerCountKey = "manna.adSupportedAnswerCount"
    private let purchasedEntitlementKey = "manna.hasVerifiedAdFreePurchase"
    private let productID: String
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
        super.init()
        hasPurchasedAdFree = defaults.bool(forKey: purchasedEntitlementKey)
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
            await loadProduct()
            if shouldShowAds { await gatherConsentAndStartAds() }
        }
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
            purchaseMessage = hasPurchasedAdFree
                ? "Your ad-free purchase has been restored."
                : "No previous ad-free purchase was found."
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

    private func loadProduct() async {
        removeAdsProduct = try? await Product.products(for: [productID]).first
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
        for await result in Transaction.currentEntitlements {
            if case let .verified(transaction) = result,
               transaction.productID == productID,
               transaction.revocationDate == nil {
                purchased = true
            }
        }
        if purchased || (networkStatusKnown && isOnline) {
            hasPurchasedAdFree = purchased
            defaults.set(purchased, forKey: purchasedEntitlementKey)
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
        .accessibilityLabel("Advertisement")
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
