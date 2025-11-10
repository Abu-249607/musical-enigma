//
//  AuthenticationView.swift
//  Therapist.Me
//
//  HIPAA Compliance: Secure authentication with biometrics
//

import SwiftUI

struct AuthenticationView: View {
    @ObservedObject var viewModel: AuthenticationViewModel
    @State private var passcode: String = ""

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color.blue.opacity(0.6), Color.purple.opacity(0.6)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(spacing: 40) {
                // Logo and title
                VStack(spacing: 20) {
                    Image(systemName: "heart.text.square.fill")
                        .font(.system(size: 80))
                        .foregroundColor(.white)

                    Text("Therapist.Me")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundColor(.white)

                    Text("Welcome Back")
                        .font(.title3)
                        .foregroundColor(.white.opacity(0.9))
                }
                .padding(.top, 60)

                Spacer()

                // Authentication options
                VStack(spacing: 20) {
                    if viewModel.isBiometricsAvailable() {
                        Button(action: {
                            viewModel.authenticateWithBiometrics()
                        }) {
                            HStack {
                                Image(systemName: viewModel.biometricIcon)
                                    .font(.title2)
                                Text("Authenticate with \(viewModel.biometricDisplayName)")
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.white)
                            .foregroundColor(.blue)
                            .cornerRadius(12)
                        }
                        .disabled(viewModel.isAuthenticating)
                    }

                    // Error message
                    if let error = viewModel.authError {
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.red)
                            .padding(.horizontal)
                    }
                }
                .padding(.horizontal, 40)

                Spacer()

                // Privacy note
                Text("Your data is encrypted and secure")
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.8))
                    .padding(.bottom, 40)
            }

            // Loading overlay
            if viewModel.isAuthenticating {
                Color.black.opacity(0.4)
                    .ignoresSafeArea()

                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    .scaleEffect(1.5)
            }
        }
    }
}
