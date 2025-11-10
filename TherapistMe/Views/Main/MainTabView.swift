//
//  MainTabView.swift
//  Therapist.Me
//
//  Main navigation interface with all app features
//

import SwiftUI

struct MainTabView: View {
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            // Home/Dashboard
            DashboardView()
                .tabItem {
                    Label("Home", systemImage: "house.fill")
                }
                .tag(0)

            // Mood Tracker
            MoodTrackerView()
                .tabItem {
                    Label("Mood", systemImage: "heart.text.square")
                }
                .tag(1)

            // Chat/Therapist
            ChatView()
                .tabItem {
                    Label("Therapist", systemImage: "message.fill")
                }
                .tag(2)

            // Exercises
            ExercisesView()
                .tabItem {
                    Label("Exercises", systemImage: "figure.mind.and.body")
                }
                .tag(3)

            // Profile
            ProfileView()
                .tabItem {
                    Label("Profile", systemImage: "person.fill")
                }
                .tag(4)
        }
        .accentColor(.blue)
    }
}

// MARK: - Dashboard View

struct DashboardView: View {
    @StateObject private var viewModel = DashboardViewModel()

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Welcome header
                    WelcomeHeader(username: viewModel.username)

                    // Crisis button (always visible)
                    CrisisButton()

                    // Sobriety counter
                    if let daysSober = viewModel.daysSober {
                        SobrietyCard(daysSober: daysSober)
                    }

                    // Current streak
                    StreakCard(
                        currentStreak: viewModel.currentStreak,
                        longestStreak: viewModel.longestStreak
                    )

                    // Quick actions
                    QuickActionsGrid()

                    // Recent achievements
                    if !viewModel.recentAchievements.isEmpty {
                        AchievementsSection(achievements: viewModel.recentAchievements)
                    }

                    // Mood trend
                    MoodTrendCard(moodData: viewModel.moodTrend)
                }
                .padding()
            }
            .navigationTitle("Dashboard")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        // Settings action
                    }) {
                        Image(systemName: "gearshape.fill")
                    }
                }
            }
        }
        .onAppear {
            viewModel.loadData()
        }
    }
}

struct WelcomeHeader: View {
    let username: String

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("Hello, \(username)")
                    .font(.title2)
                    .fontWeight(.bold)

                Text("How are you feeling today?")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }

            Spacer()
        }
    }
}

struct CrisisButton: View {
    @State private var showingCrisisToolkit = false

    var body: some View {
        Button(action: {
            showingCrisisToolkit = true
        }) {
            HStack {
                Image(systemName: "exclamationmark.triangle.fill")
                Text("Need Help Now?")
                    .fontWeight(.semibold)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(Color.red)
            .foregroundColor(.white)
            .cornerRadius(12)
        }
        .sheet(isPresented: $showingCrisisToolkit) {
            CrisisToolkitView()
        }
    }
}

struct SobrietyCard: View {
    let daysSober: Int

    var body: some View {
        VStack(spacing: 10) {
            Text("\(daysSober)")
                .font(.system(size: 60, weight: .bold))
                .foregroundColor(.green)

            Text("Days Sober")
                .font(.headline)
                .foregroundColor(.secondary)

            Text("Keep going! Every day is a victory.")
                .font(.caption)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color.green.opacity(0.1))
        .cornerRadius(16)
    }
}

struct StreakCard: View {
    let currentStreak: Int
    let longestStreak: Int

