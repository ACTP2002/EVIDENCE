"""
Automated Case Report Generator (Skill #9)

Generates investigation summaries and audit-ready documentation
suitable for compliance and review.

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
SKILL_DIR = Path(__file__).parent / "report_generator"


@dataclass
class ReportSection:
    """A section of the report."""
    title: str
    content: str
    subsections: List[Dict[str, str]] = None


@dataclass
class CaseReport:
    """Complete case report."""
    report_id: str
    case_id: str
    generated_at: str
    report_type: str  # investigation_summary, compliance_report, sar_draft
    executive_summary: str
    sections: List[ReportSection]
    key_findings: List[str]
    recommendations: List[str]
    appendices: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        """Convert report to markdown format."""
        lines = []
        lines.append(f"# Investigation Report: {self.case_id}")
        lines.append(f"\n**Report ID:** {self.report_id}")
        lines.append(f"**Generated:** {self.generated_at}")
        lines.append(f"**Type:** {self.report_type}")

        lines.append("\n## Executive Summary")
        lines.append(self.executive_summary)

        lines.append("\n## Key Findings")
        for finding in self.key_findings:
            lines.append(f"- {finding}")

        for section in self.sections:
            lines.append(f"\n## {section.title}")
            lines.append(section.content)
            if section.subsections:
                for sub in section.subsections:
                    lines.append(f"\n### {sub.get('title', '')}")
                    lines.append(sub.get('content', ''))

        lines.append("\n## Recommendations")
        for rec in self.recommendations:
            lines.append(f"- {rec}")

        return "\n".join(lines)


class ReportGenerator:
    """
    Generates investigation reports using AI.

    This skill creates:
    - Investigation summaries for case review
    - Compliance reports for regulatory review
    - SAR (Suspicious Activity Report) drafts
    - Audit-ready documentation
    """

    def __init__(self, model: str = "models/gemini-2.5-flash-lite"):
        """
        Initialize the report generator.

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

    def generate(
        self,
        case_context: CaseContext,
        report_type: str = "investigation_summary",
        include_appendices: bool = True
    ) -> CaseReport:
        """
        Generate a report for the given case.

        Args:
            case_context: Assembled case context
            report_type: Type of report to generate
            include_appendices: Whether to include detailed appendices

        Returns:
            CaseReport with complete documentation
        """
        from langchain_core.messages import SystemMessage, HumanMessage
        from jsonschema import validate, ValidationError

        self._load_resources()
        llm = self._get_llm()

        case_input = case_context.to_dict()
        case_input["_report_type"] = report_type
        case_input["_include_appendices"] = include_appendices

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

    def _parse_output(self, output: Dict[str, Any]) -> CaseReport:
        """Convert AI output dict to CaseReport dataclass."""
        sections = [
            ReportSection(
                title=s.get("title", ""),
                content=s.get("content", ""),
                subsections=s.get("subsections")
            )
            for s in output.get("sections", [])
        ]

        return CaseReport(
            report_id=output.get("report_id", ""),
            case_id=output.get("case_id", ""),
            generated_at=output.get("generated_at", ""),
            report_type=output.get("report_type", "investigation_summary"),
            executive_summary=output.get("executive_summary", ""),
            sections=sections,
            key_findings=output.get("key_findings", []),
            recommendations=output.get("recommendations", []),
            appendices=output.get("appendices", [])
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
#     def generate(self, case_context: CaseContext, ...) -> CaseReport:
#         try:
#             return self._generate_with_ai(case_context, ...)
#         except Exception as e:
#             logger.warning(f"AI failed, falling back to rules: {e}")
#             return self._generate_with_rules(case_context, ...)
#
#     def _generate_with_rules(self, case_context: CaseContext, ...) -> CaseReport:
#         # Pure Python logic to generate structured report from case data
#         pass
# =============================================================================
