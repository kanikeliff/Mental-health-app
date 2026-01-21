//
//  AccountView.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//

import Foundation

import SwiftUI

struct AccountView: View {
    @EnvironmentObject var authVM: AuthViewModel

    var body: some View {
        NavigationStack {
            VStack(spacing: 16) {
                Text("Account")
                    .font(.title2).bold()

                if let uid = authVM.userId {
                    Text("User ID:")
                        .foregroundStyle(.secondary)
                    Text(uid)
                        .font(.footnote)
                        .textSelection(.enabled)
                }

                Spacer()

                Button(role: .destructive) {
                    authVM.signOut()
                } label: {
                    Text("Log out")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)

            }
            .padding()
            .navigationTitle("Account")
        }
    }
}
