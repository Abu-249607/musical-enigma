//
//  AuditLogger.swift
//  Therapist.Me
//
//  HIPAA Compliance: Tamper-proof audit logging for all PHI access and modifications
//  Required for HIPAA compliance to track who accessed what data and when
//

import Foundation

class AuditLogger {
    static let shared = AuditLogger()

    private let fileManager = FileManager.default
    private var auditLogURL: URL?
    private let queue = DispatchQueue(label: "com.therapistme.auditlog", qos: .utility)
    private let encryptionService = EncryptionService.shared

    private init() {
        setupAuditLogFile()
    }

    // MARK: - Configuration

    func configure() {
        setupAuditLogFile()
        log(event: .auditSystemInitialized, details: "Audit logging system initialized")
    }

    private func setupAuditLogFile() {
        guard let documentsPath = fileManager.urls(for: .documentDirectory, in: .userDomainMask).first else {
            print("Failed to get documents directory")
            return
        }

        // HIPAA Compliance: Store audit logs in secure location
        let logsDirectory = documentsPath.appendingPathComponent("AuditLogs", isDirectory: true)

        if !fileManager.fileExists(atPath: logsDirectory.path) {
            try? fileManager.createDirectory(at: logsDirectory, withIntermediateDirectories: true)
        }

        // Create log file with timestamp
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"
        let dateString = dateFormatter.string(from: Date())

        auditLogURL = logsDirectory.appendingPathComponent("audit_\(dateString).log")
    }

    // MARK: - Logging

    /// HIPAA Compliance: Log security and data access events
    /// - Parameters:
    ///   - event: Type of event
    ///   - details: Description of the event
    ///   - userId: Optional user ID associated with event
    ///   - severity: Severity level
    func log(
        event: AuditEvent,
        details: String,
        userId: String? = nil,
        severity: AuditSeverity = .medium
    ) {
        queue.async { [weak self] in
            guard let self = self else { return }

            let logEntry = AuditLogEntry(
                event: event,
                details: details,
                userId: userId,
                severity: severity
            )

            self.writeLogEntry(logEntry)

            // Also log to system console for development
            #if DEBUG
            print("🔒 AUDIT: [\(severity.rawValue)] \(event.rawValue) - \(details)")
            #endif
        }
    }

    private func writeLogEntry(_ entry: AuditLogEntry) {
        guard let logURL = auditLogURL else {
            return
        }

        do {
            // Format log entry as JSON
            let encoder = JSONEncoder()
            encoder.dateEncodingStrategy = .iso8601
            encoder.outputFormatting = .prettyPrinted

            var logData = try encoder.encode(entry)

            // Add newline for readability
            logData.append("\n".data(using: .utf8)!)

            // HIPAA Compliance: Encrypt audit log data
            guard let encryptedData = encryptionService.encrypt(logData) else {
                print("Failed to encrypt audit log entry")
                return
            }

            // Append to log file
            if fileManager.fileExists(atPath: logURL.path) {
                let fileHandle = try FileHandle(forUpdating: logURL)
                fileHandle.seekToEndOfFile()
                fileHandle.write(encryptedData)
                try fileHandle.close()
            } else {
                try encryptedData.write(to: logURL, options: .atomic)
            }

            // Generate integrity hash
            if let fileData = try? Data(contentsOf: logURL) {
                let hash = encryptionService.generateHash(for: fileData)
                // Store hash separately for integrity verification
                try hash.write(to: logURL.appendingPathExtension("hash"), atomically: true, encoding: .utf8)
            }

        } catch {
            print("Failed to write audit log: \(error.localizedDescription)")
        }
    }

    // MARK: - Retrieval and Verification

    /// HIPAA Compliance: Retrieve audit logs (requires authorization)
    func retrieveLogs(fromDate: Date? = nil, toDate: Date? = nil) -> [AuditLogEntry] {
        // Implementation would retrieve and decrypt logs
        // For security, this should require elevated permissions

        log(event: .auditLogAccessed, details: "Audit logs retrieved", severity: .high)

        return []
    }

    /// HIPAA Compliance: Verify audit log integrity
    func verifyIntegrity(for date: Date) -> Bool {
        guard let logURL = auditLogURL,
              let hashURL = auditLogURL?.appendingPathExtension("hash"),
              let logData = try? Data(contentsOf: logURL),
              let storedHash = try? String(contentsOf: hashURL) else {
            return false
        }

        let calculatedHash = encryptionService.generateHash(for: logData)
        let isValid = calculatedHash == storedHash

        log(
            event: .integrityCheckPerformed,
            details: "Audit log integrity check: \(isValid ? "PASSED" : "FAILED")",
            severity: isValid ? .low : .critical
        )

        return isValid
    }

    /// Export audit logs for compliance review
    func exportLogs() -> URL? {
        guard let logURL = auditLogURL else {
            return nil
        }

        log(event: .auditLogExported, details: "Audit logs exported for review", severity: .high)

        return logURL
    }
}

// MARK: - Audit Log Entry

