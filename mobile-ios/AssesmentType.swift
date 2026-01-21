//
//  AssesmentType.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//


import Foundation

enum AssessmentType: String, CaseIterable, Codable {
    case phq9 = "PHQ-9"
    case who5 = "WHO-5"
    case scl90 = "SCL-90"
}

struct Question: Identifiable, Codable, Equatable {
    var id: String
    var text: String
    var options: [String]
    var minValue: Int
    var maxValue: Int
}

struct Response: Codable, Equatable {
    var questionId: String
    var answerValue: Int
}

struct AssessmentResult: Codable, Equatable {
    var score: Int
    var severityBand: String
    var interpretation: String
}

struct AssessmentSession: Identifiable, Codable, Equatable {
    var id: String
    var type: AssessmentType
    var startedAt: Date
    var completedAt: Date?
    var responses: [Response]
    var result: AssessmentResult?
}
