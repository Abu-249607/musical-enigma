import Foundation

// HIPAA Compliance: Journal entry model with encryption
// All journal entries are PHI and must be encrypted at rest (§164.312(a)(2)(iv))
// Implements audit logging for all PHI access (§164.312(b))

struct JournalEntry: Identifiable, Codable {
    // HIPAA: Unique identifier
    let id: UUID

    // Ownership (for access control)
    let userID: UUID

    // Journal content (ENCRYPTED - PHI)
    var title: String           // Encrypted before storage
    var content: String         // Encrypted before storage
    var mood: MoodType?

    // Metadata
    let createdAt: Date
    var updatedAt: Date
    var isDeleted: Bool = false  // Soft delete for audit trail
    var deletedAt: Date?

    // Encryption metadata
    var encryptedData: Data?     // AES-256-GCM encrypted content
    var encryptionNonce: Data?   // Unique nonce for GCM mode
    var encryptionTag: Data?     // Authentication tag for GCM mode

    // Integrity
    var checksum: String?        // SHA-256 checksum for integrity verification

    // Versioning (HIPAA audit requirement)
    var version: Int = 1
    var previousVersionID: UUID?

    init(
        id: UUID = UUID(),
        userID: UUID,
        title: String,
        content: String,
        mood: MoodType? = nil
    ) {
        self.id = id
        self.userID = userID
        self.title = title
        self.content = content
        self.mood = mood
        self.createdAt = Date()
        self.updatedAt = Date()
    }

    // MARK: - Encryption Helpers

    /// HIPAA Compliance: Prepare entry for encryption before storage
    mutating func encrypt(using encryptionService: EncryptionService) throws {
        // Combine title and content into JSON
        let plaintext = JournalPlaintext(title: title, content: content)
        let plaintextData = try JSONEncoder().encode(plaintext)

        // Associated data for authenticated encryption (entity ID + timestamp)
        let associatedData = "\(id.uuidString):\(createdAt.timeIntervalSince1970)"
            .data(using: .utf8)!

        // Encrypt using AES-256-GCM
        let encrypted = try encryptionService.encrypt(
            plaintextData,
            associatedData: associatedData
        )

        self.encryptedData = encrypted.ciphertext
        self.encryptionNonce = encrypted.nonce
        self.encryptionTag = encrypted.tag

        // Generate SHA-256 checksum for integrity
        self.checksum = try IntegrityValidator.shared.generateChecksum(for: encrypted.ciphertext)

        // Clear plaintext from memory (security best practice)
        self.title = ""
        self.content = ""

        // HIPAA Audit: Log encryption event
        AuditLogger.shared.log(.phiEncrypted, metadata: [
            "entityType": "JournalEntry",
            "entityID": id.uuidString,
            "userID": userID.uuidString
        ])
    }

    /// HIPAA Compliance: Decrypt entry after retrieval from storage
    mutating func decrypt(using encryptionService: EncryptionService) throws {
        guard let encryptedData = encryptedData,
              let nonce = encryptionNonce,
              let tag = encryptionTag else {
            throw EncryptionError.missingEncryptionData
        }

        // Verify integrity before decryption
        if let checksum = checksum {
            let isValid = try IntegrityValidator.shared.verifyChecksum(
                checksum,
                for: encryptedData
            )
            if !isValid {
                // HIPAA Security: Integrity violation detected
                AuditLogger.shared.log(.integrityViolation, metadata: [
                    "entityType": "JournalEntry",
                    "entityID": id.uuidString
                ])
                throw EncryptionError.integrityCheckFailed
            }
        }

        // Associated data must match encryption
        let associatedData = "\(id.uuidString):\(createdAt.timeIntervalSince1970)"
            .data(using: .utf8)!

        // Decrypt
        let encrypted = EncryptedData(
            nonce: nonce,
            ciphertext: encryptedData,
            tag: tag
        )

        let plaintextData = try encryptionService.decrypt(
            encrypted,
            associatedData: associatedData
        )

        // Decode plaintext
        let plaintext = try JSONDecoder().decode(JournalPlaintext.self, from: plaintextData)
        self.title = plaintext.title
        self.content = plaintext.content

        // HIPAA Audit: Log PHI access (read)
        AuditLogger.shared.log(.phiRead, metadata: [
            "entityType": "JournalEntry",
            "entityID": id.uuidString,
            "userID": userID.uuidString
        ])
    }

    // MARK: - Soft Delete (HIPAA audit trail requirement)

    mutating func markAsDeleted() {
        self.isDeleted = true
        self.deletedAt = Date()

        // HIPAA Audit: Log PHI deletion
        AuditLogger.shared.log(.phiDeleted, metadata: [
            "entityType": "JournalEntry",
            "entityID": id.uuidString,
            "userID": userID.uuidString
        ])
    }
}

// MARK: - Journal Plaintext (for encryption)

private struct JournalPlaintext: Codable {
    let title: String
    let content: String
}

// MARK: - Mood Type

enum MoodType: String, Codable, CaseIterable {
    case veryHappy = "Very Happy"
    case happy = "Happy"
    case neutral = "Neutral"
    case sad = "Sad"
    case verySad = "Very Sad"
    case anxious = "Anxious"
    case stressed = "Stressed"
    case calm = "Calm"
    case energetic = "Energetic"
    case tired = "Tired"

    var emoji: String {
        switch self {
        case .veryHappy: return "😄"
        case .happy: return "🙂"
        case .neutral: return "😐"
        case .sad: return "😔"
        case .verySad: return "😢"
        case .anxious: return "😰"
        case .stressed: return "😣"
        case .calm: return "😌"
        case .energetic: return "⚡"
        case .tired: return "😴"
        }
    }

    var color: String {
        switch self {
        case .veryHappy, .happy: return "green"
        case .neutral, .calm: return "blue"
        case .sad, .verySad, .anxious, .stressed: return "red"
        case .energetic: return "yellow"
        case .tired: return "gray"
        }
    }
}
