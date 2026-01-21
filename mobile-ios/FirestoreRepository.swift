//
//  FirestoreRepository.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//

import Foundation

import FirebaseAuth
import FirebaseFirestore

final class FirestoreRepository: DataRepository {
    
    
    private let db = Firestore.firestore()
    private let moodsPath = "moods"

    private func currentUID() throws -> String {
        guard let uid = Auth.auth().currentUser?.uid else {
            throw NSError(domain: "FirestoreRepository", code: 401,
                          userInfo: [NSLocalizedDescriptionKey: "User not signed in"])
        }
        return uid
    }

    private func moodsCol() throws -> CollectionReference {
        db.collection("users").document(try currentUID()).collection("moods")
    }
    func deleteMood(id: String) async throws {
        try await db
            .collection(moodsPath)
            .document(id)
            .delete()
    }
    

    // MARK: - Mood
    func saveMood(_ entry: MoodEntry) async throws {
        // Document id = entry.id (stable)
        try await moodsCol().document(entry.id).setData([
            "id": entry.id,
            "timestamp": Timestamp(date: entry.timestamp),
            "moodScore": entry.moodScore,
            "note": entry.note
        ])
    }

    func getMoodHistory() async throws -> [MoodEntry] {
        let snap = try await moodsCol()
            .order(by: "timestamp", descending: true)
            .getDocuments()

        return snap.documents.compactMap { doc in
            let d = doc.data()
            guard
                let id = d["id"] as? String,
                let ts = d["timestamp"] as? Timestamp,
                let moodScore = d["moodScore"] as? Int,
                let note = d["note"] as? String
            else { return nil }

            return MoodEntry(id: id, timestamp: ts.dateValue(), moodScore: moodScore, note: note)
        }
    }
    private func chatCol() throws -> CollectionReference {
        db.collection("users").document(try currentUID()).collection("chat")
    }
    func saveMessage(_ msg: ChatMessage) async throws {
        var data: [String: Any] = [
            "id": msg.id,
            "timestamp": Timestamp(date: msg.timestamp),
            "role": msg.role.rawValue,
            "content": msg.content
        ]

        if let s = msg.sentiment {
            data["sentiment"] = [
                "polarity": s.polarity,
                "topEmotion": s.topEmotion,
                
            ]
        }

        try await chatCol().document(msg.id).setData(data)
    }

    func getChatThread() async throws -> [ChatMessage] {
        let snap = try await chatCol()
            .order(by: "timestamp", descending: false)
            .getDocuments()

        var out: [ChatMessage] = []

        for doc in snap.documents {
            let d = doc.data()

            guard
                let id = d["id"] as? String,
                let ts = d["timestamp"] as? Timestamp,
                let roleStr = d["role"] as? String,
                let role = ChatRole(rawValue: roleStr),
                let content = d["content"] as? String
            else { continue }

            var sentiment: SentimentResult? = nil
            if let s = d["sentiment"] as? [String: Any] {
                if let polarity = s["polarity"] as? Double,
                   let topEmotion = s["topEmotion"] as? String {

                    let probsAny = s["emotionProbs"] as? [String: Any] ?? [:]
                    var probs: [String: Double] = [:]
                    for (k, v) in probsAny {
                        if let dv = v as? Double { probs[k] = dv }
                        else if let iv = v as? Int { probs[k] = Double(iv) } // safety
                    }

                    sentiment = SentimentResult(polarity: polarity, topEmotion: topEmotion)
                }
            }

            out.append(ChatMessage(
                id: id,
                timestamp: ts.dateValue(),
                role: role,
                content: content,
                sentiment: sentiment
            ))
        }

        return out
    }
    func clearChat() async throws {
        let snapshot = try await db.collection("chat").getDocuments()
        for doc in snapshot.documents {
            try await doc.reference.delete()
        }
        
    }
    

    // MARK: - Chat / Assessment (şimdilik placeholder)
    // Senin app bu methodları çağırıyorsa sonra aynı patternle ekleriz.
   

    func saveAssessment(_ session: AssessmentSession) async throws { }
    func getAssessments() async throws -> [AssessmentSession] { [] }
}
