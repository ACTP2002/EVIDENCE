"""
AI Agent Module

This module contains the AI-powered investigation agent and its skills.
The agent processes cases assembled by the Case Builder and produces
investigation results with evidence and justification.

Skills (11 total):
1. case_context_assembler - Aggregates all relevant data into a coherent case view
2. explainability_generator - Produces human-readable explanations
3. risk_decomposer - Breaks down risk scores into explainable components
4. pattern_matching - Compares against historical fraud patterns
5. false_positive_predictor - Identifies likely false positives (optional)
6. timeline_reconstruction - Builds chronological sequence of events
7. recommendation_engine - Suggests next investigation steps
8. network_intelligence - Detects hidden relationships across entities
9. report_generator - Generates investigation summaries
10. regulatory_explainer - Tailors findings for different audiences
11. learning_engine - Learns from investigation outcomes

Usage:
    from ai_agent.orchestrator import InvestigationOrchestrator

    orchestrator = InvestigationOrchestrator()
    result = orchestrator.investigate(case_id="CASE-2025-88412")
"""

from .orchestrator import InvestigationOrchestrator

__all__ = ['InvestigationOrchestrator']
