//
//  Exercise.swift
//  Therapist.Me
//
//  Guided therapy exercises and activities
//

import Foundation

struct TherapyExercise: Codable, Identifiable {
    let id: UUID
    var title: String
    var description: String
    var category: ExerciseCategory
    var therapyMethod: TherapyMethod
    var duration: Int // minutes
    var difficulty: Difficulty
    var instructions: [String]
    var benefits: [String]
    var tags: [String]
    var audioGuideURL: String?
    var completionCount: Int

    init(
        id: UUID = UUID(),
        title: String,
        description: String,
        category: ExerciseCategory,
        therapyMethod: TherapyMethod,
        duration: Int,
        difficulty: Difficulty,
        instructions: [String],
        benefits: [String] = [],
        tags: [String] = [],
        audioGuideURL: String? = nil,
        completionCount: Int = 0
    ) {
        self.id = id
        self.title = title
        self.description = description
        self.category = category
        self.therapyMethod = therapyMethod
        self.duration = duration
        self.difficulty = difficulty
        self.instructions = instructions
        self.benefits = benefits
        self.tags = tags
        self.audioGuideURL = audioGuideURL
        self.completionCount = completionCount
    }
}

enum ExerciseCategory: String, Codable, CaseIterable {
    case breathingExercise = "Breathing Exercise"
    case meditation = "Meditation"
    case mindfulness = "Mindfulness"
    case cognitiveRestructuring = "Cognitive Restructuring"
    case behavioralActivation = "Behavioral Activation"
    case grounding = "Grounding Technique"
    case visualization = "Visualization"
    case progressiveMuscleRelaxation = "Progressive Muscle Relaxation"
    case journalingPrompt = "Journaling Prompt"
    case psychoeducation = "Psychoeducation"
    case triggerManagement = "Trigger Management"
    case cravingUrfSurfing = "Urge Surfing"
}

enum Difficulty: String, Codable, CaseIterable {
    case beginner = "Beginner"
    case intermediate = "Intermediate"
    case advanced = "Advanced"
}

struct ExerciseCompletion: Codable, Identifiable {
    let id: UUID
    let userId: UUID
    let exerciseId: UUID
    var completionDate: Date
    var rating: Int? // 1-5
    var notes: String?
    var wasHelpful: Bool?

    init(
        id: UUID = UUID(),
        userId: UUID,
        exerciseId: UUID,
        completionDate: Date = Date(),
        rating: Int? = nil,
        notes: String? = nil,
        wasHelpful: Bool? = nil
    ) {
        self.id = id
        self.userId = userId
        self.exerciseId = exerciseId
        self.completionDate = completionDate
        self.rating = rating
        self.notes = notes
        self.wasHelpful = wasHelpful
    }
}

// MARK: - Breathing Exercise
struct BreathingExercise: Codable, Identifiable {
    let id: UUID
    var name: String
    var description: String
    var inhaleCount: Int
    var holdCount: Int
    var exhaleCount: Int
    var cycles: Int
    var visualGuide: String

    init(
        id: UUID = UUID(),
        name: String,
        description: String,
        inhaleCount: Int,
        holdCount: Int,
        exhaleCount: Int,
        cycles: Int,
        visualGuide: String = "circle"
    ) {
        self.id = id
        self.name = name
        self.description = description
        self.inhaleCount = inhaleCount
        self.holdCount = holdCount
        self.exhaleCount = exhaleCount
        self.cycles = cycles
        self.visualGuide = visualGuide
    }
}

extension BreathingExercise {
    static let predefinedExercises: [BreathingExercise] = [
        BreathingExercise(
            name: "Box Breathing",
            description: "Used by Navy SEALs to stay calm under pressure",
            inhaleCount: 4,
            holdCount: 4,
            exhaleCount: 4,
            cycles: 4
        ),
        BreathingExercise(
            name: "4-7-8 Breathing",
            description: "Promotes relaxation and helps with sleep",
            inhaleCount: 4,
            holdCount: 7,
            exhaleCount: 8,
            cycles: 4
        ),
        BreathingExercise(
            name: "Deep Belly Breathing",
            description: "Activates the body's relaxation response",
            inhaleCount: 4,
            holdCount: 2,
            exhaleCount: 6,
            cycles: 5
        ),
        BreathingExercise(
            name: "Quick Calm",
            description: "Fast relief for acute stress or cravings",
            inhaleCount: 3,
            holdCount: 3,
            exhaleCount: 3,
            cycles: 3
        )
    ]
}

// MARK: - Psychoeducation Content
struct PsychoeducationContent: Codable, Identifiable {
    let id: UUID
    var title: String
    var content: String
    var category: PsychoeducationCategory
    var readingTime: Int // minutes
    var resources: [String]
    var keyTakeaways: [String]

    init(
        id: UUID = UUID(),
        title: String,
        content: String,
        category: PsychoeducationCategory,
        readingTime: Int,
        resources: [String] = [],
        keyTakeaways: [String] = []
    ) {
        self.id = id
        self.title = title
        self.content = content
        self.category = category
        self.readingTime = readingTime
        self.resources = resources
        self.keyTakeaways = keyTakeaways
    }
}

enum PsychoeducationCategory: String, Codable, CaseIterable {
    case addictionScience = "Understanding Addiction"
    case recoveryProcess = "Recovery Process"
    case neurobiology = "Brain & Neurobiology"
    case cbtBasics = "CBT Fundamentals"
    case mindfulnessPractice = "Mindfulness Practice"
    case relapsePrevention = "Relapse Prevention"
    case copingSkills = "Coping Skills"
    case selfCare = "Self-Care"
    case relationships = "Relationships in Recovery"
    case successStories = "Success Stories"
}
