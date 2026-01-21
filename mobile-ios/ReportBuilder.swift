//
//  ReportBuilder.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//


import Foundation

struct ReportPayload: Codable {
    let generatedAt: Date
    let moods: [MoodEntry]
    let assessments: [AssessmentSession]
}

struct ReportBuilder {
    func build(moods: [MoodEntry], assessments: [AssessmentSession]) -> Data? {
        let payload = ReportPayload(generatedAt: Date(), moods: moods, assessments: assessments)
        return try? JSONEncoder().encode(payload)
    }
}
