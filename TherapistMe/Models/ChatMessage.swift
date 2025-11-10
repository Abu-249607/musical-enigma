//
//  ChatMessage.swift
//  Therapist.Me
//
//  Virtual therapist chatbot conversation models
//

import Foundation

struct ChatSession: Codable, Identifiable {
    let id: UUID
    let userId: UUID
    var startTime: Date
    var endTime: Date?
    var messages: [ChatMessage]
    var sessionType: SessionType
    var mood: MoodLevel?
    var summary: String?

    init(
        id: UUID = UUID(),
        userId: UUID,
        startTime: Date = Date(),
        endTime: Date? = nil,
        messages: [ChatMessage] = [],
        sessionType: SessionType,
        mood: MoodLevel? = nil,
        summary: String? = nil
    ) {
        self.id = id
        self.userId = userId
        self.startTime = startTime
        self.endTime = endTime
        self.messages = messages
        self.sessionType = sessionType
        self.mood = mood
        self.summary = summary
    }
}

enum SessionType: String, Codable, CaseIterable {
    case general = "General Chat"
    case crisis = "Crisis Support"
    case cbt = "CBT Session"
    case motivationalInterviewing = "Motivational Interviewing"
    case mindfulness = "Mindfulness"
    case relapsePrevention = "Relapse Prevention"
    case checkIn = "Daily Check-in"
}

struct ChatMessage: Codable, Identifiable {
    let id: UUID
    var content: String
    var sender: MessageSender
    var timestamp: Date
    var therapyTechnique: TherapyTechnique?
    var suggestedActions: [SuggestedAction]
    var emotionalTone: EmotionalTone?

    init(
        id: UUID = UUID(),
        content: String,
        sender: MessageSender,
        timestamp: Date = Date(),
        therapyTechnique: TherapyTechnique? = nil,
        suggestedActions: [SuggestedAction] = [],
        emotionalTone: EmotionalTone? = nil
    ) {
        self.id = id
        self.content = content
        self.sender = sender
        self.timestamp = timestamp
        self.therapyTechnique = therapyTechnique
        self.suggestedActions = suggestedActions
        self.emotionalTone = emotionalTone
    }
}

enum MessageSender: String, Codable {
    case user = "User"
    case therapist = "Therapist"
    case system = "System"
}

enum TherapyTechnique: String, Codable {
    // CBT Techniques
    case thoughtChallenging = "Thought Challenging"
    case behavioralActivation = "Behavioral Activation"
    case cognitiveRestructuring = "Cognitive Restructuring"
    case exposureTherapy = "Exposure"

    // Motivational Interviewing
    case openEndedQuestion = "Open-ended Question"
    case affirmation = "Affirmation"
    case reflectiveListening = "Reflective Listening"
    case summarizing = "Summarizing"
    case changeAffirmation = "Affirming Change"

    // DBT Techniques
    case distressTolerance = "Distress Tolerance"
    case emotionRegulation = "Emotion Regulation"
    case mindfulness = "Mindfulness"
    case interpersonalEffectiveness = "Interpersonal Effectiveness"

    // Relapse Prevention
    case triggerIdentification = "Trigger Identification"
    case copingSkills = "Coping Skills"
    case urgeSurfing = "Urge Surfing"
    case consequenceAnalysis = "Consequence Analysis"

    // General
    case psychoeducation = "Psychoeducation"
    case validationAndSupport = "Validation & Support"
}

enum EmotionalTone: String, Codable {
    case supportive = "Supportive"
    case empathetic = "Empathetic"
    case encouraging = "Encouraging"
    case challenging = "Challenging"
    case educational = "Educational"
    case crisis = "Crisis Support"
}

struct SuggestedAction: Codable, Identifiable {
    let id: UUID
    var title: String
    var actionType: ActionType
    var description: String?

    init(
        id: UUID = UUID(),
        title: String,
        actionType: ActionType,
        description: String? = nil
    ) {
        self.id = id
        self.title = title
        self.actionType = actionType
        self.description = description
    }
}

enum ActionType: String, Codable {
    case startExercise = "Start Exercise"
    case journalPrompt = "Journal"
    case breathingExercise = "Breathing Exercise"
    case contactSupport = "Contact Support"
    case viewResources = "View Resources"
    case setGoal = "Set Goal"
    case trackMood = "Track Mood"
    case emergencyCrisis = "Emergency Crisis"
}

// MARK: - Chatbot Response Templates
struct ChatbotPrompt {
    // CBT Prompts
    static let cbtThoughtChallenge = [
        "What evidence do you have for this thought?",
        "What evidence contradicts this thought?",
        "What would you tell a friend who had this thought?",
        "Is there another way to look at this situation?",
        "What's the worst that could happen? How likely is it?"
    ]

    // Motivational Interviewing
    static let motivationalInterviewing = [
        "What makes you want to change?",
        "On a scale of 1-10, how important is this change to you?",
        "What would your life look like without this struggle?",
        "What strengths have helped you in the past?",
        "What's one small step you could take today?"
    ]

    // Crisis Support
    static let crisisSupport = [
        "I'm here with you. You're not alone.",
        "Let's focus on getting through this moment together.",
        "What has helped you in similar situations before?",
        "Would a breathing exercise help right now?",
        "Is there someone you trust who you could reach out to?"
    ]

    // Relapse Prevention
    static let relapsePrevention = [
        "What triggered this craving?",
        "Let's identify your warning signs together.",
        "What coping skills have worked for you before?",
        "How can you reward yourself for getting through this?",
        "What will you feel proud of tomorrow if you don't use today?"
    ]

    // Affirmations
    static let affirmations = [
        "Recovery is a journey, not a destination. Every step counts.",
        "You have the strength within you to overcome this.",
        "Progress, not perfection. Be proud of how far you've come.",
        "Each day sober is a victory worth celebrating.",
        "You are worthy of a healthy, fulfilling life.",
        "Healing takes time. Be patient with yourself.",
        "You're not alone in this journey. Support is always available."
    ]

    // Mindfulness Prompts
    static let mindfulnessPrompts = [
        "Take a moment to notice your breath. How does it feel?",
        "What are three things you can see right now?",
        "Notice any sensations in your body without judgment.",
        "What emotions are present for you right now?",
        "Can you observe this feeling without acting on it?"
    ]
}
