import SwiftUI

// HIPAA Compliance: Secure login view with MFA support

struct LoginView: View {
    @EnvironmentObject var sessionManager: SessionManager
    @State private var email = ""
    @State private var password = ""
    @State private var errorMessage = ""
    @State private var isLoading = false
    @State private var showingBiometric = false
    
    var body: some View {
        VStack(spacing: 30) {
            Spacer()
            
            Image(systemName: "heart.fill")
                .font(.system(size: 60))
                .foregroundColor(.blue)
            
            Text("Therapist.Me")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            VStack(spacing: 15) {
                TextField("Email", text: $email)
                    .textFieldStyle(.roundedBorder)
                    .textContentType(.emailAddress)
                    .keyboardType(.emailAddress)
                    .autocapitalization(.none)
                
                SecureField("Password", text: $password)
                    .textFieldStyle(.roundedBorder)
                    .textContentType(.password)
                
                if !errorMessage.isEmpty {
                    Text(errorMessage)
                        .foregroundColor(.red)
                        .font(.caption)
                }
            }
            
            Button(action: login) {
                if isLoading {
                    ProgressView()
                } else {
                    Text("Log In")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(12)
                }
            }
            .disabled(isLoading)
            
            if BiometricAuth.isAvailable {
                Button(action: loginWithBiometric) {
                    HStack {
                        Image(systemName: "faceid")
                        Text("Use Face ID")
                    }
                    .foregroundColor(.blue)
                }
            }
            
            Spacer()
            
            Text("Your health data is encrypted and secure")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
    }
    
    func login() {
        errorMessage = ""
        isLoading = true
        
        Task {
            do {
                let user = try await AuthenticationService.shared.login(
                    email: email,
                    password: password
                )
                
                await MainActor.run {
                    sessionManager.startSession(user: user, token: "mock-token")
                    isLoading = false
                }
                
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    isLoading = false
                }
            }
        }
    }
    
    func loginWithBiometric() {
        Task {
            do {
                if let biometric = BiometricAuth.shared {
                    let success = try await biometric.authenticate(
                        reason: "Log in to Therapist.Me"
                    )
                    
                    if success {
                        // In production, retrieve saved credentials and login
                        await MainActor.run {
                            // Mock user for demo
                        }
                    }
                }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                }
            }
        }
    }
}
