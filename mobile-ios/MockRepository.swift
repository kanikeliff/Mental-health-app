//
//  MockRepository.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//



import Foundation

actor MockRepository: DataRepository {

    // MARK: - Storage
    private var moods: [MoodEntry] = []
    private var messages: [ChatMessage] = []
    private var assessments: [AssessmentSession] = []

    // MARK: - Mood
    func saveMood(_ entry: MoodEntry) async throws {
        moods.append(entry)
    }

    func deleteMood(id: String) async throws {
        moods.removeAll { $0.id == id }
    }

    func getMoodHistory() async throws -> [MoodEntry] {
        moods.sorted { $0.timestamp < $1.timestamp }
    }

    // MARK: - Chat
    func saveMessage(_ msg: ChatMessage) async throws {
        messages.append(msg)
    }

    func getChatThread() async throws -> [ChatMessage] {
        messages.sorted { $0.timestamp < $1.timestamp }
    }

    func clearChat() async throws {
        messages.removeAll()
    }

    // MARK: - Assessments
    func saveAssessment(_ session: AssessmentSession) async throws {
        assessments.append(session)
    }

    func getAssessments() async throws -> [AssessmentSession] {
        assessments.sorted { $0.startedAt < $1.startedAt }
    }
}
