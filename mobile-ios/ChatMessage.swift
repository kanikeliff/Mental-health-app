//
//  ChatMessage.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//



import Foundation

enum ChatRole: String, Codable {
    case user, assistant
}

struct ChatMessage: Identifiable, Codable, Equatable {
    var id: String
    var timestamp: Date
    var role: ChatRole
    var content: String
    var sentiment: SentimentResult?
}
