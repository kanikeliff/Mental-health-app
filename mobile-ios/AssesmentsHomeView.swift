//
//  AssesmentsHomeView.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//

import Foundation
import SwiftUI

struct AssessmentsHomeView: View {
    @StateObject var vm: AssessmentsViewModel
    @State private var showRunner = false
    
    var body: some View {
        VStack(spacing: 12) {
            Text("Assessments").font(.title2).bold()
            
            Picker("Type", selection: $vm.selectedType) {
                ForEach(AssessmentType.allCases, id: \.self) { t in
                    Text(t.rawValue).tag(t)
                }
            }
            .pickerStyle(.segmented)
            
            Button("Start") {
                vm.start(type: vm.selectedType)
                showRunner = true
            }
            .buttonStyle(.borderedProminent)
            
            if let res = vm.currentResult {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Score: \(res.score)")
                    Text("Band: \(res.severityBand)").bold()
                    Text(res.interpretation)
                }
                .padding()
                .background(.gray.opacity(0.15))
                .cornerRadius(12)
            }
            
            if let err = vm.errorMsg {
                Text(err).foregroundStyle(.red)
            }
        }
        .padding()
        .sheet(isPresented: $showRunner) {
            AssessmentRunnerView(vm: vm)
        }
    }
}
