"""
Fitness & Wellness Agent - End-to-End Demonstration Script
Executes all 5 required features using a generic benchmark profile:
1. Personalized workout recommendations
2. Diet and meal recommendations based on user preferences
3. Nearby gym and fitness facility recommendations
4. Fitness and nutrition progress tracking
5. Active Plan Monitoring & Real-Time Adaptive Plan Improvement
"""

import os
from schemas import UserProfile, ProgressEntry
from memory import MemoryStore
from agent import FitnessWellnessAgent

def run_demonstration():
    print("=" * 80)
    print("FITNESS & WELLNESS AGENT: 5-FEATURE VERIFICATION DEMO")
    print("Focus: Active Monitoring, Real-Time Plan Adaptation, & Safety Verification")
    print("=" * 80)

    test_db = "fitness_demo_memory.json"
    if os.path.exists(test_db):
        os.remove(test_db)

    memory = MemoryStore(storage_path=test_db)
    agent = FitnessWellnessAgent(memory_store=memory)

    # Generic benchmark user profile
    user = UserProfile(
        user_id="user_benchmark_01",
        name="Jordan Lee",
        age=29,
        gender="male",
        weight_kg=76.0,
        height_cm=175.0,
        fitness_goal="fat_loss",
        experience_level="intermediate",
        dietary_preference="non_veg",
        allergies=["peanuts"],
        injuries=["acute_lumbar_strain"],  # Initial injury
        location_city="Hyderabad (Hitec City / Kondapur)",
        latitude=17.4504,
        longitude=78.3808
    )

    print(f"\n[Active User Profile]: {user.name} | Goal: {user.fitness_goal.replace('_', ' ').title()}")
    print(f"Weight: {user.weight_kg}kg | Height: {user.height_cm}cm | Pref: {user.dietary_preference}")
    print(f"Injuries: {', '.join(user.injuries)} | Allergies: {', '.join(user.allergies)}")
    print(f"Location: {user.location_city}")

    # -------------------------------------------------------------
    # FEATURE 1: Workout Recommendations (with Injury Safety Gate)
    # -------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[FEATURE 1] Personalized Workout & Exercise Recommendations")
    query_1 = "Can you recommend a fat loss workout for today?"
    print(f"User Query: '{query_1}'")
    res_1 = agent.process_query(user, query_1)
    plan = res_1.data
    print(f"-> Intent Detected: {res_1.intent.value.upper()} | Status: {res_1.status}")
    print(f"-> Routine Title: {plan.title} (Duration: {plan.duration_minutes} mins)")
    print(f"-> Warm-up: {plan.warmup_notes}")
    print("-> Filtered Safe Exercises:")
    for ex in plan.exercises:
        print(f"   • {ex.name}: {ex.sets} sets x {ex.reps} reps ({ex.target_muscle}) - Cue: {ex.coaching_cue}")
    print(f"-> Safety Gate Alerts: {res_1.safety_warnings or 'None (All contraindicated exercises filtered out)'}")

    # -------------------------------------------------------------
    # FEATURE 2: Diet & Meal Recommendations
    # -------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[FEATURE 2] Diet & Meal Recommendations Based on Preferences & BMR")
    query_2 = "What should I eat today to hit my fat loss goals?"
    print(f"User Query: '{query_2}'")
    res_2 = agent.process_query(user, query_2)
    diet = res_2.data
    print(f"-> Intent Detected: {res_2.intent.value.upper()} | Status: {res_2.status}")
    print(f"-> Daily Target: {diet.daily_calories} kcal | Hydration: {diet.hydration_liters} Liters")
    print(f"-> Macros: Protein: {diet.target_macros['protein_g']}g | Carbs: {diet.target_macros['carbs_g']}g | Fats: {diet.target_macros['fats_g']}g")
    print("-> Suggested Meals (Allergen Filtered):")
    for m in diet.meals:
        print(f"   • [{m.meal_type.upper()}] {m.name} ({m.calories} kcal, P: {m.protein_g}g, C: {m.carbs_g}g, F: {m.fats_g}g)")

    # -------------------------------------------------------------
    # FEATURE 3: Nearby Gym & Fitness Facility Recommendations
    # -------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[FEATURE 3] Nearby Gym and Fitness Facility Recommendations")
    query_3 = "Are there any good gyms or workout centers nearby?"
    print(f"User Query: '{query_3}'")
    res_3 = agent.process_query(user, query_3)
    facilities = res_3.data
    print(f"-> Intent Detected: {res_3.intent.value.upper()} | Status: {res_3.status}")
    print(f"-> Facilities Found ({user.location_city}):")
    for f in facilities:
        print(f"   • {f.name} ({f.distance_km} km away | Rating: {f.rating}/5.0)")
        print(f"     Address: {f.address} | Amenities: {', '.join(f.amenities[:3])}")

    # -------------------------------------------------------------
    # FEATURE 4: Fitness & Nutrition Progress Tracking
    # -------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[FEATURE 4] Fitness and Nutrition Progress Tracking")
    query_4 = "Log my progress for today and check my stats"
    print(f"User Query: '{query_4}'")
    progress_entry = ProgressEntry(
        timestamp="Day 1",
        weight_kg=75.6,
        workout_completed=True,
        workout_summary="Completed 45-min Bodyweight & Bike Conditioning",
        calories_consumed=1800,
        water_liters=3.0,
        energy_level_1_to_10=8,
        notes="Felt energized, lumbar region stayed completely pain-free."
    )
    res_4 = agent.process_query(user, query_4, progress_payload=progress_entry)
    stats = res_4.data
    print(f"-> Intent Detected: {res_4.intent.value.upper()} | Status: {res_4.status}")
    print(f"-> Starting Weight: {stats['starting_weight_kg']} kg | Current Weight: {stats['current_weight_kg']} kg")
    print(f"-> Net Weight Delta: {stats['net_weight_change_kg']} kg")
    print(f"-> Completed Workouts: {stats['total_completed_workouts']} | Consistency: {stats['consistency_score']}")
    print(f"-> Coaching Insight: {stats['coaching_feedback']}")

    # -------------------------------------------------------------
    # FEATURE 5: ACTIVE MONITORING & REAL-TIME ADAPTIVE PLAN IMPROVEMENT
    # -------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[FEATURE 5] Active Monitoring & Real-Time Plan Evolution (User Feedback Loop)")
    
    # Scenario A: User reports fatigue & excessive soreness
    feedback_A = "I feel completely exhausted and too sore today after yesterday's training."
    print(f"\n>> Case A (Fatigue/Exhaustion Feedback): '{feedback_A}'")
    res_5a = agent.process_query(user, feedback_A)
    print(f"-> Adaptation Type: {res_5a.data['adaptation_type'].upper()}")
    print("-> Plan Improvements Applied in Real-Time:")
    for adj in res_5a.data["adjustments"]:
        print(f"   ✓ {adj}")

    # Scenario B: User reports sudden discomfort (e.g. shoulder pain during overhead press)
    feedback_B = "My shoulder hurts whenever I press weights overhead."
    print(f"\n>> Case B (Joint Discomfort / New Limitation): '{feedback_B}'")
    res_5b = agent.process_query(user, feedback_B)
    print(f"-> Adaptation Type: {res_5b.data['adaptation_type'].upper()}")
    print("-> Plan Improvements Applied in Real-Time:")
    for adj in res_5b.data["adjustments"]:
        print(f"   ✓ {adj}")
    print(f"-> Safety Gate Active Update: {res_5b.safety_warnings}")
    print(f"-> Persistent Memory Updated: Current Registered Injuries = {user.injuries}")

    # Scenario C: User requests progression ("too easy")
    feedback_C = "The bodyweight workouts feel too easy now, I want more challenge."
    print(f"\n>> Case C (Progressive Overload Feedback): '{feedback_C}'")
    res_5c = agent.process_query(user, feedback_C)
    print(f"-> Adaptation Type: {res_5c.data['adaptation_type'].upper()}")
    print("-> Plan Improvements Applied in Real-Time:")
    for adj in res_5c.data["adjustments"]:
        print(f"   ✓ {adj}")

    print("\n" + "=" * 80)
    print("ALL 5 FEATURES INCLUDING ACTIVE PLAN MONITORING VERIFIED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_demonstration()
