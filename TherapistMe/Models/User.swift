//
//  User.swift
//  Therapist.Me
//
//  HIPAA Compliance: PHI (Protected Health Information) - Handle with encryption
//

import Foundation

struct User: Codable, Identifiable {
    let id: UUID
    var username: String
    var email: String? // Optional for privacy

    // HIPAA PHI: Personal health information
    var profile: UserProfile
    var recoveryGoals: [RecoveryGoal]
    var substanceHistory: [SubstanceHistory]
    var emergencyContacts: [EmergencyContact]

    // Privacy and consent
    var privacyConsent: PrivacyConsent
    var notificationPreferences: NotificationPreferences

    // Account security
    var authenticationMethod: AuthenticationMethod
    var lastLoginDate: Date?
    var accountCreatedDate: Date

    // HIPAA Compliance: Audit trail reference
    var auditLogId: String

    init(
        id: UUID = UUID(),
        username: String,
        email: String? = nil,
        profile: UserProfile = UserProfile(),
        recoveryGoals: [RecoveryGoal] = [],
        substanceHistory: [SubstanceHistory] = [],
        emergencyContacts: [EmergencyContact] = [],
        privacyConsent: PrivacyConsent = PrivacyConsent(),
        notificationPreferences: NotificationPreferences = NotificationPreferences(),
        authenticationMethod: AuthenticationMethod = .none,
        accountCreatedDate: Date = Date()
    ) {
        self.id = id
        self.username = username
        self.email = email
        self.profile = profile
        self.recoveryGoals = recoveryGoals
        self.substanceHistory = substanceHistory
        self.emergencyContacts = emergencyContacts
        self.privacyConsent = privacyConsent
        self.notificationPreferences = notificationPreferences
        self.authenticationMethod = authenticationMethod
        self.accountCreatedDate = accountCreatedDate
        self.auditLogId = "USER_\(id.uuidString)"
    }
}

// MARK: - User Profile
struct UserProfile: Codable {
    var firstName: String?
    var age: Int?
    var gender: Gender?
    var timezone: String
    var language: String

    init(
        firstName: String? = nil,
        age: Int? = nil,
        gender: Gender? = nil,
        timezone: String = TimeZone.current.identifier,
        language: String = "en"
    ) {
        self.firstName = firstName
        self.age = age
        self.gender = gender
        self.timezone = timezone
        self.language = language
    }
}

enum Gender: String, Codable, CaseIterable {
    case male = "Male"
    case female = "Female"
    case nonBinary = "Non-binary"
    case preferNotToSay = "Prefer not to say"
}

// MARK: - Recovery Goals
struct RecoveryGoal: Codable, Identifiable {
    let id: UUID
    var title: String
    var description: String
    var goalType: GoalType
    var targetDate: Date?
    var isCompleted: Bool
    var createdDate: Date
    var completedDate: Date?
    var milestones: [Milestone]

    init(
        id: UUID = UUID(),
        title: String,
        description: String,
        goalType: GoalType,
        targetDate: Date? = nil,
        isCompleted: Bool = false,
        createdDate: Date = Date(),
        milestones: [Milestone] = []
    ) {
        self.id = id
        self.title = title
        self.description = description
        self.goalType = goalType
        self.targetDate = targetDate
        self.isCompleted = isCompleted
        self.createdDate = createdDate
        self.milestones = milestones
    }
}

enum GoalType: String, Codable, CaseIterable {
    case sobriety = "Complete Sobriety"
    case reduction = "Substance Reduction"
    case mentalHealth = "Mental Health Improvement"
    case relationships = "Relationship Building"
    case career = "Career/Education"
    case physical = "Physical Health"
    case custom = "Custom Goal"
}

struct Milestone: Codable, Identifiable {
    let id: UUID
    var title: String
    var isCompleted: Bool
    var completedDate: Date?

    init(id: UUID = UUID(), title: String, isCompleted: Bool = false) {
        self.id = id
        self.title = title
        self.isCompleted = isCompleted
    }
}

