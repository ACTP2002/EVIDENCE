import google.generativeai as genai
import json
import os
from pathlib import Path
from typing import Dict, Any

class BaseAISkill:
    def __init__(self, skill_folder_name: str):
        # 1. Setup paths
        self.skill_path = Path(__file__).parent / skill_folder_name
        self.system_prompt = (self.skill_path / "SKILL.md").read_text()
        
        # 2. Configure Gemini
        # It looks for GOOGLE_API_KEY environment variable
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        
        # 3. Initialize the model with the SKILL.md as the system instruction
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro", # or gemini-1.5-flash
            system_instruction=self.system_prompt
        )

    def ask_ai(self, case_context: Any) -> Dict[str, Any]:
        """Send data to Gemini and get structured JSON back."""
        
        # We tell Gemini to use JSON mode
        generation_config = {
            "response_mime_type": "application/json",
        }

        # Send the case context as the user prompt
        response = self.model.generate_content(
            json.dumps(case_context, default=str),
            generation_config=generation_config
        )
        
        # Gemini's response text will be a JSON string
        return json.loads(response.text)

class SkillResultWrapper:
    def __init__(self, data: Dict):
        self.data = data
    def to_dict(self):
        return self.data