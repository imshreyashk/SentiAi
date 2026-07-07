from dataclasses import dataclass
import json
from typing import Union
import unittest

@dataclass(frozen=True)
class TelemetryPayload:
    gate_id: Union[str, int]
    current_occupancy: int
    max_capacity: int
    transit_status: str
    crowd_temperament: str
    active_language: str

class StadiumOperationsEngine:
    TRANSLATIONS = {
        "en": {
            "low": "Welcome to the stadium. Please follow the signs to your gate.",
            "moderate": "Crowd density is high. Please move slowly and follow staff instructions.",
            "high": "Emergency alert. Please evacuate the area immediately through the nearest exit."
        },
        "es": {
            "low": "Bienvenido al estadio. Siga las indicaciones hacia su puerta.",
            "moderate": "La densidad de la multitud es alta. Avance despacio y siga las instrucciones del personal.",
            "high": "Alerta de emergencia. Evacue la zona inmediatamente por la salida más cercana."
        },
        "fr": {
            "low": "Bienvenue au stade. Veuillez suivre les panneaux vers votre porte.",
            "moderate": "La densité de foule est élevée. Déplacez-vous lentement et suivez les instructions du personnel.",
            "high": "Alerte d'urgence. Veuillez évacuer la zone immédiatement par la sortie la plus proche."
        },
        "ar": {
            "low": "مرحباً بكم في الملعب. يرجى اتباع اللافتات المؤدية إلى البوابة الخاصة بكم.",
            "moderate": "كثافة الحشود مرتفعة. يرجى التحرك ببطء واتباع تعليمات المنظمين.",
            "high": "تنبيه طوارئ. يرجى إخلاء المنطقة فوراً من خلال أقرب مخرج."
        }
    }

    @staticmethod
    def validate_payload(payload: TelemetryPayload) -> None:
        if not isinstance(payload.gate_id, (str, int)) or str(payload.gate_id).strip() == "":
            raise ValueError("Invalid gate_id")
        if payload.current_occupancy < 0:
            raise ValueError("Occupancy cannot be negative")
        if payload.max_capacity <= 0:
            raise ValueError("Max capacity must be greater than zero")
        
        occupancy_ratio = payload.current_occupancy / payload.max_capacity
        if occupancy_ratio > 3.0:
            raise ValueError(f"Capacity overflow detected: occupancy ratio ({occupancy_ratio:.2%}) exceeds 300%")

        valid_transit = {"normal", "delayed", "blocked"}
        if payload.transit_status not in valid_transit:
            raise ValueError(f"Invalid transit_status: {payload.transit_status}")

        valid_temperament = {"calm", "anxious", "angry", "violent"}
        if payload.crowd_temperament not in valid_temperament:
            raise ValueError(f"Invalid crowd_temperament: {payload.crowd_temperament}")

        if payload.active_language not in StadiumOperationsEngine.TRANSLATIONS:
            raise ValueError(f"Unsupported active_language: {payload.active_language}")

    def evaluate_threat_score(self, payload: TelemetryPayload) -> float:
        self.validate_payload(payload)
        
        ratio = payload.current_occupancy / payload.max_capacity
        if ratio <= 1.0:
            occ_score = ratio * 50.0
        else:
            occ_score = 50.0 + (ratio - 1.0) * 25.0
            if occ_score > 100.0:
                occ_score = 100.0

        transit_map = {"normal": 0.0, "delayed": 12.5, "blocked": 25.0}
        transit_score = transit_map[payload.transit_status]

        mood_map = {"calm": 0.0, "anxious": 10.0, "angry": 18.0, "violent": 25.0}
        mood_score = mood_map[payload.crowd_temperament]

        score = (occ_score * 0.5) + transit_score + mood_score

        if payload.transit_status == "blocked" and payload.crowd_temperament in {"violent", "angry"}:
            score = (score ** 1.1) * 1.5

        return min(max(score, 0.0), 100.0)

    def broker_mitigation(self, payload: TelemetryPayload) -> str:
        threat_score = self.evaluate_threat_score(payload)
        lang = payload.active_language

        if threat_score < 40.0:
            level = "low"
            routing = "Maintain current routing."
            staff = "Standard steward patrols active."
        elif threat_score < 70.0:
            level = "moderate"
            routing = "Slow flow, redirect 20% to adjacent gates."
            staff = "Deploy crowd control officers to gate."
        else:
            level = "high"
            routing = "Full diversion. Close gate, reroute all inbound traffic."
            staff = "Deploy rapid response and medical teams."

        msg = self.TRANSLATIONS[lang][level]

        result = {
            "dynamic_routing": routing,
            "staff_allocation": staff,
            "broadcast_msg": msg
        }
        return json.dumps(result, separators=(',', ':'), ensure_ascii=False)

class TestStadiumOperationsEngine(unittest.TestCase):
    def setUp(self):
        self.engine = StadiumOperationsEngine()

    def test_normal_low_threat(self):
        payload = TelemetryPayload(
            gate_id="Gate_A",
            current_occupancy=500,
            max_capacity=1000,
            transit_status="normal",
            crowd_temperament="calm",
            active_language="en"
        )
        score = self.engine.evaluate_threat_score(payload)
        self.assertLess(score, 40.0)
        
        mitigation_json = self.engine.broker_mitigation(payload)
        mitigation = json.loads(mitigation_json)
        self.assertIn("dynamic_routing", mitigation)
        self.assertIn("staff_allocation", mitigation)
        self.assertIn("broadcast_msg", mitigation)
        self.assertEqual(mitigation["broadcast_msg"], self.engine.TRANSLATIONS["en"]["low"])

    def test_validation_errors(self):
        with self.assertRaises(ValueError):
            self.engine.validate_payload(TelemetryPayload("G1", -1, 100, "normal", "calm", "en"))
        with self.assertRaises(ValueError):
            self.engine.validate_payload(TelemetryPayload("G1", 10, 0, "normal", "calm", "en"))
        with self.assertRaises(ValueError):
            self.engine.validate_payload(TelemetryPayload("G1", 301, 100, "normal", "calm", "en"))
        with self.assertRaises(ValueError):
            self.engine.validate_payload(TelemetryPayload("G1", 50, 100, "fast", "calm", "en"))

    def test_high_threat_mitigation_and_localization(self):
        payload = TelemetryPayload(
            gate_id=12,
            current_occupancy=2500,
            max_capacity=1000,
            transit_status="blocked",
            crowd_temperament="violent",
            active_language="es"
        )
        score = self.engine.evaluate_threat_score(payload)
        self.assertGreaterEqual(score, 70.0)
        
        mitigation_json = self.engine.broker_mitigation(payload)
        mitigation = json.loads(mitigation_json)
        self.assertEqual(mitigation["broadcast_msg"], self.engine.TRANSLATIONS["es"]["high"])

    def test_compounding_risk_and_empty_gate_hostility(self):
        payload = TelemetryPayload(
            gate_id="Gate_Empty_Hostile",
            current_occupancy=0,
            max_capacity=1000,
            transit_status="blocked",
            crowd_temperament="violent",
            active_language="en"
        )
        score = self.engine.evaluate_threat_score(payload)
        self.assertEqual(score, 100.0)
        
        mitigation_json = self.engine.broker_mitigation(payload)
        mitigation = json.loads(mitigation_json)
        self.assertEqual(mitigation["broadcast_msg"], self.engine.TRANSLATIONS["en"]["high"])
        self.assertIn("Full diversion", mitigation["dynamic_routing"])

if __name__ == "__main__":
    unittest.main()
