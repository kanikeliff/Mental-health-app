//
//  NuvioApp.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//

import SwiftUI
import FirebaseCore

@main
struct NuvioApp: App {
    init() {
        FirebaseApp.configure()
    }

    var body: some Scene {
        WindowGroup { AppRootView() }
    }
}
