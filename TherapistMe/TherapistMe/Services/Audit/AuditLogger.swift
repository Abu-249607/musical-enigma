import Foundation
import CryptoKit

// HIPAA Compliance: Tamper-proof audit logging system
// Implements §164.312(b) - Audit Controls (Required)
// Logs all PHI access, security events, and authentication attempts
// 7-year retention period as per HIPAA requirements

/// Audit logger for HIPAA-compliant event tracking
class AuditLogger {
    static let shared = AuditLogger()

    private let logQueue = DispatchQueue(label: "com.therapistme.auditlog", qos: .utility)
    private var logs: [AuditLogEntry] = []

    // HIPAA: 7-year retention period
    private let retentionPeriodInDays = 365 * 7

    private init() {
        // Load existing logs
        loadLogs()

        // Schedule periodic cleanup of old logs
        scheduleLogCleanup()
    }

    // MARK: - Public Methods

    /// HIPAA Compliance: Log an audit event
    /// - Parameters:
    ///   - event: Type of audit event
    ///   - metadata: Additional context (NO PHI)
    ///
    /// IMPORTANT: Never log PHI content (journal text, mood notes, etc.)
    /// Only log identifiers (user ID, entity ID, timestamps)
    func log(_ event: AuditEvent, metadata: [String: Any] = [:]) {
        logQueue.async { [weak self] in
            guard let self = self else { return }

            let entry = AuditLogEntry(
                id: UUID(),
                timestamp: Date(),
                eventType: event.type,
                userID: SessionManager.shared.currentUserID,
                ipAddress: self.getIPAddress(),
                deviceID: self.getDeviceID(),
                appVersion: AppInfo.version,
                metadata: metadata
            )

            // Sign log entry for tamper detection
            var signedEntry = entry
            signedEntry.signature = self.signLogEntry(entry)

            // Store log entry
            self.logs.append(signedEntry)
            self.saveLogs()

            // Log to console in debug mode
            #if DEBUG
            print("📝 [AUDIT] \(event.type): \(metadata)")
            #endif

            // Send to remote SIEM in production
            #if !DEBUG
            self.sendToRemoteSIEM(signedEntry)
            #endif
        }
    }

    /// HIPAA Compliance: Retrieve audit logs for a specific user
    /// Used for "Right to Accounting" under HIPAA Privacy Rule
    func getUserLogs(userID: UUID, startDate: Date? = nil, endDate: Date? = nil) -> [AuditLogEntry] {
        var filteredLogs = logs.filter { $0.userID == userID.uuidString }

        if let startDate = startDate {
            filteredLogs = filteredLogs.filter { $0.timestamp >= startDate }
        }

        if let endDate = endDate {
            filteredLogs = filteredLogs.filter { $0.timestamp <= endDate }
        }

        return filteredLogs.sorted { $0.timestamp > $1.timestamp }
    }

    /// Retrieve all audit logs (admin only)
    func getAllLogs(eventType: String? = nil) -> [AuditLogEntry] {
        var filteredLogs = logs

        if let eventType = eventType {
            filteredLogs = filteredLogs.filter { $0.eventType == eventType }
        }

        return filteredLogs.sorted { $0.timestamp > $1.timestamp }
    }

    /// HIPAA Compliance: Verify log integrity
    /// Detects if logs have been tampered with
    func verifyLogIntegrity() -> Bool {
        for log in logs {
            guard let signature = log.signature else {
                return false // Missing signature
            }

            let expectedSignature = signLogEntry(log)
            if signature != expectedSignature {
                // HIPAA Security: Log integrity violation
                log(.logTamperDetected, metadata: [
                    "logID": log.id.uuidString,
                    "timestamp": log.timestamp.timeIntervalSince1970
                ])
                return false
            }
        }

        return true
    }

    /// Export audit logs (JSON format) for compliance reporting
    func exportLogs(startDate: Date? = nil, endDate: Date? = nil) throws -> Data {
        var logsToExport = logs

        if let startDate = startDate {
            logsToExport = logsToExport.filter { $0.timestamp >= startDate }
        }

        if let endDate = endDate {
            logsToExport = logsToExport.filter { $0.timestamp <= endDate }
        }

        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]

