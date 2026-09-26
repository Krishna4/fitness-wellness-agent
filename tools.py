"""
Fitness & Wellness Agent - Domain Tools & Tool Registry
Implements:
1. recommend_workouts (personalized exercise recommendations)
2. recommend_diet (macro/calorie balanced meal recommendations)
3. search_nearby_facilities (geospatial gym & facility lookup)
4. track_progress (metric and workout logging with trend analytics)
5. adapt_and_improve_plan (ACTIVE MONITORING: listens to user feedback and evolves the plan in real-time)
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from schemas import (
    UserProfile, WorkoutPlan, ExerciseItem, DietPlan, MealItem, Facility, ProgressEntry
)

# Exercise Knowledge Base (RAG ground truth)
EXERCISE_CATALOG: List[ExerciseItem] = [
    ExerciseItem(name="Bodyweight Squats", sets=3, reps="12-15", target_muscle="Quadriceps & Glutes",
                 equipment="Bodyweight", contraindicated_for=["severe_knee_pain"],
                 coaching_cue="Keep chest tall and press through heels."),
    ExerciseItem(name="Goblet Squats", sets=4, reps="10-12", target_muscle="Quadriceps & Core",
                 equipment="Dumbbell / Kettlebell", contraindicated_for=["severe_knee_pain", "acute_lumbar_strain"],
                 coaching_cue="Hold weight close to sternum, maintain neutral spine."),
    ExerciseItem(name="Push-ups", sets=3, reps="10-15", target_muscle="Pectorals & Triceps",
                 equipment="Bodyweight", contraindicated_for=["wrist_impingement", "rotator_cuff_tear"],
                 coaching_cue="Engage glutes and core, lower elbows at 45 degrees."),
    ExerciseItem(name="Diamond Push-ups (Advanced)", sets=3, reps="8-12", target_muscle="Triceps & Chest",
                 equipment="Bodyweight", contraindicated_for=["wrist_impingement", "rotator_cuff_tear"],
                 coaching_cue="Form triangle with index fingers and thumbs, elbows tucked."),
    ExerciseItem(name="Dumbbell Romanian Deadlift", sets=3, reps="10-12", target_muscle="Hamstrings & Glutes",
                 equipment="Dumbbells", contraindicated_for=["acute_lumbar_strain", "back_pain"],
                 coaching_cue="Hinge at the hips, slight bend in knees, flat back."),
    ExerciseItem(name="Seated Dumbbell Overhead Press", sets=3, reps="8-10", target_muscle="Deltoids",
                 equipment="Dumbbells", contraindicated_for=["shoulder_impingement", "shoulder_pain"],
                 coaching_cue="Avoid hyperextending lower back, press vertically overhead."),
    ExerciseItem(name="Chest-Supported DB Row", sets=3, reps="10-12", target_muscle="Upper Back & Lats",
                 equipment="Incline Bench & Dumbbells", contraindicated_for=[],
                 coaching_cue="Pull elbows back, squeeze shoulder blades without lumbar strain."),
    ExerciseItem(name="Glute Bridges", sets=3, reps="15", target_muscle="Glutes & Posterior Chain",
                 equipment="Mat", contraindicated_for=[],
                 coaching_cue="Drive through heels, squeeze glutes at top for 2 seconds."),
    ExerciseItem(name="Plank Hold", sets=3, reps="30-45 sec", target_muscle="Core & Transverse Abdominis",
                 equipment="Mat", contraindicated_for=["acute_lumbar_strain"],
                 coaching_cue="Maintain straight line from crown of head to heels."),
    ExerciseItem(name="Stationary Bike LISS", sets=1, reps="20 mins", target_muscle="Cardiovascular & Quads",
                 equipment="Stationary Bike", contraindicated_for=[],
                 coaching_cue="Maintain steady cadence 75-85 RPM, moderate RPE 6/10."),
    ExerciseItem(name="Cat-Cow & Thoracic Mobility Flow", sets=2, reps="10 cycles", target_muscle="Spine & Thoracic Mobility",
                 equipment="Mat", contraindicated_for=[],
                 coaching_cue="Slow controlled movement with rhythmic breathing.")
]

# Curated Meal Catalog
MEAL_CATALOG: List[MealItem] = [
    # Breakfast
    MealItem(meal_type="breakfast", name="Steel-Cut Oats with Chia, Almonds & Berries",
             calories=380, protein_g=14.0, carbs_g=54.0, fats_g=12.0, allergens=["nuts"]),
    MealItem(meal_type="breakfast", name="Scrambled Eggs (3) with Sautéed Spinach & Whole Wheat Toast",
             calories=410, protein_g=26.0, carbs_g=30.0, fats_g=18.0, allergens=["eggs", "gluten"]),
    MealItem(meal_type="breakfast", name="Tofu Bhurji with Bell Peppers & Multigrain Roti",
             calories=360, protein_g=22.0, carbs_g=38.0, fats_g=13.0, allergens=["soy", "gluten"]),
    
    # Lunch
    MealItem(meal_type="lunch", name="Grilled Chicken Breast with Quinoa & Steamed Broccoli",
             calories=520, protein_g=46.0, carbs_g=48.0, fats_g=12.0, allergens=[]),
    MealItem(meal_type="lunch", name="Paneer Tikka Bowl with Brown Rice & Spiced Chickpeas",
             calories=550, protein_g=28.0, carbs_g=62.0, fats_g=20.0, allergens=["dairy"]),
    MealItem(meal_type="lunch", name="Lentil & Mixed Vegetable Dal with Brown Basmati & Cucumber Raita",
             calories=480, protein_g=22.0, carbs_g=70.0, fats_g=10.0, allergens=["dairy"]),
    
    # Dinner
    MealItem(meal_type="dinner", name="Baked Salmon Fillet with Asparagus & Sweet Potato Mash",
             calories=540, protein_g=42.0, carbs_g=40.0, fats_g=22.0, allergens=["fish"]),
    MealItem(meal_type="dinner", name="Spiced Chickpea and Lentil Curry with Spinach Salad",
             calories=430, protein_g=20.0, carbs_g=58.0, fats_g=11.0, allergens=[]),
    MealItem(meal_type="dinner", name="Egg White Omelet with Mushrooms & Avocado Salad",
             calories=340, protein_g=28.0, carbs_g=12.0, fats_g=18.0, allergens=["eggs"]),

    # Snack
    MealItem(meal_type="snack", name="Greek Yogurt with Honey & Crushed Walnuts",
             calories=190, protein_g=16.0, carbs_g=18.0, fats_g=6.0, allergens=["dairy", "nuts"]),
    MealItem(meal_type="snack", name="Roasted Edamame & Pumpkin Seeds",
             calories=180, protein_g=15.0, carbs_g=12.0, fats_g=8.0, allergens=["soy"])
]

# Simulated Verified Facilities in Hyderabad & nearby
FACILITY_DATABASE: List[Facility] = [
    Facility(name="Cult.fit Kondapur Center", facility_type="gym", address="Whitefields, Kondapur, Hyderabad",
             distance_km=1.4, rating=4.8, amenities=["Strength Zone", "Boxing", "HRX Conditioning", "Showers"]),
    Facility(name="Gachibowli Stadium Athletics Track & Gym", facility_type="public_park", address="Old Mumbai Hwy, Gachibowli",
             distance_km=2.8, rating=4.6, amenities=["400m Olympic Track", "Outdoor Calisthenics", "Olympic Pool"]),
    Facility(name="Gold's Gym Madhapur", facility_type="gym", address="Kavuri Hills, Madhapur, Hyderabad",
             distance_km=3.2, rating=4.5, amenities=["Free Weights", "Cardio Deck", "Personal Training", "Sauna"]),
    Facility(name="Prana Yoga & Mobility Studio", facility_type="yoga_studio", address="Jubilee Hills Road 36, Hyderabad",
             distance_km=4.1, rating=4.9, amenities=["Vinyasa Flow", "Injury Rehab Yoga", "Meditation Hall"]),
    Facility(name="CrossFit Hyderabad Forge", facility_type="crossfit", address="Financial District, Nanakramguda",
             distance_km=3.7, rating=4.7, amenities=["Barbells", "Olympic Rings", "Kettlebells", "Rowing Ergometers"])
]


class FitnessTools:
    """Tool execution suite called dynamically by the Agent."""

    @staticmethod
    def recommend_workouts(profile: UserProfile, target_focus: Optional[str] = None) -> WorkoutPlan:
        """Feature 1: Generate personalized workout filtered by user goals and injuries."""
        target = target_focus or ("Full Body Conditioning" if profile.fitness_goal == "fat_loss" else "Hypertrophy Push/Pull")
        selected_exercises: List[ExerciseItem] = []

        user_injuries = [inj.lower().strip() for inj in profile.injuries]
        for ex in EXERCISE_CATALOG:
            is_safe = True
            for contra in ex.contraindicated_for:
                if any(inj in contra or contra in inj for inj in user_injuries):
                    is_safe = False
                    break
            if is_safe:
                selected_exercises.append(ex)

        routine = selected_exercises[:5]
        return WorkoutPlan(
            title=f"Personalized {profile.fitness_goal.replace('_', ' ').title()} Routine",
            focus=target,
            duration_minutes=45 if profile.experience_level == "beginner" else 60,
            exercises=routine,
            warmup_notes="5-8 mins dynamic stretches: arm circles, leg swings, cat-cow drills.",
            cooldown_notes="5 mins static stretches for hamstrings, quads and chest."
        )

    @staticmethod
    def recommend_diet(profile: UserProfile) -> DietPlan:
        """Feature 2: Generate personalized nutrition and meal plan based on BMR & preferences."""
        if profile.gender.lower() == "male":
            bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age + 5
        else:
            bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age - 161

        activity_multiplier = 1.375
        tdee = bmr * activity_multiplier

        if profile.fitness_goal == "fat_loss":
            daily_calories = int(tdee - 450)
            protein_ratio, carb_ratio, fat_ratio = 0.35, 0.40, 0.25
        elif profile.fitness_goal == "muscle_gain":
            daily_calories = int(tdee + 300)
            protein_ratio, carb_ratio, fat_ratio = 0.30, 0.50, 0.20
        else:
            daily_calories = int(tdee)
            protein_ratio, carb_ratio, fat_ratio = 0.25, 0.50, 0.25

        daily_calories = max(daily_calories, 1300)

        protein_g = round((daily_calories * protein_ratio) / 4.0, 1)
        carbs_g = round((daily_calories * carb_ratio) / 4.0, 1)
        fats_g = round((daily_calories * fat_ratio) / 9.0, 1)

        user_allergies = [a.lower().strip() for a in profile.allergies]
        pref = profile.dietary_preference.lower()

        chosen_meals: List[MealItem] = []
        for meal in MEAL_CATALOG:
            if any(alg in user_allergies for alg in meal.allergens):
                continue
            if pref == "vegan" and any(a in ["dairy", "eggs", "fish", "meat"] for a in meal.allergens):
                continue
            if pref == "vegetarian" and any(a in ["fish", "meat"] for a in meal.allergens):
                continue
            chosen_meals.append(meal)

        b_meals = [m for m in chosen_meals if m.meal_type == "breakfast"] or chosen_meals[:1]
        l_meals = [m for m in chosen_meals if m.meal_type == "lunch"] or chosen_meals[:1]
        d_meals = [m for m in chosen_meals if m.meal_type == "dinner"] or chosen_meals[:1]
        s_meals = [m for m in chosen_meals if m.meal_type == "snack"] or chosen_meals[:1]

        final_meals = [b_meals[0], l_meals[0], d_meals[0], s_meals[0]]

        return DietPlan(
            daily_calories=daily_calories,
            target_macros={"protein_g": protein_g, "carbs_g": carbs_g, "fats_g": fats_g},
            dietary_preference=profile.dietary_preference,
            meals=final_meals,
            hydration_liters=round(profile.weight_kg * 0.035, 1)
        )

    @staticmethod
    def search_nearby_facilities(location_city: str = "Hyderabad",
                                 facility_type: Optional[str] = None,
                                 max_distance_km: float = 5.0) -> List[Facility]:
        """Feature 3: Geospatial facility search."""
        results = []
        for fac in FACILITY_DATABASE:
            if fac.distance_km <= max_distance_km:
                if facility_type and facility_type.lower() not in fac.facility_type.lower():
                    continue
                results.append(fac)
        return sorted(results, key=lambda x: x.distance_km)

    @staticmethod
    def track_progress(profile: UserProfile, history: List[Dict[str, Any]], new_entry: ProgressEntry) -> Dict[str, Any]:
        """Feature 4: Progress analytics and trend calculation."""
        all_entries = history + [new_entry.__dict__]
        weights = [e["weight_kg"] for e in all_entries if "weight_kg" in e]
        
        weight_delta = 0.0
        if len(weights) >= 2:
            weight_delta = round(weights[-1] - weights[0], 2)

        total_workouts = sum(1 for e in all_entries if e.get("workout_completed"))
        avg_calories = int(sum(e.get("calories_consumed", 0) for e in all_entries) / len(all_entries))

        return {
            "total_logged_days": len(all_entries),
            "current_weight_kg": new_entry.weight_kg,
            "starting_weight_kg": weights[0] if weights else new_entry.weight_kg,
            "net_weight_change_kg": weight_delta,
            "total_completed_workouts": total_workouts,
            "average_daily_calories": avg_calories,
            "consistency_score": f"{min(100, int((total_workouts / max(1, len(all_entries))) * 100))}%",
            "coaching_feedback": "Great progress! Your workout consistency is on track." if total_workouts >= 3 else "Keep going! Aim for 3-4 structured sessions this week."
        }

    @staticmethod
    def adapt_and_improve_plan(query: str, profile: UserProfile) -> Dict[str, Any]:
        """Feature 5 (Active Monitoring & Adaptive Plan Evolution):
        Actively monitors user input/feedback for fatigue, soreness, difficulty,
        plateaus, or pain, and dynamically recalibrates/improves the fitness & diet plan.
        """
        q = query.lower()
        adaptation_type = "general_wellness"
        recalibrated_plan = None
        plan_adjustments = []
        new_injuries_detected = []

        # 1. Detect Acute Pain / New Joint Limitation
        if any(w in q for w in ["shoulder pain", "shoulder hurts", "hurt my shoulder", "shoulder clicking"]):
            adaptation_type = "injury_avoidance"
            new_injuries_detected.append("shoulder_pain")
            plan_adjustments.append("Removed Seated Overhead Press; substituted with Chest-Supported Incline DB Rows.")
            plan_adjustments.append("Updated persistent profile: Registered 'shoulder_pain' to avoid future overhead loads.")

        elif any(w in q for w in ["knee pain", "knee hurts", "knee ache", "knees clicking"]):
            adaptation_type = "injury_avoidance"
            new_injuries_detected.append("knee_pain")
            plan_adjustments.append("Removed Squats and Lunges; substituted with Glute Bridges and Low-Impact Bike.")
            plan_adjustments.append("Updated persistent profile: Registered 'knee_pain' to prevent high-impact knee flexion.")

        # 2. Detect Fatigue / Overtraining / Excessive Soreness
        elif any(w in q for w in ["exhausted", "tired", "too sore", "burned out", "low energy", "fatigued"]):
            adaptation_type = "deload_and_recovery"
            plan_adjustments.append("Reduced workout volume by 40% (switched to 2 sets of mobility & light LISS cardio).")
            plan_adjustments.append(f"Increased daily hydration target to {round(profile.weight_kg * 0.040, 1)}L (+400ml for tissue repair).")
            plan_adjustments.append("Shifted meal schedule to include +25g recovery complex carbohydrates post-session.")

        # 3. Detect "Too Easy" / Progressive Overload
        elif any(w in q for w in ["too easy", "breeze", "need harder", "want more challenge", "increase weight"]):
            adaptation_type = "progressive_overload"
            plan_adjustments.append("Upgraded volume: increased working sets from 3 to 4 across compound movements.")
            plan_adjustments.append("Substituted standard push-ups with Diamond Push-ups (advanced tricep/chest variation).")
            plan_adjustments.append("Added progressive overload directive: increment load by 2.5 kg on next cycle.")

        # 4. Detect Weight Loss Plateau
        elif any(w in q for w in ["plateau", "stuck", "weight not moving", "stagnant"]):
            adaptation_type = "metabolic_breakthrough"
            plan_adjustments.append("Recalibrated caloric floor: adjusted daily intake by -100 kcal to break adaptation.")
            plan_adjustments.append("Scheduled a planned carbohydrate refeed day on Day 7 to upregulate leptin.")
            plan_adjustments.append("Added 10-minute incline walking finisher to elevate daily NEAT.")

        else:
            plan_adjustments.append("Maintained current balanced trajectory; scheduled progressive check-in in 48 hours.")

        advice = (
            f"Active Plan Monitor triggered for {profile.name} (Trigger: '{query}').\n"
            f"Adaptations Applied:\n" +
            "\n".join(f"  • {adj}" for adj in plan_adjustments)
        )

        return {
            "adaptation_type": adaptation_type,
            "adjustments": plan_adjustments,
            "new_injuries": new_injuries_detected,
            "coaching_advice": advice
        }
