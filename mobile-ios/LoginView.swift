//
//  LoginView.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//

import Foundation

import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authVM: AuthViewModel
    @State private var email = ""
    @State private var password = ""

    var body: some View {
        VStack(spacing: 12) {
            Image("NuvioLogo")
                .resizable()
                .scaledToFit()
                .frame(width: 260, height: 260)
                .padding(.bottom, 24)
            
           

            TextField("Email", text: $email)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .textFieldStyle(.roundedBorder)

            SecureField("Password", text: $password)
                .textFieldStyle(.roundedBorder)

            Button("Login") { authVM.signIn(email: email, password: password) }
                .buttonStyle(.borderedProminent)

            Button("Sign Up") { authVM.signUp(email: email, password: password) }
                .buttonStyle(.bordered)

            if let err = authVM.errorMsg {
                Text(err).foregroundStyle(.red)
            }
        }
        .padding()
    }
}
