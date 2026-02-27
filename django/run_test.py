import os
import json
from pathlib import Path
from ai_agent.skills.explainability_generator import ExplainabilityGenerator

# 1. SET YOUR KEY
os.environ["GOOGLE_API_KEY"] = "AIzaSyALDy-Ry-k7WFE2c3sVm_2KzhnbuEw2KAs" # Your key here

# 2. CREATE FAKE (MOCK) DATA
# This replaces the need for the CaseContextAssembler
class MockCaseContext:
    def __init__(self, data):
        self.data = data
    
    def to_dict(self):
        return self.data

fake_data = {
    "alerts": [
        {
            "id": "AL-99", 
            "type": "Impossible Travel", 
            "severity": "High", 
            "evidence": "Login from Malaysia followed by Login from Brazil 5 minutes later."
        }
    ],
    "customer": {"name": "Test User", "id": "USR-1"},
    "transactions": [],
    "logins": [
        {"timestamp": "2025-01-01T10:00:00Z", "location": "Malaysia"},
        {"timestamp": "2025-01-01T10:05:00Z", "location": "Brazil"}
    ],
    "devices": ["Device-A", "Device-B"]
}

def run_direct_test():
    print("--- Directly Testing ExplainabilityGenerator ---")
    
    # Initialize the Skill directly
    # Note: Ensure the model name matches what is available to you
    skill = ExplainabilityGenerator(model="gemini-2.5-flash-lite")
    
    # Wrap our fake data in our mock class
    context = MockCaseContext(fake_data)
    
    try:
        # Call the AI directly
        print("Sending data to Gemini...")
        result = skill.generate(context)
        
        print("\n" + "="*50)
        print("AI RESPONSE SUCCESSFUL")
        print("="*50)
        print(f"Hypothesis: {result.primary_hypothesis}")
        print(f"Confidence: {result.confidence}")
        print(f"Summary: {result.plain_english_summary}")
        
        print("\nClaims:")
        for claim in result.justification:
            print(f"- {claim.claim}")
            for fact in claim.business_facts:
                print(f"  * {fact}")

    except Exception as e:
        print(f"Skill test failed: {e}")

if __name__ == "__main__":
    run_direct_test()