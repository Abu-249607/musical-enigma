//
//  Progress.swift
//  Therapist.Me
//
//  Track user progress, achievements, and recovery metrics
//

import Foundation

struct UserProgress: Codable, Identifiable {
    let id: UUID
    let userId: UUID
    var currentStreak: Int
    var longestStreak: Int
    var totalDaysTracked: Int
    var sobrietyStartDate: Date?
    var achievements: [Achievement]
    var statistics: ProgressStatistics
    var lastUpdated: Date

    init(
        id: UUID = UUID(),
        userId: UUID,
        currentStreak: Int = 0,
        longestStreak: Int = 0,
        totalDaysTracked: Int = 0,
        sobrietyStartDate: Date? = nil,
        achievements: [Achievement] = [],
        statistics: ProgressStatistics = ProgressStatistics(),
        lastUpdated: Date = Date()
    ) {
        self.id = id
        self.userId = userId
        self.currentStreak = currentStreak
        self.longestStreak = longestStreak
        self.totalDaysTracked = totalDaysTracked
        self.sobrietyStartDate = sobrietyStartDate
        self.achievements = achievements
        self.statistics = statistics
        self.lastUpdated = lastUpdated
    }

    var daysSober: Int? {
        guard let startDate = sobrietyStartDate else { return nil }
        return Calendar.current.dateComponents([.day], from: startDate, to: Date()).day
    }
}

struct ProgressStatistics: Codable {
    var totalMoodEntries: Int
    var totalJournalEntries: Int
    var totalExercisesCompleted: Int
    var totalChatSessions: Int
    var averageMoodScore: Double
    var averageCravingLevel: Double
    var cravingFreeTrend: [CravingDataPoint]
    var moodTrend: [MoodDataPoint]
    var triggersIdentified: Int
    var copingStrategiesUsed: Int

    init(
        totalMoodEntries: Int = 0,
        totalJournalEntries: Int = 0,
        totalExercisesCompleted: Int = 0,
        totalChatSessions: Int = 0,
        averageMoodScore: Double = 0,
        averageCravingLevel: Double = 0,
        cravingFreeTrend: [CravingDataPoint] = [],
        moodTrend: [MoodDataPoint] = [],
        triggersIdentified: Int = 0,
        copingStrategiesUsed: Int = 0
    ) {
        self.totalMoodEntries = totalMoodEntries
        self.totalJournalEntries = totalJournalEntries
        self.totalExercisesCompleted = totalExercisesCompleted
        self.totalChatSessions = totalChatSessions
        self.averageMoodScore = averageMoodScore
        self.averageCravingLevel = averageCravingLevel
        self.cravingFreeTrend = cravingFreeTrend
        self.moodTrend = moodTrend
        self.triggersIdentified = triggersIdentified
        self.copingStrategiesUsed = copingStrategiesUsed
    }
}

struct CravingDataPoint: Codable, Identifiable {
    let id: UUID
    var date: Date
    var cravingLevel: Int

    init(id: UUID = UUID(), date: Date, cravingLevel: Int) {
        self.id = id
        self.date = date
        self.cravingLevel = cravingLevel
    }
}

struct MoodDataPoint: Codable, Identifiable {
    let id: UUID
    var date: Date
    var moodScore: Int

    init(id: UUID = UUID(), date: Date, moodScore: Int) {
        self.id = id
        self.date = date
        self.moodScore = moodScore
    }
}

struct Achievement: Codable, Identifiable {
    let id: UUID
    var title: String
    var description: String
    var icon: String
    var category: AchievementCategory
    var dateEarned: Date
    var isUnlocked: Bool

    init(
        id: UUID = UUID(),
        title: String,
        description: String,
        icon: String,
        category: AchievementCategory,
        dateEarned: Date = Date(),
        isUnlocked: Bool = false
    ) {
        self.id = id
        self.title = title
        self.description = description
        self.icon = icon
        self.category = category
        self.dateEarned = dateEarned
        self.isUnlocked = isUnlocked
    }
}

enum AchievementCategory: String, Codable, CaseIterable {
    case sobriety = "Sobriety Milestones"
    case engagement = "Engagement"
    case journaling = "Journaling"
    case exercises = "Exercises"
    case community = "Community"
    case streaks = "Streaks"
    case special = "Special"
}

// Predefined achievements
extension Achievement {
    static let predefinedAchievements: [Achievement] = [
        // Sobriety milestones
        Achievement(title: "First Day", description: "Complete your first day of sobriety", icon: "🌟", category: .sobriety),
        Achievement(title: "One Week Strong", description: "7 days of sobriety", icon: "💪", category: .sobriety),
        Achievement(title: "Two Weeks Champion", description: "14 days of sobriety", icon: "🏆", category: .sobriety),
        Achievement(title: "One Month Warrior", description: "30 days of sobriety", icon: "⭐️", category: .sobriety),
        Achievement(title: "Three Months Hero", description: "90 days of sobriety", icon: "🎖", category: .sobriety),
        Achievement(title: "Six Months Legend", description: "180 days of sobriety", icon: "👑", category: .sobriety),
        Achievement(title: "One Year Milestone", description: "365 days of sobriety", icon: "🏅", category: .sobriety),

        // Engagement
        Achievement(title: "Getting Started", description: "Complete your first mood check-in", icon: "✅", category: .engagement),
        Achievement(title: "Daily Warrior", description: "Log mood for 7 consecutive days", icon: "📅", category: .engagement),
        Achievement(title: "Commitment", description: "Log mood for 30 consecutive days", icon: "💯", category: .engagement),

        // Journaling
        Achievement(title: "First Entry", description: "Write your first journal entry", icon: "📝", category: .journaling),
        Achievement(title: "Reflection Master", description: "Complete 10 journal entries", icon: "📖", category: .journaling),
        Achievement(title: "Storyteller", description: "Complete 50 journal entries", icon: "✍️", category: .journaling),

        // Exercises
        Achievement(title: "First Steps", description: "Complete your first guided exercise", icon: "🎯", category: .exercises),
        Achievement(title: "Practice Makes Progress", description: "Complete 10 exercises", icon: "🧘", category: .exercises),
        Achievement(title: "Exercise Expert", description: "Complete 25 exercises", icon: "🏋️", category: .exercises),

        // Community
        Achievement(title: "Community Member", description: "Join the peer support forum", icon: "👥", category: .community),
        Achievement(title: "Supportive Friend", description: "Support 5 community members", icon: "🤝", category: .community),

        // Special
        Achievement(title: "Crisis Overcome", description: "Successfully navigate a crisis using toolkit", icon: "🛟", category: .special),
        Achievement(title: "Goal Achiever", description: "Complete your first recovery goal", icon: "🎯", category: .special),
    ]
}
