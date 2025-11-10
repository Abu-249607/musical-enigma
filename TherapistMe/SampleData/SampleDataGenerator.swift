//
//  SampleDataGenerator.swift
//  Therapist.Me
//
//  Sample data for development and testing
//

import Foundation

class SampleDataGenerator {
    static let shared = SampleDataGenerator()

    private init() {}

    // MARK: - Sample Users

    func generateSampleUser() -> User {
        var user = User(
            username: "johndoe123",
            email: "john@example.com",
            profile: UserProfile(
                firstName: "John",
                age: 32,
                gender: .male,
                timezone: TimeZone.current.identifier,
                language: "en"
            ),
            privacyConsent: PrivacyConsent(
                hasAcceptedTerms: true,
                hasAcceptedPrivacyPolicy: true,
                hasAcceptedHIPAANotice: true,
                consentDate: Date(),
                dataProcessingConsent: true,
                analyticsConsent: true,
                marketingConsent: false
            ),
            authenticationMethod: .biometric
        )

        // Add recovery goals
        user.recoveryGoals = [
            RecoveryGoal(
                title: "Achieve 30 Days Sobriety",
                description: "Complete 30 consecutive days without substance use",
                goalType: .sobriety,
                targetDate: Calendar.current.date(byAdding: .day, value: 30, to: Date()),
                milestones: [
                    Milestone(title: "First Week", isCompleted: true),
                    Milestone(title: "Two Weeks", isCompleted: false),
                    Milestone(title: "One Month", isCompleted: false)
                ]
            ),
            RecoveryGoal(
                title: "Improve Mental Health",
                description: "Practice daily mindfulness and mood tracking",
                goalType: .mentalHealth,
                milestones: [
                    Milestone(title: "Track mood daily for 7 days", isCompleted: true),
                    Milestone(title: "Complete 5 mindfulness exercises", isCompleted: false)
                ]
            )
        ]

        // Add substance history
        user.substanceHistory = [
            SubstanceHistory(
                substanceType: .alcohol,
                frequencyOfUse: .daily,
                yearsOfUse: 10,
                lastUsedDate: Calendar.current.date(byAdding: .day, value: -7, to: Date()),
                sobrietyStartDate: Calendar.current.date(byAdding: .day, value: -7, to: Date()),
                notes: "Started recovery journey"
            )
        ]

        // Add emergency contacts
        user.emergencyContacts = [
            EmergencyContact(
                name: "Jane Doe",
                relationship: "Spouse",
                phoneNumber: "+1-555-123-4567",
                isPrimary: true
            ),
            EmergencyContact(
                name: "Dr. Smith",
                relationship: "Therapist",
                phoneNumber: "+1-555-987-6543",
                isPrimary: false
            )
        ]

        return user
    }

    // MARK: - Sample Mood Entries

    func generateSampleMoodEntries(userId: UUID, count: Int = 7) -> [MoodEntry] {
        var entries: [MoodEntry] = []
        let calendar = Calendar.current

        for i in 0..<count {
            guard let date = calendar.date(byAdding: .day, value: -i, to: Date()) else { continue }

            let entry = MoodEntry(
                userId: userId,
                timestamp: date,
                mood: MoodLevel.allCases.randomElement() ?? .okay,
                emotions: [
                    Emotion.allCases.randomElement() ?? .calm,
                    Emotion.allCases.randomElement() ?? .hopeful
                ],
                cravingLevel: CravingLevel.allCases.randomElement() ?? .none,
                triggers: [],
                copingStrategiesUsed: [.deepBreathing, .journaling],
                notes: "Sample mood entry for day \(i + 1)",
                energyLevel: Int.random(in: 3...8),
                sleepQuality: Int.random(in: 4...9),
                stressLevel: Int.random(in: 2...7)
            )

            entries.append(entry)
        }

        return entries
    }

    // MARK: - Sample Journal Entries

    func generateSampleJournalEntries(userId: UUID, count: Int = 5) -> [JournalEntry] {
        var entries: [JournalEntry] = []
        let calendar = Calendar.current

        let sampleContents = [
            "Today was a challenging day, but I made it through without giving in to cravings. I'm proud of myself.",
            "I'm grateful for my support system. Having people who understand makes all the difference.",
            "Practiced mindfulness this morning. It really helped me start the day with a clear mind.",
            "Had a difficult conversation with my family, but I handled it better than I would have before recovery.",
            "Feeling strong today. One day at a time, I'm building a better life for myself."
        ]

        for i in 0..<count {
            guard let date = calendar.date(byAdding: .day, value: -i * 2, to: Date()) else { continue }

            let entry = JournalEntry(
                userId: userId,
                timestamp: date,
                title: "Day \(i + 1) Reflection",
                content: sampleContents[i % sampleContents.count],
                journalType: JournalType.allCases.randomElement() ?? .freeForm,
                mood: MoodLevel.allCases.randomElement(),
                tags: ["recovery", "gratitude"],
                isFavorite: i == 0
            )

            entries.append(entry)
        }

        return entries
    }

    // MARK: - Sample Progress

