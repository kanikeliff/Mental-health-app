//
//  MoodView.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//

import SwiftUI

struct MoodView: View {
    @StateObject var vm: MoodViewModel

    var body: some View {
        VStack(spacing: 12) {

            Text("Daily Mood")
                .font(.title2)
                .bold()

            Stepper("Mood: \(vm.moodScore)", value: $vm.moodScore, in: 1...5)

            TextField("Note (optional)", text: $vm.note)
                .textFieldStyle(.roundedBorder)

            Button("Save Mood") {
                Task { await vm.submit() }
            }
            .buttonStyle(.borderedProminent)

            if let err = vm.errorMsg {
                Text(err)
                    .foregroundStyle(.red)
            }

            Divider()

            // 🔥 MOOD LIST + SWIPE DELETE
            List {
                ForEach(vm.moods) { e in
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Mood: \(e.moodScore)/5")
                            .bold()
                        if !e.note.isEmpty {
                            Text(e.note)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
                .onDelete(perform: vm.deleteMood) // ✅ SİLME
            }
        }
        .padding()

        .task {
           await  vm.load()
        }
        .refreshable {
            await vm.load()
        }

        .alert("Error", isPresented: Binding(
            get: { vm.errorMsg != nil },
            set: { if !$0 { vm.errorMsg = nil } }
        )) {
            Button("OK", role: .cancel) {
                vm.errorMsg = nil
            }
        } message: {
            Text(vm.errorMsg ?? "Unknown error")
        }
    }
}
