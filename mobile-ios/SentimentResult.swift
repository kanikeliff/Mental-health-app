//
//  SentimentResult.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//



import Foundation

struct SentimentResult: Codable, Equatable {
    /// -1.0 ... +1.0
    let polarity: Double
    /// e.g. "sad", "anxious", "happy"
    let topEmotion: String
}

