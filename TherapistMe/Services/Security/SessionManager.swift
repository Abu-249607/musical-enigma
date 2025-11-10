//
//  SessionManager.swift
//  Therapist.Me
//
//  HIPAA Compliance: Session management with automatic timeout
//

import Foundation
import Combine
import LocalAuthentication

class SessionManager: ObservableObject {
    static let shared = SessionManager()

    // HIPAA Compliance: Session timeout after 15 minutes of inactivity
    private let sessionTimeoutInterval: TimeInterval = 15 * 60 // 15 minutes

    @Published var isSessionActive: Bool = false
    @Published var isSessionExpired: Bool = false
    @Published var currentUser: User?

    private var sessionStartTime: Date?
    private var lastActivityTime: Date?
    private var backgroundTimer: Timer?
    private var activityTimer: Timer?

    private let keychain = KeychainService.shared

    private init() {
        setupActivityMonitoring()
    }

    // MARK: - Session Lifecycle

    /// Start new session after successful authentication
    func startSession(user: User) {
        sessionStartTime = Date()
        lastActivityTime = Date()
        isSessionActive = true
        isSessionExpired = false
        currentUser = user

        startActivityTimer()

        AuditLogger.shared.log(
            event: .sessionStarted,
            details: "User session started",
            userId: user.id.uuidString,
            severity: .medium
        )

        // Save session token
        let sessionToken = UUID().uuidString
        keychain.save(sessionToken, for: KeychainService.Keys.sessionToken)
    }

    /// End current session
    func endSession() {
        guard let user = currentUser else { return }

        stopActivityTimer()

        isSessionActive = false
        sessionStartTime = nil
        lastActivityTime = nil

        AuditLogger.shared.log(
            event: .logoutPerformed,
            details: "User session ended",
            userId: user.id.uuidString,
            severity: .medium
        )

        // Clear session data
        keychain.delete(KeychainService.Keys.sessionToken)
        currentUser = nil
    }

    /// HIPAA Compliance: Expire session due to inactivity
    func expireSession() {
        guard let user = currentUser else { return }

        stopActivityTimer()

        isSessionActive = false
        isSessionExpired = true

        AuditLogger.shared.log(
            event: .sessionExpired,
            details: "Session expired due to inactivity",
            userId: user.id.uuidString,
            severity: .high
        )

        // Lock sensitive data
        SecurityManager.shared.lockSensitiveData()
    }

    /// Resume session (after returning from background)
    func resumeSession() {
        guard let lastActivity = lastActivityTime,
              isSessionActive else {
            return
        }

        let timeSinceLastActivity = Date().timeIntervalSince(lastActivity)

        if timeSinceLastActivity > sessionTimeoutInterval {
            // Session has expired
            expireSession()
        } else {
            // Update activity time
            updateActivity()

            AuditLogger.shared.log(
                event: .sessionUnlocked,
                details: "Session resumed",
                userId: currentUser?.id.uuidString,
                severity: .medium
            )
        }
    }

    /// Renew expired session with authentication
    func renewSession() {
        authenticate { [weak self] success in
            if success {
                self?.isSessionExpired = false
                self?.isSessionActive = true
                self?.lastActivityTime = Date()
                self?.startActivityTimer()

                AuditLogger.shared.log(
                    event: .sessionStarted,
                    details: "Session renewed after authentication",
                    userId: self?.currentUser?.id.uuidString,
                    severity: .medium
                )
            }
        }
    }

    // MARK: - Activity Monitoring

    /// Update last activity time
    func updateActivity() {
        lastActivityTime = Date()
    }

