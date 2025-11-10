import Foundation

// HIPAA Compliance: User model with role-based access control
// Implements §164.308(a)(3) - Workforce Security
// Implements §164.308(a)(4) - Information Access Management

/// User entity representing an app user with security attributes
struct User: Identifiable, Codable {
    // HIPAA: Unique user identification (§164.312(a)(2)(i))
    let id: UUID

    // User profile (some fields are PHI)
    let email: String
    var firstName: String      // PHI: Demographic information
    var lastName: String       // PHI: Demographic information
    var dateOfBirth: Date?     // PHI: Demographic information
    var phoneNumber: String?   // PHI: Contact information

    // Authentication
    var passwordHash: String   // Never stored in plain text
    var passwordSalt: String
    var passwordHistory: [String] = [] // Store last 5 password hashes

    // Multi-Factor Authentication
    var mfaEnabled: Bool = false
    var mfaMethod: MFAMethod?
    var totpSecret: String?    // Encrypted TOTP secret
    var phoneNumberVerified: Bool = false

    // Biometric Authentication
    var biometricEnabled: Bool = false
    var biometricType: BiometricType?

    // Authorization (RBAC)
    var role: UserRole = .patient
    var permissions: Set<Permission> = []

    // Account metadata
    let createdAt: Date
    var lastLoginAt: Date?
    var lastPasswordChangeAt: Date
    var accountStatus: AccountStatus = .active

    // HIPAA Consent
    var hasAcceptedPrivacyNotice: Bool = false
    var privacyNoticeAcceptedAt: Date?
    var hasAcceptedTerms: Bool = false
    var termsAcceptedAt: Date?

    // Granular consent
    var consentPreferences: ConsentPreferences = ConsentPreferences()

    // Therapist assignment (for patient role)
    var assignedTherapistID: UUID?

    // Patient assignment (for therapist role)
    var assignedPatientIDs: [UUID] = []

    init(
        id: UUID = UUID(),
        email: String,
        firstName: String,
        lastName: String,
        passwordHash: String,
        passwordSalt: String,
        role: UserRole = .patient
    ) {
        self.id = id
        self.email = email
        self.firstName = firstName
        self.lastName = lastName
        self.passwordHash = passwordHash
        self.passwordSalt = passwordSalt
        self.role = role
        self.createdAt = Date()
        self.lastPasswordChangeAt = Date()

        // Set default permissions based on role
        self.permissions = role.defaultPermissions
    }

    // MARK: - Computed Properties

    var fullName: String {
        "\(firstName) \(lastName)"
    }

    var initials: String {
        let first = firstName.prefix(1)
        let last = lastName.prefix(1)
        return "\(first)\(last)".uppercased()
    }

    var needsPasswordChange: Bool {
        // Force password change every 90 days (HIPAA recommended)
        let daysSinceChange = Calendar.current.dateComponents(
            [.day],
            from: lastPasswordChangeAt,
            to: Date()
        ).day ?? 0
        return daysSinceChange > 90
    }

    // MARK: - Methods

    mutating func updatePassword(hash: String, salt: String) {
        // Add current password to history
        passwordHistory.append(passwordHash)

        // Keep only last 5 passwords
        if passwordHistory.count > 5 {
            passwordHistory.removeFirst()
        }

        self.passwordHash = hash
        self.passwordSalt = salt
        self.lastPasswordChangeAt = Date()
    }

    func hasRecentlyUsedPassword(_ hash: String) -> Bool {
        passwordHistory.contains(hash)
    }
}

// MARK: - User Role

/// HIPAA Compliance: Role definitions for RBAC
/// Implements minimum necessary principle (§164.502(b))
enum UserRole: String, Codable, CaseIterable {
    case patient           // End user
    case therapist         // Licensed therapist
    case admin             // System administrator
    case emergencyAccess   // Break-glass emergency access

    var displayName: String {
        switch self {
        case .patient: return "Patient"
        case .therapist: return "Therapist"
        case .admin: return "Administrator"
        case .emergencyAccess: return "Emergency Access"
        }
    }

    /// Default permissions for each role (HIPAA minimum necessary)
    var defaultPermissions: Set<Permission> {
        switch self {
        case .patient:
            return [
                .readOwnJournal,
                .writeOwnJournal,
                .deleteOwnJournal,
                .readOwnMoodData,
                .writeOwnMoodData,
                .readOwnCravingData,
                .writeOwnCravingData,
                .accessAITherapist,
                .exportOwnData,
                .deleteOwnAccount,
                .manageOwnConsent,
                .viewOwnAuditLogs
            ]

        case .therapist:
            return [
                .readAssignedPatientJournal,
                .readAssignedPatientMoodData,
                .readAssignedPatientCravingData,
                .accessAssignedPatientChat,
                .createTherapyNotes
            ]

        case .admin:
            return [
                .viewAllAuditLogs,
                .manageUsers,
                .viewSystemHealth,
                .configureSystem
            ]

        case .emergencyAccess:
            return [
                .emergencyAccessPHI
            ]
        }
    }
}

// MARK: - Permission

/// HIPAA Compliance: Granular permissions for ABAC
enum Permission: String, Codable, CaseIterable, Hashable {
    // Journal permissions
    case readOwnJournal
    case writeOwnJournal
    case deleteOwnJournal
    case readAssignedPatientJournal

    // Mood tracker permissions
    case readOwnMoodData
    case writeOwnMoodData
    case readAssignedPatientMoodData

    // Craving tracker permissions
    case readOwnCravingData
    case writeOwnCravingData
    case readAssignedPatientCravingData

    // Chat permissions
    case accessAITherapist
    case accessAssignedPatientChat

    // Therapy notes
    case createTherapyNotes

    // Privacy permissions
    case exportOwnData
    case deleteOwnAccount
    case manageOwnConsent

    // Audit permissions
    case viewOwnAuditLogs
    case viewAllAuditLogs

    // Admin permissions
    case manageUsers
    case viewSystemHealth
    case configureSystem

    // Emergency access
    case emergencyAccessPHI
}

// MARK: - Account Status

enum AccountStatus: String, Codable {
    case active
    case suspended
    case locked        // Locked due to failed login attempts
    case disabled      // Disabled by admin
    case pendingDeletion  // User requested account deletion
    case deleted
}

// MARK: - MFA Method

enum MFAMethod: String, Codable {
    case sms
    case totp  // Time-based One-Time Password (e.g., Google Authenticator)
}

// MARK: - Biometric Type

enum BiometricType: String, Codable {
    case faceID
    case touchID
}

// MARK: - Consent Preferences

/// HIPAA Compliance: Granular consent management
/// Implements Privacy Rule consent requirements
struct ConsentPreferences: Codable {
    // Core consents (required)
    var privacyNotice: Bool = false
    var termsOfService: Bool = false
    var hipaaAuthorization: Bool = false

    // Optional consents
    var analyticsConsent: Bool = false
    var crashReportingConsent: Bool = false
    var marketingConsent: Bool = false
    var researchConsent: Bool = false

    // Data sharing
    var shareDataWithTherapist: Bool = false
    var shareDataForResearch: Bool = false

    // Communication preferences
    var emailNotifications: Bool = true
    var pushNotifications: Bool = true
    var smsNotifications: Bool = false

    // Consent timestamps
    var privacyNoticeTimestamp: Date?
    var termsTimestamp: Date?
    var hipaaAuthorizationTimestamp: Date?

    var allRequiredConsentsGranted: Bool {
        privacyNotice && termsOfService && hipaaAuthorization
    }
}
