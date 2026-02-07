import json
import uuid
import sys
from datetime import datetime, timedelta


def is_within_5_hours(updated_at_iso: str) -> bool:
    updated_at = datetime.fromisoformat(
        updated_at_iso.replace("Z", "+00:00")
    )
    now = datetime.utcnow().replace(tzinfo=updated_at.tzinfo)
    return now - updated_at < timedelta(hours=5)


def load_cases(path):
    with open(path, 'r') as file:
        return json.load(file)
    

def find_latest_case(case_store, user_id):
    for case in reversed(case_store):
        if case["user_id"] == user_id:
            return case
    return None

SEVERITY_WEIGHT = {"LOW": 10, "MEDIUM": 30, "HIGH": 60}

def compute_risk(alerts):
    score = sum(SEVERITY_WEIGHT[a["severity"]] * a["confidence"] for a in alerts)
    score = min(100, int(round(score)))

    if score <= 30:
        sev = "LOW"
    elif score <= 70:
        sev = "MEDIUM"
    else:
        sev = "HIGH"

    return score, sev

def save_cases(path, case_store):
    with open(path, "w") as f:
        json.dump(case_store, f, indent=2, ensure_ascii=False)


def emit_case(case):
    return json.dumps(case, indent=2) if case else json.dumps({"error": "No case created"}, indent=2)


def build_case(alert, case_store):
    user_id = alert.get("user_id")
    if not user_id:
        return None
        

    now_iso = datetime.utcnow().isoformat() + "Z"
    case = find_latest_case(case_store, user_id)

    # For now we will be using 5 hours as the threshold to update existing case

    if case and is_within_5_hours(case["last_updated"]):
        case["last_updated"] = now_iso
        case["alerts"].append(alert)

        case["case_score"], case["risk_level"] = compute_risk(case["alerts"])

        return case


    else:
        risk_score, severity = compute_risk([alert])
        new_case = {
                'case_id': f"CASE-{uuid.uuid4().hex[:8]}",
                'user_id': user_id,
                'status': 'open',
                'opened_at': now_iso,
                'last_updated': now_iso,
                'case_score': risk_score,
                'risk_level': severity,
                'alerts': [
                    alert
                ],
            }
    
    

    case_store.append(new_case)

    return new_case

def main():
    if len(sys.argv) != 4:
        print("Usage: python case_builder.py <alert_json> <case_store_path> <output_case_store_path>")
        sys.exit(1)

    alert_json = sys.argv[1]
    case_store_path = sys.argv[2]
    output_case_store_path = sys.argv[3]

    alert = json.loads(alert_json)
    case_store = load_cases(case_store_path)

    case = build_case(alert, case_store)

    if case:
        save_cases(output_case_store_path, case_store)

    return emit_case(case)


if __name__ == "__main__":
    case_json = main()
    print(case_json)

