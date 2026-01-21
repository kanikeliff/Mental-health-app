//
//  AuthViewModel.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//


import Foundation
import FirebaseAuth
import Combine
@MainActor
final class AuthViewModel: ObservableObject {
    @Published var isSignedIn = false
    @Published var errorMsg: String?

    let auth: AuthService
    let repo: DataRepository
    private(set) var userId: String?

    init(auth: AuthService, repo: DataRepository) {
        self.auth = auth
        self.repo = repo
        if let user = Auth.auth().currentUser {
            self.userId = user.uid
            self.isSignedIn = true
        }
    }

    func signIn(email: String, password: String) {
        Task {
            do {
                userId = try await auth.signIn(email: email, password: password)
                isSignedIn = true
                errorMsg = nil
            } catch {
                isSignedIn = false
                errorMsg = prettyAuthError(error)
            }
        }
    }

    func signUp(email: String, password: String) {
        Task {
            do {
                userId = try await auth.signUp(email: email, password: password)
                isSignedIn = true
                errorMsg = nil
            } catch {
                isSignedIn = false
                errorMsg = prettyAuthError(error)
            }
        }
    }

    func signOut() {
        Task {
            await auth.signOut()
            isSignedIn = false
            userId = nil
        }
    }

    private func prettyAuthError(_ error: Error) -> String {
        let ns = error as NSError

        // FirebaseAuth errors are in AuthErrorDomain with integer codes
        if ns.domain == AuthErrorDomain, let code = AuthErrorCode(rawValue: ns.code) {
            switch code {
            case .operationNotAllowed:
                return "Email/Password sign-in is disabled in Firebase Console."
            case .invalidEmail:
                return "Invalid email format."
            case .wrongPassword:
                return "Wrong password."
            case .userNotFound:
                return "No account exists with this email."
            case .emailAlreadyInUse:
                return "This email is already in use."
            case .weakPassword:
                return "Password is too weak (min 6 chars)."
            case .networkError:
                return "Network error. Check your internet connection."
            default:
                return "Auth error"
            }
        }

        return "Auth error: \(ns.localizedDescription)"
    }
}
