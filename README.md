# Therapist.Me 🧠💙

![iOS](https://img.shields.io/badge/iOS-16.0%2B-blue)
![Swift](https://img.shields.io/badge/Swift-5.9-orange)
![License](https://img.shields.io/badge/License-Proprietary-red)
![HIPAA](https://img.shields.io/badge/HIPAA-Compliant-green)

A comprehensive, HIPAA-compliant iOS mental health and addiction recovery support application built with SwiftUI. Therapist.Me provides personalized recovery support using evidence-based therapy methods, mood tracking, virtual therapist, guided exercises, and a supportive community.

## 🌟 Features

### Core Features

- **🔐 HIPAA-Compliant Security**
  - AES-256 encryption for all Protected Health Information (PHI)
  - Biometric authentication (Face ID / Touch ID)
  - Automatic session timeout (15 minutes)
  - Tamper-proof audit logging
  - Secure Keychain/Secure Enclave key storage

- **📝 Mood & Craving Tracker**
  - Daily mood check-ins with emotional states
  - Craving level monitoring (0-4 scale)
  - Trigger identification and tracking
  - Notes and context capture
  - Historical trend analysis

- **📖 Secure Journaling**
  - Free-form journaling with encryption
  - CBT thought records
  - Gratitude practice
  - Guided prompts
  - Tagging and organization

- **🤖 Virtual Therapist**
  - AI-powered conversational support
  - Evidence-based therapy techniques:
    - Cognitive Behavioral Therapy (CBT)
    - Motivational Interviewing (MI)
    - Dialectical Behavior Therapy (DBT)
    - Mindfulness-Based Stress Reduction (MBSR)
  - Crisis support mode
  - Personalized responses

- **🧘 Guided Exercises**
  - Breathing exercises (Box Breathing, 4-7-8, etc.)
  - Mindfulness meditations
  - Progressive muscle relaxation
  - Cognitive restructuring
  - Urge surfing
  - Psychoeducational content

- **🆘 Crisis Toolkit**
  - Emergency hotline access (988, SAMHSA)
  - Immediate coping tools
  - Breathing exercises
  - Grounding techniques (5-4-3-2-1)
  - Motivational quotes
  - Emergency contact quick access

- **📊 Progress Dashboard**
  - Sobriety day counter
  - Streak tracking (current & longest)
  - Achievement badges
  - Mood trends and analytics
  - Visual progress charts
  - Milestone celebrations

### Security & Compliance

#### HIPAA Compliance Features

- **Encryption**: AES-256-GCM for data at rest, TLS 1.3 for data in transit
- **Access Controls**: Unique user identification, biometric authentication, automatic logoff
- **Audit Controls**: Comprehensive logging of all PHI access with cryptographic integrity
- **Data Integrity**: SHA-256 hashing and verification
- **Authentication**: Face ID, Touch ID, device passcode
- **Breach Notification**: Automated detection and response procedures
- **User Rights**: Access, amendment, export, and deletion of data

See [HIPAA_COMPLIANCE.md](./HIPAA_COMPLIANCE.md) for detailed compliance documentation.

## 🏗️ Architecture

### Tech Stack

- **Language**: Swift 5.9+
- **UI Framework**: SwiftUI
- **Reactive Programming**: Combine
- **Security**: CryptoKit, LocalAuthentication
- **Storage**: Encrypted FileManager, iOS Keychain
- **Cloud Backup**: iCloud (optional)
- **Testing**: XCTest
- **Minimum iOS**: 16.0+

### Design Pattern

MVVM (Model-View-ViewModel) with dependency injection and protocol-oriented programming.

```
TherapistMe/
├── Models/              # Data models (User, MoodEntry, Journal, etc.)
├── ViewModels/          # Business logic and state management
├── Views/               # SwiftUI views
│   ├── Onboarding/
│   ├── Authentication/
│   └── Main/
├── Services/            # Business services
│   └── Security/        # Encryption, audit, session management
├── Coordinators/        # Navigation coordination
├── SampleData/          # Test data generation
└── Tests/              # Unit and integration tests
```

See [DEVELOPMENT_ROADMAP.md](./DEVELOPMENT_ROADMAP.md) for detailed architecture documentation.

## 🚀 Getting Started

### Prerequisites

- macOS 14.0+ (Sonoma) or later
- Xcode 15.0+
- iOS 16.0+ device or simulator
- Apple Developer Account (for device testing)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-org/therapist-me.git
cd musical-enigma
```

2. **Open in Xcode**
```bash
open TherapistMe/TherapistMeApp.swift
```

3. **Configure signing**
   - Select your development team in Xcode
   - Update the bundle identifier if needed

4. **Build and run**
   - Select a simulator or connected device
   - Press `⌘ + R` or click the Run button

## 📄 Documentation

- **[PRIVACY_POLICY.md](./PRIVACY_POLICY.md)**: Complete privacy policy with HIPAA notices
- **[HIPAA_COMPLIANCE.md](./HIPAA_COMPLIANCE.md)**: Detailed HIPAA compliance documentation
- **[DEVELOPMENT_ROADMAP.md](./DEVELOPMENT_ROADMAP.md)**: Development phases, testing strategy, deployment checklist

## 🗺️ Roadmap

### Current Phase: MVP ✅ COMPLETED
- [x] Core security infrastructure
- [x] User authentication and onboarding
- [x] Mood and craving tracking
- [x] Basic journaling
- [x] Virtual therapist (basic)
- [x] Guided exercises
- [x] Crisis toolkit
- [x] Progress dashboard

### Future Enhancements 📋 PLANNED
- [ ] AI-powered chatbot (GPT-4/Claude integration)
- [ ] Forum with moderation
- [ ] Apple Health integration
- [ ] Apple Watch companion app
- [ ] Advanced analytics and insights

See [DEVELOPMENT_ROADMAP.md](./DEVELOPMENT_ROADMAP.md) for detailed timeline.

## ⚠️ Disclaimer

**Therapist.Me is NOT a substitute for professional medical advice, diagnosis, or treatment.**

This app provides supportive tools and resources for addiction recovery and mental wellness but does not replace professional healthcare. Always seek the advice of qualified health providers with questions about mental health or substance use conditions.

**In case of emergency:**
- Call 911 (US)
- Call 988 (Suicide & Crisis Lifeline)
- Call SAMHSA: 1-800-662-4357
- Go to your nearest emergency room

## 📞 Support

- **Technical Issues**: support@therapist.me
- **Privacy Questions**: privacy@therapist.me
- **HIPAA Compliance**: hipaa@therapist.me
- **Security Reports**: security@therapist.me

## 📜 License

Proprietary - All Rights Reserved

Copyright © 2025 Therapist.Me. This software and associated documentation files are proprietary and confidential.

---

**Built with ❤️ for the recovery community**
