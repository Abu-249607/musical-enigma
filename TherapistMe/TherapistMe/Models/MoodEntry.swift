import Foundation

// HIPAA Compliance: Mood tracking entry model with encryption
// Mood data is PHI and must be encrypted at rest (§164.312(a)(2)(iv))

struct MoodEntry: Identifiable, Codable {
    // HIPAA: Unique identifier
    let id: UUID

    // Ownership (for access control)
    let userID: UUID

    // Mood data (ENCRYPTED - PHI)
    var mood: MoodType
    var intensity: Int           // 1-10 scale
    var notes: String?          // Optional notes about the mood
    var triggers: [String]      // What triggered this mood

    // Context
    var location: String?       // Optional location (encrypted)
    var activities: [String]    // What was the user doing

    // Metadata
    let recordedAt: Date
    var createdAt: Date
    var isDeleted: Bool = false
    var deletedAt: Date?

    // Encryption metadata
    var encryptedData: Data?
    var encryptionNonce: Data?
    var encryptionTag: Data?
    var checksum: String?

    init(
        id: UUID = UUID(),
        userID: UUID,
        mood: MoodType,
        intensity: Int,
        notes: String? = nil,
        triggers: [String] = [],
        activities: [String] = [],
        recordedAt: Date = Date()
    ) {
        self.id = id
        self.userID = userID
        self.mood = mood
        self.intensity = min(max(intensity, 1), 10) // Clamp to 1-10
        self.notes = notes
        self.triggers = triggers
        self.activities = activities
        self.recordedAt = recordedAt
        self.createdAt = Date()
    }

    // MARK: - Encryption

    mutating func encrypt(using encryptionService: EncryptionService) throws {
        let plaintext = MoodPlaintext(
            mood: mood,
            intensity: intensity,
            notes: notes,
            triggers: triggers,
            location: location,
            activities: activities
        )
        let plaintextData = try JSONEncoder().encode(plaintext)

        let associatedData = "\(id.uuidString):\(recordedAt.timeIntervalSince1970)"
            .data(using: .utf8)!

        let encrypted = try encryptionService.encrypt(
            plaintextData,
            associatedData: associatedData
        )

        self.encryptedData = encrypted.ciphertext
        self.encryptionNonce = encrypted.nonce
        self.encryptionTag = encrypted.tag
        self.checksum = try IntegrityValidator.shared.generateChecksum(for: encrypted.ciphertext)

        // Clear plaintext
        self.notes = nil
        self.triggers = []
        self.activities = []

        AuditLogger.shared.log(.phiEncrypted, metadata: [
            "entityType": "MoodEntry",
            "entityID": id.uuidString,
            "userID": userID.uuidString
        ])
    }

    mutating func decrypt(using encryptionService: EncryptionService) throws {
        guard let encryptedData = encryptedData,
              let nonce = encryptionNonce,
              let tag = encryptionTag else {
            throw EncryptionError.missingEncryptionData
        }

        if let checksum = checksum {
            let isValid = try IntegrityValidator.shared.verifyChecksum(
                checksum,
                for: encryptedData
            )
            if !isValid {
                AuditLogger.shared.log(.integrityViolation, metadata: [
                    "entityType": "MoodEntry",
                    "entityID": id.uuidString
                ])
                throw EncryptionError.integrityCheckFailed
            }
        }

        let associatedData = "\(id.uuidString):\(recordedAt.timeIntervalSince1970)"
            .data(using: .utf8)!

        let encrypted = EncryptedData(
            nonce: nonce,
            ciphertext: encryptedData,
            tag: tag
        )

        let plaintextData = try encryptionService.decrypt(
            encrypted,
            associatedData: associatedData
        )

        let plaintext = try JSONDecoder().decode(MoodPlaintext.self, from: plaintextData)
        self.mood = plaintext.mood
        self.intensity = plaintext.intensity
        self.notes = plaintext.notes
        self.triggers = plaintext.triggers
        self.location = plaintext.location
        self.activities = plaintext.activities

        AuditLogger.shared.log(.phiRead, metadata: [
            "entityType": "MoodEntry",
            "entityID": id.uuidString,
            "userID": userID.uuidString
        ])
    }

    mutating func markAsDeleted() {
        self.isDeleted = true
        self.deletedAt = Date()

        AuditLogger.shared.log(.phiDeleted, metadata: [
            "entityType": "MoodEntry",
            "entityID": id.uuidString,
            "userID": userID.uuidString
        ])
    }
}

// MARK: - Mood Plaintext

private struct MoodPlaintext: Codable {
    let mood: MoodType
    let intensity: Int
    let notes: String?
    let triggers: [String]
    let location: String?
    let activities: [String]
}
