"""
Timeline Reconstruction Engine (Skill #6)

Automatically builds a chronological sequence of suspicious activities
to highlight behavioral escalation.

This skill uses LangChain + Google Gemini for AI-powered analysis.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .case_context_assembler import CaseContext

logger = logging.getLogger(__name__)

# Path to skill resources
SKILL_DIR = Path(__file__).parent / "timeline_reconstruction"


@dataclass
class TimelineEvent:
    """A single event in the timeline."""
    t: str  # ISO timestamp
    type: str  # AUTH, TRANSACTION, BEHAVIOR, ALERT
    event: str  # Event name/description
    details: Dict[str, Any]
    related_alerts: List[str] = field(default_factory=list)
    severity: str = "info"  # info, warning, critical


@dataclass
class EscalationAssessment:
    """Assessment of escalation pattern."""
    pattern: str
    severity: str
    escalation_detected: bool
    time_to_escalation_minutes: Optional[int] = None
    narrative: Optional[str] = None


@dataclass
class Timeline:
    """Complete timeline reconstruction output."""
    sequence: List[TimelineEvent]
    escalation_assessment: EscalationAssessment
    window_start: str
    window_end: str
    total_events: int
    critical_events: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TimelineReconstructor:
    """
    Reconstructs timeline of events for a case using AI.
    """

    def __init__(self, model: str = "models/gemini-2.5-flash-lite"):
        """
        Initialize the timeline reconstructor.

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

    def reconstruct(self, case_context: CaseContext) -> Timeline:
        """
        Reconstruct timeline for the given case context.

        Args:
            case_context: Assembled case context

        Returns:
            Timeline with ordered events and escalation assessment
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

        # Convert to Timeline dataclass
        return self._parse_output(output)

    def _parse_output(self, output: Dict[str, Any]) -> Timeline:
        """Convert AI output dict to Timeline dataclass."""
        sequence = [
            TimelineEvent(
                t=e.get("t", ""),
                type=e.get("type", "BEHAVIOR"),
                event=e.get("event", ""),
                details=e.get("details", {}),
                related_alerts=e.get("related_alerts", []),
                severity=e.get("severity", "info")
            )
            for e in output.get("sequence", [])
        ]

        escalation = output.get("escalation_assessment", {})
        escalation_assessment = EscalationAssessment(
            pattern=escalation.get("pattern", ""),
            severity=escalation.get("severity", "low"),
            escalation_detected=escalation.get("escalation_detected", False),
            time_to_escalation_minutes=escalation.get("time_to_escalation_minutes"),
            narrative=escalation.get("narrative")
        )

        return Timeline(
            sequence=sequence,
            escalation_assessment=escalation_assessment,
            window_start=output.get("window_start", ""),
            window_end=output.get("window_end", ""),
            total_events=output.get("total_events", len(sequence)),
            critical_events=output.get("critical_events", 0)
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
#     def reconstruct(self, case_context: CaseContext) -> Timeline:
#         try:
#             return self._reconstruct_with_ai(case_context)
#         except Exception as e:
#             logger.warning(f"AI failed, falling back to rules: {e}")
#             return self._reconstruct_with_rules(case_context)
#
#     def _reconstruct_with_rules(self, case_context: CaseContext) -> Timeline:
#         # Pure Python logic to build timeline from logins, transactions, alerts
#         pass
# =============================================================================
