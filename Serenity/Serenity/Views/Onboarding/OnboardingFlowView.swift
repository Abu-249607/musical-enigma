import SwiftUI

// HIPAA Compliance: Onboarding flow with privacy notice and consent
// Implements §164.520 - Notice of Privacy Practices

struct OnboardingFlowView: View {
    @EnvironmentObject var appState: AppState
    @State private var currentStep = 0
    
    var body: some View {
        TabView(selection: $currentStep) {
            WelcomeView(onContinue: { currentStep = 1 })
                .tag(0)
            
            PrivacyNoticeView(onAccept: { currentStep = 2 })
                .tag(1)
            
            ConsentView(onAccept: { currentStep = 3 })
                .tag(2)
            
            RegistrationView(onComplete: {
                appState.hasCompletedOnboarding = true
            })
                .tag(3)
        }
        .tabViewStyle(.page(indexDisplayMode: .always))
        .indexViewStyle(.page(backgroundDisplayMode: .always))
    }
}

struct WelcomeView: View {
    let onContinue: () -> Void
    
    var body: some View {
        VStack(spacing: 30) {
            Spacer()
            
            Image(systemName: "heart.fill")
                .font(.system(size: 80))
                .foregroundColor(.blue)
            
            Text("Welcome to Serenity")
                .font(.largeTitle)
                .fontWeight(.bold)
                .multilineTextAlignment(.center)
            
            Text("Your journey to recovery starts here")
                .font(.title3)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
            
            Spacer()
            
            Button(action: onContinue) {
                Text("Get Started")
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(12)
            }
            .padding(.horizontal)
        }
        .padding()
    }
}

struct PrivacyNoticeView: View {
    let onAccept: () -> Void
    @State private var hasScrolledToBottom = false
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Privacy Notice")
                .font(.title)
                .fontWeight(.bold)
            
            ScrollView {
                VStack(alignment: .leading, spacing: 15) {
                    Text("HIPAA Notice of Privacy Practices")
                        .font(.headline)
                    
                    Text("""
                    This notice describes how medical information about you may be used and disclosed and how you can get access to this information.
                    
                    YOUR RIGHTS:
                    • Right to Access: You can view and get copies of your health information
                    • Right to Amend: You can ask us to correct your health information
                    • Right to Accounting: You can see a list of who accessed your information
                    • Right to Request Restrictions: You can ask us to limit how we use your data
                    • Right to Request Deletion: You can request complete deletion of your account
                    
                    OUR USES AND DISCLOSURES:
                    We may use and disclose your health information for:
                    • Treatment: To provide addiction recovery support and therapy
                    • Healthcare Operations: To improve our services
                    • As Required by Law: When legally required
                    
                    SECURITY MEASURES:
                    • All data encrypted with AES-256 encryption
                    • Biometric authentication for sensitive operations
                    • Comprehensive audit logging
                    • No sharing with third parties without consent
                    
                    For more information, please contact our Privacy Officer.
                    """)
                    .font(.body)
                }
                .padding()
            }
            .border(Color.gray.opacity(0.3), width: 1)
            
            Button(action: {
                // HIPAA Audit: Log privacy notice acceptance
                AuditLogger.shared.log(.privacyNoticeAccepted, metadata: [:])
                onAccept()
            }) {
                Text("I Accept")
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(12)
            }
        }
        .padding()
    }
}

struct ConsentView: View {
    let onAccept: () -> Void
    @State private var requiredConsents: [Bool] = [false, false, false]
    @State private var optionalConsents: [Bool] = [false, false]
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Consent & Preferences")
                .font(.title)
                .fontWeight(.bold)
            
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    Text("Required Consents")
                        .font(.headline)
                    
                    Toggle("I accept the Privacy Notice", isOn: $requiredConsents[0])
                    Toggle("I accept the Terms of Service", isOn: $requiredConsents[1])
                    Toggle("I authorize HIPAA data processing", isOn: $requiredConsents[2])
                    
                    Divider()
                    
                    Text("Optional Preferences")
                        .font(.headline)
                    
