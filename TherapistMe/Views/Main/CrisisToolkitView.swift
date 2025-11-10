//
//  CrisisToolkitView.swift
//  Therapist.Me
//
//  Emergency crisis support toolkit
//

import SwiftUI

struct CrisisToolkitView: View {
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Crisis header
                    VStack(spacing: 10) {
                        Image(systemName: "heart.circle.fill")
                            .font(.system(size: 60))
                            .foregroundColor(.red)

                        Text("You're Not Alone")
                            .font(.title)
                            .fontWeight(.bold)

                        Text("We're here to help. Choose an option below.")
                            .font(.body)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding()

                    // Emergency hotlines
                    VStack(alignment: .leading, spacing: 15) {
                        Text("Emergency Hotlines")
                            .font(.headline)

                        CrisisHotlineCard(
                            name: "988 Suicide & Crisis Lifeline",
                            number: "988",
                            description: "24/7 crisis support"
                        )

                        CrisisHotlineCard(
                            name: "SAMHSA National Helpline",
                            number: "1-800-662-4357",
                            description: "Substance abuse support"
                        )

                        CrisisHotlineCard(
                            name: "Crisis Text Line",
                            number: "Text HOME to 741741",
                            description: "24/7 text support"
                        )
                    }
                    .padding(.horizontal)

                    Divider()

                    // Immediate coping tools
                    VStack(alignment: .leading, spacing: 15) {
                        Text("Immediate Coping Tools")
                            .font(.headline)
                            .padding(.horizontal)

                        CopingToolCard(
                            icon: "wind",
                            title: "Breathing Exercise",
                            description: "Calm your nervous system",
                            color: .cyan
                        )

                        CopingToolCard(
                            icon: "book",
                            title: "Emergency Journal",
                            description: "Write down your feelings",
                            color: .green
                        )

                        CopingToolCard(
                            icon: "quote.bubble",
                            title: "Motivational Quotes",
                            description: "Read inspiring messages",
                            color: .purple
                        )

                        CopingToolCard(
                            icon: "figure.walk",
                            title: "Grounding Exercises",
                            description: "5-4-3-2-1 technique",
                            color: .orange
                        )
                    }
                    .padding(.horizontal)

                    Divider()

                    // Emergency contacts
                    VStack(alignment: .leading, spacing: 15) {
                        Text("Your Emergency Contacts")
                            .font(.headline)
                            .padding(.horizontal)

                        // This would load user's emergency contacts
                        Text("No emergency contacts added yet")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .padding(.horizontal)

                        Button("Add Emergency Contact") {
                            // Add contact
                        }
                        .buttonStyle(.bordered)
                        .padding(.horizontal)
                    }

                    Spacer(minLength: 40)
                }
            }
            .navigationTitle("Crisis Support")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}

struct CrisisHotlineCard: View {
    let name: String
    let number: String
    let description: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(name)
                .font(.headline)

            Text(description)
                .font(.caption)
                .foregroundColor(.secondary)

            Button(action: {
                // Call hotline
                if let url = URL(string: "tel://\(number.filter { $0.isNumber })") {
                    UIApplication.shared.open(url)
                }
            }) {
                HStack {
                    Image(systemName: "phone.fill")
                    Text(number)
                        .fontWeight(.semibold)
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.red)
                .foregroundColor(.white)
                .cornerRadius(12)
            }
        }
        .padding()
        .background(Color.red.opacity(0.1))
        .cornerRadius(12)
    }
}

struct CopingToolCard: View {
    let icon: String
    let title: String
    let description: String
    let color: Color
    @State private var showingDetail = false

    var body: some View {
        Button(action: {
            showingDetail = true
        }) {
            HStack(spacing: 15) {
                Image(systemName: icon)
                    .font(.title)
                    .foregroundColor(color)
                    .frame(width: 50)

                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.headline)
                        .foregroundColor(.primary)

                    Text(description)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(color.opacity(0.1))
            .cornerRadius(12)
        }
        .sheet(isPresented: $showingDetail) {
            CopingToolDetailView(title: title, icon: icon, color: color)
        }
    }
}

