"""
Case Context Assembler - Updated for New ML Output Schema
=========================================================
Aggregates all relevant data from ML output JSON files into a single,
coherent case view for the AI Agent to investigate.

Data source: django/api/dummy_data/
- cases.json (array of cases with embedded alerts)
- profile.json (user KYC and account data)
- transactional_json (buy/sell transactions)
- auth.json (login events)
- network.json (network health/VPN detection)
- status.json (aggregated metrics)
- alert.json (standalone alerts - optional)
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path


# Path to Django's dummy data
DUMMY_DATA_PATH = Path(__file__).parent.parent.parent / "api" / "dummy_data"


# =============================================================================
# DATA CLASSES - Matching new ML output schema
# =============================================================================

@dataclass
class Evidence:
    """SHAP-style evidence from ML model"""
    risk_category: str = ""
    feature: str = ""
    impact: str = ""
    contribution: float = 0.0
    value: float = None
    explanation: str = ""


@dataclass
class AlertInfo:
    """Alert from ML detection system"""
    alert_id: str = ""
    event_time: str = ""
    txn_id: str = ""
    user_id: str = ""
    is_anomaly: int = 0
    detector_type: str = ""  # RULE_BASED, BEHAVIOR, GRAPH RISK
    signal: str = ""         # Monetary Deviation, Liquidity Shift, Multi-Accounting
    severity: str = ""       # LOW, MED, HIGH
    confidence: str = ""
    evidence: List[Evidence] = field(default_factory=list)


@dataclass
class AccountData:
    """Account information from profile"""
    account_id: str = ""
    account_status: str = ""
    account_deposit: str = "0"


@dataclass
class KYCData:
    """KYC information from profile"""
    kyc_level: str = ""
    verified_at: str = ""
    nationality: str = ""
    residence_country: str = ""
    age: str = ""
    occupation: str = ""
    income: str = "0"
    source_of_funds: str = ""


@dataclass
class RiskData:
    """Risk flags from profile"""
    risk_tier: str = ""
    pep_flag: bool = False
    sanctions_status: str = "false"
    adverse_media_flag: bool = False


@dataclass
class VerificationData:
    """Verification status from profile"""
    email_verified: bool = False
    phone_verified: bool = False


@dataclass
class Profile:
    """Complete user profile"""
    user_id: str = ""
    username: str = ""
    created_at: str = ""
    account_status: str = ""
    account: AccountData = field(default_factory=AccountData)
    kyc: KYCData = field(default_factory=KYCData)
    risk: RiskData = field(default_factory=RiskData)
    verification: VerificationData = field(default_factory=VerificationData)


@dataclass
class TransactionData:
    """Nested data in transaction"""
    txn_id: str = ""
    amount: float = 0.0
    currency: str = "USD"
    channel: str = ""
    result: str = ""
    stock_id: str = ""


@dataclass
class Transaction:
    """Transaction event"""
    event_id: str = ""
    event_time: str = ""
    stream_type: str = ""
    event_type: str = ""  # buy, sell, deposit, withdrawal
    user_id: str = ""
    account_id: str = ""
    session_id: str = ""
    device_id: str = ""
    ip: str = ""
    data: TransactionData = field(default_factory=TransactionData)


@dataclass
class GeoData:
    """Geographic location"""
    country: str = ""
    city: str = ""


@dataclass
class AuthEventData:
    """Nested data in auth event"""
    method: str = ""
    mfa_used: bool = False
    success: bool = True
    failure_reason: str = ""
    risk_hint: str = ""
    user_agent: str = ""
    geo: GeoData = field(default_factory=GeoData)


@dataclass
class LoginEvent:
    """Login/auth event"""
    event_id: str = ""
    event_time: str = ""
    stream_type: str = ""
    event_type: str = ""
    user_id: str = ""
    account_id: str = ""
    session_id: str = ""
    device_id: str = ""
    ip: str = ""
    data: AuthEventData = field(default_factory=AuthEventData)


@dataclass
class NetworkEventData:
    """Nested data in network event"""
    rtt_ms_p95: int = 0
    packet_loss_pct: float = 0.0
    jitter_ms_p95: int = 0
    asn: int = 0
    vpn_suspected: bool = False
    geo: GeoData = field(default_factory=GeoData)


@dataclass
class NetworkEvent:
    """Network session event"""
    event_id: str = ""
    event_time: str = ""
    stream_type: str = ""
    event_type: str = ""
    user_id: str = ""
    account_id: str = ""
    session_id: str = ""
    device_id: str = ""
    ip: str = ""
    data: NetworkEventData = field(default_factory=NetworkEventData)


@dataclass
class TxnStatus:
    """Transaction aggregations"""
    count_5m: int = 0
    count_1h: int = 0
    count_1d: int = 0
    amount_in_5m: float = 0.0
    amount_in_1h: float = 0.0
    amount_in_1d: float = 0.0
    amount_in_30d: float = 0.0
    amount_out_5m: float = 0.0
    amount_out_1h: float = 0.0
    amount_out_1d: float = 0.0
    amount_out_30d: float = 0.0


@dataclass
class AuthStatus:
    """Auth aggregations"""
    login_count_1h: int = 0
    failed_login_5m: int = 0
    failed_login_1h: int = 0
    new_device_1d: int = 0
    new_ip_1d: int = 0
    last_login_ts: str = ""


@dataclass
class NetworkStatus:
    """Network aggregations"""
    unique_ip_5m: int = 0
    geo_change_1d: int = 0
    rtt_p95_5m: float = 0.0
    packet_loss_5m: float = 0.0


@dataclass
class StatusAggregation:
    """Aggregated status metrics"""
    user_id: str = ""
    as_of: str = ""
    txn: TxnStatus = field(default_factory=TxnStatus)
    auth: AuthStatus = field(default_factory=AuthStatus)
    network: NetworkStatus = field(default_factory=NetworkStatus)


@dataclass
class CaseInfo:
    """Case metadata"""
    case_id: str = ""
    user_id: str = ""
    status: str = ""
    opened_at: str = ""
    last_updated: str = ""
    case_score: int = 0
    risk_level: str = ""
    alerts: List[AlertInfo] = field(default_factory=list)


@dataclass
class DataCompleteness:
    """Which data sources were available"""
    case_data: bool = False
    profile: bool = False
    transactions: bool = False
    logins: bool = False
    network_events: bool = False
    status: bool = False
    alerts: bool = False


@dataclass
class CaseContext:
    """Complete case context for fraud investigation"""
    case_id: str = ""
    user_id: str = ""
    assembled_at: str = ""
    case_info: CaseInfo = field(default_factory=CaseInfo)
    profile: Profile = field(default_factory=Profile)
    transactions: List[Transaction] = field(default_factory=list)
    logins: List[LoginEvent] = field(default_factory=list)
    network_events: List[NetworkEvent] = field(default_factory=list)
    status: StatusAggregation = field(default_factory=StatusAggregation)
    alerts: List[AlertInfo] = field(default_factory=list)
    data_completeness: DataCompleteness = field(default_factory=DataCompleteness)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, default=str)


# =============================================================================
# ASSEMBLER CLASS
# =============================================================================

class CaseContextAssembler:
    """
    Assembles case context from Django's ML output JSON files.

    Updated to use new file structure:
    - cases.json (array)
    - profile.json (array)
    - transactional_json (array)
    - auth.json (array)
    - network.json (single object or array)
    - status.json (array)
    - alert.json (array)
    """

    def __init__(self, data_path: Path = None):
        self.data_path = data_path or DUMMY_DATA_PATH
        self._cache: Dict[str, Any] = {}

    def _load_json(self, filename: str) -> Any:
        """Load and cache a JSON file"""
        if filename not in self._cache:
            file_path = self.data_path / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self._cache[filename] = json.load(f)
            else:
                print(f"[Warning] File not found: {file_path}")
                self._cache[filename] = []
        return self._cache[filename]

    def _ensure_list(self, data: Any) -> List:
        """Ensure data is a list"""
        if data is None:
            return []
        if isinstance(data, list):
            return data
        return [data]

    def _find_by_id(self, data: List[Dict], id_field: str, id_value: str) -> Optional[Dict]:
        """Find a single item by ID field"""
        for item in self._ensure_list(data):
            if item.get(id_field) == id_value:
                return item
        return None

    def _filter_by(self, data: List[Dict], **filters) -> List[Dict]:
        """Filter data by multiple field values"""
        results = []
        for item in self._ensure_list(data):
            match = all(item.get(k) == v for k, v in filters.items())
            if match:
                results.append(item)
        return results

    def _parse_evidence(self, ev_data: Dict) -> Evidence:
        """Parse evidence dict to Evidence dataclass"""
        return Evidence(
            risk_category=ev_data.get("risk_category", ""),
            feature=ev_data.get("feature", ""),
            impact=ev_data.get("impact", ""),
            contribution=ev_data.get("contribution", 0.0),
            value=ev_data.get("value"),
            explanation=ev_data.get("explanation", "")
        )

    def _parse_alert(self, alert_data: Dict) -> AlertInfo:
        """Parse alert dict to AlertInfo dataclass"""
        evidence_list = [
            self._parse_evidence(ev)
            for ev in alert_data.get("evidence", [])
        ]
        return AlertInfo(
            alert_id=alert_data.get("alert_id", ""),
            event_time=alert_data.get("event_time", ""),
            txn_id=alert_data.get("txn_id", ""),
            user_id=alert_data.get("user_id", ""),
            is_anomaly=alert_data.get("is_anomaly", 0),
            detector_type=alert_data.get("detector_type", ""),
            signal=alert_data.get("signal", ""),
            severity=alert_data.get("severity", ""),
            confidence=str(alert_data.get("confidence", "")),
            evidence=evidence_list
        )

    def _parse_profile(self, profile_data: Dict) -> Profile:
        """Parse profile dict to Profile dataclass"""
        account_data = profile_data.get("account", {})
        kyc_data = profile_data.get("kyc", {})
        risk_data = profile_data.get("risk", {})
        verification_data = profile_data.get("verification", {})

        return Profile(
            user_id=profile_data.get("user_id", ""),
            username=profile_data.get("username", ""),
            created_at=profile_data.get("created_at", ""),
            account_status=profile_data.get("account_status", ""),
            account=AccountData(
                account_id=account_data.get("account_id", ""),
                account_status=account_data.get("account_status", ""),
                account_deposit=str(account_data.get("account_deposit", "0"))
            ),
            kyc=KYCData(
                kyc_level=kyc_data.get("kyc_level", ""),
                verified_at=kyc_data.get("verified_at", ""),
                nationality=kyc_data.get("nationality", ""),
                residence_country=kyc_data.get("residence_country", ""),
                age=str(kyc_data.get("age", "")),
                occupation=kyc_data.get("occupation", ""),
                income=str(kyc_data.get("income", "0")),
                source_of_funds=kyc_data.get("source_of_funds", "")
            ),
            risk=RiskData(
                risk_tier=risk_data.get("risk_tier", ""),
                pep_flag=risk_data.get("pep_flag", False),
                sanctions_status=str(risk_data.get("sanctions_status", "false")),
                adverse_media_flag=risk_data.get("adverse_media_flag", False)
            ),
            verification=VerificationData(
                email_verified=verification_data.get("email_verified", False),
                phone_verified=verification_data.get("phone_verified", False)
            )
        )

    def _parse_transaction(self, txn_data: Dict) -> Transaction:
        """Parse transaction dict to Transaction dataclass"""
        data = txn_data.get("data", {})
        return Transaction(
            event_id=txn_data.get("event_id", ""),
            event_time=txn_data.get("event_time", ""),
            stream_type=txn_data.get("stream_type", ""),
            event_type=txn_data.get("event_type", ""),
            user_id=txn_data.get("user_id", ""),
            account_id=txn_data.get("account_id", ""),
            session_id=txn_data.get("session_id", ""),
            device_id=txn_data.get("device_id", ""),
            ip=txn_data.get("ip", ""),
            data=TransactionData(
                txn_id=data.get("txn_id", ""),
                amount=data.get("amount", 0.0),
                currency=data.get("currency", "USD"),
                channel=data.get("channel", ""),
                result=data.get("result", ""),
                stock_id=data.get("stock_id", "")
            )
        )

    def _parse_login(self, login_data: Dict) -> LoginEvent:
        """Parse login dict to LoginEvent dataclass"""
        data = login_data.get("data", {})
        geo = data.get("geo", {})
        return LoginEvent(
            event_id=login_data.get("event_id", ""),
            event_time=login_data.get("event_time", ""),
            stream_type=login_data.get("stream_type", ""),
            event_type=login_data.get("event_type", ""),
            user_id=login_data.get("user_id", ""),
            account_id=login_data.get("account_id", ""),
            session_id=login_data.get("session_id", ""),
            device_id=login_data.get("device_id", ""),
            ip=login_data.get("ip", ""),
            data=AuthEventData(
                method=data.get("method", ""),
                mfa_used=data.get("mfa_used", False),
                success=data.get("success", True),
                failure_reason=data.get("failure_reason", ""),
                risk_hint=data.get("risk_hint", ""),
                user_agent=data.get("user_agent", ""),
                geo=GeoData(
                    country=geo.get("country", ""),
                    city=geo.get("city", "")
                )
            )
        )

    def _parse_network_event(self, net_data: Dict) -> NetworkEvent:
        """Parse network event dict to NetworkEvent dataclass"""
        data = net_data.get("data", {})
        geo = data.get("geo", {})
        return NetworkEvent(
            event_id=net_data.get("event_id", ""),
            event_time=net_data.get("event_time", ""),
            stream_type=net_data.get("stream_type", ""),
            event_type=net_data.get("event_type", ""),
            user_id=net_data.get("user_id", ""),
            account_id=net_data.get("account_id", ""),
            session_id=net_data.get("session_id", ""),
            device_id=net_data.get("device_id", ""),
            ip=net_data.get("ip", ""),
            data=NetworkEventData(
                rtt_ms_p95=data.get("rtt_ms_p95", 0),
                packet_loss_pct=data.get("packet_loss_pct", 0.0),
                jitter_ms_p95=data.get("jitter_ms_p95", 0),
                asn=data.get("asn", 0),
                vpn_suspected=data.get("vpn_suspected", False),
                geo=GeoData(
                    country=geo.get("country", ""),
                    city=geo.get("city", "")
                )
            )
        )

    def _parse_status(self, status_data: Dict) -> StatusAggregation:
        """Parse status dict to StatusAggregation dataclass"""
        txn = status_data.get("txn", {})
        auth = status_data.get("auth", {})
        network = status_data.get("network", {})

        return StatusAggregation(
            user_id=status_data.get("user_id", ""),
            as_of=status_data.get("as_of", ""),
            txn=TxnStatus(
                count_5m=txn.get("count_5m", 0),
                count_1h=txn.get("count_1h", 0),
                count_1d=txn.get("count_1d", 0),
                amount_in_5m=txn.get("amount_in_5m", 0.0),
                amount_in_1h=txn.get("amount_in_1h", 0.0),
                amount_in_1d=txn.get("amount_in_1d", 0.0),
                amount_in_30d=txn.get("amount_in_30d", 0.0),
                amount_out_5m=txn.get("amount_out_5m", 0.0),
                amount_out_1h=txn.get("amount_out_1h", 0.0),
                amount_out_1d=txn.get("amount_out_1d", 0.0),
                amount_out_30d=txn.get("amount_out_30d", 0.0)
            ),
            auth=AuthStatus(
                login_count_1h=auth.get("login_count_1h", 0),
                failed_login_5m=auth.get("failed_login_5m", 0),
                failed_login_1h=auth.get("failed_login_1h", 0),
                new_device_1d=auth.get("new_device_1d", 0),
                new_ip_1d=auth.get("new_ip_1d", 0),
                last_login_ts=auth.get("last_login_ts", "")
            ),
            network=NetworkStatus(
                unique_ip_5m=network.get("unique_ip_5m", 0),
                geo_change_1d=network.get("geo_change_1d", 0),
                rtt_p95_5m=network.get("rtt_p95_5m", 0.0),
                packet_loss_5m=network.get("packet_loss_5m", 0.0)
            )
        )

    def assemble(self, case_id: str) -> CaseContext:
        """
        Assemble complete case context for the given case ID.

        Args:
            case_id: The case ID to assemble context for

        Returns:
            CaseContext with all relevant data assembled

        Raises:
            ValueError: If case not found
        """
        # Load all data files with NEW filenames
        cases = self._load_json("cases.json")
        profiles = self._load_json("profile.json")
        transactions = self._load_json("transactional_json")
        logins = self._load_json("auth.json")
        network_events = self._load_json("network.json")
        statuses = self._load_json("status.json")
        alerts = self._load_json("alert.json")

        # Find the case
        case_data = self._find_by_id(cases, "case_id", case_id)
        if not case_data:
            raise ValueError(f"Case not found: {case_id}")

        user_id = case_data.get("user_id", "")

        # Parse case alerts (embedded in case or from alert.json)
        case_alerts = case_data.get("alerts", [])
        if not case_alerts:
            # Fall back to alert.json filtered by user_id
            case_alerts = self._filter_by(alerts, user_id=user_id)

        alert_list = [self._parse_alert(a) for a in case_alerts]

        # Build CaseInfo
        case_info = CaseInfo(
            case_id=case_data.get("case_id", ""),
            user_id=user_id,
            status=case_data.get("status", ""),
            opened_at=case_data.get("opened_at", ""),
            last_updated=case_data.get("last_updated", ""),
            case_score=case_data.get("case_score", 0),
            risk_level=case_data.get("risk_level", ""),
            alerts=alert_list
        )

        # Get profile for this user
        profile_data = self._find_by_id(profiles, "user_id", user_id)
        profile = self._parse_profile(profile_data) if profile_data else Profile(user_id=user_id)

        # Get transactions for this user
        user_transactions = self._filter_by(transactions, user_id=user_id)
        txn_list = [self._parse_transaction(t) for t in user_transactions]

        # Get logins for this user
        user_logins = self._filter_by(logins, user_id=user_id)
        login_list = [self._parse_login(l) for l in user_logins]

        # Get network events for this user
        network_list_raw = self._ensure_list(network_events)
        user_network = self._filter_by(network_list_raw, user_id=user_id)
        network_list = [self._parse_network_event(n) for n in user_network]

        # Get status aggregation for this user
        status_data = self._find_by_id(statuses, "user_id", user_id)
        status = self._parse_status(status_data) if status_data else StatusAggregation(user_id=user_id)

        # Build data completeness
        data_completeness = DataCompleteness(
            case_data=True,
            profile=profile_data is not None,
            transactions=len(txn_list) > 0,
            logins=len(login_list) > 0,
            network_events=len(network_list) > 0,
            status=status_data is not None,
            alerts=len(alert_list) > 0
        )

        # Assemble final CaseContext
        return CaseContext(
            case_id=case_id,
            user_id=user_id,
            assembled_at=datetime.now(timezone.utc).isoformat() + "Z",
            case_info=case_info,
            profile=profile,
            transactions=txn_list,
            logins=login_list,
            network_events=network_list,
            status=status,
            alerts=alert_list,
            data_completeness=data_completeness
        )

    def clear_cache(self):
        """Clear the data cache"""
        self._cache.clear()


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def assemble_case_context(case_id: str, data_path: Path = None) -> CaseContext:
    """
    Convenience function to assemble case context.

    Args:
        case_id: The case ID to assemble
        data_path: Optional path to data directory

    Returns:
        Assembled CaseContext
    """
    assembler = CaseContextAssembler(data_path)
    return assembler.assemble(case_id)


# =============================================================================
# DEMO / TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Case Context Assembler - Testing with new ML output")
    print("=" * 60)

    try:
        context = assemble_case_context("CASE-20260207-0001")
        print(f"\nCase ID: {context.case_id}")
        print(f"User ID: {context.user_id}")
        print(f"Risk Level: {context.case_info.risk_level}")
        print(f"Case Score: {context.case_info.case_score}")
        print(f"\nAlerts: {len(context.alerts)}")
        for alert in context.alerts[:3]:
            print(f"  - [{alert.severity}] {alert.signal}: {alert.detector_type}")
        print(f"\nProfile: {context.profile.kyc.occupation}")
        print(f"Transactions: {len(context.transactions)}")
        print(f"Logins: {len(context.logins)}")
        print(f"\nData Completeness: {context.data_completeness}")
        print("\n" + "=" * 60)
        print("SUCCESS!")
    except Exception as e:
        print(f"ERROR: {e}")
