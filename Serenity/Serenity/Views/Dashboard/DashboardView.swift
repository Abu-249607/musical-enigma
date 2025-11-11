import SwiftUI

// HIPAA Compliance: Main dashboard with secure navigation
// Headspace/Ahead inspired design: minimalist, calming, accessible

struct DashboardView: View {
    @EnvironmentObject var sessionManager: SessionManager
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            HomeView()
                .tabItem {
                    Label("Home", systemImage: "house.fill")
                }
                .tag(0)
            
            MoodTrackerView()
                .tabItem {
                    Label("Mood", systemImage: "chart.line.uptrend.xyaxis")
                }
                .tag(1)
            
            JournalListView()
                .tabItem {
                    Label("Journal", systemImage: "book.fill")
                }
                .tag(2)
            
            AITherapistChatView()
                .tabItem {
                    Label("Chat", systemImage: "message.fill")
                }
                .tag(3)
            
            ProfileView()
                .tabItem {
                    Label("Profile", systemImage: "person.fill")
                }
                .tag(4)
        }
        .accentColor(.blue)
        .onAppear {
            sessionManager.updateActivity()
        }
    }
}

struct HomeView: View {
    @EnvironmentObject var sessionManager: SessionManager
    @State private var showingMoodTracker = false
    @State private var showingJournal = false
    @State private var showingCravingLog = false
    @State private var showingChat = false

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 25) {
                    // Welcome header
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Welcome back,")
                            .font(.title3)
                            .foregroundColor(.secondary)

                        Text(sessionManager.currentUser?.firstName ?? "User")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()

                    // Quick actions
                    VStack(spacing: 15) {
                        QuickActionCard(
                            title: "Log Mood",
                            icon: "face.smiling",
                            color: .blue,
                            action: { showingMoodTracker = true }
                        )

                        QuickActionCard(
                            title: "Journal Entry",
                            icon: "square.and.pencil",
                            color: .green,
                            action: { showingJournal = true }
                        )

                        QuickActionCard(
                            title: "Track Craving",
                            icon: "bolt.fill",
                            color: .orange,
                            action: { showingCravingLog = true }
                        )

                        QuickActionCard(
                            title: "Talk to AI Therapist",
                            icon: "message.fill",
                            color: .purple,
                            action: { showingChat = true }
                        )
                    }
                    .padding(.horizontal)

                    Spacer()
                }
            }
            .navigationTitle("Home")
            .sheet(isPresented: $showingMoodTracker) {
                MoodEntryView()
            }
            .sheet(isPresented: $showingJournal) {
                JournalEntryView()
            }
            .sheet(isPresented: $showingCravingLog) {
                CravingLogView()
            }
            .sheet(isPresented: $showingChat) {
                AITherapistChatView()
            }
        }
    }
}

struct QuickActionCard: View {
    let title: String
    let icon: String
    let color: Color
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(.white)
                    .frame(width: 50, height: 50)
                    .background(color)
                    .cornerRadius(12)

                Text(title)
                    .font(.headline)
                    .foregroundColor(.primary)

                Spacer()

                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color(.systemBackground))
            .cornerRadius(12)
            .shadow(color: .gray.opacity(0.2), radius: 5)
        }
    }
}

struct ProfileView: View {
    @EnvironmentObject var sessionManager: SessionManager
    
    var body: some View {
        NavigationView {
            List {
                Section {
                    HStack {
                        Circle()
                            .fill(Color.blue)
                            .frame(width: 60, height: 60)
                            .overlay(
                                Text(sessionManager.currentUser?.initials ?? "U")
                                    .foregroundColor(.white)
                                    .font(.title2)
                            )
                        
                        VStack(alignment: .leading) {
                            Text(sessionManager.currentUser?.fullName ?? "User")
                                .font(.headline)
                            Text(sessionManager.currentUser?.email ?? "")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }
                
                Section("Privacy & Security") {
                    NavigationLink("Privacy Settings") {
                        PrivacySettingsView()
                    }
                    NavigationLink("Export My Data") {
                        DataExportView()
                    }
                }
                
                Section {
                    Button("Log Out", role: .destructive) {
                        sessionManager.endSession()
                    }
                }
            }
            .navigationTitle("Profile")
        }
    }
}

// Placeholder views
struct MoodTrackerView: View {
    var body: some View {
        NavigationView {
            Text("Mood Tracker")
                .navigationTitle("Mood")
        }
    }
}

struct JournalListView: View {
    var body: some View {
        NavigationView {
            Text("Journal Entries")
                .navigationTitle("Journal")
        }
    }
}

struct AITherapistChatView: View {
    var body: some View {
        NavigationView {
            VStack {
                Text("AI Therapist")
                    .font(.title)
                Text("Coming soon...")
                    .foregroundColor(.secondary)
            }
            .navigationTitle("Chat")
        }
    }
}

struct PrivacySettingsView: View {
    var body: some View {
        List {
            Text("Privacy settings...")
        }
        .navigationTitle("Privacy Settings")
    }
}

struct DataExportView: View {
    var body: some View {
        VStack {
            Text("Export your data")
                .font(.title)
            Button("Export as JSON") {}
                .buttonStyle(.borderedProminent)
        }
        .navigationTitle("Data Export")
    }
}

// MARK: - Entry Forms

struct MoodEntryView: View {
    @Environment(\.dismiss) var dismiss
    @State private var selectedMood: String = "neutral"
    @State private var energy: Double = 5
    @State private var notes: String = ""

    let moods = [
        ("veryHappy", "😊", "Very Happy"),
        ("happy", "🙂", "Happy"),
        ("neutral", "😐", "Neutral"),
        ("sad", "🙁", "Sad"),
        ("anxious", "😰", "Anxious")
    ]

    var body: some View {
        NavigationView {
            Form {
                Section("How are you feeling?") {
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 20) {
                            ForEach(moods, id: \.0) { mood in
                                VStack {
                                    Text(mood.1)
                                        .font(.system(size: 44))
                                    Text(mood.2)
                                        .font(.caption)
                                }
                                .padding()
                                .background(selectedMood == mood.0 ? Color.blue.opacity(0.2) : Color.clear)
                                .cornerRadius(12)
                                .onTapGesture {
                                    selectedMood = mood.0
                                }
                            }
                        }
                        .padding(.vertical)
                    }
                }

                Section("Energy Level") {
                    VStack {
                        Slider(value: $energy, in: 1...10, step: 1)
                        Text("Energy: \(Int(energy))/10")
                            .font(.caption)
                    }
                }

                Section("Notes (Optional)") {
                    TextEditor(text: $notes)
                        .frame(height: 100)
                }

                Button("Save Mood Entry") {
                    // TODO: Save mood entry
                    AuditLogger.shared.log(.moodLogged, metadata: ["mood": selectedMood])
                    dismiss()
                }
                .buttonStyle(.borderedProminent)
            }
            .navigationTitle("Log Mood")
            .navigationBarItems(trailing: Button("Cancel") { dismiss() })
        }
    }
}

