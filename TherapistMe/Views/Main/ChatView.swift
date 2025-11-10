//
//  ChatView.swift
//  Therapist.Me
//
//  Virtual therapist chatbot with evidence-based therapy methods
//

import SwiftUI

struct ChatView: View {
    @StateObject private var viewModel = ChatViewModel()

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Messages list
                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(spacing: 16) {
                            ForEach(viewModel.messages) { message in
                                MessageBubble(message: message)
                                    .id(message.id)
                            }
                        }
                        .padding()
                    }
                    .onChange(of: viewModel.messages.count) { _, _ in
                        if let lastMessage = viewModel.messages.last {
                            withAnimation {
                                proxy.scrollTo(lastMessage.id, anchor: .bottom)
                            }
                        }
                    }
                }

                // Quick actions (if suggested)
                if !viewModel.suggestedActions.isEmpty {
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 10) {
                            ForEach(viewModel.suggestedActions) { action in
                                Button(action: {
                                    viewModel.performAction(action)
                                }) {
                                    Text(action.title)
                                        .font(.caption)
                                        .padding(.horizontal, 12)
                                        .padding(.vertical, 6)
                                        .background(Color.blue.opacity(0.1))
                                        .foregroundColor(.blue)
                                        .cornerRadius(16)
                                }
                            }
                        }
                        .padding()
                    }
                }

                // Input bar
                HStack(spacing: 12) {
                    TextField("Type your message...", text: $viewModel.messageText)
                        .textFieldStyle(.roundedBorder)

                    Button(action: {
                        viewModel.sendMessage()
                    }) {
                        Image(systemName: "arrow.up.circle.fill")
                            .font(.title)
                            .foregroundColor(viewModel.messageText.isEmpty ? .gray : .blue)
                    }
                    .disabled(viewModel.messageText.isEmpty)
                }
                .padding()
            }
            .navigationTitle("Virtual Therapist")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        Button("CBT Session") {
                            viewModel.startSession(.cbt)
                        }
                        Button("Motivational Interview") {
                            viewModel.startSession(.motivationalInterviewing)
                        }
                        Button("Crisis Support") {
                            viewModel.startSession(.crisis)
                        }
                        Button("General Chat") {
                            viewModel.startSession(.general)
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }
            }
        }
        .onAppear {
            viewModel.initialize()
        }
    }
}

struct MessageBubble: View {
    let message: ChatMessage

    var body: some View {
        HStack {
            if message.sender == .user {
                Spacer()
            }

            VStack(alignment: message.sender == .user ? .trailing : .leading, spacing: 4) {
                Text(message.content)
                    .padding(12)
                    .background(message.sender == .user ? Color.blue : Color.gray.opacity(0.2))
                    .foregroundColor(message.sender == .user ? .white : .primary)
                    .cornerRadius(16)

                Text(message.timestamp, style: .time)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            .frame(maxWidth: 280, alignment: message.sender == .user ? .trailing : .leading)

            if message.sender == .therapist {
                Spacer()
            }
        }
    }
}

// MARK: - ViewModel

class ChatViewModel: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var messageText = ""
    @Published var suggestedActions: [SuggestedAction] = []
    @Published var currentSession: SessionType = .general

    func initialize() {
        // Start with welcome message
        let welcomeMessage = ChatMessage(
            content: "Hello! I'm your virtual therapist. I'm here to support you on your recovery journey. How are you feeling today?",
            sender: .therapist,
            therapyTechnique: .validationAndSupport,
            emotionalTone: .supportive
        )
        messages.append(welcomeMessage)
    }

    func sendMessage() {
        guard !messageText.isEmpty else { return }

        // User message
        let userMessage = ChatMessage(
            content: messageText,
            sender: .user
        )
        messages.append(userMessage)

        let userInput = messageText
        messageText = ""

        // Generate response
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) { [weak self] in
            self?.generateResponse(to: userInput)
        }
    }

    func generateResponse(to input: String) {
        // Simplified AI response logic
        let lowercased = input.lowercased()

        var response = ""
        var technique: TherapyTechnique?
        var actions: [SuggestedAction] = []

        if lowercased.contains("craving") || lowercased.contains("urge") {
            response = "I understand you're experiencing a craving. That's completely normal in recovery. Let's work through this together. What triggered this craving?"
            technique = .urgeSurfing
            actions = [
                SuggestedAction(title: "Breathing Exercise", actionType: .breathingExercise),
                SuggestedAction(title: "View Coping Strategies", actionType: .viewResources)
            ]
        } else if lowercased.contains("sad") || lowercased.contains("depressed") {
            response = "I hear that you're feeling sad. That takes courage to share. Can you tell me more about what's contributing to these feelings?"
            technique = .reflectiveListening
            actions = [
                SuggestedAction(title: "Journal", actionType: .journalPrompt),
                SuggestedAction(title: "Mood Exercise", actionType: .startExercise)
            ]
        } else if lowercased.contains("anxious") || lowercased.contains("worried") {
            response = "Anxiety can be overwhelming. Let's try to break down what you're worried about. What specific thoughts are troubling you?"
            technique = .thoughtChallenging
            actions = [
                SuggestedAction(title: "Deep Breathing", actionType: .breathingExercise),
                SuggestedAction(title: "CBT Exercise", actionType: .startExercise)
            ]
        } else if lowercased.contains("proud") || lowercased.contains("good") || lowercased.contains("great") {
            response = "That's wonderful to hear! I'm proud of you. Celebrating these positive moments is important. What contributed to feeling this way?"
            technique = .affirmation
        } else {
            response = "Thank you for sharing that with me. I'm here to listen and support you. What would you like to talk about today?"
            technique = .openEndedQuestion
        }

        let therapistMessage = ChatMessage(
            content: response,
            sender: .therapist,
            therapyTechnique: technique,
            suggestedActions: actions,
            emotionalTone: .empathetic
        )

        messages.append(therapistMessage)
        suggestedActions = actions
    }

    func startSession(_ type: SessionType) {
        currentSession = type

        var message = ""
        switch type {
        case .cbt:
            message = "Let's start a CBT session. We'll work on identifying and challenging unhelpful thought patterns. What situation has been bothering you recently?"
        case .motivationalInterviewing:
            message = "Let's explore your motivation for change. On a scale of 1-10, how important is recovery to you right now?"
        case .crisis:
            message = "I'm here to help. You're not alone. What's happening right now that's making you feel this way?"
        case .general:
            message = "I'm here to chat about whatever is on your mind. What would you like to talk about?"
        default:
            message = "How can I support you today?"
        }

        let therapistMessage = ChatMessage(
            content: message,
            sender: .therapist,
            emotionalTone: .supportive
        )
        messages.append(therapistMessage)
    }

    func performAction(_ action: SuggestedAction) {
        // In production, navigate to appropriate view or start action
        print("Performing action: \(action.title)")
    }
}
