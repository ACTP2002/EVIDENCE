"""
Investigation Orchestrator

Main orchestrator that coordinates all AI Agent skills to perform
comprehensive fraud investigations.

Usage:
    from ai_agent.orchestrator import InvestigationOrchestrator

    orchestrator = InvestigationOrchestrator()
    result = orchestrator.investigate("CASE-2025-88412")
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

# Import all skills
from .skills.case_context_assembler import CaseContextAssembler, CaseContext
from .skills.explainability_generator import ExplainabilityGenerator
from .skills.risk_decomposer import RiskDecomposer
from .skills.pattern_matching import PatternMatcher
from .skills.timeline_reconstruction import TimelineReconstructor
from .skills.recommendation_engine import RecommendationEngine
from .skills.network_intelligence import NetworkIntelligence
from .skills.report_generator import ReportGenerator
from .skills.regulatory_explainer import RegulatoryExplainer, Audience
from .skills.learning_engine import LearningEngine, InvestigationOutcome


@dataclass
class SkillExecution:
    """Record of a skill execution."""
    skill_name: str
    executed_at: str
    duration_ms: int
    success: bool
    error: Optional[str] = None


@dataclass
class InvestigationResult:
    """Complete investigation result from all skills."""
    case_id: str
    investigation_id: str
    started_at: str
    completed_at: str
    status: str  # completed, partial, failed

    # Assembled context
    case_context: Dict[str, Any]

    # Skill outputs
    explainability: Dict[str, Any]
    risk_decomposition: Dict[str, Any]
    pattern_matches: Dict[str, Any]
    timeline: Dict[str, Any]
    recommendations: Dict[str, Any]
    network_analysis: Dict[str, Any]
    report: Dict[str, Any]

    # Metadata
    skills_executed: List[SkillExecution]
    total_duration_ms: int

    # Dashboard-ready summary
    dashboard_summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)


class InvestigationOrchestrator:
    """
    Orchestrates the AI Agent's investigation skills.

    This class coordinates:
    1. Case Context Assembly - Gather all relevant data
    2. Explainability Generation - Explain why alerts fired
    3. Risk Decomposition - Break down risk scores
    4. Pattern Matching - Compare to historical cases
    5. Timeline Reconstruction - Build event sequence
    6. Recommendation Generation - Suggest next steps
    7. Network Intelligence - Analyze connections
    8. Report Generation - Create documentation

    Skills can be run individually or as a complete investigation.
    """

    def __init__(self, data_path: Path = None):
        """
        Initialize the orchestrator.

        Args:
            data_path: Optional path to data directory
        """
        self.data_path = data_path

        # Initialize all skills
        self.assembler = CaseContextAssembler(data_path)
        self.explainability = ExplainabilityGenerator()
        self.risk_decomposer = RiskDecomposer()
        self.pattern_matcher = PatternMatcher()
        self.timeline_reconstructor = TimelineReconstructor()
        self.recommendation_engine = RecommendationEngine()
        self.network_intelligence = NetworkIntelligence()
        self.report_generator = ReportGenerator()
        self.regulatory_explainer = RegulatoryExplainer()
        self.learning_engine = LearningEngine()

    def investigate(
        self,
        case_id: str,
        skills: List[str] = None,
        include_report: bool = True,
        include_regulatory: bool = False
    ) -> InvestigationResult:
        """
        Perform a complete investigation on a case.

        Args:
            case_id: The case ID to investigate
            skills: Optional list of specific skills to run (runs all if None)
            include_report: Whether to generate full report
            include_regulatory: Whether to include regulatory explanations

        Returns:
            InvestigationResult with all findings
        """
        investigation_id = f"INV-{case_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        started_at = datetime.now(timezone.utc)
        skills_executed = []
        status = "completed"

        # Default skills to run
        default_skills = [
            "case_context_assembler",
            "explainability_generator",
            "risk_decomposer",
            "pattern_matching",
            "timeline_reconstruction",
            "recommendation_engine",
            "network_intelligence",
        ]
        if include_report:
            default_skills.append("report_generator")
        if include_regulatory:
            default_skills.append("regulatory_explainer")

        skills_to_run = skills or default_skills

        # Initialize result containers
        case_context = None
        case_context_dict = {}
        explainability_result = {}
        risk_result = {}
        pattern_result = {}
        timeline_result = {}
        recommendation_result = {}
        network_result = {}
        report_result = {}

        # Step 1: Assemble case context (required for all other skills)
        if "case_context_assembler" in skills_to_run:
            skill_start = datetime.now(timezone.utc)
            try:
                case_context = self.assembler.assemble(case_id)
                case_context_dict = case_context.to_dict()
                skills_executed.append(SkillExecution(
                    skill_name="Case Context Assembler",
                    executed_at=skill_start.isoformat(),
                    duration_ms=int((datetime.now(timezone.utc) - skill_start).total_seconds() * 1000),
                    success=True
                ))
            except Exception as e:
                skills_executed.append(SkillExecution(
                    skill_name="Case Context Assembler",
                    executed_at=skill_start.isoformat(),
                    duration_ms=int((datetime.now(timezone.utc) - skill_start).total_seconds() * 1000),
                    success=False,
                    error=str(e)
                ))
                status = "failed"
                # Can't continue without case context
                return self._build_failed_result(
                    case_id, investigation_id, started_at, skills_executed, str(e)
                )

        # Step 2: Generate explainability
        if "explainability_generator" in skills_to_run and case_context:
            skill_start = datetime.now(timezone.utc)
            try:
                result = self.explainability.generate(case_context)
                explainability_result = result.to_dict()
                skills_executed.append(SkillExecution(
                    skill_name="Explainability Generator",
                    executed_at=skill_start.isoformat(),
                    duration_ms=int((datetime.now(timezone.utc) - skill_start).total_seconds() * 1000),
                    success=True
                ))
            except Exception as e:
                skills_executed.append(SkillExecution(
                    skill_name="Explainability Generator",
                    executed_at=skill_start.isoformat(),
                    duration_ms=int((datetime.now(timezone.utc) - skill_start).total_seconds() * 1000),
                    success=False,
                    error=str(e)
                ))
                status = "partial"

        # Step 3: Decompose risk
        if "risk_decomposer" in skills_to_run and case_context:
            skill_start = datetime.now(timezone.utc)
            try:
                result = self.risk_decomposer.decompose(case_context)
                risk_result = result.to_dict()
                skills_executed.append(SkillExecution(
                    skill_name="Risk Decomposer",
                    executed_at=skill_start.isoformat(),
                    duration_ms=int((datetime.now(timezone.utc) - skill_start).total_seconds() * 1000),
                    success=True
                ))
            except Exception as e:
                skills_executed.append(SkillExecution(
                    skill_name="Risk Decomposer",
                    executed_at=skill_start.isoformat(),
                    duration_ms=int((datetime.now(timezone.utc) - skill_start).total_seconds() * 1000),
                    success=False,
                    error=str(e)
                ))
                status = "partial"

        # Step 4: Pattern matching
        if "pattern_matching" in skills_to_run and case_context:
            skill_start = datetime.now(timezone.utc)
            try:
                result = self.pattern_matcher.match(case_context)
                pattern_result = result.to_dict()
                skills_executed.append(SkillExecution(
                    skill_name="Pattern Matcher",
                    executed_at=skill_start.isoformat(),
                    duration_ms=int((datetime.now(timezone.utc) - skill_start).total_seconds() * 1000),
                    success=True
                ))
            except Exception as e:
                skills_executed.append(SkillExecution(
                    skill_name="Pattern Matcher",
                    executed_at=skill_start.isoformat(),
                    duration_ms=int((datetime.now(timezone.utc) - skill_start).total_seconds() * 1000),
                    success=False,
                    error=str(e)
                ))
                status = "partial"

        # Step 5: Timeline reconstruction
        if "timeline_reconstruction" in skills_to_run and case_context:
            skill_start = datetime.now(timezone.utc)
            try:
                result = self.timeline_reconstructor.reconstruct(case_context)
                timeline_result = result.to_dict()
                skills_executed.append(SkillExecution(
                    skill_name="Timeline Reconstructor",
                    executed_at=skill_start.isoformat(),
                    duration_ms=int((datetime.now(timezone.utc) - skill_start).total_seconds() * 1000),
                    success=True
                ))
            except Exception as e:
                skills_executed.append(SkillExecution(
                    skill_name="Timeline Reconstructor",
                    executed_at=skill_start.isoformat(),
                    duration_ms=int((datetime.now(timezone.utc) - skill_start).total_seconds() * 1000),
                    success=False,
                    error=str(e)
                ))
                status = "partial"

        # Step 6: Recommendations
        if "recommendation_engine" in skills_to_run and case_context:
            skill_start = datetime.now(timezone.utc)
            try:
                result = self.recommendation_engine.recommend(case_context)
                recommendation_result = result.to_dict()
                skills_executed.append(SkillExecution(
                    skill_name="Recommendation Engine",
                    executed_at=skill_start.isoformat(),
                    duration_ms=int((datetime.now(timezone.utc) - skill_start).total_seconds() * 1000),
                    success=True
                ))
            except Exception as e:
                skills_executed.append(SkillExecution(
                    skill_name="Recommendation Engine",
                    executed_at=skill_start.isoformat(),
                    duration_ms=int((datetime.now(timezone.utc) - skill_start).total_seconds() * 1000),
                    success=False,
                    error=str(e)
                ))
                status = "partial"

        # Step 7: Network intelligence
        if "network_intelligence" in skills_to_run and case_context:
            skill_start = datetime.now(timezone.utc)
            try:
                result = self.network_intelligence.analyze(case_context)
                network_result = result.to_dict()
                skills_executed.append(SkillExecution(
                    skill_name="Network Intelligence",
                    executed_at=skill_start.isoformat(),
                    duration_ms=int((datetime.now(timezone.utc) - skill_start).total_seconds() * 1000),
                    success=True
                ))
            except Exception as e:
                skills_executed.append(SkillExecution(
                    skill_name="Network Intelligence",
                    executed_at=skill_start.isoformat(),
                    duration_ms=int((datetime.now(timezone.utc) - skill_start).total_seconds() * 1000),
                    success=False,
                    error=str(e)
                ))
                status = "partial"

        # Step 8: Report generation (optional)
        if "report_generator" in skills_to_run and case_context:
            skill_start = datetime.now(timezone.utc)
            try:
                result = self.report_generator.generate(case_context)
                report_result = result.to_dict()
                skills_executed.append(SkillExecution(
                    skill_name="Report Generator",
                    executed_at=skill_start.isoformat(),
                    duration_ms=int((datetime.now(timezone.utc) - skill_start).total_seconds() * 1000),
                    success=True
                ))
            except Exception as e:
                skills_executed.append(SkillExecution(
                    skill_name="Report Generator",
                    executed_at=skill_start.isoformat(),
                    duration_ms=int((datetime.now(timezone.utc) - skill_start).total_seconds() * 1000),
                    success=False,
                    error=str(e)
                ))
                status = "partial"

        # Calculate totals
        completed_at = datetime.now(timezone.utc)
        total_duration = int((completed_at - started_at).total_seconds() * 1000)

        # Build dashboard summary
        dashboard_summary = self._build_dashboard_summary(
            case_context_dict,
            explainability_result,
            risk_result,
            recommendation_result,
            timeline_result
        )

        return InvestigationResult(
            case_id=case_id,
            investigation_id=investigation_id,
            started_at=started_at.isoformat() + "Z",
            completed_at=completed_at.isoformat() + "Z",
            status=status,
            case_context=case_context_dict,
            explainability=explainability_result,
            risk_decomposition=risk_result,
            pattern_matches=pattern_result,
            timeline=timeline_result,
            recommendations=recommendation_result,
            network_analysis=network_result,
            report=report_result,
            skills_executed=skills_executed,
            total_duration_ms=total_duration,
            dashboard_summary=dashboard_summary
        )

    def _build_failed_result(
        self,
        case_id: str,
        investigation_id: str,
        started_at: datetime,
        skills_executed: List[SkillExecution],
        error: str
    ) -> InvestigationResult:
        """Build a failed investigation result."""
        completed_at = datetime.now(timezone.utc)
        return InvestigationResult(
            case_id=case_id,
            investigation_id=investigation_id,
            started_at=started_at.isoformat() + "Z",
            completed_at=completed_at.isoformat() + "Z",
            status="failed",
            case_context={},
            explainability={},
            risk_decomposition={},
            pattern_matches={},
            timeline={},
            recommendations={},
            network_analysis={},
            report={},
            skills_executed=skills_executed,
            total_duration_ms=int((completed_at - started_at).total_seconds() * 1000),
            dashboard_summary={"error": error}
        )

    def _build_dashboard_summary(
        self,
        case_context: Dict,
        explainability: Dict,
        risk: Dict,
        recommendations: Dict,
        timeline: Dict
    ) -> Dict[str, Any]:
        """Build dashboard-ready summary."""
        summary = {
            "headline": "",
            "risk_level": "unknown",
            "risk_score": 0,
            "key_evidence": [],
            "recommended_actions": [],
            "escalation_required": False,
        }

        # Extract headline from explainability
        if explainability:
            summary["headline"] = explainability.get("primary_hypothesis", "Under investigation")

        # Extract risk from decomposition
        if risk:
            summary["risk_level"] = risk.get("risk_level", "unknown")
            summary["risk_score"] = risk.get("overall_risk_score", 0)

        # Extract key evidence from explainability
        if explainability and "justification" in explainability:
            for claim in explainability["justification"][:3]:
                if isinstance(claim, dict):
                    for fact in claim.get("business_facts", [])[:2]:
                        summary["key_evidence"].append(fact)

        # Extract recommended actions
        if recommendations and "recommendations" in recommendations:
            for rec in recommendations["recommendations"][:4]:
                if isinstance(rec, dict):
                    summary["recommended_actions"].append({
                        "action": rec.get("action", ""),
                        "priority": rec.get("priority", "P2")
                    })

        # Check escalation
        if recommendations:
            summary["escalation_required"] = recommendations.get("requires_escalation", False)

        return summary

    def record_outcome(
        self,
        case_id: str,
        outcome: str,
        investigator_notes: str = None
    ) -> Dict[str, Any]:
        """
        Record investigation outcome for learning.

        Args:
            case_id: The case ID
            outcome: One of 'confirmed_fraud', 'false_positive', 'inconclusive'
            investigator_notes: Optional notes from investigator

        Returns:
            Learning result
        """
        # Map string to enum
        outcome_map = {
            "confirmed_fraud": InvestigationOutcome.CONFIRMED_FRAUD,
            "false_positive": InvestigationOutcome.FALSE_POSITIVE,
            "inconclusive": InvestigationOutcome.INCONCLUSIVE,
        }
        outcome_enum = outcome_map.get(outcome, InvestigationOutcome.INCONCLUSIVE)

        # Assemble context
        case_context = self.assembler.assemble(case_id)

        # Run learning
        result = self.learning_engine.learn(case_context, outcome_enum, investigator_notes)

        return result.to_dict()


# Convenience function for quick investigations
def investigate_case(case_id: str, data_path: Path = None) -> InvestigationResult:
    """
    Convenience function to investigate a case.

    Args:
        case_id: The case ID to investigate
        data_path: Optional path to data directory

    Returns:
        InvestigationResult
    """
    orchestrator = InvestigationOrchestrator(data_path)
    return orchestrator.investigate(case_id)
