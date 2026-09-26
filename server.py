"""
Fitness & Wellness Agent - Full-Stack Web Server
Runs the web app connected directly to the Python Agent and LLM backend.
Logs all queries, tool executions, and LLM calls in real time to the terminal.

Run with:
  python3 server.py [port]
"""

import sys
import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from schemas import UserProfile, ProgressEntry
from memory import MemoryStore
from agent import FitnessWellnessAgent

memory = MemoryStore(storage_path="fitness_memory.json")
agent = FitnessWellnessAgent(memory_store=memory)

class AgentWebHandler(SimpleHTTPRequestHandler):
    """Serves static files and handles /api/query for agent execution."""

    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        if self.path in ["/", "/index.html"]:
            self.path = "/dashboard.html"
            return super().do_GET()
        elif self.path == "/api/logs":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            logs = []
            if os.path.exists("llm_execution.log"):
                try:
                    with open("llm_execution.log", "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        for line in lines[-20:]:
                            if line.strip():
                                logs.append(json.loads(line.strip()))
                except Exception:
                    pass
            self.wfile.write(json.dumps(logs).encode("utf-8"))
            return
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/query":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            try:
                data = json.loads(body)
                prof_data = data.get("profile", {})
                query = data.get("query", "")

                user_profile = UserProfile(
                    user_id=prof_data.get("user_id", "web_user"),
                    name=prof_data.get("name", "User"),
                    age=int(prof_data.get("age", 28)),
                    gender=prof_data.get("gender", "male"),
                    weight_kg=float(prof_data.get("weight_kg", 70.0)),
                    height_cm=float(prof_data.get("height_cm", 175.0)),
                    fitness_goal=prof_data.get("fitness_goal", "fat_loss"),
                    experience_level=prof_data.get("experience_level", "intermediate"),
                    dietary_preference=prof_data.get("dietary_preference", "non_veg"),
                    allergies=prof_data.get("allergies", []),
                    injuries=prof_data.get("injuries", []),
                    location_city=prof_data.get("location_city", "Hyderabad")
                )

                print("\n" + "=" * 65, flush=True)
                print(f"🌐 [WEB API REQUEST] User: {user_profile.name} | City: {user_profile.location_city}", flush=True)
                print(f"   Query: \"{query}\"", flush=True)
                print("=" * 65, flush=True)

                result = agent.process_query(user_profile, query)

                active_model = agent.llm.gemini_model if agent.llm.provider == "gemini" else agent.llm.ollama_model

                # Prepare JSON response
                resp_payload = {
                    "intent": result.intent.value,
                    "status": result.status,
                    "guidance": result.guidance,
                    "safety_warnings": result.safety_warnings,
                    "data": self._serialize(result.data),
                    "llm_trace": {
                        "provider": agent.llm.provider.upper(),
                        "model": active_model,
                        "query": query
                    }
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(resp_payload, default=str).encode("utf-8"))

            except Exception as e:
                print(f"❌ [Server Error]: {e}", flush=True)
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def _serialize(self, obj):
        if hasattr(obj, "__dict__"):
            d = {}
            for k, v in obj.__dict__.items():
                if isinstance(v, list):
                    d[k] = [self._serialize(item) for item in v]
                else:
                    d[k] = self._serialize(v)
            return d
        elif isinstance(obj, list):
            return [self._serialize(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: self._serialize(v) for k, v in obj.items()}
        return obj

    def log_message(self, format, *args):
        try:
            msg = format % args
            if "POST /api/query" in msg or "GET" in msg:
                sys.stderr.write(f"[{self.log_date_time_string()}] {msg}\n")
        except Exception:
            pass

def run_server(port: int = 8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, AgentWebHandler)
    print("=" * 70)
    print(f"🚀 FITNESS & WELLNESS AGENT WEB SERVER STARTED")
    print(f"   URL: http://localhost:{port}")
    print(f"   LLM Provider: {agent.llm.provider.upper()} ({agent.llm.gemini_model if agent.llm.provider == 'gemini' else agent.llm.ollama_model})")
    print("   Live terminal logging of all API queries & LLM calls is ACTIVE.")
    print("=" * 70 + "\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping web server. Goodbye!")
        httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
