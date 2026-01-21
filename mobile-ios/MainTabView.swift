//
//  MainTabView.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//

import Foundation

import SwiftUI

struct MainTabView: View {
    let repo: DataRepository

    var body: some View {
        TabView {
            ChatView(vm: ChatViewModel(repo: repo))
                .tabItem { Label("Chat", systemImage: "message") }

            MoodView(vm: MoodViewModel(repo: repo))
                .tabItem { Label("Mood", systemImage: "face.smiling") }

            AssessmentsHomeView(vm: AssessmentsViewModel(repo: repo))
                .tabItem { Label("Tests", systemImage: "checklist") }

            InsightsView(vm: InsightsViewModel(repo: repo))
                .tabItem { Label("Insights", systemImage: "chart.line.uptrend.xyaxis") }

            ReportView(vm: ReportViewModel(repo: repo))
                .tabItem { Label("Report", systemImage: "doc") }
            AccountView()
                .tabItem { Label("Account",systemImage: "person.circle")}
            InsightsView(vm: InsightsViewModel(repo: repo))
        }
    }
}
