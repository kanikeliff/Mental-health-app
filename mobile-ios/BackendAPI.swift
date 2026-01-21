//
//  BackendAPI.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//

import Foundation

struct ChatResponseDTO: Codable {
    let reply: String
}

protocol BackendAPI {
    func chat(
        userText: String,
        sentiment: SentimentResult?,
        context: [ChatMessage]
    ) async throws -> ChatResponseDTO
}

import Foundation

final class MockBackendAPI: BackendAPI {

    func chat(
        userText: String,
        sentiment: SentimentResult?,
        context: [ChatMessage]
    ) async throws -> ChatResponseDTO {

        // Gerçek API hissi
        try await Task.sleep(nanoseconds: 500_000_000)

        let text = userText.lowercased()
        let reply: String

        if context.count <= 1 {
            reply = "Hi 👋 I’m Nuvio. Want to tell me how you’re feeling today?"
        }
        else if text.contains("stress") || text.contains("stressed") {
            reply = "That sounds stressful 😟 What do you think triggered it today?"
        }
        else if text.contains("project") || text.contains("assignment") {
            reply = "Oh I see. What’s your project about?"
        }
        else if text.contains("mental") || text.contains("app") {
            reply = "That sounds meaningful 😊 When is your project due?"
        }
        else if text.contains("tonight") {
            reply = "That’s a tight deadline 😬 What part are you working on right now?"
        }
        else if text.contains("coding") {
            reply = "Coding under pressure can be tough. Is there a specific bug slowing you down?"
        }
        else if text.contains("almost") || text.contains("done") {
            reply = "That’s great progress 👏 You’re closer than you think!"
        }
        else {
            reply = "I’m listening 🙂 Want to tell me a bit more?"
        }

        return ChatResponseDTO(reply: reply)
    }
}
