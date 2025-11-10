import Foundation

// HIPAA Compliance: Craving log entry model with encryption
// Craving data is PHI related to substance use disorder treatment

struct CravingLog: Identifiable, Codable {
    // HIPAA: Unique identifier
    let id: UUID

    // Ownership
    let userID: UUID

    // Craving data (ENCRYPTED - PHI)
    var substance: SubstanceType
    var intensity: Int           // 1-10 scale
    var duration: TimeInterval?  // How long did the craving last (in seconds)
    var triggers: [String]
    var copingStrategies: [String]  // What did the user do to cope
    var didUse: Bool?           // Did the user relapse (optional, sensitive)
    var notes: String?

    // Context
    var location: String?
    var socialContext: SocialContext?

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
        substance: SubstanceType,
        intensity: Int,
        triggers: [String] = [],
        copingStrategies: [String] = [],
        recordedAt: Date = Date()
    ) {
        self.id = id
        self.userID = userID
        self.substance = substance
        self.intensity = min(max(intensity, 1), 10)
        self.triggers = triggers
        self.copingStrategies = copingStrategies
        self.recordedAt = recordedAt
        self.createdAt = Date()
    }

    // MARK: - Encryption

    mutating func encrypt(using encryptionService: EncryptionService) throws {
        let plaintext = CravingPlaintext(
            substance: substance,
            intensity: intensity,
            duration: duration,
            triggers: triggers,
            copingStrategies: copingStrategies,
            didUse: didUse,
            notes: notes,
            location: location,
            socialContext: socialContext
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
        self.copingStrategies = []

        AuditLogger.shared.log(.phiEncrypted, metadata: [
            "entityType": "CravingLog",
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
                    "entityType": "CravingLog",
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

        let plaintext = try JSONDecoder().decode(CravingPlaintext.self, from: plaintextData)
        self.substance = plaintext.substance
        self.intensity = plaintext.intensity
        self.duration = plaintext.duration
        self.triggers = plaintext.triggers
        self.copingStrategies = plaintext.copingStrategies
        self.didUse = plaintext.didUse
        self.notes = plaintext.notes
        self.location = plaintext.location
        self.socialContext = plaintext.socialContext

        AuditLogger.shared.log(.phiRead, metadata: [
            "entityType": "CravingLog",
            "entityID": id.uuidString,
            "userID": userID.uuidString
        ])
    }

    mutating func markAsDeleted() {
        self.isDeleted = true
        self.deletedAt = Date()

        AuditLogger.shared.log(.phiDeleted, metadata: [
            "entityType": "CravingLog",
            "entityID": id.uuidString,
            "userID": userID.uuidString
        ])
    }
}

// MARK: - Craving Plaintext

private struct CravingPlaintext: Codable {
    let substance: SubstanceType
    let intensity: Int
    let duration: TimeInterval?
    let triggers: [String]
    let copingStrategies: [String]
    let didUse: Bool?
    let notes: String?
    let location: String?
    let socialContext: SocialContext?
}

// MARK: - Substance Type

enum SubstanceType: String, Codable, CaseIterable {
    case alcohol = "Alcohol"
    case nicotine = "Nicotine"
    case cannabis = "Cannabis"
    case opioids = "Opioids"
    case stimulants = "Stimulants"
    case sedatives = "Sedatives"
    case hallucinogens = "Hallucinogens"
    case other = "Other"

    var icon: String {
        switch self {
        case .alcohol: return "🍺"
        case .nicotine: return "🚬"
        case .cannabis: return "🌿"
        case .opioids: return "💊"
        case .stimulants: return "⚡"
        case .sedatives: return "😴"
        case .hallucinogens: return "🌈"
        case .other: return "❓"
        }
    }
}

// MARK: - Social Context

enum SocialContext: String, Codable {
    case alone = "Alone"
    case withFriends = "With Friends"
    case withFamily = "With Family"
    case atWork = "At Work"
    case inPublic = "In Public"
    case other = "Other"
}
