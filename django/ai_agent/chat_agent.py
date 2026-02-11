"""
SENTINEL Conversational Investigation Agent

Hybrid approach (Option C):
- Loads full case context at conversation start (no LLM call)
- Agent answers most questions from context (single LLM call)
- Heavy tools (network, similar cases, report) called only when explicitly needed

Usage:
    from ai_agent.chat_agent import chat_with_sentinel

    result = chat_with_sentinel(
        case_id="FR-2024-0847",
        message="Why was this flagged?",
        history=[]
    )
    print(result["response"])
    print(result["suggested_questions"])
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

# Load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .skills.case_context_assembler import CaseContextAssembler, CaseContext

# Model configuration from environment
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "models/gemini-2.5-flash-lite")
from .skills.network_intelligence import NetworkIntelligence
from .skills.pattern_matching import PatternMatcher
from .skills.report_generator import ReportGenerator

logger = logging.getLogger(__name__)


# =============================================================================
# SYSTEM PROMPT - Case context is injected here
# =============================================================================

SENTINEL_SYSTEM_PROMPT = """You are SENTINEL, an AI fraud investigation assistant helping fraud analysts investigate cases efficiently.

You are currently investigating case {case_id}. Below is the complete case context - use this data to answer questions accurately.

---

## CASE SUMMARY
- **Case ID:** {case_id}
- **Created:** {created_at}
- **Customer:** {customer_name} ({customer_id})
- **Account:** {account_id}
- **Account Status:** {account_status}
- **Account Age:** {account_age_days} days

## ALERTS TRIGGERED
{alerts_formatted}

## CUSTOMER KYC DATA
{kyc_formatted}

## ACCOUNT ACTIVITY (Last 30 Days)
- Total Deposits: ${total_deposits:,.2f}
- Total Withdrawals: ${total_withdrawals:,.2f}
- Deposit-to-Income Ratio: {deposit_to_income_ratio}
- Total Trades: {total_trades}

## RECENT TRANSACTIONS
{transactions_formatted}

## LOGIN HISTORY
{logins_formatted}

## DEVICES
{devices_formatted}

## NETWORK CONNECTIONS
{network_formatted}

## PRIOR CASES
{prior_cases_formatted}

---

## YOUR INSTRUCTIONS

1. **Answer questions using the case data above.** Be specific - cite transaction IDs, dates, amounts, and other concrete details.

2. **Explain risk factors in plain language.** Help investigators understand WHY something is suspicious.

3. **For complex analysis requests**, let the user know you can provide:
   - Detailed network/fraud ring analysis
   - Historical pattern matching
   - Formal compliance reports

4. **Be concise but thorough.** Investigators are busy - get to the point while providing actionable insights.

5. **At the end of your response, suggest 2-3 follow-up questions** the investigator might find useful.

