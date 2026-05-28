import StoreKit

class StoreManager: ObservableObject {
    static let shared = StoreManager()

    @Published var products: [Product] = []
    @Published var purchaseInProgress = false
    var onTokensPurchased: ((Int) -> Void)?

    private let productIds = [
        "com.doctorosg.manna.tokens.500",
        "com.doctorosg.manna.tokens.1200",
        "com.doctorosg.manna.tokens.3000",
        "com.doctorosg.manna.tokens.7500"
    ]

    init() {
        Task { await loadProducts() }
        Task { await listenForTransactions() }
    }

    func loadProducts() async {
        do {
            products = try await Product.products(for: Set(productIds))
                .sorted { $0.price < $1.price }
        } catch {
            print("Failed to load products: \(error)")
        }
    }

    func purchase(_ product: Product) async {
        purchaseInProgress = true
        defer { purchaseInProgress = false }
        do {
            let result = try await product.purchase()
            switch result {
            case .success(let verification):
                if case .verified(let tx) = verification {
                    let tokens = tokensFor(product.id)
                    await MainActor.run { onTokensPurchased?(tokens) }
                    await tx.finish()
                }
            case .pending: break
            case .userCancelled: break
            @unknown default: break
            }
        } catch {
            print("Purchase failed: \(error)")
        }
    }

    private func tokensFor(_ productId: String) -> Int {
        switch productId {
        case "com.doctorosg.manna.tokens.500": return 1000
        case "com.doctorosg.manna.tokens.1200": return 2500
        case "com.doctorosg.manna.tokens.3000": return 7500
        case "com.doctorosg.manna.tokens.7500": return 20000
        default: return 0
        }
    }

    private func listenForTransactions() async {
        for await result in Transaction.updates {
            if case .verified(let tx) = result {
                let tokens = tokensFor(tx.productID)
                await MainActor.run { onTokensPurchased?(tokens) }
                await tx.finish()
            }
        }
    }
}
