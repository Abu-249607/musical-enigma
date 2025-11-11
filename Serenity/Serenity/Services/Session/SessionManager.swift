import Foundation
import Combine

// HIPAA Compliance: Secure session management
// Implements §164.312(a)(2)(iii) - Automatic Logoff (Addressable)
// 15-minute inactivity timeout as per HIPAA recommendations

/// Manages user authentication sessions with automatic timeout
class SessionManager: ObservableObject {
    static let shared = SessionManager()

    // HIPAA: 15-minute session timeout (900 seconds)
    static let sessionTimeout: TimeInterval = 900

    // Published properties for SwiftUI
    @Published var isAuthenticated: Bool = false
    @Published var currentUser: User?

    // Session state
    private var sessionToken: String?
    private var lastActivityTime: Date?
    private var sessionExpiryTimer: Timer?

    // Computed properties
    var currentUserID: String? {
        currentUser?.id.uuidString
    }

    private init() {
        // Restore session if exists
        restoreSession()

        // Start session monitoring
        startSessionMonitoring()
    }

    // MARK: - Session Management

    /// HIPAA Compliance: Start authenticated session
    /// - Parameters:
    ///   - user: Authenticated user
    ///   - token: Session token
    func startSession(user: User, token: String) {
        self.currentUser = user
        self.sessionToken = token
        self.isAuthenticated = true
        self.lastActivityTime = Date()

        // Save session to keychain (encrypted)
        saveSession()

        // Start session timeout timer
        resetSessionTimer()

        // HIPAA Audit: Log session start
        AuditLogger.shared.log(.loginSuccess, metadata: [
            "userID": user.id.uuidString,
            "email": user.email
        ])
    }

    /// HIPAA Compliance: End authenticated session
    /// - Parameter reason: Reason for session termination
    func endSession(reason: SessionEndReason = .userLogout) {
        // HIPAA Audit: Log session end
        if let user = currentUser {
            let event: AuditEvent = reason == .timeout ? .sessionTimeout : .logoutSuccess

            AuditLogger.shared.log(event, metadata: [
                "userID": user.id.uuidString,
                "reason": reason.rawValue
            ])
        }

        // Clear session data
        self.currentUser = nil
        self.sessionToken = nil
        self.isAuthenticated = false
        self.lastActivityTime = nil

        // Stop session timer
        sessionExpiryTimer?.invalidate()
        sessionExpiryTimer = nil

        // Clear saved session
        clearSavedSession()
    }

    /// HIPAA Compliance: Update last activity time
    /// Resets session timeout timer
    func updateActivity() {
        self.lastActivityTime = Date()
        resetSessionTimer()
    }

    /// HIPAA Compliance: Validate session is still active
    /// Checks if session has expired due to inactivity
    func validateSession() {
        guard isAuthenticated,
              let lastActivity = lastActivityTime else {
            endSession(reason: .invalidSession)
            return
        }

        let inactiveDuration = Date().timeIntervalSince(lastActivity)

        if inactiveDuration >= Self.sessionTimeout {
            // Session expired due to inactivity
            endSession(reason: .timeout)
        }
    }

    /// Refresh session token
    func refreshSession() async throws {
        guard let currentToken = sessionToken else {
            throw SessionError.noActiveSession
        }

        // In production, this would call API to refresh token
        // For MVP, we just extend the session
        updateActivity()

        // HIPAA Audit: Log session refresh
        AuditLogger.shared.log(.sessionRefresh, metadata: [:])
    }

    // MARK: - Session Persistence

    /// Save session to keychain (for app restart)
    private func saveSession() {
        guard let user = currentUser,
              let token = sessionToken else {
            return
        }

        do {
            let sessionData = SessionData(
                user: user,
                token: token,
                lastActivity: Date()
            )

            let encoder = JSONEncoder()
            let data = try encoder.encode(sessionData)

            // Store in keychain (encrypted)
            try KeychainManager.shared.storeData(
                data,
                identifier: "userSession",
                requiresBiometric: false
            )

        } catch {
            print("❌ Failed to save session: \(error)")
        }
    }

    /// Restore session from keychain
    private func restoreSession() {
        do {
            let data = try KeychainManager.shared.retrieveData(identifier: "userSession")
            let decoder = JSONDecoder()
            let sessionData = try decoder.decode(SessionData.self, from: data)

            // Check if session is still valid (within 24 hours)
            let sessionAge = Date().timeIntervalSince(sessionData.lastActivity)
            guard sessionAge < 86400 else { // 24 hours
                clearSavedSession()
                return
            }

            // Restore session
            self.currentUser = sessionData.user
            self.sessionToken = sessionData.token
            self.isAuthenticated = true
            self.lastActivityTime = Date()

            resetSessionTimer()

        } catch {
            // No saved session or failed to restore
            clearSavedSession()
        }
    }

    /// Clear saved session from keychain
    private func clearSavedSession() {
        try? KeychainManager.shared.deleteData(identifier: "userSession")
    }

    // MARK: - Session Timeout Timer

    /// Start session monitoring (check for inactivity)
    private func startSessionMonitoring() {
        // Check session validity every minute
        Timer.scheduledTimer(withTimeInterval: 60, repeats: true) { [weak self] _ in
            self?.validateSession()
        }
    }

    /// Reset session timeout timer
    private func resetSessionTimer() {
        // Invalidate existing timer
        sessionExpiryTimer?.invalidate()

        // Create new timer for session timeout
        sessionExpiryTimer = Timer.scheduledTimer(
            withTimeInterval: Self.sessionTimeout,
            repeats: false
        ) { [weak self] _ in
            // Session expired due to inactivity
            self?.endSession(reason: .timeout)
        }
    }

    // MARK: - Biometric Re-authentication

    /// HIPAA Compliance: Require biometric re-authentication for sensitive operations
    /// Used before PHI export, account deletion, etc.
    func requireBiometricAuth() async throws {
        guard let biometricAuth = BiometricAuth.shared else {
            throw SessionError.biometricNotAvailable
        }

        let success = try await biometricAuth.authenticate(
            reason: "Authenticate to access sensitive data"
        )

        if !success {
            throw SessionError.biometricAuthFailed
        }

        // Update activity after successful auth
        updateActivity()
    }
}

// MARK: - Session Data

/// Session data for persistence
private struct SessionData: Codable {
    let user: User
    let token: String
    let lastActivity: Date
}

// MARK: - Session End Reason

enum SessionEndReason: String {
    case userLogout = "User Logout"
    case timeout = "Inactivity Timeout"
    case invalidSession = "Invalid Session"
    case forceLogout = "Force Logout"
}

// MARK: - Session Errors

enum SessionError: LocalizedError {
    case noActiveSession
    case sessionExpired
    case biometricNotAvailable
    case biometricAuthFailed

    var errorDescription: String? {
        switch self {
        case .noActiveSession:
            return "No active session"
        case .sessionExpired:
            return "Your session has expired. Please log in again."
        case .biometricNotAvailable:
            return "Biometric authentication is not available"
        case .biometricAuthFailed:
            return "Biometric authentication failed"
        }
    }
}
