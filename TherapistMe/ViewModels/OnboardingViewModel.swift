//
//  OnboardingViewModel.swift
//  Therapist.Me
//
//  Onboarding flow state management
//

import Foundation

class OnboardingViewModel: ObservableObject {
    // Navigation
    @Published var currentStep: OnboardingStep = .welcome
    @Published var isOnboardingComplete = false

    // Privacy consent
    @Published var hasAcceptedTerms = false
    @Published var hasAcceptedPrivacyPolicy = false
    @Published var hasAcceptedHIPAANotice = false
    @Published var analyticsConsent = false

    // Profile
    @Published var username = ""
    @Published var firstName = ""
    @Published var email = ""
    @Published var selectedGender: Gender? = nil
    @Published var age: Int? = nil

    // Goals
    @Published var selectedGoals: Set<GoalType> = []

    // Substance history
    @Published var primarySubstance: SubstanceType? = nil
    @Published var frequencyOfUse: FrequencyOfUse = .former
    @Published var sobrietyStartDate = Date()

    // MARK: - Navigation

    func nextStep() {
        guard let nextStep = OnboardingStep(rawValue: currentStep.rawValue + 1) else {
            return
        }
        currentStep = nextStep
    }

    func previousStep() {
        guard let previousStep = OnboardingStep(rawValue: currentStep.rawValue - 1) else {
            return
        }
        currentStep = previousStep
    }

    func completeOnboarding() {
        isOnboardingComplete = true
    }

    // MARK: - Validation

    func canProceedFromPrivacy() -> Bool {
        return hasAcceptedTerms && hasAcceptedPrivacyPolicy && hasAcceptedHIPAANotice
    }

    // MARK: - User Creation

    func createUser() -> User? {
        guard !username.isEmpty else {
            return nil
        }

        // Create privacy consent
        let privacyConsent = PrivacyConsent(
            hasAcceptedTerms: hasAcceptedTerms,
            hasAcceptedPrivacyPolicy: hasAcceptedPrivacyPolicy,
            hasAcceptedHIPAANotice: hasAcceptedHIPAANotice,
            consentDate: Date(),
            dataProcessingConsent: true,
            analyticsConsent: analyticsConsent,
            marketingConsent: false
        )

        // Create profile
        let profile = UserProfile(
            firstName: firstName.isEmpty ? nil : firstName,
            age: age,
            gender: selectedGender,
            timezone: TimeZone.current.identifier,
            language: "en"
        )

        // Create recovery goals
        let goals = selectedGoals.map { goalType in
            RecoveryGoal(
                title: goalType.rawValue,
                description: "Primary recovery goal",
                goalType: goalType
            )
        }

        // Create substance history
        var substanceHistory: [SubstanceHistory] = []
        if let substance = primarySubstance {
            let history = SubstanceHistory(
                substanceType: substance,
                frequencyOfUse: frequencyOfUse,
                yearsOfUse: 0,
                lastUsedDate: nil,
                sobrietyStartDate: sobrietyStartDate,
                notes: nil
            )
            substanceHistory.append(history)
        }

        // Create user
        let user = User(
            username: username,
            email: email.isEmpty ? nil : email,
            profile: profile,
            recoveryGoals: goals,
            substanceHistory: substanceHistory,
            privacyConsent: privacyConsent
        )

        return user
    }

    // MARK: - Goal Management

    func toggleGoal(_ goalType: GoalType) {
        if selectedGoals.contains(goalType) {
            selectedGoals.remove(goalType)
        } else {
            selectedGoals.insert(goalType)
        }
    }
}
