package com.oddcurrent.manna

import android.app.Activity
import android.content.Context
import android.content.SharedPreferences
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import com.android.billingclient.api.AcknowledgePurchaseParams
import com.android.billingclient.api.BillingClient
import com.android.billingclient.api.BillingClientStateListener
import com.android.billingclient.api.BillingFlowParams
import com.android.billingclient.api.BillingResult
import com.android.billingclient.api.PendingPurchasesParams
import com.android.billingclient.api.ProductDetails
import com.android.billingclient.api.QueryProductDetailsParams
import com.android.billingclient.api.QueryPurchasesParams
import com.google.android.gms.ads.AdRequest
import com.google.android.gms.ads.AdSize
import com.google.android.gms.ads.AdView
import com.google.android.gms.ads.FullScreenContentCallback
import com.google.android.gms.ads.LoadAdError
import com.google.android.gms.ads.MobileAds
import com.google.android.gms.ads.interstitial.InterstitialAd
import com.google.android.gms.ads.interstitial.InterstitialAdLoadCallback
import com.google.android.gms.ads.rewarded.RewardedAd
import com.google.android.gms.ads.rewarded.RewardedAdLoadCallback
import com.google.android.ump.ConsentInformation
import com.google.android.ump.ConsentRequestParameters
import com.google.android.ump.UserMessagingPlatform

