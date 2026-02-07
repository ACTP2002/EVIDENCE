"""
Regulatory & Audience-Aware Explanation Engine (Skill #10)

Tailors investigation findings for different audiences, including
investigators, compliance teams, and regulators.

This skill uses LangChain + Google Gemini for AI-powered analysis.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from .case_context_assembler import CaseContext

logger = logging.getLogger(__name__)

# Path to skill resources
SKILL_DIR = Path(__file__).parent / "regulatory_explainer"


class Audience(Enum):
    """Target audiences for explanations."""
    INVESTIGATOR = "investigator"
    COMPLIANCE = "compliance"
    REGULATOR = "regulator"
    MANAGEMENT = "management"
    CUSTOMER_SERVICE = "customer_service"


@dataclass
class AudienceExplanation:
    """Explanation tailored for a specific audience."""
    audience: str
    summary: str
    key_points: List[str]
    technical_details: Optional[str]
    recommended_actions: List[str]
    regulatory_references: List[str]
    risk_level_description: str


@dataclass
class RegulatoryExplanationResult:
    """Complete regulatory explanation output."""
    case_id: str
    explanations: Dict[str, AudienceExplanation]
    compliance_requirements: List[str]
    reporting_obligations: List[str]
    documentation_checklist: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RegulatoryExplainer:
    """
    Generates audience-appropriate explanations using AI.

    This skill tailors findings for:
    - Investigators (technical, actionable)
    - Compliance teams (regulatory focus)
    - Regulators (formal, evidence-based)
    - Management (high-level, impact-focused)
    - Customer service (simple, script-ready)
    """

    def __init__(self, model: str = "models/gemini-2.5-flash-lite"):
        """
        Initialize the regulatory explainer.

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

    def explain(
        self,
        case_context: CaseContext,
        audiences: List[Audience] = None
    ) -> RegulatoryExplanationResult:
        """
        Generate audience-tailored explanations.

        Args:
            case_context: Assembled case context
            audiences: List of target audiences (defaults to all)

        Returns:
            RegulatoryExplanationResult with tailored explanations
        """
        from langchain_core.messages import SystemMessage, HumanMessage
        from jsonschema import validate, ValidationError

        self._load_resources()
        llm = self._get_llm()

        if audiences is None:
            audiences = list(Audience)

        case_input = case_context.to_dict()
        case_input["_requested_audiences"] = [a.value for a in audiences]

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

    def _parse_output(self, output: Dict[str, Any]) -> RegulatoryExplanationResult:
        """Convert AI output dict to RegulatoryExplanationResult dataclass."""
        explanations = {}
        for audience_key, exp_data in output.get("explanations", {}).items():
            explanations[audience_key] = AudienceExplanation(
                audience=exp_data.get("audience", audience_key),
                summary=exp_data.get("summary", ""),
                key_points=exp_data.get("key_points", []),
                technical_details=exp_data.get("technical_details"),
                recommended_actions=exp_data.get("recommended_actions", []),
                regulatory_references=exp_data.get("regulatory_references", []),
                risk_level_description=exp_data.get("risk_level_description", "")
            )

        return RegulatoryExplanationResult(
            case_id=output.get("case_id", ""),
            explanations=explanations,
            compliance_requirements=output.get("compliance_requirements", []),
            reporting_obligations=output.get("reporting_obligations", []),
            documentation_checklist=output.get("documentation_checklist", [])
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
#     def explain(self, case_context: CaseContext, ...) -> RegulatoryExplanationResult:
#         try:
#             return self._explain_with_ai(case_context, ...)
#         except Exception as e:
#             logger.warning(f"AI failed, falling back to rules: {e}")
#             return self._explain_with_rules(case_context, ...)
#
#     def _explain_with_rules(self, case_context: CaseContext, ...) -> RegulatoryExplanationResult:
#         # Pure Python logic to generate audience-specific explanations
#         pass
# =============================================================================
