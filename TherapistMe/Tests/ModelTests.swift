//
//  ModelTests.swift
//  Therapist.Me Tests
//
//  Unit tests for data models
//

import XCTest
@testable import TherapistMe

final class UserModelTests: XCTestCase {
    func testUserCreation() throws {
        // Given/When
        let user = User(
            username: "testuser",
            email: "test@example.com"
        )

        // Then
        XCTAssertNotNil(user.id)
        XCTAssertEqual(user.username, "testuser")
        XCTAssertEqual(user.email, "test@example.com")
        XCTAssertNotNil(user.profile)
        XCTAssertNotNil(user.privacyConsent)
    }

    func testUserCodable() throws {
        // Given
        let user = User(username: "testuser")
        let encoder = JSONEncoder()
        let decoder = JSONDecoder()

        // When
        let encoded = try encoder.encode(user)
        let decoded = try decoder.decode(User.self, from: encoded)

        // Then
        XCTAssertEqual(decoded.id, user.id)
        XCTAssertEqual(decoded.username, user.username)
    }
}

final class MoodEntryTests: XCTestCase {
    func testMoodEntryCreation() throws {
        // Given
        let userId = UUID()

        // When
        let moodEntry = MoodEntry(
            userId: userId,
            mood: .good,
            emotions: [.happy, .grateful],
            cravingLevel: .none
        )

        // Then
        XCTAssertEqual(moodEntry.mood, .good)
        XCTAssertEqual(moodEntry.cravingLevel, .none)
        XCTAssertEqual(moodEntry.emotions.count, 2)
    }

    func testMoodLevelScoring() throws {
        // Then
        XCTAssertEqual(MoodLevel.veryPoor.score, 1)
        XCTAssertEqual(MoodLevel.poor.score, 2)
        XCTAssertEqual(MoodLevel.okay.score, 3)
        XCTAssertEqual(MoodLevel.good.score, 4)
        XCTAssertEqual(MoodLevel.excellent.score, 5)
    }

    func testCravingLevelScoring() throws {
        // Then
        XCTAssertEqual(CravingLevel.none.score, 0)
        XCTAssertEqual(CravingLevel.mild.score, 1)
        XCTAssertEqual(CravingLevel.moderate.score, 2)
        XCTAssertEqual(CravingLevel.strong.score, 3)
        XCTAssertEqual(CravingLevel.severe.score, 4)
    }
}

final class JournalEntryTests: XCTestCase {
    func testJournalEntryCreation() throws {
        // Given
        let userId = UUID()

        // When
        let entry = JournalEntry(
            userId: userId,
            content: "Test journal entry",
            journalType: .freeForm,
            mood: .good
        )

        // Then
        XCTAssertNotNil(entry.id)
        XCTAssertEqual(entry.content, "Test journal entry")
        XCTAssertEqual(entry.journalType, .freeForm)
    }

    func testJournalEntryCodable() throws {
        // Given
        let entry = JournalEntry(
            userId: UUID(),
            content: "Test",
            journalType: .gratitude
        )
        let encoder = JSONEncoder()
        let decoder = JSONDecoder()

        // When
        let encoded = try encoder.encode(entry)
        let decoded = try decoder.decode(JournalEntry.self, from: encoded)

        // Then
        XCTAssertEqual(decoded.id, entry.id)
        XCTAssertEqual(decoded.content, entry.content)
    }
}

final class ProgressTests: XCTestCase {
    func testDaysSoberCalculation() throws {
        // Given
        let userId = UUID()
        let sevenDaysAgo = Calendar.current.date(byAdding: .day, value: -7, to: Date())!

        // When
        let progress = UserProgress(
            userId: userId,
            sobrietyStartDate: sevenDaysAgo
        )

        // Then
        XCTAssertNotNil(progress.daysSober)
        XCTAssertEqual(progress.daysSober, 7)
    }

    func testAchievementUnlocking() throws {
        // Given
        var achievement = Achievement(
            title: "First Day",
            description: "Complete first day",
            icon: "🌟",
            category: .sobriety
        )

        // When
        achievement.isUnlocked = true

        // Then
        XCTAssertTrue(achievement.isUnlocked)
    }
}

final class ChatMessageTests: XCTestCase {
    func testChatMessageCreation() throws {
        // Given/When
        let message = ChatMessage(
            content: "Test message",
            sender: .user,
            therapyTechnique: .openEndedQuestion
        )

        // Then
        XCTAssertEqual(message.content, "Test message")
        XCTAssertEqual(message.sender, .user)
        XCTAssertEqual(message.therapyTechnique, .openEndedQuestion)
    }

    func testChatSessionCreation() throws {
        // Given
        let userId = UUID()
        let message = ChatMessage(content: "Hello", sender: .therapist)

        // When
        let session = ChatSession(
            userId: userId,
            messages: [message],
            sessionType: .general
        )

        // Then
        XCTAssertEqual(session.messages.count, 1)
        XCTAssertEqual(session.sessionType, .general)
    }
}

final class ForumTests: XCTestCase {
    func testForumPostCreation() throws {
        // Given/When
        let post = ForumPost(
            authorId: UUID(),
            authorAlias: "TestUser123",
            title: "Test Post",
            content: "Test content",
            category: .general
        )

        // Then
        XCTAssertEqual(post.title, "Test Post")
        XCTAssertEqual(post.category, .general)
        XCTAssertEqual(post.moderationStatus, .pending)
    }

    func testAliasGeneration() throws {
        // When
        let alias1 = AliasGenerator.generate()
        let alias2 = AliasGenerator.generate()

        // Then
        XCTAssertFalse(alias1.isEmpty)
        XCTAssertFalse(alias2.isEmpty)
        XCTAssertNotEqual(alias1, alias2) // Should be different with high probability
    }

    func testContentModeration() throws {
        // Given
        let cleanContent = "This is a supportive message"
        let flaggedContent = "I want to end it all"

        // When
        let cleanStatus = ContentModerator.checkContent(cleanContent)
        let flaggedStatus = ContentModerator.checkContent(flaggedContent)

        // Then
        XCTAssertEqual(cleanStatus, .approved)
        XCTAssertEqual(flaggedStatus, .flagged)
    }
}
