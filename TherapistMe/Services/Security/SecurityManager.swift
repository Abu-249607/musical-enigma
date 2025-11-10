//
//  SecurityManager.swift
//  Therapist.Me
//
//  HIPAA Compliance: Central security management
//

import Foundation
import LocalAuthentication

class SecurityManager: ObservableObject {
    static let shared = SecurityManager()

    @Published var isDataLocked: Bool = false
    @Published var securityLevel: SecurityLevel = .standard

    private let encryptionService = EncryptionService.shared
    private let keychain = KeychainService.shared

    private init() {
        evaluateSecurityLevel()
    }

    // MARK: - Security Level

    enum SecurityLevel {
        case standard
        case enhanced
        case maximum
    }

    func evaluateSecurityLevel() {
        let context = LAContext()
        var error: NSError?

        // Check available security features
        let hasBiometrics = context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
        let hasPasscode = context.canEvaluatePolicy(.deviceOwnerAuthentication, error: &error)

        if hasBiometrics {
            securityLevel = .maximum
        } else if hasPasscode {
            securityLevel = .enhanced
        } else {
            securityLevel = .standard

            AuditLogger.shared.log(
                event: .securityError,
                details: "Device does not have biometric or passcode protection",
                severity: .critical
            )
        }
    }

    // MARK: - Data Protection

    /// HIPAA Compliance: Lock sensitive data when app goes to background
    func lockSensitiveData() {
        isDataLocked = true

        AuditLogger.shared.log(
            event: .sessionLocked,
            details: "Sensitive data locked",
            severity: .medium
        )
    }

    /// Unlock sensitive data after authentication
    func unlockSensitiveData() {
        isDataLocked = false

        AuditLogger.shared.log(
            event: .sessionUnlocked,
            details: "Sensitive data unlocked",
            severity: .medium
        )
    }

    // MARK: - Biometric Authentication

    func isBiometricsAvailable() -> Bool {
        let context = LAContext()
        var error: NSError?
        return context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
    }

    func biometricType() -> BiometricType {
        let context = LAContext()
        var error: NSError?

        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            return .none
        }

        switch context.biometryType {
        case .faceID:
            return .faceID
        case .touchID:
            return .touchID
        case .opticID:
            return .opticID
        case .none:
            return .none
        @unknown default:
            return .none
        }
    }

    enum BiometricType {
        case none
        case touchID
        case faceID
        case opticID

        var displayName: String {
            switch self {
            case .none: return "None"
            case .touchID: return "Touch ID"
            case .faceID: return "Face ID"
            case .opticID: return "Optic ID"
            }
        }

        var icon: String {
            switch self {
            case .none: return "lock"
            case .touchID: return "touchid"
            case .faceID: return "faceid"
            case .opticID: return "opticid"
            }
        }
    }

    // MARK: - Emergency Access

    /// HIPAA Compliance: Emergency access for critical situations
    func requestEmergencyAccess(code: String, completion: @escaping (Bool) -> Void) {
        // Verify emergency access code
        guard let storedCode = keychain.getString(for: KeychainService.Keys.emergencyAccessCode) else {
            AuditLogger.shared.log(
                event: .emergencyAccessDenied,
                details: "No emergency access code configured",
                severity: .high
            )
            completion(false)
            return
        }

        if code == storedCode {
            AuditLogger.shared.log(
                event: .emergencyAccessGranted,
                details: "Emergency access granted",
                severity: .critical
            )
            completion(true)
        } else {
            AuditLogger.shared.log(
                event: .emergencyAccessDenied,
                details: "Invalid emergency access code",
                severity: .high
            )
            completion(false)
        }
    }

    func setEmergencyAccessCode(_ code: String) {
        keychain.save(code, for: KeychainService.Keys.emergencyAccessCode)

        AuditLogger.shared.log(
            event: .phiModified,
            details: "Emergency access code configured",
            severity: .high
        )
    }

    // MARK: - Security Checks

    /// Check if device is jailbroken (security risk)
    func isDeviceCompromised() -> Bool {
        #if targetEnvironment(simulator)
        return false
        #else
        // Check for common jailbreak indicators
        let suspiciousPaths = [
            "/Applications/Cydia.app",
            "/Library/MobileSubstrate/MobileSubstrate.dylib",
            "/bin/bash",
            "/usr/sbin/sshd",
            "/etc/apt",
            "/private/var/lib/apt/"
        ]

        for path in suspiciousPaths {
            if FileManager.default.fileExists(atPath: path) {
                AuditLogger.shared.log(
                    event: .securityError,
                    details: "Device appears to be jailbroken: \(path)",
                    severity: .critical
                )
                return true
            }
        }

        // Try to write to system directory
        let testPath = "/private/jailbreak.txt"
        do {
            try "test".write(toFile: testPath, atomically: true, encoding: .utf8)
            try? FileManager.default.removeItem(atPath: testPath)

            AuditLogger.shared.log(
                event: .securityError,
                details: "Device appears to be jailbroken: write test succeeded",
                severity: .critical
            )
            return true
        } catch {
            // Good - unable to write to system directory
        }

        return false
        #endif
    }

    /// Check if debugger is attached (security risk in production)
    func isDebuggerAttached() -> Bool {
        var info = kinfo_proc()
        var mib: [Int32] = [CTL_KERN, KERN_PROC, KERN_PROC_PID, getpid()]
        var size = MemoryLayout<kinfo_proc>.stride

        let result = sysctl(&mib, UInt32(mib.count), &info, &size, nil, 0)

        if result != 0 {
            return false
        }

        return (info.kp_proc.p_flag & P_TRACED) != 0
    }

    /// Perform comprehensive security check
    func performSecurityCheck() -> SecurityCheckResult {
        var issues: [String] = []

        if isDeviceCompromised() {
            issues.append("Device appears to be jailbroken")
        }

        #if !DEBUG
        if isDebuggerAttached() {
            issues.append("Debugger is attached")
        }
        #endif

        if !isBiometricsAvailable() {
            issues.append("Biometric authentication not available")
        }

        if securityLevel == .standard {
            issues.append("Device security level is insufficient")
        }

        let result = SecurityCheckResult(
            passed: issues.isEmpty,
            issues: issues,
            securityLevel: securityLevel
        )

        if !result.passed {
            AuditLogger.shared.log(
                event: .securityError,
                details: "Security check failed: \(issues.joined(separator: ", "))",
                severity: .critical
            )
        }

        return result
    }

    struct SecurityCheckResult {
        let passed: Bool
        let issues: [String]
        let securityLevel: SecurityLevel
    }
}
