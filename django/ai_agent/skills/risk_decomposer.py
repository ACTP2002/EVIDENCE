"""
Risk & Confidence Decomposer (Skill #3)

Breaks the overall risk score into explainable components,
showing why one case scores higher than another.

This skill uses LangChain + Google Gemini for AI-powered analysis.
"""

import os
import json
import logging
from typing import Dict, List, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .case_context_assembler import CaseContext

logger = logging.getLogger(__name__)

# Path to skill resources
SKILL_DIR = Path(__file__).parent / "risk_decomposer"


@dataclass
class RiskComponent:
    """A single component of the risk score."""
    component_name: str
    component_score: int  # 0-100
    weight: float  # How much this contributes to overall score
    weighted_contribution: float  # component_score * weight
    explanation: str
    contributing_factors: List[str] = field(default_factory=list)


@dataclass
class RiskDecomposition:
    """Complete risk decomposition output."""
    overall_risk_score: int
    risk_level: str  # low, medium, high, critical
    components: List[RiskComponent]
    comparison_baseline: str
    key_differentiators: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RiskDecomposer:
    """
    Decomposes risk scores into explainable components using AI.

    This skill breaks down the overall case risk into:
    - Identity risk (KYC issues, document flags)
    - Behavioral risk (unusual patterns)
    - Transaction risk (amount, velocity, destinations)
    - Network risk (connections to suspicious entities)
    - Historical risk (prior cases)
    """

    def __init__(self, model: str = "models/gemini-2.5-flash-lite"):
        """
        Initialize the risk decomposer.

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

            # Load API key from environment
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                # python-dotenv is optional - if not installed, user must set
                # GOOGLE_API_KEY directly in their environment/shell
                try:
                    from dotenv import load_dotenv
                    load_dotenv()
                    api_key = os.environ.get("GOOGLE_API_KEY")
                except ImportError:
                    pass  # dotenv not installed, continue without it

            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment")

            self._llm = ChatGoogleGenerativeAI(
                model=self.model,
                temperature=0,
                google_api_key=api_key
            )

        return self._llm

    def decompose(self, case_context: CaseContext) -> RiskDecomposition:
        """
        Decompose risk score for the given case context.

        Args:
            case_context: Assembled case context

        Returns:
            RiskDecomposition with component breakdown
        """
        from langchain_core.messages import SystemMessage, HumanMessage
        from jsonschema import validate, ValidationError

        self._load_resources()
        llm = self._get_llm()

        # Prepare input - convert CaseContext to dict
        case_input = case_context.to_dict()

        # Build messages
        messages = [
            SystemMessage(content=self._skill_prompt),
            SystemMessage(content=(
                "When producing JSON output, return raw JSON only. "
                "Do NOT wrap the response in Markdown code fences such as ```json or ```."
            )),
            HumanMessage(content=json.dumps(case_input, ensure_ascii=False, default=str))
        ]

        # Invoke LLM
        response = llm.invoke(messages)
        response_text = response.content.strip()

        # Clean response (remove markdown if present)
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        # Parse JSON response
        output = json.loads(response_text)

        # Validate against schema
        if self._output_schema:
            try:
                validate(instance=output, schema=self._output_schema)
            except ValidationError as e:
                logger.warning(f"Schema validation failed: {e.message}")

        # Convert to RiskDecomposition dataclass
        return self._parse_output(output)

    def _parse_output(self, output: Dict[str, Any]) -> RiskDecomposition:
        """Convert AI output dict to RiskDecomposition dataclass."""
        components = [
            RiskComponent(
                component_name=c.get("component_name", ""),
                component_score=c.get("component_score", 0),
                weight=c.get("weight", 0.0),
                weighted_contribution=c.get("weighted_contribution", 0.0),
                explanation=c.get("explanation", ""),
                contributing_factors=c.get("contributing_factors", [])
            )
            for c in output.get("components", [])
        ]

        return RiskDecomposition(
            overall_risk_score=output.get("overall_risk_score", 0),
            risk_level=output.get("risk_level", "low"),
            components=components,
            comparison_baseline=output.get("comparison_baseline", ""),
            key_differentiators=output.get("key_differentiators", [])
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
#     def decompose(self, case_context: CaseContext) -> RiskDecomposition:
#         try:
#             return self._decompose_with_ai(case_context)
#         except Exception as e:
#             logger.warning(f"AI failed, falling back to rules: {e}")
#             return self._decompose_with_rules(case_context)
#
#     def _decompose_with_rules(self, case_context: CaseContext) -> RiskDecomposition:
#         # Pure Python logic to calculate risk components from case data
#         pass
# =============================================================================
