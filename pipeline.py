import json
import logging
from typing import List
from stadium_engine import StadiumOperationsEngine, TelemetryPayload

logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
logger = logging.getLogger("pipeline")

def process_batch_stream(json_payload_list: List[str]) -> List[str]:
    """
    Processes a list of raw JSON string packets representing stadium telemetry.
    Converts each packet into a TelemetryPayload object, evaluates mitigations,
    and returns a list of minified mitigation JSON strings.
    Fault-tolerant: catches exceptions on corrupted/invalid packets and logs them.
    """
    engine = StadiumOperationsEngine()
    mitigations = []
    for idx, packet in enumerate(json_payload_list):
        try:
            data = json.loads(packet)
            if not isinstance(data, dict):
                raise ValueError(f"Packet at index {idx} is not a JSON object")
            payload = TelemetryPayload(
                gate_id=data["gate_id"],
                current_occupancy=int(data["current_occupancy"]),
                max_capacity=int(data["max_capacity"]),
                transit_status=str(data["transit_status"]),
                crowd_temperament=str(data["crowd_temperament"]),
                active_language=str(data["active_language"])
            )
            mitigation_json = engine.broker_mitigation(payload)
            mitigations.append(mitigation_json)
        except Exception as e:
            logger.error("Failed to process telemetry packet at index %d: %s", idx, str(e))
    return mitigations

if __name__ == "__main__":
    mock_batch = [
        json.dumps({
            "gate_id": "Gate_A",
            "current_occupancy": 300,
            "max_capacity": 1000,
            "transit_status": "normal",
            "crowd_temperament": "calm",
            "active_language": "en"
        }),
        json.dumps({
            "gate_id": "Gate_B",
            "current_occupancy": 950,
            "max_capacity": 1000,
            "transit_status": "blocked",
            "crowd_temperament": "violent",
            "active_language": "es"
        }),
        '{"gate_id": "Gate_C", "current_occupancy": 500, "max_capacity": 1000'
    ]
    results = process_batch_stream(mock_batch)
    for res in results:
        print(res)
