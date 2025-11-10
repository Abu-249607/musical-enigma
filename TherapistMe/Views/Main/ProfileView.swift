//
//  ProfileView.swift
//  Therapist.Me
//
//  User profile and settings
//

import SwiftUI

struct ProfileView: View {
    @StateObject private var viewModel = ProfileViewModel()
    @State private var showingSettings = false

    var body: some View {
        NavigationView {
            List {
                // User info section
                Section {
                    HStack {
                        Image(systemName: "person.circle.fill")
                            .font(.system(size: 60))
                            .foregroundColor(.blue)

                        VStack(alignment: .leading, spacing: 4) {
                            Text(viewModel.username)
                                .font(.title2)
                                .fontWeight(.bold)

                            if let firstName = viewModel.firstName {
                                Text(firstName)
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                        }
                    }
                    .padding(.vertical, 8)
                }

                // Progress section
                Section("Recovery Progress") {
                    if let daysSober = viewModel.daysSober {
                        LabeledContent("Days Sober", value: "\(daysSober)")
                    }

                    LabeledContent("Current Streak", value: "\(viewModel.currentStreak) days")
                    LabeledContent("Longest Streak", value: "\(viewModel.longestStreak) days")
                    LabeledContent("Mood Entries", value: "\(viewModel.moodEntries)")
                    LabeledContent("Journal Entries", value: "\(viewModel.journalEntries)")
                }

                // Goals section
                Section("Recovery Goals") {
                    ForEach(viewModel.goals, id: \.id) { goal in
                        NavigationLink(destination: GoalDetailView(goal: goal)) {
                            HStack {
                                Image(systemName: goal.isCompleted ? "checkmark.circle.fill" : "circle")
                                    .foregroundColor(goal.isCompleted ? .green : .gray)

                                Text(goal.title)
                            }
                        }
                    }

                    Button(action: {
                        // Add goal
                    }) {
                        Label("Add Goal", systemImage: "plus")
                    }
                }

                // Settings section
                Section("Settings") {
                    NavigationLink(destination: SettingsView()) {
                        Label("App Settings", systemImage: "gearshape")
                    }

                    NavigationLink(destination: PrivacySettingsView()) {
                        Label("Privacy & Security", systemImage: "lock.shield")
                    }

                    NavigationLink(destination: NotificationSettingsView()) {
                        Label("Notifications", systemImage: "bell")
                    }
                }

                // Support section
                Section("Support & Resources") {
                    Button(action: {
                        // Open resources
                    }) {
                        Label("Crisis Resources", systemImage: "cross.case")
                    }

                    Button(action: {
                        // Open help
                    }) {
                        Label("Help & FAQ", systemImage: "questionmark.circle")
                    }

                    Button(action: {
                        // Export data
                    }) {
                        Label("Export My Data", systemImage: "square.and.arrow.up")
                    }
                }

                // Account section
                Section {
                    Button(role: .destructive, action: {
                        viewModel.logout()
                    }) {
                        Label("Sign Out", systemImage: "arrow.right.square")
                    }
                }
            }
            .navigationTitle("Profile")
        }
        .onAppear {
            viewModel.loadProfile()
        }
    }
}

struct GoalDetailView: View {
    let goal: RecoveryGoal

    var body: some View {
        List {
            Section("Details") {
                LabeledContent("Title", value: goal.title)
                LabeledContent("Type", value: goal.goalType.rawValue)
                LabeledContent("Status", value: goal.isCompleted ? "Completed" : "In Progress")
            }

            if !goal.milestones.isEmpty {
                Section("Milestones") {
                    ForEach(goal.milestones) { milestone in
                        HStack {
                            Image(systemName: milestone.isCompleted ? "checkmark.circle.fill" : "circle")
                                .foregroundColor(milestone.isCompleted ? .green : .gray)

                            Text(milestone.title)
                        }
                    }
                }
            }
        }
        .navigationTitle("Goal")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct SettingsView: View {
    var body: some View {
        List {
            Section("Appearance") {
                // Add settings options
                Text("Coming soon")
            }
        }
        .navigationTitle("Settings")
    }
}

struct PrivacySettingsView: View {
    var body: some View {
        List {
            Section("Data Protection") {
                LabeledContent("Encryption", value: "AES-256")
                LabeledContent("Authentication", value: "Biometric")
            }

            Section("Your Rights") {
                Button("View Privacy Policy") {
                    // Show policy
                }
                Button("Download My Data") {
                    // Export data
                }
                Button("Delete My Account", role: .destructive) {
                    // Delete account
                }
            }
        }
        .navigationTitle("Privacy & Security")
    }
}

struct NotificationSettingsView: View {
    @State private var dailyReminder = true
    @State private var motivational = true
    @State private var milestones = true

    var body: some View {
        List {
            Section("Notifications") {
                Toggle("Daily Check-in Reminder", isOn: $dailyReminder)
                Toggle("Motivational Messages", isOn: $motivational)
                Toggle("Milestone Alerts", isOn: $milestones)
            }
        }
        .navigationTitle("Notifications")
    }
}

// MARK: - ViewModel

class ProfileViewModel: ObservableObject {
    @Published var username = ""
    @Published var firstName: String?
    @Published var daysSober: Int?
    @Published var currentStreak = 0
    @Published var longestStreak = 0
    @Published var moodEntries = 0
    @Published var journalEntries = 0
    @Published var goals: [RecoveryGoal] = []

    func loadProfile() {
        guard let user = AppCoordinator.shared.getCurrentUser() else { return }

        username = user.username
        firstName = user.profile.firstName
        goals = user.recoveryGoals

        // Calculate days sober
        if let sobrietyDate = user.substanceHistory.first?.sobrietyStartDate {
            daysSober = Calendar.current.dateComponents([.day], from: sobrietyDate, to: Date()).day
        }

        // Load statistics (simplified)
        currentStreak = 7
        longestStreak = 14
        moodEntries = 42
        journalEntries = 18
    }

    func logout() {
        AppCoordinator.shared.logout()
    }
}
