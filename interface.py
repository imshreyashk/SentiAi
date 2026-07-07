import json
import os
import sys
import time
from stadium_engine import StadiumOperationsEngine, TelemetryPayload

# ── ANSI Palette ───────────────────────────────────────────────────────────────
RST      = "\033[0m";  BOLD = "\033[1m";  DIM = "\033[2m"
FG_WHITE = "\033[97m"; FG_CYAN = "\033[96m"; FG_YELLOW = "\033[93m"
FG_GREEN = "\033[92m"; FG_RED  = "\033[91m"; FG_MAGENTA = "\033[95m"
FG_BLUE  = "\033[94m"; FG_GRAY = "\033[90m"; FG_ORANGE  = "\033[33m"
BG_RED   = "\033[41m"; BG_DARK = "\033[40m"

# ── Terminal Helpers ───────────────────────────────────────────────────────────
def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")

def cols() -> int:
    try:    return os.get_terminal_size().columns
    except: return 100

def hr(ch: str = "─", c: str = FG_GRAY) -> str:
    return f"{c}{ch * cols()}{RST}"

def centered(text: str, c: str = FG_WHITE) -> str:
    pad = max(0, (cols() - len(text)) // 2) * " "
    return f"{c}{pad}{text}{pad}{RST}"

# ── Banner ─────────────────────────────────────────────────────────────────────
BANNER = [
    " ███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗ █████╗ ██╗      ██████╗ ██╗████████╗ ██████╗██╗  ██╗ ",
    " ██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔══██╗██║     ██╔══██╗██║╚══██╔══╝██╔════╝██║  ██║ ",
    " ███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║███████║██║     ██████╔╝██║   ██║   ██║     ███████║ ",
    " ╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══██║██║     ██╔═══╝ ██║   ██║   ██║     ██╔══██║ ",
    " ███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║██║  ██║███████╗██║     ██║   ██║   ╚██████╗██║  ██║ ",
    " ╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝ ",
]

PULSE = [FG_CYAN, FG_BLUE, FG_MAGENTA, FG_BLUE]

def print_banner(tick: int) -> None:
    c = PULSE[tick % len(PULSE)]
    sys.stdout.write("\n")
    for ln in BANNER:
        sys.stdout.write(f"{BOLD}{c}{ln}{RST}\n")
    sys.stdout.write(centered("FIFA WORLD CUP 2026  ·  STADIUM COMMAND NETWORK  ·  SENTINAI-PITCH  ·  LIVE CONTROL PROTOCOL", BOLD + FG_WHITE) + "\n")
    sys.stdout.write(hr("═", FG_CYAN) + "\n")

def section(title: str, c: str = FG_CYAN) -> None:
    sys.stdout.write(f"\n{BOLD}{c}  ▌ {title}{RST}\n{hr('─', FG_GRAY)}\n")

# ── FIFA WC 2026 Telemetry Simulation Dataset ──────────────────────────────────
# crowd_temperament must be one of: calm | anxious | angry | violent
# "CELEBRATORY" post-match egress is mapped to "calm" (orderly dispersal)
SCENARIOS = [
    # ── PHASE 1: PAST HISTORIC FIXTURES ───────────────────────────────────────
    {
        "phase": "PAST", "phase_color": FG_GRAY,
        "label": "R16 · Seattle · Belgium vs USA",
        "result": "Belgium 4 – 1 USA",
        "date": "COMPLETED",
        "mood_display": "CELEBRATORY (Orderly Egress)",
        "payload": '{"gate_id":"SEA-GATE-N","current_occupancy":950,"max_capacity":1000,"transit_status":"normal","crowd_temperament":"calm","active_language":"en"}'
    },
    {
        "phase": "PAST", "phase_color": FG_GRAY,
        "label": "R16 · New York/New Jersey · Norway vs Brazil",
        "result": "Norway 2 – 1 Brazil",
        "date": "COMPLETED",
        "mood_display": "CALM",
        "payload": '{"gate_id":"NYN-GATE-E","current_occupancy":880,"max_capacity":1000,"transit_status":"normal","crowd_temperament":"calm","active_language":"en"}'
    },
    {
        "phase": "PAST", "phase_color": FG_GRAY,
        "label": "R32 · Mexico City · Mexico vs Ecuador",
        "result": "Mexico 2 – 0 Ecuador",
        "date": "COMPLETED",
        "mood_display": "CELEBRATORY (Orderly Egress)",
        "payload": '{"gate_id":"MEX-GATE-S","current_occupancy":1000,"max_capacity":1000,"transit_status":"normal","crowd_temperament":"calm","active_language":"es"}'
    },

    # ── PHASE 2: LIVE ACTIVE FIXTURES (July 7) ─────────────────────────────────
    {
        "phase": "LIVE", "phase_color": FG_GREEN,
        "label": "R16 · Atlanta · Argentina vs Egypt  ◉ LIVE",
        "result": "ONGOING — Kick-off 20:00 EST",
        "date": "JUL 07 2026",
        "mood_display": "CALM",
        "payload": '{"gate_id":"ATL-GATE-W","current_occupancy":320,"max_capacity":1000,"transit_status":"normal","crowd_temperament":"calm","active_language":"en"}'
    },
    {
        "phase": "LIVE", "phase_color": FG_GREEN,
        "label": "R16 · BC Place Vancouver · Switzerland vs Colombia  ◉ LIVE",
        "result": "ONGOING — Kick-off 22:00 EST",
        "date": "JUL 07 2026",
        "mood_display": "ANXIOUS (Shuttle Delay)",
        "payload": '{"gate_id":"VAN-GATE-A","current_occupancy":760,"max_capacity":1000,"transit_status":"delayed","crowd_temperament":"anxious","active_language":"fr"}'
    },

    # ── PHASE 3: UPCOMING KNOCKOUT FIXTURES ────────────────────────────────────
    {
        "phase": "UPCOMING", "phase_color": FG_YELLOW,
        "label": "QF · Boston · France vs Morocco",
        "result": "SCHEDULED",
        "date": "JUL 09 2026",
        "mood_display": "ANXIOUS (Pre-match Transit Delay)",
        "payload": '{"gate_id":"BOS-GATE-C","current_occupancy":850,"max_capacity":1000,"transit_status":"delayed","crowd_temperament":"anxious","active_language":"fr"}'
    },
    {
        "phase": "UPCOMING", "phase_color": FG_YELLOW,
        "label": "QF · SoFi Stadium Los Angeles · Spain vs Belgium",
        "result": "SCHEDULED — CRITICAL RISK",
        "date": "JUL 10 2026",
        "mood_display": "VIOLENT (Non-linear Compounding Risk Triggered)",
        "payload": '{"gate_id":"LAX-GATE-B","current_occupancy":980,"max_capacity":1000,"transit_status":"blocked","crowd_temperament":"violent","active_language":"es"}'
    },
    {
        "phase": "UPCOMING", "phase_color": FG_MAGENTA,
        "label": "FINAL · MetLife Stadium · Finalist Slot Allocation",
        "result": "PREVIEW — Pre-gates Structural Intake",
        "date": "JUL 19 2026",
        "mood_display": "CALM (Early Structural Load)",
        "payload": '{"gate_id":"MET-GATE-VIP","current_occupancy":150,"max_capacity":1000,"transit_status":"normal","crowd_temperament":"calm","active_language":"en"}'
    },

    # ── SECURITY VALIDATION: Corrupted Telemetry Fault Injection ───────────────
    {
        "phase": "FAULT", "phase_color": FG_RED,
        "label": "SECURITY TEST · Fault Injection · Sensor Tamper Simulation",
        "result": "CORRUPTED PACKET — FAULT TOLERANCE CHECK",
        "date": "SYSTEM AUDIT",
        "mood_display": "N/A — MALFORMED INPUT",
        "payload": '{"gate_id":"FLT-GATE-X","current_occupancy":"CORRUPTED","max_capacity":1000,"transit_status":"normal"'
    },
]

# ── Threat styling ─────────────────────────────────────────────────────────────
def threat_meta(score: float) -> tuple:
    if score < 40.0:   return "LOW",    FG_GREEN
    elif score < 70.0: return "MEDIUM", FG_YELLOW
    else:              return "HIGH",   FG_RED

# ── Render telemetry block ─────────────────────────────────────────────────────
def render_telemetry(sc: dict, ts: str, payload, score, error_msg) -> None:
    pc = sc["phase_color"]
    sys.stdout.write(f"\n  {BOLD}{pc}[ {sc['phase']:<8}]{RST}  "
                     f"{BOLD}{FG_WHITE}{sc['label']}{RST}\n")
    sys.stdout.write(f"  {DIM}Date: {sc['date']}  ·  Result: {sc['result']}{RST}\n")

    if error_msg:
        sys.stdout.write(f"  {BG_RED}{FG_WHITE}{BOLD} CORRUPTED PACKET {RST}  "
                         f"{FG_RED}{error_msg}{RST}\n")
        sys.stdout.write(f"  {DIM}Mood Display: {sc['mood_display']}{RST}\n")
    elif payload and score is not None:
        tlbl, tc = threat_meta(score)
        occ_pct = (payload.current_occupancy / payload.max_capacity) * 100
        bar_len = 28
        filled  = min(int((occ_pct / 100) * bar_len), bar_len)
        bar = f"{tc}{'█' * filled}{FG_GRAY}{'░' * (bar_len - filled)}{RST}"
        sys.stdout.write(f"  {DIM}[{ts}]{RST}  Gate: {BOLD}{FG_WHITE}{payload.gate_id:<16}{RST}  "
                         f"Threat: {BOLD}{tc}{tlbl:<6}{RST}  Score: {BOLD}{tc}{score:.2f}/100{RST}\n")
        sys.stdout.write(f"  Occupancy: {bar} {FG_WHITE}{occ_pct:.1f}%{RST} "
                         f"{DIM}({payload.current_occupancy:,}/{payload.max_capacity:,}){RST}\n")
        sys.stdout.write(f"  {DIM}Transit:{RST} {FG_YELLOW}{payload.transit_status.upper():<10}{RST}  "
                         f"{DIM}Temperament:{RST} {FG_MAGENTA}{payload.crowd_temperament.upper():<10}{RST}  "
                         f"{DIM}Lang:{RST} {FG_CYAN}{payload.active_language.upper()}{RST}  "
                         f"{DIM}Mood Display:{RST} {pc}{sc['mood_display']}{RST}\n")
    sys.stdout.write(hr("·", FG_GRAY) + "\n")

# ── Render mitigation block ────────────────────────────────────────────────────
def render_mitigation(sc: dict, payload, score, mitigation_json: str, error_msg) -> None:
    pc = sc["phase_color"]
    sys.stdout.write(f"\n  {BOLD}{pc}[ {sc['phase']:<8}]{RST}  {FG_WHITE}{sc['label']}{RST}\n")

    if error_msg:
        sys.stdout.write(f"  {BOLD}{FG_RED}■ FAULT INTERCEPT ACTIVE{RST}\n")
        sys.stdout.write(f"    {FG_RED}▶ STATUS      {RST}{FG_WHITE}Pipeline caught corrupted telemetry packet safely.{RST}\n")
        sys.stdout.write(f"    {FG_RED}▶ ACTION      {RST}{FG_WHITE}Packet discarded. Sensor reset queued. Supervisor alerted.{RST}\n")
        sys.stdout.write(f"    {FG_RED}▶ BROADCAST   {RST}{FG_CYAN}\"Control room standby. Signal integrity check in progress.\"{RST}\n")
    elif payload and score is not None and mitigation_json:
        _, tc = threat_meta(score)
        d = json.loads(mitigation_json)
        sys.stdout.write(f"  {BOLD}{tc}■ GATE {payload.gate_id} — MITIGATION ISSUED:{RST}\n")
        sys.stdout.write(f"    {FG_BLUE}▶ DYNAMIC ROUTING   {RST}{FG_WHITE}{d['dynamic_routing']}{RST}\n")
        sys.stdout.write(f"    {FG_YELLOW}▶ STAFF ALLOCATION  {RST}{FG_WHITE}{d['staff_allocation']}{RST}\n")
        sys.stdout.write(f"    {FG_MAGENTA}▶ FAN BROADCAST     {RST}{FG_CYAN}\"{d['broadcast_msg']}\"{RST}\n")
    sys.stdout.write(hr("·", FG_GRAY) + "\n")

# ── Main TUI Loop ──────────────────────────────────────────────────────────────
def run() -> None:
    engine   = StadiumOperationsEngine()
    tick     = 0
    interval = 4

    sys.stdout.write(f"\n{BOLD}{FG_CYAN}  Initialising SentinAI-Pitch FIFA WC 2026 Command Network...{RST}\n")
    time.sleep(1.2)

    while True:
        sc  = SCENARIOS[tick % len(SCENARIOS)]
        ts  = time.strftime("%H:%M:%S")

        payload = score = mitigation_json = None
        error_msg = None

        try:
            data = json.loads(sc["payload"])
            payload = TelemetryPayload(
                gate_id           = data["gate_id"],
                current_occupancy = int(data["current_occupancy"]),
                max_capacity      = int(data["max_capacity"]),
                transit_status    = str(data["transit_status"]),
                crowd_temperament = str(data["crowd_temperament"]),
                active_language   = str(data["active_language"])
            )
            score          = engine.evaluate_threat_score(payload)
            mitigation_json = engine.broker_mitigation(payload)
        except Exception as exc:
            error_msg = str(exc)

        clear()
        print_banner(tick)

        section("LIVE TELEMETRY INCIDENTS ─── FIFA WC 2026 FIXTURE FEED", FG_CYAN)
        render_telemetry(sc, ts, payload, score, error_msg)

        section("AUTOMATED COGNITIVE MITIGATION ACTIONS", FG_YELLOW)
        render_mitigation(sc, payload, score, mitigation_json, error_msg)

        # ── Progress tracker ──
        total   = len(SCENARIOS)
        filled  = tick % total + 1
        bar     = f"{FG_CYAN}{'■' * filled}{FG_GRAY}{'□' * (total - filled)}{RST}"
        phases  = f"PAST:3  LIVE:2  UPCOMING:3  FAULT:1"
        sys.stdout.write(hr("═", FG_CYAN) + "\n")
        sys.stdout.write(f"  {DIM}CYCLE {tick + 1:04d}  ·  SCENARIO {filled}/{total}  ·  {bar}  "
                         f"·  {phases}  ·  NEXT IN {interval}s  ·  Ctrl+C TO EXIT{RST}\n")

        tick += 1
        time.sleep(interval)

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.stdout.write(f"\n{BOLD}{FG_CYAN}  SentinAI-Pitch Command Network — SESSION TERMINATED.{RST}\n")
        sys.exit(0)
