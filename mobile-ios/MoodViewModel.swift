//
//  MoodViewModel.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//


import SwiftUI
import Foundation
import Combine
@MainActor
final class MoodViewModel: ObservableObject {

    @Published var moodScore: Int = 3
    @Published var note: String = ""
    @Published var moods: [MoodEntry] = []
    @Published var errorMsg: String?

    private let repo: DataRepository

    init(repo: DataRepository) {
        self.repo = repo
    }

    // MARK: - Load
    func load() async {
        do {
            moods = try await repo.getMoodHistory()
        } catch {
            errorMsg = "Failed to load mood history."
        }
    }

    // MARK: - Save
    func submit() {
        guard (1...5).contains(moodScore) else {
            errorMsg = "Mood must be between 1 and 5."
            return
        }

        let entry = MoodEntry(
            id: UUID().uuidString,
            timestamp: Date(),
            moodScore: moodScore,
            note: note
        )

        Task {
            do {
                try await repo.saveMood(entry)
                note = ""
                await load()   // 🔥 SADECE BURASI UI’ı GÜNCELLER
            } catch {
                errorMsg = "Failed to save mood."
            }
        }
    }

    // MARK: - Delete
    func deleteMood(at offsets: IndexSet) {
        let ids = offsets.map { moods[$0].id }

        Task {
            do {
                for id in ids {
                    try await repo.deleteMood(id: id)
                }
                await load()   // 🔥 geri gelme burada biter
            } catch {
                errorMsg = "Failed to delete mood."
            }
        }
    }
}