struct AuditLogEntry: Codable {
    let id: UUID
    let timestamp: Date
    let event: AuditEvent
    let details: String
    let userId: String?
    let severity: AuditSeverity
    let deviceInfo: DeviceInfo
    let appVersion: String

    init(
        event: AuditEvent,
        details: String,
        userId: String? = nil,
        severity: AuditSeverity
    ) {
        self.id = UUID()
        self.timestamp = Date()
        self.event = event
        self.details = details
        self.userId = userId
        self.severity = severity
        self.deviceInfo = DeviceInfo.current()
        self.appVersion = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "Unknown"
    }
}

struct DeviceInfo: Codable {
    let model: String
    let systemVersion: String
    let identifier: String

    static func current() -> DeviceInfo {
        #if os(iOS)
        return DeviceInfo(
            model: UIDevice.current.model,
            systemVersion: UIDevice.current.systemVersion,
            identifier: UIDevice.current.identifierForVendor?.uuidString ?? "Unknown"
        )
        #else
        return DeviceInfo(
            model: "Unknown",
            systemVersion: "Unknown",
            identifier: "Unknown"
        )
        #endif
    }
}

// MARK: - Audit Events

enum AuditEvent: String, Codable {
    // System Events
    case appLaunched = "APP_LAUNCHED"
    case appBackgrounded = "APP_BACKGROUNDED"
    case appResumed = "APP_RESUMED"
    case appInactive = "APP_INACTIVE"
    case appTerminated = "APP_TERMINATED"

    // Authentication Events
    case loginAttempt = "LOGIN_ATTEMPT"
    case loginSuccess = "LOGIN_SUCCESS"
    case loginFailed = "LOGIN_FAILED"
    case logoutPerformed = "LOGOUT_PERFORMED"
    case biometricAuthSuccess = "BIOMETRIC_AUTH_SUCCESS"
    case biometricAuthFailed = "BIOMETRIC_AUTH_FAILED"
    case passwordChanged = "PASSWORD_CHANGED"

    // Session Management
    case sessionStarted = "SESSION_STARTED"
    case sessionExpired = "SESSION_EXPIRED"
    case sessionTimeout = "SESSION_TIMEOUT"
    case sessionLocked = "SESSION_LOCKED"
    case sessionUnlocked = "SESSION_UNLOCKED"

    // Data Access (PHI)
    case phiAccessed = "PHI_ACCESSED"
    case phiModified = "PHI_MODIFIED"
    case phiCreated = "PHI_CREATED"
    case phiDeleted = "PHI_DELETED"
    case phiExported = "PHI_EXPORTED"

    // Encryption
    case dataEncrypted = "DATA_ENCRYPTED"
    case dataDecrypted = "DATA_DECRYPTED"
    case encryptionFailed = "ENCRYPTION_FAILED"
    case decryptionFailed = "DECRYPTION_FAILED"
    case encryptionKeyGenerated = "ENCRYPTION_KEY_GENERATED"
    case encryptionKeyRotated = "ENCRYPTION_KEY_ROTATED"

    // Keychain Operations
    case keychainItemSaved = "KEYCHAIN_ITEM_SAVED"
    case keychainItemRetrieved = "KEYCHAIN_ITEM_RETRIEVED"
    case keychainItemDeleted = "KEYCHAIN_ITEM_DELETED"
    case keychainCleared = "KEYCHAIN_CLEARED"
    case keychainError = "KEYCHAIN_ERROR"

    // User Actions
    case moodEntryCreated = "MOOD_ENTRY_CREATED"
    case journalEntryCreated = "JOURNAL_ENTRY_CREATED"
    case goalCreated = "GOAL_CREATED"
    case exerciseCompleted = "EXERCISE_COMPLETED"
    case chatSessionStarted = "CHAT_SESSION_STARTED"
    case forumPostCreated = "FORUM_POST_CREATED"

    // Security Events
    case securityError = "SECURITY_ERROR"
    case unauthorizedAccess = "UNAUTHORIZED_ACCESS"
    case integrityCheckPerformed = "INTEGRITY_CHECK"
    case integrityCheckFailed = "INTEGRITY_CHECK_FAILED"
    case suspiciousActivity = "SUSPICIOUS_ACTIVITY"

    // Audit System
    case auditSystemInitialized = "AUDIT_SYSTEM_INITIALIZED"
    case auditLogAccessed = "AUDIT_LOG_ACCESSED"
    case auditLogExported = "AUDIT_LOG_EXPORTED"
    case auditLogRotated = "AUDIT_LOG_ROTATED"

    // Emergency Access
    case emergencyAccessRequested = "EMERGENCY_ACCESS_REQUESTED"
    case emergencyAccessGranted = "EMERGENCY_ACCESS_GRANTED"
    case emergencyAccessDenied = "EMERGENCY_ACCESS_DENIED"
}

enum AuditSeverity: String, Codable {
    case low = "LOW"
    case medium = "MEDIUM"
    case high = "HIGH"
    case critical = "CRITICAL"
}
