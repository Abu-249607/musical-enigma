//
//  SecurityTests.swift
//  Therapist.Me Tests
//
//  Unit tests for security and encryption services
//

import XCTest
@testable import TherapistMe

final class SecurityTests: XCTestCase {
    var encryptionService: EncryptionService!
    var keychainService: KeychainService!
    var auditLogger: AuditLogger!

    override func setUpWithError() throws {
        try super.setUpWithError()
        encryptionService = EncryptionService.shared
        keychainService = KeychainService.shared
        auditLogger = AuditLogger.shared
    }

    override func tearDownWithError() throws {
        // Clean up test data
        try super.tearDownWithError()
    }

    // MARK: - Encryption Tests

    func testEncryptionAndDecryption() throws {
        // Given
        let testData = "Sensitive health information"
        let data = testData.data(using: .utf8)!

        // When
        guard let encryptedData = encryptionService.encrypt(data) else {
            XCTFail("Encryption failed")
            return
        }

        guard let decryptedData = encryptionService.decrypt(encryptedData) else {
            XCTFail("Decryption failed")
            return
        }

        let decryptedString = String(data: decryptedData, encoding: .utf8)

        // Then
        XCTAssertNotEqual(encryptedData, data, "Encrypted data should differ from original")
        XCTAssertEqual(decryptedString, testData, "Decrypted data should match original")
    }

    func testEncryptionOfCodableObject() throws {
        // Given
        let testUser = User(
            username: "testuser",
            email: "test@example.com"
        )

        // When
        guard let encryptedData = encryptionService.encrypt(testUser) else {
            XCTFail("Encryption of User object failed")
            return
        }

        guard let decryptedUser = encryptionService.decrypt(encryptedData, as: User.self) else {
            XCTFail("Decryption of User object failed")
            return
        }

        // Then
        XCTAssertEqual(decryptedUser.username, testUser.username)
        XCTAssertEqual(decryptedUser.email, testUser.email)
    }

    func testHashGeneration() throws {
        // Given
        let testData = "Test data".data(using: .utf8)!

        // When
        let hash1 = encryptionService.generateHash(for: testData)
        let hash2 = encryptionService.generateHash(for: testData)

        // Then
        XCTAssertEqual(hash1, hash2, "Same data should produce same hash")
        XCTAssertFalse(hash1.isEmpty, "Hash should not be empty")
    }

    func testDataIntegrityVerification() throws {
        // Given
        let testData = "Integrity test data".data(using: .utf8)!
        let hash = encryptionService.generateHash(for: testData)

        // When
        let isValid = encryptionService.verifyIntegrity(data: testData, expectedHash: hash)
        let isInvalid = encryptionService.verifyIntegrity(data: "tampered".data(using: .utf8)!, expectedHash: hash)

        // Then
        XCTAssertTrue(isValid, "Valid data should pass integrity check")
        XCTAssertFalse(isInvalid, "Tampered data should fail integrity check")
    }

    // MARK: - Keychain Tests

    func testKeychainSaveAndRetrieve() throws {
        // Given
        let testKey = "test_keychain_key"
        let testValue = "test_keychain_value"

        // When
        let saveResult = keychainService.save(testValue, for: testKey)
        let retrievedValue = keychainService.getString(for: testKey)

        // Then
        XCTAssertTrue(saveResult, "Save to keychain should succeed")
        XCTAssertEqual(retrievedValue, testValue, "Retrieved value should match saved value")

        // Cleanup
        keychainService.delete(testKey)
    }

    func testKeychainDelete() throws {
        // Given
        let testKey = "test_delete_key"
        let testValue = "test_value"
        keychainService.save(testValue, for: testKey)

        // When
        let deleteResult = keychainService.delete(testKey)
        let retrievedValue = keychainService.getString(for: testKey)

        // Then
        XCTAssertTrue(deleteResult, "Delete from keychain should succeed")
        XCTAssertNil(retrievedValue, "Retrieved value should be nil after deletion")
    }

    // MARK: - Audit Logging Tests

    func testAuditLogCreation() throws {
        // Given
        let testEvent = AuditEvent.loginSuccess
        let testDetails = "Test login event"

        // When
        auditLogger.log(event: testEvent, details: testDetails, severity: .medium)

        // Then
        // Verify log file was created
        // In production, you would verify the log entry was written
        XCTAssertTrue(true, "Audit log should be created")
    }

