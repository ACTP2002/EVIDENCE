"""
Explainability Generator (Skill #2)

Produces human-readable explanations describing why an alert was triggered
using observable business facts.

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
SKILL_DIR = Path(__file__).parent / "explainability_generator"


@dataclass
class Claim:
    """A single claim in the explanation."""
    claim: str
    business_facts: List[str]
    linked_alerts: List[str] = field(default_factory=list)


@dataclass
class Explainability:
    """Complete explainability output."""
    primary_hypothesis: str
    confidence: float
    justification: List[Claim]
    plain_english_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ExplainabilityGenerator:
    """
    Generates human-readable explanations for fraud alerts using AI.

    This skill takes a CaseContext and produces explanations that:
    - State the primary hypothesis (what type of fraud is suspected)
    - Provide confidence level
    - List claims backed by observable business facts
    - Link claims to specific alerts
    - Summarize in plain English
    """

    def __init__(self, model: str = "models/gemini-2.5-flash-lite"):
        """
        Initialize the explainability generator.

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

    def generate(self, case_context: CaseContext) -> Explainability:
        """
        Generate explainability for the given case context.

        Args:
            case_context: Assembled case context

        Returns:
            Explainability with hypothesis, justification, and summary
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

        # Convert to Explainability dataclass
        return self._parse_output(output)

    def _parse_output(self, output: Dict[str, Any]) -> Explainability:
        """Convert AI output dict to Explainability dataclass."""
        justification = [
            Claim(
                claim=c.get("claim", ""),
                business_facts=c.get("business_facts", []),
                linked_alerts=c.get("linked_alerts", [])
            )
            for c in output.get("justification", [])
        ]

        return Explainability(
            primary_hypothesis=output.get("primary_hypothesis", "Unknown suspicious activity"),
            confidence=output.get("confidence", 0.0),
            justification=justification,
            plain_english_summary=output.get("plain_english_summary", "")
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
#     def generate(self, case_context: CaseContext) -> Explainability:
#         try:
#             return self._generate_with_ai(case_context)
#         except Exception as e:
#             logger.warning(f"AI failed, falling back to rules: {e}")
#             return self._generate_with_rules(case_context)
#
#     def _generate_with_rules(self, case_context: CaseContext) -> Explainability:
#         # Pure Python logic to generate explanations from alerts and evidence
#         pass
# =============================================================================
