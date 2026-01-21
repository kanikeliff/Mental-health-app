//
//  AssesmentsRunnerView.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//
import SwiftUI
struct AssessmentRunnerView: View {
    @ObservedObject var vm: AssessmentsViewModel

    var body: some View {
        NavigationStack {
            List(vm.questions) { q in
                VStack(alignment: .leading, spacing: 8) {
                    Text(q.text).bold()

                    Picker("Answer", selection: Binding(
                        get: { vm.answers[q.id] ?? q.minValue },
                        set: { vm.setAnswer(questionId: q.id, value: $0) }
                    )) {
                        ForEach(q.minValue...q.maxValue, id: \.self) { v in
                            Text("\(v)").tag(v)
                        }
                    }
                    .pickerStyle(.segmented)
                }
                .padding(.vertical, 6)
            }
            .navigationTitle(vm.selectedType.rawValue)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Finish") { vm.finish() }
                }
            }
        }
        .onAppear {
            vm.start(type: vm.selectedType) // ✅ BU ŞART
        }
    }
}
        
