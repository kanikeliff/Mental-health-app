//
//  RecommendationEngine.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//



import Foundation

struct RecommendationEngine {
    func generate(moods: [MoodEntry], latestAssessment: AssessmentResult?) -> [Recommendation] {
        var recs: [Recommendation] = []

        let avg = moods.isEmpty ? 0 : moods.map{$0.moodScore}.reduce(0,+) / moods.count
        if avg <= 2 {
            recs.append(Recommendation(
                id: UUID().uuidString,
                title: "Reset routine",
                rationale: "Your recent mood average is low.",
                action: "Try a 10-minute walk + one small task + a short check-in with someone you trust."
            ))
        } else {
            recs.append(Recommendation(
                id: UUID().uuidString,
                title: "Maintain stability",
                rationale: "Your mood looks relatively stable.",
                action: "Keep your sleep schedule and add one enjoyable activity today."
            ))
        }

        if let band = latestAssessment?.severityBand, band.contains("Severe") || band.contains("Elevated") {
            recs.append(Recommendation(
                id: UUID().uuidString,
                title: "Extra support",
                rationale: "Your assessment suggests higher distress.",
                action: "Consider professional support resources and reduce overload where possible."
            ))
        }

        return recs
    }
}
