"""
Aggregates all relevant data (transactions, logins, devices, KYC, history)
into a single, coherent case view that matches the CaseContext schema.

This skill reads from Django's separate dummy_data JSON files and assembles
them into a unified CaseContext object for the AI Agent to investigate.
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path


# Path to Django's dummy data (relative to Django project root)
DUMMY_DATA_PATH = Path(__file__).parent.parent.parent / "api" / "dummy_data"


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
    Assembles case context from Django's separate data files.

    This class reads from the dummy_data directory and joins all relevant
    data for a given case into a single CaseContext object.
    """

    def __init__(self, data_path: Path = None):
        """
        Initialize the assembler.

        Args:
            data_path: Path to the dummy_data directory. Defaults to Django's api/dummy_data.
        """
        self.data_path = data_path or DUMMY_DATA_PATH
        self._cache: Dict[str, List[Dict]] = {}

    def _load_json(self, filename: str) -> List[Dict[str, Any]]:
        """Load and cache a JSON file."""
        if filename not in self._cache:
            file_path = self.data_path / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self._cache[filename] = json.load(f)
            else:
                self._cache[filename] = []
        return self._cache[filename]

    def _find_by_id(self, data: List[Dict], id_field: str, id_value: str) -> Optional[Dict]:
        """Find a single item by ID field."""
        for item in data:
            if item.get(id_field) == id_value:
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
        # Load all data files
        cases = self._load_json("cases.json")
        customers = self._load_json("customers.json")
        accounts = self._load_json("accounts.json")
        transactions = self._load_json("transactions.json")
        logins = self._load_json("logins.json")
        devices = self._load_json("devices.json")
        network_connections = self._load_json("network_connections.json")
        prior_cases = self._load_json("prior_cases.json")

        # Find the case
        case_data = self._find_by_id(cases, "case_id", case_id)
        if not case_data:
            raise ValueError(f"Case not found: {case_id}")

        customer_id = case_data.get("customer_id")
        account_id = case_data.get("account_id")

        # Assemble alerts
        alerts = [
            AlertInfo(
                alert_id=a.get("alert_id", ""),
                alert_type=a.get("alert_type", ""),
                triggered_at=a.get("triggered_at", ""),
                severity=a.get("severity", ""),
                risk_score=a.get("risk_score", 0),
                description=a.get("description", ""),
                detector_source=a.get("detector_source", ""),
                evidence=a.get("evidence") or [],
                raw_signal_refs=a.get("raw_signal_refs") or []
            )
            for a in case_data.get("alerts", [])
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
        account_transactions = self._filter_by(transactions, account_id=account_id)
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

        # Assemble logins for this account
        account_logins = self._filter_by(logins, account_id=account_id)
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
            for l in account_logins
        ]

        # Assemble devices - find devices linked to this account
        device_list = []
        for d in devices:
            if account_id in d.get("linked_accounts", []):
                device_list.append(DeviceInfo(
                    device_id=d.get("device_id", ""),
                    device_type=d.get("device_type", ""),
                    os=d.get("os", ""),
                    first_seen=d.get("first_seen", ""),
                    last_seen=d.get("last_seen", ""),
                    is_trusted=d.get("is_trusted", False),
                    linked_accounts=d.get("linked_accounts") or []
                ))

        # Assemble network connections for this account
        account_connections = self._filter_by(network_connections, entity_id=account_id)
        # Also check for customer-level connections
        customer_connections = self._filter_by(network_connections, entity_id=customer_id)
        all_connections = account_connections + customer_connections

        connection_list = [
            NetworkConnection(
                connection_type=c.get("connection_type", ""),
                connected_entity_id=c.get("connected_entity_id", ""),
                connection_strength=c.get("connection_strength", ""),
                first_observed=c.get("first_observed", ""),
                details=c.get("details", "")
            )
            for c in all_connections
        ]

        # Assemble prior cases for this customer
        customer_prior_cases = self._filter_by(prior_cases, customer_id=customer_id)
        prior_case_list = [
            PriorCase(
                case_id=p.get("case_id", ""),
                case_date=p.get("case_date", ""),
                case_type=p.get("case_type", ""),
                outcome=p.get("outcome", ""),
                resolution_notes=p.get("resolution_notes")
            )
            for p in customer_prior_cases
        ]

        # Generate data completeness dynamically
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
