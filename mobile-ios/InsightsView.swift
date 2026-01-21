//
//  InsightsView.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//
import SwiftUI

struct InsightsView: View {
    @StateObject var vm: InsightsViewModel

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {

                // MARK: - Title
                Text("Insights")
                    .font(.title2)
                    .bold()

                // MARK: - Loading
                if vm.isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity, alignment: .center)

                // MARK: - Data Loaded
                } else if let insights = vm.insights {

                    // MARK: - Weekly Summary
                    GroupBox {
                        VStack(alignment: .leading, spacing: 6) {
                            Text("Last 7 days")
                                .font(.headline)

                            Text("Recorded days: \(insights.recordedDays)")
                            Text(String(format: "Average mood: %.2f / 5", insights.averageMood))

                            if let best = insights.bestDay {
                                Text(
                                    "Best day: \(best.day.formatted(date: .abbreviated, time: .omitted)) • \(String(format: "%.1f", best.avgMood))"
                                )
                            }

                            if let worst = insights.worstDay {
                                Text(
                                    "Worst day: \(worst.day.formatted(date: .abbreviated, time: .omitted)) • \(String(format: "%.1f", worst.avgMood))"
                                )
                            }
                        }
                    }

                    // MARK: - Patterns  ✅ EKLENDİ
                    GroupBox {
                        VStack(alignment: .leading, spacing: 6) {
                            Text("Patterns")
                                .font(.headline)

                            Text(vm.patternText)
                                .foregroundStyle(.secondary)
                        }
                    }

                    // MARK: - Daily Points
                    VStack(spacing: 6) {
                        ForEach(insights.points) { p in
                            HStack {
                                Text(p.day.formatted(date: .abbreviated, time: .omitted))
                                Spacer()
                                Text(String(format: "%.1f / 5", p.avgMood))
                            }
                        }
                    }

                    // MARK: - Extra Recommendation  ✅ EKLENDİ
                    if let extra = vm.extraRecommendation {
                        GroupBox {
                            VStack(alignment: .leading, spacing: 6) {
                                Text("Insight")
                                    .font(.headline)

                                Text(extra)
                                    .foregroundStyle(.secondary)
                            }
                        }
                    }

                    // MARK: - Recommendations
                    Text("Recommendations")
                        .font(.headline)
                        .padding(.top, 8)

                    if vm.recommendations.isEmpty {
                        Text("No recommendations yet.")
                            .foregroundStyle(.secondary)
                    } else {
                        ForEach(vm.recommendations) { rec in
                            VStack(alignment: .leading, spacing: 6) {
                                Text(rec.title)
                                    .font(.subheadline)
                                    .bold()

                                Text(rec.rationale)
                                    .foregroundStyle(.secondary)

                                Text(rec.action)
                                    .font(.footnote)
                            }
                            .padding()
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(.gray.opacity(0.12))
                            .cornerRadius(12)
                        }
                    }

                // MARK: - No Data
                } else {
                    Text("No data yet.")
                        .foregroundStyle(.secondary)
                }
            }
            .padding()
        }
        .task {
            vm.loadWeekly()
        }
        .refreshable {
            vm.loadWeekly()
        }
    }
}
