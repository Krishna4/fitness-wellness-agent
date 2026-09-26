"""
Fitness & Wellness Agent - Dual-Layer Memory Store
Implements:
1. In-session ephemeral turn context
2. Persistent JSON disk storage for user profile, injuries, and historical progress logs (survives restart)
"""

import os
import json
from typing import Dict, Any, Optional, List
from schemas import UserProfile, ProgressEntry

class MemoryStore:
    def __init__(self, storage_path: str = "fitness_memory.json"):
        self.storage_path = storage_path
        self.session_history: List[Dict[str, str]] = []
        self.data: Dict[str, Any] = {
            "users": {},
            "progress_logs": {}
        }
        self.load()

    def load(self) -> None:
        """Load persistent memory from disk."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                pass

    def save(self) -> None:
        """Flush memory state to disk."""
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, default=str)

    def get_or_create_user(self, default_profile: UserProfile) -> UserProfile:
        """Retrieve user profile from store or seed with default."""
        uid = default_profile.user_id
        if uid in self.data["users"]:
            u = self.data["users"][uid]
            return UserProfile(
                user_id=u["user_id"],
                name=u["name"],
                age=u["age"],
                gender=u["gender"],
                weight_kg=u["weight_kg"],
                height_cm=u["height_cm"],
                fitness_goal=u["fitness_goal"],
                experience_level=u["experience_level"],
                dietary_preference=u["dietary_preference"],
                allergies=u.get("allergies", []),
                injuries=u.get("injuries", []),
                location_city=u.get("location_city", "Hyderabad"),
                latitude=u.get("latitude", 17.3850),
                longitude=u.get("longitude", 78.4867)
            )
        else:
            self.data["users"][uid] = default_profile.__dict__
            if uid not in self.data["progress_logs"]:
                self.data["progress_logs"][uid] = []
            self.save()
            return default_profile

    def update_profile(self, user_profile: UserProfile) -> None:
        """Update persistent user profile."""
        self.data["users"][user_profile.user_id] = user_profile.__dict__
        self.save()

    def append_progress(self, user_id: str, entry: ProgressEntry) -> None:
        """Append progress entry to persistent log."""
        if user_id not in self.data["progress_logs"]:
            self.data["progress_logs"][user_id] = []
        self.data["progress_logs"][user_id].append(entry.__dict__)
        self.save()

    def get_progress_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve user progress history."""
        return self.data["progress_logs"].get(user_id, [])

    def record_turn(self, role: str, message: str) -> None:
        """Record conversational turn in ephemeral session."""
        self.session_history.append({"role": role, "message": message})
