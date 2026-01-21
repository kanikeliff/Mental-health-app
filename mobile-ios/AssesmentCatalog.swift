//
//  AssesmentCatalog.swift
//  Nuvio
//
//  Created by Can on 21.01.2026.
//



import Foundation

struct AssessmentCatalog {

    func questions(for type: AssessmentType) -> [Question] {
        switch type {

        // MARK: - PHQ-9
        case .phq9:
            let texts = [
                "Little interest or pleasure in doing things",
                "Feeling down, depressed, or hopeless",
                "Trouble falling or staying asleep, or sleeping too much",
                "Feeling tired or having little energy",
                "Poor appetite or overeating",
                "Feeling bad about yourself — or that you are a failure",
                "Trouble concentrating on things",
                "Moving or speaking so slowly that others could notice",
                "Thoughts that you would be better off dead"
            ]

            return texts.enumerated().map { index, text in
                Question(
                    id: "phq9_q\(index + 1)",
                    text: text,
                    options: [
                        "Not at all",
                        "Several days",
                        "More than half the days",
                        "Nearly every day"
                    ],
                    minValue: 0,
                    maxValue: 3
                )
            }

        // MARK: - WHO-5
        case .who5:
            let texts = [
                "I have felt cheerful and in good spirits",
                "I have felt calm and relaxed",
                "I have felt active and vigorous",
                "I woke up feeling fresh and rested",
                "My daily life has been filled with things that interest me"
            ]

            return texts.enumerated().map { index, text in
                Question(
                    id: "who5_q\(index + 1)",
                    text: text,
                    options: [
                        "At no time",
                        "Some of the time",
                        "Less than half the time",
                        "More than half the time",
                        "All of the time"
                    ],
                    minValue: 0,
                    maxValue: 4
                )
            }

        // MARK: - SCL-90
        case .scl90:
             let scl90Texts: [String] = [
                // 1–10
                "Headaches",
                "Nervousness or shakiness inside",
                "Unwanted thoughts or ideas",
                "Feeling lonely",
                "Feeling blue",
                "Worrying too much about things",
                "Feeling no interest in things",
                "Feeling fearful",
                "Trouble falling asleep",
                "Feeling low in energy or slowed down",

                // 11–20
                "Blaming yourself for things",
                "Crying easily",
                "Feeling restless",
                "Feeling tense or keyed up",
                "Spells of terror or panic",
                "Feeling hopeless about the future",
                "Trouble concentrating",
                "Feeling everything is an effort",
                "Feelings of worthlessness",
                "Thoughts of ending your life",

                // 21–30
                "Feeling trapped or caught",
                "Suddenly scared for no reason",
                "Poor appetite",
                "Feeling afraid to go out",
                "Trouble remembering things",
                "Feeling critical of others",
                "Feeling angry",
                "Muscle soreness",
                "Trouble getting your breath",
                "Hot or cold spells",

                // 31–40
                "Numbness or tingling",
                "A lump in your throat",
                "Feeling weak in parts of your body",
                "Heavy feelings in arms or legs",
                "Thoughts about death",
                "Overeating",
                "Feeling uneasy in crowds",
                "Feeling everything is unreal",
                "Trouble falling asleep",
                "Feeling self-conscious",

                // 41–50
                "Feeling judged by others",
                "Feeling others are watching you",
                "Having to check and double-check what you do",
                "Difficulty making decisions",
                "Fear of losing control",
                "Feeling inferior to others",
                "Feeling uneasy when people are talking about you",
                "Feeling very nervous",
                "Feeling easily annoyed or irritated",
                "Feeling distant or cut off from others",

                // 51–60
                "Having thoughts you cannot get rid of",
                "Feeling uncomfortable eating in public",
                "Feeling that people are unfriendly or dislike you",
                "Feeling others do not understand you",
                "Feeling that something bad is going to happen",
                "Feeling afraid in open spaces",
                "Having trouble enjoying things",
                "Feeling your mind going blank",
                "Feeling tense in social situations",
                "Feeling uncomfortable around people",

                // 61–70
                "Having trouble controlling your thoughts",
                "Feeling others are to blame for your troubles",
                "Feeling like you cannot trust people",
                "Feeling that people will take advantage of you",
                "Feeling watched or talked about",
                "Having thoughts about harming yourself",
                "Feeling detached from reality",
                "Feeling uneasy in unfamiliar places",
                "Feeling that your body is not functioning properly",
                "Feeling uncomfortable being alone",

                // 71–80
                "Feeling your thoughts are slowed down",
                "Feeling unable to relax",
                "Feeling emotionally numb",
                "Feeling that your feelings are blocked",
                "Feeling uneasy when things are out of place",
                "Feeling afraid of crowds",
                "Feeling uneasy in public places",
                "Feeling like you do not belong",
                "Feeling emotionally overwhelmed",
                "Feeling exhausted even after rest",

                // 81–90
                "Feeling tense when being watched",
                "Feeling that your thoughts are confused",
                "Feeling uneasy in close relationships",
                "Feeling uncomfortable expressing emotions",
                "Feeling mentally exhausted",
                "Feeling emotionally fragile",
                "Feeling uneasy about your future",
                "Feeling disconnected from your body",
                "Feeling psychologically overwhelmed",
                "Feeling unable to cope with daily life"
            ]
            return (1...90).map { i in
                Question(
                    id: "scl90_q\(i)",
                    text: scl90Texts[i - 1],
                    options: [
                        "Not at all",
                        "A little",
                        "Moderately",
                        "Quite a bit",
                        "Extremely"
                    ],
                    minValue: 0,
                    maxValue: 4
                )
            }
        }
    }
}
