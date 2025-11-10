//
//  SecureStorageService.swift
//  Therapist.Me
//
//  HIPAA Compliance: Secure local storage for PHI data with encryption
//

import Foundation
import CoreData

class SecureStorageService {
    static let shared = SecureStorageService()

    private let encryptionService = EncryptionService.shared
    private let fileManager = FileManager.default
    private var secureStorageURL: URL?

    private init() {
        setupSecureStorage()
    }

    func initialize() {
        setupSecureStorage()
    }

    // MARK: - Setup

    private func setupSecureStorage() {
        guard let documentsPath = fileManager.urls(for: .documentDirectory, in: .userDomainMask).first else {
            AuditLogger.shared.log(
                event: .securityError,
                details: "Failed to access documents directory",
                severity: .critical
            )
            return
        }

        // HIPAA Compliance: Create secure storage directory with restricted access
        secureStorageURL = documentsPath.appendingPathComponent("SecureData", isDirectory: true)

        if let url = secureStorageURL, !fileManager.fileExists(atPath: url.path) {
            do {
                try fileManager.createDirectory(at: url, withIntermediateDirectories: true)

                // Set file protection
                try fileManager.setAttributes(
                    [.protectionKey: FileProtectionType.completeUntilFirstUserAuthentication],
                    ofItemAtPath: url.path
                )

                AuditLogger.shared.log(
                    event: .phiCreated,
                    details: "Secure storage directory created",
                    severity: .medium
                )
            } catch {
                AuditLogger.shared.log(
                    event: .securityError,
                    details: "Failed to create secure storage: \(error.localizedDescription)",
                    severity: .critical
                )
            }
        }
    }

    // MARK: - Save Operations

    /// HIPAA Compliance: Save encrypted PHI data
    func save<T: Codable>(_ object: T, withKey key: String, userId: String) -> Bool {
        guard let storageURL = secureStorageURL else {
            return false
        }

        do {
            // Encode object
            let encoder = JSONEncoder()
            encoder.dateEncodingStrategy = .iso8601
            let jsonData = try encoder.encode(object)

            // HIPAA Compliance: Encrypt data before writing
            guard let encryptedData = encryptionService.encrypt(jsonData) else {
                AuditLogger.shared.log(
                    event: .encryptionFailed,
                    details: "Failed to encrypt data for key: \(key)",
                    userId: userId,
                    severity: .critical
                )
                return false
            }

            // Generate integrity hash
            let hash = encryptionService.generateHash(for: encryptedData)

            // Write encrypted data
            let fileURL = storageURL.appendingPathComponent(key)
            try encryptedData.write(to: fileURL, options: .completeFileProtectionUntilFirstUserAuthentication)

            // Write hash for integrity verification
            let hashURL = storageURL.appendingPathComponent("\(key).hash")
            try hash.write(to: hashURL, atomically: true, encoding: .utf8)

            AuditLogger.shared.log(
                event: .phiCreated,
                details: "PHI data saved: \(key)",
                userId: userId,
                severity: .medium
            )

            return true
        } catch {
            AuditLogger.shared.log(
                event: .securityError,
                details: "Failed to save data: \(error.localizedDescription)",
                userId: userId,
                severity: .high
            )
            return false
        }
    }

    // MARK: - Retrieve Operations

    /// HIPAA Compliance: Retrieve and decrypt PHI data
    func retrieve<T: Codable>(_ type: T.Type, forKey key: String, userId: String) -> T? {
        guard let storageURL = secureStorageURL else {
            return nil
        }

        do {
            let fileURL = storageURL.appendingPathComponent(key)

            // Check if file exists
            guard fileManager.fileExists(atPath: fileURL.path) else {
                return nil
            }

            // Read encrypted data
            let encryptedData = try Data(contentsOf: fileURL)

            // HIPAA Compliance: Verify integrity before decryption
            let hashURL = storageURL.appendingPathComponent("\(key).hash")
            if let storedHash = try? String(contentsOf: hashURL) {
                if !encryptionService.verifyIntegrity(data: encryptedData, expectedHash: storedHash) {
                    AuditLogger.shared.log(
                        event: .integrityCheckFailed,
                        details: "Data integrity check failed for: \(key)",
                        userId: userId,
                        severity: .critical
                    )
                    return nil
                }
            }

            // Decrypt data
            guard let decryptedData = encryptionService.decrypt(encryptedData) else {
                AuditLogger.shared.log(
                    event: .decryptionFailed,
                    details: "Failed to decrypt data for key: \(key)",
                    userId: userId,
                    severity: .critical
                )
                return nil
            }

            // Decode object
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            let object = try decoder.decode(T.self, from: decryptedData)

            AuditLogger.shared.log(
                event: .phiAccessed,
                details: "PHI data accessed: \(key)",
                userId: userId,
                severity: .medium
            )

            return object
        } catch {
            AuditLogger.shared.log(
                event: .securityError,
                details: "Failed to retrieve data: \(error.localizedDescription)",
                userId: userId,
                severity: .high
            )
            return nil
        }
    }

