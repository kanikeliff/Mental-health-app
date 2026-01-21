//
//  TrendAnalyzer.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//


import Foundation

struct TrendAnalyzer {
    func weeklySummary(moods: [MoodEntry], assessments: [AssessmentSession]) -> String {
        let last7 = moods.filter { $0.timestamp >= Calendar.current.date(byAdding: .day, value: -7, to: Date())! }
        guard !last7.isEmpty else { return "No mood history yet. Start with a daily check-in to see trends." }

        let avg = Double(last7.map{$0.moodScore}.reduce(0,+)) / Double(last7.count)
        let moodText = String(format: "%.1f", avg)

        let latestAssessment = assessments.last?.result?.severityBand ?? "No recent assessments"
        return "Last 7 days average mood: \(moodText)/5. Latest assessment: \(latestAssessment)."
    }

    func detectPatterns(moods: [MoodEntry]) -> [String] {
        guard moods.count >= 3 else { return [] }
        let sorted = moods.sorted { $0.timestamp < $1.timestamp }
        let last3 = sorted.suffix(3).map { $0.moodScore }

        if last3[0] > last3[1] && last3[1] > last3[2] {
            return ["Mood is trending down in the last few check-ins."]
        }
        if last3[0] < last3[1] && last3[1] < last3[2] {
            return ["Mood is improving across recent check-ins."]
        }
        return ["Mood is fluctuating recently."]
    }
}
