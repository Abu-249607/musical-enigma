//
//  ContentView.swift
//  Therapist.Me
//
//  Main app routing view with authentication checks
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appCoordinator: AppCoordinator
    @EnvironmentObject var sessionManager: SessionManager
    @StateObject private var authViewModel = AuthenticationViewModel()

    var body: some View {
        ZStack {
            // Main navigation based on app state
            switch appCoordinator.currentState {
            case .launching:
                LaunchView()

            case .onboarding:
                OnboardingCoordinatorView()

            case .authentication:
                AuthenticationView(viewModel: authViewModel)

            case .main:
                MainTabView()

            case .locked:
                SessionLockedView()
            }

            // HIPAA Compliance: Session timeout overlay
            if sessionManager.isSessionExpired {
                SessionExpiredOverlay()
            }
        }
        .onAppear {
            appCoordinator.determineInitialState()
        }
    }
}

// MARK: - Launch View
struct LaunchView: View {
    var body: some View {
        ZStack {
            Color("PrimaryBackground")
                .ignoresSafeArea()

            VStack(spacing: 20) {
                Image(systemName: "heart.text.square.fill")
                    .font(.system(size: 80))
                    .foregroundColor(.blue)

                Text("Therapist.Me")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Text("Your Recovery Journey Companion")
                    .font(.subheadline)
                    .foregroundColor(.secondary)

                ProgressView()
                    .padding(.top)
            }
        }
    }
}

// MARK: - Session Locked View
struct SessionLockedView: View {
    @EnvironmentObject var sessionManager: SessionManager

    var body: some View {
        ZStack {
            Color.black.opacity(0.9)
                .ignoresSafeArea()

            VStack(spacing: 30) {
                Image(systemName: "lock.shield.fill")
                    .font(.system(size: 60))
                    .foregroundColor(.white)

                Text("Session Locked")
                    .font(.title)
                    .foregroundColor(.white)

                Text("For your security, please authenticate to continue")
                    .font(.body)
                    .foregroundColor(.white.opacity(0.8))
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)

                Button(action: {
                    sessionManager.authenticate()
                }) {
                    HStack {
                        Image(systemName: "faceid")
                        Text("Unlock")
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(12)
                }
                .padding(.horizontal, 40)
            }
        }
    }
}

// MARK: - Session Expired Overlay
struct SessionExpiredOverlay: View {
    @EnvironmentObject var sessionManager: SessionManager

    var body: some View {
        ZStack {
            Color.black.opacity(0.8)
                .ignoresSafeArea()

            VStack(spacing: 20) {
                Image(systemName: "clock.badge.exclamationmark")
                    .font(.system(size: 50))
                    .foregroundColor(.orange)

                Text("Session Expired")
                    .font(.title2)
                    .foregroundColor(.white)

                Text("Your session has expired for security. Please authenticate again.")
                    .font(.body)
                    .foregroundColor(.white.opacity(0.9))
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)

                Button("Authenticate") {
                    sessionManager.renewSession()
                }
                .buttonStyle(.borderedProminent)
            }
            .padding()
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(AppCoordinator.shared)
        .environmentObject(SessionManager.shared)
}