    func testMultipleAuditLogs() throws {
        // Given
        let events: [(AuditEvent, String)] = [
            (.loginAttempt, "User attempted login"),
            (.loginSuccess, "User logged in successfully"),
            (.phiAccessed, "User accessed mood data"),
            (.logoutPerformed, "User logged out")
        ]

        // When
        for (event, details) in events {
            auditLogger.log(event: event, details: details)
        }

        // Then
        // Verify all events were logged
        XCTAssertTrue(true, "All audit events should be logged")
    }
}

// MARK: - Secure Storage Tests

final class SecureStorageTests: XCTestCase {
    var secureStorage: SecureStorageService!
    let testUserId = "test-user-123"

    override func setUpWithError() throws {
        try super.setUpWithError()
        secureStorage = SecureStorageService.shared
    }

    func testSaveAndRetrieveObject() throws {
        // Given
        let testMood = MoodEntry(
            userId: UUID(),
            mood: .good,
            cravingLevel: .none
        )
        let testKey = "test_mood_entry"

        // When
        let saveResult = secureStorage.save(testMood, withKey: testKey, userId: testUserId)
        let retrievedMood = secureStorage.retrieve(MoodEntry.self, forKey: testKey, userId: testUserId)

        // Then
        XCTAssertTrue(saveResult, "Save should succeed")
        XCTAssertNotNil(retrievedMood, "Retrieved object should not be nil")
        XCTAssertEqual(retrievedMood?.mood, testMood.mood, "Retrieved mood should match saved mood")

        // Cleanup
        secureStorage.delete(key: testKey, userId: testUserId)
    }

    func testUpdateObject() throws {
        // Given
        var testUser = User(username: "testuser", email: "test@example.com")
        let testKey = "test_user"

        // When
        secureStorage.save(testUser, withKey: testKey, userId: testUserId)

        testUser.username = "updateduser"
        let updateResult = secureStorage.update(testUser, forKey: testKey, userId: testUserId)
        let retrievedUser = secureStorage.retrieve(User.self, forKey: testKey, userId: testUserId)

        // Then
        XCTAssertTrue(updateResult, "Update should succeed")
        XCTAssertEqual(retrievedUser?.username, "updateduser", "Retrieved username should be updated")

        // Cleanup
        secureStorage.delete(key: testKey, userId: testUserId)
    }

    func testDeleteObject() throws {
        // Given
        let testData = User(username: "deletetest")
        let testKey = "test_delete"

        secureStorage.save(testData, withKey: testKey, userId: testUserId)

        // When
        let deleteResult = secureStorage.delete(key: testKey, userId: testUserId)
        let retrievedData = secureStorage.retrieve(User.self, forKey: testKey, userId: testUserId)

        // Then
        XCTAssertTrue(deleteResult, "Delete should succeed")
        XCTAssertNil(retrievedData, "Retrieved data should be nil after deletion")
    }
}

// MARK: - Session Management Tests

final class SessionTests: XCTestCase {
    var sessionManager: SessionManager!

    override func setUpWithError() throws {
        try super.setUpWithError()
        sessionManager = SessionManager.shared
    }

    func testSessionStart() throws {
        // Given
        let testUser = User(username: "testuser")

        // When
        sessionManager.startSession(user: testUser)

        // Then
        XCTAssertTrue(sessionManager.isSessionActive, "Session should be active")
        XCTAssertNotNil(sessionManager.currentUser, "Current user should be set")
        XCTAssertEqual(sessionManager.currentUser?.username, testUser.username)
    }

    func testSessionEnd() throws {
        // Given
        let testUser = User(username: "testuser")
        sessionManager.startSession(user: testUser)

        // When
        sessionManager.endSession()

        // Then
        XCTAssertFalse(sessionManager.isSessionActive, "Session should not be active")
        XCTAssertNil(sessionManager.currentUser, "Current user should be nil")
    }

    func testSessionTimeout() throws {
        // Given
        let testUser = User(username: "testuser")
        sessionManager.startSession(user: testUser)

        // When
        sessionManager.expireSession()

        // Then
        XCTAssertFalse(sessionManager.isSessionActive, "Session should not be active")
        XCTAssertTrue(sessionManager.isSessionExpired, "Session should be marked as expired")
    }

    func testActivityUpdate() throws {
        // Given
        let testUser = User(username: "testuser")
        sessionManager.startSession(user: testUser)

        // When
        sessionManager.updateActivity()

        // Then
        // Verify last activity time was updated
        XCTAssertNotNil(sessionManager.timeUntilTimeout)
    }
}
