//
//  ExercisesView.swift
//  Therapist.Me
//
//  Guided therapy exercises and mindfulness activities
//

import SwiftUI

struct ExercisesView: View {
    @StateObject private var viewModel = ExercisesViewModel()

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Breathing exercises section
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Breathing Exercises")
                            .font(.headline)

                        ForEach(viewModel.breathingExercises) { exercise in
                            BreathingExerciseCard(exercise: exercise)
                        }
                    }

                    // Therapy exercises
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Guided Exercises")
                            .font(.headline)

                        ForEach(viewModel.therapyExercises) { exercise in
                            TherapyExerciseCard(exercise: exercise)
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("Exercises")
        }
        .onAppear {
            viewModel.loadExercises()
        }
    }
}

struct BreathingExerciseCard: View {
    let exercise: BreathingExercise
    @State private var showingExercise = false

    var body: some View {
        Button(action: {
            showingExercise = true
        }) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(exercise.name)
                        .font(.headline)
                        .foregroundColor(.primary)

                    Text(exercise.description)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(2)

                    Text("\(exercise.cycles) cycles")
                        .font(.caption2)
                        .foregroundColor(.blue)
                }

                Spacer()

                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color.cyan.opacity(0.1))
            .cornerRadius(12)
        }
        .sheet(isPresented: $showingExercise) {
            BreathingExerciseDetailView(exercise: exercise)
        }
    }
}

struct BreathingExerciseDetailView: View {
    let exercise: BreathingExercise
    @State private var isActive = false
    @State private var currentPhase = "Ready"
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationView {
            VStack(spacing: 40) {
                Text(exercise.name)
                    .font(.title)
                    .fontWeight(.bold)

                // Visual breathing guide
                Circle()
                    .stroke(Color.blue, lineWidth: 4)
                    .frame(width: 200, height: 200)
                    .overlay(
                        Text(currentPhase)
                            .font(.title2)
                    )

                Text(exercise.description)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)

                Button(isActive ? "Stop" : "Start") {
                    if isActive {
                        stopExercise()
                    } else {
                        startExercise()
                    }
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)

                Spacer()
            }
            .padding()
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

    private func startExercise() {
        isActive = true
        // Implement breathing cycle animation
        animateBreathingCycle()
    }

    private func stopExercise() {
        isActive = false
        currentPhase = "Ready"
    }

    private func animateBreathingCycle() {
        // Simplified animation logic
        currentPhase = "Inhale"

        DispatchQueue.main.asyncAfter(deadline: .now() + Double(exercise.inhaleCount)) {
            if isActive {
                currentPhase = "Hold"
                DispatchQueue.main.asyncAfter(deadline: .now() + Double(exercise.holdCount)) {
                    if isActive {
                        currentPhase = "Exhale"
                        DispatchQueue.main.asyncAfter(deadline: .now() + Double(exercise.exhaleCount)) {
                            if isActive {
                                animateBreathingCycle()
                            }
                        }
                    }
                }
            }
        }
    }
}

struct TherapyExerciseCard: View {
    let exercise: TherapyExercise

    var body: some View {
        NavigationLink(destination: TherapyExerciseDetailView(exercise: exercise)) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(exercise.title)
                        .font(.headline)
                        .foregroundColor(.primary)

                    Text(exercise.description)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(2)

                    HStack {
                        Text("\(exercise.duration) min")
                            .font(.caption2)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.blue.opacity(0.2))
                            .cornerRadius(8)

                        Text(exercise.difficulty.rawValue)
                            .font(.caption2)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.green.opacity(0.2))
                            .cornerRadius(8)
                    }
                }

                Spacer()

                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color.green.opacity(0.1))
            .cornerRadius(12)
        }
    }
}

struct TherapyExerciseDetailView: View {
    let exercise: TherapyExercise
    @State private var currentStep = 0

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text(exercise.description)
                    .font(.body)

                Divider()

                Text("Benefits")
                    .font(.headline)

                ForEach(exercise.benefits, id: \.self) { benefit in
                    HStack(alignment: .top) {
                        Text("•")
                        Text(benefit)
                    }
                }

                Divider()

                Text("Instructions")
                    .font(.headline)

                ForEach(Array(exercise.instructions.enumerated()), id: \.offset) { index, instruction in
                    HStack(alignment: .top, spacing: 12) {
                        Text("\(index + 1).")
                            .fontWeight(.bold)
                            .foregroundColor(.blue)

                        Text(instruction)
                    }
                    .padding(.vertical, 8)
                }

                Button("Mark as Complete") {
                    // Save completion
                }
                .buttonStyle(.borderedProminent)
                .frame(maxWidth: .infinity)
            }
            .padding()
        }
        .navigationTitle(exercise.title)
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - ViewModel

class ExercisesViewModel: ObservableObject {
    @Published var breathingExercises: [BreathingExercise] = []
    @Published var therapyExercises: [TherapyExercise] = []

    func loadExercises() {
        // Load breathing exercises
        breathingExercises = BreathingExercise.predefinedExercises

        // Load therapy exercises
        therapyExercises = [
            TherapyExercise(
                title: "Thought Record (CBT)",
                description: "Identify and challenge negative automatic thoughts",
                category: .cognitiveRestructuring,
                therapyMethod: .cbt,
                duration: 10,
                difficulty: .beginner,
                instructions: [
                    "Identify the situation that triggered negative thoughts",
                    "Write down your automatic thoughts",
                    "Identify the emotions you felt",
                    "Examine the evidence for and against your thoughts",
                    "Create a more balanced alternative thought"
                ],
                benefits: [
                    "Reduces negative thinking patterns",
                    "Improves emotional regulation",
                    "Increases self-awareness"
                ]
            ),
            TherapyExercise(
                title: "Body Scan Meditation",
                description: "Mindfulness practice for relaxation and awareness",
                category: .mindfulness,
                therapyMethod: .mindfulness,
                duration: 15,
                difficulty: .beginner,
                instructions: [
                    "Find a comfortable position",
                    "Close your eyes and take deep breaths",
                    "Focus attention on each part of your body",
                    "Notice sensations without judgment",
                    "Gradually bring awareness back to your breath"
                ],
                benefits: [
                    "Reduces stress and anxiety",
                    "Improves body awareness",
                    "Promotes relaxation"
                ]
            ),
            TherapyExercise(
                title: "Urge Surfing",
                description: "Ride out cravings without giving in",
                category: .cravingUrfSurfing,
                therapyMethod: .dbt,
                duration: 10,
                difficulty: .intermediate,
                instructions: [
                    "Notice the urge or craving",
                    "Observe where you feel it in your body",
                    "Imagine the urge as a wave",
                    "Watch it rise, peak, and fall",
                    "Breathe through it without acting on it"
                ],
                benefits: [
                    "Increases ability to tolerate cravings",
                    "Reduces impulsive behavior",
                    "Builds distress tolerance"
                ]
            )
        ]
    }
}
