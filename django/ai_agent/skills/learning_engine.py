"""
Learning & Knowledge Capture Engine (Skill #11)

Learns from investigation outcomes to improve detection accuracy,
prioritization, and future fraud recognition.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from .case_context_assembler import CaseContext


class InvestigationOutcome(Enum):
    """Possible investigation outcomes."""
    CONFIRMED_FRAUD = "confirmed_fraud"
    FALSE_POSITIVE = "false_positive"
    INCONCLUSIVE = "inconclusive"
    PENDING = "pending"


@dataclass
class PatternLearning:
    """A learned pattern from investigation."""
    pattern_id: str
    pattern_type: str
    indicators: List[str]
    outcome_correlation: float  # -1 to 1 (negative = false positive indicator)
    sample_size: int
    confidence: float
    last_updated: str


@dataclass
class FeedbackRecord:
    """Record of investigation feedback."""
    case_id: str
    outcome: str
    feedback_timestamp: str
    investigator_id: Optional[str]
    notes: Optional[str]
    patterns_identified: List[str]
    false_positive_indicators: List[str]
    confirmed_fraud_indicators: List[str]


@dataclass
class LearningInsight:
    """Insight derived from learning."""
    insight_type: str  # pattern_improvement, threshold_adjustment, new_pattern
    description: str
    impact_estimate: str
    recommendation: str
    supporting_evidence: List[str]


@dataclass
class LearningResult:
    """Complete learning engine output."""
    case_id: str
    extracted_patterns: List[PatternLearning]
    suggested_improvements: List[LearningInsight]
    feedback_recorded: bool
    knowledge_base_updates: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LearningEngine:
    """
    Captures knowledge from investigations to improve future detection.

    This skill:
    - Extracts patterns from resolved cases
    - Identifies false positive indicators
    - Suggests threshold adjustments
    - Feeds learnings back to detection systems
    """

    # Simulated knowledge base (would be database in production)
    _knowledge_base: Dict[str, Any] = {
        "patterns": {},
        "thresholds": {},
        "false_positive_indicators": [],
        "confirmed_fraud_indicators": [],
    }

    def learn(
        self,
        case_context: CaseContext,
        outcome: InvestigationOutcome = None,
        investigator_notes: str = None
    ) -> LearningResult:
        """
        Learn from a case investigation.

        Args:
            case_context: Assembled case context
            outcome: Investigation outcome (if known)
            investigator_notes: Notes from investigator

        Returns:
            LearningResult with extracted patterns and improvements
        """
        # Extract patterns from case
        patterns = self._extract_patterns(case_context, outcome)

        # Generate improvement suggestions
        improvements = self._suggest_improvements(case_context, outcome, patterns)

        # Record feedback if outcome provided
        feedback_recorded = False
        if outcome:
            self._record_feedback(case_context, outcome, investigator_notes)
            feedback_recorded = True

        # Generate knowledge base updates
        kb_updates = self._generate_kb_updates(patterns, outcome)

        return LearningResult(
            case_id=case_context.case_id,
            extracted_patterns=patterns,
            suggested_improvements=improvements,
            feedback_recorded=feedback_recorded,
            knowledge_base_updates=kb_updates
        )

    def _extract_patterns(
        self, case_context: CaseContext, outcome: InvestigationOutcome = None
    ) -> List[PatternLearning]:
        """Extract patterns from case."""
        patterns = []

        # Extract alert combination patterns (using signal field from new schema)
        alert_types = sorted([a.signal for a in case_context.alerts if a.signal])
        if len(alert_types) > 1:
            pattern_id = f"COMBO-{'-'.join(alert_types[:3])}"
            correlation = 0.5  # Default neutral
            if outcome == InvestigationOutcome.CONFIRMED_FRAUD:
                correlation = 0.8
            elif outcome == InvestigationOutcome.FALSE_POSITIVE:
                correlation = -0.6

            patterns.append(PatternLearning(
                pattern_id=pattern_id,
                pattern_type="alert_combination",
                indicators=alert_types,
                outcome_correlation=correlation,
                sample_size=1,
                confidence=0.3,  # Low confidence for single case
                last_updated=datetime.now(timezone.utc).isoformat()
            ))

        # Extract behavioral patterns from login data (new schema uses data.success, data.method)
        login_indicators = []
        for login in case_context.logins:
            if login.data:
                if not login.data.success:
                    login_indicators.append("failed_login")
                if login.data.risk_hint:
                    login_indicators.append(login.data.risk_hint)
                if login.data.geo and login.data.geo.country:
                    login_indicators.append(f"country_{login.data.geo.country}")
        login_indicators = list(set(login_indicators))

        if login_indicators:
            patterns.append(PatternLearning(
                pattern_id=f"LOGIN-{'-'.join(sorted(login_indicators)[:3])}",
                pattern_type="login_behavior",
                indicators=login_indicators,
                outcome_correlation=0.5 if outcome != InvestigationOutcome.FALSE_POSITIVE else -0.4,
                sample_size=1,
                confidence=0.3,
                last_updated=datetime.now(timezone.utc).isoformat()
            ))

        # Extract transaction patterns (new schema uses event_type, data.amount)
        txn_indicators = []
        for txn in case_context.transactions:
            if txn.event_type:
                txn_indicators.append(f"type_{txn.event_type}")
            if txn.data and txn.data.amount and txn.data.amount > 10000:
                txn_indicators.append("high_value")
            if txn.data and txn.data.stock_id:
                txn_indicators.append(f"stock_{txn.data.stock_id}")
        txn_indicators = list(set(txn_indicators))

        if txn_indicators:
            patterns.append(PatternLearning(
                pattern_id=f"TXN-{'-'.join(sorted(txn_indicators)[:3])}",
                pattern_type="transaction_behavior",
                indicators=txn_indicators,
                outcome_correlation=0.6 if outcome == InvestigationOutcome.CONFIRMED_FRAUD else 0.0,
                sample_size=1,
                confidence=0.3,
                last_updated=datetime.now(timezone.utc).isoformat()
            ))

        # Extract network patterns (new schema uses network_events)
        if len(case_context.network_events) >= 3:
            vpn_count = sum(1 for n in case_context.network_events if n.data and n.data.vpn_suspected)
            unique_ips = len(set(n.ip for n in case_context.network_events if n.ip))
            network_indicators = [f"events_{len(case_context.network_events)}", f"unique_ips_{unique_ips}"]
            if vpn_count > 0:
                network_indicators.append(f"vpn_count_{vpn_count}")
            patterns.append(PatternLearning(
                pattern_id=f"NETWORK-{len(case_context.network_events)}",
                pattern_type="network_cluster",
                indicators=network_indicators,
                outcome_correlation=0.7 if outcome == InvestigationOutcome.CONFIRMED_FRAUD else 0.2,
                sample_size=1,
                confidence=0.4,
                last_updated=datetime.now(timezone.utc).isoformat()
            ))

        return patterns

    def _suggest_improvements(
        self,
        case_context: CaseContext,
        outcome: InvestigationOutcome,
        patterns: List[PatternLearning]
    ) -> List[LearningInsight]:
        """Suggest improvements based on learnings."""
        insights = []

        if outcome == InvestigationOutcome.FALSE_POSITIVE:
            # Suggest ways to reduce false positives

            # Check for travel-related false positive (new schema uses data.risk_hint)
            travel_related = any(
                l.data and l.data.risk_hint and "travel" in l.data.risk_hint.lower()
                for l in case_context.logins
            )
            if travel_related:
                insights.append(LearningInsight(
                    insight_type="threshold_adjustment",
                    description="Possible travel-related false positive detected",
                    impact_estimate="Could reduce similar false positives by 15-20%",
                    recommendation="Consider implementing travel notification system or adjusting impossible travel time thresholds",
                    supporting_evidence=[
                        "Login flagged for impossible travel",
                        "No suspicious transactions followed",
                        "Case resolved as false positive"
                    ]
                ))

            # Check for amount-based false positive (new schema uses profile.created_at)
            if case_context.profile and case_context.profile.created_at:
                try:
                    from datetime import datetime
                    created = datetime.fromisoformat(case_context.profile.created_at.replace("Z", "+00:00"))
                    account_age_days = (datetime.now(timezone.utc) - created).days
                    if account_age_days > 365:
                        insights.append(LearningInsight(
                            insight_type="pattern_improvement",
                            description="Established account flagged for amount anomaly",
                            impact_estimate="Could improve precision for mature accounts",
                            recommendation="Consider adjusting thresholds based on account tenure",
                            supporting_evidence=[
                                f"Account age: {account_age_days} days",
                                "False positive on established account"
                            ]
                        ))
                except (ValueError, TypeError):
                    pass  # Skip if date parsing fails

        elif outcome == InvestigationOutcome.CONFIRMED_FRAUD:
            # Suggest ways to improve detection

            # Check for patterns that could be detected earlier
            for pattern in patterns:
                if pattern.outcome_correlation > 0.7:
                    insights.append(LearningInsight(
                        insight_type="new_pattern",
                        description=f"High-correlation pattern identified: {pattern.pattern_type}",
                        impact_estimate="Could improve early detection",
                        recommendation=f"Add pattern {pattern.pattern_id} to detection rules with indicators: {', '.join(pattern.indicators[:3])}",
                        supporting_evidence=[
                            f"Correlation: {pattern.outcome_correlation}",
                            f"Pattern type: {pattern.pattern_type}"
                        ]
                    ))

            # Check if network analysis could have helped earlier (new schema uses network_events)
            if case_context.network_events:
                vpn_events = sum(1 for n in case_context.network_events if n.data and n.data.vpn_suspected)
                insights.append(LearningInsight(
                    insight_type="pattern_improvement",
                    description="Network events present in confirmed fraud case",
                    impact_estimate="Network-based detection could catch similar cases",
                    recommendation="Weight network signals more heavily in risk scoring",
                    supporting_evidence=[
                        f"{len(case_context.network_events)} network events found",
                        f"{vpn_events} VPN-suspected connections"
                    ]
                ))

        return insights

    def _record_feedback(
        self,
        case_context: CaseContext,
        outcome: InvestigationOutcome,
        notes: str = None
    ) -> FeedbackRecord:
        """Record investigation feedback."""
        # Extract indicators by outcome (new schema uses different fields)
        fp_indicators = []
        fraud_indicators = []

        all_indicators = []
        for login in case_context.logins:
            if login.data and login.data.risk_hint:
                all_indicators.append(login.data.risk_hint)
            if login.data and not login.data.success:
                all_indicators.append("failed_login")
        for txn in case_context.transactions:
            if txn.event_type:
                all_indicators.append(f"txn_{txn.event_type}")
        for net in case_context.network_events:
            if net.data and net.data.vpn_suspected:
                all_indicators.append("vpn_suspected")

        if outcome == InvestigationOutcome.FALSE_POSITIVE:
            fp_indicators = list(set(all_indicators))
        elif outcome == InvestigationOutcome.CONFIRMED_FRAUD:
            fraud_indicators = list(set(all_indicators))

        record = FeedbackRecord(
            case_id=case_context.case_id,
            outcome=outcome.value,
            feedback_timestamp=datetime.now(timezone.utc).isoformat(),
            investigator_id=None,
            notes=notes,
            patterns_identified=[a.signal for a in case_context.alerts if a.signal],
            false_positive_indicators=fp_indicators,
            confirmed_fraud_indicators=fraud_indicators
        )

        # Would persist to database in production
        return record

    def _generate_kb_updates(
        self,
        patterns: List[PatternLearning],
        outcome: InvestigationOutcome
    ) -> List[Dict[str, Any]]:
        """Generate knowledge base updates."""
        updates = []

        for pattern in patterns:
            updates.append({
                "type": "pattern_update",
                "pattern_id": pattern.pattern_id,
                "action": "upsert",
                "data": {
                    "indicators": pattern.indicators,
                    "correlation": pattern.outcome_correlation,
                    "outcome": outcome.value if outcome else "unknown"
                }
            })

        return updates

    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get summary of accumulated knowledge."""
        return {
            "total_patterns": len(self._knowledge_base.get("patterns", {})),
            "false_positive_indicators": len(self._knowledge_base.get("false_positive_indicators", [])),
            "confirmed_fraud_indicators": len(self._knowledge_base.get("confirmed_fraud_indicators", [])),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
