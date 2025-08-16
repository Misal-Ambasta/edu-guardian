# Edu-Guardian Frontend API Endpoints

Base URL: http(s)://<host>:<port>/api

Scope aligned with problem_statement.md
- Data Upload & Tracking: upload CSVs, create/update student journeys, list students with risk cues
- Historical Intelligence: similar patterns, recommended interventions, insights from past cohorts
- Sentiment Intelligence: analyze comments to rich emotion signals
- Weekly Intelligence Reports: generate/retrieve automated weekly reports and summaries
- Intervention Tracking: manage interventions and measure outcomes

Health and Auth
- GET /api/health — Service health probe
- POST /api/auth/token — OAuth2 password flow (placeholder)
- POST /api/auth/register — Register user (placeholder)
- GET /api/auth/me — Current user (placeholder)

1) Data Upload & Tracking (Students)
- GET /api/students/?course_id&risk_level&limit
  - Lists distinct students (latest journey snapshot + computed risk_level)
- GET /api/students/{student_id}/emotional-journey?course_id&start_week&end_week
  - Time series of emotion metrics per week + journey metrics
- GET /api/students/{student_id}/emotion-trajectory?course_id
  - Predicted emotion trajectory (uses trajectory predictor)
- GET /api/students/{student_id}/risk-assessment?course_id
  - Risk escalations, confidence scores, optimal intervention windows
- POST /api/students/{student_id}/journey
  - Body: StudentJourneyCreate {course_id, week_number, nps_score, aspect scores, comments, ...}
  - Creates/updates a journey and auto-fills emotion fields from comments
- POST /api/students/batch-journey
  - Body: List<StudentJourneyCreate>
  - Batch create/update with comment-based emotion analysis
- POST /api/students/upload-csv
  - multipart/form-data: file (CSV)
  - Validates + ingests a CSV; returns per-row results and quality metrics
- POST /api/students/upload-batch
  - Body: { "directory_path": string }
  - Processes all CSV files in a server directory (batch import)

2) Weekly Intelligence Reports
- GET /api/reports/weekly?course_id&week_number
  - Retrieves a generated weekly NPS intelligence report
- POST /api/reports/generate?course_id&week_number&force_regenerate=false
  - Creates a new weekly report (or returns existing if not forced)
- GET /api/reports/ai-insights?course_id&week_number
  - AI-powered insights derived from the weekly report
- GET /api/reports/recommendations?course_id&week_number
  - Dynamic recommendations based on insights and resource constraints
- GET /api/reports/executive-summary?course_id&week_number
  - Executive summary + confidence and data quality scores

3) Enhanced RAG (Historical Intelligence)
- GET /api/reports/enhanced-rag/similar-patterns?student_id&course_id&week_number&limit=5
  - Finds students with similar emotion patterns
- GET /api/reports/enhanced-rag/recommended-interventions?student_id&course_id&week_number
  - Interventions that worked for similar historical cases
- GET /api/reports/enhanced-rag/insights?student_id&course_id&week_number&limit=5
  - Narrative insights synthesized from similar patterns
- GET /api/reports/enhanced-rag/query?query&student_id&course_id&week_number
  - Ask targeted questions leveraging RAG context
- POST /api/reports/enhanced-rag/add-emotion-profile?student_id&course_id&week_number
  - Body: emotion_profile (EmotionProfile-like dict)
  - Adds an emotion profile to the vector DB

4) Emotion & Pattern Utilities
- GET /api/emotion/analyze?text
  - Analyzes a comment and returns a comprehensive EmotionProfile
- POST /api/emotion/batch-analyze
  - Body: ["text1", "text2", ...]
  - Batch emotion analysis for multiple texts
- GET /api/emotion/similar-patterns/{student_id}?course_id&week_number&limit=5
  - Similar patterns via vector DB (LangChain)
- GET /api/emotion/trajectory-prediction/{student_id}?course_id
  - Full trajectory prediction payload
- GET /api/emotion/multi-week-prediction/{student_id}?course_id&weeks_ahead=2
  - Risk escalations for future weeks
- GET /api/emotion/intervention-window/{student_id}?course_id
  - Optimal intervention windows
- POST /api/emotion/store-emotion-vector?student_id&course_id&week_number
  - Body: EmotionProfile
  - Stores an emotion pattern in vector DB
- GET /api/emotion/recommended-interventions/{student_id}?course_id&week_number
  - Recommendations from historical pattern matches
- GET /api/emotion/historical-patterns/{student_id}?course_id&week_number
  - Recognize historical patterns (service-computed)

5) Interventions (Management & Analytics)
- GET /api/interventions/?student_id&course_id&limit=10&with_recommendations=false
  - List interventions; optionally include recommendations for a student
- POST /api/interventions/
  - Body: InterventionCreate
  - Create a new intervention record
- GET /api/interventions/{intervention_id}
  - Fetch a specific intervention
- PUT /api/interventions/{intervention_id}
  - Body: InterventionUpdate
  - Update an intervention
- DELETE /api/interventions/{intervention_id}
  - Delete an intervention
- GET /api/interventions/track/{intervention_id}?student_id
  - Track emotional outcome of an intervention
- GET /api/interventions/templates/performance?template_name&limit=10
  - Performance metrics for intervention templates
- GET /api/interventions/timing/analysis
  - Timing analysis and impact on success

Notes
- All paths above are available under /api (as per FastAPI router prefixes in app.main).
- Some auth endpoints are placeholders; secure appropriately for production.
- Emotion and RAG endpoints rely on configured vector DB and API keys (e.g., GOOGLE_API_KEY).