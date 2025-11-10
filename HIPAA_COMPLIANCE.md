# HIPAA Compliance Guide - Therapist.Me

## Overview

This document outlines how Therapist.Me complies with the Health Insurance Portability and Accountability Act (HIPAA) Privacy Rule and Security Rule requirements.

## Table of Contents

1. [HIPAA Security Rule Compliance](#hipaa-security-rule-compliance)
2. [HIPAA Privacy Rule Compliance](#hipaa-privacy-rule-compliance)
3. [Technical Safeguards](#technical-safeguards)
4. [Administrative Safeguards](#administrative-safeguards)
5. [Physical Safeguards](#physical-safeguards)
6. [Audit Controls](#audit-controls)
7. [Breach Notification](#breach-notification)
8. [Testing and Validation](#testing-and-validation)

---

## HIPAA Security Rule Compliance

### Required Implementation Specifications

#### 1. Access Control (§164.312(a)(1))

**Unique User Identification**
- ✅ Each user has a unique UUID
- ✅ Biometric authentication (Face ID/Touch ID)
- ✅ No shared accounts permitted

**Emergency Access Procedure**
- ✅ Implemented in `SecurityManager.swift`
- ✅ Emergency access codes with audit logging
- ✅ Documented emergency access procedures

**Automatic Logoff**
- ✅ Session timeout after 15 minutes of inactivity
- ✅ Implemented in `SessionManager.swift`
- ✅ Configurable timeout period

**Encryption and Decryption**
- ✅ AES-256-GCM encryption for all PHI
- ✅ Implemented in `EncryptionService.swift`
- ✅ Key management via iOS Keychain/Secure Enclave

#### 2. Audit Controls (§164.312(b))

**Implementation**
- ✅ Comprehensive audit logging in `AuditLogger.swift`
- ✅ Tamper-proof audit logs with cryptographic hashing
- ✅ Logs all PHI access, modifications, and deletions
- ✅ Timestamps, user IDs, and event details recorded

**What We Log**
```
- User authentication events
- PHI access (read operations)
- PHI modifications (create, update, delete)
- Security events (failed logins, integrity checks)
- System events (app launch, background, termination)
- Emergency access requests
```

#### 3. Integrity (§164.312(c)(1))

**Mechanism to Authenticate ePHI**
- ✅ SHA-256 cryptographic hashing
- ✅ Hash verification before data access
- ✅ Integrity checks in `EncryptionService.swift`
- ✅ Tamper detection and logging

**Implementation**
```swift
// Data integrity verification
func verifyIntegrity(data: Data, expectedHash: String) -> Bool {
    let actualHash = generateHash(for: data)
    if actualHash != expectedHash {
        AuditLogger.shared.log(
            event: .integrityCheckFailed,
            severity: .critical
        )
        return false
    }
    return true
}
```

#### 4. Person or Entity Authentication (§164.312(d))

**Implementation**
- ✅ Biometric authentication (Face ID/Touch ID)
- ✅ Device-based passcode authentication
- ✅ Session tokens stored in Keychain
- ✅ Implemented in `SessionManager.swift`

#### 5. Transmission Security (§164.312(e)(1))

**Integrity Controls**
- ✅ TLS 1.3 for all network communications
- ✅ Certificate pinning for API connections
- ✅ End-to-end encryption

**Encryption**
- ✅ Data encrypted before transmission
- ✅ HTTPS-only communications
- ✅ No PHI transmitted in URLs or headers

---

## HIPAA Privacy Rule Compliance

### Minimum Necessary Standard

**Implementation**
- ✅ Users can only access their own data
- ✅ Role-based access control (when applicable)
- ✅ Data minimization in collection
- ✅ Limited data retention periods

### Individual Rights

#### Right of Access (§164.524)
**Implementation**
- ✅ Users can view all their data in the app
- ✅ Export functionality to download data
- ✅ Response within 30 days (immediate for app data)

**Code Location**: `ProfileView.swift` - Export My Data feature

#### Right to Request Amendment (§164.526)
**Implementation**
- ✅ Users can edit their profile information
- ✅ Journal and mood entries can be modified
- ✅ All modifications are logged in audit trail

#### Right to Accounting of Disclosures (§164.528)
**Implementation**
- ✅ Audit logs track all data access
- ✅ Users can request disclosure history
- ✅ 6-year retention of audit logs

**Code Location**: `AuditLogger.swift` - retrieveLogs() method

#### Right to Request Restrictions (§164.522)
**Implementation**
- ✅ Privacy settings to control data collection
- ✅ Optional features can be disabled
- ✅ Analytics can be opted out

#### Right to Confidential Communications (§164.522(b))
**Implementation**
- ✅ No PHI in push notifications
- ✅ Generic notification messages only
- ✅ Notification preferences in settings

### Notice of Privacy Practices

**Implementation**
- ✅ Privacy Policy presented during onboarding
- ✅ HIPAA Notice of Privacy Practices acceptance required
- ✅ Available anytime in app settings
- ✅ Updates notified to users

**Code Location**: `OnboardingCoordinatorView.swift` - PrivacyConsentView

---

## Technical Safeguards

### Encryption Implementation

#### Data at Rest
```swift
// AES-256-GCM Encryption
EncryptionService.shared.encrypt(data)
- Algorithm: AES-256-GCM
- Key Size: 256 bits
- Key Storage: iOS Keychain (Secure Enclave when available)
- Unique keys per user
```

#### Data in Transit
- TLS 1.3 minimum
- Perfect Forward Secrecy (PFS)
- Certificate validation
- No mixed content

#### Key Management
```
- Encryption keys generated on device
- Stored in iOS Keychain with highest security
- Accessibility: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
- Key rotation capability implemented
- Keys never leave the device unencrypted
```

### Access Control Matrix

| User Role | PHI Access | Modify Own Data | Export Data | Delete Account |
|-----------|------------|-----------------|-------------|----------------|
| User      | Own Only   | ✅              | ✅          | ✅             |
| Emergency | Read Only  | ❌              | ❌          | ❌             |

### Authentication Flow

```
1. App Launch
   ↓
2. Check for existing session
   ↓
3. If expired → Request biometric authentication
   ↓
4. Validate with LAContext (LocalAuthentication)
   ↓
5. On success → Start new session
   ↓
6. Set 15-minute inactivity timeout
   ↓
7. Monitor activity and auto-lock if needed
```

---

## Administrative Safeguards

### Security Management Process

**Risk Analysis**
- Regular security assessments
- Vulnerability scanning
- Penetration testing recommendations
- Third-party security audits

**Risk Management**
- Identified risks documented
- Mitigation strategies implemented
- Regular review and updates

**Sanction Policy**
- Violations of privacy/security policies result in:
  - Account suspension
  - Legal action if warranted
  - Reporting to authorities

**Information System Activity Review**
- Audit log review procedures
- Automated anomaly detection
- Regular compliance reviews

### Workforce Training (for Development Team)

**Required Training**
- HIPAA Privacy and Security Rules
- PHI handling procedures
- Incident response protocols
- Secure coding practices

### Contingency Planning

**Data Backup**
- Optional encrypted iCloud backup
- Local device storage
- Backup encryption with same standards

**Disaster Recovery**
- Data can be restored from backup
- Multiple recovery methods
- Tested recovery procedures

**Emergency Mode Operation**
- Emergency access procedures
- Crisis support always available
- Offline functionality maintained

---

## Physical Safeguards

### Device and Media Controls

**Disposal**
```swift
// Secure data deletion
SecureStorageService.shared.deleteAllData(userId: userId)
- Overwrites data with random bytes before deletion
- Multiple overwrite passes
- File system deletion
- Keychain cleanup
```

**Media Re-use**
- Data must be securely erased before device sale/transfer
- Account deletion removes all local data
- Cloud data deletion within 30 days

**Accountability**
- Device-specific identifiers
- User cannot access data from other devices without credentials
- Data tied to user account and device

---

## Audit Controls

### Events Logged

```swift
enum AuditEvent {
    // Authentication
    case loginAttempt
    case loginSuccess
    case loginFailed
    case logoutPerformed
    case biometricAuthSuccess
    case biometricAuthFailed

    // PHI Access
    case phiAccessed
    case phiModified
    case phiCreated
    case phiDeleted
    case phiExported

    // Security
    case encryptionKeyGenerated
    case encryptionKeyRotated
    case integrityCheckFailed
    case unauthorizedAccess
    case sessionExpired

    // System
    case appLaunched
    case appBackgrounded
    case appTerminated
}
```

### Audit Log Format

```json
{
  "id": "UUID",
  "timestamp": "ISO8601 DateTime",
  "event": "Event Type",
  "details": "Description",
  "userId": "User UUID (if applicable)",
  "severity": "LOW | MEDIUM | HIGH | CRITICAL",
  "deviceInfo": {
    "model": "Device Model",
    "systemVersion": "iOS Version",
    "identifier": "Device ID"
  },
  "appVersion": "App Version"
}
```

### Log Retention

- **Minimum**: 6 years (HIPAA requirement)
- **Storage**: Encrypted on device and cloud
- **Access**: Available for compliance review
- **Integrity**: Cryptographic hash verification

---

## Breach Notification

### Breach Detection

**Automated Monitoring**
- Integrity check failures
- Multiple failed authentication attempts
- Unauthorized access attempts
- Unusual data access patterns

**Manual Review**
- Regular audit log review
- Security incident reports
- User-reported issues

### Breach Response Plan

**Discovery Phase** (0-24 hours)
1. Identify the breach
2. Stop ongoing breach
3. Secure affected systems
4. Preserve evidence

**Assessment Phase** (24-72 hours)
1. Determine scope of breach
2. Identify affected users
3. Assess risk to PHI
4. Determine if notification required

**Notification Phase** (within 60 days)
1. Notify affected individuals
2. Notify HHS if affecting 500+ users
3. Notify media if affecting 500+ users in a state
4. Document all actions taken

### Notification Content

Required information:
- Brief description of breach
- Types of PHI involved
- Steps individuals should take
- What we're doing to investigate
- Contact information for questions

---

## Testing and Validation

### Security Testing Checklist

#### Encryption Testing
- [ ] Verify AES-256 encryption for all PHI
- [ ] Test encryption key generation
- [ ] Validate key storage in Keychain
- [ ] Test data decryption
- [ ] Verify encryption of backups

#### Authentication Testing
- [ ] Test biometric authentication
- [ ] Test passcode fallback
- [ ] Verify session timeout (15 minutes)
- [ ] Test emergency access
- [ ] Validate session token security

#### Audit Logging Testing
- [ ] Verify all PHI access is logged
- [ ] Test log integrity (hash verification)
- [ ] Validate timestamp accuracy
- [ ] Test log retrieval
- [ ] Verify log encryption

#### Access Control Testing
- [ ] Test user isolation (cannot access other users' data)
- [ ] Verify automatic logoff
- [ ] Test emergency access procedures
- [ ] Validate permission system

#### Integrity Testing
- [ ] Test hash generation
- [ ] Verify integrity check on data read
- [ ] Test tamper detection
- [ ] Validate alert on integrity failure

### Penetration Testing Recommendations

**Annual Testing Should Include:**
- Authentication bypass attempts
- Encryption vulnerability assessment
- SQL injection testing (if applicable)
- API security testing
- Session management testing
- Input validation testing
- Data leakage assessment

### Compliance Validation

**Regular Reviews:**
- Quarterly: Access control effectiveness
- Semi-annually: Encryption key rotation
- Annually: Full HIPAA compliance audit
- As needed: Post-incident reviews

---

## Code References

### Security Services Location

```
TherapistMe/
├── Services/
│   └── Security/
│       ├── EncryptionService.swift      # AES-256 encryption
│       ├── KeychainService.swift        # Secure key storage
│       ├── AuditLogger.swift            # Tamper-proof logging
│       ├── SecureStorageService.swift   # Encrypted PHI storage
│       ├── SessionManager.swift         # Session timeout & auth
│       └── SecurityManager.swift        # Central security control
```

### HIPAA-Critical Functions

**PHI Encryption** (`EncryptionService.swift:45`)
```swift
func encrypt(_ data: Data) -> Data?
```

**Audit Logging** (`AuditLogger.swift:78`)
```swift
func log(event: AuditEvent, details: String, userId: String?, severity: AuditSeverity)
```

**Session Timeout** (`SessionManager.swift:112`)
```swift
func expireSession()
```

**Data Integrity** (`EncryptionService.swift:152`)
```swift
func verifyIntegrity(data: Data, expectedHash: String) -> Bool
```

---

## Compliance Checklist

### Privacy Rule
- [x] Notice of Privacy Practices provided
- [x] Individual rights implemented
- [x] Minimum necessary standard applied
- [x] Accounting of disclosures available
- [x] Business Associate Agreements (for cloud providers)

### Security Rule - Administrative
- [x] Security Management Process
- [x] Workforce training requirements
- [x] Contingency planning
- [x] Evaluation procedures

### Security Rule - Physical
- [x] Facility access controls (device-based)
- [x] Workstation security (device security)
- [x] Device and media controls

### Security Rule - Technical
- [x] Access control
- [x] Audit controls
- [x] Integrity controls
- [x] Person/entity authentication
- [x] Transmission security

### Breach Notification Rule
- [x] Breach detection procedures
- [x] Risk assessment process
- [x] Notification procedures (60-day)
- [x] Documentation requirements

---

## Contact Information

**HIPAA Compliance Officer**
Email: hipaa@therapist.me
Phone: [Phone Number]

**Security Team**
Email: security@therapist.me

**For Reporting Security Issues**
Email: security-report@therapist.me
PGP Key: [Key ID]

---

**Document Version**: 1.0
**Last Updated**: [Date]
**Next Review Date**: [Date + 1 year]
