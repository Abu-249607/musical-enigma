import Foundation
import CryptoKit

// HIPAA Compliance: Authentication service with strong password policies
// Implements §164.312(d) - Person or Entity Authentication (Required)
// Implements §164.308(a)(5)(ii)(D) - Password Management (Addressable)

class AuthenticationService {
    static let shared = AuthenticationService()
    
    private init() {}
    
    // MARK: - Registration
    
    /// HIPAA Compliance: Register new user with strong password
    func register(
        email: String,
        password: String,
        firstName: String,
        lastName: String
    ) async throws -> User {
        // Validate email format
        guard isValidEmail(email) else {
            throw AuthenticationError.invalidEmail
        }
        
        // Validate password strength (HIPAA requirement)
        try PasswordValidator.shared.validate(password)
        
        // Check if email already exists
        if await userExists(email: email) {
            throw AuthenticationError.emailAlreadyExists
        }
        
        // Generate password salt
        let salt = generateSalt()
        
        // Hash password with salt
        let passwordHash = hashPassword(password, salt: salt)
        
        // Create user
        let user = User(
            email: email,
            firstName: firstName,
            lastName: lastName,
            passwordHash: passwordHash,
            passwordSalt: salt
        )
        
        // Save user (in production, save to backend)
        try await saveUser(user)
        
        // HIPAA Audit: Log registration
        AuditLogger.shared.log(.userRegistered, metadata: [
            "userID": user.id.uuidString,
            "email": email
        ])
        
        return user
    }
    
    // MARK: - Login
    
    /// HIPAA Compliance: Authenticate user with email and password
    func login(email: String, password: String) async throws -> User {
        // Retrieve user by email
        guard let user = await getUserByEmail(email) else {
            // HIPAA Audit: Log failed login attempt
            AuditLogger.shared.log(.loginFailure, metadata: [
                "email": email,
                "reason": "User not found"
            ])
            throw AuthenticationError.invalidCredentials
        }
        
        // Check if account is locked
        if user.accountStatus == .locked {
            throw AuthenticationError.accountLocked
        }
        
        // Verify password
        let passwordHash = hashPassword(password, salt: user.passwordSalt)
        
        guard passwordHash == user.passwordHash else {
            // HIPAA Audit: Log failed login attempt
            AuditLogger.shared.log(.loginFailure, metadata: [
                "userID": user.id.uuidString,
                "reason": "Invalid password"
            ])
            
            // Track failed attempts (lock after 5 attempts)
            await trackFailedLoginAttempt(userID: user.id)
            
            throw AuthenticationError.invalidCredentials
        }
        
        // Check if password change is required
        if user.needsPasswordChange {
            throw AuthenticationError.passwordChangeRequired
        }
        
        // Update last login
        var updatedUser = user
        updatedUser.lastLoginAt = Date()
        try await saveUser(updatedUser)
        
        // Reset failed login attempts
        await resetFailedLoginAttempts(userID: user.id)
        
        return updatedUser
    }
    
    // MARK: - Password Management
    
    /// HIPAA Compliance: Change user password
    func changePassword(
        userID: UUID,
        currentPassword: String,
        newPassword: String
    ) async throws {
        guard var user = await getUserByID(userID) else {
            throw AuthenticationError.userNotFound
        }
        
        // Verify current password
        let currentHash = hashPassword(currentPassword, salt: user.passwordSalt)
        guard currentHash == user.passwordHash else {
            throw AuthenticationError.invalidCredentials
        }
        
        // Validate new password
        try PasswordValidator.shared.validate(newPassword)
        
        // Check if password was recently used
        let newHash = hashPassword(newPassword, salt: user.passwordSalt)
        if user.hasRecentlyUsedPassword(newHash) {
            throw AuthenticationError.passwordRecentlyUsed
        }
        
        // Generate new salt
        let newSalt = generateSalt()
        let newHashWithSalt = hashPassword(newPassword, salt: newSalt)
        
        // Update password
        user.updatePassword(hash: newHashWithSalt, salt: newSalt)
        
        try await saveUser(user)
        
        // HIPAA Audit: Log password change
        AuditLogger.shared.log(.passwordChanged, metadata: [
            "userID": userID.uuidString
        ])
    }
    
    // MARK: - Helper Methods
    
    private func generateSalt() -> String {
        let saltData = Data((0..<32).map { _ in UInt8.random(in: 0...255) })
        return saltData.base64EncodedString()
    }
    
    private func hashPassword(_ password: String, salt: String) -> String {
        let passwordData = (password + salt).data(using: .utf8)!
        let hash = SHA256.hash(data: passwordData)
        return hash.compactMap { String(format: "%02x", $0) }.joined()
    }
    
    private func isValidEmail(_ email: String) -> Bool {
        let emailRegex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
        let emailPredicate = NSPredicate(format:"SELF MATCHES %@", emailRegex)
        return emailPredicate.evaluate(with: email)
    }
    
    // MARK: - User Storage (Mock)
    
    private var mockUsers: [User] = []
    private var failedLoginAttempts: [UUID: Int] = [:]
    
    private func userExists(email: String) async -> Bool {
        mockUsers.contains { $0.email == email }
    }
    
    private func getUserByEmail(_ email: String) async -> User? {
        mockUsers.first { $0.email == email }
    }
    
    private func getUserByID(_ id: UUID) async -> User? {
        mockUsers.first { $0.id == id }
    }
    
    private func saveUser(_ user: User) async throws {
        if let index = mockUsers.firstIndex(where: { $0.id == user.id }) {
            mockUsers[index] = user
        } else {
            mockUsers.append(user)
        }
    }
    
    private func trackFailedLoginAttempt(userID: UUID) async {
        let attempts = (failedLoginAttempts[userID] ?? 0) + 1
        failedLoginAttempts[userID] = attempts
        
        // Lock account after 5 failed attempts
        if attempts >= 5 {
            if var user = await getUserByID(userID) {
                user.accountStatus = .locked
                try? await saveUser(user)
                
                AuditLogger.shared.log(.accountLocked, metadata: [
                    "userID": userID.uuidString,
                    "reason": "Too many failed login attempts"
                ])
            }
        }
    }
    
    private func resetFailedLoginAttempts(userID: UUID) async {
        failedLoginAttempts.removeValue(forKey: userID)
    }
}

// MARK: - Authentication Errors

enum AuthenticationError: LocalizedError {
    case invalidEmail
    case emailAlreadyExists
    case invalidCredentials
    case userNotFound
    case accountLocked
    case passwordChangeRequired
    case passwordRecentlyUsed
    
    var errorDescription: String? {
        switch self {
        case .invalidEmail:
            return "Invalid email address"
        case .emailAlreadyExists:
            return "Email already registered"
        case .invalidCredentials:
            return "Invalid email or password"
        case .userNotFound:
            return "User not found"
        case .accountLocked:
            return "Account locked due to too many failed login attempts"
        case .passwordChangeRequired:
            return "Password change required (90 days since last change)"
        case .passwordRecentlyUsed:
            return "Password was recently used. Please choose a different password."
        }
    }
}

// MARK: - Audit Events

extension AuditEvent {
    static let userRegistered = AuditEvent(type: "USER_REGISTERED")
    static let accountLocked = AuditEvent(type: "ACCOUNT_LOCKED")
}