struct JournalEntryView: View {
    @Environment(\.dismiss) var dismiss
    @State private var title: String = ""
    @State private var content: String = ""
    @State private var journalType: String = "daily"

    var body: some View {
        NavigationView {
            Form {
                Section("Journal Type") {
                    Picker("Type", selection: $journalType) {
                        Text("Daily Journal").tag("daily")
                        Text("CBT Worksheet").tag("cbt")
                        Text("Gratitude").tag("gratitude")
                        Text("Crisis Notes").tag("crisis")
                    }
                    .pickerStyle(.segmented)
                }

                Section("Title") {
                    TextField("Entry title", text: $title)
                }

                Section("Content") {
                    TextEditor(text: $content)
                        .frame(minHeight: 200)
                }

                Button("Save Entry") {
                    // TODO: Save journal entry with encryption
                    AuditLogger.shared.log(.journalCreated, metadata: ["type": journalType])
                    dismiss()
                }
                .buttonStyle(.borderedProminent)
                .disabled(title.isEmpty || content.isEmpty)
            }
            .navigationTitle("New Journal Entry")
            .navigationBarItems(trailing: Button("Cancel") { dismiss() })
        }
    }
}

struct CravingLogView: View {
    @Environment(\.dismiss) var dismiss
    @State private var substance: String = "alcohol"
    @State private var intensity: Double = 5
    @State private var triggers: String = ""
    @State private var copingStrategies: String = ""
    @State private var didUse: Bool = false

    var body: some View {
        NavigationView {
            Form {
                Section("Substance") {
                    Picker("Type", selection: $substance) {
                        Text("Alcohol").tag("alcohol")
                        Text("Nicotine").tag("nicotine")
                        Text("Cannabis").tag("cannabis")
                        Text("Other").tag("other")
                    }
                    .pickerStyle(.menu)
                }

                Section("Craving Intensity") {
                    VStack {
                        Slider(value: $intensity, in: 1...10, step: 1)
                        HStack {
                            Text("Low")
                            Spacer()
                            Text("\(Int(intensity))/10")
                                .fontWeight(.bold)
                            Spacer()
                            Text("High")
                        }
                        .font(.caption)
                    }
                }

                Section("What triggered this craving?") {
                    TextEditor(text: $triggers)
                        .frame(height: 80)
                }

                Section("Coping strategies used") {
                    TextEditor(text: $copingStrategies)
                        .frame(height: 80)
                }

                Section {
                    Toggle("I used the substance", isOn: $didUse)
                        .foregroundColor(didUse ? .red : .primary)
                }

                Button("Save Craving Log") {
                    // TODO: Save craving log
                    AuditLogger.shared.log(.cravingLogged, metadata: [
                        "substance": substance,
                        "intensity": Int(intensity),
                        "didUse": didUse
                    ])
                    dismiss()
                }
                .buttonStyle(.borderedProminent)
            }
            .navigationTitle("Track Craving")
            .navigationBarItems(trailing: Button("Cancel") { dismiss() })
        }
    }
}

// MARK: - Audit Events Extension

extension AuditEvent {
    static let moodLogged = AuditEvent(type: "MOOD_LOGGED")
    static let journalCreated = AuditEvent(type: "JOURNAL_CREATED")
    static let cravingLogged = AuditEvent(type: "CRAVING_LOGGED")
}
