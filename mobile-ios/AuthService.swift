//
//  AuthService.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//

import Foundation

protocol AuthService {
    func signIn(email: String, password: String) async throws -> String // returns userId
    func signUp(email: String, password: String) async throws -> String
    func signOut() async
}

// Simple placeholder; swap with FirebaseAuth implementation later
struct SimpleAuthService: AuthService {
    func signIn(email: String, password: String) async throws -> String {
        guard !email.isEmpty, !password.isEmpty else { throw NSError(domain: "Auth", code: 1) }
        return "mock-user"
    }
    func signUp(email: String, password: String) async throws -> String {
        guard !email.isEmpty, !password.isEmpty else { throw NSError(domain: "Auth", code: 2) }
        return "mock-user"
    }
    func signOut() async { }
}