TONE: Professional, direct, and helpful. You're a trusted assistant to fraud analysts.
"""


# =============================================================================
# CASE CONTEXT CACHE
# =============================================================================

_case_context_cache: Dict[str, CaseContext] = {}


def _get_case_context(case_id: str) -> CaseContext:
    """Get case context from cache or load it."""
    if case_id not in _case_context_cache:
        assembler = CaseContextAssembler()
        _case_context_cache[case_id] = assembler.assemble(case_id)
    return _case_context_cache[case_id]


# =============================================================================
# TOOL FUNCTIONS - Called when user explicitly asks for deep analysis
# =============================================================================

def run_network_analysis(case_id: str) -> str:
    """Run network/fraud ring analysis."""
    try:
        from dataclasses import asdict
        context = _get_case_context(case_id)
        analyzer = NetworkIntelligence()
        result = analyzer.analyze(context)

        output = {
            "entities_found": len(result.entities),
            "connections_found": len(result.edges),
            "clusters_identified": len(result.clusters),
            "risk_summary": result.risk_summary,
            "recommended_investigations": result.recommended_investigations,
        }
        return json.dumps(output, indent=2)
    except Exception as e:
        logger.error(f"Network analysis failed: {e}")
        return f"Error running network analysis: {str(e)}"


def run_pattern_matching(case_id: str) -> str:
    """Find similar historical cases."""
    try:
        from dataclasses import asdict
        context = _get_case_context(case_id)
        matcher = PatternMatcher()
        result = matcher.match(context)

        output = {
            "patterns_detected": result.patterns_detected,
            "fraud_type_probabilities": result.fraud_type_probabilities,
            "top_matches": [asdict(m) for m in result.top_matches[:5]] if result.top_matches else []
        }
        return json.dumps(output, indent=2)
    except Exception as e:
        logger.error(f"Pattern matching failed: {e}")
        return f"Error running pattern matching: {str(e)}"


def run_report_generation(case_id: str) -> str:
    """Generate formal investigation report."""
    try:
        context = _get_case_context(case_id)
        generator = ReportGenerator()
        result = generator.generate(context)

        if hasattr(result, 'to_markdown'):
            return result.to_markdown()
        return json.dumps(result.to_dict(), indent=2)
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return f"Error generating report: {str(e)}"


# =============================================================================
# SENTINEL CHAT AGENT CLASS
# =============================================================================

class SentinelChatAgent:
    """
    Conversational agent for fraud investigation.

    Uses a simple but effective approach:
    1. Load case context once
    2. Inject into system prompt
    3. Use LLM to answer questions
    4. Detect when tools are needed and call them
    """

    def __init__(self, case_id: str, model: str = None):
        """
        Initialize the agent for a specific case.

        Args:
            case_id: The case to investigate
            model: Gemini model to use (defaults to GEMINI_MODEL env var)
        """
        self.case_id = case_id
        self.model = model or DEFAULT_MODEL
        self.case_context: Optional[CaseContext] = None
        self.llm = None

    def _get_llm(self):
        """Get or create the LLM instance."""
        if self.llm is None:
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment. Add it to your .env file.")

            self.llm = ChatGoogleGenerativeAI(
                model=self.model,
                temperature=0.3,
                google_api_key=api_key,
            )
        return self.llm

    def _load_context(self) -> CaseContext:
        """Load full case context (no LLM call - just data assembly)."""
        self.case_context = _get_case_context(self.case_id)
        return self.case_context

    def _format_context_for_prompt(self) -> Dict[str, Any]:
        """Format case context into prompt template variables."""
        ctx = self.case_context

        # Format alerts
        if ctx.alerts:
            alerts_formatted = "\n".join([
                f"- **[{a.severity.upper()}]** {a.alert_type}: {a.description} (Score: {a.risk_score})"
                for a in ctx.alerts
            ])
        else:
            alerts_formatted = "- No alerts on record"

        # Format KYC
        kyc = ctx.customer
        if kyc:
            declared_income_str = f"${kyc.declared_income:,.2f} {kyc.income_currency or 'USD'}" if kyc.declared_income else "Not declared"
            kyc_formatted = f"""- **Name:** {kyc.full_name}
