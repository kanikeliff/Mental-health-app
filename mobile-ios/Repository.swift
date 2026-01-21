//
//  Repository.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//



import Foundation

protocol DataRepository {
    func saveMood(_ entry: MoodEntry) async throws
    func saveMessage(_ msg: ChatMessage) async throws
    func saveAssessment(_ session: AssessmentSession) async throws
    func deleteMood(id: String) async throws
    func getMoodHistory() async throws -> [MoodEntry]
    func getChatThread() async throws -> [ChatMessage]
    func getAssessments() async throws -> [AssessmentSession]
    func clearChat() async throws
}
