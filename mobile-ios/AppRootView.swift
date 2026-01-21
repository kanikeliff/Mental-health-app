//
//  AppRootView.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//

import SwiftUI

struct AppRootView: View {
    @StateObject private var authVM: AuthViewModel

    init() {
        // For now keep local storage; later we will switch to FirestoreRepository()
        let repo: DataRepository = FirestoreRepository()
        let auth: AuthService = FirebaseAuthService()

        _authVM = StateObject(wrappedValue: AuthViewModel(auth: auth, repo: repo))
    }

    var body: some View {
        Group {
            if authVM.isSignedIn {
                MainTabView(repo: authVM.repo)
                    .environmentObject(authVM)
            } else {
                LoginView()
                    .environmentObject(authVM)
            }
        }
    }
}
