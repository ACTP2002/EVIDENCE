from ai_agent.orchestrator import InvestigationOrchestrator
from pathlib import Path
import os

# 1. Set your API Key
os.environ["OPENAI_API_KEY"] = "AIzaSyALDy-Ry-k7WFE2c3sVm_2KzhnbuEw2KAs"

# 2. Point to the data folder
orchestrator = InvestigationOrchestrator(data_path=Path("./data"))

# 3. Run the investigation
print("--- Starting Investigation ---")
result = orchestrator.investigate(case_id="CASE-2025-001")

# 4. Print the Result
print(f"Status: {result.status}")
print(f"Headline: {result.dashboard_summary['headline']}")
print(f"Confidence: {result.explainability['confidence']}")
print("\nPlain English Summary:")
print(result.explainability['plain_english_summary'])