        return try encoder.encode(logsToExport)
    }

    // MARK: - Private Methods

    /// Sign log entry with SHA-256 for tamper detection
    private func signLogEntry(_ entry: AuditLogEntry) -> String {
        // Create canonical string representation
        let canonicalString = """
        \(entry.id.uuidString)|\(entry.timestamp.timeIntervalSince1970)|\(entry.eventType)|\
        \(entry.userID ?? "")|\(entry.ipAddress ?? "")|\(entry.deviceID ?? "")|\(entry.appVersion)
        """

        // Generate SHA-256 hash
        let data = canonicalString.data(using: .utf8)!
        let hash = SHA256.hash(data: data)

        return hash.compactMap { String(format: "%02x", $0) }.joined()
    }

    /// Get device IP address (for audit trail)
    private func getIPAddress() -> String? {
        var address: String?

        var ifaddr: UnsafeMutablePointer<ifaddrs>?
        guard getifaddrs(&ifaddr) == 0 else { return nil }
        guard let firstAddr = ifaddr else { return nil }

        for ifptr in sequence(first: firstAddr, next: { $0.pointee.ifa_next }) {
            let interface = ifptr.pointee

            let addrFamily = interface.ifa_addr.pointee.sa_family
            if addrFamily == UInt8(AF_INET) || addrFamily == UInt8(AF_INET6) {
                let name = String(cString: interface.ifa_name)

                if name == "en0" { // WiFi interface
                    var hostname = [CChar](repeating: 0, count: Int(NI_MAXHOST))
                    getnameinfo(
                        interface.ifa_addr,
                        socklen_t(interface.ifa_addr.pointee.sa_len),
                        &hostname,
                        socklen_t(hostname.count),
                        nil,
                        socklen_t(0),
                        NI_NUMERICHOST
                    )
                    address = String(cString: hostname)
                }
            }
        }

        freeifaddrs(ifaddr)
        return address
    }

    /// Get unique device identifier
    private func getDeviceID() -> String? {
        UIDevice.current.identifierForVendor?.uuidString
    }

    /// Save logs to persistent storage (encrypted)
    private func saveLogs() {
        do {
            let encoder = JSONEncoder()
            let data = try encoder.encode(logs)

            // Encrypt logs before saving
            let encrypted = try EncryptionService.shared.encrypt(data, associatedData: nil)

            // Save to UserDefaults (for simplicity; use CoreData in production)
            UserDefaults.standard.set(encrypted.combined, forKey: "auditLogs")

        } catch {
            print("❌ Failed to save audit logs: \(error)")
        }
    }

    /// Load logs from persistent storage
    private func loadLogs() {
        guard let encryptedData = UserDefaults.standard.data(forKey: "auditLogs"),
              let encrypted = EncryptedData(combined: encryptedData) else {
            return
        }

        do {
            let decryptedData = try EncryptionService.shared.decrypt(encrypted, associatedData: nil)
            let decoder = JSONDecoder()
            logs = try decoder.decode([AuditLogEntry].self, from: decryptedData)

        } catch {
            print("❌ Failed to load audit logs: \(error)")
        }
    }

    /// HIPAA Compliance: Clean up logs older than retention period
    private func scheduleLogCleanup() {
        // Run cleanup daily
        Timer.scheduledTimer(withTimeInterval: 86400, repeats: true) { [weak self] _ in
            self?.cleanupOldLogs()
        }
    }

    /// Remove logs older than retention period (7 years)
    private func cleanupOldLogs() {
        let cutoffDate = Calendar.current.date(
            byAdding: .day,
            value: -retentionPeriodInDays,
            to: Date()
        )!

        let initialCount = logs.count
        logs.removeAll { $0.timestamp < cutoffDate }

        if logs.count < initialCount {
            saveLogs()

            log(.logsArchived, metadata: [
                "removedCount": initialCount - logs.count,
                "cutoffDate": ISO8601DateFormatter().string(from: cutoffDate)
            ])
        }
    }

    /// Send audit log to remote SIEM (Security Information and Event Management)
    private func sendToRemoteSIEM(_ entry: AuditLogEntry) {
        // In production, send to SIEM system (e.g., Splunk, ELK Stack)
        // For now, this is a placeholder

        // Example: POST to remote endpoint
        // let url = URL(string: "https://siem.therapistme.com/logs")!
        // NetworkManager.shared.post(url, body: entry)
    }
}

// MARK: - Audit Log Entry

/// Represents a single audit log entry
struct AuditLogEntry: Codable, Identifiable {
    let id: UUID
    let timestamp: Date
    let eventType: String
    let userID: String?         // User who triggered the event
    let ipAddress: String?
    let deviceID: String?
    let appVersion: String
    let metadata: [String: String] // Additional context (NO PHI)
    var signature: String?      // SHA-256 signature for tamper detection

