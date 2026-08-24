# Building Manna

Manna is published by Odd Current Software. Its first 50 questions are completely ad-free. Beginning with question 51, its unpaid
experience shows a reserved banner after each revealed answer. After the allowance, an interstitial is eligible every 20 regular
questions at the end of a five-question session. Optional bonus questions use a clearly disclosed rewarded ad. The one-time Remove Ads purchase
removes every ad and enables offline play; there are no subscriptions or consumable purchases.

## Question bank

```bash
python3 scripts/build_question_bank.py
python3 scripts/validate_question_bank.py
```

The builder combines the four repository banks, de-duplicates normalized question text,
rejects repeated answer choices, validates categories and difficulty labels, and writes the
matching iOS and Android assets. Permanent support numbers are stored in
`question_number_registry.json`; never delete or renumber entries in that registry. New
questions receive the next unused number.

Volume 4 contains 565 KJV-source-verified questions for the eight least-populated
categories. Recreate it deterministically before rebuilding the shipping bank with:

```bash
python3 scripts/gen_v4_underrepresented.py
```

To investigate a user dispute, look up the number shown in the app:

```bash
python3 scripts/lookup_question.py 105
```

## iOS

Requires Xcode 16 or newer, XcodeGen, and iOS 18 or newer (for private on-device question
translation).

```bash
xcodegen generate
xcodebuild -project Manna.xcodeproj -scheme Manna -sdk iphonesimulator \
  -configuration Debug -derivedDataPath build/ios-derived CODE_SIGNING_ALLOWED=NO build
```

## Android

Set `sdk.dir` in `android/local.properties`, then:

```bash
cd android
./gradlew :app:assembleDebug :app:bundleRelease
```

The installable debug APK is at `android/app/build/outputs/apk/debug/app-debug.apk`.
The Play upload bundle is at `android/app/build/outputs/bundle/release/app-release.aab`;
configure the private Play upload key before production submission.
