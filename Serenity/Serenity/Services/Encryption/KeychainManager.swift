import Foundation
import Security
import CryptoKit
import LocalAuthentication

// HIPAA Compliance: Secure key storage using iOS Keychain
// Implements hardware-backed encryption key storage with Secure Enclave
// Implements §164.312(a)(2)(iv) - Encryption and Decryption

/// Manages secure storage of encryption keys in iOS Keychain
class KeychainManager {
    static let shared = KeychainManager()

    private init() {}

    // MARK: - Key Storage

    /// HIPAA Compliance: Store encryption key in hardware-backed keychain
    /// - Parameters:
    ///   - key: Symmetric encryption key
    ///   - identifier: Unique identifier for the key
    ///   - requiresBiometric: Whether biometric authentication is required to access
    /// - Throws: KeychainError if storage fails
    func storeKey(
        _ key: SymmetricKey,
        identifier: String,
        requiresBiometric: Bool = true
    ) throws {
        // Delete existing key if present
        try? deleteKey(identifier: identifier)

        // Create access control
        // HIPAA: Require biometric or device passcode for key access
        let accessControl = try createAccessControl(requiresBiometric: requiresBiometric)

        // Prepare keychain query
        let query: [String: Any] = [
            kSecClass as String: kSecClassKey,
            kSecAttrApplicationTag as String: identifier.data(using: .utf8)!,
            kSecValueData as String: key.withUnsafeBytes { Data($0) },

            // HIPAA Security: Key only accessible when device is unlocked
            // Not available in backups (prevents key extraction)
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly,

            // Require biometric/passcode authentication
            kSecAttrAccessControl as String: accessControl,

            // Use Secure Enclave when available
            kSecAttrTokenID as String: kSecAttrTokenIDSecureEnclave as Any
        ]

        // Store in keychain
        let status = SecItemAdd(query as CFDictionary, nil)

        if status == errSecDuplicateItem {
            // Update existing item
            let updateQuery: [String: Any] = [
                kSecClass as String: kSecClassKey,
                kSecAttrApplicationTag as String: identifier.data(using: .utf8)!
            ]

            let updateAttributes: [String: Any] = [
                kSecValueData as String: key.withUnsafeBytes { Data($0) }
            ]

            let updateStatus = SecItemUpdate(
                updateQuery as CFDictionary,
                updateAttributes as CFDictionary
            )

            guard updateStatus == errSecSuccess else {
                throw KeychainError.storageFailure(updateStatus)
            }
        } else if status != errSecSuccess {
            throw KeychainError.storageFailure(status)
        }

        // HIPAA Audit: Log key storage (not the key itself)
        AuditLogger.shared.log(.keychainKeyStored, metadata: [
            "identifier": identifier,
            "requiresBiometric": requiresBiometric
        ])
    }

    /// HIPAA Compliance: Retrieve encryption key from keychain
    /// - Parameter identifier: Key identifier
    /// - Returns: Symmetric encryption key
    /// - Throws: KeychainError if retrieval fails
    func retrieveKey(identifier: String) throws -> SymmetricKey {
        let query: [String: Any] = [
            kSecClass as String: kSecClassKey,
            kSecAttrApplicationTag as String: identifier.data(using: .utf8)!,
            kSecReturnData as String: true,

            // Prompt for biometric if required
            kSecUseOperationPrompt as String: "Authenticate to access your health data"
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess,
              let keyData = result as? Data else {
            throw KeychainError.retrievalFailure(status)
        }

        // Reconstruct symmetric key
        let key = SymmetricKey(data: keyData)

        return key
    }

    /// Delete encryption key from keychain
    func deleteKey(identifier: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassKey,
            kSecAttrApplicationTag as String: identifier.data(using: .utf8)!
        ]

        let status = SecItemDelete(query as CFDictionary)

        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.deletionFailure(status)
        }

        // HIPAA Audit: Log key deletion
        AuditLogger.shared.log(.keychainKeyDeleted, metadata: [
            "identifier": identifier
        ])
    }

    // MARK: - Generic Secure Storage

    /// Store generic data in keychain (e.g., passwords, tokens)
    func storeData(
        _ data: Data,
        identifier: String,
        requiresBiometric: Bool = false
    ) throws {
        try? deleteData(identifier: identifier)

        var query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: identifier,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]

        if requiresBiometric {
            let accessControl = try createAccessControl(requiresBiometric: true)
            query[kSecAttrAccessControl as String] = accessControl
        }

        let status = SecItemAdd(query as CFDictionary, nil)

        guard status == errSecSuccess else {
            throw KeychainError.storageFailure(status)
        }
    }

    /// Retrieve generic data from keychain
    func retrieveData(identifier: String) throws -> Data {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: identifier,
            kSecReturnData as String: true,
            kSecUseOperationPrompt as String: "Authenticate to access your data"
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess,
              let data = result as? Data else {
            throw KeychainError.retrievalFailure(status)
        }

        return data
    }

    /// Delete generic data from keychain
    func deleteData(identifier: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: identifier
        ]

        let status = SecItemDelete(query as CFDictionary)

        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.deletionFailure(status)
        }
    }

    // MARK: - Access Control

    /// Create access control for keychain items
    /// HIPAA: Require biometric or device passcode
    private func createAccessControl(requiresBiometric: Bool) throws -> SecAccessControl {
        var error: Unmanaged<CFError>?

        let flags: SecAccessControlCreateFlags = requiresBiometric
            ? [.userPresence, .privateKeyUsage]  // Require biometric or passcode
            : []

        guard let accessControl = SecAccessControlCreateWithFlags(
            kCFAllocatorDefault,
            kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
            flags,
            &error
        ) else {
            if let error = error?.takeRetainedValue() {
                throw KeychainError.accessControlFailure(error as Error)
            }
            throw KeychainError.accessControlFailure(nil)
        }

        return accessControl
    }

    // MARK: - Keychain Cleanup

    /// HIPAA Compliance: Securely delete all app data from keychain
    /// Used during account deletion
    func deleteAllData() throws {
        // Delete all keys
        let keyQuery: [String: Any] = [
            kSecClass as String: kSecClassKey
        ]
        SecItemDelete(keyQuery as CFDictionary)

        // Delete all generic passwords
        let passwordQuery: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword
        ]
        SecItemDelete(passwordQuery as CFDictionary)

        // HIPAA Audit: Log keychain cleanup
        AuditLogger.shared.log(.keychainCleared, metadata: [:])
    }
}

// MARK: - Keychain Errors

enum KeychainError: LocalizedError {
    case storageFailure(OSStatus)
    case retrievalFailure(OSStatus)
    case deletionFailure(OSStatus)
    case accessControlFailure(Error?)

    var errorDescription: String? {
        switch self {
        case .storageFailure(let status):
            return "Failed to store data in keychain (status: \(status))"
        case .retrievalFailure(let status):
            return "Failed to retrieve data from keychain (status: \(status))"
        case .deletionFailure(let status):
            return "Failed to delete data from keychain (status: \(status))"
        case .accessControlFailure(let error):
            return "Failed to create access control: \(error?.localizedDescription ?? "Unknown error")"
        }
    }

    var recoverySuggestion: String? {
        "Please ensure your device is unlocked and biometric authentication is available."
    }
}

// MARK: - Audit Events

extension AuditEvent {
    static let keychainKeyStored = AuditEvent(type: "KEYCHAIN_KEY_STORED")
    static let keychainKeyDeleted = AuditEvent(type: "KEYCHAIN_KEY_DELETED")
    static let keychainCleared = AuditEvent(type: "KEYCHAIN_CLEARED")
}
