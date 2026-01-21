//
//  ChatView.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//

import Foundation
import SwiftUI

struct ChatView: View {
    @StateObject var vm: ChatViewModel

    var body: some View {
        VStack {
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 10) {
                    ForEach(vm.messages) { msg in
                        HStack {
                            if msg.role == .assistant {
                                Text(msg.content)
                                    .padding(10)
                                    .background(.gray.opacity(0.2))
                                    .cornerRadius(12)
                                Spacer()
                            } else {
                                Spacer()
                                Text(msg.content)
                                    .padding(10)
                                    .background(.blue.opacity(0.2))
                                    .cornerRadius(12)
                            }
                        }
                    }
                }.padding()
            }

            if let err = vm.errorMsg {
                Text(err).foregroundStyle(.red)
            }

            HStack {
                TextField("Type...", text: $vm.inputText)
                    .textFieldStyle(.roundedBorder)

                Button(vm.isSending ? "..." : "Send") {
                    vm.send() // send zaten Task içinde
                }
                .disabled(vm.isSending)
            }
            .padding()
        }
        .task { vm.resetConversation()}              // ✅ onAppear yerine
        .refreshable { vm.loadHistory() }       // ✅ pull-to-refresh
    }
}
