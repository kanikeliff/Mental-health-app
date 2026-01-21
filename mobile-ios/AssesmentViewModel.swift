//
//  AssesmentViewModel.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//



import Foundation
import Combine
@MainActor
final class AssessmentsViewModel: ObservableObject {
    @Published var selectedType: AssessmentType = .phq9
    @Published var questions: [Question] = []
    @Published var answers: [String: Int] = [:]
    @Published var currentResult: AssessmentResult?
    @Published var errorMsg: String?

    private let repo: DataRepository
    private let catalog = AssessmentCatalog()
    private let scorer = ScoringEngine()

    init(repo: DataRepository) { self.repo = repo }

    func start(type: AssessmentType) {
        selectedType = type
        questions = catalog.questions(for: type)
        answers = [:]
        currentResult = nil
        errorMsg = nil
    }

    func setAnswer(questionId: String, value: Int) {
        answers[questionId] = value
    }

    func finish() {
        // BB-08 missing answer: block finish  [oai_citation:11‡8298021.pdf](sediment://file_0000000093fc71f4b9be0eca65ac1a34)
        for q in questions {
            if answers[q.id] == nil {
                errorMsg = "Please answer all questions."
                return
            }
        }

        // validate range (BB-09)  [oai_citation:12‡8298021.pdf](sediment://file_0000000093fc71f4b9be0eca65ac1a34)
        for q in questions {
            let v = answers[q.id] ?? q.minValue
            if v < q.minValue || v > q.maxValue {
                errorMsg = "Invalid answer detected."
                return
            }
        }

        let responses = questions.map { q in
            Response(questionId: q.id, answerValue: answers[q.id] ?? q.minValue)
        }

        let result = scorer.score(type: selectedType, responses: responses)
        currentResult = result

        let session = AssessmentSession(
            id: UUID().uuidString,
            type: selectedType,
            startedAt: Date(),
            completedAt: Date(),
            responses: responses,
            result: result
        )

        Task {
            do { try await repo.saveAssessment(session) }
            catch { errorMsg = "Failed to save assessment." }
        }
    }
}
