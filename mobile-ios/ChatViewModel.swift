//
//  ChatViewModel.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//



import Foundation
import Combine

@MainActor
final class ChatViewModel: ObservableObject {

    @Published var messages: [ChatMessage] = []
    @Published var inputText: String = ""
    @Published var isSending = false
    @Published var errorMsg: String?

    private let repo: DataRepository
    private let ml: EmotionInferenceService
    private let api: BackendAPI

    init(
        repo: DataRepository,
        ml: EmotionInferenceService = SimpleEmotionInference(),
        api: BackendAPI = MockBackendAPI()
    ) {
        self.repo = repo
        self.ml = ml
        self.api = api
    }

        
    func resetConversation() {
        Task {
            do {
                try await repo.clearChat()
                messages = []
            } catch {
                errorMsg = "Failed  to reset chat"
            }
        }
    }

    func loadHistory() {
        Task {
            do {
                messages = try await repo.getChatThread()
            } catch {
                errorMsg = "Failed to load chat."
            }
        }
    }

    func send() {
        let trimmed = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }

        isSending = true
        errorMsg = nil

        Task {
            do {
                // 1️⃣ Sentiment
                let sentiment = await ml.predict(text: trimmed)

                // 2️⃣ User message
                let userMsg = ChatMessage(
                    id: UUID().uuidString,
                    timestamp: Date(),
                    role: .user,
                    content: trimmed,
                    sentiment: sentiment
                )

                messages.append(userMsg)
                inputText = ""
                try await repo.saveMessage(userMsg)

                // 3️⃣ Backend
                let dto = try await api.chat(
                    userText: trimmed,
                    sentiment: sentiment,
                    context: messages
                )

                // 4️⃣ Assistant message
                let replyMsg = ChatMessage(
                    id: UUID().uuidString,
                    timestamp: Date(),
                    role: .assistant,
                    content: dto.reply,
                    sentiment: nil
                )

                messages.append(replyMsg)
                try await repo.saveMessage(replyMsg)

                isSending = false
            } catch {
                isSending = false
                errorMsg = "Message could not be sent."
            }
        }
    }
}
