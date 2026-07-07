# SentinAI-Pitch: CommandCenter-AI Operational Intelligence Engine

An event-driven crowd dynamics decision support system for stadium operations at the FIFA World Cup 2026.

## Chosen Vertical
**CommandCenter-AI (Operational Intelligence & Real-Time Decision Support)**

## Approach & Logic

### 1. Deterministic Input Validation Tier
Inputs are received via immutable `TelemetryPayload` packets. They are strictly vetted to block malformed data:
- Type safety validation utilizing native typing constructs.
- Boundary trapping: checks for negative occupancy/capacity and capacity overflows (>300%).
- Domain validation: enforces strict allowed sets for `transit_status` and `crowd_temperament`.

### 2. Asymmetric Threat Compounding Formula
Baseline threat levels calculate linear combinations of occupancy, transit, and crowd temperament metrics. However, when critical conditions overlap, risk multiplies non-linearly:
- **Baseline Threat Calculation:** 
  - Occupancy Score: Up to 50% (scaled ratio relative to capacity).
  - Transit Score: Up to 25% (Normal: 0.0, Delayed: 12.5, Blocked: 25.0).
  - Mood Score: Up to 25% (Calm: 0.0, Anxious: 10.0, Angry: 18.0, Violent: 25.0).
- **Asymmetric Multiplier:** If `transit_status == 'blocked'` AND `crowd_temperament` is `violent` or `angry`, the total base score is amplified compounding-style:
  $$\text{Final Score} = (\text{Base Score}^{1.1}) \times 1.5$$
  This ensures low-occupancy but highly volatile/hostile situations trigger maximum level mitigation actions, with the final score clamped strictly to `[0.0, 100.0]`.

## How It Works
1. **Telemetry Ingestion:** System takes a validated payload containing gate occupancy, capacity, delays, temperament, and user language.
2. **Threat Assessment:** Evaluation matrix computes the deterministic/compounding threat score.
3. **Mitigation Brokering:** Score maps into three levels (`low`, `moderate`, `high`), yielding:
   - Dynamic routing plans
   - Staff allocation directives
   - Localized broadcast notifications (EN, ES, FR, AR) output as minified JSON.

## Operational Assumptions
- **Continuous Event Streams:** The system processes continuous telemetry streams independently.
- **Zero Third-Party Dependency footprint:** Built strictly using native standard Python libraries.
- **Single-Branch Tracking:** Managed via a single main codebase branch to eliminate integration latency.
