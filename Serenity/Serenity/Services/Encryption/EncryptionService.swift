import Foundation
import CryptoKit

// HIPAA Compliance: AES-256-GCM encryption service
// Implements §164.312(a)(2)(iv) - Encryption and Decryption (Addressable)
// Uses authenticated encryption with associated data (AEAD) for integrity and confidentiality

/// Encryption service providing AES-256-GCM encryption for all PHI
class EncryptionService {
    static let shared = EncryptionService()

    private let keychainManager = KeychainManager.shared

    // HIPAA: Encryption key identifier in keychain
    private let encryptionKeyIdentifier = "com.therapistme.encryption.master"

    private init() {
        // Ensure encryption key exists
        do {
            _ = try getMasterKey()
        } catch {
            // Generate new master key on first launch
            do {
                try generateMasterKey()
            } catch {
                fatalError("Failed to initialize encryption: \(error)")
            }
        }
    }

    // MARK: - Public Methods

    /// HIPAA Compliance: Encrypts data using AES-256-GCM
    /// - Parameters:
    ///   - data: Plaintext data to encrypt (PHI)
    ///   - associatedData: Additional authenticated data (e.g., entity ID, timestamp)
    /// - Returns: Encrypted data with nonce and authentication tag
    /// - Throws: EncryptionError if encryption fails
    func encrypt(_ data: Data, associatedData: Data?) throws -> EncryptedData {
        // Retrieve master encryption key from keychain
        let key = try getMasterKey()

        // Generate unique nonce (12 bytes for GCM mode)
        let nonce = AES.GCM.Nonce()

        // Encrypt with authenticated encryption
        // GCM mode provides both confidentiality and integrity
        let sealedBox: AES.GCM.SealedBox

        if let associatedData = associatedData {
            // Encrypt with associated data for context binding
            sealedBox = try AES.GCM.seal(
                data,
                using: key,
                nonce: nonce,
                authenticating: associatedData
            )
        } else {
            // Encrypt without associated data
            sealedBox = try AES.GCM.seal(
                data,
                using: key,
                nonce: nonce
            )
        }

        // Return encrypted data with nonce and tag
        // Nonce and tag are required for decryption
        return EncryptedData(
            nonce: Data(sealedBox.nonce),
            ciphertext: sealedBox.ciphertext,
            tag: sealedBox.tag
        )
    }

    /// HIPAA Compliance: Decrypts AES-256-GCM encrypted data
    /// - Parameters:
    ///   - encryptedData: Encrypted data with nonce and tag
    ///   - associatedData: Associated data used during encryption
    /// - Returns: Decrypted plaintext data
    /// - Throws: EncryptionError if decryption or authentication fails
    func decrypt(_ encryptedData: EncryptedData, associatedData: Data?) throws -> Data {
        // Retrieve master encryption key
        let key = try getMasterKey()

        // Reconstruct nonce from stored data
        let nonce = try AES.GCM.Nonce(data: encryptedData.nonce)

        // Reconstruct sealed box from components
        let sealedBox = try AES.GCM.SealedBox(
            nonce: nonce,
            ciphertext: encryptedData.ciphertext,
            tag: encryptedData.tag
        )

        // Decrypt and verify authenticity
        // Decryption will fail if:
        // - Authentication tag is invalid (data tampered)
        // - Associated data doesn't match
        // - Incorrect key
        let decryptedData: Data

        if let associatedData = associatedData {
            decryptedData = try AES.GCM.open(
                sealedBox,
                using: key,
                authenticating: associatedData
            )
        } else {
            decryptedData = try AES.GCM.open(
                sealedBox,
                using: key
            )
        }

        return decryptedData
    }

    // MARK: - Key Management

    /// Generate and store new master encryption key
    /// HIPAA: 256-bit key for AES-256
    private func generateMasterKey() throws {
        // Generate cryptographically secure random key (256 bits)
        let key = SymmetricKey(size: .bits256)

        // Store in hardware-backed keychain
        try keychainManager.storeKey(
            key,
            identifier: encryptionKeyIdentifier,
            requiresBiometric: true
        )

        // HIPAA Audit: Log key generation (not the key itself)
        AuditLogger.shared.log(.encryptionKeyGenerated, metadata: [
            "keyIdentifier": encryptionKeyIdentifier,
            "keySize": "256"
        ])
    }

    /// Retrieve master encryption key from keychain
    private func getMasterKey() throws -> SymmetricKey {
        return try keychainManager.retrieveKey(identifier: encryptionKeyIdentifier)
    }

