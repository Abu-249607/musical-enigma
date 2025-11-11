import Foundation
import CryptoKit

// HIPAA Compliance: Data integrity validation using SHA-256 checksums
// Implements §164.312(c)(1) - Integrity Controls

/// Validates data integrity using cryptographic checksums
class IntegrityValidator {
    static let shared = IntegrityValidator()

    private init() {}

    // MARK: - Checksum Generation

    /// HIPAA Compliance: Generate SHA-256 checksum for data integrity
    /// - Parameter data: Data to generate checksum for
    /// - Returns: Hex-encoded SHA-256 hash
    func generateChecksum(for data: Data) throws -> String {
        let hash = SHA256.hash(data: data)
        return hash.compactMap { String(format: "%02x", $0) }.joined()
    }

    /// Generate checksum from string
    func generateChecksum(for string: String) throws -> String {
        guard let data = string.data(using: .utf8) else {
            throw IntegrityError.invalidInput
        }
        return try generateChecksum(for: data)
    }

    // MARK: - Checksum Verification

    /// HIPAA Compliance: Verify data integrity using checksum
    /// - Parameters:
    ///   - checksum: Expected checksum (hex-encoded)
    ///   - data: Data to verify
    /// - Returns: True if checksum matches, false otherwise
    func verifyChecksum(_ checksum: String, for data: Data) throws -> Bool {
        let actualChecksum = try generateChecksum(for: data)
        return checksum == actualChecksum
    }

    /// Verify checksum for string
    func verifyChecksum(_ checksum: String, for string: String) throws -> Bool {
        guard let data = string.data(using: .utf8) else {
            throw IntegrityError.invalidInput
        }
        return try verifyChecksum(checksum, for: data)
    }

    // MARK: - Digital Signatures

    /// Generate digital signature for data
    /// Used for audit log signatures
    func sign(data: Data, using privateKey: P256.Signing.PrivateKey) throws -> Data {
        let signature = try privateKey.signature(for: data)
        return signature.rawRepresentation
    }

    /// Verify digital signature
    func verify(
        signature: Data,
        for data: Data,
        using publicKey: P256.Signing.PublicKey
    ) throws -> Bool {
        let signatureObj = try P256.Signing.ECDSASignature(rawRepresentation: signature)
        return publicKey.isValidSignature(signatureObj, for: data)
    }
}

// MARK: - Integrity Errors

enum IntegrityError: LocalizedError {
    case invalidInput
    case checksumMismatch
    case signatureInvalid

    var errorDescription: String? {
        switch self {
        case .invalidInput:
            return "Invalid input data"
        case .checksumMismatch:
            return "Data integrity check failed - checksum mismatch"
        case .signatureInvalid:
            return "Digital signature verification failed"
        }
    }

    var recoverySuggestion: String? {
        switch self {
        case .checksumMismatch:
            return "The data may have been tampered with. Please contact support."
        case .signatureInvalid:
            return "The signature is invalid. Please contact support."
        default:
            return "Please try again or contact support."
        }
    }
}
