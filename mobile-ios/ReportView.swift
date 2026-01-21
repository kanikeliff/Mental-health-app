//
//  ReportView.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//

import SwiftUI

struct ReportView: View {
    @StateObject var vm: ReportViewModel
    @State private var showShare = false

    var body: some View {
        NavigationView {
            VStack(spacing: 12) {
                HStack {
                    Button(vm.isLoading ? "Generating..." : "Generate Report") {
                        vm.generate()
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(vm.isLoading)

                    Spacer()

                    Button("Share") {
                        showShare = true
                    }
                    .buttonStyle(.bordered)
                    .disabled(vm.reportText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
                .padding(.horizontal)

                if let err = vm.errorMsg {
                    Text(err).foregroundStyle(.red)
                }

                Divider()

                ScrollView {
                    Text(vm.reportText.isEmpty ? "Tap “Generate Report” to build a weekly summary." : vm.reportText)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding()
                }
            }
            .navigationTitle("Report")
        }
        .sheet(isPresented: $showShare) {
            ShareSheet(items: [vm.reportText])
        }
        .onAppear {
            // İstersen otomatik generate:
            // if vm.reportText.isEmpty { vm.generate() }
        }
    }
}
