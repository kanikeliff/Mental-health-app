# Mental-health-app

## Nuvio AI – Smart Therapy Assistant

## Project Overview
Nuvio AI is an iOS-based smart mental health assistant designed to support users through AI-powered chat, standardized psychological assessments, mood tracking, and personalized insights, while strictly respecting privacy and ethical boundaries.

This project is developed as part of the course **Software Engineering – Software Project Planning & Estimation** and follows a layered MVVM-based architecture with a service-oriented backend and AI components.

---

## Key Features
- AI-powered chat with emotion and sentiment inference
- Standardized mental health assessments (PHQ-9, WHO-5, SCL-90)
- Mood tracking with visualization and trend analysis
- Insights and simple recommendations
- Secure report generation and export
- Privacy-first design with encryption and consent enforcement

---

## System Architecture
The system follows a layered architecture:

SwiftUI iOS App
↓
ViewModels (MVVM)
↓
Domain Logic and Repository
↓
Backend API (FastAPI) and AI Engine
↓
Firebase Services

### Architecture Documentation
- docs/SRS.pdf
- docs/SDS.pdf

---

## Technologies Used

### Mobile Application
- Swift
- SwiftUI
- MVVM architecture
- XCTest
- XCUITest

### Backend API
- Python
- FastAPI
- PyTest
- Docker

### AI and Machine Learning
- Python
- scikit-learn
- TensorFlow
- Serialized models (.pkl)

### Cloud and Security
- Firebase Authentication
- Firebase Firestore
- Firebase Storage
- Encryption services
- Firebase Emulator (for testing)

### Tooling and CI
- GitHub Actions
- Xcode Instruments
- Docker Compose

---

## Repository Structure
nuvio-ai/
├── docs/
├── mobile-ios/
├── backend-api/
├── ai-engine/
├── firebase/
├── ci/
└── README.md

Each directory corresponds directly to components defined in the **Software Design Specification (SDS)**.

---

## Testing Strategy
Testing follows a hybrid approach:

### Testing Methods
- Bottom-up testing for core logic
- Incremental integration testing across components
- Black-box testing based on system use cases
- White-box testing based on source code artifacts

### Test Coverage
- 25 black-box test cases
- 11 core unit tests
- 100 percent use-case path coverage

Full details are available in:
- docs/TestSpecification.pdf

---

## Ethics and Limitations
- The system does not provide medical diagnosis
- No real-time therapist communication is supported
- No crisis intervention functionality is included
- The application is designed as a self-reflection and support tool only

These limitations are explicitly documented in the SRS.

---

## How to Run

### iOS Application
1. Open `mobile-ios/NuvioAI.xcodeproj` in Xcode
2. Configure Firebase plist files
3. Run on simulator or physical device

### Backend API
```bash
cd backend-api
pip install -r requirements.txt
uvicorn app.main:app --reload
AI Engine
cd ai-engine
pip install -r requirements.txt
python inference/predict.py
Team Members
Can Sar
Elif Kanık
Berkay Aydın
Mert Doruk Özdemir
License
This project was developed for academic purposes as part of a university course.
