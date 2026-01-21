//
//  EmotionInferenceService.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//import Foundation

import Foundation

protocol EmotionInferenceService {
    func predict(text: String) async -> SentimentResult
}


struct SimpleEmotionInference: EmotionInferenceService {

    func predict(text: String) async -> SentimentResult {
        let lower = text.lowercased()

        let emotion: String
        let polarity: Double

        if lower.contains("sad") || lower.contains("down") || lower.contains("unhappy") {
            emotion = "sad"
            polarity = -0.6
        } else if lower.contains("stress") || lower.contains("anx") || lower.contains("worried") {
            emotion = "anxious"
            polarity = -0.4
        } else if lower.contains("happy") || lower.contains("good") || lower.contains("great") {
            emotion = "happy"
            polarity = 0.6
        } else {
            emotion = "neutral"
            polarity = 0.0
        }

        // Build emotion probabilities safely (no duplicate keys)
        var probs: [String: Double] = [:]

        // Always include detected emotion
        probs[emotion] = 0.9

        // Add neutral only if it's not the main emotion
        if emotion != "neutral" {
            probs["neutral"] = 0.1
        }

        return SentimentResult(
            polarity: polarity,
            topEmotion: emotion,
            
        )
    }
}
