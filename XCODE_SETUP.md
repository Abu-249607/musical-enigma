# Xcode Setup Instructions

## Quick Setup (5 minutes)

### Step 1: Create New Xcode Project

1. Open **Xcode**
2. Click **"Create New Project"** or File → New → Project
3. Select **iOS** → **App**
4. Click **Next**

### Step 2: Configure Project

Use these exact settings:

- **Product Name:** `TherapistMe`
- **Team:** (Select your team)
- **Organization Identifier:** `com.therapistme` (or your own)
- **Interface:** **SwiftUI**
- **Language:** **Swift**
- **Storage:** **None** (we're using CoreData manually)
- **Include Tests:** ✅ (Check this)

Click **Next** and save the project **outside** this repository (e.g., on your Desktop)

### Step 3: Add Source Files

**Method A: Drag & Drop (Easiest)**

1. In Finder, navigate to this repository: `TherapistMe/TherapistMe/`
2. Select ALL these folders:
   - `App/`
   - `Models/`
   - `Services/`
   - `Views/`
3. Drag them into Xcode's **Navigator** (left sidebar)
4. In the dialog:
   - ✅ Check **"Copy items if needed"**
   - ✅ Select **"Create groups"**
   - ✅ Add to target: **TherapistMe**
5. Click **Finish**

**Method B: Manual (More Control)**

In Xcode Navigator, right-click on the TherapistMe folder → **Add Files to "TherapistMe"...**

Add these files in order:

```
App/
├── TherapistMeApp.swift

Models/
├── User.swift
├── JournalEntry.swift
├── MoodEntry.swift
└── CravingLog.swift

Services/
├── Encryption/
│   ├── EncryptionService.swift
│   └── KeychainManager.swift
├── Authentication/
│   ├── AuthenticationService.swift
│   ├── PasswordValidator.swift
│   └── BiometricAuth.swift
├── Authorization/
│   └── AccessControl.swift
├── Session/
│   └── SessionManager.swift
├── Audit/
│   └── AuditLogger.swift
└── Security/
    ├── SecurityValidator.swift
    └── IntegrityValidator.swift

Views/
├── Onboarding/
│   └── OnboardingFlowView.swift
├── Authentication/
│   └── LoginView.swift
└── Dashboard/
    └── DashboardView.swift
```

### Step 4: Configure Info.plist

1. In Xcode Navigator, select **Info.plist** (or click on TherapistMe target → Info tab)
2. Add these privacy descriptions:

**Right-click in Info.plist → Add Row:**

| Key | Type | Value |
|-----|------|-------|
| `Privacy - Face ID Usage Description` | String | `We use Face ID to securely authenticate you and protect your health data.` |

### Step 5: Enable Capabilities

1. Select your project in Navigator
2. Select **TherapistMe** target
3. Click **Signing & Capabilities** tab
4. Click **"+ Capability"**
5. Add: **Keychain Sharing**

### Step 6: Fix Compilation Errors

You'll need to delete the default files Xcode created:

1. **Delete** `ContentView.swift` (we created our own views)
2. In `TherapistMeApp.swift` that Xcode created, **replace** its contents with our version

### Step 7: Build & Run

1. Select a simulator: **iPhone 15 Pro** (or any iOS 16.0+ device)
2. Press **⌘ + R** (or click the Play button)
3. Wait for build to complete (~30 seconds first time)
4. The app will launch in the simulator!

---

## Expected App Flow

When you run the app, you'll see:

1. **Welcome Screen** - "Welcome to Therapist.Me" with heart icon
2. **Privacy Notice** - HIPAA Notice of Privacy Practices
3. **Consent Screen** - Required and optional consents
4. **Registration** - Create account with strong password
5. **Dashboard** - Main app with tabs (Home, Mood, Journal, Chat, Profile)

---

## Troubleshooting

### Issue: "Cannot find type 'User' in scope"

**Solution:** Make sure you added ALL files from the Services and Models folders.

### Issue: "Missing required module 'CryptoKit'"

**Solution:** CryptoKit is built-in for iOS 16+. Make sure deployment target is set to iOS 16.0:
- Select project → TherapistMe target → General → Minimum Deployments → iOS 16.0

### Issue: "Use of undeclared type 'AuditLogger'"

**Solution:** Make sure you added `Services/Audit/AuditLogger.swift`

### Issue: Build succeeds but app crashes on launch

**Solution:** Check Console for error messages. Most likely:
- Security validation failed (jailbreak detection) - This is expected in simulator, comment out the check in DEBUG mode
- Missing encryption key - App creates it on first launch

### Issue: "Cannot find 'SessionManager' in scope"

**Solution:** Add `Services/Session/SessionManager.swift` to your project

---

## Testing Features

Once running, you can test:

### ✅ Onboarding Flow
1. Tap through welcome screens
2. Accept privacy notice
3. Check consent boxes (all required ones)
4. Register with:
   - Email: `test@example.com`
   - Password: `TestPassword123!` (must meet complexity requirements)

### ✅ Password Strength
Try weak passwords to see validation:
- `weak` - Too short
- `password123` - No uppercase
- `Password` - No numbers or special chars
- `Password123!` - ✅ Accepted

### ✅ Login (after registration)
1. You'll auto-login after registration
2. Logout from Profile tab
3. Login again with same credentials
4. Try Face ID (simulator: Hardware → Face ID → Matching Face)

### ✅ Dashboard
- Navigate between tabs
- View quick action cards
- Access profile settings

### ✅ Session Timeout
- Leave app idle for 15 minutes
- App should auto-logout (you'll need to wait or modify timeout for testing)

---

## Next Steps

After confirming the app runs:

1. **Add Test Data**: Implement the mood tracker and journal UIs
2. **Test Encryption**: Create journal entries and verify they're encrypted
3. **Test Biometrics**: Enable Face ID and test authentication
4. **Review Audit Logs**: Check console for audit events
5. **Test on Device**: Deploy to physical iPhone for full biometric testing

---

## Quick Reference

### Xcode Shortcuts
- `⌘ + R` - Build and Run
- `⌘ + .` - Stop running
- `⌘ + B` - Build only
- `⌘ + Shift + K` - Clean build folder
- `⌘ + U` - Run tests

### Useful Debug Settings
- Product → Scheme → Edit Scheme → Run → Arguments
- Add environment variable: `DEBUG_SECURITY` = `1` to see security logs

---

## Support

If you encounter issues:

1. **Clean Build Folder**: Product → Clean Build Folder (⌘ + Shift + K)
2. **Delete Derived Data**: Xcode → Preferences → Locations → Derived Data → Delete
3. **Restart Xcode**: Sometimes Xcode needs a restart
4. **Check Console**: View → Debug Area → Show Debug Area (⌘ + Shift + Y)

---

**Expected Build Time:** ~30 seconds (first build)
**Expected App Size:** ~15 MB
**Minimum iOS:** 16.0
**Supported Devices:** iPhone only (iPad support coming in Phase 2)

---

**Ready to build!** Follow the steps above and the app should launch successfully.