    // MARK: - Update Operations

    /// HIPAA Compliance: Update existing PHI data
    func update<T: Codable>(_ object: T, forKey key: String, userId: String) -> Bool {
        // Save with same key (overwrites existing)
        let success = save(object, withKey: key, userId: userId)

        if success {
            AuditLogger.shared.log(
                event: .phiModified,
                details: "PHI data updated: \(key)",
                userId: userId,
                severity: .medium
            )
        }

        return success
    }

    // MARK: - Delete Operations

    /// HIPAA Compliance: Securely delete PHI data
    func delete(key: String, userId: String) -> Bool {
        guard let storageURL = secureStorageURL else {
            return false
        }

        do {
            let fileURL = storageURL.appendingPathComponent(key)
            let hashURL = storageURL.appendingPathComponent("\(key).hash")

            // HIPAA Compliance: Securely overwrite before deletion
            if fileManager.fileExists(atPath: fileURL.path) {
                // Overwrite with random data
                if let fileHandle = try? FileHandle(forWritingTo: fileURL) {
                    let randomData = Data((0..<1024).map { _ in UInt8.random(in: 0...255) })
                    fileHandle.write(randomData)
                    try? fileHandle.close()
                }

                // Delete file and hash
                try fileManager.removeItem(at: fileURL)
                try? fileManager.removeItem(at: hashURL)

                AuditLogger.shared.log(
                    event: .phiDeleted,
                    details: "PHI data deleted: \(key)",
                    userId: userId,
                    severity: .high
                )

                return true
            }

            return false
        } catch {
            AuditLogger.shared.log(
                event: .securityError,
                details: "Failed to delete data: \(error.localizedDescription)",
                userId: userId,
                severity: .high
            )
            return false
        }
    }

    /// HIPAA Compliance: Delete all user data (for account deletion)
    func deleteAllData(userId: String) -> Bool {
        guard let storageURL = secureStorageURL else {
            return false
        }

        do {
            // Get all files
            let files = try fileManager.contentsOfDirectory(at: storageURL, includingPropertiesForKeys: nil)

            // Delete each file securely
            for file in files {
                // Overwrite with random data first
                if let fileHandle = try? FileHandle(forWritingTo: file) {
                    let randomData = Data((0..<1024).map { _ in UInt8.random(in: 0...255) })
                    fileHandle.write(randomData)
                    try? fileHandle.close()
                }

                try fileManager.removeItem(at: file)
            }

            AuditLogger.shared.log(
                event: .phiDeleted,
                details: "All PHI data deleted for user",
                userId: userId,
                severity: .critical
            )

            return true
        } catch {
            AuditLogger.shared.log(
                event: .securityError,
                details: "Failed to delete all data: \(error.localizedDescription)",
                userId: userId,
                severity: .critical
            )
            return false
        }
    }

    // MARK: - Utility Methods

    /// Check if data exists for key
    func exists(key: String) -> Bool {
        guard let storageURL = secureStorageURL else {
            return false
        }

        let fileURL = storageURL.appendingPathComponent(key)
        return fileManager.fileExists(atPath: fileURL.path)
    }

    /// Get storage size
    func getStorageSize() -> Int64 {
        guard let storageURL = secureStorageURL else {
            return 0
        }

        var totalSize: Int64 = 0

        do {
            let files = try fileManager.contentsOfDirectory(at: storageURL, includingPropertiesForKeys: [.fileSizeKey])

            for file in files {
                let attributes = try fileManager.attributesOfItem(atPath: file.path)
                if let size = attributes[.size] as? Int64 {
                    totalSize += size
                }
            }
        } catch {
            print("Failed to calculate storage size: \(error.localizedDescription)")
        }

        return totalSize
    }
}
