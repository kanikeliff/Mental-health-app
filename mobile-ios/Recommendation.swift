//
//  Recommendation.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//



import Foundation

struct Recommendation: Identifiable, Codable, Equatable {
    var id: String
    var title: String
    var rationale: String
    var action: String
}
