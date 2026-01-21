//
//  EncryptionService.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//


import Foundation
import CryptoKit

protocol EncryptionService {
    func encrypt(_ data: Data) throws -> Data
    func decrypt(_ data: Data) throws -> Data
}

// Simple symmetric encryption for demo (NOT keychain-managed here yet)
struct SimpleEncryption: EncryptionService {
    private let key = SymmetricKey(size: .bits256)

    func encrypt(_ data: Data) throws -> Data {
        let sealed = try AES.GCM.seal(data, using: key)
        return sealed.combined ?? Data()
    }

    func decrypt(_ data: Data) throws -> Data {
        let box = try AES.GCM.SealedBox(combined: data)
        return try AES.GCM.open(box, using: key)
    }
}
