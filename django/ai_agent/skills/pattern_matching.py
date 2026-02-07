"""
Historical Similarity & Pattern Matching (Skill #4)

Compares the case against past investigations to identify matching
fraud patterns and confirmed outcomes.

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
SKILL_DIR = Path(__file__).parent / "pattern_matching"


@dataclass
class PatternMatch:
    """A matched historical case."""
    matched_case_id: str
    match_score: float  # 0.0 to 1.0
    matched_patterns: List[str]
    outcome: str  # confirmed_fraud, false_positive, inconclusive
    resolution_action: str
    notes: str


@dataclass
class PatternMatchResult:
    """Complete pattern matching output."""
    top_matches: List[PatternMatch]
    inference: Dict[str, Any]
    patterns_detected: List[str]
    fraud_type_probabilities: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PatternMatcher:
    """
    Matches current case against historical fraud patterns using AI.

    This skill:
    - Extracts patterns from the current case
    - Compares against a database of known fraud patterns
    - Finds similar historical cases
    - Predicts likely outcome based on historical data
    """

    def __init__(self, model: str = "models/gemini-2.5-flash-lite"):
        """
        Initialize the pattern matcher.

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

    def match(self, case_context: CaseContext) -> PatternMatchResult:
        """
        Match case against historical patterns.

        Args:
            case_context: Assembled case context

        Returns:
            PatternMatchResult with matches and predictions
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

    def _parse_output(self, output: Dict[str, Any]) -> PatternMatchResult:
        """Convert AI output dict to PatternMatchResult dataclass."""
        top_matches = [
            PatternMatch(
                matched_case_id=m.get("matched_case_id", ""),
                match_score=m.get("match_score", 0.0),
                matched_patterns=m.get("matched_patterns", []),
                outcome=m.get("outcome", "inconclusive"),
                resolution_action=m.get("resolution_action", ""),
                notes=m.get("notes", "")
            )
            for m in output.get("top_matches", [])
        ]

        return PatternMatchResult(
            top_matches=top_matches,
            inference=output.get("inference", {}),
            patterns_detected=output.get("patterns_detected", []),
            fraud_type_probabilities=output.get("fraud_type_probabilities", {})
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
#     def match(self, case_context: CaseContext) -> PatternMatchResult:
#         try:
#             return self._match_with_ai(case_context)
#         except Exception as e:
#             logger.warning(f"AI failed, falling back to rules: {e}")
#             return self._match_with_rules(case_context)
#
#     def _match_with_rules(self, case_context: CaseContext) -> PatternMatchResult:
#         # Pure Python logic to match patterns against known fraud indicators
#         pass
# =============================================================================
