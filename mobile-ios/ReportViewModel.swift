//
//  ReportViewModel.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//



import Foundation
import Combine

@MainActor
final class ReportViewModel: ObservableObject {

    @Published var reportText: String = ""
    @Published var isLoading: Bool = false
    @Published var errorMsg: String?

    private let repo: DataRepository
    private let builder = ReportBuilder()              // JSON / Data
    private let analyzer = TrendAnalyzer()             // Domain
    private let recommender = RecommendationEngine()   // Domain

    init(repo: DataRepository) {
        self.repo = repo
    }

    func generate() {
        isLoading = true
        errorMsg = nil

        Task {
            do {
                let moods = try await repo.getMoodHistory()
                let chat = try await repo.getChatThread()
                let assessments = (try? await repo.getAssessments()) ?? []

                let summary = analyzer.weeklySummary(
                    moods: moods,
                    assessments: assessments
                )

                let patterns = analyzer.detectPatterns(moods: moods)
                let latest = assessments.last?.result

                let recs = recommender.generate(
                    moods: moods,
                    latestAssessment: latest
                )

                // ✅ JSON REPORT (istersen backend / export için)
                _ = builder.build(
                    moods: moods,
                    assessments: assessments
                )

                // ✅ UI STRING REPORT
                reportText = """
                WEEKLY REPORT

                🧠 Summary
                \(summary)

                📊 Patterns
                \(patterns.isEmpty ? "No clear patterns detected." :
                    patterns.map { "• \($0)" }.joined(separator: "\n")
                )

                💡 Recommendations
                \(recs.isEmpty ? "No recommendations yet." :
                    recs.map { "• \($0.title)" }.joined(separator: "\n")
                )

                📝 Mood Entries
                Total entries: \(moods.count)

                💬 Chat Messages
                Total messages: \(chat.count)
                """

                isLoading = false
            } catch {
                isLoading = false
                errorMsg = "Failed to generate report."
            }
        }
    }
}
