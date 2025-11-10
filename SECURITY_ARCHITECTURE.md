# Security Architecture Design
**Mental Health/Addiction Recovery iOS Application**

**Version:** 1.0
**Date:** 2025-11-10
**Status:** Design Phase
**Classification:** Internal - Security Architecture

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Overview](#2-system-overview)
3. [Security Principles](#3-security-principles)
4. [Architecture Layers](#4-architecture-layers)
5. [Data Security](#5-data-security)
6. [Authentication & Authorization](#6-authentication--authorization)
7. [Network Security](#7-network-security)
8. [Audit & Monitoring](#8-audit--monitoring)
9. [Privacy Controls](#9-privacy-controls)
10. [Threat Model](#10-threat-model)
11. [Security Components](#11-security-components)
12. [Deployment Architecture](#12-deployment-architecture)

---

## 1. Executive Summary

### 1.1 Purpose

This document defines the security architecture for a HIPAA-compliant mental health and addiction recovery iOS application. The application handles Protected Health Information (PHI) and must implement comprehensive security controls to protect user privacy and comply with regulatory requirements.

### 1.2 Scope

This architecture covers:
- iOS mobile application (primary focus)
- Backend API services (overview)
- Data storage and encryption
- Network communication
- Authentication and authorization
- Audit logging and monitoring
- Privacy controls

### 1.3 Compliance Requirements

- **HIPAA Security Rule** (45 CFR §164.312)
- **HIPAA Privacy Rule** (45 CFR §164.502)
- **HITECH Act** breach notification
- **Apple App Store** privacy requirements
- **iOS Security Best Practices**
- **OWASP Mobile Top 10**
- **NIST Cybersecurity Framework**

### 1.4 Security Objectives

| Objective | Description | Priority |
|-----------|-------------|----------|
| **Confidentiality** | Protect PHI from unauthorized access | CRITICAL |
| **Integrity** | Prevent unauthorized modification of PHI | CRITICAL |
| **Availability** | Ensure authorized users can access PHI when needed | HIGH |
| **Accountability** | Track all PHI access and modifications | CRITICAL |
| **Privacy** | Minimize data collection and respect user rights | CRITICAL |

---

## 2. System Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         iOS APPLICATION                          │
│                     (Primary Security Boundary)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Presentation │  │   Business   │  │   Security   │         │
│  │    Layer     │◄─┤    Logic     │◄─┤   Services   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                  │                  │                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  ViewModels  │  │ Data Models  │  │  Encryption  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                  │                  │                 │
│  ┌──────────────────────────────────────────────────┐         │
│  │            Storage & Persistence Layer           │         │
│  │  (Encrypted Core Data, Keychain, File Storage)   │         │
│  └──────────────────────────────────────────────────┘         │
│                           │                                     │
└───────────────────────────┼─────────────────────────────────────┘
                            │ TLS 1.3 + Certificate Pinning
                            │ Encrypted & Authenticated
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND API SERVICES                         │
│                   (Secondary Security Boundary)                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   API        │  │ Authentication│  │   Database   │         │
│  │  Gateway     │  │   Service     │  │  (Encrypted) │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Audit Log    │  │  Business     │  │  File        │         │
│  │  Service     │  │  Logic        │  │  Storage     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Trust Boundaries

**Primary Trust Boundary:** iOS Application
- User's device is considered trusted (with caveats for jailbroken devices)
- All PHI stored on device must be encrypted
- App controls all data access on device

**Secondary Trust Boundary:** Backend Services
- Backend infrastructure is trusted (cloud provider with BAA)
- All data in backend must be encrypted at rest
- Network between app and backend is untrusted (requires encryption)

**Untrusted Zones:**
- Network communication paths
- Third-party services without BAAs
- User's clipboard
- iOS backups (unless encrypted by user)
- Screenshots and screen recordings

### 2.3 Data Flow

```
User Input → Validation → Encryption → Local Storage
                                    → Network Transmission → Backend

User Request → Authentication → Authorization → Audit Log → Data Retrieval
            → Decryption → Display
```

---

## 3. Security Principles

### 3.1 Defense in Depth

Implement multiple layers of security controls:

1. **Application Layer:** Input validation, output encoding, secure coding
2. **Authentication Layer:** MFA, biometric, strong passwords
3. **Authorization Layer:** Role-based access control, least privilege
4. **Data Layer:** Encryption at rest, secure storage
5. **Network Layer:** TLS 1.3, certificate pinning, request signing
6. **Device Layer:** File protection, keychain, secure enclave
7. **Audit Layer:** Comprehensive logging, monitoring, alerting

### 3.2 Least Privilege

- Users and processes have minimum necessary permissions
- Default to deny access; explicitly grant only what's needed
- Separate duties and limit administrative access
- Regular access reviews

### 3.3 Fail Securely

- Errors don't expose sensitive information
- Failed authentication denies access (no fallback)
- Certificate pinning failures abort connection
- Encryption failures prevent data storage

### 3.4 Privacy by Design

- Collect only necessary PHI (data minimization)
- Obtain explicit user consent
- Provide granular privacy controls
- Support user rights (access, deletion, portability)
- Anonymize data when possible

### 3.5 Zero Trust

- Verify every request, even from authenticated users
- Never trust, always verify
- Assume breach mentality
- Continuous authentication and authorization

### 3.6 Secure by Default

- All features secure out of the box
- No insecure options or backdoors
- Strong security settings by default
- Users can't weaken security

---

## 4. Architecture Layers

### 4.1 Presentation Layer

**Purpose:** User interface and user experience

**Security Controls:**
- Input validation at point of entry
- Output encoding to prevent injection
- Screen masking for sensitive data
- Auto-lock/timeout on inactivity
- Disable screenshots for sensitive screens
- No sensitive data in notifications
- No sensitive data in app switcher preview

**Components:**
- SwiftUI Views
- UIKit View Controllers
- View Models (MVVM pattern)
- Navigation Controllers
- UI Components

### 4.2 Business Logic Layer

**Purpose:** Application logic and data processing

**Security Controls:**
- Authorization checks before all operations
- Data validation beyond input validation
- Secure data processing (no PHI in memory longer than necessary)
- Error handling without information disclosure
- Audit logging for all PHI operations

**Components:**
- ViewModels
- Services
- Use Cases
- Business Rules
- Validation Logic

### 4.3 Data Access Layer

**Purpose:** Data persistence and retrieval

**Security Controls:**
- Encrypted storage (AES-256)
- Prepared statements (prevent SQL injection)
- Access control enforcement
- Secure deletion
- Backup exclusion for PHI

**Components:**
- Core Data Stack (encrypted)
- Repository Pattern
- Data Access Objects (DAOs)
- Query Builders
- Migration Handlers

### 4.4 Security Services Layer

**Purpose:** Cross-cutting security functions

**Security Controls:**
- Centralized encryption/decryption
- Key management
- Authentication and authorization
- Audit logging
- Certificate pinning
- Session management

**Components:**
- `EncryptionService`
- `KeyManager`
- `KeychainManager`
- `AuthenticationService`
- `AuthorizationService`
- `AuditLogger`
- `NetworkSecurityManager`

---

## 5. Data Security

### 5.1 Data Classification

| Classification | Examples | Storage | Transmission | Retention |
|----------------|----------|---------|--------------|-----------|
| **PHI - High Sensitivity** | Journal entries, mood data, medications, health assessments | Encrypted, keychain-protected | TLS 1.3 + additional encryption layer | 7 years |
| **PHI - Medium Sensitivity** | Name, email, DOB | Encrypted | TLS 1.3 | 7 years |
| **Authentication Data** | Passwords (hashed), tokens, MFA secrets | Keychain only, never in database | TLS 1.3 | Until user deletion |
| **Audit Logs** | Access logs, security events | Encrypted, append-only | TLS 1.3 | 6+ years (HIPAA) |
| **Non-PHI** | App preferences, UI settings | Standard storage | TLS 1.3 | As needed |

### 5.2 Encryption at Rest

**Standard:** AES-256-GCM

**Implementation:**

1. **Core Data / SQLite Database**
   ```swift
   // Use SQLCipher or iOS 17+ native encryption
   - Encryption: AES-256
   - Key derivation: PBKDF2 (100,000+ iterations) or Argon2
   - File protection: NSFileProtectionComplete
   - Exclude from backups: Yes
   ```

2. **File Storage**
   ```swift
   // Encrypted file storage for attachments
   - Per-file encryption with unique keys
   - File protection attribute: .complete
   - Secure file names (no PHI in filename)
   - Exclude from backups: Yes
   ```

3. **Keychain**
   ```swift
   // Credentials, tokens, encryption keys
   - Accessibility: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
   - Biometric protection: kSecAccessControlBiometryCurrentSet
   - No iCloud sync: kSecAttrSynchronizable = false
   ```

4. **Memory**
   ```swift
   // Sensitive data in memory
   - Zero out after use
   - Avoid string interpolation with PHI
   - Use Data instead of String for sensitive data
   - Minimize PHI lifetime in memory
   ```

### 5.3 Encryption in Transit

**Standard:** TLS 1.3 (minimum TLS 1.2)

**Implementation:**

```swift
// URLSession configuration
let configuration = URLSessionConfiguration.ephemeral
configuration.tlsMinimumSupportedProtocolVersion = .TLSv13
configuration.tlsMaximumSupportedProtocolVersion = .TLSv13

// Certificate pinning
let evaluator = PinnedCertificatesTrustEvaluator(
    certificates: pinnedCertificates,
    acceptSelfSignedCertificates: false,
    performDefaultValidation: true,
    validateHost: true
)

// Strong cipher suites
- TLS_AES_256_GCM_SHA384
- TLS_CHACHA20_POLY1305_SHA256
- TLS_AES_128_GCM_SHA256

// No fallback to HTTP
NSAppTransportSecurity: NSAllowsArbitraryLoads = false
```

### 5.4 Key Management

**Key Hierarchy:**

```
Device Key (Secure Enclave)
    └── Master Key (Keychain, biometric-protected)
        ├── Database Encryption Key
        ├── File Encryption Keys (per-file)
        └── Network Encryption Keys

Authentication Keys (Separate, Keychain)
    ├── JWT Signing Key
    ├── MFA Secrets (TOTP)
    └── API Authentication Keys
```

**Key Lifecycle:**

1. **Generation**
   - Use iOS CryptoKit or Security framework
   - Derive from device-specific entropy
   - 256-bit key size minimum

2. **Storage**
   - Store in Keychain with biometric protection
   - Use Secure Enclave when possible
   - Never store in UserDefaults or files

3. **Usage**
   - Retrieve only when needed
   - Zero out from memory after use
   - Never log or transmit keys

4. **Rotation**
   - Rotate every 90-180 days
   - Automatic rotation triggered by policy
   - Re-encrypt data with new key
   - Securely delete old keys

5. **Deletion**
   - Secure deletion on user account deletion
   - Zero out memory before deletion
   - Verify key unrecoverable

---

## 6. Authentication & Authorization

### 6.1 Authentication Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Authentication Flow                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  User Credentials (Email + Password)                    │
│         │                                                │
│         ▼                                                │
│  Password Validation                                    │
│  - Complexity check                                     │
│  - Hash comparison (Argon2 or bcrypt)                   │
│         │                                                │
│         ▼                                                │
│  Multi-Factor Authentication (MFA)                      │
│  - SMS/Email OTP or TOTP                                │
│  - Time-limited code (5-10 minutes)                     │
│         │                                                │
│         ▼                                                │
│  Biometric Authentication (Optional)                    │
│  - Face ID / Touch ID                                   │
│  - Local authentication only                            │
│         │                                                │
│         ▼                                                │
│  Token Generation                                       │
│  - Access Token (JWT, 15-30 min expiry)                 │
│  - Refresh Token (7-30 days expiry)                     │
│  - Store in Keychain (biometric-protected)              │
│         │                                                │
│         ▼                                                │
│  Session Establishment                                  │
│  - Create session record                                │
│  - Set inactivity timeout (15-30 min)                   │
│  - Audit log: successful login                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Authentication Components

**Password Policy:**
```swift
- Minimum length: 12 characters
- Complexity: uppercase + lowercase + number + special char
- No common passwords (dictionary check)
- No reuse of last 12 passwords
- Optional expiration: 90 days
- Account lockout: 5 failed attempts = 30-minute lockout
```

**Multi-Factor Authentication:**
```swift
- Primary: Email/Password
- Secondary: SMS OTP or TOTP (Google Authenticator)
- Fallback: Email OTP
- Biometric: Face ID/Touch ID (local device only)
```

**Token Management:**
```swift
// Access Token (JWT)
{
  "sub": "user_uuid",
  "iat": 1699999999,
  "exp": 1700001799,  // 30 minutes
  "jti": "token_uuid",
  "roles": ["user"],
  "iss": "therapist-me-api",
  "aud": "therapist-me-ios"
}

// Refresh Token
{
  "sub": "user_uuid",
  "exp": 1702591999,  // 30 days
  "jti": "refresh_uuid",
  "type": "refresh"
}

// Storage
- Store in Keychain with kSecAttrAccessibleWhenUnlockedThisDeviceOnly
- Protect with biometric requirement
- Never transmit refresh token except for rotation
```

**Session Management:**
```swift
- Inactivity timeout: 15-30 minutes
- Absolute timeout: 8-12 hours
- Concurrent session limit: 3 devices
- Force logout on password change
- Logout on all devices capability
```

### 6.3 Authorization Architecture

**Role-Based Access Control (RBAC):**

```swift
enum UserRole {
    case user           // Standard user
    case premium        // Premium subscriber
    case therapist      // Licensed therapist (if applicable)
    case admin          // Administrator
}

// Permissions tied to roles
- User: Read/write own data only
- Premium: Extended features
- Therapist: Read assigned patient data (if applicable)
- Admin: User management, system configuration
```

**Attribute-Based Access Control (ABAC) for Sensitive Data:**

```swift
// Example: Journal entry access
if currentUser.id == journalEntry.ownerId {
    // Allow access
} else if currentUser.role == .therapist
       && currentUser.assignedPatients.contains(journalEntry.ownerId)
       && journalEntry.sharedWithTherapist == true {
    // Allow therapist access if explicitly shared
} else {
    // Deny access
}
```

**Authorization Enforcement:**

```swift
// Check authorization before every PHI access
func accessJournalEntry(_ entryId: UUID) throws -> JournalEntry {
    // 1. Authenticate: Ensure valid session
    guard let currentUser = sessionManager.currentUser else {
        throw AuthError.notAuthenticated
    }

    // 2. Authorize: Check permissions
    let entry = try dataStore.fetchJournalEntry(entryId)
    guard authorizationService.canAccess(currentUser, entry) else {
        // Audit log: unauthorized access attempt
        auditLogger.logUnauthorizedAccess(user: currentUser, resource: entry)
        throw AuthError.notAuthorized
    }

    // 3. Audit log: successful access
    auditLogger.logPHIAccess(user: currentUser, resource: entry, action: .read)

    return entry
}
```

---

## 7. Network Security

### 7.1 Network Architecture

```
┌──────────────────────────────────────────────────────┐
│              iOS App (TrustKit)                       │
└───────────────────┬──────────────────────────────────┘
                    │
                    │ TLS 1.3
                    │ Certificate Pinning
                    │ Request Signing (HMAC-SHA256)
                    │
                    ▼
┌──────────────────────────────────────────────────────┐
│           Load Balancer / CDN (TLS Termination)       │
│           - DDoS Protection                           │
│           - Rate Limiting                             │
└───────────────────┬──────────────────────────────────┘
                    │
                    │ Internal TLS
                    │
                    ▼
┌──────────────────────────────────────────────────────┐
│               API Gateway                             │
│           - Authentication                            │
│           - Authorization                             │
│           - Request Validation                        │
│           - Response Sanitization                     │
└───────────────────┬──────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────┐
│           Backend Microservices                       │
│           - User Service                              │
│           - Journal Service                           │
│           - Auth Service                              │
│           - Audit Service                             │
└──────────────────────────────────────────────────────┘
```

### 7.2 Certificate Pinning

**Strategy:** Pin both leaf and intermediate certificates with backups

```swift
// TrustKit configuration
let trustKitConfig = [
    kTSKSwizzleNetworkDelegates: false,
    kTSKPinnedDomains: [
        "api.therapist-me.com": [
            kTSKEnforcePinning: true,
            kTSKIncludeSubdomains: true,
            kTSKPublicKeyHashes: [
                // Primary certificate
                "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
                // Backup certificate (for rotation)
                "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
            ],
            kTSKReportUris: ["https://api.therapist-me.com/cert-report"]
        ]
    ]
]

// Monitor certificate expiration
- Alert 90 days before expiration
- Update backup pin before primary expires
- Test pin update in staging first
```

### 7.3 API Security

**Request Security:**

```swift
// Every API request includes:

1. Authentication Header
   Authorization: Bearer <JWT_ACCESS_TOKEN>

2. Request Signing (for sensitive operations)
   X-Signature: HMAC-SHA256(request_body + timestamp + nonce, api_secret)
   X-Timestamp: 1699999999
   X-Nonce: random_uuid

3. Content-Type Validation
   Content-Type: application/json

4. User-Agent
   User-Agent: TherapistMe-iOS/1.0.0 (iOS 17.0; iPhone14,2)

5. Request ID (for tracing)
   X-Request-ID: uuid
```

**Response Validation:**

```swift
// Validate every API response:

1. Status Code Check
   - 200-299: Success
   - 401: Re-authenticate
   - 403: Authorization error
   - 429: Rate limited
   - 500-599: Server error

2. Content-Type Validation
   - Expect: application/json
   - Reject unexpected content types

3. Response Signature (for sensitive data)
   - Verify X-Signature header
   - Ensure response not tampered

4. Schema Validation
   - Validate JSON structure
   - Reject unexpected fields (fail closed)

5. Rate Limiting Respect
   - Honor Retry-After header
   - Implement exponential backoff
```

### 7.4 Offline Mode & Sync

**Security Considerations:**

```swift
// Offline data storage
- All data encrypted at rest
- Sync queue encrypted
- Conflict resolution securely handled
- Sync only over secure connection
- Verify data integrity after sync

// Sync Architecture
1. User creates data offline → Store encrypted locally
2. App comes online → Establish secure connection
3. Authenticate → Verify valid session
4. Upload encrypted data → Server validates and stores
5. Download server changes → Client validates and decrypts
6. Resolve conflicts → Last-write-wins or manual resolution
7. Audit log sync events
```

---

## 8. Audit & Monitoring

### 8.1 Audit Logging Architecture

```
┌───────────────────────────────────────────────────────┐
│                    iOS Application                     │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │          AuditLogger Service                  │    │
│  │  - Log PHI access (view, create, update,     │    │
│  │    delete)                                    │    │
│  │  - Log authentication events                 │    │
│  │  - Log security events                       │    │
│  │  - Never log PHI content (only IDs)          │    │
│  └────────────────────┬─────────────────────────┘    │
│                       │                               │
│                       ▼                               │
│  ┌──────────────────────────────────────────────┐    │
│  │        Encrypted Log Buffer (Memory)          │    │
│  │  - Batch logs for efficiency                 │    │
│  │  - Encrypt before transmission               │    │
│  └────────────────────┬─────────────────────────┘    │
│                       │                               │
└───────────────────────┼───────────────────────────────┘
                        │ TLS 1.3
                        │ Encrypted Payload
                        ▼
┌───────────────────────────────────────────────────────┐
│              Backend Audit Service                     │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │       Log Ingestion & Validation              │    │
│  │  - Authenticate source                       │    │
│  │  - Validate log format                       │    │
│  │  - Decrypt payload                           │    │
│  │  - Enrich with server-side data              │    │
│  └────────────────────┬─────────────────────────┘    │
│                       ▼                               │
│  ┌──────────────────────────────────────────────┐    │
│  │    Append-Only Log Storage (Tamper-Proof)    │    │
│  │  - Encrypted at rest                         │    │
│  │  - Retention: 6+ years                       │    │
│  │  - Indexed for search                        │    │
│  └────────────────────┬─────────────────────────┘    │
│                       │                               │
└───────────────────────┼───────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────┐
│              SIEM / Monitoring System                  │
│  - Real-time anomaly detection                        │
│  - Alerting for suspicious activity                   │
│  - Compliance reporting                               │
│  - Incident investigation                             │
└───────────────────────────────────────────────────────┘
```

### 8.2 Audit Events

**Authentication Events:**
```swift
struct AuthenticationEvent: AuditEvent {
    let timestamp: Date
    let userId: UUID?        // Nil if login failed
    let eventType: AuthEventType  // login, logout, mfa, password_change, etc.
    let outcome: Outcome     // success, failure
    let failureReason: String?
    let deviceId: String
    let ipAddress: String?
    let sessionId: UUID?
}
```

**PHI Access Events:**
```swift
struct PHIAccessEvent: AuditEvent {
    let timestamp: Date
    let userId: UUID
    let resourceType: String    // "journal_entry", "mood_log", etc.
    let resourceId: UUID        // ID only, never content
    let action: AccessAction    // view, create, update, delete, export
    let outcome: Outcome
    let sessionId: UUID
}
```

**Security Events:**
```swift
struct SecurityEvent: AuditEvent {
    let timestamp: Date
    let userId: UUID?
    let eventType: SecurityEventType  // unauthorized_access, policy_violation, etc.
    let severity: Severity      // low, medium, high, critical
    let description: String     // Non-PHI description
    let sourceIP: String?
    let deviceId: String
}
```

### 8.3 Monitoring & Alerting

**Real-Time Alerts:**

```swift
// Alert conditions
- Multiple failed login attempts (5+ in 10 minutes)
- Unauthorized access attempts
- Certificate pinning failures
- Unexpected data access patterns
- Large data exports
- Account lockouts
- Security policy violations
- System errors or crashes

// Alert destinations
- Security team (email, Slack, PagerDuty)
- Automated response (e.g., temporary account lock)
- Incident response team (for critical events)
```

**Metrics to Track:**

```swift
// Security Metrics
- Authentication success/failure rate
- MFA adoption rate
- Session timeout rate
- Certificate pinning failure rate
- API error rates by type
- Data access patterns
- Encryption operation performance

// Compliance Metrics
- Audit log coverage (% of PHI access logged)
- Log retention compliance
- Policy violation count
- Training completion rate
- BAA coverage rate
```

---

## 9. Privacy Controls

### 9.1 Data Minimization

**Principle:** Collect only necessary PHI

```swift
// Example: User profile data
struct UserProfile {
    // Required for functionality
    let userId: UUID                  // ✅ Required: User identification
    let email: String                 // ✅ Required: Authentication, communication
    let encryptedPasswordHash: Data   // ✅ Required: Authentication

    // Necessary for personalization
    var firstName: String?            // ✅ Optional: Personalization
    var lastName: String?             // ✅ Optional: Personalization (AVOID if possible)
    var dateOfBirth: Date?            // ⚠️  Sensitive: Only if necessary for age verification

    // Do NOT collect unless absolutely necessary
    // ❌ SSN: Never needed for app functionality
    // ❌ Full address: Avoid unless required (use zip code only)
    // ❌ Phone number: Only if used for MFA
    // ❌ Race, ethnicity: Avoid unless required for health tracking
}
```

### 9.2 Consent Management

```swift
enum ConsentType {
    case dataCollection        // Consent to collect specific data
    case datasharing          // Consent to share with therapist/others
    case analytics            // Consent for anonymized analytics
    case communications       // Consent for emails/notifications
    case researchParticipation // Consent for research studies
}

struct UserConsent {
    let userId: UUID
    let consentType: ConsentType
    let granted: Bool
    let grantedAt: Date
    let version: String        // Privacy policy version
    let expiresAt: Date?       // Some consents may expire
}

// Granular consent options
- ✅ Users can grant/revoke each consent independently
- ✅ Withdraw consent at any time
- ✅ Re-consent required on policy changes
- ✅ Audit trail of all consent changes
```

### 9.3 User Rights Implementation

**Right to Access:**
```swift
// User can export all their data
func exportUserData() async throws -> ExportPackage {
    // 1. Authenticate user
    // 2. Gather all user data (PHI and non-PHI)
    // 3. Format in human-readable format (JSON + PDF)
    // 4. Encrypt export file
    // 5. Audit log export request
    // 6. Deliver via email or in-app download

    // Include:
    - User profile
    - Journal entries
    - Mood logs
    - Goals and achievements
    - Assessment results
    - Audit log of their own data access
    - All consent records
}
```

**Right to Rectification:**
```swift
// User can correct their data
func updateUserData(_ field: String, value: Any) throws {
    // 1. Authenticate user
    // 2. Authorize (users can only edit their own data)
    // 3. Validate new value
    // 4. Update data
    // 5. Audit log: data amendment
}
```

**Right to Erasure:**
```swift
// User can request account deletion
func deleteUserAccount() async throws {
    // 1. Authenticate user
    // 2. Confirm deletion (require re-authentication)
    // 3. Delete all PHI from all systems:
    //    - Local device storage
    //    - Backend database
    //    - Backups (or mark for deletion)
    //    - Audit logs (retain for compliance, but de-identify)
    // 4. Secure deletion (overwrite, not just unlink)
    // 5. Verify data unrecoverable
    // 6. Audit log: account deletion
    // 7. Send confirmation email

    // Retention exceptions:
    - Audit logs (retain for 6 years per HIPAA, but de-identify user)
    - Financial records (if applicable, per legal requirements)
}
```

**Right to Data Portability:**
```swift
// Export data in standard format
- JSON for structured data
- PDF for human-readable format
- FHIR format for health data (if interoperating with EHRs)
```

### 9.4 Privacy-Preserving Features

**Data Masking:**
```swift
// Mask sensitive data in UI
func maskEmail(_ email: String) -> String {
    // "john.doe@example.com" → "joh***oe@example.com"
    let parts = email.split(separator: "@")
    guard parts.count == 2 else { return email }
    let username = String(parts[0])
    let domain = String(parts[1])

    if username.count > 6 {
        let start = username.prefix(3)
        let end = username.suffix(2)
        return "\(start)***\(end)@\(domain)"
    }
    return email
}

// Mask in journal entry previews
func maskJournalPreview(_ text: String) -> String {
    // Show first 50 characters only in list view
    return String(text.prefix(50)) + "..."
}
```

**Secure Display:**
```swift
// Prevent screenshots of sensitive screens
NotificationCenter.default.addObserver(
    forName: UIApplication.userDidTakeScreenshotNotification,
    object: nil,
    queue: .main
) { _ in
    // Alert user that screenshots may compromise privacy
    // Audit log: screenshot taken
}

// Prevent screen recording
if UIScreen.main.isCaptured {
    // Show privacy overlay
}

// Hide sensitive content in app switcher
NotificationCenter.default.addObserver(
    forName: UIApplication.willResignActiveNotification,
    object: nil,
    queue: .main
) { _ in
    // Show privacy overlay
}
```

---

## 10. Threat Model

### 10.1 Assets to Protect

| Asset | Value | Threats |
|-------|-------|---------|
| PHI (journal entries, mood, health data) | CRITICAL | Unauthorized access, data breach, theft |
| User credentials (passwords, tokens) | CRITICAL | Credential theft, session hijacking |
| Encryption keys | CRITICAL | Key exposure, key theft |
| Audit logs | HIGH | Tampering, deletion, unauthorized access |
| User identity | HIGH | Identity theft, account takeover |
| App integrity | MEDIUM | Malware injection, reverse engineering |

### 10.2 Threat Actors

| Actor | Motivation | Capability | Likelihood |
|-------|------------|------------|------------|
| **Malicious User** | Data theft, privacy violation | Low-Medium | Medium |
| **Insider Threat** | Financial gain, revenge | Medium-High | Low |
| **Organized Crime** | Financial gain, PHI resale | High | Low-Medium |
| **Nation-State** | Espionage, surveillance | Very High | Very Low |
| **Script Kiddie** | Curiosity, reputation | Low | High |
| **Competitor** | Business intelligence | Medium | Low |

### 10.3 Attack Scenarios

#### Scenario 1: Credential Theft via Phishing

**Attack:** Attacker sends phishing email to user, steals credentials

**Mitigations:**
- ✅ MFA required (attacker needs second factor)
- ✅ Biometric authentication (harder to phish)
- ✅ Security awareness training
- ✅ Unusual login detection (alert on new device/location)
- ✅ Audit logging (detect suspicious access)

#### Scenario 2: Man-in-the-Middle (MITM) Attack

**Attack:** Attacker intercepts network traffic to steal data

**Mitigations:**
- ✅ TLS 1.3 encryption (end-to-end encryption)
- ✅ Certificate pinning (prevents MITM with fake certificates)
- ✅ Request/response signing (detects tampering)
- ✅ No HTTP fallback (always encrypted)

#### Scenario 3: Device Theft or Loss

**Attack:** Physical device stolen, attacker attempts to access PHI

**Mitigations:**
- ✅ Encryption at rest (data encrypted, useless without key)
- ✅ Keychain protection (keys require biometric or device passcode)
- ✅ Session timeout (old sessions expire)
- ✅ Remote logout capability (user can logout all devices)
- ✅ File protection attributes (iOS protects files)

#### Scenario 4: Malware Injection

**Attack:** Malware installed on device attempts to steal PHI

**Mitigations:**
- ✅ iOS sandboxing (app data isolated)
- ✅ Keychain protection (malware can't access without biometric)
- ✅ Secure coding (prevent injection vulnerabilities)
- ✅ Code signing (prevent app tampering)
- ✅ Jailbreak detection (warn user of compromised device)

#### Scenario 5: SQL Injection

**Attack:** Attacker exploits database query to access unauthorized data

**Mitigations:**
- ✅ Prepared statements / parameterized queries
- ✅ Input validation
- ✅ Least privilege database access
- ✅ Encrypted database (reduces impact if breached)

#### Scenario 6: Insider Threat

**Attack:** Malicious employee/developer accesses production PHI

**Mitigations:**
- ✅ Least privilege access
- ✅ Separation of duties
- ✅ Audit logging (all access logged)
- ✅ Regular access reviews
- ✅ Background checks (for employees with PHI access)
- ✅ Anomaly detection (unusual access patterns trigger alerts)

#### Scenario 7: API Abuse

**Attack:** Attacker exploits API to exfiltrate data or cause DoS

**Mitigations:**
- ✅ Rate limiting (prevent brute force, DDoS)
- ✅ Authentication required on all endpoints
- ✅ Authorization checks before data access
- ✅ Input validation (prevent injection attacks)
- ✅ API versioning (deprecate insecure versions)
- ✅ Audit logging (detect abuse patterns)

---

## 11. Security Components

### 11.1 Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     Security Services                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐ │
│  │  Encryption   │  │   Keychain    │  │   Key Manager    │ │
│  │   Service     │  │   Manager     │  │                  │ │
│  │               │  │               │  │                  │ │
│  │ - AES-256-GCM │  │ - Store creds │  │ - Generate keys  │ │
│  │ - Encrypt/    │  │ - Store tokens│  │ - Rotate keys    │ │
│  │   Decrypt     │  │ - Store keys  │  │ - Derive keys    │ │
│  │ - HMAC        │  │ - Biometric   │  │                  │ │
│  └───────────────┘  └───────────────┘  └──────────────────┘ │
│                                                               │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐ │
│  │Authentication │  │  Biometric    │  │   Session        │ │
│  │   Service     │  │   Auth Svc    │  │   Manager        │ │
│  │               │  │               │  │                  │ │
│  │ - Login       │  │ - Face ID     │  │ - Create session │ │
│  │ - Logout      │  │ - Touch ID    │  │ - Timeout        │ │
│  │ - MFA         │  │ - Fallback    │  │ - Validate       │ │
│  │ - Password    │  │               │  │                  │ │
│  └───────────────┘  └───────────────┘  └──────────────────┘ │
│                                                               │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐ │
│  │Authorization  │  │ Audit Logger  │  │ Security Event   │ │
│  │   Service     │  │               │  │     Logger       │ │
│  │               │  │               │  │                  │ │
│  │ - RBAC        │  │ - PHI access  │  │ - Security events│ │
│  │ - ABAC        │  │ - Auth events │  │ - Alerts         │ │
│  │ - Permission  │  │ - Data changes│  │ - Anomalies      │ │
│  │   check       │  │ - Transmit    │  │                  │ │
│  └───────────────┘  └───────────────┘  └──────────────────┘ │
│                                                               │
│  ┌───────────────────────────────────┐  ┌──────────────────┐ │
│  │    Network Security Manager       │  │  Certificate     │ │
│  │                                   │  │  Pinning Svc     │ │
│  │ - TLS 1.3 configuration           │  │                  │ │
│  │ - Request signing                 │  │ - Pin validation │ │
│  │ - Response validation             │  │ - Cert rotation  │ │
│  │ - Timeout handling                │  │ - Backup pins    │ │
│  └───────────────────────────────────┘  └──────────────────┘ │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### 11.2 Component Specifications

See `IMPLEMENTATION_GUIDE.md` for detailed component specifications, interfaces, and implementation examples.

---

## 12. Deployment Architecture

### 12.1 iOS App Distribution

```
Developer → Xcode Cloud (CI/CD) → Code Signing → TestFlight (Beta) → App Store

Security Gates:
1. Static Analysis (SwiftLint, SonarQube)
2. Dependency Scan (Snyk, Dependabot)
3. Unit Tests (90%+ coverage for security code)
4. Security Tests (SAST)
5. Code Review (security-focused)
6. Penetration Testing (before production)
7. App Store Review (privacy compliance)
```

### 12.2 Backend Infrastructure

```
iOS App → CDN/Load Balancer → API Gateway → Microservices → Database

Cloud Provider: AWS / Google Cloud / Azure (HIPAA-compliant tier, with BAA)

Security Layers:
- WAF (Web Application Firewall)
- DDoS Protection
- VPC (Virtual Private Cloud) isolation
- Encryption at rest (database, storage)
- Encryption in transit (internal TLS)
- Audit logging (all API calls)
- IAM (Identity and Access Management)
```

---

## 13. Security Testing Strategy

### 13.1 Testing Types

| Type | Frequency | Tools | Coverage |
|------|-----------|-------|----------|
| **Unit Tests** | Every commit | XCTest | 90%+ for security code |
| **Integration Tests** | Every PR | XCTest | Critical flows |
| **SAST** | Every commit | SwiftLint, SonarQube | 100% of code |
| **Dependency Scan** | Daily | Snyk, Dependabot | All dependencies |
| **DAST** | Weekly | OWASP ZAP, Burp Suite | API endpoints |
| **Penetration Test** | Quarterly | Third-party security firm | Full application |
| **Security Audit** | Annually | Third-party auditor | Compliance verification |

### 13.2 Security Test Cases

See `SECURITY_TEST_PLAN.md` for comprehensive security test cases.

---

## 14. Incident Response

### 14.1 Incident Classification

| Severity | Definition | Examples | Response Time |
|----------|------------|----------|---------------|
| **P0 - Critical** | Active data breach or severe vulnerability | PHI exposure, active attack | Immediate (15 min) |
| **P1 - High** | Serious security issue | Auth bypass, encryption failure | 1 hour |
| **P2 - Medium** | Security issue with limited impact | Failed cert pinning, anomaly | 4 hours |
| **P3 - Low** | Minor security concern | Policy violation, suspicious activity | 24 hours |

### 14.2 Incident Response Plan

See `INCIDENT_RESPONSE_PLAN.md` for detailed incident response procedures.

---

## 15. Compliance Attestation

This security architecture addresses the following compliance requirements:

- ✅ HIPAA Security Rule (45 CFR §164.312)
  - Access Control
  - Audit Controls
  - Integrity Controls
  - Authentication
  - Transmission Security

- ✅ HIPAA Privacy Rule (45 CFR §164.502)
  - Minimum necessary standard
  - Individual rights (access, amendment, accounting)
  - Notice of privacy practices

- ✅ HITECH Act
  - Breach notification procedures
  - Business associate agreements

- ✅ OWASP Mobile Top 10
  - M1: Improper Platform Usage
  - M2: Insecure Data Storage
  - M3: Insecure Communication
  - M4: Insecure Authentication
  - M5: Insufficient Cryptography
  - M6: Insecure Authorization
  - M7: Client Code Quality
  - M8: Code Tampering
  - M9: Reverse Engineering
  - M10: Extraneous Functionality

- ✅ NIST Cybersecurity Framework
  - Identify, Protect, Detect, Respond, Recover

---

## Appendix A: Glossary

- **AES-256:** Advanced Encryption Standard with 256-bit key
- **HIPAA:** Health Insurance Portability and Accountability Act
- **PHI:** Protected Health Information
- **TLS:** Transport Layer Security
- **MFA:** Multi-Factor Authentication
- **RBAC:** Role-Based Access Control
- **ABAC:** Attribute-Based Access Control
- **JWT:** JSON Web Token
- **OWASP:** Open Web Application Security Project
- **SAST:** Static Application Security Testing
- **DAST:** Dynamic Application Security Testing

---

## Document Control

**Version:** 1.0
**Status:** Draft - Pre-Development
**Author:** Security Architecture Team
**Reviewers:** Security Official, Privacy Official, Legal Counsel
**Approval:** Pending
**Next Review:** Upon architecture implementation

---

**END OF SECURITY ARCHITECTURE DESIGN**