- **Email:** {kyc.email}
- **Country:** {kyc.country}
- **Verification Status:** {kyc.verification_status}
- **Risk Rating:** {kyc.risk_rating}
- **PEP Status:** {"Yes" if kyc.pep_status else "No"}
- **Sanctions Hit:** {"Yes" if kyc.sanctions_hit else "No"}
- **Declared Income:** {declared_income_str}"""
        else:
            kyc_formatted = "- KYC data not available"

        # Format transactions (last 20)
        if ctx.transactions:
            transactions_formatted = "\n".join([
                f"- {t.timestamp[:10]} | {t.type.upper():12} | ${t.amount:>10,.2f} | {t.status} | {', '.join(t.risk_flags) if t.risk_flags else 'No flags'}"
                for t in sorted(ctx.transactions, key=lambda x: x.timestamp, reverse=True)[:20]
            ])
        else:
            transactions_formatted = "- No transactions on record"

        # Format logins (last 10)
        if ctx.logins:
            logins_formatted = "\n".join([
                f"- {l.timestamp[:16]} | {l.ip_address:15} | {l.location_country} | {'VPN' if l.is_vpn else ''} {'FAILED' if not l.login_success else 'OK'}"
                for l in sorted(ctx.logins, key=lambda x: x.timestamp, reverse=True)[:10]
            ])
        else:
            logins_formatted = "- No login history"

        # Format devices
        if ctx.devices:
            devices_formatted = "\n".join([
                f"- {d.device_id[:20]} | {d.device_type} | {d.os} | {'Trusted' if d.is_trusted else 'Untrusted'} | Linked to {len(d.linked_accounts)} accounts"
                for d in ctx.devices
            ])
        else:
            devices_formatted = "- No device data"

        # Format network connections
        if ctx.network_connections:
            network_formatted = "\n".join([
                f"- {c.connection_type}: Connected to {c.connected_entity_id} ({c.connection_strength} strength) - {c.details}"
                for c in ctx.network_connections
            ])
        else:
            network_formatted = "- No network connections detected"

        # Format prior cases
        if ctx.prior_cases:
            prior_cases_formatted = "\n".join([
                f"- {p.case_id} ({p.case_date[:10]}): {p.case_type} - **{p.outcome}**"
                for p in ctx.prior_cases
            ])
        else:
            prior_cases_formatted = "- No prior investigation cases"

        # Account data
        account = ctx.account

        return {
            "case_id": self.case_id,
            "created_at": ctx.created_at[:10] if ctx.created_at else "Unknown",
            "customer_name": kyc.full_name if kyc else "Unknown",
            "customer_id": kyc.customer_id if kyc else "Unknown",
            "account_id": account.account_id if account else "Unknown",
            "account_status": account.account_status if account else "Unknown",
            "account_age_days": account.account_age_days if account else 0,
            "total_deposits": account.total_deposits_30d if account else 0,
            "total_withdrawals": account.total_withdrawals_30d if account else 0,
            "deposit_to_income_ratio": f"{account.deposit_to_income_ratio:.1f}x" if account and account.deposit_to_income_ratio else "N/A",
            "total_trades": account.total_trades_30d if account else 0,
            "alerts_formatted": alerts_formatted,
            "kyc_formatted": kyc_formatted,
            "transactions_formatted": transactions_formatted,
            "logins_formatted": logins_formatted,
            "devices_formatted": devices_formatted,
            "network_formatted": network_formatted,
            "prior_cases_formatted": prior_cases_formatted,
        }

    def _should_run_tool(self, message: str) -> Optional[str]:
        """Check if message requires a tool call."""
        msg_lower = message.lower()

        # Network analysis triggers
        if any(phrase in msg_lower for phrase in [
            "fraud ring", "connected accounts", "network analysis",
            "shared device", "shared ip", "run network", "analyze network"
        ]):
            return "network"

        # Pattern matching triggers
        if any(phrase in msg_lower for phrase in [
            "similar cases", "historical pattern", "past cases",
            "find similar", "pattern match", "compare to history"
        ]):
            return "patterns"

        # Report generation triggers
        if any(phrase in msg_lower for phrase in [
            "generate report", "compliance report", "audit report",
            "formal report", "investigation report", "create report"
        ]):
            return "report"

        return None

    def chat(self, message: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Process user message and return response with suggestions.

        Args:
            message: User's question
            history: Conversation history as list of {"role": "user"|"assistant", "content": "..."}

        Returns:
            {
                "response": "SENTINEL's response",
                "suggested_questions": ["Follow-up 1", "Follow-up 2", ...]
            }
        """
        if history is None:
            history = []

        # Load context and build system prompt
        self._load_context()
        context_vars = self._format_context_for_prompt()
        system_prompt = SENTINEL_SYSTEM_PROMPT.format(**context_vars)

        # Check if we need to run a tool first
        tool_to_run = self._should_run_tool(message)
        tool_result = None

        if tool_to_run == "network":
            tool_result = run_network_analysis(self.case_id)
            message = f"{message}\n\n[Network Analysis Results]:\n{tool_result}"
        elif tool_to_run == "patterns":
            tool_result = run_pattern_matching(self.case_id)
            message = f"{message}\n\n[Pattern Matching Results]:\n{tool_result}"
        elif tool_to_run == "report":
            # For reports, just return the report directly
            report = run_report_generation(self.case_id)
            return {
                "response": f"Here's the investigation report:\n\n{report}",
                "suggested_questions": [
                    "What are the key risk factors?",
                    "Show me connected accounts",
                    "What should I investigate next?"
                ]
            }

        # Build messages for LLM
        messages = [SystemMessage(content=system_prompt)]

        # Add history
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        # Add current message
        messages.append(HumanMessage(content=message))

        try:
            llm = self._get_llm()
            response = llm.invoke(messages)
            response_text = response.content
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            response_text = f"I encountered an error processing your request: {str(e)}"

        # Generate suggestions
        suggested = self._generate_suggestions(message)

        return {
            "response": response_text,
            "suggested_questions": suggested,
        }

    def _generate_suggestions(self, user_msg: str) -> List[str]:
        """Generate contextual follow-up questions."""
        user_lower = user_msg.lower()

        # Base suggestions that are always relevant
        all_suggestions = [
            "What are the highest risk factors in this case?",
            "Show me the transaction timeline",
            "Are there any connected accounts or devices?",
            "Find similar historical cases",
            "What should I investigate next?",
            "Explain the login anomalies",
            "Generate a compliance report",
        ]

        # Filter out similar questions to what was asked
        filtered = []
        for q in all_suggestions:
            q_words = set(q.lower().split())
            msg_words = set(user_lower.split())
            # Keep if less than 30% word overlap
            overlap = len(q_words & msg_words) / len(q_words)
            if overlap < 0.3:
                filtered.append(q)

        return filtered[:3]


# =============================================================================
# CONVENIENCE FUNCTION - Main entry point for API
# =============================================================================

def chat_with_sentinel(
    case_id: str,
    message: str,
    history: List[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Main entry point for the chat API.

    Args:
        case_id: The case ID to investigate
        message: User's question
        history: Conversation history

    Returns:
        {
            "response": "SENTINEL's response",
            "suggested_questions": ["Follow-up 1", ...]
        }
    """
    if history is None:
        history = []

    agent = SentinelChatAgent(case_id)
    return agent.chat(message, history)


def clear_context_cache():
    """Clear the case context cache."""
    global _case_context_cache
    _case_context_cache.clear()
