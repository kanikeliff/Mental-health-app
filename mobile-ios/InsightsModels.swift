//
//  InsightsModels.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//

import Foundation


struct DailyMoodPoint: Identifiable, Equatable {
    let id = UUID().uuidString
    let day: Date          // gün başlangıcı
    let avgMood: Double    // o günün ortalaması (genelde 1 kayıt => moodScore)
    let count: Int
}

struct WeeklyInsights: Equatable {
    let from: Date
    let to: Date
    let recordedDays: Int
    let averageMood: Double
    let bestDay: DailyMoodPoint?
    let worstDay: DailyMoodPoint?
    let points: [DailyMoodPoint]
}
