//
//  FirebaseAuthService.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//

import Foundation
import FirebaseAuth

final class FirebaseAuthService: AuthService {

    func signIn(email: String, password: String) async throws -> String {
        do {
            let res = try await Auth.auth().signIn(withEmail: email, password: password)
            print("✅ signIn ok uid=", res.user.uid)
            return res.user.uid
        } catch {
            print("❌ signIn error:", error)
            throw error
        }
    }

    func signUp(email: String, password: String) async throws -> String {
        do {
            let res = try await Auth.auth().createUser(withEmail: email, password: password)
            print("✅ signUp ok uid=", res.user.uid)
            return res.user.uid
        } catch {
            print("❌ signUp error:", error)
            throw error
        }
    }

    func signOut() async {
        do {
            try Auth.auth().signOut()
            print("✅ signOut ok")
        } catch {
            print("❌ signOut error:", error)
        }
    }
}
