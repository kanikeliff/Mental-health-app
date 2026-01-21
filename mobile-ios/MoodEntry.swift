//
//  MoodEntry.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//



import Foundation

struct MoodEntry: Identifiable, Codable, Equatable {
    var id: String
    var timestamp: Date
    var moodScore: Int     // 1..5 (per tests/spec)
    var note: String
}
