import json
import event_enrichment
import case_builder
import time
import pandas as pd


def load_events(path):
    with open(path, 'r') as file:
        data = json.load(file)
    return data


def stream_data(txn_path):
    txn_events = load_events(txn_path)

    for event in txn_events:

        print("Original Event:")
        print(json.dumps(event, indent=2))
        enriched_event = event_enrichment.demo_enrichment(event)


        # print("Enriched Event:")
        # print(json.dumps(enriched_event, indent=2))

        event_df = pd.DataFrame(enriched_event)
        print("Enriched Event DataFrame:")
        print(event_df)


        # Plug this into Anomaly Dectector and get alert
        # alert = anomaly_detector.detect_anomaly(enriched_event)
        alert = None  # Placeholder for anomaly detection

        if alert:
            case = case_builder.demo_bulid_case(alert)

        
        time.sleep(1)  # Simulate delay between events

    return case

def main():
    return stream_data('streaming_events/transcation_events.json')

if __name__ == "__main__":
    main()
