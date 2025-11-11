import Foundation

// HIPAA Compliance: Password strength validation
// Implements §164.308(a)(5)(ii)(D) - Password Management

class PasswordValidator {
    static let shared = PasswordValidator()
    
    // HIPAA Password Policy
    static let minimumLength = 12
    static let requireUppercase = true
    static let requireLowercase = true
    static let requireNumbers = true
    static let requireSpecialCharacters = true
    static let preventCommonPasswords = true
    
    private init() {}
    
    /// Validate password strength
    func validate(_ password: String) throws {
        // Length check
        guard password.count >= Self.minimumLength else {
            throw PasswordError.tooShort
        }
        
        // Uppercase check
        if Self.requireUppercase {
            guard password.range(of: "[A-Z]", options: .regularExpression) != nil else {
                throw PasswordError.missingUppercase
            }
        }
        
        // Lowercase check
        if Self.requireLowercase {
            guard password.range(of: "[a-z]", options: .regularExpression) != nil else {
                throw PasswordError.missingLowercase
            }
        }
        
        // Number check
        if Self.requireNumbers {
            guard password.range(of: "[0-9]", options: .regularExpression) != nil else {
                throw PasswordError.missingNumber
            }
        }
        
        // Special character check
        if Self.requireSpecialCharacters {
            guard password.range(of: "[^A-Za-z0-9]", options: .regularExpression) != nil else {
                throw PasswordError.missingSpecialCharacter
            }
        }
        
        // Common password check
        if Self.preventCommonPasswords {
            if commonPasswords.contains(password.lowercased()) {
                throw PasswordError.commonPassword
            }
        }
    }
    
    /// Calculate password strength (0-100)
    func strength(_ password: String) -> Int {
        var score = 0
        
        // Length bonus
        score += min(password.count * 4, 40)
        
        // Uppercase bonus
        if password.range(of: "[A-Z]", options: .regularExpression) != nil {
            score += 10
        }
        
        // Lowercase bonus
        if password.range(of: "[a-z]", options: .regularExpression) != nil {
            score += 10
        }
        
        // Number bonus
        if password.range(of: "[0-9]", options: .regularExpression) != nil {
            score += 10
        }
        
        // Special character bonus
        if password.range(of: "[^A-Za-z0-9]", options: .regularExpression) != nil {
            score += 20
        }
        
        // Penalty for common patterns
        if password.lowercased().contains("password") || 
           password.lowercased().contains("12345") {
            score -= 20
        }
        
        return min(max(score, 0), 100)
    }
    
    // Common passwords to reject
    private let commonPasswords = [
        "password", "123456", "12345678", "qwerty", "abc123",
        "monkey", "1234567", "letmein", "trustno1", "dragon",
        "baseball", "iloveyou", "master", "sunshine", "ashley",
        "bailey", "passw0rd", "shadow", "123123", "654321",
        "superman", "qazwsx", "michael", "football"
    ]
}

// MARK: - Password Errors

enum PasswordError: LocalizedError {
    case tooShort
    case missingUppercase
    case missingLowercase
    case missingNumber
    case missingSpecialCharacter
    case commonPassword
    
    var errorDescription: String? {
        switch self {
        case .tooShort:
            return "Password must be at least \(PasswordValidator.minimumLength) characters"
        case .missingUppercase:
            return "Password must contain at least one uppercase letter"
        case .missingLowercase:
            return "Password must contain at least one lowercase letter"
        case .missingNumber:
            return "Password must contain at least one number"
        case .missingSpecialCharacter:
            return "Password must contain at least one special character (!@#$%^&*)"
        case .commonPassword:
            return "Password is too common. Please choose a stronger password."
        }
    }
}
