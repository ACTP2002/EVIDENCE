"""
Cross-Case & Network Intelligence (Skill #7)

Detects hidden relationships across accounts, devices, IPs, and wallets
using graph-based analysis.

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
SKILL_DIR = Path(__file__).parent / "network_intelligence"


@dataclass
class NetworkEntity:
    """An entity in the network graph."""
    entity_id: str
    entity_type: str  # account, customer, device, ip, wallet
    risk_level: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NetworkEdge:
    """A connection between entities."""
    source_id: str
    target_id: str
    connection_type: str
    strength: str
    evidence: str


@dataclass
class NetworkCluster:
    """A cluster of connected entities."""
    cluster_id: str
    entities: List[str]
    risk_score: int
    classification: str  # fraud_ring, legitimate_family, business_accounts, unknown
    central_entity: str


@dataclass
class NetworkIntelligenceResult:
    """Complete network intelligence output."""
    entities: List[NetworkEntity]
    edges: List[NetworkEdge]
    clusters: List[NetworkCluster]
    risk_summary: Dict[str, Any]
    recommended_investigations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class NetworkIntelligence:
    """
    Analyzes network relationships for fraud detection using AI.

    This skill:
    - Maps entity relationships (accounts, devices, IPs)
    - Identifies clusters of connected accounts
    - Detects fraud rings
    - Recommends related entities to investigate
    """

    def __init__(self, model: str = "models/gemini-2.5-flash-lite"):
        """
        Initialize the network intelligence analyzer.

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

    def analyze(self, case_context: CaseContext) -> NetworkIntelligenceResult:
        """
        Analyze network relationships for the given case.

        Args:
            case_context: Assembled case context

        Returns:
            NetworkIntelligenceResult with graph analysis
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

    def _parse_output(self, output: Dict[str, Any]) -> NetworkIntelligenceResult:
        """Convert AI output dict to NetworkIntelligenceResult dataclass."""
        entities = [
            NetworkEntity(
                entity_id=e.get("entity_id", ""),
                entity_type=e.get("entity_type", "account"),
                risk_level=e.get("risk_level", "unknown"),
                attributes=e.get("attributes", {})
            )
            for e in output.get("entities", [])
        ]

        edges = [
            NetworkEdge(
                source_id=e.get("source_id", ""),
                target_id=e.get("target_id", ""),
                connection_type=e.get("connection_type", ""),
                strength=e.get("strength", "medium"),
                evidence=e.get("evidence", "")
            )
            for e in output.get("edges", [])
        ]

        clusters = [
            NetworkCluster(
                cluster_id=c.get("cluster_id", ""),
                entities=c.get("entities", []),
                risk_score=c.get("risk_score", 0),
                classification=c.get("classification", "unknown"),
                central_entity=c.get("central_entity", "")
            )
            for c in output.get("clusters", [])
        ]

        return NetworkIntelligenceResult(
            entities=entities,
            edges=edges,
            clusters=clusters,
            risk_summary=output.get("risk_summary", {}),
            recommended_investigations=output.get("recommended_investigations", [])
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
#     def analyze(self, case_context: CaseContext) -> NetworkIntelligenceResult:
#         try:
#             return self._analyze_with_ai(case_context)
#         except Exception as e:
#             logger.warning(f"AI failed, falling back to rules: {e}")
#             return self._analyze_with_rules(case_context)
#
#     def _analyze_with_rules(self, case_context: CaseContext) -> NetworkIntelligenceResult:
#         # Pure Python logic to build network graph and identify clusters
#         pass
# =============================================================================
