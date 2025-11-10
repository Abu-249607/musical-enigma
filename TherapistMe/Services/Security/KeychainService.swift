//
//  KeychainService.swift
//  Therapist.Me
//
//  HIPAA Compliance: Secure storage for sensitive data using iOS Keychain
//

import Foundation
import Security

class KeychainService {
    static let shared = KeychainService()

    private init() {}

    // MARK: - Save Data

    /// HIPAA Compliance: Save data securely in Keychain
    /// - Parameters:
    ///   - data: Data to store
    ///   - key: Unique identifier
    ///   - accessibility: When data should be accessible
    /// - Returns: Success status
    @discardableResult
    func save(_ data: Data, for key: String, accessibility: CFString = kSecAttrAccessibleWhenUnlockedThisDeviceOnly) -> Bool {
        // Delete existing item first
        delete(key)

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: accessibility
        ]

        let status = SecItemAdd(query as CFDictionary, nil)

        if status == errSecSuccess {
            AuditLogger.shared.log(
                event: .keychainItemSaved,
                details: "Item saved to Keychain: \(key)",
                severity: .low
            )
            return true
        } else {
            AuditLogger.shared.log(
                event: .keychainError,
                details: "Failed to save to Keychain: \(key), status: \(status)",
                severity: .high
            )
            return false
        }
    }

    /// Save string to Keychain
    @discardableResult
    func save(_ string: String, for key: String, accessibility: CFString = kSecAttrAccessibleWhenUnlockedThisDeviceOnly) -> Bool {
        guard let data = string.data(using: .utf8) else {
            return false
        }
        return save(data, for: key, accessibility: accessibility)
    }

    // MARK: - Retrieve Data

    /// HIPAA Compliance: Retrieve data from Keychain
    func getData(for key: String) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess,
              let data = result as? Data else {
            if status != errSecItemNotFound {
                AuditLogger.shared.log(
                    event: .keychainError,
                    details: "Failed to retrieve from Keychain: \(key), status: \(status)",
                    severity: .medium
                )
            }
            return nil
        }

        AuditLogger.shared.log(
            event: .keychainItemRetrieved,
            details: "Item retrieved from Keychain: \(key)",
            severity: .low
        )

        return data
    }

    /// Retrieve string from Keychain
    func getString(for key: String) -> String? {
        guard let data = getData(for: key),
              let string = String(data: data, encoding: .utf8) else {
            return nil
        }
        return string
    }

    // MARK: - Delete Data

    /// Delete item from Keychain
    @discardableResult
    func delete(_ key: String) -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]

        let status = SecItemDelete(query as CFDictionary)

        if status == errSecSuccess || status == errSecItemNotFound {
            if status == errSecSuccess {
                AuditLogger.shared.log(
                    event: .keychainItemDeleted,
                    details: "Item deleted from Keychain: \(key)",
                    severity: .low
                )
            }
            return true
        } else {
            AuditLogger.shared.log(
                event: .keychainError,
                details: "Failed to delete from Keychain: \(key), status: \(status)",
                severity: .medium
            )
            return false
        }
    }

    /// HIPAA Compliance: Clear all app-related Keychain items
    func deleteAll() -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword
        ]

        let status = SecItemDelete(query as CFDictionary)

        if status == errSecSuccess || status == errSecItemNotFound {
            AuditLogger.shared.log(
                event: .keychainCleared,
                details: "All Keychain items cleared",
                severity: .medium
            )
            return true
        } else {
            return false
        }
    }
}

// MARK: - Keychain Keys
extension KeychainService {
    enum Keys {
        static let userCredentials = "com.therapistme.user.credentials"
        static let encryptionKey = "com.therapistme.encryption.key"
        static let biometricAuthEnabled = "com.therapistme.biometric.enabled"
        static let sessionToken = "com.therapistme.session.token"
        static let emergencyAccessCode = "com.therapistme.emergency.code"
    }
}