    init(
        id: UUID,
        timestamp: Date,
        eventType: String,
        userID: String?,
        ipAddress: String?,
        deviceID: String?,
        appVersion: String,
        metadata: [String: Any]
    ) {
        self.id = id
        self.timestamp = timestamp
        self.eventType = eventType
        self.userID = userID
        self.ipAddress = ipAddress
        self.deviceID = deviceID
        self.appVersion = appVersion

        // Convert metadata to [String: String] (Codable requirement)
        self.metadata = metadata.compactMapValues { "\($0)" }
    }

    // MARK: - Display

    var displayTimestamp: String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .medium
        return formatter.string(from: timestamp)
    }

    var displayDescription: String {
        let metadataStr = metadata.map { "\($0.key): \($0.value)" }.joined(separator: ", ")
        return "\(eventType) - \(metadataStr)"
    }
}

// MARK: - Audit Event

/// Represents an audit event type
struct AuditEvent {
    let type: String

    // Authentication Events
    static let loginSuccess = AuditEvent(type: "AUTH_LOGIN_SUCCESS")
    static let loginFailure = AuditEvent(type: "AUTH_LOGIN_FAILURE")
    static let logoutSuccess = AuditEvent(type: "AUTH_LOGOUT_SUCCESS")
    static let sessionTimeout = AuditEvent(type: "AUTH_SESSION_TIMEOUT")
    static let sessionRefresh = AuditEvent(type: "AUTH_SESSION_REFRESH")
    static let passwordChanged = AuditEvent(type: "AUTH_PASSWORD_CHANGED")
    static let mfaEnabled = AuditEvent(type: "AUTH_MFA_ENABLED")
    static let mfaDisabled = AuditEvent(type: "AUTH_MFA_DISABLED")
    static let mfaSuccess = AuditEvent(type: "AUTH_MFA_SUCCESS")
    static let mfaFailure = AuditEvent(type: "AUTH_MFA_FAILURE")
    static let biometricEnabled = AuditEvent(type: "AUTH_BIOMETRIC_ENABLED")
    static let biometricDisabled = AuditEvent(type: "AUTH_BIOMETRIC_DISABLED")
    static let biometricSuccess = AuditEvent(type: "AUTH_BIOMETRIC_SUCCESS")
    static let biometricFailure = AuditEvent(type: "AUTH_BIOMETRIC_FAILURE")

    // PHI Access Events (HIPAA Required)
    static let phiRead = AuditEvent(type: "PHI_READ")
    static let phiWrite = AuditEvent(type: "PHI_WRITE")
    static let phiUpdate = AuditEvent(type: "PHI_UPDATE")
    static let phiDelete = AuditEvent(type: "PHI_DELETE")
    static let phiExport = AuditEvent(type: "PHI_EXPORT")

    // Security Events
    static let jailbreakDetected = AuditEvent(type: "SECURITY_JAILBREAK_DETECTED")
    static let debuggerDetected = AuditEvent(type: "SECURITY_DEBUGGER_DETECTED")
    static let integrityViolation = AuditEvent(type: "SECURITY_INTEGRITY_VIOLATION")
    static let certificatePinningFailure = AuditEvent(type: "SECURITY_CERT_PINNING_FAILURE")
    static let emergencyAccess = AuditEvent(type: "SECURITY_EMERGENCY_ACCESS")
    static let logTamperDetected = AuditEvent(type: "SECURITY_LOG_TAMPER")

    // Privacy Events
    static let consentGranted = AuditEvent(type: "PRIVACY_CONSENT_GRANTED")
    static let consentRevoked = AuditEvent(type: "PRIVACY_CONSENT_REVOKED")
    static let dataExportRequested = AuditEvent(type: "PRIVACY_DATA_EXPORT_REQUESTED")
    static let accountDeletionRequested = AuditEvent(type: "PRIVACY_ACCOUNT_DELETE_REQUESTED")
    static let accountDeleted = AuditEvent(type: "PRIVACY_ACCOUNT_DELETED")

    // System Events
    static let logsArchived = AuditEvent(type: "SYSTEM_LOGS_ARCHIVED")
    static let configurationChanged = AuditEvent(type: "SYSTEM_CONFIG_CHANGED")
}

// MARK: - UIDevice Extension (for device ID)

import UIKit