class MonetizationManager(
    private val activity: Activity,
    private val preferences: SharedPreferences
) {
    companion object {
        const val REMOVE_ADS_PRODUCT_ID = "com.oddcurrent.manna.remove_ads"
        private const val PRODUCTION_BANNER_ID = "ca-app-pub-9667779972496607/8779786915"
        private const val PRODUCTION_INTERSTITIAL_ID = "ca-app-pub-9667779972496607/5124396753"
        private const val PRODUCTION_REWARDED_ID = "ca-app-pub-9667779972496607/9873376734"
        private const val SAMPLE_BANNER_ID = "ca-app-pub-3940256099942544/9214589741"
        private const val SAMPLE_INTERSTITIAL_ID = "ca-app-pub-3940256099942544/1033173712"
        private const val SAMPLE_REWARDED_ID = "ca-app-pub-3940256099942544/5224354917"
        val BANNER_AD_UNIT_ID = if (BuildConfig.DEBUG) SAMPLE_BANNER_ID else PRODUCTION_BANNER_ID
        private val INTERSTITIAL_AD_UNIT_ID = if (BuildConfig.DEBUG) SAMPLE_INTERSTITIAL_ID else PRODUCTION_INTERSTITIAL_ID
        private val REWARDED_AD_UNIT_ID = if (BuildConfig.DEBUG) SAMPLE_REWARDED_ID else PRODUCTION_REWARDED_ID
        const val AD_FREE_QUESTION_ALLOWANCE = 50
        const val INTERSTITIAL_QUESTION_INTERVAL = 20
    }

    var hasPurchasedAdFree by mutableStateOf(false)
        private set
    var purchaseMessage by mutableStateOf<String?>(null)
        private set
    var isPurchasing by mutableStateOf(false)
        private set
    var removeAdsPrice by mutableStateOf("one-time purchase")
        private set
    var privacyOptionsRequired by mutableStateOf(false)
        private set
    var isOnline by mutableStateOf(true)
        private set
    var freeQuestionsUsed by mutableIntStateOf(0)
        private set

    private var removeAdsProduct: ProductDetails? = null
    private var rewardedAd: RewardedAd? = null
    private var interstitialAd: InterstitialAd? = null
    private val billingClient: BillingClient
    private val consentInformation = UserMessagingPlatform.getConsentInformation(activity)
    private val connectivityManager = activity.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
    private val networkCallback = object : ConnectivityManager.NetworkCallback() {
        override fun onAvailable(network: Network) = updateNetworkState()
        override fun onCapabilitiesChanged(network: Network, capabilities: NetworkCapabilities) = updateNetworkState()
        override fun onLost(network: Network) = updateNetworkState()
    }

    val shouldShowAds: Boolean
        get() = !hasPurchasedAdFree && freeQuestionsUsed > AD_FREE_QUESTION_ALLOWANCE
    val shouldExplainAdvertising: Boolean
        get() = !hasPurchasedAdFree
    val requiresInternetAccess: Boolean
        get() = shouldShowAds && !isOnline

    init {
        hasPurchasedAdFree = preferences.getBoolean("verified_ad_free_purchase", false)
        freeQuestionsUsed = if (preferences.contains("free_questions_used")) {
            preferences.getInt("free_questions_used", 0)
        } else {
            preferences.getInt("regular_answer_count", 0).also {
                preferences.edit().putInt("free_questions_used", it).apply()
            }
        }
        billingClient = BillingClient.newBuilder(activity)
            .setListener { result, purchases ->
                if (result.responseCode == BillingClient.BillingResponseCode.OK) {
                    purchases.orEmpty().forEach { processPurchase(it, showMessage = true) }
                } else if (result.responseCode != BillingClient.BillingResponseCode.USER_CANCELED) {
                    purchaseMessage = result.debugMessage
                }
                isPurchasing = false
            }
            .enablePendingPurchases(
                PendingPurchasesParams.newBuilder().enableOneTimeProducts().build()
            )
            .build()
        connectivityManager.registerNetworkCallback(
            NetworkRequest.Builder().addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET).build(),
            networkCallback
        )
        updateNetworkState()
        connectBilling()
        if (!hasPurchasedAdFree) gatherConsentAndStartAds()
    }

    fun purchaseAdFree() {
        val product = removeAdsProduct
        if (product == null) {
            purchaseMessage = "The Google Play purchase is not available yet. Please try again later."
            connectBilling()
            return
        }
        isPurchasing = true
        val params = BillingFlowParams.newBuilder()
            .setProductDetailsParamsList(
                listOf(BillingFlowParams.ProductDetailsParams.newBuilder().setProductDetails(product).build())
            ).build()
        val result = billingClient.launchBillingFlow(activity, params)
        if (result.responseCode != BillingClient.BillingResponseCode.OK) {
            isPurchasing = false
            purchaseMessage = result.debugMessage
        }
    }

    fun restorePurchases() {
        if (!billingClient.isReady) {
            purchaseMessage = "Connecting to Google Play…"
            connectBilling()
            return
        }
        queryExistingPurchases(showResult = true)
    }

    private fun queryExistingPurchases(showResult: Boolean) {
        billingClient.queryPurchasesAsync(
            QueryPurchasesParams.newBuilder().setProductType(BillingClient.ProductType.INAPP).build()
        ) { result, purchases ->
            if (result.responseCode == BillingClient.BillingResponseCode.OK) {
                val activePurchases = purchases.filter {
                    REMOVE_ADS_PRODUCT_ID in it.products &&
                        it.purchaseState == com.android.billingclient.api.Purchase.PurchaseState.PURCHASED
                }
                activePurchases.forEach { processPurchase(it, showMessage = false) }
                if (activePurchases.isEmpty()) {
                    hasPurchasedAdFree = false
                    preferences.edit().putBoolean("verified_ad_free_purchase", false).apply()
                }
                if (showResult) {
                    purchaseMessage = if (hasPurchasedAdFree) "Your ad-free purchase has been restored."
                        else "No previous ad-free purchase was found."
                }
            } else if (showResult) purchaseMessage = result.debugMessage
        }
    }

    fun showPrivacyOptions() {
        UserMessagingPlatform.showPrivacyOptionsForm(activity) { error ->
            if (error != null) purchaseMessage = error.message
        }
    }

    fun recordRegularAnswer(sessionIsComplete: Boolean, completion: () -> Unit) {
        val count = maxOf(
            preferences.getInt("ad_supported_answer_count", 0),
            preferences.getInt("regular_answer_count", 0)
        ) + 1
        preferences.edit()
            .putInt("ad_supported_answer_count", count)
            .putInt("regular_answer_count", count)
            .apply()
        if (!shouldShowAds) {
            completion()
            return
        }
        val answeredSinceAdsBegan = count - AD_FREE_QUESTION_ALLOWANCE
        if (!sessionIsComplete || answeredSinceAdsBegan <= 0 ||
            answeredSinceAdsBegan % INTERSTITIAL_QUESTION_INTERVAL != 0) {
            completion()
            return
        }
        showInterstitial(completion)
    }

    fun recordQuestionPresented(questionId: String) {
        if (hasPurchasedAdFree ||
            preferences.getString("last_free_question_id", null) == questionId) return
        freeQuestionsUsed += 1
        preferences.edit()
            .putInt("free_questions_used", freeQuestionsUsed)
            .putString("last_free_question_id", questionId)
            .apply()
    }

    fun showBonusAdIfNeeded(completion: (Boolean) -> Unit) {
        if (!shouldShowAds) {
            completion(true)
            return
        }
        val show: (RewardedAd) -> Unit = { ad ->
            rewardedAd = null
            var earned = false
            ad.fullScreenContentCallback = object : FullScreenContentCallback() {
                override fun onAdDismissedFullScreenContent() {
                    completion(earned)
                    loadRewarded()
                }

                override fun onAdFailedToShowFullScreenContent(error: com.google.android.gms.ads.AdError) {
                    completion(true)
                    loadRewarded()
                }
            }
            ad.show(activity) { earned = true }
        }
        rewardedAd?.let(show) ?: loadRewarded { loaded ->
            if (loaded == null) completion(true) else show(loaded)
        }
    }

    private fun connectBilling() {
        if (billingClient.isReady) {
            queryProductsAndEntitlement()
            return
        }
        billingClient.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(result: BillingResult) {
                if (result.responseCode == BillingClient.BillingResponseCode.OK) queryProductsAndEntitlement()
            }
            override fun onBillingServiceDisconnected() = Unit
        })
    }

    private fun queryProductsAndEntitlement() {
        val product = QueryProductDetailsParams.Product.newBuilder()
            .setProductId(REMOVE_ADS_PRODUCT_ID)
            .setProductType(BillingClient.ProductType.INAPP)
            .build()
        billingClient.queryProductDetailsAsync(
            QueryProductDetailsParams.newBuilder().setProductList(listOf(product)).build()
        ) { _, result ->
            removeAdsProduct = result.productDetailsList.firstOrNull()
            removeAdsPrice = removeAdsProduct?.oneTimePurchaseOfferDetailsList?.firstOrNull()?.formattedPrice
                ?: "one-time purchase"
        }
        queryExistingPurchases(showResult = false)
    }

    private fun processPurchase(purchase: com.android.billingclient.api.Purchase, showMessage: Boolean) {
        if (REMOVE_ADS_PRODUCT_ID !in purchase.products ||
            purchase.purchaseState != com.android.billingclient.api.Purchase.PurchaseState.PURCHASED) return
        hasPurchasedAdFree = true
        preferences.edit().putBoolean("verified_ad_free_purchase", true).apply()
        if (showMessage) purchaseMessage = "Advertising has been removed permanently."
        if (!purchase.isAcknowledged) {
            billingClient.acknowledgePurchase(
                AcknowledgePurchaseParams.newBuilder().setPurchaseToken(purchase.purchaseToken).build()
            ) { }
        }
    }

    private fun preloadAds() {
        loadRewarded()
        loadInterstitial()
    }

    private fun gatherConsentAndStartAds() {
        val parameters = ConsentRequestParameters.Builder().build()
        consentInformation.requestConsentInfoUpdate(
            activity,
            parameters,
            {
                UserMessagingPlatform.loadAndShowConsentFormIfRequired(activity) {
                    privacyOptionsRequired = consentInformation.privacyOptionsRequirementStatus ==
                        ConsentInformation.PrivacyOptionsRequirementStatus.REQUIRED
                    if (consentInformation.canRequestAds()) {
                        MobileAds.initialize(activity) { preloadAds() }
                    }
                }
            },
            {
                if (consentInformation.canRequestAds()) {
                    MobileAds.initialize(activity) { preloadAds() }
                }
            }
        )
    }

    private fun loadRewarded(onLoaded: ((RewardedAd?) -> Unit)? = null) {
        RewardedAd.load(activity, REWARDED_AD_UNIT_ID, AdRequest.Builder().build(), object : RewardedAdLoadCallback() {
            override fun onAdLoaded(ad: RewardedAd) {
                rewardedAd = ad
                onLoaded?.invoke(ad)
            }
            override fun onAdFailedToLoad(error: LoadAdError) {
                rewardedAd = null
                onLoaded?.invoke(null)
            }
        })
    }

    private fun loadInterstitial() {
        InterstitialAd.load(activity, INTERSTITIAL_AD_UNIT_ID, AdRequest.Builder().build(), object : InterstitialAdLoadCallback() {
            override fun onAdLoaded(ad: InterstitialAd) { interstitialAd = ad }
            override fun onAdFailedToLoad(error: LoadAdError) { interstitialAd = null }
        })
    }

    private fun showInterstitial(completion: () -> Unit) {
        val ad = interstitialAd
        if (ad == null) {
            loadInterstitial()
            completion()
            return
        }
        interstitialAd = null
        ad.fullScreenContentCallback = object : FullScreenContentCallback() {
            override fun onAdDismissedFullScreenContent() {
                loadInterstitial()
                completion()
            }
            override fun onAdFailedToShowFullScreenContent(error: com.google.android.gms.ads.AdError) {
                loadInterstitial()
                completion()
            }
        }
        ad.show(activity)
    }

    private fun updateNetworkState() {
        val capabilities = connectivityManager.activeNetwork?.let(connectivityManager::getNetworkCapabilities)
        val connected = capabilities?.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED) == true
        activity.runOnUiThread { isOnline = connected }
    }
}

@Composable
fun MannaBannerAd(modifier: Modifier = Modifier) {
    val context = LocalContext.current
    BoxWithConstraints(modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
        AndroidView(
            modifier = Modifier.fillMaxWidth().height(50.dp),
            factory = {
                AdView(context).apply {
                    adUnitId = MonetizationManager.BANNER_AD_UNIT_ID
                    setAdSize(AdSize.BANNER)
                    loadAd(AdRequest.Builder().build())
                }
            }
        )
    }
}
