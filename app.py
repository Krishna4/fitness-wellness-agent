"""
Fitness & Wellness Agent - Interactive CLI & Runner
Dynamically asks the user for their profile details instead of hardcoding any data.
"""

import sys
import os
from typing import Optional
from schemas import UserProfile, ProgressEntry
from memory import MemoryStore
from agent import FitnessWellnessAgent

def prompt_user_profile(memory: MemoryStore) -> UserProfile:
    """Interactively collect user details for customized fitness planning."""
    print("\n" + "=" * 75)
    print("  WELCOME! LET'S SET UP YOUR PERSONAL FITNESS & WELLNESS PROFILE")
    print("=" * 75)
    print("Please enter your details below (press Enter to accept default suggestions):\n")

    name = input("1. Your Name [Guest]: ").strip() or "Guest"
    
    age_str = input("2. Age [28]: ").strip() or "28"
    try:
        age = int(age_str)
    except ValueError:
        age = 28

    gender = input("3. Gender (male / female / other) [male]: ").strip().lower() or "male"
    
    weight_str = input("4. Current Weight in kg [72.0]: ").strip() or "72.0"
    try:
        weight_kg = float(weight_str)
    except ValueError:
        weight_kg = 72.0

    height_str = input("5. Height in cm [175.0]: ").strip() or "175.0"
    try:
        height_cm = float(height_str)
    except ValueError:
        height_cm = 175.0

    print("\nFitness Goals: (1) fat_loss  (2) muscle_gain  (3) endurance  (4) mobility")
    goal_choice = input("6. Primary Goal [fat_loss]: ").strip().lower() or "fat_loss"
    goal_map = {"1": "fat_loss", "2": "muscle_gain", "3": "endurance", "4": "mobility"}
    fitness_goal = goal_map.get(goal_choice, goal_choice)

    print("\nDietary Preferences: (1) non_veg  (2) vegetarian  (3) vegan  (4) eggetarian")
    diet_choice = input("7. Dietary Preference [non_veg]: ").strip().lower() or "non_veg"
    diet_map = {"1": "non_veg", "2": "vegetarian", "3": "vegan", "4": "eggetarian"}
    dietary_preference = diet_map.get(diet_choice, diet_choice)

    allergies_input = input("8. Any Food Allergies? (comma-separated, e.g. peanuts, dairy, or Enter for None): ").strip()
    allergies = [a.strip().lower() for a in allergies_input.split(",") if a.strip()] if allergies_input else []

    injuries_input = input("9. Any Injuries or joint limitations? (e.g. knee pain, acute lumbar strain, or Enter for None): ").strip()
    injuries = [i.strip().lower().replace(" ", "_") for i in injuries_input.split(",") if i.strip()] if injuries_input else []

    city = input("10. Your City / Area [Hyderabad]: ").strip() or "Hyderabad"

    user_id = f"user_{name.lower().replace(' ', '_')}"
    profile = UserProfile(
        user_id=user_id,
        name=name,
        age=age,
        gender=gender,
        weight_kg=weight_kg,
        height_cm=height_cm,
        fitness_goal=fitness_goal,
        experience_level="intermediate",
        dietary_preference=dietary_preference,
        allergies=allergies,
        injuries=injuries,
        location_city=city,
        latitude=17.3850,
        longitude=78.4867
    )

    memory.update_profile(profile)
    print("\n" + "=" * 75)
    print(f"  PROFILE CREATED SUCCESSFULLY FOR {name.upper()}!")
    print(f"  Goal: {fitness_goal.replace('_', ' ').title()} | Caloric baseline calculating...")
    if injuries:
        print(f"  Safety Gate: Filter active for injuries: {', '.join(injuries)}")
    if allergies:
        print(f"  Allergen Gate: Filter active for: {', '.join(allergies)}")
    print("=" * 75 + "\n")
    return profile


