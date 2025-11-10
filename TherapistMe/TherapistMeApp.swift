//
//  TherapistMeApp.swift
//  Therapist.Me
//
//  A HIPAA-compliant addiction recovery and mental health support app
//  Features: CBT, Motivational Interviewing, Crisis Support, Progress Tracking
//

import SwiftUI

@main
struct TherapistMeApp: App {
    // MARK: - Dependencies
    @StateObject private var appCoordinator = AppCoordinator.shared
    @StateObject private var securityManager = SecurityManager.shared
    @StateObject private var sessionManager = SessionManager.shared

    // MARK: - App Lifecycle
    @Environment(\.scenePhase) private var scenePhase

    init() {
        // Initialize security services on app launch
        // HIPAA Compliance: Set up encryption and audit logging
        setupSecurity()
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appCoordinator)
                .environmentObject(securityManager)
                .environmentObject(sessionManager)
                .onAppear {
                    // HIPAA Compliance: Log app access
                    AuditLogger.shared.log(event: .appLaunched, details: "App started")
                }
                .onChange(of: scenePhase) { oldPhase, newPhase in
                    handleScenePhaseChange(newPhase)
                }
        }
    }

    // MARK: - Private Methods

    /// HIPAA Compliance: Initialize encryption and security services
    private func setupSecurity() {
        // Initialize encryption keys
        _ = EncryptionService.shared

        // Set up audit logging
        AuditLogger.shared.configure()

        // Initialize secure storage
        SecureStorageService.shared.initialize()
    }

    /// HIPAA Compliance: Handle session timeout and background security
    private func handleScenePhaseChange(_ phase: ScenePhase) {
        switch phase {
        case .active:
            // Resume session if valid
            sessionManager.resumeSession()
            AuditLogger.shared.log(event: .appResumed, details: "App became active")

        case .inactive:
            // Prepare for background
            AuditLogger.shared.log(event: .appInactive, details: "App became inactive")

        case .background:
            // HIPAA Compliance: Lock sensitive data and start session timeout
            sessionManager.startBackgroundTimer()
            securityManager.lockSensitiveData()
            AuditLogger.shared.log(event: .appBackgrounded, details: "App entered background")

        @unknown default:
            break
        }
    }
}
