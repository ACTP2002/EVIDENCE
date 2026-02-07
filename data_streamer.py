import json
import event_enrichment
import case_builder
import time


def load_events(path):
    with open(path, 'r') as file:
        data = json.load(file)
    return data


def stream_data(txn_path):
    txn_events = load_events(txn_path)

    for event in txn_events:

        enriched_event = event_enrichment.demo_enrichment(event)

        # Plug this into Anomaly Dectector and get alert
        # alert = anomaly_detector.detect_anomaly(enriched_event)
        alert = "placeholder_alert_based_on_anomaly_detection"

        if alert:
            case = case_builder.demo_bulid_case(alert)

        if case:
            return case
        
        time.sleep(2)

    return None

def main():
    return stream_data('streaming_events/trancation_events.json')

if __name__ == "__main__":
    main()
