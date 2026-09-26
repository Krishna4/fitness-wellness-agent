"""
Fitness & Wellness Agent - Schemas & Data Contracts
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

class IntentType(str, Enum):
    WORKOUT = "workout"
    DIET = "diet"
    FACILITY = "facility"
    PROGRESS = "progress"
    WELLNESS = "wellness"
    UNKNOWN = "unknown"

@dataclass
class UserProfile:
    user_id: str
    name: str
    age: int
    gender: str
    weight_kg: float
    height_cm: float
    fitness_goal: str  # fat_loss, muscle_gain, endurance, mobility
    experience_level: str  # beginner, intermediate, advanced
    dietary_preference: str  # vegan, vegetarian, eggetarian, non_veg, keto
    allergies: List[str] = field(default_factory=list)
    injuries: List[str] = field(default_factory=list)
    location_city: str = "Hyderabad"
    latitude: float = 17.3850
    longitude: float = 78.4867

@dataclass
class ExerciseItem:
    name: str
    sets: int
    reps: str
    target_muscle: str
    equipment: str
    contraindicated_for: List[str] = field(default_factory=list)
    coaching_cue: str = ""

@dataclass
class WorkoutPlan:
    title: str
    focus: str
    duration_minutes: int
    exercises: List[ExerciseItem]
    warmup_notes: str
    cooldown_notes: str

@dataclass
class MealItem:
    meal_type: str  # breakfast, lunch, dinner, snack
    name: str
    calories: int
    protein_g: float
    carbs_g: float
    fats_g: float
    allergens: List[str] = field(default_factory=list)

@dataclass
class DietPlan:
    daily_calories: int
    target_macros: Dict[str, float]  # protein_g, carbs_g, fats_g
    dietary_preference: str
    meals: List[MealItem]
    hydration_liters: float

@dataclass
class Facility:
    name: str
    facility_type: str  # gym, crossfit, yoga_studio, swimming_pool, public_park
    address: str
    distance_km: float
    rating: float
    amenities: List[str]

@dataclass
class ProgressEntry:
    timestamp: str
    weight_kg: float
    workout_completed: bool
    workout_summary: str
    calories_consumed: int
    water_liters: float
    energy_level_1_to_10: int
    notes: str = ""

@dataclass
class AgentResult:
    intent: IntentType
    status: str
    data: Any
    guidance: str
    safety_warnings: List[str] = field(default_factory=list)
    disclaimer: str = "Disclaimer: AI wellness guidance does not replace professional medical or clinical advice."