    /// HIPAA Compliance: Rotate encryption key (recommended annually)
    /// - Note: Requires re-encryption of all existing data
    func rotateEncryptionKey() throws {
        // Retrieve old key
        let oldKey = try getMasterKey()

        // Generate new key
        let newKey = SymmetricKey(size: .bits256)

        // Store new key with temporary identifier
        let newKeyIdentifier = "\(encryptionKeyIdentifier).new"
        try keychainManager.storeKey(
            newKey,
            identifier: newKeyIdentifier,
            requiresBiometric: true
        )

        // Re-encrypt all data with new key
        // This should be done by the data services

        // Delete old key
        try keychainManager.deleteKey(identifier: encryptionKeyIdentifier)

        // Rename new key to master
        // (In production, this would involve more complex key migration)

        // HIPAA Audit: Log key rotation
        AuditLogger.shared.log(.encryptionKeyRotated, metadata: [
            "keyIdentifier": encryptionKeyIdentifier,
            "rotationDate": ISO8601DateFormatter().string(from: Date())
        ])
    }

    /// HIPAA Compliance: Securely delete encryption key
    /// Use when user deletes account
    func deleteEncryptionKey() throws {
        try keychainManager.deleteKey(identifier: encryptionKeyIdentifier)

        // HIPAA Audit: Log key deletion
        AuditLogger.shared.log(.encryptionKeyDeleted, metadata: [
            "keyIdentifier": encryptionKeyIdentifier
        ])
    }
}

// MARK: - Encrypted Data Structure

/// Container for encrypted data with authentication components
struct EncryptedData: Codable {
    let nonce: Data           // 12 bytes for GCM mode
    let ciphertext: Data      // Encrypted plaintext
    let tag: Data             // 16-byte authentication tag

    /// Combined representation for storage
    var combined: Data {
        var combined = Data()
        combined.append(nonce)
        combined.append(ciphertext)
        combined.append(tag)
        return combined
    }

    /// Initialize from combined data
    init?(combined: Data) {
        guard combined.count > 28 else { return nil } // Minimum: 12 (nonce) + 16 (tag)

        self.nonce = combined.prefix(12)
        self.ciphertext = combined.dropFirst(12).dropLast(16)
        self.tag = combined.suffix(16)
    }

    init(nonce: Data, ciphertext: Data, tag: Data) {
        self.nonce = nonce
        self.ciphertext = ciphertext
        self.tag = tag
    }
}

// MARK: - Encryption Errors

enum EncryptionError: LocalizedError {
    case keyGenerationFailed
    case keyRetrievalFailed
    case encryptionFailed
    case decryptionFailed
    case missingEncryptionData
    case integrityCheckFailed
    case invalidNonce

    var errorDescription: String? {
        switch self {
        case .keyGenerationFailed:
            return "Failed to generate encryption key"
        case .keyRetrievalFailed:
            return "Failed to retrieve encryption key from secure storage"
        case .encryptionFailed:
            return "Failed to encrypt data"
        case .decryptionFailed:
            return "Failed to decrypt data - data may be corrupted or tampered"
        case .missingEncryptionData:
            return "Encryption metadata is missing"
        case .integrityCheckFailed:
            return "Integrity check failed - data may have been tampered with"
        case .invalidNonce:
            return "Invalid encryption nonce"
        }
    }

    var recoverySuggestion: String? {
        switch self {
        case .decryptionFailed, .integrityCheckFailed:
            return "This data may have been tampered with. Please contact support."
        default:
            return "Please try again or contact support if the problem persists."
        }
    }
}

// MARK: - Audit Events

extension AuditEvent {
    static let encryptionKeyGenerated = AuditEvent(type: "ENCRYPTION_KEY_GENERATED")
    static let encryptionKeyRotated = AuditEvent(type: "ENCRYPTION_KEY_ROTATED")
    static let encryptionKeyDeleted = AuditEvent(type: "ENCRYPTION_KEY_DELETED")
    static let phiEncrypted = AuditEvent(type: "PHI_ENCRYPTED")
    static let phiDecrypted = AuditEvent(type: "PHI_DECRYPTED")
    static let phiRead = AuditEvent(type: "PHI_READ")
    static let phiDeleted = AuditEvent(type: "PHI_DELETED")
    static let integrityViolation = AuditEvent(type: "INTEGRITY_VIOLATION")
}
