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
                            color: .blue
                        )
                        
                        QuickActionCard(
                            title: "Journal Entry",
                            icon: "square.and.pencil",
                            color: .green
                        )
                        
                        QuickActionCard(
                            title: "Track Craving",
                            icon: "bolt.fill",
                            color: .orange
                        )
                        
                        QuickActionCard(
                            title: "Talk to AI Therapist",
                            icon: "message.fill",
                            color: .purple
                        )
                    }
                    .padding(.horizontal)
                    
                    Spacer()
                }
            }
            .navigationTitle("Home")
        }
    }
}

struct QuickActionCard: View {
    let title: String
    let icon: String
    let color: Color
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.white)
                .frame(width: 50, height: 50)
                .background(color)
                .cornerRadius(12)
            
            Text(title)
                .font(.headline)
            
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
