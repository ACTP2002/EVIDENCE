---
name: timeline-reconstruction-engine
description: Use this skill for each case investigation upon collecting the necessary case details to articulate the chronological sequences of suspicious activity
---

## Instructions

### 1. Your input will be from the case context skill. You should be receiving the input as below format:

{
  "case_id": "CASE-123",
  "alert_id": "ALERT-456",
  "events": [
    {
      "event_id": "evt-001",
      "timestamp": "2026-02-06T10:15:00Z",
      "entity": { "entity_type": "user", "entity_id": "u123" },
      "source": "edr",
      "raw": {
        "event": "LOGIN_SUCCESS",
        "ip": "203.0.113.10",
        "location": "Berlin, DE",
        "device_id": "dev-9"
      }
    }
  ]
}


### 2. Analyse the input and arrange them in chronological order. Include the criticality score (mandatory) and annotate/describe the event that is happening. Every event must be cited back linking to the input. None of the contents here must be hallucinated. It must be solely based on the input received. Sample output format after this stage:

{
  "case_id": "",
  "alert_id": "",
  "timeline": [
    {
      "timestamp": "",
      "entity": {
        "entity_type": "",
        "entity_id": ""
      },
      "event": "",
      "what": "",	
      "who": "",
      "where": {
        "ip": "",
        "location": "",
        "device_id": ""
      },
      "annotation": "",
      "annotation_confidence": ,
      "criticality": "",
      "evidence": {
        "source": "",
        "event_id": ""
      }
    },
    {
      "timestamp": "",
      "entity": {
        "entity_type": "",
        "entity_id": ""
      },
      "event": "",
      "what": {
        "amount": ,
        "currency": "",
        "channel": ""
      },
      "who": ,
      "where": ,
      "annotation": "",
      "annotation_confidence": ,
      "criticality": "",
      "evidence": {
        "source": "",
        "event_id": ""
      }
    }
  ]
}