// MARK: - Substance History (PHI)
struct SubstanceHistory: Codable, Identifiable {
    let id: UUID
    var substanceType: SubstanceType
    var frequencyOfUse: FrequencyOfUse
    var yearsOfUse: Int
    var lastUsedDate: Date?
    var sobrietyStartDate: Date?
    var notes: String?

    init(
        id: UUID = UUID(),
        substanceType: SubstanceType,
        frequencyOfUse: FrequencyOfUse,
        yearsOfUse: Int,
        lastUsedDate: Date? = nil,
        sobrietyStartDate: Date? = nil,
        notes: String? = nil
    ) {
        self.id = id
        self.substanceType = substanceType
        self.frequencyOfUse = frequencyOfUse
        self.yearsOfUse = yearsOfUse
        self.lastUsedDate = lastUsedDate
        self.sobrietyStartDate = sobrietyStartDate
        self.notes = notes
    }
}

enum SubstanceType: String, Codable, CaseIterable {
    case alcohol = "Alcohol"
    case tobacco = "Tobacco/Nicotine"
    case cannabis = "Cannabis"
    case opioids = "Opioids"
    case stimulants = "Stimulants"
    case benzodiazepines = "Benzodiazepines"
    case hallucinogens = "Hallucinogens"
    case gambling = "Gambling"
    case other = "Other"
}

enum FrequencyOfUse: String, Codable, CaseIterable {
    case daily = "Daily"
    case weekly = "Multiple times per week"
    case occasionally = "Occasionally"
    case rarely = "Rarely"
    case former = "Former user"
}

// MARK: - Emergency Contacts
struct EmergencyContact: Codable, Identifiable {
    let id: UUID
    var name: String
    var relationship: String
    var phoneNumber: String
    var isPrimary: Bool

    init(
        id: UUID = UUID(),
        name: String,
        relationship: String,
        phoneNumber: String,
        isPrimary: Bool = false
    ) {
        self.id = id
        self.name = name
        self.relationship = relationship
        self.phoneNumber = phoneNumber
        self.isPrimary = isPrimary
    }
}

// MARK: - Privacy Consent (HIPAA Compliance)
struct PrivacyConsent: Codable {
    var hasAcceptedTerms: Bool
    var hasAcceptedPrivacyPolicy: Bool
    var hasAcceptedHIPAANotice: Bool
    var consentDate: Date?
    var dataProcessingConsent: Bool
    var analyticsConsent: Bool
    var marketingConsent: Bool

    init(
        hasAcceptedTerms: Bool = false,
        hasAcceptedPrivacyPolicy: Bool = false,
        hasAcceptedHIPAANotice: Bool = false,
        consentDate: Date? = nil,
        dataProcessingConsent: Bool = false,
        analyticsConsent: Bool = false,
        marketingConsent: Bool = false
    ) {
        self.hasAcceptedTerms = hasAcceptedTerms
        self.hasAcceptedPrivacyPolicy = hasAcceptedPrivacyPolicy
        self.hasAcceptedHIPAANotice = hasAcceptedHIPAANotice
        self.consentDate = consentDate
        self.dataProcessingConsent = dataProcessingConsent
        self.analyticsConsent = analyticsConsent
        self.marketingConsent = marketingConsent
    }
}

// MARK: - Notification Preferences
struct NotificationPreferences: Codable {
    var dailyCheckInReminder: Bool
    var encouragementMessages: Bool
    var milestoneAlerts: Bool
    var cravingSupport: Bool
    var preferredReminderTime: Date?

    init(
        dailyCheckInReminder: Bool = true,
        encouragementMessages: Bool = true,
        milestoneAlerts: Bool = true,
        cravingSupport: Bool = true,
        preferredReminderTime: Date? = nil
    ) {
        self.dailyCheckInReminder = dailyCheckInReminder
        self.encouragementMessages = encouragementMessages
        self.milestoneAlerts = milestoneAlerts
        self.cravingSupport = cravingSupport
        self.preferredReminderTime = preferredReminderTime
    }
}

// MARK: - Authentication Method
enum AuthenticationMethod: String, Codable {
    case none = "None"
    case biometric = "Face ID / Touch ID"
    case passcode = "Passcode"
    case biometricAndPasscode = "Biometric + Passcode"
}
