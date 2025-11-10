//
//  OnboardingCoordinatorView.swift
//  Therapist.Me
//
//  Multi-step onboarding flow
//

import SwiftUI

struct OnboardingCoordinatorView: View {
    @StateObject private var viewModel = OnboardingViewModel()
    @EnvironmentObject var appCoordinator: AppCoordinator

    var body: some View {
        TabView(selection: $viewModel.currentStep) {
            WelcomeView(viewModel: viewModel)
                .tag(OnboardingStep.welcome)

            PrivacyConsentView(viewModel: viewModel)
                .tag(OnboardingStep.privacyConsent)

            ProfileSetupView(viewModel: viewModel)
                .tag(OnboardingStep.profileSetup)

            GoalsSetupView(viewModel: viewModel)
                .tag(OnboardingStep.goalsSetup)

            SubstanceHistoryView(viewModel: viewModel)
                .tag(OnboardingStep.substanceHistory)

            CompletionView(viewModel: viewModel)
                .tag(OnboardingStep.completion)
        }
        .tabViewStyle(.page(indexDisplayMode: .always))
        .indexViewStyle(.page(backgroundDisplayMode: .always))
        .onChange(of: viewModel.isOnboardingComplete) { _, isComplete in
            if isComplete, let user = viewModel.createUser() {
                appCoordinator.completeOnboarding(user: user)
            }
        }
    }
}

// MARK: - Onboarding Steps

enum OnboardingStep: Int, CaseIterable {
    case welcome = 0
    case privacyConsent
    case profileSetup
    case goalsSetup
    case substanceHistory
    case completion
}

// MARK: - Welcome View

struct WelcomeView: View {
    @ObservedObject var viewModel: OnboardingViewModel

    var body: some View {
        VStack(spacing: 30) {
            Spacer()

            Image(systemName: "heart.text.square.fill")
                .font(.system(size: 100))
                .foregroundColor(.blue)

            Text("Welcome to Therapist.Me")
                .font(.largeTitle)
                .fontWeight(.bold)
                .multilineTextAlignment(.center)

            Text("Your personal companion for addiction recovery and mental wellness")
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)

            Spacer()

            Button("Get Started") {
                viewModel.nextStep()
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)

            Spacer()
        }
        .padding()
    }
}

// MARK: - Privacy Consent View

struct PrivacyConsentView: View {
    @ObservedObject var viewModel: OnboardingViewModel
    @State private var scrollOffset: CGFloat = 0

    var body: some View {
        VStack(spacing: 20) {
            Text("Privacy & Consent")
                .font(.title)
                .fontWeight(.bold)
                .padding(.top)

            ScrollView {
                VStack(alignment: .leading, spacing: 15) {
                    Text("HIPAA Compliance Notice")
                        .font(.headline)

                    Text("""
                    Therapist.Me is committed to protecting your privacy and health information in compliance with HIPAA regulations.

                    Key Privacy Features:
                    • AES-256 encryption for all data
                    • Secure biometric authentication
                    • Automatic session timeout
                    • Tamper-proof audit logs
                    • No third-party data sharing

                    Your Rights:
                    • Access your data anytime
                    • Request data deletion
                    • Export your information
                    • Control what data is collected
                    """)
                    .font(.body)
                    .foregroundColor(.secondary)

                    Divider()

                    Text("Consent Agreement")
                        .font(.headline)

                    ConsentToggle(
                        isOn: $viewModel.hasAcceptedTerms,
                        title: "Terms of Service",
                        description: "I accept the Terms of Service"
                    )

                    ConsentToggle(
                        isOn: $viewModel.hasAcceptedPrivacyPolicy,
                        title: "Privacy Policy",
                        description: "I accept the Privacy Policy"
                    )

                    ConsentToggle(
                        isOn: $viewModel.hasAcceptedHIPAANotice,
                        title: "HIPAA Notice",
                        description: "I acknowledge the HIPAA Notice of Privacy Practices"
                    )

                    ConsentToggle(
                        isOn: $viewModel.analyticsConsent,
                        title: "Analytics (Optional)",
                        description: "Help improve the app with anonymous usage data"
                    )
                }
                .padding()
            }

            HStack {
                Button("Back") {
                    viewModel.previousStep()
                }
                .buttonStyle(.bordered)

                Spacer()

                Button("Continue") {
                    viewModel.nextStep()
                }
                .buttonStyle(.borderedProminent)
                .disabled(!viewModel.canProceedFromPrivacy())
            }
            .padding()
        }
    }
}

struct ConsentToggle: View {
    @Binding var isOn: Bool
    let title: String
    let description: String

    var body: some View {
        Toggle(isOn: $isOn) {
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                Text(description)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 8)
    }
}

// MARK: - Profile Setup View

struct ProfileSetupView: View {
    @ObservedObject var viewModel: OnboardingViewModel

