"""
Investigation Recommendation Engine (Skill #6)

Suggests logical next investigation steps while keeping
final decisions with human investigators.

This skill uses LangChain + Google Gemini for AI-powered analysis.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from .case_context_assembler import CaseContext

logger = logging.getLogger(__name__)

# Path to skill resources
SKILL_DIR = Path(__file__).parent / "recommendation_engine"


@dataclass
class Recommendation:
    """A single recommended action."""
    action: str
    priority: str  # P0 (immediate), P1 (high), P2 (medium), P3 (low)
    reason: str
    category: str  # immediate_action, investigation_step, monitoring, documentation
    estimated_impact: str


@dataclass
class RecommendationResult:
    """Complete recommendation output."""
    recommendations: List[Recommendation]
    investigation_priority: str
    suggested_sla_hours: int
    requires_escalation: bool
    escalation_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RecommendationEngine:
    """
    Generates investigation recommendations using AI.

    This skill analyzes the case and suggests:
    - Immediate actions (lock account, hold funds)
    - Investigation steps (verify identity, review history)
    - Monitoring recommendations
    - Documentation requirements
    """

    def __init__(self, model: str = "models/gemini-2.5-flash-lite"):
        """
        Initialize the recommendation engine.

        Args:
            model: Gemini model to use
        """
        self.model = model
        self._llm = None
        self._skill_prompt = None
        self._output_schema = None

    def _load_resources(self):
        """Load SKILL.md prompt and output schema."""
        if self._skill_prompt is None:
            skill_path = SKILL_DIR / "SKILL.md"
            if skill_path.exists():
                self._skill_prompt = skill_path.read_text(encoding="utf-8")
            else:
                raise FileNotFoundError(f"SKILL.md not found at {skill_path}")

        if self._output_schema is None:
            schema_path = SKILL_DIR / "schema.json"
            if schema_path.exists():
                self._output_schema = json.loads(schema_path.read_text(encoding="utf-8"))

    def _get_llm(self):
        """Get or create the LLM instance."""
        if self._llm is None:
            from langchain_google_genai import ChatGoogleGenerativeAI

            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                try:
                    from dotenv import load_dotenv
                    load_dotenv()
                    api_key = os.environ.get("GOOGLE_API_KEY")
                except ImportError:
                    pass

            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment")

            self._llm = ChatGoogleGenerativeAI(
                model=self.model,
                temperature=0,
                google_api_key=api_key
            )

        return self._llm

    def recommend(self, case_context: CaseContext) -> RecommendationResult:
        """
        Generate recommendations for the given case context.

        Args:
            case_context: Assembled case context

        Returns:
            RecommendationResult with prioritized recommendations
        """
        from langchain_core.messages import SystemMessage, HumanMessage
        from jsonschema import validate, ValidationError

        self._load_resources()
        llm = self._get_llm()

        case_input = case_context.to_dict()

        messages = [
            SystemMessage(content=self._skill_prompt),
            SystemMessage(content=(
                "When producing JSON output, return raw JSON only. "
                "Do NOT wrap the response in Markdown code fences such as ```json or ```."
            )),
            HumanMessage(content=json.dumps(case_input, ensure_ascii=False, default=str))
        ]

        response = llm.invoke(messages)
        response_text = response.content.strip()

        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        output = json.loads(response_text)

        if self._output_schema:
            try:
                validate(instance=output, schema=self._output_schema)
            except ValidationError as e:
                logger.warning(f"Schema validation failed: {e.message}")

        return self._parse_output(output)

    def _parse_output(self, output: Dict[str, Any]) -> RecommendationResult:
        """Convert AI output dict to RecommendationResult dataclass."""
        recommendations = [
            Recommendation(
                action=r.get("action", ""),
                priority=r.get("priority", "P2"),
                reason=r.get("reason", ""),
                category=r.get("category", "investigation_step"),
                estimated_impact=r.get("estimated_impact", "")
            )
            for r in output.get("recommendations", [])
        ]

        return RecommendationResult(
            recommendations=recommendations,
            investigation_priority=output.get("investigation_priority", "P2"),
            suggested_sla_hours=output.get("suggested_sla_hours", 72),
            requires_escalation=output.get("requires_escalation", False),
            escalation_reason=output.get("escalation_reason")
        )


# =============================================================================
# FUTURE DEVELOPMENT: Rule-based Fallback
# =============================================================================
# Consider adding a rule-based fallback method for cases when:
# - GOOGLE_API_KEY is not available
# - LangChain dependencies are not installed
# - Network/API errors occur
#
# Example structure:
#
#     def recommend(self, case_context: CaseContext) -> RecommendationResult:
#         try:
#             return self._recommend_with_ai(case_context)
#         except Exception as e:
#             logger.warning(f"AI failed, falling back to rules: {e}")
#             return self._recommend_with_rules(case_context)
#
#     def _recommend_with_rules(self, case_context: CaseContext) -> RecommendationResult:
#         # Pure Python logic to generate recommendations based on alert types
#         pass
# =============================================================================
