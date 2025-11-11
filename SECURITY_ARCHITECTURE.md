# Security Architecture - Serenity

**Version:** 1.0
**Last Updated:** November 10, 2025
**Platform:** iOS 16.0+

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Security Layers](#2-security-layers)
3. [Component Architecture](#3-component-architecture)
4. [Data Flow](#4-data-flow)
5. [Encryption Architecture](#5-encryption-architecture)
6. [Authentication & Authorization](#6-authentication--authorization)
7. [Audit Logging Architecture](#7-audit-logging-architecture)
8. [Network Security](#8-network-security)
9. [Secure Storage](#9-secure-storage)
10. [Threat Model](#10-threat-model)

---

## 1. Architecture Overview

### 1.1 Design Principles

The Serenity security architecture is built on the following principles:

- **Defense in Depth**: Multiple layers of security controls
- **Zero Trust**: Verify every access request
- **Privacy by Design**: Data minimization and encryption by default
- **Principle of Least Privilege**: Minimal access rights
- **Fail Secure**: System defaults to secure state on failure
- **Separation of Concerns**: Modular architecture with clear boundaries

### 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│                        (SwiftUI Views)                       │
├─────────────────────────────────────────────────────────────┤
│                   Presentation Layer                         │
│              (ViewModels, State Management)                  │
├─────────────────────────────────────────────────────────────┤
│                    Security Layer                            │
│   ┌──────────────┬──────────────┬──────────────────────┐   │
│   │ Authentication│ Authorization│   Audit Logging      │   │
│   ├──────────────┼──────────────┼──────────────────────┤   │
│   │  Encryption  │ Session Mgmt │  Integrity Checks    │   │
│   └──────────────┴──────────────┴──────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   Business Logic Layer                       │
│   ┌──────────────┬──────────────┬──────────────────────┐   │
│   │    Mood      │   Journal    │   AI Chat            │   │
│   │   Tracker    │   Service    │   Service            │   │
│   └──────────────┴──────────────┴──────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   Data Access Layer                          │
│   ┌──────────────┬──────────────┬──────────────────────┐   │
│   │  CoreData    │   Keychain   │   UserDefaults       │   │
│   │  Manager     │   Manager    │   (Non-PHI only)     │   │
│   └──────────────┴──────────────┴──────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   Storage Layer                              │
│   ┌──────────────┬──────────────┬──────────────────────┐   │
│   │   Encrypted  │ Hardware-    │   Local Storage      │   │
│   │   CoreData   │ Backed Keys  │   (Non-sensitive)    │   │
│   └──────────────┴──────────────┴──────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Security Layers

### 2.1 Layer 1: Application Security

**Components:**
- Jailbreak detection
- Debugger detection
- Code obfuscation
- Binary integrity checks
- Screenshot prevention for PHI screens

**Implementation:**
```swift
// SecurityValidator.swift
class SecurityValidator {
    static func validateEnvironment() throws {
        try checkJailbreak()
        try checkDebugger()
        try verifyBinaryIntegrity()
    }
}
```

### 2.2 Layer 2: Authentication & Authorization

**Components:**
- Multi-factor authentication
- Biometric authentication (Face ID/Touch ID)
- Role-based access control (RBAC)
- Attribute-based access control (ABAC)
- Session management with timeout

**Implementation:**
```swift
// AccessControl.swift
protocol AccessControl {
    func hasPermission(_ permission: Permission, for resource: Resource) -> Bool
    func enforcePolicy(_ policy: AccessPolicy) throws
}
```

### 2.3 Layer 3: Data Encryption

**Components:**
- AES-256-GCM encryption at rest
- TLS 1.3 encryption in transit
- Hardware-backed key storage
- Secure key generation and rotation

### 2.4 Layer 4: Audit & Monitoring

**Components:**
- Tamper-proof audit logging
- Real-time security monitoring
- Anomaly detection
- Breach detection

---

## 3. Component Architecture

### 3.1 Security Services

```
Services/
├── Authentication/
│   ├── AuthenticationService.swift
│   ├── BiometricAuth.swift
│   ├── MFAService.swift
│   ├── TOTPGenerator.swift
│   └── PasswordValidator.swift
├── Authorization/
│   ├── AccessControl.swift
│   ├── PermissionManager.swift
│   └── PolicyEngine.swift
├── Encryption/
│   ├── EncryptionService.swift
│   ├── KeychainManager.swift
│   └── KeyRotationService.swift
├── Session/
│   ├── SessionManager.swift
│   └── TokenManager.swift
├── Audit/
│   ├── AuditLogger.swift
│   ├── AuditEvent.swift
│   └── LogIntegrityValidator.swift
├── Privacy/
│   ├── ConsentManager.swift
│   ├── DataExporter.swift
│   └── AccountDeletionService.swift
└── Security/
    ├── SecurityValidator.swift
    ├── IntegrityValidator.swift
    └── SecureDataManager.swift
```

### 3.2 Data Models

```
Models/
├── User.swift                  // User entity with role
├── UserRole.swift              // Role definitions
├── Permission.swift            // Permission definitions
├── JournalEntry.swift          // Encrypted journal entry
├── MoodEntry.swift             // Encrypted mood data
├── CravingLog.swift            // Encrypted craving data
├── ChatMessage.swift           // Encrypted chat transcript
├── AuditLog.swift              // Audit event record
├── Consent.swift               // User consent record
└── Session.swift               // Active session data
```

### 3.3 View Layer

```
Views/
├── Onboarding/
│   ├── WelcomeView.swift
│   ├── PrivacyNoticeView.swift
│   ├── ConsentView.swift
│   └── RegistrationView.swift
├── Authentication/
│   ├── LoginView.swift
│   ├── MFASetupView.swift
│   └── BiometricSetupView.swift
├── Dashboard/
│   └── DashboardView.swift
├── Mood/
│   ├── MoodTrackerView.swift
│   └── MoodHistoryView.swift
├── Journal/
│   ├── JournalListView.swift
│   ├── JournalEntryView.swift
│   └── JournalEditorView.swift
├── Chat/
│   └── AITherapistChatView.swift
└── Privacy/
    ├── PrivacySettingsView.swift
    ├── DataExportView.swift
    ├── ConsentManagementView.swift
    └── AccountDeletionView.swift
```

---

## 4. Data Flow

### 4.1 Authentication Flow

```
┌─────────┐       ┌──────────────┐       ┌─────────────┐
│  User   │──1──>│   LoginView  │──2──>│ Biometric   │
└─────────┘       └──────────────┘       │ Auth        │
                         │                └─────────────┘
                         │                       │
                         3                       4
                         ▼                       ▼
                  ┌──────────────┐       ┌─────────────┐
                  │ Password     │<──5──│ MFA Service │
                  │ Validation   │       └─────────────┘
                  └──────────────┘              │
                         │                       6
                         7                       ▼
                         ▼                ┌─────────────┐
                  ┌──────────────┐       │ Session     │
                  │ Auth Service │──8──>│ Manager     │
                  └──────────────┘       └─────────────┘
                         │                       │
                         9                      10
                         ▼                       ▼
                  ┌──────────────┐       ┌─────────────┐
                  │ Audit Logger │       │ Dashboard   │
                  └──────────────┘       └─────────────┘

1. User enters credentials
2. Biometric prompt (if enabled)
3. Password strength validation
4. Biometric authentication
5. MFA challenge (SMS/TOTP)
6. MFA verification
7. Password hash comparison
8. Create secure session
9. Log authentication event
10. Navigate to dashboard
```

### 4.2 Journal Entry Creation Flow

```
┌─────────┐       ┌──────────────┐       ┌─────────────┐
│  User   │──1──>│ Journal      │──2──>│ Access      │
└─────────┘       │ Editor       │       │ Control     │
                  └──────────────┘       └─────────────┘
                         │                       │
                         3                       4
                         ▼                       ▼
                  ┌──────────────┐       ┌─────────────┐
                  │ Encryption   │<──5──│ Journal     │
                  │ Service      │       │ Service     │
                  └──────────────┘       └─────────────┘
                         │                       │
                         6                       7
                         ▼                       ▼
                  ┌──────────────┐       ┌─────────────┐
                  │ Keychain     │       │ CoreData    │
                  │ (Get Key)    │       │ Manager     │
                  └──────────────┘       └─────────────┘
                         │                       │
                         8                       9
                         ▼                       ▼
                  ┌──────────────┐       ┌─────────────┐
                  │ Integrity    │       │ Audit       │
                  │ Validator    │       │ Logger      │
                  └──────────────┘       └─────────────┘

1. User writes journal entry
2. Check write permission
3. Permission granted
4. Create journal entry
5. Request encryption
6. Retrieve encryption key from Keychain
7. Save encrypted entry to CoreData
8. Generate SHA-256 checksum
9. Log PHI write event
```

### 4.3 Data Export Flow (HIPAA Right to Access)

```
┌─────────┐       ┌──────────────┐       ┌─────────────┐
│  User   │──1──>│ Data Export  │──2──>│ Re-Auth     │
└─────────┘       │ View         │       │ (Biometric) │
                  └──────────────┘       └─────────────┘
                         │                       │
                         3                       4
                         ▼                       ▼
                  ┌──────────────┐       ┌─────────────┐
                  │ Access       │       │ Data        │
                  │ Control      │──5──>│ Exporter    │
                  └──────────────┘       └─────────────┘
                         │                       │
                         6                       7
                         ▼                       ▼
                  ┌──────────────┐       ┌─────────────┐
                  │ Fetch PHI    │       │ Decrypt     │
                  │ from Storage │──8──>│ Data        │
                  └──────────────┘       └─────────────┘
                         │                       │
                         9                      10
                         ▼                       ▼
                  ┌──────────────┐       ┌─────────────┐
                  │ Generate     │       │ Audit       │
                  │ JSON/PDF     │──11─>│ Logger      │
                  └──────────────┘       └─────────────┘
                         │
                        12
                         ▼
                  ┌──────────────┐
                  │ Share Sheet  │
                  └──────────────┘

1. User requests data export
2. Re-authenticate with biometric
3. Check export permission
4. Initialize export process
5. Grant access
6. Fetch all user PHI
7. Decrypt entries
8. Decryption complete
9. Generate export file
10. Log data export event
11. Export complete
12. Present share sheet
```

---

## 5. Encryption Architecture

### 5.1 Encryption Strategy

**Encryption at Rest:**
- **Algorithm**: AES-256-GCM (Authenticated Encryption with Associated Data)
- **Key Size**: 256 bits
- **Key Storage**: iOS Keychain (hardware-backed via Secure Enclave)
- **Key Generation**: CryptoKit `SymmetricKey.init(size: .bits256)`
- **Nonce**: Unique 12-byte nonce per encryption operation
- **Associated Data**: Entity ID and timestamp for context binding

**Encryption in Transit:**
- **Protocol**: TLS 1.3
- **Certificate Pinning**: Public key pinning for API endpoints
- **Perfect Forward Secrecy**: Ephemeral Diffie-Hellman key exchange

### 5.2 Encryption Implementation

```swift
// EncryptionService.swift
import CryptoKit
import Foundation

class EncryptionService {
    // HIPAA Compliance: AES-256-GCM encryption for all PHI

    /// Encrypts data using AES-256-GCM
    /// - Parameters:
    ///   - data: Plaintext data to encrypt
    ///   - associatedData: Context data (entity ID, timestamp)
    /// - Returns: Encrypted data with nonce and tag
    func encrypt(_ data: Data, associatedData: Data?) throws -> EncryptedData {
        // Retrieve or generate encryption key
        let key = try getEncryptionKey()

        // Generate unique nonce (12 bytes for GCM)
        let nonce = AES.GCM.Nonce()

        // Encrypt with authenticated encryption
        let sealedBox = try AES.GCM.seal(
            data,
            using: key,
            nonce: nonce,
            authenticating: associatedData ?? Data()
        )

        // Combine nonce + ciphertext + tag
        let encrypted = EncryptedData(
            nonce: sealedBox.nonce,
            ciphertext: sealedBox.ciphertext,
            tag: sealedBox.tag
        )

        // HIPAA Audit: Log encryption event (no PHI in log)
        AuditLogger.shared.log(.dataEncrypted, metadata: [
            "entityType": String(describing: type(of: data)),
            "dataSize": data.count
        ])

        return encrypted
    }

    /// Decrypts AES-256-GCM encrypted data
    func decrypt(_ encryptedData: EncryptedData, associatedData: Data?) throws -> Data {
        let key = try getEncryptionKey()

        // Reconstruct sealed box
        let sealedBox = try AES.GCM.SealedBox(
            nonce: encryptedData.nonce,
            ciphertext: encryptedData.ciphertext,
            tag: encryptedData.tag
        )

        // Decrypt and verify authenticity
        let decrypted = try AES.GCM.open(
            sealedBox,
            using: key,
            authenticating: associatedData ?? Data()
        )

        return decrypted
    }
}
```

### 5.3 Key Management

```swift
// KeychainManager.swift
class KeychainManager {
    // HIPAA Compliance: Hardware-backed encryption key storage

    /// Stores encryption key in iOS Keychain with Secure Enclave protection
    func storeEncryptionKey(_ key: SymmetricKey, identifier: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassKey,
            kSecAttrApplicationTag as String: identifier.data(using: .utf8)!,
            kSecValueData as String: key.dataRepresentation,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
            // Require biometric or device passcode
            kSecAttrAccessControl as String: try createAccessControl()
        ]

        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else {
            throw KeychainError.storageFailure(status)
        }

        // HIPAA Audit: Log key storage (no key data in log)
        AuditLogger.shared.log(.encryptionKeyStored, metadata: [
            "keyIdentifier": identifier
        ])
    }

    private func createAccessControl() throws -> SecAccessControl {
        var error: Unmanaged<CFError>?

        guard let access = SecAccessControlCreateWithFlags(
            kCFAllocatorDefault,
            kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
            [.userPresence, .privateKeyUsage], // Require biometric/passcode
            &error
        ) else {
            throw KeychainError.accessControlFailure
        }

        return access
    }
}
```

---

## 6. Authentication & Authorization

### 6.1 Authentication Architecture

**Multi-Factor Authentication:**
1. **Factor 1**: Password (knowledge-based)
2. **Factor 2**: SMS OTP or TOTP (possession-based)
3. **Factor 3**: Biometric (inherence-based)

**Password Policy:**
```swift
// PasswordValidator.swift
struct PasswordPolicy {
    static let minimumLength = 12
    static let requireUppercase = true
    static let requireLowercase = true
    static let requireNumbers = true
    static let requireSpecialCharacters = true
    static let preventCommonPasswords = true
    static let passwordHistoryCount = 5 // Prevent reuse of last 5
}
```

### 6.2 Authorization Architecture (RBAC + ABAC)

**Role Definitions:**
```swift
// UserRole.swift
enum UserRole: String, Codable {
    case patient           // End user
    case therapist         // Assigned therapist
    case admin             // System administrator
    case emergencyAccess   // Break-glass access
}
```

**Permission Matrix:**
```swift
// Permission.swift
enum Permission: String {
    // Journal permissions
    case readOwnJournal
    case writeOwnJournal
    case deleteOwnJournal
    case readAssignedPatientJournal  // Therapist only

    // Mood tracker permissions
    case readOwnMoodData
    case writeOwnMoodData
    case readAssignedPatientMoodData

    // Chat permissions
    case accessAITherapist
    case accessAssignedTherapist

    // Privacy permissions
    case exportOwnData
    case deleteOwnAccount
    case manageConsent

    // Admin permissions
    case viewAuditLogs
    case manageUsers
    case emergencyAccess
}
```

**Access Control Implementation:**
```swift
// AccessControl.swift
class AccessControl {
    // HIPAA Compliance: RBAC + ABAC for minimum necessary access

    func hasPermission(_ permission: Permission, for resource: Resource, user: User) -> Bool {
        // Role-based check
        guard user.role.permissions.contains(permission) else {
            return false
        }

        // Attribute-based check
        switch permission {
        case .readOwnJournal, .writeOwnJournal, .deleteOwnJournal:
            // User can only access their own data
            return resource.ownerID == user.id

        case .readAssignedPatientJournal:
            // Therapist can only access assigned patients
            return user.role == .therapist &&
                   user.assignedPatientIDs.contains(resource.ownerID)

        case .emergencyAccess:
            // Emergency access requires special authorization + audit
            return authorizeEmergencyAccess(user: user, resource: resource)

        default:
            return true
        }
    }

    private func authorizeEmergencyAccess(user: User, resource: Resource) -> Bool {
        // HIPAA Break-Glass: Emergency access with mandatory audit
        AuditLogger.shared.log(.emergencyAccess, metadata: [
            "userID": user.id,
            "resourceID": resource.id,
            "timestamp": ISO8601DateFormatter().string(from: Date()),
            "severity": "CRITICAL"
        ])

        // Notify security team
        NotificationService.shared.notifySecurityTeam(.emergencyAccessUsed)

        return user.role == .emergencyAccess
    }
}
```

---

## 7. Audit Logging Architecture

### 7.1 Audit Requirements (HIPAA §164.312(b))

**What to Log:**
- ✅ User authentication (success/failure)
- ✅ PHI access (read/write/delete)
- ✅ Configuration changes
- ✅ Security incidents
- ✅ Data export operations
- ✅ Consent changes
- ✅ Emergency access
- ✅ Account deletion

**What NOT to Log:**
- ❌ PHI content (journal entries, mood data, etc.)
- ❌ Passwords or encryption keys
- ❌ Biometric templates

### 7.2 Audit Log Implementation

```swift
// AuditLogger.swift
class AuditLogger {
    // HIPAA Compliance: Tamper-proof audit logging with 7-year retention

    static let shared = AuditLogger()

    func log(_ event: AuditEvent, metadata: [String: Any] = [:]) {
        let logEntry = AuditLogEntry(
            id: UUID(),
            timestamp: Date(),
            eventType: event,
            userID: SessionManager.shared.currentUser?.id,
            metadata: metadata,
            ipAddress: getIPAddress(),
            deviceID: UIDevice.current.identifierForVendor?.uuidString
        )

        // Sign log entry with SHA-256 for tamper detection
        let signature = try? signLogEntry(logEntry)
        logEntry.signature = signature

        // Encrypt log entry (logs contain user IDs, which are identifiers)
        let encryptedLog = try? EncryptionService.shared.encrypt(
            logEntry.toJSON(),
            associatedData: nil
        )

        // Save to persistent storage
        CoreDataManager.shared.save(logEntry)

        // Optional: Send to remote SIEM for real-time monitoring
        #if !DEBUG
        sendToSIEM(logEntry)
        #endif
    }

    private func signLogEntry(_ entry: AuditLogEntry) throws -> String {
        // Create SHA-256 hash of log entry
        let jsonData = entry.toJSON()
        let hash = SHA256.hash(data: jsonData)
        return hash.compactMap { String(format: "%02x", $0) }.joined()
    }
}
```

### 7.3 Audit Event Types

```swift
// AuditEvent.swift
enum AuditEvent: String, Codable {
    // Authentication events
    case loginSuccess = "AUTH_LOGIN_SUCCESS"
    case loginFailure = "AUTH_LOGIN_FAILURE"
    case logoutSuccess = "AUTH_LOGOUT_SUCCESS"
    case mfaEnabled = "AUTH_MFA_ENABLED"
    case mfaDisabled = "AUTH_MFA_DISABLED"
    case biometricEnabled = "AUTH_BIOMETRIC_ENABLED"

    // PHI access events (HIPAA required)
    case phiRead = "PHI_READ"
    case phiWrite = "PHI_WRITE"
    case phiDelete = "PHI_DELETE"
    case phiExport = "PHI_EXPORT"

    // Security events
    case emergencyAccess = "SECURITY_EMERGENCY_ACCESS"
    case jailbreakDetected = "SECURITY_JAILBREAK_DETECTED"
    case integrityViolation = "SECURITY_INTEGRITY_VIOLATION"
    case sessionTimeout = "SECURITY_SESSION_TIMEOUT"

    // Privacy events
    case consentGranted = "PRIVACY_CONSENT_GRANTED"
    case consentRevoked = "PRIVACY_CONSENT_REVOKED"
    case accountDeleted = "PRIVACY_ACCOUNT_DELETED"

    // Data events
    case dataEncrypted = "DATA_ENCRYPTED"
    case dataDecrypted = "DATA_DECRYPTED"
    case encryptionKeyStored = "DATA_KEY_STORED"
    case encryptionKeyRotated = "DATA_KEY_ROTATED"
}
```

---

## 8. Network Security

### 8.1 TLS Configuration

```swift
// NetworkManager.swift
class NetworkManager {
    // HIPAA Compliance: TLS 1.3 for all network communications

    private func createSecureSession() -> URLSession {
        let configuration = URLSessionConfiguration.default
        configuration.tlsMinimumSupportedProtocolVersion = .TLSv13
        configuration.tlsMaximumSupportedProtocolVersion = .TLSv13

        let session = URLSession(
            configuration: configuration,
            delegate: self,
            delegateQueue: nil
        )

        return session
    }
}

extension NetworkManager: URLSessionDelegate {
    // Certificate pinning for API endpoints
    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        guard let serverTrust = challenge.protectionSpace.serverTrust else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Verify certificate against pinned public keys
        if CertificatePinner.shared.validate(serverTrust, for: challenge.protectionSpace.host) {
            let credential = URLCredential(trust: serverTrust)
            completionHandler(.useCredential, credential)
        } else {
            // Certificate pinning failure - log security incident
            AuditLogger.shared.log(.securityIncident, metadata: [
                "reason": "Certificate pinning failure",
                "host": challenge.protectionSpace.host
            ])
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}
```

### 8.2 Certificate Pinning

```swift
// CertificatePinner.swift
class CertificatePinner {
    // HIPAA Compliance: Prevent MITM attacks via certificate pinning

    private let pinnedPublicKeys: [String: [String]] = [
        "api.serenity.com": [
            "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
            "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=" // Backup key
        ]
    ]

    func validate(_ serverTrust: SecTrust, for host: String) -> Bool {
        guard let pinnedKeys = pinnedPublicKeys[host] else {
            // No pinned keys for this host - reject by default
            return false
        }

        // Extract public key from server certificate
        guard let serverPublicKey = extractPublicKey(from: serverTrust) else {
            return false
        }

        // Compare with pinned keys
        return pinnedKeys.contains(serverPublicKey)
    }
}
```

---

## 9. Secure Storage

### 9.1 Storage Security Matrix

| Data Type | Storage Location | Encryption | Backup |
|-----------|------------------|------------|--------|
| Encryption keys | Keychain (Secure Enclave) | Hardware-backed | ❌ Excluded |
| User credentials | Keychain | AES-256 | ❌ Excluded |
| Journal entries | CoreData | AES-256-GCM | ✅ Encrypted |
| Mood tracker data | CoreData | AES-256-GCM | ✅ Encrypted |
| Chat transcripts | CoreData | AES-256-GCM | ✅ Encrypted |
| Audit logs | CoreData | AES-256-GCM | ✅ Encrypted |
| App preferences | UserDefaults | None | ✅ Allowed |

### 9.2 CoreData Encryption

```swift
// CoreDataManager.swift
class CoreDataManager {
    // HIPAA Compliance: Encrypted persistent storage for all PHI

    lazy var persistentContainer: NSPersistentContainer = {
        let container = NSPersistentContainer(name: "Serenity")

        // Enable persistent history tracking for sync
        let description = container.persistentStoreDescriptions.first
        description?.setOption(true as NSNumber, forKey: NSPersistentHistoryTrackingKey)

        // Enable CloudKit sync (encrypted)
        description?.cloudKitContainerOptions = NSPersistentCloudKitContainerOptions(
            containerIdentifier: "iCloud.com.serenityapp.app"
        )

        container.loadPersistentStores { description, error in
            if let error = error {
                fatalError("CoreData store failed to load: \\(error)")
            }
        }

        return container
    }()

    // All entities are encrypted before saving
    func save<T: EncryptableEntity>(_ entity: T) throws {
        let context = persistentContainer.viewContext

        // Encrypt entity data
        let encryptedData = try EncryptionService.shared.encrypt(
            entity.toData(),
            associatedData: entity.id.uuidString.data(using: .utf8)
        )

        entity.encryptedData = encryptedData.combined

        try context.save()

        // HIPAA Audit: Log PHI write
        AuditLogger.shared.log(.phiWrite, metadata: [
            "entityType": String(describing: T.self),
            "entityID": entity.id.uuidString
        ])
    }
}
```

---

## 10. Threat Model

### 10.1 Threat Actors

| Threat Actor | Motivation | Capability | Mitigation |
|--------------|------------|------------|------------|
| Malicious insider | Data theft, sabotage | High | RBAC, audit logging, least privilege |
| External attacker | Data breach, ransomware | Medium-High | Encryption, TLS, certificate pinning |
| Curious user | Unauthorized access to others' data | Low | Access control, authentication |
| Lost/stolen device | Device compromise | Medium | Full-disk encryption, biometric lock |
| Malware | Data exfiltration | Medium | Jailbreak detection, code signing |

### 10.2 Attack Scenarios

**Scenario 1: Stolen Device**
- **Attack**: Attacker gains physical access to unlocked device
- **Mitigations**:
  - ✅ 15-minute auto-logout on inactivity
  - ✅ Biometric re-authentication for sensitive operations
  - ✅ Hardware-backed encryption keys (inaccessible without biometric)
  - ✅ Remote wipe capability

**Scenario 2: Man-in-the-Middle Attack**
- **Attack**: Attacker intercepts network traffic
- **Mitigations**:
  - ✅ TLS 1.3 encryption
  - ✅ Certificate pinning
  - ✅ No sensitive data in URL parameters
  - ✅ Short-lived session tokens

**Scenario 3: Jailbroken Device**
- **Attack**: Attacker bypasses iOS security to access app data
- **Mitigations**:
  - ✅ Jailbreak detection on app launch
  - ✅ Refuse to run on jailbroken devices
  - ✅ Additional runtime integrity checks
  - ✅ Log jailbreak detection events

**Scenario 4: Insider Threat**
- **Attack**: Malicious employee accesses patient data
- **Mitigations**:
  - ✅ Role-based access control
  - ✅ Minimum necessary principle
  - ✅ Comprehensive audit logging
  - ✅ Separation of duties
  - ✅ Background checks

**Scenario 5: SQL Injection / Data Tampering**
- **Attack**: Attacker modifies database records
- **Mitigations**:
  - ✅ CoreData (ORM) prevents SQL injection
  - ✅ SHA-256 integrity checks on critical data
  - ✅ Digital signatures on audit logs
  - ✅ Tamper detection mechanisms

---

## 11. Security Testing Strategy

### 11.1 Automated Testing

```swift
// EncryptionTests.swift
class EncryptionTests: XCTestCase {
    // HIPAA Compliance: Verify AES-256 encryption

    func testAES256Encryption() throws {
        let service = EncryptionService()
        let plaintext = "Sensitive PHI data".data(using: .utf8)!

        // Encrypt
        let encrypted = try service.encrypt(plaintext, associatedData: nil)

        // Verify ciphertext is different from plaintext
        XCTAssertNotEqual(encrypted.ciphertext, plaintext)

        // Decrypt
        let decrypted = try service.decrypt(encrypted, associatedData: nil)

        // Verify decryption produces original plaintext
        XCTAssertEqual(decrypted, plaintext)
    }

    func testEncryptionWithAssociatedData() throws {
        let service = EncryptionService()
        let plaintext = "PHI".data(using: .utf8)!
        let associatedData = "user-123".data(using: .utf8)!

        let encrypted = try service.encrypt(plaintext, associatedData: associatedData)

        // Decryption with correct associated data succeeds
        let decrypted = try service.decrypt(encrypted, associatedData: associatedData)
        XCTAssertEqual(decrypted, plaintext)

        // Decryption with wrong associated data fails
        let wrongAssociatedData = "user-456".data(using: .utf8)!
        XCTAssertThrowsError(try service.decrypt(encrypted, associatedData: wrongAssociatedData))
    }
}
```

### 11.2 Penetration Testing Checklist

- [ ] OWASP Mobile Top 10 testing
- [ ] Jailbreak bypass attempts
- [ ] Certificate pinning bypass
- [ ] Keychain extraction attempts
- [ ] Memory dump analysis
- [ ] Network traffic analysis
- [ ] Authentication bypass testing
- [ ] Session fixation attacks
- [ ] SQL injection testing (CoreData)
- [ ] XSS testing (WebView, if used)

---

## 12. Incident Response

### 12.1 Security Incident Classification

| Severity | Description | Response Time | Notification |
|----------|-------------|---------------|--------------|
| **Critical** | Data breach, system compromise | Immediate | CISO, Legal, Users |
| **High** | Unauthorized access, malware | 1 hour | CISO, Security Team |
| **Medium** | Failed login attempts, anomalies | 4 hours | Security Team |
| **Low** | Policy violations, minor issues | 24 hours | Security Team |

### 12.2 Breach Notification Timeline (HIPAA)

```
Day 0: Breach Discovered
  ↓
Day 0-1: Assess and contain
  ↓
Day 1-2: Determine if breach affects 500+ individuals
  ↓
Day 2-60: Notify affected individuals (< 60 days)
  ↓
Day 60: Notify HHS Secretary (if 500+)
  ↓
Day 365: Annual report to HHS (breaches < 500)
```

---

## 13. Compliance Maintenance

### 13.1 Ongoing Activities

**Daily:**
- Automated security scans
- Log monitoring and analysis

**Weekly:**
- Manual audit log review
- Vulnerability scan review

**Monthly:**
- Access rights review
- Security patch deployment

**Quarterly:**
- Risk assessment
- Compliance audit
- Disaster recovery testing

**Annually:**
- Penetration testing
- HIPAA security assessment
- Business continuity plan review
- Encryption key rotation

---

**Document Version:** 1.0
**Last Updated:** November 10, 2025
**Next Review:** February 10, 2026
**Owner:** Chief Security Officer
