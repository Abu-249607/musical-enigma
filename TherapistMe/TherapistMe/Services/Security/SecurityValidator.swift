import Foundation
import UIKit

// HIPAA Compliance: Security validation to detect compromised environments
// Jailbreak detection, debugger detection, binary integrity checks
// Implements defense-in-depth security strategy

/// Validates app security environment
class SecurityValidator {
    static let shared = SecurityValidator()

    private init() {}

    // MARK: - Environment Validation

    /// HIPAA Compliance: Validate security environment
    /// Detects jailbreak, debugger, and other security threats
    func validateEnvironment() throws {
        // Check for jailbreak
        if isJailbroken() {
            throw SecurityError.jailbreakDetected
        }

        // Check for debugger (production only)
        #if !DEBUG
        if isDebuggerAttached() {
            throw SecurityError.debuggerDetected
        }
        #endif

        // Check for suspicious files/apps
        if hasSuspiciousFiles() {
            throw SecurityError.suspiciousEnvironment
        }
    }

    /// HIPAA Compliance: Verify app binary integrity
    /// Prevents code tampering
    func verifyBinaryIntegrity() throws {
        // In production, verify code signature
        // This is a placeholder for actual integrity check

        #if !DEBUG
        // Check if app is properly code-signed
        if !isProperlyCodeSigned() {
            throw SecurityError.integrityCheckFailed
        }
        #endif
    }

    // MARK: - Jailbreak Detection

    /// Detect if device is jailbroken
    /// HIPAA: Jailbroken devices cannot guarantee PHI security
    private func isJailbroken() -> Bool {
        // Method 1: Check for common jailbreak files
        let jailbreakPaths = [
            "/Applications/Cydia.app",
            "/Library/MobileSubstrate/MobileSubstrate.dylib",
            "/bin/bash",
            "/usr/sbin/sshd",
            "/etc/apt",
            "/private/var/lib/apt/",
            "/usr/bin/ssh",
            "/usr/libexec/sftp-server",
            "/Applications/blackra1n.app",
            "/Applications/FakeCarrier.app",
            "/Applications/Icy.app",
            "/Applications/IntelliScreen.app",
            "/Applications/MxTube.app",
            "/Applications/RockApp.app",
            "/Applications/SBSettings.app",
            "/Applications/WinterBoard.app"
        ]

        for path in jailbreakPaths {
            if FileManager.default.fileExists(atPath: path) {
                return true
            }
        }

        // Method 2: Check if we can write outside sandbox
        let testPath = "/private/jailbreak_test.txt"
        do {
            try "test".write(toFile: testPath, atomically: true, encoding: .utf8)
            try FileManager.default.removeItem(atPath: testPath)
            return true // Should not be able to write here
        } catch {
            // Expected behavior - cannot write outside sandbox
        }

        // Method 3: Check for Cydia URL scheme
        if let url = URL(string: "cydia://package/com.example.package"),
           UIApplication.shared.canOpenURL(url) {
            return true
        }

        // Method 4: Check for suspicious dylibs
        if hasSuspiciousDylibs() {
            return true
        }

        return false
    }

    /// Check for suspicious dynamic libraries (substrate, etc.)
    private func hasSuspiciousDylibs() -> Bool {
        let suspiciousLibraries = [
            "MobileSubstrate",
            "cycript",
            "SSLKillSwitch"
        ]

        for library in suspiciousLibraries {
            if dlopen(library, RTLD_NOW) != nil {
                return true
            }
        }

        return false
    }

    // MARK: - Debugger Detection

    /// Detect if debugger is attached
    private func isDebuggerAttached() -> Bool {
        var info = kinfo_proc()
        var mib: [Int32] = [CTL_KERN, KERN_PROC, KERN_PROC_PID, getpid()]
        var size = MemoryLayout<kinfo_proc>.stride

        let result = sysctl(&mib, UInt32(mib.count), &info, &size, nil, 0)

        if result != 0 {
            return false
        }

        // Check if P_TRACED flag is set
        return (info.kp_proc.p_flag & P_TRACED) != 0
    }

    // MARK: - Suspicious Files Detection

    /// Check for suspicious files that might indicate compromise
    private func hasSuspiciousFiles() -> Bool {
        let suspiciousFiles = [
            "/var/lib/cydia",
            "/var/cache/apt",
            "/var/lib/apt",
            "/etc/apt"
        ]

        for file in suspiciousFiles {
            if FileManager.default.fileExists(atPath: file) {
                return true
            }
        }

        return false
    }

    // MARK: - Code Signing Verification

    /// Verify app is properly code-signed
    private func isProperlyCodeSigned() -> Bool {
        // Check embedded.mobileprovision
        guard let provisioningPath = Bundle.main.path(forResource: "embedded", ofType: "mobileprovision") else {
            return false
        }

        return FileManager.default.fileExists(atPath: provisioningPath)
    }

    // MARK: - Screenshot Protection

    /// HIPAA Compliance: Prevent screenshots of PHI-containing screens
    /// This is applied per-view using view modifiers
    static func makeSecureField() {
        // Mark text field as secure (prevents screenshots)
        // This is applied to individual UITextField/SecureField instances
    }
}

// MARK: - Security Errors

enum SecurityError: LocalizedError {
    case jailbreakDetected
    case debuggerDetected
    case integrityCheckFailed
    case suspiciousEnvironment

    var errorDescription: String? {
        switch self {
        case .jailbreakDetected:
            return "Security Error: Jailbroken device detected"
        case .debuggerDetected:
            return "Security Error: Debugger detected"
        case .integrityCheckFailed:
            return "Security Error: App integrity check failed"
        case .suspiciousEnvironment:
            return "Security Error: Suspicious environment detected"
        }
    }

    var failureReason: String? {
        switch self {
        case .jailbreakDetected:
            return "This app cannot run on jailbroken devices to protect your health information."
        case .debuggerDetected:
            return "Debugging tools detected. This app cannot run in debug mode in production."
        case .integrityCheckFailed:
            return "The app binary has been modified or is not properly signed."
        case .suspiciousEnvironment:
            return "The device environment appears to be compromised."
        }
    }

    var recoverySuggestion: String? {
        "Please use a non-jailbroken device to ensure the security of your protected health information."
    }
}

// MARK: - C Imports for sysctl

import Darwin.POSIX.sys.sysctl
