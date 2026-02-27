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
        """Format case context into prompt template variables (updated for new ML output schema)."""
        ctx = self.case_context

        # Format alerts - using new schema fields: signal, severity, confidence, evidence
        if ctx.alerts:
            alerts_list = []
            for a in ctx.alerts:
                # Get first evidence explanation or use signal as description
                description = a.signal
                if a.evidence and len(a.evidence) > 0:
                    description = a.evidence[0].explanation or a.signal
                alerts_list.append(
                    f"- **[{a.severity.upper()}]** {a.signal}: {description} (Confidence: {a.confidence})"
                )
            alerts_formatted = "\n".join(alerts_list)
        else:
            alerts_formatted = "- No alerts on record"

        # Format KYC - using new schema: profile.kyc, profile.risk
        profile = ctx.profile
        if profile and profile.kyc:
            kyc = profile.kyc
            risk = profile.risk
            try:
                income_val = float(kyc.income) if kyc.income else 0
                declared_income_str = f"${income_val:,.2f} USD" if income_val > 0 else "Not declared"
            except (ValueError, TypeError):
                declared_income_str = str(kyc.income) if kyc.income else "Not declared"

            kyc_formatted = f"""- **User ID:** {profile.user_id}
- **Country:** {kyc.residence_country or kyc.nationality or 'Unknown'}
- **Nationality:** {kyc.nationality or 'Unknown'}
- **KYC Level:** {kyc.kyc_level or 'Unknown'}
- **Occupation:** {kyc.occupation or 'Unknown'}
- **Risk Tier:** {risk.risk_tier if risk else 'Unknown'}
- **PEP Status:** {"Yes" if risk and risk.pep_flag else "No"}
- **Sanctions Status:** {risk.sanctions_status if risk else 'Clear'}
- **Declared Income:** {declared_income_str}
- **Source of Funds:** {kyc.source_of_funds or 'Not specified'}"""
        else:
            kyc_formatted = "- KYC data not available"

        # Format transactions (last 20) - using new schema: event_time, event_type, data.amount
        if ctx.transactions:
            txn_list = []
            for t in sorted(ctx.transactions, key=lambda x: x.event_time, reverse=True)[:20]:
                amount = t.data.amount if t.data else 0
                result = t.data.result if t.data else "unknown"
                stock_id = t.data.stock_id if t.data else ""
                stock_info = f" [{stock_id}]" if stock_id else ""
                txn_list.append(
                    f"- {t.event_time[:10]} | {t.event_type.upper():12} | ${amount:>10,.2f} | {result}{stock_info}"
                )
            transactions_formatted = "\n".join(txn_list)
        else:
            transactions_formatted = "- No transactions on record"

        # Format logins (last 10) - using new schema: event_time, ip, data.geo, data.success
        if ctx.logins:
            login_list = []
            for l in sorted(ctx.logins, key=lambda x: x.event_time, reverse=True)[:10]:
                country = l.data.geo.country if l.data and l.data.geo else "Unknown"
                success = l.data.success if l.data else True
                method = l.data.method if l.data else "unknown"
                status = "OK" if success else "FAILED"
                login_list.append(
                    f"- {l.event_time[:16]} | {l.ip:15} | {country} | {method} | {status}"
                )
            logins_formatted = "\n".join(login_list)
        else:
            logins_formatted = "- No login history"

        # Format devices from network events - extract unique devices
        unique_devices = {}
        for n in ctx.network_events:
            if n.device_id and n.device_id not in unique_devices:
                vpn = "VPN suspected" if n.data and n.data.vpn_suspected else "Clean"
                unique_devices[n.device_id] = f"- {n.device_id[:20]} | IP: {n.ip} | {vpn}"
        devices_formatted = "\n".join(unique_devices.values()) if unique_devices else "- No device data"

        # Format network events (VPN, geo anomalies)
        if ctx.network_events:
            network_list = []
            for n in ctx.network_events[:10]:
                vpn = "VPN DETECTED" if n.data and n.data.vpn_suspected else ""
                country = n.data.geo.country if n.data and n.data.geo else "Unknown"
                rtt = n.data.rtt_ms_p95 if n.data else 0
                network_list.append(
                    f"- {n.event_time[:16]} | {n.ip:15} | {country} | RTT: {rtt}ms | {vpn}"
                )
            network_formatted = "\n".join(network_list)
        else:
            network_formatted = "- No network events recorded"

        # Prior cases - not in new schema, show as N/A
        prior_cases_formatted = "- No prior investigation cases in current data"

        # Account and status data
        account = profile.account if profile else None
        status = ctx.status

        # Calculate deposits/withdrawals from status
        total_deposits = status.txn.amount_in_30d if status and status.txn else 0
        total_withdrawals = status.txn.amount_out_30d if status and status.txn else 0
        total_trades = status.txn.count_1d if status and status.txn else 0

        # Calculate deposit to income ratio
        try:
            income = float(profile.kyc.income) if profile and profile.kyc and profile.kyc.income else 0
            if income > 0 and total_deposits > 0:
                deposit_ratio = f"{total_deposits / income:.1f}x"
            else:
                deposit_ratio = "N/A"
        except (ValueError, TypeError):
            deposit_ratio = "N/A"

        return {
            "case_id": self.case_id,
            "created_at": ctx.case_info.opened_at[:10] if ctx.case_info and ctx.case_info.opened_at else "Unknown",
            "customer_name": ctx.user_id,
            "customer_id": ctx.user_id,
            "account_id": account.account_id if account else ctx.user_id,
            "account_status": account.account_status if account else (profile.account_status if profile else "Unknown"),
            "account_age_days": 0,  # Not available in new schema
            "total_deposits": total_deposits,
            "total_withdrawals": total_withdrawals,
            "deposit_to_income_ratio": deposit_ratio,
            "total_trades": total_trades,
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
