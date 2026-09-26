"""
Fitness & Wellness Agent - Deterministic Intent Triage
Course Concept (FN6): Zero-token deterministic pre-routing to classify incoming queries
into domain actions without burning LLM tokens on classification overhead.
"""

from schemas import IntentType

class IntentTriage:
    """Deterministic Rule-based Intent Classifier."""

    ADAPTATION_KEYWORDS = [
        "sore", "exhausted", "tired", "burned out", "low energy", "fatigued",
        "hurts", "pain", "clicking", "tight", "too easy", "breeze", "harder",
        "more challenge", "plateau", "stuck", "recovery", "deload", "motivation"
    ]
    WORKOUT_KEYWORDS = ["workout", "exercise", "routine", "reps", "sets", "gym routine", "chest", "leg", "arm", "squat", "pushup", "cardio", "train "]
    DIET_KEYWORDS = ["diet", "meal", "food", "nutrition", "calorie", "calories", "protein", "carbs", "macro", "macros", "eat", "breakfast", "lunch", "dinner", "recipe"]
    FACILITY_KEYWORDS = ["nearby", "gym near", "facilities", "center", "studio", "crossfit", "park", "fitness center", "location", "where to train"]
    PROGRESS_KEYWORDS = ["progress", "track", "log", "weight lost", "weight gain", "metric", "history", "stats", "consistency", "weigh"]
    WELLNESS_KEYWORDS = ["habit", "water", "sleep", "guidance", "advice", "help", "coach", "wellness", "lifestyle"]

    @classmethod
    def classify(cls, query: str) -> IntentType:
        q = query.lower()

        # Check adaptation / feedback cues first
        if any(k in q for k in cls.ADAPTATION_KEYWORDS):
            return IntentType.WELLNESS
        if any(k in q for k in cls.PROGRESS_KEYWORDS):
            return IntentType.PROGRESS
        if any(k in q for k in cls.FACILITY_KEYWORDS):
            return IntentType.FACILITY
        if any(k in q for k in cls.DIET_KEYWORDS):
            return IntentType.DIET
        if any(k in q for k in cls.WORKOUT_KEYWORDS):
            return IntentType.WORKOUT
        if any(k in q for k in cls.WELLNESS_KEYWORDS):
            return IntentType.WELLNESS

        return IntentType.WELLNESS
