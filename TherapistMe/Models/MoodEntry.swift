//
//  MoodEntry.swift
//  Therapist.Me
//
//  HIPAA Compliance: PHI - Mood and mental health data
//

import Foundation

struct MoodEntry: Codable, Identifiable {
    let id: UUID
    let userId: UUID
    var timestamp: Date
    var mood: MoodLevel
    var emotions: [Emotion]
    var cravingLevel: CravingLevel
    var triggers: [Trigger]
    var copingStrategiesUsed: [CopingStrategy]
    var notes: String?
    var energyLevel: Int // 1-10
    var sleepQuality: Int? // 1-10
    var stressLevel: Int // 1-10

    // Context
    var location: String?
    var socialContext: SocialContext?

    init(
        id: UUID = UUID(),
        userId: UUID,
        timestamp: Date = Date(),
        mood: MoodLevel,
        emotions: [Emotion] = [],
        cravingLevel: CravingLevel,
        triggers: [Trigger] = [],
        copingStrategiesUsed: [CopingStrategy] = [],
        notes: String? = nil,
        energyLevel: Int = 5,
        sleepQuality: Int? = nil,
        stressLevel: Int = 5,
        location: String? = nil,
        socialContext: SocialContext? = nil
    ) {
        self.id = id
        self.userId = userId
        self.timestamp = timestamp
        self.mood = mood
        self.emotions = emotions
        self.cravingLevel = cravingLevel
        self.triggers = triggers
        self.copingStrategiesUsed = copingStrategiesUsed
        self.notes = notes
        self.energyLevel = energyLevel
        self.sleepQuality = sleepQuality
        self.stressLevel = stressLevel
        self.location = location
        self.socialContext = socialContext
    }
}

// MARK: - Mood Level
enum MoodLevel: String, Codable, CaseIterable {
    case veryPoor = "Very Poor"
    case poor = "Poor"
    case okay = "Okay"
    case good = "Good"
    case excellent = "Excellent"

    var emoji: String {
        switch self {
        case .veryPoor: return "😢"
        case .poor: return "😟"
        case .okay: return "😐"
        case .good: return "😊"
        case .excellent: return "😄"
        }
    }

    var score: Int {
        switch self {
        case .veryPoor: return 1
        case .poor: return 2
        case .okay: return 3
        case .good: return 4
        case .excellent: return 5
        }
    }
}

// MARK: - Emotions
enum Emotion: String, Codable, CaseIterable {
    // Positive
    case happy = "Happy"
    case grateful = "Grateful"
    case hopeful = "Hopeful"
    case proud = "Proud"
    case calm = "Calm"
    case confident = "Confident"

    // Negative
    case sad = "Sad"
    case angry = "Angry"
    case anxious = "Anxious"
    case lonely = "Lonely"
    case frustrated = "Frustrated"
    case overwhelmed = "Overwhelmed"
    case guilty = "Guilty"
    case ashamed = "Ashamed"
    case bored = "Bored"
    case restless = "Restless"

    var category: EmotionCategory {
        switch self {
        case .happy, .grateful, .hopeful, .proud, .calm, .confident:
            return .positive
        case .sad, .angry, .anxious, .lonely, .frustrated, .overwhelmed, .guilty, .ashamed, .bored, .restless:
            return .negative
        }
    }
}

enum EmotionCategory: String, Codable {
    case positive = "Positive"
    case negative = "Challenging"
}

// MARK: - Craving Level
enum CravingLevel: String, Codable, CaseIterable {
    case none = "None"
    case mild = "Mild"
    case moderate = "Moderate"
    case strong = "Strong"
    case severe = "Severe/Crisis"

    var emoji: String {
        switch self {
        case .none: return "✅"
        case .mild: return "⚠️"
        case .moderate: return "🟡"
        case .strong: return "🟠"
        case .severe: return "🔴"
        }
    }

    var score: Int {
        switch self {
        case .none: return 0
        case .mild: return 1
        case .moderate: return 2
        case .strong: return 3
        case .severe: return 4
        }
    }
}

// MARK: - Triggers
struct Trigger: Codable, Identifiable {
    let id: UUID
    var name: String
    var category: TriggerCategory
    var intensity: Int // 1-10
    var notes: String?

    init(
        id: UUID = UUID(),
        name: String,
        category: TriggerCategory,
        intensity: Int = 5,
        notes: String? = nil
    ) {
        self.id = id
        self.name = name
        self.category = category
        self.intensity = intensity
        self.notes = notes
    }
}

enum TriggerCategory: String, Codable, CaseIterable {
    case people = "People"
    case places = "Places"
    case emotions = "Emotions"
    case events = "Events"
    case stress = "Stress"
    case physical = "Physical Sensations"
    case time = "Time of Day"
    case substances = "Substance Exposure"
    case media = "Media/Content"
    case other = "Other"
}

// MARK: - Coping Strategies
enum CopingStrategy: String, Codable, CaseIterable {
    // Healthy strategies
    case deepBreathing = "Deep Breathing"
    case meditation = "Meditation"
    case exercise = "Exercise"
    case journaling = "Journaling"
    case talkToFriend = "Talk to Friend"
    case talkToTherapist = "Talk to Therapist"
    case musicTherapy = "Listen to Music"
    case distraction = "Distraction Activity"
    case gratitudePractice = "Gratitude Practice"
    case prayer = "Prayer/Spiritual Practice"
    case creativeExpression = "Creative Expression"
    case nature = "Time in Nature"
    case reading = "Reading"
    case helpingOthers = "Helping Others"

    // Support resources
    case attendMeeting = "Attend Support Meeting"
    case callHotline = "Call Hotline"
    case emergencyContact = "Contact Emergency Support"

    var category: CopingCategory {
        switch self {
        case .deepBreathing, .meditation:
            return .mindfulness
        case .exercise, .nature:
            return .physical
        case .journaling, .gratitudePractice, .creativeExpression, .reading:
            return .creative
        case .talkToFriend, .talkToTherapist, .attendMeeting, .helpingOthers:
            return .social
        case .musicTherapy, .prayer, .distraction:
            return .distraction
        case .callHotline, .emergencyContact:
            return .crisis
        }
    }
}

enum CopingCategory: String, Codable {
    case mindfulness = "Mindfulness"
    case physical = "Physical"
    case creative = "Creative"
    case social = "Social Support"
    case distraction = "Healthy Distraction"
    case crisis = "Crisis Resources"
}

// MARK: - Social Context
enum SocialContext: String, Codable, CaseIterable {
    case alone = "Alone"
    case withFamily = "With Family"
    case withFriends = "With Friends"
    case atWork = "At Work"
    case inPublic = "In Public"
    case supportGroup = "Support Group"
    case therapy = "Therapy Session"
}