    var body: some View {
        HStack {
            VStack {
                Text("\(currentStreak)")
                    .font(.title)
                    .fontWeight(.bold)
                    .foregroundColor(.orange)

                Text("Current Streak")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .frame(maxWidth: .infinity)

            Divider()

            VStack {
                Text("\(longestStreak)")
                    .font(.title)
                    .fontWeight(.bold)
                    .foregroundColor(.purple)

                Text("Longest Streak")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .frame(maxWidth: .infinity)
        }
        .padding()
        .background(Color.gray.opacity(0.1))
        .cornerRadius(12)
    }
}

struct QuickActionsGrid: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Quick Actions")
                .font(.headline)

            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 15) {
                QuickActionButton(icon: "heart.text.square", title: "Log Mood", color: .blue)
                QuickActionButton(icon: "book", title: "Journal", color: .green)
                QuickActionButton(icon: "wind", title: "Breathe", color: .cyan)
                QuickActionButton(icon: "chart.line.uptrend.xyaxis", title: "Progress", color: .purple)
            }
        }
    }
}

struct QuickActionButton: View {
    let icon: String
    let title: String
    let color: Color

    var body: some View {
        Button(action: {
            // Action
        }) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title)
                Text(title)
                    .font(.caption)
                    .fontWeight(.medium)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(color.opacity(0.1))
            .foregroundColor(color)
            .cornerRadius(12)
        }
    }
}

struct AchievementsSection: View {
    let achievements: [Achievement]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Recent Achievements")
                .font(.headline)

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 15) {
                    ForEach(achievements) { achievement in
                        AchievementBadge(achievement: achievement)
                    }
                }
            }
        }
    }
}

struct AchievementBadge: View {
    let achievement: Achievement

    var body: some View {
        VStack {
            Text(achievement.icon)
                .font(.largeTitle)

            Text(achievement.title)
                .font(.caption)
                .fontWeight(.medium)
                .multilineTextAlignment(.center)
        }
        .frame(width: 100, height: 100)
        .background(Color.yellow.opacity(0.2))
        .cornerRadius(12)
    }
}

struct MoodTrendCard: View {
    let moodData: [MoodDataPoint]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("7-Day Mood Trend")
                .font(.headline)

            // Simplified chart placeholder
            HStack(alignment: .bottom, spacing: 8) {
                ForEach(moodData.prefix(7)) { dataPoint in
                    VStack {
                        RoundedRectangle(cornerRadius: 4)
                            .fill(Color.blue)
                            .frame(width: 30, height: CGFloat(dataPoint.moodScore * 20))

                        Text(dataPoint.date, style: .date)
                            .font(.caption2)
                            .rotationEffect(.degrees(-45))
                    }
                }
            }
            .frame(height: 150)
            .padding()
        }
        .background(Color.gray.opacity(0.1))
        .cornerRadius(12)
    }
}

// MARK: - Dashboard ViewModel

class DashboardViewModel: ObservableObject {
    @Published var username = ""
    @Published var daysSober: Int? = nil
    @Published var currentStreak = 0
    @Published var longestStreak = 0
    @Published var recentAchievements: [Achievement] = []
    @Published var moodTrend: [MoodDataPoint] = []

    func loadData() {
        // Load user data
        if let user = AppCoordinator.shared.getCurrentUser() {
            username = user.profile.firstName ?? user.username

            // Calculate days sober
            if let sobrietyDate = user.substanceHistory.first?.sobrietyStartDate {
                daysSober = Calendar.current.dateComponents([.day], from: sobrietyDate, to: Date()).day
            }

            // Load progress data
            loadProgress(userId: user.id)

            // Load achievements
            loadAchievements(userId: user.id)

            // Load mood trend
            loadMoodTrend(userId: user.id)
        }
    }

    private func loadProgress(userId: UUID) {
        // In production, load from secure storage
        currentStreak = 7
        longestStreak = 14
    }

    private func loadAchievements(userId: UUID) {
        // Load recent achievements
        recentAchievements = Achievement.predefinedAchievements.prefix(3).map { $0 }
    }

    private func loadMoodTrend(userId: UUID) {
        // Generate sample mood data for last 7 days
        let calendar = Calendar.current
        for i in 0..<7 {
            if let date = calendar.date(byAdding: .day, value: -i, to: Date()) {
                moodTrend.append(MoodDataPoint(date: date, moodScore: Int.random(in: 2...5)))
            }
        }
    }
}
