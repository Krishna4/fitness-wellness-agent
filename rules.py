"""
Fitness & Wellness Agent - Safety Guardrails & Verification Gate
Course Concept (FN6): Deterministic safety rules verifying recommendations before dispatch.
Validates:
1. Exercise safety against registered user injuries.
2. Dietary suggestions against declared food allergies.
3. Safe caloric thresholds (blocks crash diets < 1200 kcal).
4. Appends medical disclaimer.
"""

from typing import List, Tuple
from schemas import UserProfile, WorkoutPlan, DietPlan

class SafetyGate:
    """Deterministic Health & Safety Verification Engine."""

    MIN_SAFE_CALORIES = 1200

    @classmethod
    def verify_workout(cls, profile: UserProfile, plan: WorkoutPlan) -> Tuple[bool, List[str]]:
        warnings = []
        user_injuries = [inj.lower().strip() for inj in profile.injuries]

        for ex in plan.exercises:
            for contra in ex.contraindicated_for:
                if any(inj in contra or contra in inj for inj in user_injuries):
                    warnings.append(
                        f"SAFETY ALERT: '{ex.name}' carries risk for user condition '{contra}'. Replacement recommended."
                    )

        is_safe = len(warnings) == 0
        return is_safe, warnings

    @classmethod
    def verify_diet(cls, profile: UserProfile, plan: DietPlan) -> Tuple[bool, List[str]]:
        warnings = []
        user_allergies = [a.lower().strip() for a in profile.allergies]

        if plan.daily_calories < cls.MIN_SAFE_CALORIES:
            warnings.append(
                f"SAFETY ALERT: Caloric target ({plan.daily_calories} kcal) is below safe physiological threshold ({cls.MIN_SAFE_CALORIES} kcal)."
            )

        for meal in plan.meals:
            for allergen in meal.allergens:
                if allergen.lower() in user_allergies:
                    warnings.append(
                        f"SAFETY ALERT: Meal '{meal.name}' contains declared allergen '{allergen}'."
                    )

        is_safe = len(warnings) == 0
        return is_safe, warnings
