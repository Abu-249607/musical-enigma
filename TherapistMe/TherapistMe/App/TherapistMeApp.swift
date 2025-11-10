import SwiftUI

// HIPAA Compliance: Main app entry point with security validation
// Implements §164.312(a)(1) - Access Control
// Implements §164.312(b) - Audit Controls

@main
struct TherapistMeApp: App {
    @StateObject private var sessionManager = SessionManager.shared
    @StateObject private var appState = AppState.shared

    init() {
        // HIPAA Security: Validate environment before app launch
        performSecurityChecks()

        // Configure app-wide security settings
        configureSecuritySettings()
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(sessionManager)
                .environmentObject(appState)
                .onAppear {
                    // HIPAA Audit: Log app launch
                    AuditLogger.shared.log(.appLaunched, metadata: [
                        "version": AppInfo.version,
                        "build": AppInfo.build
                    ])
                }
                .onDisappear {
                    // HIPAA Audit: Log app termination
                    AuditLogger.shared.log(.appTerminated)
                }
        }
    }

    // MARK: - Security Validation

    /// HIPAA Compliance: Perform security checks before app launch
    /// Implements jailbreak detection, debugger detection, integrity validation
    private func performSecurityChecks() {
        do {
            // Check for jailbreak/compromised device
            try SecurityValidator.shared.validateEnvironment()

            // Verify app binary integrity
            try SecurityValidator.shared.verifyBinaryIntegrity()

        } catch SecurityError.jailbreakDetected {
            // HIPAA Security: Refuse to run on jailbroken devices
            // Compromised devices cannot guarantee PHI security
            AuditLogger.shared.log(.securityViolation, metadata: [
                "reason": "Jailbreak detected"
            ])
            fatalError("Security Error: This app cannot run on jailbroken devices to protect your health information.")

        } catch SecurityError.debuggerDetected {
            AuditLogger.shared.log(.securityViolation, metadata: [
                "reason": "Debugger detected"
            ])
            // In production, this would terminate the app
            #if !DEBUG
            fatalError("Security Error: Debugger detected")
            #endif

        } catch {
            AuditLogger.shared.log(.securityViolation, metadata: [
                "reason": error.localizedDescription
            ])
        }
    }

    /// Configure security settings for the app
    private func configureSecuritySettings() {
        // Disable screenshot for PHI-containing screens
        // Implemented per-screen in view modifiers

        // Configure network security
        NetworkManager.shared.configureTLS()

        // Initialize encryption service
        _ = EncryptionService.shared
    }
}

// MARK: - Content View Router

struct ContentView: View {
    @EnvironmentObject var sessionManager: SessionManager
    @EnvironmentObject var appState: AppState

    var body: some View {
        Group {
            if !appState.hasCompletedOnboarding {
                // Show onboarding flow
                OnboardingFlowView()
            } else if sessionManager.isAuthenticated {
                // Show main dashboard
                DashboardView()
            } else {
                // Show login screen
                LoginView()
            }
        }
        .onAppear {
            // HIPAA Session Management: Check for expired session
            sessionManager.validateSession()
        }
    }
}

// MARK: - App State

class AppState: ObservableObject {
    static let shared = AppState()

    @Published var hasCompletedOnboarding: Bool {
        didSet {
            UserDefaults.standard.set(hasCompletedOnboarding, forKey: "hasCompletedOnboarding")
        }
    }

    @Published var hasAcceptedPrivacyNotice: Bool {
        didSet {
            UserDefaults.standard.set(hasAcceptedPrivacyNotice, forKey: "hasAcceptedPrivacyNotice")
        }
    }

    private init() {
        self.hasCompletedOnboarding = UserDefaults.standard.bool(forKey: "hasCompletedOnboarding")
        self.hasAcceptedPrivacyNotice = UserDefaults.standard.bool(forKey: "hasAcceptedPrivacyNotice")
    }
}

// MARK: - App Info

struct AppInfo {
    static var version: String {
        Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0"
    }

    static var build: String {
        Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "1"
    }
}

// MARK: - Audit Events

extension AuditEvent {
    static let appLaunched = AuditEvent(type: "APP_LAUNCHED")
    static let appTerminated = AuditEvent(type: "APP_TERMINATED")
    static let securityViolation = AuditEvent(type: "SECURITY_VIOLATION")
}