def run_interactive():
    print("=" * 75)
    print("  FITNESS & WELLNESS AGENT - INTERACTIVE ASSISTANT")
    print("=" * 75)

    memory = MemoryStore(storage_path="fitness_memory.json")
    agent = FitnessWellnessAgent(memory_store=memory)

    # Check if a user profile is already saved in memory
    users = memory.data.get("users", {})
    if users:
        first_uid = list(users.keys())[0]
        u = users[first_uid]
        user = UserProfile(
            user_id=u["user_id"],
            name=u["name"],
            age=u["age"],
            gender=u["gender"],
            weight_kg=u["weight_kg"],
            height_cm=u["height_cm"],
            fitness_goal=u["fitness_goal"],
            experience_level=u.get("experience_level", "intermediate"),
            dietary_preference=u["dietary_preference"],
            allergies=u.get("allergies", []),
            injuries=u.get("injuries", []),
            location_city=u.get("location_city", "Hyderabad"),
            latitude=u.get("latitude", 17.3850),
            longitude=u.get("longitude", 78.4867)
        )
        print(f"\nWelcome back, {user.name}!")
        change = input(f"Do you want to use existing profile '{user.name}' ({user.fitness_goal})? [Y/n]: ").strip().lower()
        if change in ['n', 'no']:
            user = prompt_user_profile(memory)
    else:
        user = prompt_user_profile(memory)

    print("\nYou can now ask the Fitness Agent anything:")
    print("  • 'Recommend a workout routine for today'")
    print("  • 'What should I eat today to hit my target calories?'")
    print("  • 'Find gyms and fitness centers near me'")
    print("  • 'Log my workout progress'")
    print("  • 'My legs feel very sore, how should I recover?'")
    print("Type 'exit' to quit, or 'profile' to edit details.\n")

    while True:
        try:
            query = input(f"[{user.name}] Ask Fitness Agent > ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                print(f"Exiting Fitness & Wellness Agent. Stay healthy, {user.name}!")
                break
            if query.lower() in ["profile", "edit"]:
                user = prompt_user_profile(memory)
                continue
            if query.lower() == "demo":
                from demo import run_demonstration
                run_demonstration()
                continue

            result = agent.process_query(user, query)
            print(f"\n[Intent Detected: {result.intent.value.upper()}] Status: {result.status}")
            print(f"\n[Coach Guidance]:\n{result.guidance}\n")

            if result.intent.value == "workout":
                plan = result.data
                print(f"Routine: {plan.title} (Duration: {plan.duration_minutes} mins)")
                print(f"Warm-up: {plan.warmup_notes}")
                print("Exercises:")
                for ex in plan.exercises:
                    print(f"  • {ex.name}: {ex.sets} sets x {ex.reps} ({ex.target_muscle})")
                    if ex.coaching_cue:
                        print(f"    Cue: {ex.coaching_cue}")
                print(f"Cool-down: {plan.cooldown_notes}")

            elif result.intent.value == "diet":
                diet = result.data
                print(f"Daily Target: {diet.daily_calories} kcal | Hydration: {diet.hydration_liters}L")
                print("Suggested Meals:")
                for m in diet.meals:
                    print(f"  • [{m.meal_type.upper()}] {m.name} ({m.calories} kcal | P: {m.protein_g}g, C: {m.carbs_g}g, F: {m.fats_g}g)")

            elif result.intent.value == "facility":
                facilities = result.data
                print(f"Nearby Facilities ({len(facilities)} found near {user.location_city}):")
                for f in facilities:
                    print(f"  • {f.name} ({f.distance_km} km | Rating: {f.rating}/5.0)")
                    print(f"    Address: {f.address} | Features: {', '.join(f.amenities[:3])}")

            elif result.intent.value == "progress":
                stats = result.data
                print(f"Progress Summary:")
                print(f"  • Logged Days: {stats.get('total_logged_days', 1)}")
                print(f"  • Weight: {stats.get('current_weight_kg')} kg (Delta: {stats.get('net_weight_change_kg', 0.0)} kg)")
                print(f"  • Completed Workouts: {stats.get('total_completed_workouts', 1)} | Consistency: {stats.get('consistency_score', '100%')}")
                print(f"  • Feedback: {stats.get('coaching_feedback')}")

            if result.safety_warnings:
                print(f"\n[Safety Warnings]: {', '.join(result.safety_warnings)}")
            print("-" * 75)

        except (KeyboardInterrupt, EOFError):
            print(f"\nGoodbye {user.name}! Keep crushing your fitness goals.")
            break

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        from demo import run_demonstration
        run_demonstration()
    else:
        if not sys.stdin.isatty():
            from demo import run_demonstration
            run_demonstration()
        else:
            run_interactive()