struct CopingToolDetailView: View {
    let title: String
    let icon: String
    let color: Color
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 30) {
                    Image(systemName: icon)
                        .font(.system(size: 80))
                        .foregroundColor(color)

                    Text(title)
                        .font(.title)
                        .fontWeight(.bold)

                    // Content based on tool type
                    if title.contains("Breathing") {
                        BreathingInstructions()
                    } else if title.contains("Journal") {
                        EmergencyJournalView()
                    } else if title.contains("Quotes") {
                        MotivationalQuotesView()
                    } else if title.contains("Grounding") {
                        GroundingExerciseView()
                    }

                    Spacer()
                }
                .padding()
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}

struct BreathingInstructions: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Quick Breathing Exercise")
                .font(.headline)

            Text("Follow these steps:")
                .font(.subheadline)

            VStack(alignment: .leading, spacing: 10) {
                InstructionRow(number: 1, text: "Breathe in slowly through your nose for 4 counts")
                InstructionRow(number: 2, text: "Hold your breath for 4 counts")
                InstructionRow(number: 3, text: "Breathe out slowly through your mouth for 4 counts")
                InstructionRow(number: 4, text: "Repeat 4 times")
            }

            Button("Start Guided Breathing") {
                // Start breathing exercise
            }
            .buttonStyle(.borderedProminent)
            .frame(maxWidth: .infinity)
        }
    }
}

struct InstructionRow: View {
    let number: Int
    let text: String

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Text("\(number)")
                .font(.headline)
                .foregroundColor(.white)
                .frame(width: 30, height: 30)
                .background(Color.blue)
                .clipShape(Circle())

            Text(text)
                .font(.body)
        }
    }
}

struct EmergencyJournalView: View {
    @State private var journalText = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Write down what you're feeling")
                .font(.headline)

            Text("Getting your thoughts on paper can help process difficult emotions.")
                .font(.subheadline)
                .foregroundColor(.secondary)

            TextEditor(text: $journalText)
                .frame(height: 200)
                .padding(8)
                .background(Color.gray.opacity(0.1))
                .cornerRadius(8)

            Button("Save Entry") {
                // Save journal entry
            }
            .buttonStyle(.borderedProminent)
            .frame(maxWidth: .infinity)
        }
    }
}

struct MotivationalQuotesView: View {
    let quotes = [
        "You are stronger than your struggles.",
        "Every day sober is a day won.",
        "Recovery is not a race. You don't have to feel guilty if it takes you longer than you thought it would.",
        "Fall seven times, stand up eight.",
        "Your life isn't behind you; your life is in front of you.",
        "Be patient with yourself. Nothing in nature blooms all year.",
        "You are worth the effort."
    ]

    @State private var currentQuote = 0

    var body: some View {
        VStack(spacing: 30) {
            Text(quotes[currentQuote])
                .font(.title3)
                .fontWeight(.medium)
                .multilineTextAlignment(.center)
                .padding()
                .background(Color.purple.opacity(0.1))
                .cornerRadius(12)

            Button("Next Quote") {
                currentQuote = (currentQuote + 1) % quotes.count
            }
            .buttonStyle(.bordered)
        }
    }
}

struct GroundingExerciseView: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("5-4-3-2-1 Grounding Technique")
                .font(.headline)

            Text("Use your senses to ground yourself in the present moment:")
                .font(.subheadline)
                .foregroundColor(.secondary)

            VStack(alignment: .leading, spacing: 15) {
                GroundingStep(emoji: "👀", title: "5 things you can see", color: .blue)
                GroundingStep(emoji: "✋", title: "4 things you can touch", color: .green)
                GroundingStep(emoji: "👂", title: "3 things you can hear", color: .orange)
                GroundingStep(emoji: "👃", title: "2 things you can smell", color: .purple)
                GroundingStep(emoji: "👅", title: "1 thing you can taste", color: .red)
            }

            Text("Take your time with each step. This exercise helps bring you back to the present moment.")
                .font(.caption)
                .foregroundColor(.secondary)
                .padding(.top)
        }
    }
}

struct GroundingStep: View {
    let emoji: String
    let title: String
    let color: Color

    var body: some View {
        HStack {
            Text(emoji)
                .font(.title)

            Text(title)
                .font(.body)

            Spacer()
        }
        .padding()
        .background(color.opacity(0.1))
        .cornerRadius(8)
    }
}
