import json
import sys

def load_store(path):
    with open(path, 'r') as file:
        data = json.load(file)
    return {row['user_id']: row for row in data}

def enrich_event(event, profile_store, status_store):
    user_id = event.get('user_id')
    if not user_id:
        return {"event": event, "profile": None, "stauts": None, "error": "user_id not found in event"}

    profile = profile_store.get(user_id)
    status = status_store.get(user_id)

    return {"event": event, "profile": profile, "status": status}

def main():
    if len(sys.argv) != 4:
        print("Usage: python event_enrichment.py <event_json> <profile_store_path> <status_store_path>")
        sys.exit(1)

    event_json = sys.argv[1]
    profile_store_path = sys.argv[2]
    status_store_path = sys.argv[3]

    event = json.loads(event_json)
    profile_store = load_store(profile_store_path)
    status_store = load_store(status_store_path)

    enriched_event = enrich_event(event, profile_store, status_store)
    print(json.dumps(enriched_event, indent=2))

if __name__ == "__main__":
    main()

