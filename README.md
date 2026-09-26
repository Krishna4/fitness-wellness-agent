# Fitness & Wellness Agent

**Project:** Autonomous AI System for Personalized Health, Nutrition & Location Intelligence  
**Team:** FitPulse  
**Presenter / Student:** Murali Krishna D (`evernorth-aai-1152623`)  
**Submitted to:** Course Faculty & Mentors | IIIT Hyderabad  
**Repository:** [https://github.com/Krishna4/fitness-wellness-agent](https://github.com/Krishna4/fitness-wellness-agent)  
**Presentation:** `Fitness_Wellness_Agent_Presentation.pptx` (also at `~/Downloads/Fitness_Wellness_Agent.pptx`)

---

## 1. Executive Summary & Problem Formulation

The **Fitness & Wellness Agent** is an autonomous AI system engineered to deliver hyper-personalized physical exercise regimens, clinical-grade nutritional planning, proximity-aware fitness facility recommendations, and longitudinal progress tracking. 

Rather than relying on unconstrained, monolithic LLM text generation—which is prone to dangerous kinesiological and nutritional hallucinations—our team designed a **modular, tool-augmented agent architecture** with deterministic safety boundaries and persistent state continuity.

---

## 2. Core Capabilities Matrix

| Capability | Module / Tool | Technical Implementation & Grounding |
|---|---|---|
| **1. Targeted Workout Synthesis** | `recommend_workouts()` | Generates biomechanically safe routines matching user goals, equipment availability, and injury contraindications with structured set/rep coaching cues. |
| **2. Nutritional Precision** | `recommend_diet()` | Calculates metabolic expenditure via the Mifflin-St Jeor formula, establishes macro ratios, and matches meal schedules filtered against declared allergens. |
| **3. Geospatial Facility Discovery** | `search_nearby_facilities()` | Proximity-ranked spatial lookup connecting users with nearby gyms, calisthenics parks, Olympic tracks, and recovery studios based on live coordinates. |
| **4. Closed-Loop Progress Analytics** | `track_progress()` | Atomically ingests weight, volume, hydration, and adherence logs to calculate longitudinal deltas, trend lines, and consistency ratings. |
| **5. Active Plan Monitoring & Evolution** | `adapt_and_improve_plan()` | Actively monitors conversational feedback (soreness, fatigue, perceived exertion, pain cues) to dynamically recalibrate volume, substitute exercises, and evolve the plan in real-time. |

---

## 3. Team Engineering Insights & Architectural Decisions

1. **Tool Orchestration over Pure Generation**
   - End-to-end LLM generation is fundamentally brittle for quantitative exercise prescriptions and caloric metrics. Decoupling the reasoning brain from deterministic tool execution (`WorkoutDB`, `NutritionAPI`, `PlacesGPS`) guarantees mathematical accuracy and grounded kinesiology.
2. **Dual-Layer State Continuity**
   - Real-world health guidance fails without state persistence across sessions. Our team decoupled ephemeral multi-turn dialogue context from a persistent biometric/injury store (`fitness_memory.json`), ensuring consistent guidance across time.
3. **External Grounding Mitigates Risk**
   - Grounding exercise mechanics and meal compositions in verified domain catalogs rather than unbounded model recall prevents dangerous hallucinations in fitness prescriptions.
4. **Deterministic Pre-Triage Optimizes Latency**
   - Directing queries through rule-based intent triage prior to LLM invocation cuts token expenditure by >50% and provides sub-second response times for routine data and facility lookups.
5. **Safety as a Non-Negotiable Invariant**
   - Health systems mandate a clinical verification gate. Generated routines and diet plans must pass post-generation contraindication filters and safe caloric minimums before reaching the end-user.

---

## 4. End-to-End Execution Flow

```
[User Input: Query, Biometrics, GPS]
                 │
                 ▼
┌──────────────────────────────────────────────┐
│ 1. Intent Triage & Ingestion                 │ (Deterministic Zero-Token Classifier)
└──────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────┐
│ 2. Biometric State Hydration                 │ <──> [Persistent Memory Store]
└──────────────────────────────────────────────┘      (Profile, Injuries, History)
                 │
                 ▼
┌──────────────────────────────────────────────┐
│ 3. Autonomous Tool Execution (ReAct Brain)   │
│    • Dynamic Planning & Tool Calling         │
└──────────────────────┬───────────────────────┘
                       │
      ┌────────────────┼────────────────┐
      ▼                ▼                ▼
[Workout Engine] [Nutrition Calc] [Places API]
(Exercise DB)    (Macros & BMR)   (Nearby Gyms)
      └────────────────┬────────────────┘
                       │ Tool Results
                       ▼
┌──────────────────────────────────────────────┐
│ 4. Deterministic Clinical Safety Gate        │ ──> Blocks Contraindications & Allergens
└──────────────────────────────────────────────┘
                 │ (Verified Safe Guidance)
                 ▼
┌──────────────────────────────────────────────┐
│ 5. Response Dispatch & Metric Persistence    │ ──> Atomic Update to fitness_memory.json
└──────────────────────────────────────────────┘
```

---

## 5. Directory Structure & Verification

```
FitnessWellnessAgent_MuraliKrishnaD/
├── Fitness_Wellness_Agent_Presentation.pptx  # 2-Slide presentation built from AAI-Template.pptx
├── README.md                                 # Technical submission documentation
├── architecture_diagram.png                  # System architecture diagram
├── qr_repo.png                               # Project QR code asset
├── config.py                                 # Provider config (Gemini / Ollama / Fallback)
├── llm_client.py                             # Unified LLM client with backoff & fallback
├── schemas.py                                # Data contracts and typed entities
├── memory.py                                 # Dual-layer session and disk memory store
├── tools.py                                  # Domain tool suite with adaptive monitoring
├── triage.py                                 # Deterministic intent routing engine
├── rules.py                                  # Deterministic safety verification gate
├── agent.py                                  # ReAct agent orchestrator with LLM synthesis
├── app.py                                    # Interactive CLI with dynamic user onboarding
├── dashboard.html                            # Visual web app with dynamic plan generator
└── demo.py                                   # Automated 5-feature verification test suite
```

---

## 6. LLM Configuration & Switching

The system integrates **Google Gemini** as the primary high-speed reasoning model and supports local **Ollama**:

### A. Google Gemini (Default)
Uses the lightweight, high-throughput model:
```bash
# In .env or shell environment:
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-flash-lite-latest
GEMINI_API_KEY=your_key_here
```

### B. Local Ollama (Offline / Private Mode)
To run fully offline on local open weights (e.g. `qwen2.5:1.5b` or `llama3.2`):
```bash
# In .env or shell environment:
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:1.5b
OLLAMA_HOST=http://localhost:11434
```

### C. Graceful Fallback
If API limits are exceeded or Ollama is offline, the system automatically falls back to the deterministic, rule-grounded engine with zero downtime or crashing.

---

## 7. Running the System

### 1. Interactive Assistant (Dynamic User Profile Onboarding)
```bash
cd /Users/muralidupati/Downloads/IIt/FitnessWellnessAgent_MuraliKrishnaD
python3 app.py
```

### 2. Automated 5-Feature Test Suite
```bash
python3 demo.py
```

### 3. Visual Web Dashboard
```bash
python3 -m http.server 8080
# Open http://localhost:8080/dashboard.html in your browser
```
