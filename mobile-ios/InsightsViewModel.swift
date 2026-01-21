//
//  InsightsViewModel.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//


import Foundation
import Combine
@MainActor
final class InsightsViewModel: ObservableObject {
    @Published var insights: WeeklyInsights?
    @Published var isLoading: Bool = false
    @Published var errorMsg: String?
    @Published var recommendations: [Recommendation] = []
    

    private let repo: DataRepository

    init(repo: DataRepository) {
        self.repo = repo
    }

    func loadWeekly() {
        isLoading = true
        errorMsg = nil

        Task {
            do {
                let moods = try await repo.getMoodHistory()
                let weekly = buildWeeklyInsights(from: moods)
                insights = weekly
                recommendations = buildRecommendations(from: weekly)
                isLoading = false
            } catch {
                isLoading = false
                errorMsg = "Failed to load insights."
            }
        }
        
    }
    private func buildRecommendations(from insights: WeeklyInsights) -> [Recommendation] {
        var recs: [Recommendation] = []

        // 1️⃣ Düşük ortalama mood
        if insights.averageMood < 3 {
            recs.append(
                Recommendation(
                    id : UUID().uuidString,
                    title: "Support your mood",
                    rationale: "Your average mood has been on the lower side this week.",
                    action: "Try a short daily walk or write one thing you’re grateful for today."
                )
            )
        }

        // 2️⃣ Dalgalı ruh hali
        if let best = insights.bestDay,
           let worst = insights.worstDay,
           best.avgMood - worst.avgMood >= 1.5 {

            recs.append(
                Recommendation(
                    id : UUID().uuidString,
                    title: "Reduce mood fluctuations",
                    rationale: "Your mood changed significantly between days.",
                    action: "Aim for consistent sleep and meal times to stabilize your routine."
                )
            )
        }

        // 3️⃣ Az veri varsa
        if insights.recordedDays < 3 {
            recs.append(
                Recommendation(
                    id : UUID().uuidString,
                    title: "Keep it up",
                    rationale: "Your mood looks relatively stable this week.",
                    action: "Maintain your routine and do one enjoyable activity today."
                )
            )
        }

        // 4️⃣ Her şey yolundaysa
        if recs.isEmpty {
            recs.append(
                Recommendation(
                    id : UUID().uuidString,
                    title: "Keep it up",
                    rationale: "Your mood looks relatively stable this week.",
                    action: "Maintain your routine and do one enjoyable activity today."
                )
            )
        }

        return recs
    }

    private func buildWeeklyInsights(from moods: [MoodEntry]) -> WeeklyInsights {
        let cal = Calendar.current
        let now = Date()
        let start = cal.date(byAdding: .day, value: -6, to: cal.startOfDay(for: now))! // 7 gün
        let end = now

        // Son 7 gün filtrele
        let recent = moods.filter { $0.timestamp >= start && $0.timestamp <= end }

        // Gün bazında grupla
        let grouped = Dictionary(grouping: recent) { entry in
            cal.startOfDay(for: entry.timestamp)
        }

        // Her günün ortalamasını çıkar
        var points: [DailyMoodPoint] = grouped.map { (day, entries) in
            let avg = entries.map { Double($0.moodScore) }.reduce(0, +) / Double(entries.count)
            return DailyMoodPoint(day: day, avgMood: avg, count: entries.count)
        }

        // Günleri sırala (eski -> yeni)
        points.sort { $0.day < $1.day }

        // Genel ortalama
        let allScores = recent.map { Double($0.moodScore) }
        let overallAvg = allScores.isEmpty ? 0.0 : (allScores.reduce(0, +) / Double(allScores.count))

        // Best/Worst
        let best = points.max { $0.avgMood < $1.avgMood }
        let worst = points.min { $0.avgMood < $1.avgMood }

        return WeeklyInsights(
            from: start,
            to: end,
            recordedDays: points.count,
            averageMood: overallAvg,
            bestDay: best,
            worstDay: worst,
            points: points
        )
    }
    var patternText: String {
        guard let insights else { return "Not enough data yet." }
        guard insights.points.count >= 2 else {
            return "Track more days to detect patterns."
        }

        let first = insights.points.first!.avgMood
        let last = insights.points.last!.avgMood
        let diff = last - first

        if diff > 0.5 {
            return "Your mood has been improving over the last few days."
        } else if diff < -0.5 {
            return "Your mood has been declining recently."
        } else {
            return "Your mood has been relatively stable this week."
        }
    }
    var extraRecommendation: String? {
        guard let insights else { return nil }

        if insights.averageMood < 3 {
            return "Try to slow down today and do something calming."
        }

        if insights.recordedDays < 3 {
            return "Log your mood daily for better insights."
        }

        return nil
    }
}