    private func setupActivityMonitoring() {
        // Monitor for user interaction
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(userDidInteract),
            name: NSNotification.Name("UserInteraction"),
            object: nil
        )
    }

    @objc private func userDidInteract() {
        updateActivity()
    }

    private func startActivityTimer() {
        stopActivityTimer()

        // Check for inactivity every minute
        activityTimer = Timer.scheduledTimer(withTimeInterval: 60, repeats: true) { [weak self] _ in
            self?.checkSessionTimeout()
        }
    }

    private func stopActivityTimer() {
        activityTimer?.invalidate()
        activityTimer = nil
    }

    private func checkSessionTimeout() {
        guard let lastActivity = lastActivityTime,
              isSessionActive else {
            return
        }

        let timeSinceLastActivity = Date().timeIntervalSince(lastActivity)

        if timeSinceLastActivity > sessionTimeoutInterval {
            expireSession()
        } else if timeSinceLastActivity > (sessionTimeoutInterval - 300) {
            // Warn user 5 minutes before timeout
            showTimeoutWarning()
        }
    }

    private func showTimeoutWarning() {
        // Post notification for UI to show warning
        NotificationCenter.default.post(name: NSNotification.Name("SessionTimeoutWarning"), object: nil)
    }

    // MARK: - Background Timer

    /// HIPAA Compliance: Start background timer when app enters background
    func startBackgroundTimer() {
        backgroundTimer?.invalidate()

        // Lock session after 5 minutes in background
        backgroundTimer = Timer.scheduledTimer(withTimeInterval: 300, repeats: false) { [weak self] _ in
            self?.lockSession()
        }

        AuditLogger.shared.log(
            event: .appBackgrounded,
            details: "Background timer started",
            userId: currentUser?.id.uuidString,
            severity: .low
        )
    }

    private func lockSession() {
        guard let user = currentUser else { return }

        isSessionActive = false

        AuditLogger.shared.log(
            event: .sessionLocked,
            details: "Session locked due to background timeout",
            userId: user.id.uuidString,
            severity: .medium
        )

        AppCoordinator.shared.currentState = .locked
    }

    // MARK: - Authentication

    /// Authenticate user with biometrics or passcode
    func authenticate(completion: @escaping (Bool) -> Void) {
        let context = LAContext()
        var error: NSError?

        // Check if biometric authentication is available
        if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {
            let reason = "Authenticate to access Therapist.Me"

            context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: reason) { [weak self] success, error in
                DispatchQueue.main.async {
                    if success {
                        AuditLogger.shared.log(
                            event: .biometricAuthSuccess,
                            details: "Biometric authentication successful",
                            userId: self?.currentUser?.id.uuidString,
                            severity: .medium
                        )
                        completion(true)
                    } else {
                        AuditLogger.shared.log(
                            event: .biometricAuthFailed,
                            details: "Biometric authentication failed: \(error?.localizedDescription ?? "Unknown")",
                            userId: self?.currentUser?.id.uuidString,
                            severity: .high
                        )
                        completion(false)
                    }
                }
            }
        } else {
            // Fallback to passcode
            authenticateWithPasscode(completion: completion)
        }
    }

    private func authenticateWithPasscode(completion: @escaping (Bool) -> Void) {
        // In production, implement passcode authentication
        // For now, use device passcode authentication

        let context = LAContext()
        context.evaluatePolicy(.deviceOwnerAuthentication, localizedReason: "Authenticate to access Therapist.Me") { [weak self] success, error in
            DispatchQueue.main.async {
                if success {
                    AuditLogger.shared.log(
                        event: .loginSuccess,
                        details: "Passcode authentication successful",
                        userId: self?.currentUser?.id.uuidString,
                        severity: .medium
                    )
                    completion(true)
                } else {
                    AuditLogger.shared.log(
                        event: .loginFailed,
                        details: "Passcode authentication failed: \(error?.localizedDescription ?? "Unknown")",
                        userId: self?.currentUser?.id.uuidString,
                        severity: .high
                    )
                    completion(false)
                }
            }
        }
    }

    // MARK: - Session Info

    var sessionDuration: TimeInterval? {
        guard let startTime = sessionStartTime else { return nil }
        return Date().timeIntervalSince(startTime)
    }

    var timeUntilTimeout: TimeInterval? {
        guard let lastActivity = lastActivityTime else { return nil }
        let elapsed = Date().timeIntervalSince(lastActivity)
        return max(0, sessionTimeoutInterval - elapsed)
    }
}
