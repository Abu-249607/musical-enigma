//
//  Journal.swift
//  Therapist.Me
//
//  HIPAA Compliance: PHI - Personal journal entries
//

import Foundation

struct JournalEntry: Codable, Identifiable {
    let id: UUID
    let userId: UUID
    var timestamp: Date
    var title: String?
    var content: String
    var journalType: JournalType
    var mood: MoodLevel?
    var tags: [String]
    var isFavorite: Bool
    var linkedMoodEntryId: UUID?

    // Therapy-focused prompts
    var prompt: JournalPrompt?
    var insights: [String]

    init(
        id: UUID = UUID(),
        userId: UUID,
        timestamp: Date = Date(),
        title: String? = nil,
        content: String,
        journalType: JournalType = .freeForm,
        mood: MoodLevel? = nil,
        tags: [String] = [],
        isFavorite: Bool = false,
        linkedMoodEntryId: UUID? = nil,
        prompt: JournalPrompt? = nil,
        insights: [String] = []
    ) {
        self.id = id
        self.userId = userId
        self.timestamp = timestamp
        self.title = title
        self.content = content
        self.journalType = journalType
        self.mood = mood
        self.tags = tags
        self.isFavorite = isFavorite
        self.linkedMoodEntryId = linkedMoodEntryId
        self.prompt = prompt
        self.insights = insights
    }
}

enum JournalType: String, Codable, CaseIterable {
    case freeForm = "Free Form"
    case gratitude = "Gratitude"
    case cbtThoughtRecord = "CBT Thought Record"
    case triggerAnalysis = "Trigger Analysis"
    case cravingLog = "Craving Log"
    case successStory = "Success Story"
    case letterToSelf = "Letter to Self"
    case goalReflection = "Goal Reflection"
}

struct JournalPrompt: Codable, Identifiable {
    let id: UUID
    var question: String
    var category: JournalPromptCategory
    var therapyMethod: TherapyMethod

    init(
        id: UUID = UUID(),
        question: String,
        category: JournalPromptCategory,
        therapyMethod: TherapyMethod
    ) {
        self.id = id
        self.question = question
        self.category = category
        self.therapyMethod = therapyMethod
    }
}

enum JournalPromptCategory: String, Codable {
    case reflection = "Reflection"
    case gratitude = "Gratitude"
    case goalSetting = "Goal Setting"
    case triggerIdentification = "Trigger Identification"
    case copingStrategies = "Coping Strategies"
    case selfCompassion = "Self-Compassion"
    case futureVision = "Future Vision"
}

enum TherapyMethod: String, Codable {
    case cbt = "CBT"
    case motivationalInterviewing = "Motivational Interviewing"
    case mindfulness = "Mindfulness"
    case dbt = "DBT"
    case relapsePrevention = "Relapse Prevention"
    case general = "General"
}
