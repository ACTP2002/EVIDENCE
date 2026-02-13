"""
Aggregates all relevant data (transactions, logins, devices, KYC, history)
into a single, coherent case view that matches the CaseContext schema.

This skill reads from ML pipeline output (ml_data/) and assembles
them into a unified CaseContext object for the AI Agent to investigate.

Updated to support ML pipeline data structure:
- output/: cases.json, alerts.json
- input/: profiles.json, transactions_raw.json, auth_events.json, network_events.json
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path


# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# Path to ML data directory (configurable via FRAUD_DATA_DIR env var)
def _get_data_path() -> Path:
    """Get the data path from environment or default."""
    data_dir = os.getenv('FRAUD_DATA_DIR', 'api/ml_data')
    # Handle both absolute and relative paths
    if os.path.isabs(data_dir):
        return Path(data_dir)
    # Relative to Django project root
    return Path(__file__).parent.parent.parent / data_dir


ML_DATA_PATH = _get_data_path()


@dataclass
class AlertInfo:
    """What triggered this case to be created."""
    alert_id: str
    alert_type: str  # e.g., ATO, money_laundering, identity_fraud
    triggered_at: str  # ISO datetime string
    severity: str  # low, medium, high, critical
    risk_score: int  # 0-100
    description: str
    detector_source: str
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    raw_signal_refs: List[str] = field(default_factory=list)


@dataclass
class Transaction:
    """A single financial transaction."""
    transaction_id: str
    timestamp: str
    type: str  # deposit, withdrawal, trade, transfer
    amount: float
    currency: str
    status: str  # completed, pending, failed, reversed, blocked
    channel: str  # bank_transfer, card, crypto, ewallet, platform
    counterparty: Optional[str] = None
    risk_flags: List[str] = field(default_factory=list)


@dataclass
class LoginEvent:
    """A single login/authentication event."""
    event_id: str
    timestamp: str
    ip_address: str
    device_id: str
    device_type: str  # mobile, desktop, tablet
    location_country: str
    is_vpn: bool
    is_proxy: bool
    login_success: bool
    risk_flags: List[str] = field(default_factory=list)
    browser: Optional[str] = None
    location_city: Optional[str] = None
    failure_reason: Optional[str] = None


@dataclass
class DeviceInfo:
    """Information about a device used by the customer."""
    device_id: str
    device_type: str
    os: str
    first_seen: str
    last_seen: str
    is_trusted: bool
    linked_accounts: List[str] = field(default_factory=list)


@dataclass
class KYCData:
    """Know Your Customer - Identity verification data."""
    customer_id: str
    full_name: str
    email: str
    phone: str
    country: str
    verification_status: str  # verified, pending, failed, expired
    verification_method: str  # document, biometric, video
    risk_rating: str  # low, medium, high
    pep_status: bool  # Politically Exposed Person
    sanctions_hit: bool
    adverse_media: bool
    document_verified: bool
    document_flags: List[str] = field(default_factory=list)
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    verification_date: Optional[str] = None
    declared_income: Optional[float] = None
    income_currency: Optional[str] = None
    employment_status: Optional[str] = None
    document_type: Optional[str] = None
    document_country: Optional[str] = None


@dataclass
class AccountSummary:
    """Summary of the account status and activity."""
    account_id: str
    account_type: str  # trading, wallet, savings
    account_status: str  # active, suspended, closed, under_review, pending_verification
    created_at: str
    total_deposits_30d: float
    total_withdrawals_30d: float
    total_trades_30d: int
    average_transaction_amount: float
    account_age_days: int
    is_dormant_reactivated: bool
    customer_id: str
    deposit_to_income_ratio: Optional[float] = None


@dataclass
class NetworkConnection:
    """Links to other accounts/entities (for fraud ring detection)."""
    connection_type: str  # shared_device, shared_ip, shared_phone, same_document
    connected_entity_id: str
    connection_strength: str  # strong, medium, weak
    first_observed: str
    details: str


@dataclass
class PriorCase:
    """Previous investigation cases for this customer."""
    case_id: str
    case_date: str
    case_type: str
    outcome: str  # confirmed_fraud, false_positive, inconclusive
    resolution_notes: Optional[str] = None


@dataclass
class DataCompleteness:
    """Which data sources were available."""
    kyc_data: bool
    transaction_history: bool
    login_history: bool
    device_data: bool
    network_analysis: bool
    prior_cases: bool


@dataclass
class CaseContext:
    """Complete case context for fraud investigation."""
    case_id: str
    created_at: str
    assembled_at: str
    alerts: List[AlertInfo]
    customer: KYCData
    account: AccountSummary
    transactions: List[Transaction]
    logins: List[LoginEvent]
    devices: List[DeviceInfo]
    network_connections: List[NetworkConnection]
    prior_cases: List[PriorCase]
    data_completeness: DataCompleteness

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)


class CaseContextAssembler:
    """
    Assembles case context from ML pipeline data files.

    This class reads from the ml_data directory structure:
    - output/: cases.json, alerts.json (ML pipeline results)
    - input/: profiles.json, transactions_raw.json, auth_events.json, network_events.json

    It transforms these into the unified CaseContext schema for AI investigation.
    """

    def __init__(self, data_path: Path = None):
        """
        Initialize the assembler.

        Args:
            data_path: Path to the ml_data directory. Defaults to FRAUD_DATA_DIR env var.
        """
        self.data_path = data_path or ML_DATA_PATH
        self.input_path = self.data_path / "input"
        self.output_path = self.data_path / "output"
        self._cache: Dict[str, List[Dict]] = {}

    def _load_json(self, filename: str, subdir: str = None) -> List[Dict[str, Any]]:
        """Load and cache a JSON file."""
        cache_key = f"{subdir}/{filename}" if subdir else filename

        if cache_key not in self._cache:
            if subdir:
                file_path = self.data_path / subdir / filename
            else:
                file_path = self.data_path / filename

            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self._cache[cache_key] = json.load(f)
            else:
                self._cache[cache_key] = []
        return self._cache[cache_key]

    def _find_by_id(self, data: List[Dict], id_field: str, id_value: str) -> Optional[Dict]:
        """Find a single item by ID field."""
        for item in data:
            item_id = item.get(id_field)
            # Handle cases where id_field can be a list (fraud rings have user_id as list)
            if isinstance(item_id, list):
                if id_value in item_id:
                    return item
            elif item_id == id_value:
                return item
        return None

    def _filter_by(self, data: List[Dict], **filters) -> List[Dict]:
        """Filter data by multiple field values."""
        results = []
        for item in data:
            match = all(item.get(k) == v for k, v in filters.items())
            if match:
                results.append(item)
        return results

    def _filter_by_account_or_user(self, data: List[Dict], account_id: str = None, user_id: str = None) -> List[Dict]:
        """Filter data by account_id or user_id (whichever matches)."""
        results = []
        for item in data:
            if account_id and item.get("account_id") == account_id:
                results.append(item)
            elif user_id and item.get("user_id") == user_id:
                results.append(item)
        return results

    # =========================================================================
    # SCHEMA ADAPTERS - Transform ML data to CaseContext schema
    # =========================================================================

    def _load_cases(self) -> List[Dict[str, Any]]:
        """Load cases from ML pipeline output."""
        return self._load_json("cases.json", subdir="output")

    def _load_alerts(self) -> List[Dict[str, Any]]:
        """Load and transform alerts from ML pipeline output."""
        raw_alerts = self._load_json("alerts.json", subdir="output")

        transformed = []
        for a in raw_alerts:
            transformed.append({
                "alert_id": a.get("alert_id", ""),
                "alert_type": a.get("detector_type", a.get("fraud_type_inferred", "")),
                "triggered_at": a.get("event_time", a.get("created_at", "")),
                "severity": a.get("severity", "medium").lower(),
                "risk_score": int(a.get("confidence", 0) * 100),
                "description": f"{a.get('signal', 'Anomaly detected')} - {a.get('fraud_type_inferred', 'unknown')}",
                "detector_source": a.get("detector_source", "ml_pipeline"),
                "evidence": [a.get("evidence", {})] if a.get("evidence") else [],
                "raw_signal_refs": [str(a.get("txn_id", ""))] if a.get("txn_id") else [],
                # Keep original fields for lookups
                "user_id": a.get("user_id"),
                "account_id": a.get("account_id"),
            })
        return transformed

    def _load_customers(self) -> List[Dict[str, Any]]:
        """Transform profiles.json to customers schema."""
        profiles = self._load_json("profiles.json", subdir="input")

        transformed = []
        for p in profiles:
            user_id = p.get("user_id", "")
            country = p.get("residence_country", "").upper()

            transformed.append({
                "customer_id": user_id,
                "full_name": f"Customer {user_id}",  # Placeholder - ML data doesn't have names
                "email": f"{user_id.lower().replace('-', '.')}@example.com",  # Placeholder
                "phone": "+1-XXX-XXX-XXXX",  # Placeholder
                "country": country,
                "verification_status": "verified",  # Default assumption
                "verification_method": "document",
                "risk_rating": "medium",  # Default
                "pep_status": False,
                "sanctions_hit": False,
                "adverse_media": False,
                "document_verified": True,
                "document_flags": [],
                "declared_income": p.get("declared_income"),
                "income_currency": "USD",
                "accounts": p.get("accounts", []),
            })
        return transformed

    def _load_accounts(self) -> List[Dict[str, Any]]:
        """Derive accounts from profiles.json."""
        profiles = self._load_json("profiles.json", subdir="input")
        transactions = self._load_json("transactions_raw.json", subdir="input")

        accounts = []
        for p in profiles:
            user_id = p.get("user_id", "")
            account_ids = p.get("accounts", [])
            account_deposit = p.get("account_deposit", 0)

            for acc_id in account_ids:
                # Calculate activity from transactions
                acc_txns = [t for t in transactions if t.get("account_id") == acc_id]

                deposits = sum(t.get("amount", 0) for t in acc_txns
                             if t.get("event_type") in ["deposit"])
                withdrawals = sum(t.get("amount", 0) for t in acc_txns
                                if t.get("event_type") in ["withdrawal"])
                trades = len([t for t in acc_txns if t.get("event_type") in ["buy", "sell"]])

                avg_amount = sum(t.get("amount", 0) for t in acc_txns) / len(acc_txns) if acc_txns else 0

                # Calculate deposit to income ratio
                declared_income = p.get("declared_income", 0)
                deposit_ratio = deposits / declared_income if declared_income > 0 else None

                accounts.append({
                    "account_id": acc_id,
                    "customer_id": user_id,
                    "account_type": "trading",
                    "account_status": "active",
                    "created_at": "2025-01-01T00:00:00Z",  # Placeholder
                    "total_deposits_30d": deposits,
                    "total_withdrawals_30d": withdrawals,
                    "total_trades_30d": trades,
                    "average_transaction_amount": round(avg_amount, 2),
                    "account_age_days": 365,  # Placeholder
                    "is_dormant_reactivated": False,
                    "deposit_to_income_ratio": round(deposit_ratio, 2) if deposit_ratio else None,
                    "account_deposit": account_deposit,
                })
        return accounts

    def _load_transactions(self) -> List[Dict[str, Any]]:
        """Transform transactions_raw.json to transactions schema."""
        raw_txns = self._load_json("transactions_raw.json", subdir="input")

        # Map event_type to standard types
        type_map = {
            "deposit": "deposit",
            "withdrawal": "withdrawal",
            "buy": "trade",
            "sell": "trade",
            "transfer": "transfer",
        }

        transformed = []
        for t in raw_txns:
            event_type = t.get("event_type", "").lower()
            transformed.append({
                "transaction_id": str(t.get("txn_id", "")),
                "timestamp": t.get("event_time", ""),
                "type": type_map.get(event_type, event_type),
                "amount": t.get("amount", 0),
                "currency": t.get("currency", "USD").upper(),
                "status": "completed",  # Assume completed
                "channel": t.get("channel", "unknown"),
                "counterparty": None,
                "risk_flags": [],
                # Keep original fields for filtering
                "account_id": t.get("account_id"),
                "user_id": t.get("user_id"),
                "device_id": t.get("device_id"),
                "ip_address": t.get("ip_address"),
                "transaction_country": t.get("transaction_country"),
            })
        return transformed

    def _load_logins(self) -> List[Dict[str, Any]]:
        """Transform auth_events.json to logins schema."""
        auth_events = self._load_json("auth_events.json", subdir="input")

        transformed = []
        for e in auth_events:
            event_type = e.get("event_type", "")
            login_success = event_type == "login_success"

            transformed.append({
                "event_id": e.get("event_id", ""),
                "timestamp": e.get("event_time", ""),
                "ip_address": e.get("ip_address", ""),
                "device_id": e.get("device_id", ""),
                "device_type": "unknown",  # Not in ML data
                "location_country": e.get("geo_country", "").upper(),
                "is_vpn": False,  # Not in ML data
                "is_proxy": False,  # Not in ML data
                "login_success": login_success,
                "risk_flags": [] if login_success else ["login_failed"],
                "browser": None,
                "location_city": None,
                "failure_reason": "authentication_failed" if not login_success else None,
                # Keep for filtering
                "user_id": e.get("user_id"),
                "account_id": e.get("account_id"),
            })
        return transformed

    def _derive_devices(self, account_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Derive device information from transactions and auth events."""
        transactions = self._load_transactions()
        logins = self._load_logins()

        # Collect all device IDs for this account/user
        device_data: Dict[str, Dict] = {}

        # From transactions
        for t in transactions:
            if t.get("account_id") == account_id or t.get("user_id") == user_id:
                device_id = t.get("device_id")
                if device_id:
                    if device_id not in device_data:
                        device_data[device_id] = {
                            "device_id": device_id,
                            "timestamps": [],
                            "accounts": set(),
                            "channels": set(),
                        }
                    device_data[device_id]["timestamps"].append(t.get("timestamp", ""))
                    device_data[device_id]["accounts"].add(t.get("account_id", ""))
                    device_data[device_id]["channels"].add(t.get("channel", ""))

        # From logins
        for l in logins:
            if l.get("user_id") == user_id:
                device_id = l.get("device_id")
                if device_id:
                    if device_id not in device_data:
                        device_data[device_id] = {
                            "device_id": device_id,
                            "timestamps": [],
                            "accounts": set(),
                            "channels": set(),
                        }
                    device_data[device_id]["timestamps"].append(l.get("timestamp", ""))

        # Transform to DeviceInfo format
        devices = []
        for device_id, data in device_data.items():
            timestamps = sorted([t for t in data["timestamps"] if t])
            channels = data.get("channels", set())

            # Infer device type from channel
            device_type = "unknown"
            if "mobile" in channels:
                device_type = "mobile"
            elif "web" in channels:
                device_type = "desktop"
            elif "api" in channels:
                device_type = "desktop"

            devices.append({
                "device_id": device_id,
                "device_type": device_type,
                "os": "unknown",
                "first_seen": timestamps[0] if timestamps else "",
                "last_seen": timestamps[-1] if timestamps else "",
                "is_trusted": True,  # Default
                "linked_accounts": list(data.get("accounts", set())),
            })

        return devices

    def _derive_network_connections(self, case_data: Dict, account_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Derive network connections from case data (fraud rings, shared devices)."""
        connections = []

        # Check for fraud ring data
        if case_data.get("fraud_type") == "fraud_ring":
            ring_members = case_data.get("ring_members", [])
            shared_device = case_data.get("shared_device")
            shared_ip = case_data.get("shared_ip")

            for member in ring_members:
                if member != user_id:
                    connections.append({
                        "connection_type": "shared_device",
                        "connected_entity_id": member,
                        "connection_strength": "strong",
                        "first_observed": case_data.get("created_at", ""),
                        "details": f"Shared device {shared_device} and IP {shared_ip}",
                    })

        # Check for multi-account fraud
        if case_data.get("fraud_type") == "multi_account_fraud":
            accounts_involved = case_data.get("accounts_involved", [])
            for acc in accounts_involved:
                if acc != account_id:
                    connections.append({
                        "connection_type": "same_owner",
                        "connected_entity_id": acc,
                        "connection_strength": "strong",
                        "first_observed": case_data.get("created_at", ""),
                        "details": f"Multiple accounts owned by same user {user_id}",
                    })

        return connections

    # =========================================================================
    # MAIN ASSEMBLY METHOD
    # =========================================================================

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
        # Load all data using adapters
        cases = self._load_cases()
        all_alerts = self._load_alerts()
        customers = self._load_customers()
        accounts = self._load_accounts()
        all_transactions = self._load_transactions()
        all_logins = self._load_logins()

        # Find the case
        case_data = self._find_by_id(cases, "case_id", case_id)
        if not case_data:
            raise ValueError(f"Case not found: {case_id}")

        # Get user_id and account_id - handle both string and list formats
        user_id = case_data.get("user_id")
        if isinstance(user_id, list):
            user_id = user_id[0]  # Take first user for fraud rings

        account_id = case_data.get("account_id")

        # Map user_id to customer_id (they're the same in ML data)
        customer_id = user_id

        # Assemble alerts for this case
        case_alert_ids = case_data.get("alert_ids", [])
        case_alerts = [a for a in all_alerts if a.get("alert_id") in case_alert_ids]

        alerts = [
            AlertInfo(
                alert_id=a.get("alert_id", ""),
                alert_type=a.get("alert_type", ""),
                triggered_at=a.get("triggered_at", ""),
                severity=a.get("severity", "medium"),
                risk_score=a.get("risk_score", 0),
                description=a.get("description", ""),
                detector_source=a.get("detector_source", ""),
                evidence=a.get("evidence") or [],
                raw_signal_refs=a.get("raw_signal_refs") or []
            )
            for a in case_alerts
        ]

        # Assemble customer (KYC data)
        customer_data = self._find_by_id(customers, "customer_id", customer_id)
        customer = None
        if customer_data:
            customer = KYCData(
                customer_id=customer_data.get("customer_id", ""),
                full_name=customer_data.get("full_name", ""),
                email=customer_data.get("email", ""),
                phone=customer_data.get("phone", ""),
                country=customer_data.get("country", ""),
                verification_status=customer_data.get("verification_status", ""),
                verification_method=customer_data.get("verification_method", ""),
                risk_rating=customer_data.get("risk_rating", ""),
                pep_status=customer_data.get("pep_status", False),
                sanctions_hit=customer_data.get("sanctions_hit", False),
                adverse_media=customer_data.get("adverse_media", False),
                document_verified=customer_data.get("document_verified", False),
                document_flags=customer_data.get("document_flags") or [],
                date_of_birth=customer_data.get("date_of_birth"),
                address=customer_data.get("address"),
                verification_date=customer_data.get("verification_date"),
                declared_income=customer_data.get("declared_income"),
                income_currency=customer_data.get("income_currency"),
                employment_status=customer_data.get("employment_status"),
                document_type=customer_data.get("document_type"),
                document_country=customer_data.get("document_country")
            )

        # Assemble account
        account_data = self._find_by_id(accounts, "account_id", account_id)
        account = None
        if account_data:
            account = AccountSummary(
                account_id=account_data.get("account_id", ""),
                customer_id=account_data.get("customer_id", ""),
                account_type=account_data.get("account_type", ""),
                account_status=account_data.get("account_status", ""),
                created_at=account_data.get("created_at", ""),
                total_deposits_30d=account_data.get("total_deposits_30d", 0),
                total_withdrawals_30d=account_data.get("total_withdrawals_30d", 0),
                total_trades_30d=account_data.get("total_trades_30d", 0),
                average_transaction_amount=account_data.get("average_transaction_amount", 0),
                account_age_days=account_data.get("account_age_days", 0),
                is_dormant_reactivated=account_data.get("is_dormant_reactivated", False),
                deposit_to_income_ratio=account_data.get("deposit_to_income_ratio")
            )

        # Assemble transactions for this account
        account_transactions = [t for t in all_transactions if t.get("account_id") == account_id]
        txn_list = [
            Transaction(
                transaction_id=t.get("transaction_id", ""),
                timestamp=t.get("timestamp", ""),
                type=t.get("type", ""),
                amount=t.get("amount", 0),
                currency=t.get("currency", ""),
                status=t.get("status", ""),
                channel=t.get("channel", ""),
                counterparty=t.get("counterparty"),
                risk_flags=t.get("risk_flags") or []
            )
            for t in account_transactions
        ]

        # Assemble logins for this user
        user_logins = [l for l in all_logins if l.get("user_id") == user_id]
        login_list = [
            LoginEvent(
                event_id=l.get("event_id", ""),
                timestamp=l.get("timestamp", ""),
                ip_address=l.get("ip_address", ""),
                device_id=l.get("device_id", ""),
                device_type=l.get("device_type", ""),
                location_country=l.get("location_country", ""),
                is_vpn=l.get("is_vpn", False),
                is_proxy=l.get("is_proxy", False),
                login_success=l.get("login_success", True),
                risk_flags=l.get("risk_flags") or [],
                browser=l.get("browser"),
                location_city=l.get("location_city"),
                failure_reason=l.get("failure_reason")
            )
            for l in user_logins
        ]

        # Derive devices
        device_data_list = self._derive_devices(account_id, user_id)
        device_list = [
            DeviceInfo(
                device_id=d.get("device_id", ""),
                device_type=d.get("device_type", ""),
                os=d.get("os", ""),
                first_seen=d.get("first_seen", ""),
                last_seen=d.get("last_seen", ""),
                is_trusted=d.get("is_trusted", False),
                linked_accounts=d.get("linked_accounts") or []
            )
            for d in device_data_list
        ]

        # Derive network connections from case data
        network_data = self._derive_network_connections(case_data, account_id, user_id)
        connection_list = [
            NetworkConnection(
                connection_type=c.get("connection_type", ""),
                connected_entity_id=c.get("connected_entity_id", ""),
                connection_strength=c.get("connection_strength", ""),
                first_observed=c.get("first_observed", ""),
                details=c.get("details", "")
            )
            for c in network_data
        ]

        # Prior cases - not available in ML data, return empty
        prior_case_list = []

        # Generate data completeness
        data_completeness = DataCompleteness(
            kyc_data=customer is not None,
            transaction_history=len(txn_list) > 0,
            login_history=len(login_list) > 0,
            device_data=len(device_list) > 0,
            network_analysis=len(connection_list) > 0,
            prior_cases=len(prior_case_list) > 0
        )

        # Assemble final CaseContext
        return CaseContext(
            case_id=case_id,
            created_at=case_data.get("created_at", ""),
            assembled_at=datetime.now(timezone.utc).isoformat() + "Z",
            alerts=alerts,
            customer=customer,
            account=account,
            transactions=txn_list,
            logins=login_list,
            devices=device_list,
            network_connections=connection_list,
            prior_cases=prior_case_list,
            data_completeness=data_completeness
        )

    def clear_cache(self):
        """Clear the data cache."""
        self._cache.clear()

    def get_all_case_ids(self) -> List[str]:
        """Get all available case IDs from ML output."""
        cases = self._load_cases()
        return [c.get("case_id") for c in cases if c.get("case_id")]


# Convenience function for quick assembly
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
