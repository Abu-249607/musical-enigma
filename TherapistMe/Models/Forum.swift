//
//  Forum.swift
//  Therapist.Me
//
//  Anonymous peer support forum with content moderation
//

import Foundation

struct ForumPost: Codable, Identifiable {
    let id: UUID
    let authorId: UUID // Anonymous, not linked to real user identity
    var authorAlias: String // Generated anonymous name
    var title: String
    var content: String
    var category: ForumCategory
    var tags: [String]
    var timestamp: Date
    var lastEditedDate: Date?
    var likeCount: Int
    var supportCount: Int
    var replies: [ForumReply]
    var isModerated: Bool
    var moderationStatus: ModerationStatus
    var isPinned: Bool
    var isLocked: Bool

    init(
        id: UUID = UUID(),
        authorId: UUID,
        authorAlias: String,
        title: String,
        content: String,
        category: ForumCategory,
        tags: [String] = [],
        timestamp: Date = Date(),
        lastEditedDate: Date? = nil,
        likeCount: Int = 0,
        supportCount: Int = 0,
        replies: [ForumReply] = [],
        isModerated: Bool = false,
        moderationStatus: ModerationStatus = .pending,
        isPinned: Bool = false,
        isLocked: Bool = false
    ) {
        self.id = id
        self.authorId = authorId
        self.authorAlias = authorAlias
        self.title = title
        self.content = content
        self.category = category
        self.tags = tags
        self.timestamp = timestamp
        self.lastEditedDate = lastEditedDate
        self.likeCount = likeCount
        self.supportCount = supportCount
        self.replies = replies
        self.isModerated = isModerated
        self.moderationStatus = moderationStatus
        self.isPinned = isPinned
        self.isLocked = isLocked
    }
}

struct ForumReply: Codable, Identifiable {
    let id: UUID
    let authorId: UUID
    var authorAlias: String
    var content: String
    var timestamp: Date
    var lastEditedDate: Date?
    var likeCount: Int
    var supportCount: Int
    var isModerated: Bool
    var moderationStatus: ModerationStatus

    init(
        id: UUID = UUID(),
        authorId: UUID,
        authorAlias: String,
        content: String,
        timestamp: Date = Date(),
        lastEditedDate: Date? = nil,
        likeCount: Int = 0,
        supportCount: Int = 0,
        isModerated: Bool = false,
        moderationStatus: ModerationStatus = .pending
    ) {
        self.id = id
        self.authorId = authorId
        self.authorAlias = authorAlias
        self.content = content
        self.timestamp = timestamp
        self.lastEditedDate = lastEditedDate
        self.likeCount = likeCount
        self.supportCount = supportCount
        self.isModerated = isModerated
        self.moderationStatus = moderationStatus
    }
}

enum ForumCategory: String, Codable, CaseIterable {
    case general = "General Support"
    case newToRecovery = "New to Recovery"
    case cravingsAndTriggers = "Cravings & Triggers"
    case celebratingMilestones = "Celebrating Milestones"
    case relationships = "Relationships"
    case mentalHealth = "Mental Health"
    case relapse = "Relapse Support"
    case dailyCheckIn = "Daily Check-in"
    case resources = "Resources & Tools"
    case spirituality = "Spirituality"
}

enum ModerationStatus: String, Codable {
    case pending = "Pending Review"
    case approved = "Approved"
    case flagged = "Flagged for Review"
    case rejected = "Rejected"
    case removed = "Removed"
}

struct ModerationReport: Codable, Identifiable {
    let id: UUID
    let reporterId: UUID
    let contentId: UUID // Post or Reply ID
    var contentType: ReportedContentType
    var reason: ModerationReason
    var additionalDetails: String?
    var timestamp: Date
    var status: ModerationStatus
    var reviewedBy: UUID?
    var reviewedDate: Date?
    var moderatorNotes: String?

    init(
        id: UUID = UUID(),
        reporterId: UUID,
        contentId: UUID,
        contentType: ReportedContentType,
        reason: ModerationReason,
        additionalDetails: String? = nil,
        timestamp: Date = Date(),
        status: ModerationStatus = .pending,
        reviewedBy: UUID? = nil,
        reviewedDate: Date? = nil,
        moderatorNotes: String? = nil
    ) {
        self.id = id
        self.reporterId = reporterId
        self.contentId = contentId
        self.contentType = contentType
        self.reason = reason
        self.additionalDetails = additionalDetails
        self.timestamp = timestamp
        self.status = status
        self.reviewedBy = reviewedBy
        self.reviewedDate = reviewedDate
        self.moderatorNotes = moderatorNotes
    }
}

enum ReportedContentType: String, Codable {
    case post = "Post"
    case reply = "Reply"
}

enum ModerationReason: String, Codable, CaseIterable {
    case spam = "Spam"
    case harassment = "Harassment"
    case inappropriateContent = "Inappropriate Content"
    case misinformation = "Misinformation"
    case triggeringContent = "Triggering Content"
    case promotingSubstanceUse = "Promoting Substance Use"
    case personalInformation = "Sharing Personal Information"
    case other = "Other"
}

// MARK: - Content Moderation Helper
struct ContentModerator {
    // Keywords that trigger automatic flagging
    static let flaggedKeywords = [
        // Substance promotion
        "where to buy", "dealer", "connect", "plug",
        // Personal info
        "phone number", "address", "email me at",
        // Crisis indicators
        "end it all", "suicide", "kill myself", "not worth living"
    ]

    // Positive support phrases to encourage
    static let supportivePhrases = [
        "stay strong", "proud of you", "you've got this",
        "one day at a time", "here for you", "keep going"
    ]

    /// Basic content moderation check
    static func checkContent(_ text: String) -> ModerationStatus {
        let lowercased = text.lowercased()

        // Check for flagged keywords
        for keyword in flaggedKeywords {
            if lowercased.contains(keyword) {
                return .flagged
            }
        }

        // Check for crisis keywords - requires immediate review
        if lowercased.contains("suicide") || lowercased.contains("kill myself") {
            return .flagged
        }

        return .approved
    }
}

// MARK: - Anonymous Alias Generator
struct AliasGenerator {
    private static let adjectives = [
        "Brave", "Strong", "Resilient", "Hopeful", "Peaceful",
        "Calm", "Wise", "Kind", "Bright", "Gentle",
        "Courageous", "Determined", "Inspired", "Mindful", "Serene"
    ]

    private static let nouns = [
        "Phoenix", "Warrior", "Journey", "Spirit", "Soul",
        "Heart", "Path", "Light", "Dawn", "Hope",
        "Mountain", "River", "Star", "Tree", "Ocean"
    ]

    static func generate() -> String {
        let adjective = adjectives.randomElement() ?? "Brave"
        let noun = nouns.randomElement() ?? "Soul"
        let number = Int.random(in: 100...999)
        return "\(adjective)\(noun)\(number)"
    }
}
