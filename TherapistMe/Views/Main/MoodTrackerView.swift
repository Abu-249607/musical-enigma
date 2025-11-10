//
//  MoodTrackerView.swift
//  Therapist.Me
//
//  HIPAA Compliance: PHI - Mood and craving tracking
//

import SwiftUI

struct MoodTrackerView: View {
    @StateObject private var viewModel = MoodTrackerViewModel()

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Current mood selection
                    VStack(alignment: .leading, spacing: 10) {
                        Text("How are you feeling?")
                            .font(.headline)

                        HStack(spacing: 15) {
                            ForEach(MoodLevel.allCases, id: \.self) { mood in
                                MoodButton(
                                    mood: mood,
                                    isSelected: viewModel.selectedMood == mood,
                                    action: {
                                        viewModel.selectedMood = mood
                                    }
                                )
                            }
                        }
                    }

                    // Craving level
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Craving Level")
                            .font(.headline)

                        HStack(spacing: 15) {
                            ForEach(CravingLevel.allCases, id: \.self) { level in
                                CravingButton(
                                    level: level,
                                    isSelected: viewModel.selectedCraving == level,
                                    action: {
                                        viewModel.selectedCraving = level
                                    }
                                )
                            }
                        }
                    }

                    // Emotions
                    VStack(alignment: .leading, spacing: 10) {
                        Text("What emotions are you experiencing?")
                            .font(.headline)

                        FlowLayout(spacing: 10) {
                            ForEach(Emotion.allCases, id: \.self) { emotion in
                                EmotionTag(
                                    emotion: emotion,
                                    isSelected: viewModel.selectedEmotions.contains(emotion),
                                    action: {
                                        viewModel.toggleEmotion(emotion)
                                    }
                                )
                            }
                        }
                    }

                    // Notes
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Notes (Optional)")
                            .font(.headline)

                        TextEditor(text: $viewModel.notes)
                            .frame(height: 100)
                            .padding(8)
                            .background(Color.gray.opacity(0.1))
                            .cornerRadius(8)
                    }

                    // Save button
                    Button(action: {
                        viewModel.saveMoodEntry()
                    }) {
                        Text("Save Mood Entry")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(viewModel.canSave ? Color.blue : Color.gray)
                            .foregroundColor(.white)
                            .cornerRadius(12)
                    }
                    .disabled(!viewModel.canSave)

                    // Recent entries
                    if !viewModel.recentEntries.isEmpty {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Recent Entries")
                                .font(.headline)

                            ForEach(viewModel.recentEntries.prefix(5)) { entry in
                                MoodEntryCard(entry: entry)
                            }
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("Mood Tracker")
        }
    }
}

struct MoodButton: View {
    let mood: MoodLevel
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Text(mood.emoji)
                    .font(.largeTitle)
                Text(mood.rawValue)
                    .font(.caption2)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 8)
            .background(isSelected ? Color.blue.opacity(0.2) : Color.clear)
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(isSelected ? Color.blue : Color.gray.opacity(0.3), lineWidth: 2)
            )
        }
    }
}

struct CravingButton: View {
    let level: CravingLevel
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Text(level.emoji)
                    .font(.title2)
                Text(level.rawValue)
                    .font(.caption2)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 8)
            .background(isSelected ? Color.orange.opacity(0.2) : Color.clear)
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(isSelected ? Color.orange : Color.gray.opacity(0.3), lineWidth: 2)
            )
        }
    }
}

struct EmotionTag: View {
    let emotion: Emotion
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(emotion.rawValue)
                .font(.caption)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(isSelected ? Color.blue : Color.gray.opacity(0.2))
                .foregroundColor(isSelected ? .white : .primary)
                .cornerRadius(16)
        }
    }
}

struct FlowLayout: Layout {
    var spacing: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let sizes = subviews.map { $0.sizeThatFits(.unspecified) }
        var totalHeight: CGFloat = 0
        var totalWidth: CGFloat = 0
        var lineWidth: CGFloat = 0
        var lineHeight: CGFloat = 0

        for size in sizes {
            if lineWidth + size.width > proposal.width ?? 0 {
                totalHeight += lineHeight + spacing
                lineWidth = size.width
                lineHeight = size.height
            } else {
                lineWidth += size.width + spacing
                lineHeight = max(lineHeight, size.height)
            }
            totalWidth = max(totalWidth, lineWidth)
        }

        totalHeight += lineHeight
        return CGSize(width: totalWidth, height: totalHeight)
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        var lineX = bounds.minX
        var lineY = bounds.minY
        var lineHeight: CGFloat = 0

        for subview in subviews {
            let size = subview.sizeThatFits(.unspecified)

            if lineX + size.width > bounds.maxX {
                lineX = bounds.minX
                lineY += lineHeight + spacing
                lineHeight = 0
            }

            subview.place(at: CGPoint(x: lineX, y: lineY), proposal: .unspecified)

            lineX += size.width + spacing
            lineHeight = max(lineHeight, size.height)
        }
    }
}

struct MoodEntryCard: View {
    let entry: MoodEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(entry.mood.emoji)
                    .font(.title2)

                VStack(alignment: .leading) {
                    Text(entry.mood.rawValue)
                        .font(.headline)
                    Text(entry.timestamp, style: .relative)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                Text(entry.cravingLevel.emoji)
                    .font(.title3)
            }

            if !entry.emotions.isEmpty {
                Text(entry.emotions.map { $0.rawValue }.joined(separator: ", "))
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            if let notes = entry.notes, !notes.isEmpty {
                Text(notes)
                    .font(.caption)
                    .lineLimit(2)
            }
        }
        .padding()
        .background(Color.gray.opacity(0.1))
        .cornerRadius(12)
    }
}

// MARK: - ViewModel

class MoodTrackerViewModel: ObservableObject {
    @Published var selectedMood: MoodLevel?
    @Published var selectedCraving: CravingLevel = .none
    @Published var selectedEmotions: Set<Emotion> = []
    @Published var notes = ""
    @Published var recentEntries: [MoodEntry] = []

    var canSave: Bool {
        selectedMood != nil
    }

    func toggleEmotion(_ emotion: Emotion) {
        if selectedEmotions.contains(emotion) {
            selectedEmotions.remove(emotion)
        } else {
            selectedEmotions.insert(emotion)
        }
    }

    func saveMoodEntry() {
        guard let mood = selectedMood,
              let user = AppCoordinator.shared.getCurrentUser() else {
            return
        }

        let entry = MoodEntry(
            userId: user.id,
            mood: mood,
            emotions: Array(selectedEmotions),
            cravingLevel: selectedCraving,
            notes: notes.isEmpty ? nil : notes,
            energyLevel: 5,
            stressLevel: 5
        )

        // Save to secure storage
        let key = "mood_entry_\(entry.id.uuidString)"
        _ = SecureStorageService.shared.save(entry, withKey: key, userId: user.id.uuidString)

        AuditLogger.shared.log(
            event: .moodEntryCreated,
            details: "Mood entry created",
            userId: user.id.uuidString,
            severity: .low
        )

        // Reset form
        selectedMood = nil
        selectedCraving = .none
        selectedEmotions.removeAll()
        notes = ""

        // Reload entries
        loadRecentEntries()
    }

    private func loadRecentEntries() {
        // In production, load from secure storage
        recentEntries = []
    }
}
