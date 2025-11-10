//
//  AuthenticationViewModel.swift
//  Therapist.Me
//
//  Authentication view model with biometric support
//

import Foundation
import LocalAuthentication

class AuthenticationViewModel: ObservableObject {
    @Published var isAuthenticating = false
    @Published var authError: String?
    @Published var biometricType: SecurityManager.BiometricType = .none

    private let securityManager = SecurityManager.shared
    private let sessionManager = SessionManager.shared
    private let appCoordinator = AppCoordinator.shared

    init() {
        biometricType = securityManager.biometricType()
    }

    // MARK: - Authentication

    func authenticateWithBiometrics() {
        isAuthenticating = true
        authError = nil

        sessionManager.authenticate { [weak self] success in
            DispatchQueue.main.async {
                self?.isAuthenticating = false

                if success {
                    self?.completeAuthentication()
                } else {
                    self?.authError = "Authentication failed. Please try again."
                }
            }
        }
    }

    func authenticateWithPasscode(_ passcode: String) {
        // In production, verify passcode against stored hash
        isAuthenticating = true
        authError = nil

        // Simulate authentication
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
            self?.isAuthenticating = false
            self?.completeAuthentication()
        }
    }

    private func completeAuthentication() {
        guard let user = appCoordinator.getCurrentUser() else {
            authError = "User not found"
            return
        }

        appCoordinator.authenticate(user: user)
    }

    // MARK: - Biometric Setup

    func isBiometricsAvailable() -> Bool {
        return securityManager.isBiometricsAvailable()
    }

    var biometricDisplayName: String {
        return biometricType.displayName
    }

    var biometricIcon: String {
        return biometricType.icon
    }
}
