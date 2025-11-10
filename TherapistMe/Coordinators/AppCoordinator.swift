//
//  AppCoordinator.swift
//  Therapist.Me
//
//  Central navigation and state management
//

import Foundation
import SwiftUI

class AppCoordinator: ObservableObject {
    static let shared = AppCoordinator()

    @Published var currentState: AppState = .launching
    @Published var hasCompletedOnboarding: Bool = false
    @Published var isAuthenticated: Bool = false

    private let userDefaults = UserDefaults.standard
    private let storageService = SecureStorageService.shared

    private init() {}

    // MARK: - App State

    enum AppState {
        case launching
        case onboarding
        case authentication
        case main
        case locked
    }

    // MARK: - State Management

    func determineInitialState() {
        // Check if onboarding is completed
        hasCompletedOnboarding = userDefaults.bool(forKey: "hasCompletedOnboarding")

        // Check if user exists and is authenticated
        if let userIdString = userDefaults.string(forKey: "currentUserId"),
           let userId = UUID(uuidString: userIdString) {
            // User exists, check authentication
            if SessionManager.shared.isSessionActive {
                currentState = .main
            } else {
                currentState = .authentication
            }
        } else if hasCompletedOnboarding {
            // Completed onboarding but no user (shouldn't happen normally)
            currentState = .onboarding
        } else {
            // First launch
            currentState = .onboarding
        }

        AuditLogger.shared.log(
            event: .appLaunched,
            details: "App launched with state: \(currentState)",
            severity: .low
        )
    }

    func completeOnboarding(user: User) {
        // Save user
        _ = storageService.save(user, withKey: "user_\(user.id.uuidString)", userId: user.id.uuidString)

        // Update state
        hasCompletedOnboarding = true
        userDefaults.set(true, forKey: "hasCompletedOnboarding")
        userDefaults.set(user.id.uuidString, forKey: "currentUserId")

        // Start session
        SessionManager.shared.startSession(user: user)

        // Navigate to main app
        currentState = .main

        AuditLogger.shared.log(
            event: .phiCreated,
            details: "Onboarding completed, user created",
            userId: user.id.uuidString,
            severity: .medium
        )
    }

    func authenticate(user: User) {
        SessionManager.shared.startSession(user: user)
        isAuthenticated = true
        currentState = .main
    }

    func logout() {
        SessionManager.shared.endSession()
        isAuthenticated = false
        currentState = .authentication

        AuditLogger.shared.log(
            event: .logoutPerformed,
            details: "User logged out",
            severity: .medium
        )
    }

    func resetApp() {
        // Clear all data
        SessionManager.shared.endSession()
        userDefaults.removeObject(forKey: "hasCompletedOnboarding")
        userDefaults.removeObject(forKey: "currentUserId")

        hasCompletedOnboarding = false
        isAuthenticated = false
        currentState = .onboarding

        AuditLogger.shared.log(
            event: .phiDeleted,
            details: "App reset performed",
            severity: .critical
        )
    }

    // MARK: - User Management

    func getCurrentUser() -> User? {
        guard let userIdString = userDefaults.string(forKey: "currentUserId"),
              let userId = UUID(uuidString: userIdString) else {
            return nil
        }

        return storageService.retrieve(User.self, forKey: "user_\(userIdString)", userId: userId.uuidString)
    }

    func updateUser(_ user: User) {
        _ = storageService.update(user, forKey: "user_\(user.id.uuidString)", userId: user.id.uuidString)

        AuditLogger.shared.log(
            event: .phiModified,
            details: "User profile updated",
            userId: user.id.uuidString,
            severity: .medium
        )
    }
}