    var body: some View {
        VStack(spacing: 20) {
            Text("Tell Us About You")
                .font(.title)
                .fontWeight(.bold)
                .padding(.top)

            Form {
                Section("Basic Information") {
                    TextField("Username", text: $viewModel.username)
                    TextField("First Name (Optional)", text: $viewModel.firstName)
                    TextField("Email (Optional)", text: $viewModel.email)
                }

                Section("Demographics (Optional)") {
                    Picker("Gender", selection: $viewModel.selectedGender) {
                        Text("Prefer not to say").tag(Gender?.none)
                        ForEach(Gender.allCases, id: \.self) { gender in
                            Text(gender.rawValue).tag(Gender?.some(gender))
                        }
                    }

                    Stepper("Age: \(viewModel.age ?? 0)", value: Binding(
                        get: { viewModel.age ?? 18 },
                        set: { viewModel.age = $0 }
                    ), in: 13...120)
                }
            }

            HStack {
                Button("Back") {
                    viewModel.previousStep()
                }
                .buttonStyle(.bordered)

                Spacer()

                Button("Continue") {
                    viewModel.nextStep()
                }
                .buttonStyle(.borderedProminent)
                .disabled(viewModel.username.isEmpty)
            }
            .padding()
        }
    }
}

// MARK: - Goals Setup View

struct GoalsSetupView: View {
    @ObservedObject var viewModel: OnboardingViewModel

    var body: some View {
        VStack(spacing: 20) {
            Text("Your Recovery Goals")
                .font(.title)
                .fontWeight(.bold)
                .padding(.top)

            Text("Select your primary goals for recovery")
                .font(.subheadline)
                .foregroundColor(.secondary)

            ScrollView {
                LazyVStack(spacing: 15) {
                    ForEach(GoalType.allCases, id: \.self) { goalType in
                        GoalSelectionCard(
                            goalType: goalType,
                            isSelected: viewModel.selectedGoals.contains(goalType),
                            onTap: {
                                viewModel.toggleGoal(goalType)
                            }
                        )
                    }
                }
                .padding()
            }

            HStack {
                Button("Back") {
                    viewModel.previousStep()
                }
                .buttonStyle(.bordered)

                Spacer()

                Button("Continue") {
                    viewModel.nextStep()
                }
                .buttonStyle(.borderedProminent)
                .disabled(viewModel.selectedGoals.isEmpty)
            }
            .padding()
        }
    }
}

struct GoalSelectionCard: View {
    let goalType: GoalType
    let isSelected: Bool
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(goalType.rawValue)
                        .font(.headline)
                        .foregroundColor(.primary)
                }

                Spacer()

                if isSelected {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.blue)
                        .font(.title2)
                }
            }
            .padding()
            .background(isSelected ? Color.blue.opacity(0.1) : Color.gray.opacity(0.1))
            .cornerRadius(12)
        }
    }
}

// MARK: - Substance History View

struct SubstanceHistoryView: View {
    @ObservedObject var viewModel: OnboardingViewModel

    var body: some View {
        VStack(spacing: 20) {
            Text("Substance History")
                .font(.title)
                .fontWeight(.bold)
                .padding(.top)

            Text("This information helps personalize your recovery journey")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)

            Form {
                Section("Primary Substance (Optional)") {
                    Picker("Substance Type", selection: $viewModel.primarySubstance) {
                        Text("None").tag(SubstanceType?.none)
                        ForEach(SubstanceType.allCases, id: \.self) { substance in
                            Text(substance.rawValue).tag(SubstanceType?.some(substance))
                        }
                    }

                    if viewModel.primarySubstance != nil {
                        Picker("Frequency", selection: $viewModel.frequencyOfUse) {
                            ForEach(FrequencyOfUse.allCases, id: \.self) { frequency in
                                Text(frequency.rawValue).tag(frequency)
                            }
                        }

                        DatePicker("Sobriety Start Date", selection: $viewModel.sobrietyStartDate, displayedComponents: .date)
                    }
                }
            }

            HStack {
                Button("Back") {
                    viewModel.previousStep()
                }
                .buttonStyle(.bordered)

                Spacer()

                Button("Continue") {
                    viewModel.nextStep()
                }
                .buttonStyle(.borderedProminent)
            }
            .padding()
        }
    }
}

// MARK: - Completion View

struct CompletionView: View {
    @ObservedObject var viewModel: OnboardingViewModel

    var body: some View {
        VStack(spacing: 30) {
            Spacer()

            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 100))
                .foregroundColor(.green)

            Text("You're All Set!")
                .font(.largeTitle)
                .fontWeight(.bold)

            Text("Your recovery journey begins now. We're here to support you every step of the way.")
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)

            Spacer()

            Button("Start Your Journey") {
                viewModel.completeOnboarding()
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)

            Spacer()
        }
        .padding()
    }
}
