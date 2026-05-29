import SwiftUI

struct LuminaView: View {
    @EnvironmentObject var gameManager: GameManager
    @Environment(\.openURL) private var openURL

    // TODO: replace with the real store listing URLs once Lumina is published.
    private let macAppStoreURL = URL(string: "https://apps.apple.com/app/lumina-bible")!
    private let microsoftStoreURL = URL(string: "https://apps.microsoft.com/detail/lumina-bible")!
    // Android build → Google Play (also covers Google's Android-based desktop OS, Aluminium OS):
    private let googlePlayURL = URL(string: "https://play.google.com/store/apps/details?id=com.doctorosg.lumina")!

    private let gold = Color(hex: "#D4A843") ?? .yellow

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Button(action: { gameManager.goHome() }) {
                    Image(systemName: "chevron.left")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.white)
                }
                Spacer()
                Text("Lumina Bible")
                    .font(.system(size: 18, weight: .bold, design: .rounded))
                    .foregroundColor(.white)
                Spacer()
                Color.clear.frame(width: 24, height: 24)
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 10)

            ScrollView {
                VStack(spacing: 18) {
                    hero
                    priceBadge
                    whatsInside
                    howItsDifferent
                    availableFor
                    footnote
                }
                .padding(.horizontal, 16)
                .padding(.bottom, 32)
            }
        }
    }

    // MARK: - Hero
    private var hero: some View {
        VStack(spacing: 10) {
            Image(systemName: "book.closed.fill")
                .font(.system(size: 46))
                .foregroundColor(gold)
                .padding(.top, 8)
            Text("LUMINA BIBLE")
                .font(.system(size: 30, weight: .black, design: .serif))
                .foregroundColor(gold)
                .tracking(3)
            Text("The Pastor Edition")
                .font(.system(size: 15, weight: .semibold, design: .rounded))
                .foregroundColor(.white.opacity(0.7))
                .tracking(1)
            Text("A complete desktop study Bible built for sermon preparation — cross-references, original languages, commentaries, and the Church Fathers, all in one place.")
                .font(.system(size: 14))
                .foregroundColor(.white.opacity(0.6))
                .multilineTextAlignment(.center)
                .lineSpacing(3)
                .padding(.horizontal, 8)
                .padding(.top, 2)
        }
    }

    // MARK: - Price
    private var priceBadge: some View {
        VStack(spacing: 4) {
            Text("$19.99")
                .font(.system(size: 34, weight: .black, design: .rounded))
                .foregroundColor(.white)
            Text("One-time purchase · No subscription, ever")
                .font(.system(size: 13, weight: .semibold, design: .rounded))
                .foregroundColor(gold)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 18)
        .background(gold.opacity(0.10))
        .overlay(RoundedRectangle(cornerRadius: 14).stroke(gold.opacity(0.35), lineWidth: 1))
        .cornerRadius(14)
    }

    // MARK: - What's inside
    private var whatsInside: some View {
        VStack(alignment: .leading, spacing: 0) {
            sectionTitle("What's inside")
            featureRow("text.book.closed.fill", "KJV reading", "Clean two-page layout with day & night modes")
            featureRow("arrow.triangle.branch", "Cross-references", "Every verse linked across the whole Bible")
            featureRow("character.book.closed.fill", "Strong's concordance", "Hebrew & Greek word study, word by word")
            featureRow("text.quote", "Commentaries", "Matthew Henry, Spurgeon's Treasury of David, JFB")
            featureRow("person.2.fill", "Church Fathers", "Catena Aurea — patristic commentary on the Gospels")
            featureRow("scroll.fill", "Septuagint & Peshitta", "Brenton's English LXX and the Syriac text")
            featureRow("books.vertical.fill", "Mishnah & Talmud", "Rabbinic sources for historical context")
            featureRow("map.fill", "Maps", "1,342 biblical places linked to the verses")
            featureRow("square.and.pencil", "Notes & search", "Personal notes, highlights, and full-text search")
        }
        .padding(16)
        .background(Color.white.opacity(0.05))
        .cornerRadius(14)
    }

    // MARK: - Differentiation
    private var howItsDifferent: some View {
        VStack(alignment: .leading, spacing: 0) {
            sectionTitle("How it's different")
            diffRow("No monthly fees", "Other premium study apps bill you every month. Lumina is yours for one price.")
            diffRow("Everything in one app", "No paid add-ons or modules to unlock — the full library is included.")
            diffRow("Works fully offline", "All resources live on your machine. No account, no internet required.")
        }
        .padding(16)
        .background(Color.white.opacity(0.05))
        .cornerRadius(14)
    }

    // MARK: - Available for (per platform)
    private var availableFor: some View {
        VStack(spacing: 10) {
            Text("Available for")
                .font(.system(size: 16, weight: .bold, design: .rounded))
                .foregroundColor(.white)
                .frame(maxWidth: .infinity, alignment: .leading)
            storeRow(icon: "apple.logo", platform: "Mac", store: "App Store", filled: true) { openURL(macAppStoreURL) }
            storeRow(icon: "desktopcomputer", platform: "Windows", store: "Microsoft Store", filled: false) { openURL(microsoftStoreURL) }
            storeRow(icon: "play.fill", platform: "Android", store: "Google Play", filled: false) { openURL(googlePlayURL) }
        }
    }

    private func storeRow(icon: String, platform: String, store: String, filled: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Image(systemName: icon).font(.system(size: 20, weight: .semibold))
                VStack(alignment: .leading, spacing: 1) {
                    Text(platform).font(.system(size: 12, weight: .medium, design: .rounded)).opacity(0.7)
                    Text(store).font(.system(size: 16, weight: .bold, design: .rounded))
                }
                Spacer()
                Image(systemName: "arrow.up.right").font(.system(size: 13, weight: .bold)).opacity(0.6)
            }
            .foregroundColor(filled ? .black : .white)
            .padding(.horizontal, 16)
            .padding(.vertical, 14)
            .frame(maxWidth: .infinity)
            .background(filled ? gold : Color.white.opacity(0.06))
            .overlay(RoundedRectangle(cornerRadius: 14).stroke(gold.opacity(filled ? 0 : 0.4), lineWidth: 1))
            .cornerRadius(14)
        }
    }

    private var footnote: some View {
        Text("Lumina Bible is a separate app from Manna.")
            .font(.system(size: 11))
            .foregroundColor(.white.opacity(0.35))
            .multilineTextAlignment(.center)
            .frame(maxWidth: .infinity)
    }

    // MARK: - Helpers
    private func sectionTitle(_ t: String) -> some View {
        Text(t)
            .font(.system(size: 16, weight: .bold, design: .rounded))
            .foregroundColor(.white)
            .padding(.bottom, 10)
    }

    private func featureRow(_ icon: String, _ title: String, _ detail: String) -> some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 16))
                .foregroundColor(gold)
                .frame(width: 26)
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.system(size: 14, weight: .semibold, design: .rounded))
                    .foregroundColor(.white)
                Text(detail)
                    .font(.system(size: 12))
                    .foregroundColor(.white.opacity(0.5))
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer(minLength: 0)
        }
        .padding(.vertical, 7)
    }

    private func diffRow(_ title: String, _ detail: String) -> some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 16))
                .foregroundColor(.green)
                .frame(width: 26)
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.system(size: 14, weight: .semibold, design: .rounded))
                    .foregroundColor(.white)
                Text(detail)
                    .font(.system(size: 12))
                    .foregroundColor(.white.opacity(0.55))
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer(minLength: 0)
        }
        .padding(.vertical, 7)
    }
}
