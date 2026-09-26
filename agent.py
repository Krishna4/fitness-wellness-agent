"""
Fitness & Wellness Agent - Core Agent Orchestrator
Course Concepts Applied:
- ReAct / Decision-Action cycle
- Grounded Tool Execution (pure Python, zero-framework overhead)
- Dual-Layer Memory Integration
- Deterministic Safety Verification Gate
- Active Plan Monitoring & Feedback Adaptation Loop
- LLM Integration: Google Gemini (gemini-flash-lite-latest) & Local Ollama
"""

from typing import Optional, Dict, Any, List
from schemas import (
    UserProfile, IntentType, AgentResult, ProgressEntry
)
from memory import MemoryStore
from triage import IntentTriage
from tools import FitnessTools
from rules import SafetyGate
from llm_client import LLMClient

class FitnessWellnessAgent:
    """The central agent coordinating user input, tools, memory, safety, and adaptive LLM coaching."""

    def __init__(self, memory_store: Optional[MemoryStore] = None, llm_provider: Optional[str] = None):
        self.memory = memory_store or MemoryStore()
        self.llm = LLMClient(provider=llm_provider)

    def process_query(self, user_profile: UserProfile, query: str, progress_payload: Optional[ProgressEntry] = None) -> AgentResult:
        """Execute the 5-phase agentic workflow."""
        # Phase 1: Hydrate Memory & Profile
        profile = self.memory.get_or_create_user(user_profile)
        self.memory.record_turn("user", query)

        # Phase 2: Deterministic Intent Triage
        intent = IntentTriage.classify(query)

        warnings: List[str] = []
        result_data: Any = None
        guidance: str = ""

        # Phase 3: Tool Execution (ReAct Decision)
        if intent == IntentType.WORKOUT:
            plan = FitnessTools.recommend_workouts(profile)
            # Phase 4: Safety Verification Gate
            is_safe, safety_warnings = SafetyGate.verify_workout(profile, plan)
            warnings.extend(safety_warnings)
            result_data = plan

            # LLM-enhanced coaching explanation
            ex_names = ", ".join(e.name for e in plan.exercises)
            prompt = (
                f"User: {profile.name} (Goal: {profile.fitness_goal}, Limitations: {profile.injuries or 'None'}). "
                f"Generated Workout: {plan.title} ({plan.duration_minutes} mins). "
                f"Selected safe exercises: {ex_names}. "
                f"Provide a brief 2-sentence motivating coaching briefing explaining why this routine fits their goal."
            )
            llm_text = self.llm.generate(
                prompt,
                system_instruction="You are FitPulse, an expert exercise physiologist. Keep responses concise, direct, and actionable. Do not hallucinate exercises not provided in the list."
            )
            guidance = llm_text if "Offline" not in llm_text else f"Here is your personalized {plan.title} ({plan.duration_minutes} mins) tailored to your goal."

        elif intent == IntentType.DIET:
            plan = FitnessTools.recommend_diet(profile)
            is_safe, safety_warnings = SafetyGate.verify_diet(profile, plan)
            warnings.extend(safety_warnings)
            result_data = plan

            prompt = (
                f"User: {profile.name} (Goal: {profile.fitness_goal}, Diet: {profile.dietary_preference}). "
                f"Caloric Target: {plan.daily_calories} kcal/day (Protein: {plan.target_macros['protein_g']}g, Carbs: {plan.target_macros['carbs_g']}g, Fats: {plan.target_macros['fats_g']}g). "
                f"Hydration: {plan.hydration_liters}L. "
                f"Provide a brief 2-sentence nutritional coaching tip focused on hitting their protein and hydration targets."
            )
            llm_text = self.llm.generate(
                prompt,
                system_instruction="You are FitPulse, a sports nutritionist. Be encouraging, concise, and scientifically grounded."
            )
            guidance = (
                f"Nutritional Plan ({plan.daily_calories} kcal | Protein: {plan.target_macros['protein_g']}g | Hydration: {plan.hydration_liters}L):\n"
                f"{llm_text}"
            )

        elif intent == IntentType.FACILITY:
            facilities = FitnessTools.search_nearby_facilities(
                location_city=profile.location_city,
                max_distance_km=5.0
            )
            result_data = facilities
            guidance = f"Located {len(facilities)} verified fitness and wellness facilities near {profile.location_city} within 5 km."

        elif intent == IntentType.PROGRESS:
            history = self.memory.get_progress_history(profile.user_id)
            entry = progress_payload or ProgressEntry(
                timestamp="Today",
                weight_kg=profile.weight_kg,
                workout_completed=True,
                workout_summary="Completed recommended routine",
                calories_consumed=1850,
                water_liters=2.8,
                energy_level_1_to_10=8,
                notes="Felt energized and strong."
            )
            self.memory.append_progress(profile.user_id, entry)
            stats = FitnessTools.track_progress(profile, history, entry)
            result_data = stats
            guidance = f"Progress updated successfully! Current consistency score: {stats['consistency_score']} ({stats.get('total_completed_workouts', 1)} completed sessions)."

        else:  # WELLNESS / ADAPTIVE PLAN MONITORING (Feature 5)
            # Actively monitor user input for fatigue, pain, feedback, or difficulty
            adaptation = FitnessTools.adapt_and_improve_plan(query, profile)
            
            # If a new physical limitation/injury was reported, update memory store automatically
            if adaptation.get("new_injuries"):
                for inj in adaptation["new_injuries"]:
                    if inj not in profile.injuries:
                        profile.injuries.append(inj)
                self.memory.update_profile(profile)
                warnings.append(f"SAFETY ADAPTATION: Registered new limitation '{', '.join(adaptation['new_injuries'])}' in persistent memory.")

            # LLM synthesis for empathetic, adaptive response
            adjustments_str = "; ".join(adaptation["adjustments"])
            prompt = (
                f"User Feedback: '{query}'. "
                f"User Profile: {profile.name} (Goal: {profile.fitness_goal}, Current injuries: {profile.injuries}). "
                f"Adaptation Type: {adaptation['adaptation_type']}. "
                f"Applied Adjustments: {adjustments_str}. "
                f"Synthesize an articulate, empathetic, and professional coaching response explaining the adaptations."
            )
            llm_text = self.llm.generate(
                prompt,
                system_instruction="You are an elite, empathetic wellness coach. Explain the plan adjustments clearly. Emphasize active recovery, joint safety, and sustainable consistency."
            )
            
            result_data = adaptation
            guidance = f"{llm_text}\n\n[Active Plan Adjustments]:\n" + "\n".join(f"  • {adj}" for adj in adaptation["adjustments"])

        # Phase 5: Response Dispatch & Ephemeral Turn Logging
        self.memory.record_turn("agent", guidance)

        return AgentResult(
            intent=intent,
            status="VERIFIED_SUCCESS" if not warnings else "VERIFIED_WITH_SAFETY_ADAPTATION",
            data=result_data,
            guidance=guidance,
            safety_warnings=warnings
        )
