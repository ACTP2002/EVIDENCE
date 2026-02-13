"""
SENTINEL Synthetic Data Generator
==================================
Generates realistic fraud detection training data with multiple scenarios:
- Normal user behavior (baseline)
- Income anomalies
- Account takeover (ATO)
- Fraud rings (shared devices, coordinated timing)
- Money mules (structuring)
- Geographic anomalies
- Multi-account fraud (1 user with multiple accounts, layering/structuring)

Usage:
    python data_generator.py --output training_data.csv --rows 20000
    python data_generator.py --output demo_data.csv --demo-mode
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import argparse
import json

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# ============ CONFIGURATION ============

COUNTRIES = ['my', 'sg', 'id', 'th', 'vn', 'ph', 'au', 'gb', 'us', 'cn', 'in', 'jp']
HIGH_RISK_COUNTRIES = ['ru', 'ng', 'pk', 'ir']  # For suspicious transactions
CURRENCIES = ['usd', 'eur', 'gbp', 'myr', 'sgd', 'jpy']
CHANNELS = ['web', 'mobile', 'api']
EVENT_TYPES = ['deposit', 'withdrawal', 'buy', 'sell']

# ============ USER PROFILES ============

def generate_user_profile(user_id: str, profile_type: str = 'normal') -> dict:
    """Generate a user profile based on type."""

    profiles = {
        'normal': {
            'declared_income': np.random.randint(30000, 150000),
            'account_deposit': np.random.randint(5000, 50000),
            'residence_country': random.choice(COUNTRIES),
            'risk_level': 'low',
            'typical_txn_range': (100, 5000),
            'typical_login_hour': np.random.randint(8, 22),
        },
        'high_value': {
            'declared_income': np.random.randint(150000, 500000),
            'account_deposit': np.random.randint(50000, 200000),
            'residence_country': random.choice(['sg', 'au', 'gb', 'us']),
            'risk_level': 'low',
            'typical_txn_range': (1000, 20000),
            'typical_login_hour': np.random.randint(9, 18),
        },
        'suspicious': {
            'declared_income': np.random.randint(20000, 50000),  # Low income
            'account_deposit': np.random.randint(2000, 10000),
            'residence_country': random.choice(COUNTRIES),
            'risk_level': 'high',
            'typical_txn_range': (50, 1000),
            'typical_login_hour': np.random.randint(0, 6),  # Unusual hours
        }
    }

    profile = profiles.get(profile_type, profiles['normal']).copy()
    profile['user_id'] = user_id
    profile['device_id'] = f"DEV-{user_id.split('-')[-1]}-{random.randint(100,999)}"
    profile['ip_address'] = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

    return profile


def generate_normal_transactions(user_profile: dict, num_transactions: int,
                                  start_date: datetime, account_id: str = None) -> list:
    """Generate normal transaction patterns for a user."""

    transactions = []
    current_time = start_date
    account_id = account_id or f"ACC-{user_profile['user_id'].split('-')[-1]}"

    for i in range(num_transactions):
        # Normal time gaps (hours to days between transactions)
        gap_hours = np.random.exponential(scale=24)  # Average 1 day between txns
        current_time += timedelta(hours=gap_hours)

        # Normal transaction amount within typical range
        min_amt, max_amt = user_profile['typical_txn_range']
        amount = np.random.uniform(min_amt, max_amt)

        # Mostly same country
        txn_country = user_profile['residence_country']
        if random.random() < 0.05:  # 5% cross-border (normal travel)
            txn_country = random.choice(COUNTRIES)

        # Normal login behavior
        login_count = np.random.poisson(2)
        failed_logins = 0 if random.random() > 0.1 else np.random.randint(1, 3)

        txn = {
            'user_id': user_profile['user_id'],
            'account_id': account_id,
            'txn_id': f"TXN-{user_profile['user_id']}-{i+1}",
            'event_time': current_time.isoformat(),
            'event_type': random.choice(EVENT_TYPES),
            'amount': round(amount, 2),
            'currency': random.choice(CURRENCIES),
            'channel': random.choice(CHANNELS),
            'declared_income': user_profile['declared_income'],
            'account_deposit': user_profile['account_deposit'],
            'residence_country': user_profile['residence_country'],
            'transaction_country': txn_country,
            'amount_in_1d': round(np.random.uniform(0, amount * 2), 2),
            'amount_out_1d': round(np.random.uniform(0, amount), 2),
            'login_count_1h': login_count,
            'failed_login_1h': failed_logins,
            'new_ip_1d': 0,
            'geo_change_1d': 0,
            'device_id': user_profile['device_id'],
            'ip_address': user_profile['ip_address'],
            'is_fraud': 0,
            'fraud_type': 'none'
        }
        transactions.append(txn)

    return transactions


# ============ FRAUD SCENARIOS ============

def generate_income_anomaly(user_id: str, start_date: datetime) -> list:
    """
    Scenario: User deposits way more than their declared income suggests.
    Red flag: Deposits 1400%+ of monthly income in short period.
    """
    profile = generate_user_profile(user_id, 'suspicious')
    profile['declared_income'] = 30000  # Low declared income

    transactions = []
    current_time = start_date
    account_id = f"ACC-{user_id.split('-')[-1]}"

    # First, some normal small transactions
    for i in range(5):
        current_time += timedelta(hours=np.random.uniform(12, 48))
        transactions.append({
            'user_id': user_id,
            'account_id': account_id,
            'txn_id': f"TXN-{user_id}-{i+1}",
            'event_time': current_time.isoformat(),
            'event_type': 'deposit',
            'amount': round(np.random.uniform(100, 500), 2),
            'currency': 'usd',
            'channel': 'mobile',
            'declared_income': profile['declared_income'],
            'account_deposit': 5000,
            'residence_country': 'my',
            'transaction_country': 'my',
            'amount_in_1d': 500,
            'amount_out_1d': 0,
            'login_count_1h': 2,
            'failed_login_1h': 0,
            'new_ip_1d': 0,
            'geo_change_1d': 0,
            'device_id': profile['device_id'],
            'ip_address': profile['ip_address'],
            'is_fraud': 0,
            'fraud_type': 'none'
        })

    # Then SUSPICIOUS: massive deposits way above income
    for i in range(3):
        current_time += timedelta(hours=np.random.uniform(1, 4))
        suspicious_amount = np.random.uniform(25000, 50000)  # Way above income

        transactions.append({
            'user_id': user_id,
            'account_id': account_id,
            'txn_id': f"TXN-{user_id}-{i+10}",
            'event_time': current_time.isoformat(),
            'event_type': 'deposit',
            'amount': round(suspicious_amount, 2),
            'currency': 'usd',
            'channel': 'mobile',
            'declared_income': profile['declared_income'],
            'account_deposit': 5000 + (i * 25000),
            'residence_country': 'my',
            'transaction_country': 'my',
            'amount_in_1d': round(suspicious_amount * 2, 2),
            'amount_out_1d': 0,
            'login_count_1h': 5,
            'failed_login_1h': 0,
            'new_ip_1d': 0,
            'geo_change_1d': 0,
            'device_id': profile['device_id'],
            'ip_address': profile['ip_address'],
            'is_fraud': 1,
            'fraud_type': 'income_anomaly'
        })

    return transactions


def generate_account_takeover(user_id: str, start_date: datetime) -> list:
    """
    Scenario: Account takeover - attacker gains access and drains funds.
    Red flags: New device, new IP, unusual time, failed logins, rapid withdrawals.
    """
    profile = generate_user_profile(user_id, 'normal')
    transactions = []
    current_time = start_date
    account_id = f"ACC-{user_id.split('-')[-1]}"

    # Normal history first
    for i in range(8):
        current_time += timedelta(hours=np.random.uniform(24, 72))
        transactions.append({
            'user_id': user_id,
            'account_id': account_id,
            'txn_id': f"TXN-{user_id}-{i+1}",
            'event_time': current_time.isoformat(),
            'event_type': random.choice(['deposit', 'buy', 'sell']),
            'amount': round(np.random.uniform(200, 2000), 2),
            'currency': 'usd',
            'channel': 'web',
            'declared_income': profile['declared_income'],
            'account_deposit': 25000,
            'residence_country': profile['residence_country'],
            'transaction_country': profile['residence_country'],
            'amount_in_1d': 1000,
            'amount_out_1d': 500,
            'login_count_1h': 2,
            'failed_login_1h': 0,
            'new_ip_1d': 0,
            'geo_change_1d': 0,
            'device_id': profile['device_id'],
            'ip_address': profile['ip_address'],
            'is_fraud': 0,
            'fraud_type': 'none'
        })

    # TAKEOVER EVENT: Attacker accesses account
    attacker_device = f"DEV-ATTACKER-{random.randint(1000,9999)}"
    attacker_ip = f"185.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

    # 3AM in a different country, multiple failed logins, then rapid withdrawals
    current_time = current_time.replace(hour=3, minute=random.randint(0, 59))

    for i in range(3):
        current_time += timedelta(minutes=random.randint(1, 5))
        withdrawal_amount = np.random.uniform(8000, 15000)

        transactions.append({
            'user_id': user_id,
            'account_id': account_id,
            'txn_id': f"TXN-{user_id}-ATO-{i+1}",
            'event_time': current_time.isoformat(),
            'event_type': 'withdrawal',
            'amount': round(withdrawal_amount, 2),
            'currency': 'usd',
            'channel': 'mobile',
            'declared_income': profile['declared_income'],
            'account_deposit': max(0, 25000 - (i * 10000)),
            'residence_country': profile['residence_country'],
            'transaction_country': random.choice(HIGH_RISK_COUNTRIES),
            'amount_in_1d': 0,
            'amount_out_1d': round(withdrawal_amount * (i + 1), 2),
            'login_count_1h': 15 + i * 3,
            'failed_login_1h': 8 + i * 2,
            'new_ip_1d': 1,
            'geo_change_1d': 1,
            'device_id': attacker_device,
            'ip_address': attacker_ip,
            'is_fraud': 1,
            'fraud_type': 'account_takeover'
        })

    return transactions


def generate_fraud_ring(ring_id: str, num_members: int, start_date: datetime) -> list:
    """
    Scenario: Coordinated fraud ring - multiple users, shared device, synchronized timing.
    Red flags: Same device across users, transactions within minutes, cross-border.

    THIS IS THE "BLOW MINDS" SCENARIO FOR THE HACKATHON.
    """
    transactions = []

    # SHARED indicators (what connects the ring)
    shared_device = f"DEV-RING-{ring_id}"
    shared_ip = f"103.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    ring_time = start_date.replace(hour=1, minute=10)  # Coordinated 1:10 AM

    ring_members = []

    for i in range(num_members):
        user_id = f"U-RING-{ring_id}-{i+1:03d}"
        account_id = f"ACC-RING-{ring_id}-{i+1:03d}"

        ring_members.append({
            'user_id': user_id,
            'account_id': account_id,
            'declared_income': np.random.randint(25000, 45000),
        })

        # Each member has some normal-looking history first
        current_time = start_date - timedelta(days=random.randint(10, 30))
        profile = generate_user_profile(user_id, 'normal')

        for j in range(5):
            current_time += timedelta(hours=np.random.uniform(24, 72))
            transactions.append({
                'user_id': user_id,
                'account_id': account_id,
                'txn_id': f"TXN-{user_id}-{j+1}",
                'event_time': current_time.isoformat(),
                'event_type': random.choice(['deposit', 'buy']),
                'amount': round(np.random.uniform(500, 3000), 2),
                'currency': 'usd',
                'channel': 'mobile',
                'declared_income': ring_members[i]['declared_income'],
                'account_deposit': 10000,
                'residence_country': 'my',
                'transaction_country': 'my',
                'amount_in_1d': 2000,
                'amount_out_1d': 500,
                'login_count_1h': 2,
                'failed_login_1h': 0,
                'new_ip_1d': 0,
                'geo_change_1d': 0,
                'device_id': profile['device_id'],  # Normal device
                'ip_address': profile['ip_address'],
                'is_fraud': 0,
                'fraud_type': 'none'
            })

    # COORDINATED ATTACK: All members withdraw within minutes
    for i, member in enumerate(ring_members):
        attack_time = ring_time + timedelta(minutes=i)  # 1 minute apart
        withdrawal_amount = np.random.uniform(12000, 25000)

        transactions.append({
            'user_id': member['user_id'],
            'account_id': member['account_id'],
            'txn_id': f"TXN-{member['user_id']}-RING-ATTACK",
            'event_time': attack_time.isoformat(),
            'event_type': 'withdrawal',
            'amount': round(withdrawal_amount, 2),
            'currency': 'usd',
            'channel': 'mobile',
            'declared_income': member['declared_income'],
            'account_deposit': max(0, 10000 - withdrawal_amount),
            'residence_country': 'my',
            'transaction_country': random.choice(['sg', 'cn', 'ru']),
            'amount_in_1d': 500,
            'amount_out_1d': round(withdrawal_amount, 2),
            'login_count_1h': 12 + i,
            'failed_login_1h': 6 + i,
            'new_ip_1d': 1,
            'geo_change_1d': 1,
            'device_id': shared_device,  # SAME DEVICE!
            'ip_address': shared_ip,      # SAME IP!
            'is_fraud': 1,
            'fraud_type': 'fraud_ring'
        })

    return transactions


def generate_money_mule(user_id: str, start_date: datetime) -> list:
    """
    Scenario: Money mule - rapid deposit/withdrawal cycles (structuring).
    Red flags: Many small transactions, rapid in/out, amounts just under reporting threshold.
    """
    profile = generate_user_profile(user_id, 'suspicious')
    transactions = []
    current_time = start_date
    account_id = f"ACC-{user_id.split('-')[-1]}"

    # Pattern: deposit, then quick withdrawal, repeat
    for cycle in range(5):
        # Deposit (just under $10k reporting threshold)
        deposit_amount = np.random.uniform(8000, 9900)
        current_time += timedelta(hours=np.random.uniform(2, 8))

        transactions.append({
            'user_id': user_id,
            'account_id': account_id,
            'txn_id': f"TXN-{user_id}-D{cycle+1}",
            'event_time': current_time.isoformat(),
            'event_type': 'deposit',
            'amount': round(deposit_amount, 2),
            'currency': 'usd',
            'channel': 'mobile',
            'declared_income': profile['declared_income'],
            'account_deposit': 5000 + (cycle * 1000),
            'residence_country': 'my',
            'transaction_country': 'my',
            'amount_in_1d': round(deposit_amount * (cycle + 1), 2),
            'amount_out_1d': round(deposit_amount * cycle * 0.9, 2),
            'login_count_1h': 3,
            'failed_login_1h': 0,
            'new_ip_1d': 0,
            'geo_change_1d': 0,
            'device_id': profile['device_id'],
            'ip_address': profile['ip_address'],
            'is_fraud': 1,
            'fraud_type': 'money_mule'
        })

        # Quick withdrawal (within hours)
        withdrawal_amount = deposit_amount * 0.95
        current_time += timedelta(hours=np.random.uniform(0.5, 3))

        transactions.append({
            'user_id': user_id,
            'account_id': account_id,
            'txn_id': f"TXN-{user_id}-W{cycle+1}",
            'event_time': current_time.isoformat(),
            'event_type': 'withdrawal',
            'amount': round(withdrawal_amount, 2),
            'currency': 'usd',
            'channel': 'mobile',
            'declared_income': profile['declared_income'],
            'account_deposit': 5000,
            'residence_country': 'my',
            'transaction_country': random.choice(['sg', 'th', 'id']),
            'amount_in_1d': round(deposit_amount * (cycle + 1), 2),
            'amount_out_1d': round(withdrawal_amount * (cycle + 1), 2),
            'login_count_1h': 4,
            'failed_login_1h': 0,
            'new_ip_1d': 0,
            'geo_change_1d': 0,
            'device_id': profile['device_id'],
            'ip_address': profile['ip_address'],
            'is_fraud': 1,
            'fraud_type': 'money_mule'
        })

    return transactions


def generate_multi_account_fraud(user_id: str, start_date: datetime) -> list:
    """
    Scenario: Single user with multiple accounts doing suspicious activity.
    Red flags: Same user spreading transactions across accounts to avoid detection,
    layering money through different accounts, structuring deposits/withdrawals.

    THIS SCENARIO ADDS TRUE MULTI-ACCOUNT SUPPORT.
    """
    profile = generate_user_profile(user_id, 'suspicious')
    transactions = []
    current_time = start_date

    # User has 3 accounts
    accounts = [
        f"ACC-{user_id.split('-')[-1]}-A",
        f"ACC-{user_id.split('-')[-1]}-B",
        f"ACC-{user_id.split('-')[-1]}-C"
    ]

    # Normal activity on primary account first
    for i in range(5):
        current_time += timedelta(hours=np.random.uniform(12, 36))
        transactions.append({
            'user_id': user_id,
            'account_id': accounts[0],
            'txn_id': f"TXN-{user_id}-{i+1}",
            'event_time': current_time.isoformat(),
            'event_type': random.choice(['deposit', 'buy']),
            'amount': round(np.random.uniform(200, 1500), 2),
            'currency': 'usd',
            'channel': 'web',
            'declared_income': profile['declared_income'],
            'account_deposit': 8000,
            'residence_country': 'my',
            'transaction_country': 'my',
            'amount_in_1d': 1000,
            'amount_out_1d': 300,
            'login_count_1h': 2,
            'failed_login_1h': 0,
            'new_ip_1d': 0,
            'geo_change_1d': 0,
            'device_id': profile['device_id'],
            'ip_address': profile['ip_address'],
            'is_fraud': 0,
            'fraud_type': 'none'
        })

    # SUSPICIOUS: Large deposit to account A, then spread withdrawals across B and C
    # This is "layering" - moving money through multiple accounts

    # Step 1: Large deposit to account A
    current_time += timedelta(hours=np.random.uniform(2, 6))
    deposit_amount = np.random.uniform(35000, 50000)  # Way above income

    transactions.append({
        'user_id': user_id,
        'account_id': accounts[0],
        'txn_id': f"TXN-{user_id}-MA-D1",
        'event_time': current_time.isoformat(),
        'event_type': 'deposit',
        'amount': round(deposit_amount, 2),
        'currency': 'usd',
        'channel': 'mobile',
        'declared_income': profile['declared_income'],
        'account_deposit': 8000 + deposit_amount,
        'residence_country': 'my',
        'transaction_country': 'my',
        'amount_in_1d': round(deposit_amount, 2),
        'amount_out_1d': 0,
        'login_count_1h': 5,
        'failed_login_1h': 0,
        'new_ip_1d': 0,
        'geo_change_1d': 0,
        'device_id': profile['device_id'],
        'ip_address': profile['ip_address'],
        'is_fraud': 1,
        'fraud_type': 'multi_account_fraud'
    })

    # Step 2: Quick withdrawals from accounts B and C (splitting to avoid detection)
    remaining = deposit_amount * 0.95
    for idx, acc in enumerate(accounts[1:]):
        current_time += timedelta(minutes=np.random.uniform(15, 45))
        withdrawal_amt = remaining / 2 if idx == 0 else remaining - (remaining / 2)

        transactions.append({
            'user_id': user_id,
            'account_id': acc,
            'txn_id': f"TXN-{user_id}-MA-W{idx+1}",
            'event_time': current_time.isoformat(),
            'event_type': 'withdrawal',
            'amount': round(withdrawal_amt, 2),
            'currency': 'usd',
            'channel': 'mobile',
            'declared_income': profile['declared_income'],
            'account_deposit': 5000,
            'residence_country': 'my',
            'transaction_country': random.choice(['sg', 'th', 'id']),
            'amount_in_1d': round(deposit_amount, 2),
            'amount_out_1d': round(withdrawal_amt, 2),
            'login_count_1h': 6 + idx,
            'failed_login_1h': 0,
            'new_ip_1d': 0,
            'geo_change_1d': 1,
            'device_id': profile['device_id'],
            'ip_address': profile['ip_address'],
            'is_fraud': 1,
            'fraud_type': 'multi_account_fraud'
        })

    # Step 3: Another round - smaller deposits across all accounts (structuring)
    for idx, acc in enumerate(accounts):
        current_time += timedelta(hours=np.random.uniform(2, 8))
        # Just under $10k each (structuring)
        struct_amount = np.random.uniform(8500, 9800)

        transactions.append({
            'user_id': user_id,
            'account_id': acc,
            'txn_id': f"TXN-{user_id}-MA-S{idx+1}",
            'event_time': current_time.isoformat(),
            'event_type': 'deposit',
            'amount': round(struct_amount, 2),
            'currency': 'usd',
            'channel': 'mobile',
            'declared_income': profile['declared_income'],
            'account_deposit': 5000 + struct_amount,
            'residence_country': 'my',
            'transaction_country': 'my',
            'amount_in_1d': round(struct_amount * 3, 2),
            'amount_out_1d': round(deposit_amount * 0.95, 2),
            'login_count_1h': 8 + idx,
            'failed_login_1h': 0,
            'new_ip_1d': 0,
            'geo_change_1d': 0,
            'device_id': profile['device_id'],
            'ip_address': profile['ip_address'],
            'is_fraud': 1,
            'fraud_type': 'multi_account_fraud'
        })

    return transactions


def generate_geo_anomaly(user_id: str, start_date: datetime) -> list:
    """
    Scenario: Geographic impossibility - login from MY, transaction from RU 10 min later.
    Red flag: Impossible travel time.
    """
    profile = generate_user_profile(user_id, 'normal')
    profile['residence_country'] = 'my'
    transactions = []
    current_time = start_date
    account_id = f"ACC-{user_id.split('-')[-1]}"

    # Normal history
    for i in range(5):
        current_time += timedelta(hours=np.random.uniform(24, 48))
        transactions.append({
            'user_id': user_id,
            'account_id': account_id,
            'txn_id': f"TXN-{user_id}-{i+1}",
            'event_time': current_time.isoformat(),
            'event_type': random.choice(['deposit', 'buy']),
            'amount': round(np.random.uniform(500, 2000), 2),
            'currency': 'usd',
            'channel': 'web',
            'declared_income': profile['declared_income'],
            'account_deposit': 15000,
            'residence_country': 'my',
            'transaction_country': 'my',
            'amount_in_1d': 1500,
            'amount_out_1d': 500,
            'login_count_1h': 2,
            'failed_login_1h': 0,
            'new_ip_1d': 0,
            'geo_change_1d': 0,
            'device_id': profile['device_id'],
            'ip_address': profile['ip_address'],
            'is_fraud': 0,
            'fraud_type': 'none'
        })

    # SUSPICIOUS: Transaction from Russia 10 minutes after Malaysia login
    current_time += timedelta(minutes=10)

    transactions.append({
        'user_id': user_id,
        'account_id': account_id,
        'txn_id': f"TXN-{user_id}-GEO-ANOMALY",
        'event_time': current_time.isoformat(),
        'event_type': 'withdrawal',
        'amount': round(np.random.uniform(8000, 15000), 2),
        'currency': 'usd',
        'channel': 'mobile',
        'declared_income': profile['declared_income'],
        'account_deposit': 5000,
        'residence_country': 'my',
        'transaction_country': 'ru',  # Impossible travel!
        'amount_in_1d': 500,
        'amount_out_1d': 12000,
        'login_count_1h': 8,
        'failed_login_1h': 4,
        'new_ip_1d': 1,
        'geo_change_1d': 1,
        'device_id': f"DEV-SUSPICIOUS-{random.randint(1000,9999)}",
        'ip_address': f"185.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
        'is_fraud': 1,
        'fraud_type': 'geo_anomaly'
    })

    return transactions


# ============ DATASET GENERATION ============

def generate_training_dataset(num_normal_users: int = 200,
                               start_date: datetime = None) -> pd.DataFrame:
    """Generate a complete training dataset with all fraud scenarios."""

    if start_date is None:
        start_date = datetime(2026, 1, 1)

    all_transactions = []

    print("Generating normal users...")
    # Normal users (80% of data)
    for i in range(num_normal_users):
        user_id = f"U-NORM-{i+1:04d}"
        profile = generate_user_profile(user_id, random.choice(['normal', 'high_value']))
        num_txns = np.random.randint(15, 50)
        txns = generate_normal_transactions(profile, num_txns, start_date)
        all_transactions.extend(txns)

        if (i + 1) % 50 == 0:
            print(f"  Generated {i+1}/{num_normal_users} normal users")

    print("Generating fraud scenarios...")

    # Income anomalies (5 cases)
    for i in range(5):
        user_id = f"U-INCOME-{i+1:03d}"
        txns = generate_income_anomaly(user_id, start_date + timedelta(days=random.randint(30, 90)))
        all_transactions.extend(txns)
    print("  - Income anomalies: 5 users")

    # Account takeovers (5 cases)
    for i in range(5):
        user_id = f"U-ATO-{i+1:03d}"
        txns = generate_account_takeover(user_id, start_date + timedelta(days=random.randint(30, 90)))
        all_transactions.extend(txns)
    print("  - Account takeovers: 5 users")

    # Fraud rings (3 rings of 4 members each = 12 fraud accounts)
    for ring_num in range(3):
        ring_id = f"{ring_num+1:02d}"
        txns = generate_fraud_ring(ring_id, 4, start_date + timedelta(days=random.randint(60, 120)))
        all_transactions.extend(txns)
    print("  - Fraud rings: 3 rings (12 users total)")

    # Money mules (5 cases)
    for i in range(5):
        user_id = f"U-MULE-{i+1:03d}"
        txns = generate_money_mule(user_id, start_date + timedelta(days=random.randint(30, 90)))
        all_transactions.extend(txns)
    print("  - Money mules: 5 users")

    # Geo anomalies (5 cases)
    for i in range(5):
        user_id = f"U-GEO-{i+1:03d}"
        txns = generate_geo_anomaly(user_id, start_date + timedelta(days=random.randint(30, 90)))
        all_transactions.extend(txns)
    print("  - Geo anomalies: 5 users")

    # Multi-account fraud (3 cases - each user has 3 accounts)
    for i in range(3):
        user_id = f"U-MULTI-{i+1:03d}"
        txns = generate_multi_account_fraud(user_id, start_date + timedelta(days=random.randint(40, 100)))
        all_transactions.extend(txns)
    print("  - Multi-account fraud: 3 users (9 accounts total)")

    # Convert to DataFrame
    df = pd.DataFrame(all_transactions)

    # Sort by event_time
    df['event_time'] = pd.to_datetime(df['event_time'], format='ISO8601')
    df = df.sort_values('event_time').reset_index(drop=True)

    # Add sequential txn_id
    df['txn_id'] = range(1, len(df) + 1)

    print(f"\nDataset generated:")
    print(f"  Total transactions: {len(df)}")
    print(f"  Normal transactions: {len(df[df['is_fraud'] == 0])}")
    print(f"  Fraud transactions: {len(df[df['is_fraud'] == 1])}")
    print(f"  Fraud types: {df[df['is_fraud'] == 1]['fraud_type'].value_counts().to_dict()}")

    return df


def generate_demo_dataset(start_date: datetime = None) -> pd.DataFrame:
    """Generate a smaller, curated demo dataset for presentation."""

    if start_date is None:
        start_date = datetime(2026, 2, 1)

    all_transactions = []

    print("Generating demo dataset...")

    # Fewer normal users for demo
    for i in range(20):
        user_id = f"U-NORM-{i+1:04d}"
        profile = generate_user_profile(user_id, 'normal')
        txns = generate_normal_transactions(profile, 10, start_date)
        all_transactions.extend(txns)

    # One of each fraud type for demo
    all_transactions.extend(generate_income_anomaly("U-DEMO-INCOME", start_date + timedelta(days=15)))
    all_transactions.extend(generate_account_takeover("U-DEMO-ATO", start_date + timedelta(days=20)))
    all_transactions.extend(generate_fraud_ring("DEMO", 4, start_date + timedelta(days=25)))
    all_transactions.extend(generate_money_mule("U-DEMO-MULE", start_date + timedelta(days=30)))
    all_transactions.extend(generate_geo_anomaly("U-DEMO-GEO", start_date + timedelta(days=35)))
    all_transactions.extend(generate_multi_account_fraud("U-DEMO-MULTI", start_date + timedelta(days=40)))

    df = pd.DataFrame(all_transactions)
    df['event_time'] = pd.to_datetime(df['event_time'], format='ISO8601')
    df = df.sort_values('event_time').reset_index(drop=True)
    df['txn_id'] = range(1, len(df) + 1)

    print(f"Demo dataset: {len(df)} transactions, {len(df[df['is_fraud'] == 1])} fraud cases")

    return df


# ============ MAIN ============

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate synthetic fraud detection data')
    parser.add_argument('--output', '-o', default='training_data.csv', help='Output CSV file')
    parser.add_argument('--demo-mode', action='store_true', help='Generate smaller demo dataset')
    parser.add_argument('--users', '-u', type=int, default=200, help='Number of normal users')

    args = parser.parse_args()

    if args.demo_mode:
        df = generate_demo_dataset()
    else:
        df = generate_training_dataset(num_normal_users=args.users)

    # Save to CSV (without is_fraud and fraud_type for model training)
    training_cols = [
        'user_id', 'account_id', 'txn_id', 'event_time', 'event_type', 'amount',
        'currency', 'channel', 'declared_income', 'account_deposit',
        'residence_country', 'transaction_country', 'amount_in_1d', 'amount_out_1d',
        'login_count_1h', 'failed_login_1h', 'new_ip_1d', 'geo_change_1d',
        'device_id', 'ip_address'
    ]

    df[training_cols].to_csv(args.output, index=False)
    print(f"\nSaved to {args.output}")

    # Also save full version with labels for evaluation
    labeled_output = args.output.replace('.csv', '_labeled.csv')
    df.to_csv(labeled_output, index=False)
    print(f"Saved labeled version to {labeled_output}")