                    Toggle("Allow crash reporting (de-identified)", isOn: $optionalConsents[0])
                    Toggle("Receive email notifications", isOn: $optionalConsents[1])
                }
            }
            
            Button(action: {
                // HIPAA Audit: Log consent
                AuditLogger.shared.log(.consentGranted, metadata: [
                    "privacyNotice": requiredConsents[0],
                    "terms": requiredConsents[1],
                    "hipaa": requiredConsents[2]
                ])
                onAccept()
            }) {
                Text("Continue")
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(allRequiredAccepted ? Color.blue : Color.gray)
                    .cornerRadius(12)
            }
            .disabled(!allRequiredAccepted)
        }
        .padding()
    }
    
    var allRequiredAccepted: Bool {
        requiredConsents.allSatisfy { $0 }
    }
}

struct RegistrationView: View {
    let onComplete: () -> Void
    @State private var email = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var firstName = ""
    @State private var lastName = ""
    @State private var errorMessage = ""
    @State private var isLoading = false
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Create Account")
                .font(.title)
                .fontWeight(.bold)
            
            ScrollView {
                VStack(spacing: 15) {
                    TextField("First Name", text: $firstName)
                        .textFieldStyle(.roundedBorder)
                        .textContentType(.givenName)
                    
                    TextField("Last Name", text: $lastName)
                        .textFieldStyle(.roundedBorder)
                        .textContentType(.familyName)
                    
                    TextField("Email", text: $email)
                        .textFieldStyle(.roundedBorder)
                        .textContentType(.emailAddress)
                        .keyboardType(.emailAddress)
                        .autocapitalization(.none)
                    
                    SecureField("Password (min 12 characters)", text: $password)
                        .textFieldStyle(.roundedBorder)
                        .textContentType(.newPassword)
                    
                    PasswordStrengthIndicator(password: password)
                    
                    SecureField("Confirm Password", text: $confirmPassword)
                        .textFieldStyle(.roundedBorder)
                        .textContentType(.newPassword)
                    
                    if !errorMessage.isEmpty {
                        Text(errorMessage)
                            .foregroundColor(.red)
                            .font(.caption)
                    }
                }
            }
            
            Button(action: register) {
                if isLoading {
                    ProgressView()
                        .progressViewStyle(.circular)
                } else {
                    Text("Create Account")
                        .font(.headline)
                }
            }
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .padding()
            .background(Color.blue)
            .cornerRadius(12)
            .disabled(isLoading)
        }
        .padding()
    }
    
    func register() {
        errorMessage = ""
        
        // Validation
        guard !firstName.isEmpty, !lastName.isEmpty else {
            errorMessage = "Please enter your name"
            return
        }
        
        guard password == confirmPassword else {
            errorMessage = "Passwords do not match"
            return
        }
        
        isLoading = true
        
        Task {
            do {
                let user = try await AuthenticationService.shared.register(
                    email: email,
                    password: password,
                    firstName: firstName,
                    lastName: lastName
                )
                
                // Start session
                SessionManager.shared.startSession(user: user, token: "mock-token")
                
                await MainActor.run {
                    onComplete()
                }
                
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    isLoading = false
                }
            }
        }
    }
}

struct PasswordStrengthIndicator: View {
    let password: String
    
    var strength: Int {
        PasswordValidator.shared.strength(password)
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            ProgressView(value: Double(strength), total: 100)
                .progressViewStyle(.linear)
                .tint(strengthColor)
            
            Text(strengthText)
                .font(.caption)
                .foregroundColor(strengthColor)
        }
    }
    
    var strengthColor: Color {
        if strength < 40 { return .red }
        if strength < 70 { return .orange }
        return .green
    }
    
    var strengthText: String {
        if strength < 40 { return "Weak password" }
        if strength < 70 { return "Medium strength" }
        return "Strong password"
    }
}

// MARK: - Audit Events

extension AuditEvent {
    static let privacyNoticeAccepted = AuditEvent(type: "PRIVACY_NOTICE_ACCEPTED")
}