    func generateSampleProgress(userId: UUID) -> UserProgress {
        let calendar = Calendar.current
        var moodTrend: [MoodDataPoint] = []
        var cravingTrend: [CravingDataPoint] = []

        // Generate 30 days of trend data
        for i in 0..<30 {
            if let date = calendar.date(byAdding: .day, value: -i, to: Date()) {
                moodTrend.append(MoodDataPoint(date: date, moodScore: Int.random(in: 2...5)))
                cravingTrend.append(CravingDataPoint(date: date, cravingLevel: Int.random(in: 0...3)))
            }
        }

        let statistics = ProgressStatistics(
            totalMoodEntries: 42,
            totalJournalEntries: 18,
            totalExercisesCompleted: 25,
            totalChatSessions: 15,
            averageMoodScore: 3.8,
            averageCravingLevel: 1.2,
            cravingFreeTrend: cravingTrend,
            moodTrend: moodTrend,
            triggersIdentified: 12,
            copingStrategiesUsed: 8
        )

        var achievements = Achievement.predefinedAchievements
        // Unlock first few achievements
        for i in 0..<3 {
            achievements[i].isUnlocked = true
        }

        return UserProgress(
            userId: userId,
            currentStreak: 7,
            longestStreak: 14,
            totalDaysTracked: 42,
            sobrietyStartDate: calendar.date(byAdding: .day, value: -7, to: Date()),
            achievements: achievements,
            statistics: statistics
        )
    }

    // MARK: - Sample Chat Messages

    func generateSampleChatSession(userId: UUID) -> ChatSession {
        let messages = [
            ChatMessage(
                content: "Hello! How are you feeling today?",
                sender: .therapist,
                therapyTechnique: .openEndedQuestion,
                emotionalTone: .supportive
            ),
            ChatMessage(
                content: "I'm feeling a bit anxious today.",
                sender: .user
            ),
            ChatMessage(
                content: "Thank you for sharing that. Anxiety is a common experience in recovery. Can you tell me more about what's making you feel anxious?",
                sender: .therapist,
                therapyTechnique: .reflectiveListening,
                emotionalTone: .empathetic
            ),
            ChatMessage(
                content: "I'm worried about going to a social event where there will be drinking.",
                sender: .user
            ),
            ChatMessage(
                content: "That's a valid concern, and it shows good self-awareness. Let's work on a plan together. What coping strategies have worked for you in the past?",
                sender: .therapist,
                therapyTechnique: .copingSkills,
                suggestedActions: [
                    SuggestedAction(title: "Breathing Exercise", actionType: .breathingExercise),
                    SuggestedAction(title: "Create Coping Plan", actionType: .setGoal)
                ],
                emotionalTone: .supportive
            )
        ]

        return ChatSession(
            userId: userId,
            messages: messages,
            sessionType: .general,
            mood: .okay
        )
    }

    // MARK: - Sample Therapy Exercises

    func generateSampleExercises() -> [TherapyExercise] {
        return [
            TherapyExercise(
                title: "Gratitude Practice",
                description: "List three things you're grateful for today",
                category: .journalingPrompt,
                therapyMethod: .general,
                duration: 5,
                difficulty: .beginner,
                instructions: [
                    "Find a quiet place to reflect",
                    "Think about your day",
                    "Write down three things you're grateful for",
                    "Reflect on why each one matters to you"
                ],
                benefits: [
                    "Improves mood",
                    "Increases positive thinking",
                    "Reduces stress"
                ],
                tags: ["gratitude", "mindfulness"]
            ),
            TherapyExercise(
                title: "Mindful Observation",
                description: "Practice present moment awareness",
                category: .mindfulness,
                therapyMethod: .mindfulness,
                duration: 10,
                difficulty: .beginner,
                instructions: [
                    "Choose an object to focus on",
                    "Observe it with all your senses",
                    "Notice colors, textures, sounds",
                    "Bring your attention back when it wanders",
                    "Continue for 10 minutes"
                ],
                benefits: [
                    "Improves focus",
                    "Reduces anxiety",
                    "Enhances present moment awareness"
                ],
                tags: ["mindfulness", "grounding"]
            )
        ]
    }

    // MARK: - Sample Forum Posts

    func generateSampleForumPosts(count: Int = 5) -> [ForumPost] {
        var posts: [ForumPost] = []

        let samplePosts = [
            (title: "Celebrating 30 Days!", content: "I just hit 30 days sober and I couldn't be more proud. To anyone struggling, keep going!", category: ForumCategory.celebratingMilestones),
            (title: "Tips for handling social situations?", content: "I'm going to my first party sober. Any advice on how to handle this?", category: ForumCategory.cravingsAndTriggers),
            (title: "Morning routines that help", content: "Starting my day with meditation and journaling has been game-changing. What are your morning rituals?", category: ForumCategory.general),
            (title: "Struggling today", content: "Having a rough day with cravings. Just needed to share with people who understand.", category: ForumCategory.general),
            (title: "6 Months Update", content: "6 months ago I never thought I'd be here. Life isn't perfect, but it's so much better. Thank you all for the support.", category: ForumCategory.celebratingMilestones)
        ]

        for (index, sample) in samplePosts.prefix(count).enumerated() {
            let post = ForumPost(
                authorId: UUID(),
                authorAlias: AliasGenerator.generate(),
                title: sample.title,
                content: sample.content,
                category: sample.category,
                timestamp: Calendar.current.date(byAdding: .day, value: -index, to: Date()) ?? Date(),
                likeCount: Int.random(in: 5...50),
                supportCount: Int.random(in: 10...100),
                moderationStatus: .approved
            )

            posts.append(post)
        }

        return posts
    }
}
