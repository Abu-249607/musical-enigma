import Foundation
import LocalAuthentication

// HIPAA Compliance: Biometric authentication (Face ID / Touch ID)
// Implements §164.312(d) - Person or Entity Authentication
// Provides additional authentication factor

class BiometricAuth {
    static let shared: BiometricAuth? = {
        let context = LAContext()
        var error: NSError?
        
        // Check if biometric authentication is available
        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            return nil
        }
        
        return BiometricAuth()
    }()
    
    private let context = LAContext()
    
    private init() {}
    
    /// Get available biometric type
    var biometricType: BiometricType {
        switch context.biometryType {
        case .faceID:
            return .faceID
        case .touchID:
            return .touchID
        default:
            return .touchID // Fallback
        }
    }
    
    /// HIPAA Compliance: Authenticate using biometrics
    func authenticate(reason: String) async throws -> Bool {
        let context = LAContext()
        context.localizedCancelTitle = "Cancel"
        context.localizedFallbackTitle = "Use Passcode"
        
        do {
            let success = try await context.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: reason
            )
            
            if success {
                AuditLogger.shared.log(.biometricSuccess, metadata: [
                    "biometricType": biometricType.rawValue
                ])
            }
            
            return success
            
        } catch {
            AuditLogger.shared.log(.biometricFailure, metadata: [
                "biometricType": biometricType.rawValue,
                "error": error.localizedDescription
            ])
            throw BiometricError.authenticationFailed
        }
    }
    
    /// Check if biometric authentication is available
    static var isAvailable: Bool {
        let context = LAContext()
        var error: NSError?
        return context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
    }
}

// MARK: - Biometric Errors

enum BiometricError: LocalizedError {
    case notAvailable
    case authenticationFailed
    
    var errorDescription: String? {
        switch self {
        case .notAvailable:
            return "Biometric authentication is not available on this device"
        case .authenticationFailed:
            return "Biometric authentication failed"
        }
    }
}
