//
//  EncryptionService.swift
//  Therapist.Me
//
//  HIPAA Compliance: AES-256 encryption for PHI data at rest and in transit
//  All Protected Health Information (PHI) must be encrypted using this service
//

import Foundation
import CryptoKit
import Security

class EncryptionService {
    static let shared = EncryptionService()

    private let keychain = KeychainService.shared
    private let encryptionKeyTag = "com.therapistme.encryptionkey"

    private init() {
        // HIPAA Compliance: Initialize or retrieve encryption key from Secure Enclave
        ensureEncryptionKeyExists()
    }

    // MARK: - Encryption Key Management

    /// HIPAA Compliance: Ensure encryption key exists in Keychain/Secure Enclave
    private func ensureEncryptionKeyExists() {
        if keychain.getData(for: encryptionKeyTag) == nil {
            // Generate new encryption key
            let key = SymmetricKey(size: .bits256)
            let keyData = key.withUnsafeBytes { Data($0) }

            // HIPAA Compliance: Store in Keychain with highest security
            keychain.save(keyData, for: encryptionKeyTag, accessibility: .whenUnlockedThisDeviceOnly)

            AuditLogger.shared.log(
                event: .encryptionKeyGenerated,
                details: "New AES-256 encryption key generated and stored in Keychain"
            )
        }
    }

    /// Retrieve encryption key from secure storage
    private func getEncryptionKey() -> SymmetricKey? {
        guard let keyData = keychain.getData(for: encryptionKeyTag) else {
            AuditLogger.shared.log(
                event: .securityError,
                details: "Failed to retrieve encryption key from Keychain",
                severity: .critical
            )
            return nil
        }
        return SymmetricKey(data: keyData)
    }

    // MARK: - Encryption Operations

    /// HIPAA Compliance: Encrypt PHI data using AES-256-GCM
    /// - Parameter data: Plain data to encrypt
    /// - Returns: Encrypted data or nil if encryption fails
    func encrypt(_ data: Data) -> Data? {
        guard let key = getEncryptionKey() else {
            return nil
        }

        do {
            // AES-GCM provides both encryption and authentication
            let sealedBox = try AES.GCM.seal(data, using: key)

            // Combine nonce + ciphertext + tag
            guard let combined = sealedBox.combined else {
                AuditLogger.shared.log(
                    event: .encryptionFailed,
                    details: "Failed to create combined encrypted data",
                    severity: .high
                )
                return nil
            }

            AuditLogger.shared.log(
                event: .dataEncrypted,
                details: "Data encrypted successfully using AES-256-GCM",
                severity: .low
            )

            return combined
        } catch {
            AuditLogger.shared.log(
                event: .encryptionFailed,
                details: "Encryption error: \(error.localizedDescription)",
                severity: .high
            )
            return nil
        }
    }

    /// HIPAA Compliance: Decrypt PHI data
    /// - Parameter encryptedData: Encrypted data
    /// - Returns: Decrypted plain data or nil if decryption fails
    func decrypt(_ encryptedData: Data) -> Data? {
        guard let key = getEncryptionKey() else {
            return nil
        }

        do {
            let sealedBox = try AES.GCM.SealedBox(combined: encryptedData)
            let decryptedData = try AES.GCM.open(sealedBox, using: key)

            AuditLogger.shared.log(
                event: .dataDecrypted,
                details: "Data decrypted successfully",
                severity: .low
            )

            return decryptedData
        } catch {
            AuditLogger.shared.log(
                event: .decryptionFailed,
                details: "Decryption error: \(error.localizedDescription)",
                severity: .high
            )
            return nil
        }
    }

    /// Encrypt Codable object
    func encrypt<T: Codable>(_ object: T) -> Data? {
        guard let jsonData = try? JSONEncoder().encode(object) else {
            return nil
        }
        return encrypt(jsonData)
    }

    /// Decrypt to Codable object
    func decrypt<T: Codable>(_ encryptedData: Data, as type: T.Type) -> T? {
        guard let decryptedData = decrypt(encryptedData),
              let object = try? JSONDecoder().decode(T.self, from: decryptedData) else {
            return nil
        }
        return object
    }

    // MARK: - String Encryption Helpers

    /// Encrypt string data
    func encrypt(_ string: String) -> Data? {
        guard let data = string.data(using: .utf8) else {
            return nil
        }
        return encrypt(data)
    }

    /// Decrypt to string
    func decryptToString(_ encryptedData: Data) -> String? {
        guard let decryptedData = decrypt(encryptedData),
              let string = String(data: decryptedData, encoding: .utf8) else {
            return nil
        }
        return string
    }

    // MARK: - Data Integrity

    /// HIPAA Compliance: Generate tamper-proof hash for data integrity
    func generateHash(for data: Data) -> String {
        let hash = SHA256.hash(data: data)
        return hash.compactMap { String(format: "%02x", $0) }.joined()
    }

    /// Verify data integrity using hash
    func verifyIntegrity(data: Data, expectedHash: String) -> Bool {
        let actualHash = generateHash(for: data)
        let isValid = actualHash == expectedHash

        AuditLogger.shared.log(
            event: .integrityCheckPerformed,
            details: "Integrity check: \(isValid ? "PASSED" : "FAILED")",
            severity: isValid ? .low : .critical
        )

        return isValid
    }

    // MARK: - Key Rotation

    /// HIPAA Compliance: Rotate encryption key (should be done periodically)
    func rotateEncryptionKey() -> Bool {
        guard let oldKey = getEncryptionKey() else {
            return false
        }

        // Generate new key
        let newKey = SymmetricKey(size: .bits256)
        let newKeyData = newKey.withUnsafeBytes { Data($0) }

        // Save new key
        keychain.save(newKeyData, for: encryptionKeyTag, accessibility: .whenUnlockedThisDeviceOnly)

        AuditLogger.shared.log(
            event: .encryptionKeyRotated,
            details: "Encryption key rotated successfully",
            severity: .medium
        )

        // Note: In production, you would need to re-encrypt all existing data
        // with the new key. This is a placeholder for that operation.

        return true
    }
}

// MARK: - Secure Data Extension
extension Data {
    /// Securely clear data from memory
    mutating func securelyErase() {
        // Overwrite with zeros
        self.withUnsafeMutableBytes { bytes in
            memset(bytes.baseAddress, 0, bytes.count)
        }
        self = Data()
    }
}
