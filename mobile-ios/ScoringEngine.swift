//
//  ScoringEngine.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//


import Foundation

struct ScoringEngine {
    func score(type: AssessmentType, responses: [Response]) -> AssessmentResult {
        let total = responses.map { $0.answerValue }.reduce(0, +)

        switch type {
        case .phq9:
            let band: String
            if total <= 4 { band = "Minimal" }
            else if total <= 9 { band = "Mild" }
            else if total <= 14 { band = "Moderate" }
            else if total <= 19 { band = "Moderately Severe" }
            else { band = "Severe" }

            return AssessmentResult(
                score: total,
                severityBand: band,
                interpretation: "Your PHQ-9 score suggests: \(band). Consider small daily routines and reach out to support if needed."
            )

        case .who5:
            // WHO-5 often scaled; we keep it simple: higher is better
            let band = total >= 13 ? "Good well-being" : "Low well-being"
            return AssessmentResult(
                score: total,
                severityBand: band,
                interpretation: "Your WHO-5 result indicates \(band). Try sleep + movement + social support habits."
            )

        case .scl90:
            let band = total >= 20 ? "Elevated distress" : "Within normal range"
            return AssessmentResult(
                score: total,
                severityBand: band,
                interpretation: "SCL-90 summary: \(band). Track triggers and consider structured self-care."
            )
        }
    }
}
