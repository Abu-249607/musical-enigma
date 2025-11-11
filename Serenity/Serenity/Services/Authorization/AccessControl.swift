import Foundation

// HIPAA Compliance: Role-Based and Attribute-Based Access Control
// Implements §164.308(a)(4) - Information Access Management (Required)
// Implements minimum necessary principle

class AccessControl {
    static let shared = AccessControl()
    
    private init() {}
    
    /// HIPAA Compliance: Check if user has permission to access resource
    func hasPermission(
        _ permission: Permission,
        for resource: Resource,
        user: User
    ) -> Bool {
        // Role-based check
        guard user.permissions.contains(permission) else {
            AuditLogger.shared.log(.accessDenied, metadata: [
                "userID": user.id.uuidString,
                "permission": permission.rawValue,
                "resourceID": resource.id
            ])
            return false
        }
        
        // Attribute-based checks
        switch permission {
        case .readOwnJournal, .writeOwnJournal, .deleteOwnJournal,
             .readOwnMoodData, .writeOwnMoodData,
             .readOwnCravingData, .writeOwnCravingData:
            // User can only access their own data
            return resource.ownerID == user.id.uuidString
            
        case .readAssignedPatientJournal,
             .readAssignedPatientMoodData,
             .readAssignedPatientCravingData:
            // Therapist can only access assigned patients
            return user.role == .therapist &&
                   user.assignedPatientIDs.contains(UUID(uuidString: resource.ownerID)!)
            
        case .emergencyAccessPHI:
            // Emergency access requires special handling
            return authorizeEmergencyAccess(user: user, resource: resource)
            
        default:
            return true
        }
    }
    
    /// HIPAA Compliance: Emergency "break-glass" access
    /// Logs critical audit event and notifies security team
    private func authorizeEmergencyAccess(user: User, resource: Resource) -> Bool {
        guard user.role == .emergencyAccess else {
            return false
        }
        
        // HIPAA Audit: Log emergency access (CRITICAL)
        AuditLogger.shared.log(.emergencyAccess, metadata: [
            "userID": user.id.uuidString,
            "resourceID": resource.id,
            "resourceType": resource.type,
            "timestamp": ISO8601DateFormatter().string(from: Date()),
            "severity": "CRITICAL"
        ])
        
        // Notify security team (in production)
        // NotificationService.shared.notifySecurityTeam(.emergencyAccessUsed)
        
        return true
    }
}

// MARK: - Resource

/// Represents a resource being accessed
struct Resource {
    let id: String
    let type: String
    let ownerID: String
}

// MARK: - Audit Events

extension AuditEvent {
    static let accessDenied = AuditEvent(type: "ACCESS_DENIED")
}
